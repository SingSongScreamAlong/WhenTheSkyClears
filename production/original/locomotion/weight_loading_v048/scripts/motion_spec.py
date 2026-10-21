"""v048 support-loading specification; pure NumPy, shared by planning and native build."""
import math
import numpy as np
PERIOD=32.;STRIDE=.78;SPEED=.73125;STANCE=18.8;LANDING_X=.185
PHASE={'BOY':0.,'GIRL':2.};CHAR={}
def configure(data):
 global CHAR
 CHAR=data
 for who,d in CHAR.items():
  d['offsets_np']=np.array(d['boot_offsets'],dtype=float);z=d['offsets_np'][:,2].min();d['heel_x']=float(d['offsets_np'][d['offsets_np'][:,2]<=z+1e-6,0].min())
  points=sorted(set((float(p[0]),float(p[2])) for p in d['offsets_np']));lower=[]
  for p in points:
   while len(lower)>1:
    a,b=lower[-2:];cross=(b[0]-a[0])*(p[1]-b[1])-(b[1]-a[1])*(p[0]-b[0])
    if cross>1e-12:break
    lower.pop()
   lower.append(p)
  arc=[0.]
  for a,b in zip(lower[:-1],lower[1:]):arc.append(arc[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
  d['sole_hull']=lower;d['sole_arc_np']=np.interp(d['offsets_np'][:,0],[p[0] for p in lower],arc)
  Q=rotate(d['offsets_np'],math.radians(12));ids=np.flatnonzero(Q[:,2]<=Q[:,2].min()+1e-7);d['landing_heel_x']=float(d['offsets_np'][ids,0].mean());d['landing_heel_arc']=float(d['sole_arc_np'][ids].mean())
def D(f):return STRIDE*(f-1)/PERIOD
def ease3(u):u=max(0,min(1,u));return u*u*(3-2*u)
def ease5(u):u=max(0,min(1,u));return u*u*u*(10+u*(-15+6*u))
def rotate(v,beta):
 c=math.cos(beta);s=math.sin(beta);a=np.array(v,dtype=float);out=a.copy();out[...,0]=c*a[...,0]-s*a[...,2];out[...,2]=s*a[...,0]+c*a[...,2];return out
def hermite(t,keys):
 for a,b in zip(keys[:-1],keys[1:]):
  if a[0]<=t<=b[0]:
   x0,y0,m0=a;x1,y1,m1=b;h=x1-x0;u=(t-x0)/h;return (2*u**3-3*u*u+1)*y0+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*y1+(u**3-u*u)*h*m1
 return keys[0][1] if t<keys[0][0] else keys[-1][1]
def hip(g,who):
 phi=math.tau*(g-1)/PERIOD;q=(g-1)%16
 # Slow initial rise while the knee accepts load; then advance over the foot.
 # This keeps one low/high per half-step, with LESS total excursion than v047.
 z=CHAR[who]['hip_rest_z_m']-.0295+hermite(q,[(0,0,0),(4,.004,.002),(9.5,.0215,0),(16,0,0)])
 return np.array([.0015*math.sin(2*phi),0,z])
def posture(g,who):
 q=(g-1)%16;phi=math.tau*(g-1)/32;lean=hermite(q,[(0,2.2,-.15),(2.75,1.4,0),(6.5,2.15,.18),(12,2.75,0),(16,2.2,-.15)])
 if who=='GIRL':lean=2.5+(lean-2.2)*.85
 return {'pelvis_degrees':.25*math.sin(2*phi+.2),'chest_degrees':lean,'head_degrees':(1 if who=='BOY' else 1.3)+.20*math.sin(2*phi-.25)}
def angle(q):
 if q<4.5:return math.radians(12)*(1-ease3(q/4.5))
 if q<10.5:return 0.
 return -math.radians(26)*ease3((q-10.5)/(STANCE-10.5))
def support_geometry(who,beta):
 d=CHAR[who];Q=rotate(d['offsets_np'],beta);z=float(Q[:,2].min());inds=np.flatnonzero(Q[:,2]<=z+1e-7);p=Q[inds].mean(axis=0);flatx=float(d['offsets_np'][inds,0].mean());return z,p,flatx,inds.tolist()
def stance(g,who,side,q=None):
 start=1. if side=='near' else 17.;q=(g-start)%PERIOD if q is None else q;c=g-q;beta=angle(q);z,p,flatx,inds=support_geometry(who,beta);d=CHAR[who];heelworld=D(c)+LANDING_X+d['landing_heel_x'];roll=float(d['sole_arc_np'][inds].mean())-d['landing_heel_arc'];xworld=heelworld+roll;a=np.array([xworld-p[0]-D(g),0,-z]);return a,beta,{'stance':True,'contact_start':c,'support_indices':inds,'expected_support_x_plus_D':xworld,'phase_frame':q,'sole_roll_arc_m':roll,'rest_contact_x_m':flatx}
def foot(g,who,side):
 start=1. if side=='near' else 17.;q=(g-start)%PERIOD;c=g-q
 if q<=STANCE+1e-8:return stance(g,who,side,q)
 u=(q-STANCE)/(PERIOD-STANCE);a0=stance(c+STANCE,who,side,STANCE)[0];a1=stance(c+PERIOD,who,side,0)[0];duration=PERIOD-STANCE;v=-STRIDE/PERIOD;x=a0[0]+v*duration*u+(a1[0]-a0[0]-v*duration)*ease3(u)
 beta=math.radians(-26+30*ease5(u/.50)) if u<.50 else math.radians(4+8*ease5((u-.5)/.5));z=support_geometry(who,beta)[0];clearance=.040*(ease3(u/.28) if u<=.28 else 1-ease3((u-.28)/.72))
 return np.array([x,0,clearance-z]),beta,{'stance':False,'phase_frame':q,'swing_u':u,'authored_clearance_m':clearance}
def knee_angle(H,A,who):
 l1=CHAR[who]['thigh_m'];l2=CHAR[who]['shin_m'];d=float(np.linalg.norm(A-H));return math.degrees(math.acos(max(-1,min(1,(d*d-l1*l1-l2*l2)/(2*l1*l2)))))
