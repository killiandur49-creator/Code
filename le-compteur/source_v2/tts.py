import sys, os, wave, subprocess, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lines import L
from piper import PiperVoice, SynthesisConfig
V="/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/dl/voice/"
VOICES={"leo":("tom-medium",None,1.0,1.0),"armand":("upmc-medium",1,1.15,0.86),"maxime":("gilles-low",None,0.8,1.0),
        "ines":("siwis-medium",None,1.0,1.0),"samy":("tom-medium",None,1.0,1.14)}
loaded={}
def voice(n):
    if n not in loaded: loaded[n]=PiperVoice.load(V+f"vits-piper-fr_FR-{n}/fr_FR-{n}.onnx")
    return loaded[n]
os.makedirs("vo",exist_ok=True)
SR=44100
out={}
for part,shots in L.items():
    for sid,t0,t1,lines in shots:
        for i,(off,spk,tts,sub,kw) in enumerate(lines):
            name,spkid,ls,pitch=VOICES[spk]
            raw=f"vo/raw_{part}_{sid}_{i}.wav"
            with wave.open(raw,"wb") as w:
                voice(name).synthesize_wav(tts,w,syn_config=SynthesisConfig(speaker_id=spkid,length_scale=ls,noise_scale=0.72,noise_w_scale=0.85))
            fin=f"vo/p{part}_{sid}_{i}.wav"
            af=f"aresample={SR}"
            if pitch!=1.0: af=f"rubberband=pitch={pitch}:formant=preserved,aresample={SR}"
            af+=",silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
            subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",af,"-ac","1","-ar",str(SR),fin],check=True)
            with wave.open(fin) as w: d=w.getnframes()/w.getframerate()
            nxt = lines[i+1][0] if i+1<len(lines) else (t1-t0)
            room = nxt-off-0.1
            out[f"{part}_{sid}_{i}"]=dict(dur=d,room=room)
            flag = "  <-- OVER x%.2f"%(d/room) if d>room else ""
            print(f"P{part}-{sid}.{i} {spk:7s} dur={d:5.2f} room={room:5.2f}{flag}")
json.dump(out,open("vo/durs.json","w"),indent=1)
