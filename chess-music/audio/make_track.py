"""Deterministic 85 BPM chess sonification; source: study.pgn, chapter 2."""
from pathlib import Path
import csv
import json
import math
import struct
import wave
import numpy as np
import chess
import chess.pgn

ROOT = Path(__file__).resolve().parent
SR, BPM, BARS = 44100, 85, 32
BEAT = 60 / BPM
DURATION = BARS * 4 * BEAT + 3
SIZE = round(DURATION * SR)
rng = np.random.default_rng(7)
stems = {name: np.zeros((SIZE, 2), dtype=np.float32) for name in ['01-dusty-drums', '02-warm-bass', '03-soft-chords', '04-white-moves', '05-black-moves']}
events = []

def add(name, start, sound, amplitude=1, pan=0):
    i = round(start * SR)
    sound = sound[:max(0, SIZE - i)]
    if i < 0 or not len(sound): return
    gains = np.array([math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)], dtype=np.float32)
    stems[name][i:i+len(sound)] += sound[:, None] * gains * amplitude


def t(duration): return np.arange(round(duration * SR), dtype=np.float32) / SR

def tone(note, duration, kind='bell'):
    times = t(duration)
    freq = 440 * 2 ** ((note - 69) / 12)
    phase = 2 * math.pi * freq * times
    if kind == 'bass':
        sound = np.sin(phase) + .18 * np.sin(2*phase)
        envelope = np.minimum(times/.012, 1) * np.exp(-times/1.1) * np.minimum((duration-times)/.06, 1)
    elif kind == 'pad':
        sound = .65 * np.sin(phase) + .25 * np.sin(phase * 1.003) + .10 * np.sin(2*phase)
        envelope = np.minimum(times/.12, 1) * np.minimum((duration-times)/.35, 1)
    else:
        sound = np.sin(phase) + .25*np.sin(2*phase)*np.exp(-times*6) + .10*np.sin(3*phase)*np.exp(-times*10)
        envelope = np.minimum(times/.007, 1) * np.exp(-times/ .38) * np.minimum((duration-times)/.05, 1)
    return (sound * envelope).astype(np.float32)


def kick():
    times = t(.4)
    phase = 2*np.pi*(45*times + 80*.025*(1-np.exp(-times/.025)))
    return (.85*np.sin(phase)*np.exp(-times*12) + rng.normal(0,.04,len(times))*np.exp(-times*120)).astype(np.float32)

def snare():
    times=t(.24); noise=rng.normal(0,1,len(times)); noise=np.convolve(noise,np.ones(5)/5,mode='same')
    return (.6*noise*np.exp(-times*22)+.22*np.sin(2*np.pi*180*times)*np.exp(-times*30)).astype(np.float32)

def hat():
    times=t(.08); noise=rng.normal(0,1,len(times)); noise=noise-np.convolve(noise,np.ones(9)/9,mode='same')
    return (noise*np.exp(-times*65)).astype(np.float32)

