"""Offline PCM speech decoding using Ubuntu's installed PocketSphinx 0.8 ABI.

No microphone recording or network calls occur here. The browser explicitly
captures an utterance and submits signed 16-bit little-endian 16 kHz PCM.
This recognizes speech; it does NOT establish speaker identity or liveness.
"""
import ctypes as c
from pathlib import Path


class OfflineVoice:
    def __init__(self, log_path="/dev/null"):
        self.ps=c.CDLL('libpocketsphinx.so.3')
        self.base=c.CDLL('libsphinxbase.so.3')
        self.ps.ps_args.restype=c.c_void_p
        self.base.cmd_ln_parse_r.argtypes=[c.c_void_p,c.c_void_p,c.c_int,c.POINTER(c.c_char_p),c.c_int]
        self.base.cmd_ln_parse_r.restype=c.c_void_p
        self.base.cmd_ln_free_r.argtypes=[c.c_void_p]
        self.ps.ps_init.argtypes=[c.c_void_p]; self.ps.ps_init.restype=c.c_void_p
        self.ps.ps_free.argtypes=[c.c_void_p]
        self.ps.ps_set_jsgf_string.argtypes=[c.c_void_p,c.c_char_p,c.c_char_p]
        self.ps.ps_set_search.argtypes=[c.c_void_p,c.c_char_p]
        self.ps.ps_start_utt.argtypes=[c.c_void_p,c.c_char_p]
        self.ps.ps_end_utt.argtypes=[c.c_void_p]
        self.ps.ps_process_raw.argtypes=[c.c_void_p,c.POINTER(c.c_int16),c.c_size_t,c.c_int,c.c_int]
        self.ps.ps_get_hyp.argtypes=[c.c_void_p,c.POINTER(c.c_int32),c.POINTER(c.c_char_p)]
        self.ps.ps_get_hyp.restype=c.c_char_p
        model=Path('/usr/share/pocketsphinx/model/en-us')
        if not (model/'en-us').is_dir(): raise RuntimeError('Install pocketsphinx-en-us for offline voice.')
        args=[b'robot_voice',b'-hmm',str(model/'en-us').encode(),b'-dict',str(model/'cmudict-en-us.dict').encode(),
              b'-samprate',b'16000',b'-logfn',str(log_path).encode(),b'-bestpath',b'yes',b'-beam',b'1e-80',b'-pbeam',b'1e-80',b'-wbeam',b'1e-60']
        argv=(c.c_char_p*len(args))(*args)
        config=self.base.cmd_ln_parse_r(None,self.ps.ps_args(),len(args),argv,1)
        if not config: raise RuntimeError('PocketSphinx configuration failed')
        self.decoder=self.ps.ps_init(config); self.base.cmd_ln_free_r(config)
        if not self.decoder: raise RuntimeError('PocketSphinx decoder failed')

    def decode(self,pcm,challenge,expected=None):
        if len(pcm)<3200 or len(pcm)>320000 or len(pcm)%2:
            raise ValueError('Record between 0.1 and 10 seconds of 16 kHz PCM')
        # A command must include this request's unpredictable spoken challenge.
        spoken={'start':'go','stop':'stop','shutdown':'shutdown','sleep':'sleep','wake':'wake',
                'present':'present','reset':'reset','disturb':'disturb'}
        choices=spoken[expected] if expected in spoken else ' | '.join(spoken.values())
        vocabulary='blue | green | red | gold | one | two | three | four | five | six | seven | eight | nine'
        grammar=f'#JSGF V1.0; grammar robot; <word> = {vocabulary}; public <command> = (robot ({choices}) <word> <word> <word> <word>) | ([robot] (stop | shutdown));'
        if self.ps.ps_set_jsgf_string(self.decoder,b'robot',grammar.encode())<0:
            raise RuntimeError('Speech grammar setup failed')
        self.ps.ps_set_search(self.decoder,b'robot')
        if self.ps.ps_start_utt(self.decoder,None)<0: raise RuntimeError('Speech decoder could not start')
        samples=(c.c_int16*(len(pcm)//2)).from_buffer_copy(pcm)
        self.ps.ps_process_raw(self.decoder,samples,len(samples),0,1)
        self.ps.ps_end_utt(self.decoder)
        score=c.c_int32(); utt=c.c_char_p()
        result=self.ps.ps_get_hyp(self.decoder,c.byref(score),c.byref(utt))
        text='' if not result else result.decode()
        if text in {'stop','robot stop'}: return 'stop',text
        if text in {'shutdown','robot shutdown'}: return 'shutdown',text
        text=text.replace('robot go ', 'robot start ')
        parts=text.split()
        action=parts[1] if len(parts)>=2 and parts[0]=='robot' and ' '.join(parts[2:])==challenge else None
        return action,text

    def close(self):
        if self.decoder: self.ps.ps_free(self.decoder); self.decoder=None
