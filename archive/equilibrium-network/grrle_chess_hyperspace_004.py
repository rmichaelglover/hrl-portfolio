#!/usr/bin/env python3
"""GRRLE 004: Lichess PGN empirical drawishness audit.

No third-party Python libraries needed for .pgn, .gz, .pgn.zst via external zstdcat.
Examples:
  python3 grrle_chess_hyperspace_004.py games.pgn --limit 100000 --out results004
  python3 grrle_chess_hyperspace_004.py lichess_db.pgn.zst --limit 100000
  python3 grrle_chess_hyperspace_004.py --self-test

Data source: https://database.lichess.org/
This counts real PGN results and rating/time-control strata. It does NOT infer
intentional sandbagging, prove theoretical draws, or calculate move evaluations.
"""
import argparse, collections, csv, gzip, io, re, subprocess, sys
from contextlib import contextmanager
from pathlib import Path
HEADER = re.compile(r'^\[([^\s]+)\s+"(.*)"\]\s*$')
RESULTS = {'1-0','0-1','1/2-1/2'}

def parse_pgn(f):
    headers={}
    # In regular PGNs a blank line separates header tags and movetext.
    for line in f:
        line=line.strip()
        m=HEADER.match(line)
        if m:
            # A new [Event] tag denotes a new game when the last move section
            # has already begun (robust to missing separator lines).
            if m.group(1)=='Event' and 'Event' in headers:
                yield headers
                headers={}
            headers[m.group(1)] = m.group(2)
    if headers:
        yield headers

def kind(tc, event):
    if tc:
        match=re.fullmatch(r'(\d+)\+(\d+)',tc)
        if match:
            initial,increment=map(int,match.groups())
            est=initial + 40*increment
            return 'ultrabullet' if est<30 else 'bullet' if est<180 else 'blitz' if est<480 else 'rapid' if est<1500 else 'classical'
    ev=event.lower()
    for k in ('ultrabullet','bullet','blitz','rapid','classical','correspondence'):
        if k in ev:return k
    return 'unknown'

def rating_bin(avg):
    if avg<1000:return '<1000'
    if avg<1400:return '1000-1399'
    if avg<1800:return '1400-1799'
    if avg<2200:return '1800-2199'
    return '2200+'

@contextmanager
def open_games(path):
    path=Path(path)
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt',encoding='utf-8',errors='replace') as f:yield f
    elif str(path).endswith('.zst'):
        proc=subprocess.Popen(['zstdcat',str(path)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        try:
            with io.TextIOWrapper(proc.stdout,encoding='utf-8',errors='replace') as f:yield f
        finally:
            if proc.poll() is None:proc.terminate()
            proc.wait()
    else:
        with open(path,encoding='utf-8',errors='replace') as f:yield f

def analyze(games, limit=None):
    bucket=collections.defaultdict(collections.Counter)
    n=0
    for hdr in games:
        if hdr.get('Result') not in RESULTS:continue
        if hdr.get('Variant','Standard') not in ('Standard','From Position'):continue
        try:
            w=int(hdr['WhiteElo']); b=int(hdr['BlackElo'])
            if not 400<=w<=3500 or not 400<=b<=3500:continue
        except (KeyError,ValueError):continue
        if hdr.get('WhiteTitle')=='BOT' or hdr.get('BlackTitle')=='BOT':continue
        tc=kind(hdr.get('TimeControl',''),hdr.get('Event',''))
        level=rating_bin((w+b)/2)
        gap='<=100' if abs(w-b)<=100 else '101-300' if abs(w-b)<=300 else '>300'
        res=hdr['Result']
        # Aggregate by control, rating, rating-gap, and their total.
        for key in [('all','all','all'),(tc,'all','all'),(tc,level,'all'),(tc,level,gap)]:
            bucket[key][res]+=1
        n+=1
        if limit is not None and n>=limit:break
    rows=[]
    for key,counts in sorted(bucket.items()):
        total=sum(counts.values()); draws=counts['1/2-1/2']; white=counts['1-0']; black=counts['0-1']
        # Wilson interval for draw fraction, as a simple binomial descriptive CI.
        z=1.96; den=1+z*z/total; p=draws/total
        center=(p+z*z/(2*total))/den
        half=z*((p*(1-p)/total+z*z/(4*total*total))**0.5)/den
        rows.append(dict(time_control=key[0],rating_band=key[1],rating_gap=key[2],games=total,
                         white_wins=white,draws=draws,black_wins=black,
                         white_win_pct=round(100*white/total,3),draw_pct=round(100*p,3),
                         black_win_pct=round(100*black/total,3),
                         draw_ci95_low=round(100*(center-half),3),draw_ci95_high=round(100*(center+half),3),
                         white_avg_score=round((white+0.5*draws)/total,5)))
    return n,rows

def self_test():
    pgn='''[Event "Rated Rapid game"]\n[WhiteElo "1200"]\n[BlackElo "1250"]\n[TimeControl "600+0"]\n[Result "1/2-1/2"]\n\n1. e4 e5 1/2-1/2\n\n[Event "Rated Blitz game"]\n[WhiteElo "2000"]\n[BlackElo "2020"]\n[TimeControl "300+0"]\n[Result "1-0"]\n\n1. d4 d5 1-0\n'''
    n,rows=analyze(parse_pgn(io.StringIO(pgn)))
    overall=next(r for r in rows if r['time_control']==r['rating_band']==r['rating_gap']=='all')
    assert n==2 and overall['draws']==1 and overall['white_wins']==1
    assert kind('600+0','')=='rapid' and kind('300+0','')=='blitz'
    print('PASS: PGN parser, time-control classification, and summary arithmetic.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pgn',nargs='?',help='Local Lichess PGN, .gz, or .zst archive')
    ap.add_argument('--limit',type=int,default=100000,help='Maximum qualifying games to analyze')
    ap.add_argument('--out',default='grrle_004',help='Output CSV name prefix')
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if args.self_test:self_test();return
    if not args.pgn:ap.error('Supply a PGN file or --self-test')
    with open_games(args.pgn) as f:n,rows=analyze(parse_pgn(f),args.limit)
    if not n:sys.exit('No qualifying games: check archive path and PGN headers.')
    outfile=Path(args.out+'_summary.csv')
    with outfile.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    overall=next(r for r in rows if (r['time_control'],r['rating_band'],r['rating_gap'])==('all','all','all'))
    print('REAL LICHESS PGN EXPERIMENT 004')
    print('Qualifying games:',n,'| Input:',args.pgn)
    print('White wins:',overall['white_wins'],'Draws:',overall['draws'],'Black wins:',overall['black_wins'])
    print('Draw fraction: {:.3f}% (Wilson 95% {:.3f}–{:.3f}%)'.format(overall['draw_pct'],overall['draw_ci95_low'],overall['draw_ci95_high']))
    print('White expected score:',overall['white_avg_score'])
    print('Saved:',outfile)
    print('CAVEAT: descriptive sample frequencies; no proof of intent, optimal play, or perfect-play chess outcome.')

if __name__=='__main__':main()
