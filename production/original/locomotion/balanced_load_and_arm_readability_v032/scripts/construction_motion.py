"""Rough construction action: 32frames/30fps, two alternating steps.
V030 silhouette families retained; authored travel and exact polygon-rocker contacts.
This is an editable construction test, not an approved finished cycle.
"""
from pathlib import Path
import math,json,copy
import pose_keys as K
P=Path(__file__).resolve().parents[1];PER=32.;THIGH=K.THIGH;SHIN=K.SHIN
B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text())
V={s:[[(v[0]-d['flat_bone'][0][3])*K.BOOT_SCALE_X,(v[2]-d['flat_bone'][2][3])*K.BOOT_SCALE_Z] for v in d['vertices']] for s,d in B.items()}
def rot(v,a):c=math.cos(a);s=math.sin(a);return [c*v[0]+s*v[1],-s*v[0]+c*v[1]]
def pchip(xs,ys,x,ends=None):
    n=len(xs);h=[xs[i+1]-xs[i] for i in range(n-1)];d=[(ys[i+1]-ys[i])/h[i] for i in range(n-1)];m=[0.]*n
    for i in range(1,n-1):
        if d[i-1]*d[i]>0:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i])
    m[0]=d[0];m[-1]=d[-1]
    if ends:m[0],m[-1]=ends
    i=max(0,min(n-2,next((i for i in range(n-1) if x<=xs[i+1]),n-2)));t=max(0,min(1,(x-xs[i])/h[i]));return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h[i]*m[i+1]
def active(s,a):return min(range(len(V[s])),key=lambda j:rot(V[s][j],a)[1])
def compile_roll(s,sign):
    first=active(s,sign*1e-7);anchor=[V[s][first][0],0.];seq=[(0.,first,anchor[:])];last=first
    for i in range(1,5001):
        a=sign*math.radians(80)*i/5000;j=active(s,a)
        if j!=last:
            dv=[V[s][j][k]-V[s][last][k] for k in [0,1]];edge=math.atan2(dv[1],dv[0])
            while edge>math.pi/2:edge-=math.pi
            while edge<-math.pi/2:edge+=math.pi
            r=rot(dv,edge);anchor=[anchor[0]+r[0],0.];seq.append((edge,j,anchor[:]));last=j
    return seq
ROLL={(s,sgn):compile_roll(s,sgn) for s in V for sgn in [-1,1]}
def rolling(s,a,flat):
    _,j,anchor=ROLL[s,1 if a>=0 else -1][0]
    for edge,k,anc in ROLL[s,1 if a>=0 else -1][1:]:
        if abs(a)+1e-9>=abs(edge):j,anchor=k,anc
        else:break
    r=rot(V[s][j],a);return [flat+anchor[0]-r[0],-r[1]],{'vertex':j,'anchor_x':flat+anchor[0]}
NEAR_FLAT=.150-rolling('near',math.radians(-10),0)[0][0]
FAR_PREV_FLAT=-.170-rolling('far',math.radians(40),0)[0][0]
STEP=NEAR_FLAT-FAR_PREV_FLAT;STRIDE=2*STEP
RQ=[0,3,9,12,16,19,25,28]
RD=[0,NEAR_FLAT-.115,NEAR_FLAT+.025,NEAR_FLAT+rolling('near',math.radians(30),0)[0][0]+.035,STEP,NEAR_FLAT+STEP-.115,NEAR_FLAT+STEP+.025,NEAR_FLAT+STEP+rolling('far',math.radians(30),0)[0][0]+.035]
def root(q):
    # Constant ground travel; body/foot spacing carries the action, with no camera-speed pulse.
    return q*STRIDE/PER
