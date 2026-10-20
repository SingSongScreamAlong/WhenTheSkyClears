"""Small sagittal retarget model using the unchanged native limb lengths/hulls.
Feet share fixed step placements; pelvis is a free whole-pose variable. No stretch.
"""
import numpy as np,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];DATA=json.loads((P/'reference/fbx_source_inspection.json').read_text());REST=json.loads((P/'reference/child_rest_bones.json').read_text());BOOT=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());PHASES=json.loads((P/'reference/SOURCE_PHASE_TIMING_v020.json').read_text())['phases'];ROWS={r['frame']:r for r in DATA['samples']};OLD=json.loads((P/'reference/v020_eight_pose_matching.json').read_text())[:8]
def v2(v):return np.array([v[0],v[2]],float)
def rotate(v,a):c=math.cos(a);s=math.sin(a);return np.array([c*v[0]+s*v[1],-s*v[0]+c*v[1]])
def src(f):
 loop=math.floor((f-2)/31);w=round(2+(f-2)%31,6);r=ROWS[w]
 return {n:{end:np.array([-d[end][1]+loop*1.5,d[end][2]],float) for end in ['head','tail']} for n,d in r['bones'].items()}
def direction(a,b):v=b-a;return v/np.linalg.norm(v)
def legangle(u):return math.atan2(u[0],-u[1])
def legunit(a):return np.array([math.sin(a),-math.cos(a)])
def wrap(a):return math.atan2(math.sin(a),math.cos(a))
LENS={s:(REST['thigh_'+s]['length'],REST['shin_'+s]['length']) for s in ['near','far']};SIDE={'near':'R','far':'L'}
V={s:np.array([[v[0],v[2]] for v in BOOT[s]['vertices']],float) for s in SIDE};AFLAT={s:np.array([BOOT[s]['flat_bone'][0][3],BOOT[s]['flat_bone'][2][3]],float) for s in SIDE}
def boot_active(s,a):z=-math.sin(a)*V[s][:,0]+math.cos(a)*V[s][:,1];return int(np.argmin(z))
def compile_roll(s,sign):
 first=boot_active(s,sign*1e-6);anchor=np.array([V[s][first,0],0.]);sequence=[(0.,first,anchor.copy())];last=first
 for a in np.linspace(0,sign*math.radians(85),3001)[1:]:
  j=boot_active(s,a)
  if j!=last:
   dv=V[s][j]-V[s][last];edge=math.atan2(dv[1],dv[0])
   while edge>math.pi/2:edge-=math.pi
   while edge<-math.pi/2:edge+=math.pi
   anchor=anchor+rotate(dv,edge);anchor[1]=0.;sequence.append((edge,j,anchor.copy()));last=j
 return sequence
ROLL={(s,sign):compile_roll(s,sign) for s in SIDE for sign in [-1,1]}
def rolling(s,a,x):
 seq=ROLL[s,1 if a>=0 else -1];_,j,anchor=seq[0]
 for edge,k,anc in seq[1:]:
  if abs(a)+1e-9>=abs(edge):j,anchor=k,anc
  else:break
 target=anchor+np.array([x,0.]);A=target+rotate(AFLAT[s]-V[s][j],a)
 return A,{'vertex':j,'pivot_flat_xz':V[s][j].tolist(),'anchor_xz':target.tolist(),'angle_rad':a,'flat_x':x}
def sole_clear(s,A,a):return A[1]+np.min(-math.sin(a)*(V[s][:,0]-AFLAT[s][0])+math.cos(a)*(V[s][:,1]-AFLAT[s][1]))
SOURCE=[]
for i,p in enumerate(PHASES):
 B=src(p['unwrapped_source_frame']);pel=math.atan2(*(B['Spine_01']['head']-B['Hips']['head']));off={s:rotate(v2(REST['thigh_'+s]['head'])-v2(REST['pelvis']['head']),pel) for s in SIDE};angs={}
 for s,ss in SIDE.items():angs[s]=np.array([legangle(direction(B['UpperLeg_'+ss]['head'],B['LowerLeg_'+ss]['head'])),legangle(direction(B['LowerLeg_'+ss]['head'],B['Ankle_'+ss]['head']))])
 SOURCE.append({'B':B,'pelvis':pel,'offset':off,'angles':angs,'feet':{s:next(v for v in OLD[i]['feet'] if v['side']==s) for s in SIDE}})
SWINGS=[(i,s) for i in range(8) for s in SIDE if SOURCE[i]['feet'][s]['mode']=='SWING'];DOUBLE=[0,1,4,5]
def ik(H,A,s):
 l1,l2=LENS[s];d=A-H;D=float(np.linalg.norm(d));e=d/max(D,1e-12);Dc=min(max(D,abs(l1-l2)+1e-6),l1+l2-1e-6);t=(l1*l1-l2*l2+Dc*Dc)/(2*Dc);h=math.sqrt(max(1e-10,l1*l1-t*t));n=np.array([-e[1],e[0]]);K=H+e*t+n*h;u=direction(H,K);v=direction(K,A)
 return np.array([legangle(u),legangle(v)]),K,D
