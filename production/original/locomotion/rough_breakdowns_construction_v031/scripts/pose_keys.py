"""Four whole-body silhouette drawings, not a cycle or retargeted contour series.
Metres, X forward, Z up. Shared anatomical segment lengths for both legs.
"""
import math,json
THIGH=.260;SHIN=.260;BOOT_SCALE_X=.78;BOOT_SCALE_Z=.90
POSES=[
 {'frame':1,'name':'CONTACT','hip':[0,.594],'neck':[.033,1.085],
  'near_foot':[.150,-10,0],'far_foot':[-.170,25,0],
  'near_arm':[-15,-6,-2],'far_arm':[5,18,7],
  'near_shoulder_x':-.095,'far_shoulder_x':.045,
  'waist':[.004,.760],'rib':[.018,.935],'hem_front':[.089,.639],'hem_back':[-.098,.582]},
 {'frame':4,'name':'LOADED_DOWN','hip':[.030,.568],'neck':[.080,1.048],
  'near_foot':[.115,0,0],'far_foot':[-.195,33,0],
  'near_arm':[-18,-6,-2],'far_arm':[6,20,8],
  'near_shoulder_x':-.095,'far_shoulder_x':.045,
  'waist':[.075,.725],'rib':[.089,.902],'hem_front':[.120,.612],'hem_back':[-.064,.553]},
 {'frame':11,'name':'PASSING','hip':[0,.610],'neck':[.025,1.110],
  'near_foot':[-.025,0,0],'far_foot':[.065,30,.095],
  'near_arm':[-5,12,4],'far_arm':[5,18,6],
  'near_shoulder_x':-.070,'far_shoulder_x':.045,
  'waist':[.000,.777],'rib':[.018,.956],'hem_front':[.086,.654],'hem_back':[-.096,.597]},
 {'frame':13,'name':'UP','hip':[.005,.636],'neck':[.038,1.140],
  'near_foot':[-.035,30,0],'far_foot':[.105,-14,.055],
  'near_arm':[10,24,8],'far_arm':[-22,-11,-2],
  'near_shoulder_x':-.060,'far_shoulder_x':-.035,
  'waist':[.015,.803],'rib':[.030,.986],'hem_front':[.095,.680],'hem_back':[-.089,.622]}
]
def rotate(v,a):c=math.cos(a);s=math.sin(a);return [c*v[0]+s*v[1],-s*v[0]+c*v[1]]
def knee(H,A):
    dx=A[0]-H[0];dz=A[1]-H[1];d=math.hypot(dx,dz)
    if not abs(THIGH-SHIN)<d<THIGH+SHIN:raise ValueError(('pose unreachable',H,A,d))
    e=[dx/d,dz/d];t=(THIGH*THIGH-SHIN*SHIN+d*d)/(2*d);h=math.sqrt(THIGH*THIGH-t*t)
    return [H[0]+e[0]*t-e[1]*h,H[1]+e[1]*t+e[0]*h]
def foot(side,spec,boots):
    x,degrees,clearance=spec;a=math.radians(degrees);d=boots[side];flat=[d['flat_bone'][0][3],d['flat_bone'][2][3]]
    v=[rotate([(p[0]-flat[0])*BOOT_SCALE_X,(p[2]-flat[1])*BOOT_SCALE_Z],a) for p in d['vertices']]
    az=clearance-min(p[1] for p in v);return [x,az],[[x+p[0],az+p[1]] for p in v]
def analyze(boots):
    out=[]
    for p in POSES:
        r={'frame':p['frame'],'name':p['name'],'hip':p['hip'],'neck':p['neck'],'legs':{}}
        for side,offset in [('near',.018),('far',-.022)]:
            H=[p['hip'][0]+offset,p['hip'][1]];A,V=foot(side,p[side+'_foot'],boots);K=knee(H,A)
            r['legs'][side]={'hip':H,'knee':K,'ankle':A,'sole_clearance':min(v[1] for v in V),'boot_length_x':max(v[0] for v in V)-min(v[0] for v in V),'boot_vertices':V}
        out.append(r)
    return out
if __name__=='__main__':
    from pathlib import Path
    P=Path(__file__).resolve().parents[1];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());print(json.dumps([{**r,'legs':{s:{k:v for k,v in d.items() if k!='boot_vertices'} for s,d in r['legs'].items()}} for r in analyze(B)],indent=2))
