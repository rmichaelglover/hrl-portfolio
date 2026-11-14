#pragma once
// Research direction: Michael Emanuel Glover. Implementation: Cypher.
// A bounded modal logic over the existing Magnum legal-progression kernel.
#include "proof.hpp"
#include <optional>
#include <limits>
namespace magnum::logic {

// Injective natural-number code for finite byte strings. Each byte occupies
// three decimal places, after a leading 1. No hash collisions or bigint library.
inline std::string number(const std::string& text) {
    std::string result="1";
    for (unsigned char byte : text) {
        result += char('0'+byte/100);
        result += char('0'+(byte/10)%10);
        result += char('0'+byte%10);
    }
    return result;
}
inline std::string unnumber(const std::string& code) {
    if (code.empty() || code[0]!='1' || code.size()%3!=1)
        throw std::invalid_argument("Noncanonical natural code");
    std::string result;
    for (std::size_t i=1;i<code.size();i+=3) {
        unsigned value=0;
        for (std::size_t j=0;j<3;++j) {
            if (code[i+j]<'0' || code[i+j]>'9') throw std::invalid_argument("Code digit");
            value=10*value+unsigned(code[i+j]-'0');
        }
        if (value>255) throw std::invalid_argument("Code byte");
        result+=static_cast<char>(value);
    }
    return result;
}
inline std::string field(const std::string& text) { return std::to_string(text.size())+":"+text; }
inline std::string state_text(const State& state) {
    std::string result="S"+field(state.board.getFen());
    result+=field(std::to_string(state.history.size()));
    for (const auto& position : state.history) result+=field(position);
    return result;
}
// A state loaded from FEN starts a new local history, exactly as in proof.hpp.
// This certificate proves legal play from the supplied root, not reachability
// of that root from the standard initial position.
class Progression {
    State root_;
    std::vector<std::string> moves_;
public:
    explicit Progression(State root, std::vector<std::string> moves={})
        :root_(std::move(root)),moves_(std::move(moves)) { (void)end(); }
    State end() const {
        State state=root_;
        for (const auto& move:moves_) {
            if (terminal(state,legal(state.board)).done)
                throw std::invalid_argument("Progression continues after terminal state");
            state.play(move);
        }
        return state;
    }
    std::size_t length() const noexcept { return moves_.size(); }
    Progression then(const Progression& next) const {
        if (state_text(end())!=state_text(next.root_))
            throw std::invalid_argument("Composition requires identical complete intermediate state");
        auto moves=moves_;moves.insert(moves.end(),next.moves_.begin(),next.moves_.end());
        return Progression(root_,std::move(moves));
    }
    Progression prefix(std::size_t length) const {
        if (length>moves_.size()) throw std::out_of_range("Prefix length");
        return Progression(root_,{moves_.begin(),moves_.begin()+length});
    }
    std::string text() const {
        std::string result="P"+field(state_text(root_))+field(std::to_string(moves_.size()));
        for (const auto& m:moves_) result+=field(m);
        return result;
    }
};

enum class Op { True, WhiteTurn, WhiteMate, Terminal, Position, Not, And, Or, Some, Every };
struct Expression;
using Formula=std::shared_ptr<const Expression>;
struct Expression {
    const Op op;
    const std::string position;
    const Formula left,right;
    Expression(Op o,std::string p={},Formula a={},Formula b={})
        :op(o),position(std::move(p)),left(std::move(a)),right(std::move(b)) {
        if (static_cast<unsigned>(o)>static_cast<unsigned>(Op::Every))
            throw std::invalid_argument("Unknown operator");
        const bool unary=o==Op::Not||o==Op::Some||o==Op::Every;
        const bool binary=o==Op::And||o==Op::Or;
        if ((unary&&(!left||right)) || (binary&&(!left||!right)) ||
            (!unary&&!binary&&(left||right)) || (o!=Op::Position&&!position.empty()))
            throw std::invalid_argument("Malformed formula");
    }
};
inline Formula atom(Op op,std::string position={}) {return std::make_shared<Expression>(op,std::move(position));}
inline Formula unary(Op op,Formula p) {return std::make_shared<Expression>(op,"",std::move(p));}
inline Formula binary(Op op,Formula p,Formula q) {return std::make_shared<Expression>(op,"",std::move(p),std::move(q));}
inline Formula negate(Formula p) {return unary(Op::Not,std::move(p));}
inline Formula some(Formula p) {return unary(Op::Some,std::move(p));}
inline Formula every(Formula p) {return unary(Op::Every,std::move(p));}
inline std::string text(const Formula& p) {
    if (!p) throw std::invalid_argument("Null formula");
    static const char* tokens[]={"T","W","M","X","P","!","&","|","D","B"};
    auto result=std::string(tokens[static_cast<unsigned>(p->op)]);
    if (p->op==Op::Position) result+=field(p->position);
    if (p->left) result+=field(text(p->left));
    if (p->right) result+=field(text(p->right));
    return result;
}
class ResourceLimit:public std::runtime_error {
public: ResourceLimit():std::runtime_error("Logical query budget exhausted: no verdict") {}
};
class ModelChecker {
    std::size_t budget_,visited_=0;
    bool derive(State& state,const Formula& p) {
        if (++visited_>budget_) throw ResourceLimit();
        if (!p) throw std::invalid_argument("Null formula");
        switch (p->op) {
        case Op::True:return true;
        case Op::WhiteTurn:return state.board.sideToMove()==Color::WHITE;
        case Op::WhiteMate: {
            auto moves=legal(state.board);
            return moves.empty()&&state.board.inCheck()&&state.board.sideToMove()==Color::BLACK;
        }
        case Op::Terminal:return terminal(state,legal(state.board)).done;
        case Op::Position:return key(state.board)==p->position;
        case Op::Not:return !derive(state,p->left);
        case Op::And:return derive(state,p->left)&&derive(state,p->right);
        case Op::Or:return derive(state,p->left)||derive(state,p->right);
        case Op::Some:case Op::Every: {
            const bool universal=p->op==Op::Every;
            auto moves=legal(state.board);
            if (terminal(state,moves).done) return universal;
            for (auto move:moves) {
                // Copying gives exception-safe history even when a budget expires.
                State next=state;next.push(move);
                const bool result=derive(next,p->left);
                if (result!=universal) return result;
            }
            return universal;
        }
        }
        throw std::invalid_argument("Unknown operator");
    }
public:
    explicit ModelChecker(std::size_t budget=1000000):budget_(budget) {}
    bool evaluate(State state,const Formula& p) {visited_=0;return derive(state,p);}
    std::size_t visited() const noexcept {return visited_;}
};
// Bounded reachability versus bounded adversarial forcing, both from White's
// perspective. Terminal states cannot make a vacuous universal into a win.
inline Formula reach_within(Formula goal,unsigned depth,bool adversarial) {
    auto result=goal;
    for (unsigned i=0;i<depth;++i) {
        auto continuation=some(result);
        if (adversarial) {
            auto turn=atom(Op::WhiteTurn);
            continuation=binary(Op::Or,binary(Op::And,turn,continuation),
                binary(Op::And,negate(turn),every(result)));
        }
        result=binary(Op::Or,goal,binary(Op::And,negate(atom(Op::Terminal)),continuation));
    }
    return result;
}
// Explicit finite interpretation on a distinguished certified path's prefixes.
// The tables are externally constructed by length; they are not an assertion
// that addition/multiplication is definable in bare modal chess syntax.
class PrefixArithmetic {
    std::size_t maximum_;
public:
    explicit PrefixArithmetic(const Progression& path):maximum_(path.length()) {}
    std::size_t maximum() const noexcept {return maximum_;}
    std::optional<std::size_t> successor(std::size_t a) const {
        if (a>=maximum_) return {};
        return a+1;
    }
    std::optional<std::size_t> add(std::size_t a,std::size_t b) const {
        if (a>maximum_||b>maximum_-a) return {};
        return a+b;
    }
    std::optional<std::size_t> multiply(std::size_t a,std::size_t b) const {
        if (a>maximum_||b>maximum_||(a!=0&&b>maximum_/a)) return {};
        return a*b;
    }
};
} // namespace magnum::logic
