"""Retarget licensed Quaternius motion to the original 2D child proportions.
The stock adult mannequin never renders in the game. Its motion is a guide;
all child bones, hand contacts, silhouettes, clothing and head artwork are local.
"""
from pathlib import Path
import struct,json,hashlib
import numpy as np
P=Path(__file__).resolve().parents[1]
source=next(p for p in (P/'character_sources/universal-animation-library').rglob('*.glb') if '_RM' not in p.name)
raw=source.read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:]
nodes=doc['nodes'];names={n['name']:i for i,n in enumerate(nodes)};parents={c:i for i,n in enumerate(nodes) for c in n.get('children',[])}
cache={}
def acc(i):
    if i in cache:return cache[i]
    a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
    dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
    count={'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    off=v.get('byteOffset',0)+a.get('byteOffset',0)
    result=np.ndarray((a['count'],count),dtype=dtype,buffer=binary,offset=off,strides=(v.get('byteStride',np.dtype(dtype).itemsize*count),np.dtype(dtype).itemsize)).copy()
    cache[i]=result;return result
def quat(q):
    x,y,z,w=q/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def pose(animation,t):
    values={}
    for ch in animation['channels']:
        s=animation['samplers'][ch['sampler']];ts=acc(s['input'])[:,0];vs=acc(s['output']);j=int(np.clip(np.searchsorted(ts,t)-1,0,len(ts)-2));f=float(np.clip((t-ts[j])/max(1e-7,ts[j+1]-ts[j]),0,1));a=vs[j];b=vs[j+1]
        if ch['target']['path']=='rotation' and np.dot(a,b)<0:b=-b
        val=a*(1-f)+b*f
        if ch['target']['path']=='rotation':val/=np.linalg.norm(val)
        values[(ch['target']['node'],ch['target']['path'])]=val
    globals={}
    def world(i):
        if i in globals:return globals[i]
        node=nodes[i];m=np.eye(4);q=values.get((i,'rotation'),node.get('rotation',[0,0,0,1]));scale=values.get((i,'scale'),node.get('scale',[1,1,1]));m[:3,:3]=quat(np.array(q))*np.array(scale)[None,:];m[:3,3]=values.get((i,'translation'),node.get('translation',[0,0,0]));globals[i]=world(parents[i])@m if i in parents else m;return globals[i]
    return {name:world(i)[:3,3] for name,i in names.items()}
clips=['Idle_Loop','Walk_Loop','Jog_Fwd_Loop','Sprint_Loop','Crouch_Idle_Loop','Crouch_Fwd_Loop','Jump_Start','Jump_Loop','Jump_Land','Interact','Fixing_Kneeling','Hit_Head','Sitting_Idle_Loop']
out={'source':'Quaternius Universal Animation Library, free Standard, original archive License.txt CC0; current site QAL also archived in character_sources.','source_sha256':hashlib.sha256(raw).hexdigest(),'fps':30,'joints':['hip','shoulder','head','near_knee','near_foot','far_knee','far_foot','near_elbow','near_hand','far_elbow','far_hand','near_toe','far_toe'],'clips':{}}
idle=pose(next(a for a in doc['animations'] if a['name']=='Idle_Loop'),0)
base_hip=float(idle['pelvis'][1]);scale=35/base_hip
def direction(v,length):
    d=np.array([-v[2],-v[1]])
    mag=np.linalg.norm(d);return d/max(.00001,mag)*length
def retarget(p):
    hip=np.array([0,-p['pelvis'][1]*scale]);shoulder=hip+direction(p['spine_03']-p['pelvis'],23);head=shoulder+direction(p['Head']-p['spine_03'],16)
    joints={'hip':hip,'shoulder':shoulder,'head':head}
    for side,label,offset in [('r','near',2),('l','far',-2)]:
        knee=hip+np.array([offset,0])+direction(p['calf_'+side]-p['thigh_'+side],18)
        foot=knee+direction(p['foot_'+side]-p['calf_'+side],17)
        elbow=shoulder+direction(p['lowerarm_'+side]-p['upperarm_'+side],13)
        hand=elbow+direction(p['hand_'+side]-p['lowerarm_'+side],13)
        toe=foot+direction(p['ball_'+side]-p['foot_'+side],9)
        joints.update({label+'_knee':knee,label+'_foot':foot,label+'_elbow':elbow,label+'_hand':hand,label+'_toe':toe})
    # Reference feet are placed on a common baseline; child proportions stay fixed.
    floor=max(joints['near_foot'][1],joints['far_foot'][1])
    for k in joints:joints[k][1]-=floor
    return [[round(float(v),4) for v in joints[k]] for k in out['joints']]
for a in doc['animations']:
    if a['name'] not in clips:continue
    duration=max(float(acc(s['input'])[-1,0]) for s in a['samplers']);frames=[]
    for t in np.linspace(0,duration,max(2,round(duration*30)),endpoint=False):frames.append(retarget(pose(a,float(t))))
    out['clips'][a['name']]={'duration':duration,'frames':frames}
    print(a['name'],round(duration,3),len(frames),flush=True)
(P/'assets/motion/child_motion.json').write_text(json.dumps(out,separators=(',',':')))
(P/'evidence/animation_retarget.json').write_text(json.dumps({'source':str(source.relative_to(P)),'clips':list(out['clips']),'sample_rate':30,'source_height_m':base_hip*2,'child_pelvis_pixels':35,'projection':'Strict side view, -Z / -Y. Constant child limb lengths. Foot baseline corrected. Head, clothing and paired care remain authored locally.','stock_mesh_used_as_final_child':False},indent=2))