def stance_angle(t):return math.radians(pchip([0,3,9,12,16,19,20],[-10,0,0,30,40,44,45],t))
def foot(s,q):
    onset=0 if s=='near' else 16.;n=math.floor((q-onset)/PER);start=onset+n*PER;t=q-start;flat=(NEAR_FLAT if s=='near' else NEAR_FLAT+STEP)+n*STRIDE
    if t<=20:
        a=stance_angle(t);A,meta=rolling(s,a,flat);return {'A':A,'angle':a,'mode':'CONTACT','clearance':0.,'meta':meta}
    a0=stance_angle(20);A0,_=rolling(s,a0,flat);a1=stance_angle(0);A1,_=rolling(s,a1,flat+STRIDE);eps=.001
    vx0=(rolling(s,stance_angle(20),flat)[0][0]-rolling(s,stance_angle(20-eps),flat)[0][0])/eps;vx1=(rolling(s,stance_angle(eps),flat+STRIDE)[0][0]-A1[0])/eps
    ax=pchip([20,25,28,32],[A0[0],root(start+25)+.065,root(start+28)+.105,A1[0]],t,(vx0,vx1))
    a=pchip([20,22,25,28,30,32],[a0,math.radians(38),math.radians(30),math.radians(-14),math.radians(-17),a1],t,((stance_angle(20)-stance_angle(20-eps))/eps,(stance_angle(eps)-stance_angle(0))/eps))
    clear=pchip([20,22,25,28,30,32],[0,.040,.095,.055,.025,0],t,(0,0));az=clear-min(rot(v,a)[1] for v in V[s]);return {'A':[ax,az],'angle':a,'mode':'SWING','clearance':clear,'meta':{}}
KEYS=copy.deepcopy(K.POSES)
KEYS[1]['waist'][1]=.715;KEYS[1]['rib'][1]=.891
KEYS[3]['waist'][1]=.811;KEYS[3]['rib'][1]=.994;KEYS[3]['hem_front'][0]=.075;KEYS[3]['near_arm'][1]=29;KEYS[3]['near_arm'][2]=14
FIELDS=['hip','neck','waist','rib','hem_front','hem_back','near_arm','far_arm'];SCALARS=['near_shoulder_x','far_shoulder_x']
poses=[]
for j in range(8):
    p=copy.deepcopy(KEYS[j%4])
    if j>=4:
        p['near_arm'],p['far_arm']=p['far_arm'],p['near_arm']
    poses.append(p)
def cyc(vals,q):return pchip([x-PER for x in RQ]+RQ+[x+PER for x in RQ],vals*3,q%PER)
# Whole body anchors authored separately for each landing. Exact V031 sole/travel
# evaluator above is retained. Screen-space mass spacing is the target here.
BODY=[
 {'hip':[0,.590],'neck':[.033,1.074],'waist':[.004,.756],'rib':[.018,.928],'hem_front':[.089,.635],'hem_back':[-.098,.578]},
 {'hip':[.030,.568],'neck':[.080,1.046],'waist':[.075,.715],'rib':[.089,.891],'hem_front':[.120,.612],'hem_back':[-.064,.553]},
 {'hip':[0,.600],'neck':[.025,1.100],'waist':[0,.767],'rib':[.018,.946],'hem_front':[.086,.644],'hem_back':[-.096,.587]},
 {'hip':[.005,.633],'neck':[.038,1.132],'waist':[.015,.808],'rib':[.030,.991],'hem_front':[.075,.677],'hem_back':[-.089,.619]},
 {'hip':[.044,.584],'neck':[.052,1.076],'waist':[.044,.750],'rib':[.050,.926],'hem_front':[.119,.627],'hem_back':[-.062,.572]},
 {'hip':[.052,.565],'neck':[.088,1.048],'waist':[.080,.712],'rib':[.093,.891],'hem_front':[.136,.608],'hem_back':[-.046,.550]},
 {'hip':[0,.598],'neck':[.025,1.099],'waist':[0,.765],'rib':[.018,.944],'hem_front':[.086,.642],'hem_back':[-.096,.585]},
 {'hip':[-.030,.629],'neck':[.025,1.131],'waist':[.002,.808],'rib':[.018,.988],'hem_front':[.062,.673],'hem_back':[-.108,.615]}
]
def body_anchors(q):
    return {k:[cyc([v[k][i] for v in BODY],q) for i in range(2)] for k in BODY[0]}
