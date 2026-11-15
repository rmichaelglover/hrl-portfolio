#pragma once
// Michael Emanuel Glover's progression-logic research; implementation: Cypher.
#include "progression_logic.hpp"
namespace magnum::logic::words {

// Canonical decimal naturals have no fixed machine-word maximum. Every actual
// allocation is finite; this represents arbitrary finite exponents symbolically.
class Natural {
    std::string digits_;
public:
    explicit Natural(std::string digits="0"):digits_(std::move(digits)) {
        if (digits_.empty() || (digits_.size()>1 && digits_[0]=='0'))
            throw std::invalid_argument("Noncanonical natural");
        for (char c:digits_) if (c<'0'||c>'9') throw std::invalid_argument("Natural digit");
    }
    const std::string& decimal() const noexcept {return digits_;}
    bool operator==(const Natural& b) const noexcept {return digits_==b.digits_;}
    bool operator!=(const Natural& b) const noexcept {return !(*this==b);}
    bool operator<(const Natural& b) const noexcept {
        return digits_.size()!=b.digits_.size() ? digits_.size()<b.digits_.size() : digits_<b.digits_;
    }
    Natural plus(const Natural& b) const {
        std::string result;
        auto i=digits_.size(),j=b.digits_.size();unsigned carry=0;
        while (i||j||carry) {
            unsigned value=carry;
            if (i) value+=unsigned(digits_[--i]-'0');
            if (j) value+=unsigned(b.digits_[--j]-'0');
            result+=char('0'+value%10);carry=value/10;
        }
        std::reverse(result.begin(),result.end());return Natural(std::move(result));
    }
    std::optional<std::size_t> bounded_size(std::size_t limit) const {
        std::size_t value=0;
        for (char c:digits_) {
            const auto digit=std::size_t(c-'0');
            if (value>limit/10 || (value==limit/10 && digit>limit%10)) return {};
            value=10*value+digit;
        }
        return value;
    }
};

// An explicit tag prevents accidental substitution for ordinary game rules.
struct MovementOnlyNoDrawAdjudication {};
inline constexpr MovementOnlyNoDrawAdjudication movement_only{};

// A projected movement position has no clock or history adjudication. Resetting
// those fields avoids overflowing the chess library's finite counters. It does
// not remove occupancy, turn, castling rights or en-passant move constraints.
inline Board projected_board(const Board& board) {
    if (board.chess960()) throw std::invalid_argument("Movement words currently require orthodox chess");
    std::istringstream in(board.getFen());
    std::string placement,turn,rights,ep;
    in>>placement>>turn>>rights>>ep;
    Board projected;
    if (!projected.setFen(placement+" "+turn+" "+rights+" "+ep+" 0 1"))
        throw std::invalid_argument("Movement projection FEN");
    return projected;
}
class LoopCertificate {
    Board root_;
    std::vector<std::string> moves_;
    std::string signature_;
public:
    LoopCertificate(const State& root,std::vector<std::string> moves,
                    MovementOnlyNoDrawAdjudication)
        :root_(projected_board(root.board)),moves_(std::move(moves)) {
        validate(root_);
        if (moves_.empty()) throw std::invalid_argument("A generator must contain moves");
        auto board=root_;
        for (const auto& uci:moves_) {
            auto move=chess::uci::uciToMove(board,uci);auto choices=legal(board);
            if (std::find(choices.begin(),choices.end(),move)==choices.end())
                throw std::invalid_argument("Illegal generator move: "+uci);
            board.makeMove(move);board=projected_board(board);
        }
        if (key(board)!=key(root_)) throw std::invalid_argument("Generator is not a closed movement loop");
        signature_="movement-only-orthodox-v1"+field(key(root_));
        for (const auto& move:moves_) signature_+=field(move);
    }
    const Board& root() const noexcept {return root_;}
    const std::vector<std::string>& moves() const noexcept {return moves_;}
    const std::string& signature() const noexcept {return signature_;}
};
using Loop=std::shared_ptr<const LoopCertificate>;
class Word {
    Loop loop_;
    Natural cycles_;
public:
    explicit Word(Loop loop,Natural cycles=Natural{}):loop_(std::move(loop)),cycles_(std::move(cycles)) {
        if (!loop_) throw std::invalid_argument("Missing loop certificate");
    }
    const Loop& loop() const noexcept {return loop_;}
    const Natural& cycles() const noexcept {return cycles_;}
    void same_family(const Word& b) const {
        if (loop_->signature()!=b.loop_->signature()) throw std::invalid_argument("Different word generators");
    }
    Word then(const Word& b) const {
        same_family(b);return Word(loop_,cycles_.plus(b.cycles_));
    }
    Word successor() const {return then(Word(loop_,Natural("1")));}
    bool operator==(const Word& b) const {
        return loop_->signature()==b.loop_->signature() && cycles_==b.cycles_;
    }
    std::string text() const {return "U"+field(loop_->signature())+field(cycles_.decimal());}
    // Explicit expansion is a separate bounded operation, never an implicit
    // prerequisite to exact composition or symbolic equality.
    std::vector<std::string> materialize(std::size_t max_plies) const {
        const auto period=loop_->moves().size();
        auto count=cycles_.bounded_size(max_plies/period);
        if (!count) throw ResourceLimit();
        std::vector<std::string> moves;moves.reserve(*count*period);
        for (std::size_t i=0;i<*count;++i)
            moves.insert(moves.end(),loop_->moves().begin(),loop_->moves().end());
        return moves;
    }
};

// EXTRA object-language operation. Variable-count block repetition is not
// asserted definable from concatenation. Its standard interpretation multiplies
// exponents; implementing that interpretation does not prove definability.
class RepeatExtension {
    static Natural product(const Natural& a,const Natural& b) {
        const auto& x=a.decimal();const auto& y=b.decimal();
        if (x=="0"||y=="0") return Natural{};
        if (x.size()>std::numeric_limits<std::size_t>::max()-y.size()) throw ResourceLimit();
        std::vector<unsigned> digits(x.size()+y.size(),0);
        for (std::size_t i=x.size();i-->0;) {
            unsigned carry=0;
            for (std::size_t j=y.size();j-->0;) {
                unsigned value=digits[i+j+1]+unsigned(x[i]-'0')*unsigned(y[j]-'0')+carry;
                digits[i+j+1]=value%10;carry=value/10;
            }
            digits[i]=carry;
        }
        std::string result;bool started=false;
        for (auto digit:digits) if (digit||started) {result+=char('0'+digit);started=true;}
        return Natural(std::move(result));
    }
public:
    Word repeat(const Word& block,const Word& counter) const {
        block.same_family(counter);
        return Word(block.loop(),product(block.cycles(),counter.cycles()));
    }
};
inline Loop knight_loop() {
    return std::make_shared<LoopCertificate>(State{},
        std::vector<std::string>{"g1f3","g8f6","f3g1","f6g8"},movement_only);
}
} // namespace magnum::logic::words