# D minor 9 → Bb major 7 → F major 9 → C add 9; original synthesized sound, no samples.
progression = [(38,[62,65,69,72,76]), (34,[58,62,65,69]), (41,[60,65,69,72,79]), (36,[60,64,67,74])]
for bar in range(BARS):
    start=bar*4*BEAT
    active=4 <= bar < 28
    root,chord=progression[(bar//2)%4]
    for index,note in enumerate(chord):
        add('03-soft-chords',start+index*.017,tone(note,4*BEAT+.3,'pad'),.045,(-.6+.3*index))
    if bar >= 2 and bar < 30:
        for beat in ([0,1.75,2.5] if active else [0,2.5]): add('01-dusty-drums',start+beat*BEAT,kick(),.5)
        for beat in [1,3]: add('01-dusty-drums',start+beat*BEAT+.009,snare(),.4,-.05)
        for step in range(8):
            beat=step*.5 + (.075 if step%2 else 0)
            add('01-dusty-drums',start+beat*BEAT,hat(),.055 if step%2 else .085,.25)
        if active and bar%4==3: add('01-dusty-drums', start+3.65*BEAT,snare(),.09,.1)
    if 4 <= bar < 30:
        for beat,note,length in [(0,root,1.45),(1.75,root, .6),(2.5,root+7, .9),(3.5,root+12,.38)]:
            add('02-warm-bass',start+beat*BEAT,tone(note,length*BEAT,'bass'),.24)

with (ROOT/'study.pgn').open() as f:
    chess.pgn.read_game(f)
    game=chess.pgn.read_game(f)
assert game and not game.errors
board=game.board()
scale=[0,2,3,5,7,9,10,12]
for ply, move in enumerate(game.mainline_moves()):
    side='white' if board.turn==chess.WHITE else 'black'
    san=board.san(move); square=move.to_square
    file=chess.square_file(square); rank=chess.square_rank(square)
    note=62+scale[file]+(12 if rank>=4 else 0)-(12 if side=='black' else 0)
    capture=board.is_capture(move)
    # One mainline half-move per beat; eighth-note delay gives Black a swung answer.
    when=(16+ply+(.075 if side=='black' else 0))*BEAT
    add('04-white-moves' if side=='white' else '05-black-moves',when,tone(note,.65),.12 if capture else .08,-.3 if side=='white' else .3)
    if board.gives_check(move): add('04-white-moves' if side=='white' else '05-black-moves',when+.25*BEAT,tone(note+7,.5),.07)
    events.append({'ply':ply+1,'move':san,'side':side,'seconds':round(when,4),'midi_note':note,'capture':capture})
    board.push(move)
# A final D-minor cadence follows the checkmate, then the groove has room to breathe.
ending=(16+len(events))*BEAT
for note in [62,65,69,74]: add('04-white-moves',ending,tone(note,2.5),.06,-.15)

# Gentle tape-style saturation on the drum bus, then one shared gain for all stems.
stems['01-dusty-drums']=np.tanh(stems['01-dusty-drums']*1.3)/1.3
fade=np.ones(SIZE,dtype=np.float32)
fade[:SR]=np.linspace(0,1,SR)
fade[-SR*4:]=np.linspace(1,0,SR*4)
for audio in stems.values(): audio *= fade[:,None]
mix=sum(stems.values())
gain=10**(-3/20)/max(float(np.max(np.abs(mix))),1e-6)

def write_wav(name,audio):
    with wave.open(str(ROOT/name),'wb') as w:
        w.setparams((2,2,SR,0,'NONE','not compressed'))
        w.writeframes(np.round(np.clip(audio*gain,-1,1)*32767).astype('<i2').tobytes())
for name,audio in stems.items(): write_wav(name+'.wav',audio)
write_wav('Vant-Kruijsing-85bpm-mix.wav',mix)
(ROOT/'Open-in-Audacity.lof').write_text('# All stems aligned at zero; do not also import the reference mix.\n'+'\n'.join(f'file "{name}.wav" offset 0' for name in stems)+'\n')
with (ROOT/'moves.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=events[0].keys());writer.writeheader();writer.writerows(events)
with (ROOT/'Audacity-labels.txt').open('w') as f:
    f.write(f'0\t{16*BEAT:.6f}\tIntro — 85 BPM, D minor\n')
    for e in events: f.write(f'{e["seconds"]:.6f}\t{e["seconds"]:.6f}\t{e["ply"]}: {e["side"]} {e["move"]}\n')
    f.write(f'{ending:.6f}\t{DURATION:.6f}\tRh8# — outro\n')
metadata={'title':"Van’t Kruijsing — Head-Nod Chess",'bpm':BPM,'bars':BARS,'duration_seconds':DURATION,'sample_rate':SR,'source_study':'https://lichess.org/study/7hLlnCHF','source_chapter':game.headers.get('ChapterURL'),'players':{'white':game.headers['White'],'black':game.headers['Black']},'result':game.headers['Result'],'half_moves':len(events),'peak_dbfs':20*math.log10(float(np.max(np.abs(mix*gain)))),'mapping':'Destination files a–h map to D Dorian/minor-compatible scale degrees D E F G A B C D; destination ranks 5–8 raise an octave; Black uses the lower register. One half-move per beat, checks add a fifth, captures accent velocity. Accompaniment uses Dm9–Bbmaj7–Fmaj9–Cadd9.'}
(ROOT/'track.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata,indent=2))