def evaluate(q):
    p={k:[cyc([v[k][i] for v in poses],q) for i in range(len(poses[0][k]))] for k in FIELDS};p.update({k:cyc([v[k] for v in poses],q) for k in SCALARS});p['frame']=1+q;p['name']='ROUGH_BREAKDOWN'
    p.update(body_anchors(q))
    # No reach clamp: additional explicit support-side pelvis breakdowns retain length.
    hq=[0,3,8,9,10,11,12,13,14,15,16,19,20,21,24,25,26,27,28,29,30,31]
    hx=[0,.030,.002,0,.002,.005,.005,.016,.030,.042,.044,.052,.040,.025,.003,0,-.008,-.026,-.030,-.024,-.010,-.003]
    hz=[.590,.568,.596,.600,.606,.619,.631,.621,.608,.593,.584,.565,.560,.567,.594,.598,.604,.614,.629,.623,.612,.599]
    p['hip']=[pchip([x-32 for x in hq]+hq+[x+32 for x in hq],vals*3,q%32) for vals in [hx,hz]]
    # Foreground reaching-side arm leads forward; far arm supplies a rear silhouette
    # while the near forearm crosses the coat. Independent shapes, not a side swap.
    # Return swing lags the second body-UP: carry partner-side hand through F27,
    # then cross the coat deliberately instead of snapping backward at F29.
    nq=[0,3,9,12,16,19,25,26,28,30]
    near=[[-15,-6,-2],[-18,-6,-2],[-5,12,4],[10,29,14],[17,35,14],[16,36,18],[12,34,12],[10,32,12],[-6,8,2],[-16,-7,-3]]
    far=[[5,18,7],[6,20,8],[5,18,6],[-22,-11,-2],[-30,-30,-14],[-30,-27,-14],[-26,-30,-12],[10,29,14]]
    p['near_arm']=[pchip([x-32 for x in nq]+nq+[x+32 for x in nq],[v[i] for v in near]*3,q%32) for i in range(3)];p['far_arm']=[cyc([v[i] for v in far],q) for i in range(3)]
    # Foreground hand is deliberately separated from hem at UP; overlaps elsewhere stay anatomical.
    d=root(q);r={'q':q,'D':d,'H':p['hip'],'neck':p['neck'],'legs':{}};margins={}
    for s,off in [('near',.018),('far',-.022)]:
        H=[p['hip'][0]+off,p['hip'][1]];f=foot(s,q);A=[f['A'][0]-d,f['A'][1]];dist=math.hypot(A[0]-H[0],A[1]-H[1]);margins[s]=THIGH+SHIN-dist
        if dist>=THIGH+SHIN:Knee=None
        else:Knee=K.knee(H,A)
        VV=[[f['A'][0]+rot(v,f['angle'])[0]-d,f['A'][1]+rot(v,f['angle'])[1]] for v in V[s]]
        r['legs'][s]={'hip':H,'knee':Knee,'ankle':A,'world_ankle':f['A'],'angle':f['angle'],'mode':f['mode'],'sole_clearance':min(v[1] for v in VV),'boot_vertices':VV,'contact':f['meta']}
    return p,r,margins
if __name__=='__main__':
    rows=[evaluate(i/4) for i in range(129)];bad=[{'q':r['q'],'margins':m} for p,r,m in rows if min(m.values())<.0003];report={'period_frames':PER,'fps':30,'step_m':STEP,'stride_m':STRIDE,'root_knots':[[0,0],[32,STRIDE]],'root_curve':'LINEAR; slope stride/32 per frame','minimum_reach_margin_m':min(v for p,r,m in rows for v in m.values()),'bad_samples':bad};(P/'evidence/INITIAL_MOTION_MODEL_CHECK.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