def unpack(x):return x[:2],x[2:4],x[4:20].reshape(8,2),x[20:28].reshape(4,2),x[28:32]
def evaluate(x):
 steps,gains,Hs,swing,pitches=unpack(x);a,b=steps;results=[]
 for i,srcdata in enumerate(SOURCE):
  H=Hs[i];feet={};angles={};knees={};dist={}
  for s in SIDE:
   srcfoot=srcdata['feet'][s];origin=(0 if s=='near' else (-b if i<4 else a));hip=H+srcdata['offset'][s]
   if srcfoot['mode']=='SWING':
    j=SWINGS.index((i,s));up=swing[j,0];low=up-swing[j,1];l1,l2=LENS[s];K=hip+legunit(up)*l1;A=K+legunit(low)*l2;ang=pitches[j];meta={'mode':'SWING','angle_rad':ang};actual=np.array([up,low]);D=float(np.linalg.norm(A-hip))
   else:
    original=srcfoot['angle_rad'];ang=original*(gains[0] if original<0 else gains[1]);A,meta=rolling(s,ang,origin);meta['mode']='CONTACT_POLYGON_PIVOT';actual,K,D=ik(hip,A,s)
   meta['ankle_xz']=A.tolist();meta['clearance_m']=float(sole_clear(s,A,ang));feet[s]=meta;angles[s]=actual;knees[s]=K;dist[s]=D
  results.append({'hip':H,'feet':feet,'angles':angles,'knees':knees,'distance':dist})
 return results
def initial():
 gains=np.array([.65,.65]);ideal=[]
 for i,srcd in enumerate(SOURCE):
  h={}
  for s in SIDE:
   if srcd['feet'][s]['mode']=='SWING':continue
   p=srcd['feet'][s]['angle_rad'];A,_=rolling(s,p*gains[0 if p<0 else 1],0);l1,l2=LENS[s];u,v=srcd['angles'][s];h[s]=A-legunit(u)*l1-legunit(v)*l2-srcd['offset'][s]
  ideal.append(h)
 b=float(np.mean([ideal[i]['far'][0]-ideal[i]['near'][0] for i in [0,1]]));a=float(np.mean([ideal[i]['near'][0]-ideal[i]['far'][0] for i in [4,5]]));Hs=[]
 for i,h in enumerate(ideal):
  adjusted=[q+np.array([0 if s=='near' else (-b if i<4 else a),0]) for s,q in h.items()];Hs.append(np.mean(adjusted,axis=0))
 sw=[];pitches=[]
 for i,s in SWINGS:
  u,v=SOURCE[i]['angles'][s];sw.append([u,u-v]);pitches.append(min(math.radians(35),SOURCE[i]['feet'][s]['angle_rad']*.6))
 return np.r_[a,b,gains,np.array(Hs).ravel(),np.array(sw).ravel(),pitches]
def residual(x):
 steps,gains,Hs,sw,pitches=unpack(x);poses=evaluate(x);r=[]
 for i,p in enumerate(poses):
  srcd=SOURCE[i]
  for s in SIDE:
   diff=[wrap(a-b) for a,b in zip(p['angles'][s],srcd['angles'][s])];r.extend(np.array(diff)*.25)
   l1,l2=LENS[s];D=p['distance'][s];r.append(300*max(0,D-(l1+l2-.001)));r.append(300*max(0,abs(l1-l2)+.002-D))
   if p['feet'][s]['mode']=='SWING':r.append(300*max(0,.022-p['feet'][s]['clearance_m']));r.append(15*max(0,p['feet'][s]['clearance_m']-.060))
   else:r.extend([0.,0.])
  support=[s for s in SIDE if p['feet'][s]['mode']!='SWING'];A=[np.array(p['feet'][s]['ankle_xz']) for s in support]
  r.append(2*max(0,min(v[0] for v in A)-.12-Hs[i,0]));r.append(2*max(0,Hs[i,0]-max(v[0] for v in A)-.17))
 # Preserve recognizable down/passing/up order without a fixed pelvis height.
 for contact,load in [(0,1),(4,5)]:r.append(25*max(0,Hs[load,1]-Hs[contact,1]+(.004 if contact==0 else .0007)))
 for load,passing,up in [(1,2,3),(5,6,7)]:r.append(15*max(0,Hs[load,1]+.012-Hs[passing,1]));r.append(15*max(0,Hs[passing,1]+.001-Hs[up,1]))
 for i in range(7):r.append(10*max(0,Hs[i,0]+.0001-Hs[i+1,0]))
 # A soft source-derived rise/load pattern with a free common vertical offset.
 # This discourages a high-stepping/uneven torso while preserving free pelvis.
 zsrc=np.array([d['B']['Hips']['head'][1] for d in SOURCE]);profile=(zsrc-zsrc.mean())*.680922328;zbase=float(np.mean(Hs[:,1]-profile));r.extend(1.5*(Hs[:,1]-zbase-profile))
 # Weak regularity only. Global steps and pelvis heights are solved, not locked.
 r.extend(.018*(gains-np.array([.65,.65])));r.append(.03*(steps[0]-steps[1]))
 for j,(i,s) in enumerate(SWINGS):r.append(.025*(pitches[j]-min(math.radians(35),SOURCE[i]['feet'][s]['angle_rad']*.6)))
 return np.array(r)
def bounds():
 lo=np.full(32,-np.inf);hi=np.full(32,np.inf);lo[:2]=.20;hi[:2]=.65;lo[2:4]=.30;hi[2:4]=1.;lo[4:20:2]=-.5;hi[4:20:2]=1.2;lo[5:20:2]=.51;hi[5:20:2]=.65
 for j,(i,s) in enumerate(SWINGS):u,v=SOURCE[i]['angles'][s];lo[20+2*j]=u-math.radians(16);hi[20+2*j]=u+math.radians(16);lo[21+2*j]=max(.06,u-v-math.radians(25));hi[21+2*j]=u-v+math.radians(25)
 lo[28:32]=math.radians(-12);hi[28:32]=math.radians(45);return lo,hi
