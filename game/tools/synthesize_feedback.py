"""Original non-musical rain and action textures. No recordings or samples used."""
from pathlib import Path
import wave,json,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1]/'assets/audio'
sr=32000;rng=np.random.default_rng(52026)
def save(name,a):
 a=np.asarray(a);a=np.clip(a,-.8,.8);pcm=np.int16(a*32767)
 with wave.open(str(P/(name+'.wav')),'wb') as w:
  w.setnchannels(1 if a.ndim==1 else a.shape[1]);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
 return {'sha256':hashlib.sha256((P/(name+'.wav')).read_bytes()).hexdigest(),'seconds':len(a)/sr,'peak':float(abs(a).max()),'origin':'Original deterministic noise/oscillator synthesis; no external sample, voice or melody.'}
def smooth(a,n):return sum(np.roll(a,j) for j in range(n))/n
n=sr*8;t=np.arange(n)/sr;noise=rng.normal(0,1,n)
# Circular filtering/modulation keeps loop boundaries continuous.
rain=(noise-smooth(noise,18))*.075*(.85+.15*np.cos(2*np.pi*t/8))
roof=smooth(noise,40)*.25
for second in [.3,1.4,2.8,4.1,5.7,7.1]:
 k=np.arange(int(sr*.13));e=np.exp(-k/sr*36);roof[(int(second*sr)+k)%n]+=np.sin(k/sr*2*np.pi*230)*e*.08
out={'rain_open':save('rain_open',np.stack([rain,np.roll(rain,1153)],axis=-1)),'rain_roof':save('rain_roof',np.stack([roof,np.roll(roof,827)],axis=-1))}
for name,duration,decay in [('cloth',.55,9),('bread',.65,12)]:
 t=np.arange(int(sr*duration))/sr;n=rng.normal(0,1,len(t));a=smooth(n,6)*np.sin(np.pi*np.minimum(t/duration,1))**2*np.exp(-t*decay)*.5
 a*= (.35 if name=='cloth' else .28)/max(float(abs(a).max()),.00001)
 out[name]=save(name,a)
(P/'FEEDBACK_PROVENANCE_v052.json').write_text(json.dumps({'generator':'tools/synthesize_feedback.py','seed':52026,'sample_rate':sr,'assets':out},indent=2))
print('Original rain and cloth textures generated.')
