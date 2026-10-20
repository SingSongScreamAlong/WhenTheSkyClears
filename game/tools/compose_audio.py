"""Original procedural score and foley, with deterministic editable synthesis."""
from pathlib import Path
import numpy as np, wave
P=Path(__file__).resolve().parents[1]/'assets/audio'; P.mkdir(exist_ok=True)
sr=32000; rng=np.random.default_rng(271019)
def save(name,signal):
    peak=max(.96,float(np.max(np.abs(signal))))
    pcm=np.int16(np.clip(signal/peak,-1,1)*32767)
    with wave.open(str(P/(name+'.wav')),'wb') as w:
        w.setnchannels(1 if pcm.ndim==1 else 2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
t=np.arange(sr*48)/sr
# Integer-period tones and cyclic envelopes give a seamless 48-second loop.
pad=np.zeros_like(t)
for freq,amp,phase in [(73.4167,.13,0),(110,.055,.6),(146.8333,.04,1.2),(174.625,.045,2.3),(220,.03,1.1)]:
    f=round(freq*48)/48
    pad+=np.sin(2*np.pi*f*t+phase)*amp*(.7+.3*np.sin(2*np.pi*t/48+phase))
noise=rng.normal(0,1,t.size); wind=np.convolve(noise,np.ones(140)/140,'same')*.19
signal=pad+wind
save('horizon',np.stack([signal, np.roll(signal,113)*.95],axis=-1)*.55)
t=np.arange(int(sr*.16))/sr
save('step',rng.normal(0,1,t.size)*np.exp(-t*43)*.32+np.sin(2*np.pi*92*t)*np.exp(-t*55)*.21)
t=np.arange(int(sr*.9))/sr
save('collect',(np.sin(2*np.pi*440*t)+.4*np.sin(2*np.pi*660*t))*np.exp(-t*5)*np.minimum(t*30,1)*.16)
t=np.arange(sr*2)/sr
save('warning',(np.sin(2*np.pi*(147*t+3*np.sin(t*4)))+.25*np.sin(2*np.pi*294*t))*np.sin(np.pi*np.minimum(t/2,1))**2*.18)
t=np.arange(sr*3)/sr
n=rng.normal(0,1,t.size); low=np.convolve(n,np.ones(120)/120,'same')
save('blast',(low*2+np.sin(2*np.pi*(47*t-5*t*t))*.16)*np.exp(-t*2)*np.minimum(t*100,1)*.7)
t=np.arange(int(sr*.8))/sr
save('wheel',(np.sin(2*np.pi*(80*t+10*t*t))*.1+rng.normal(0,1,t.size)*.075)*np.sin(np.pi*t/.8)**2)
print('Original score and five foley cues saved.')
