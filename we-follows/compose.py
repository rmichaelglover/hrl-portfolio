from pathlib import Path
import numpy as np, wave, subprocess, json, zipfile
P=Path(__file__).resolve().parent
SR=32000; BPM=96; BEAT=60/BPM; BAR=4*BEAT; DUR=64*BAR+5; N=int(DUR*SR)
rng=np.random.default_rng(26)
stems={name:np.zeros((N,2),np.float32) for name in ['01-pulse','02-ground','03-harmony','04-letters','05-answer']}
def add(name,at,y,pan=0):
 i=int(at*SR); n=min(len(y),N-i)
 if n<=0:return
 stems[name][i:i+n,0]+=y[:n]*np.sqrt((1-pan)/2)
 stems[name][i:i+n,1]+=y[:n]*np.sqrt((1+pan)/2)
def tone(midi,duration,kind='bell'):
 t=np.arange(int(duration*SR))/SR; f=440*2**((midi-69)/12)
 if kind=='pad':
  y=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*1.003*t)+.15*np.sin(4*np.pi*f*t))*np.minimum(t/.3,1)*np.minimum((duration-t)/.5,1)*.1
 elif kind=='bass': y=(np.sin(2*np.pi*f*t)+.2*np.sin(4*np.pi*f*t))*np.minimum(t/.015,1)*np.exp(-t*3)*.25
 else:y=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*f*2*t)*np.exp(-t*5)+.12*np.sin(2*np.pi*f*3*t))*np.minimum(t/.008,1)*np.exp(-t*2.7)*.18
 return y
# Four sixteen-bar movements: emergence, definition, consequence, openness.
chords=[[50,57,60,64],[46,53,57,60],[53,60,64,67],[48,55,58,62]]
scale=[62,64,65,67,69,70,72,74]
letter_notes={chr(97+i):scale[i%8]+12*(i//16) for i in range(26)}
phrase='wefollowswordsmeanthings'
for bar in range(64):
 section=bar//16; local=bar%16; at=bar*BAR; chord=chords[(bar//2)%4]
 for note in chord:add('03-harmony',at,tone(note,BAR+1,'pad'),(note-chord[0])/24-.4)
 if section or local>=4:
  for beat in [0,1.5,2.75]:add('02-ground',at+beat*BEAT,tone(chord[0]-12,.48,'bass'))
 if section in [1,2] or (section==0 and local>=8) or (section==3 and local<8):
  for beat in [0,2,3.5] if section==2 else [0,2]:
   t=np.arange(int(.24*SR))/SR; y=np.sin(2*np.pi*(46*t+70*.035*(1-np.exp(-t/.035))))*np.exp(-t*19)*.5
   add('01-pulse',at+beat*BEAT,y)
  for beat in [1,3]:
   t=np.arange(int(.16*SR))/SR; y=(rng.normal(size=len(t))*.17+np.sin(2*np.pi*175*t)*.1)*np.exp(-t*28)*np.minimum(t/.002,1)
   add('01-pulse',at+beat*BEAT,y,-.12)
  for k in range(8):
   t=np.arange(int(.06*SR))/SR; noise=rng.normal(size=len(t)); noise=np.r_[0,np.diff(noise)]
   add('01-pulse',at+(k*.5+(0.07 if k%2 else 0))*BEAT,noise*np.exp(-t*70)*.025, .45)
 if section!=3 or local<12:
  for k in range(4 if section==0 else 8):
   letter=phrase[(bar*4+k)%len(phrase)]; note=letter_notes[letter]
   add('04-letters',at+k*(1 if section==0 else .5)*BEAT,tone(note,.9),np.sin(bar+k)*.6)
 if section>=2:
  for k in [0,1.5,3]:
   note=[74,72,69,67][(local+int(k))%4]
   add('05-answer',at+k*BEAT+.25*BEAT,tone(note,1.6),-.4)
# Light stereo echoes create space; all exported stems share one global gain.
for name in ['03-harmony','04-letters','05-answer']:
 dry=stems[name].copy()
 for delay,gain in [(BEAT*.75,.23),(BEAT*1.5,.12),(BEAT*2.25,.06)]:
  d=int(delay*SR);stems[name][d:]+=dry[:-d,::-1]*gain
fade=np.minimum(np.arange(N)/(SR*2),1)*np.minimum((N-np.arange(N))/(SR*6),1)
for a in stems.values():a*=fade[:,None]
mix=sum(stems.values());gain=.89/np.max(np.abs(mix))
def write(path,a):
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
for name,a in stems.items():
 write(P/(name+'.wav'),a*gain)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/(name+'.wav')),str(P/(name+'.flac'))],check=True)
write(P/'We-Follows.wav',mix*gain)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(P/'We-Follows.wav'),'-codec:a','libmp3lame','-b:a','192k',str(P/'We-Follows.mp3')],check=True)
movements=['I · Symbols awaken','II · Meanings gather','III · It follows','IV · The open world']
(P/'Audacity-labels.txt').write_text(''.join(f'{i*16*BAR}\t{(i+1)*16*BAR}\t{m}\n' for i,m in enumerate(movements)))
(P/'Open-in-Audacity.lof').write_text(''.join(f'file "{name}.flac"\n' for name in stems))
(P/'score.json').write_text(json.dumps({'title':'We Follows','bpm':BPM,'duration_seconds':DUR,'sample_rate':SR,'movements':[{'title':m,'start_seconds':i*40} for i,m in enumerate(movements)],'letter_notes_midi':letter_notes,'mapping_note':'Letter-to-note mapping is an artistic convention, not a proof of meaning.','peak':float(np.max(np.abs(mix*gain))),'seed':26},indent=2))
print(json.dumps({'duration':DUR,'peak':float(np.max(np.abs(mix*gain))),'finite':bool(np.isfinite(mix).all()),'stems':len(stems)}))
