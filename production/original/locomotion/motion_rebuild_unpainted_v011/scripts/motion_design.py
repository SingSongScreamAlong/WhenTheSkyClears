"""New six-second diagnostic, not a retime or reuse of rejected v010 motion.
World-space support feet drive leg construction. Each child has a separate root.
"""
import math
from mathutils import Vector,Matrix
FPS=24;N=144
def sm(a,b,t):
 u=max(0.,min(1.,(t-a)/(b-a)));return u*u*(3-2*u)
def curve(keys,t):
 if t<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if t<=b:return x+(y-x)*sm(a,b,t)
 return keys[-1][1]
def trajectory(keys,t):
 # Keys carry value AND velocity. Do not ease body travel to zero at each pose.
 if t<=keys[0][0]:return keys[0][1]
 for (a,x,v),(b,y,w) in zip(keys,keys[1:]):
  if t<=b:
   u=(t-a)/(b-a);d=b-a;return (2*u**3-3*u*u+1)*x+(u**3-2*u*u+u)*d*v+(-2*u**3+3*u*u)*y+(u**3-u*u)*d*w
 return keys[-1][1]+(t-keys[-1][0])*keys[-1][2]
ROOTS={
 'BOY':[(1,0,.0225),(13,.27,.0225),(23,.495,.0225),(27,.58,.016),(33,.70,.021),(40,.84,.014),(44,.89,.006),(51,.93,.004),(60,1.,.006),(66,1.055,.012),(78,1.20,.015),(94,1.45,.017),(109,1.71,.017),(124,1.96,.017),(139,2.21,.017),(144,2.293,.017)],
 'GIRL':[(1,.88,.0225),(13,1.15,.0225),(25,1.42,.020),(27,1.46,.012),(36,1.57,.008),(41,1.62,.006),(46,1.675,.002),(54,1.685,.001),(64,1.70,.0015),(72,1.73,.009),(82,1.93,.016),(98,2.18,.017),(113,2.43,.017),(128,2.68,.017),(143,2.93,.017),(144,2.947,.017)]}
PROPORTIONS={'BOY':{'height':1.45,'leg':(.285,.285),'arm':(.225,.215),'torso':(.18,.27),'head':(.155,.185),'ankle':.09,'hand':.070},'GIRL':{'height':1.369917744,'leg':(.27,.27),'arm':(.21,.20),'torso':(.17,.24),'head':(.145,.17),'ankle':.085,'hand':.067}}
# (toe-off,arrival,world ankle-X at flat,clearance). Toe scuff is a special first far arrival.
STEPS={('BOY','near'):[(3,13,.36,.040),(32,40,1.,.070),(82,94,1.52,.040),(111,124,2.02,.035)],('BOY','far'):[(16,24,.64,.045),(66,78,1.28,.042),(97,109,1.78,.038),(126,139,2.28,.035)],('GIRL','near'):[(2,13,1.24,.037),(32,41,1.75,.055),(86,98,2.25,.036),(116,128,2.75,.035)],('GIRL','far'):[(16,27,1.50,.036),(70,82,2.,.038),(101,113,2.5,.035),(131,143,3.,.034)]}
INITIAL={('BOY','near'):-.17,('BOY','far'):.10,('GIRL','near'):.71,('GIRL','far'):.98}
def roll_point(p,angle,pivot):return Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-pivot)@p
def foot(who,side,f):
 previous=INITIAL[who,side];events=STEPS[who,side];prev_end=-100;angle=0;pivot=Vector((.135,0,0));lift=0;state='flat';x=previous
 for i,(start,end,target,height) in enumerate(events):
  scuff=who=='BOY' and side=='far' and i==0
  if f<start:
   x=previous;state='flat';angle=.32*sm(start-4,start,f);pivot=Vector((.135,0,0))
   if prev_end>-100 and f<prev_end+3:angle=-.12*(1-sm(prev_end,prev_end+3,f));pivot=Vector((-.075,0,0));state='heel'
   if who=='BOY' and side=='far' and 27<=f<66:angle=.55*sm(44,62,f);state='toe' if angle>.01 else 'flat'
   if who=='GIRL' and side=='far' and 30<=f<70:angle=.40*sm(47,65,f);state='toe' if angle>.01 else 'flat'
   if angle>.01:state='toe'
   break
  if f<=end:
   u=(f-start)/(end-start);x=previous+(target-previous)*sm(0,1,u);lift=height*math.sin(math.pi*u)**1.1;state='swing'
   initial=.55 if who=='BOY' and side=='far' and i==1 else .40 if who=='GIRL' and side=='far' and i==1 else .32
   angle=curve([(0,initial),(.40,.035),(.72,.01),(1,.24 if scuff else -.12)],u);pivot=Vector((.135,0,0)).lerp(Vector((-.075,0,0)),sm(.35,.8,u)) if not scuff else Vector((.135,0,0))
   if f==end:state='toe_scuff' if scuff else 'heel'
   break
  previous=target;prev_end=end;x=target;nextstart=events[i+1][0] if i+1<len(events) else 1000
  if f<nextstart:
   if scuff and f<=27:angle=.24*(1-sm(24,27,f));pivot=Vector((.135,0,0));state='toe_scuff' if f<27 else 'flat';break
   # Continue loop to evaluate flat/roll interval before the following step.
   continue
 else:
  x=previous;angle=-.12*(1-sm(prev_end,prev_end+3,f));pivot=Vector((-.075,0,0));state='heel' if f<prev_end+3 else 'flat'
 transform=Matrix.Translation(Vector((x,0,lift)))@Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-pivot)
 ankle=transform@Vector((0,0,PROPORTIONS[who]['ankle']));ankle.y=-.052 if side=='near' else .052
 return {'x':x,'lift':lift,'angle':angle,'state':state,'matrix':transform,'ankle':ankle,'heel':transform@Vector((-.075,0,0)),'toe':transform@Vector((.135,0,0))}
def desired_hip_z(who,f):
 if who=='BOY':
  z=.636-sum(.023*math.exp(-((f-(c+2))/2.9)**2) for c in [13,78,94,109,124,139]);env=sm(21,24,f)*(1-sm(66,76,f));z=z*(1-env)+curve([(21,.625),(24,.61),(27,.57),(30,.53),(35,.56),(40,.57),(44,.47),(48,.49),(56,.56),(64,.61),(72,.625)],f)*env
 else:
  z=.616-sum(.020*math.exp(-((f-(c+2))/2.9)**2) for c in [13,27,41,82,98,113,128,143])
  env=sm(23,27,f)*(1-sm(66,76,f));z=z*(1-env)+curve([(25,.601),(29,.553),(33,.535),(38,.575),(41,.575),(44,.542),(49,.574),(56,.603),(64,.608),(72,.612)],f)*env
 return z
def softmin(a,b,k=.012):return min(a,b)-.25*k*max(0,1-abs(a-b)/k)**2
def two_bone(H,A,L1,L2):
 d=A-H;d.y=0;D=d.length
 if D>=L1+L2:raise ValueError(('leg reach violation',D,L1+L2))
 u=d.normalized();along=(L1*L1-L2*L2+D*D)/(2*D);h=math.sqrt(max(0,L1*L1-along*along));n=Vector((-u.z,0,u.x));return H+u*along+n*h
def angles(who,f):
 if who=='BOY':
  low=curve([(1,2),(21,4),(24,7),(27,12),(30,16),(35,13),(40,12),(44,16),(48,12),(56,7),(64,3),(72,2)],f);chest=curve([(1,4),(21,6),(24,9),(27,19),(30,27),(35,23),(40,18),(44,25),(48,21),(56,12),(64,7),(72,5)],f)
 else:low=curve([(1,1.5),(25,-4),(33,-3),(40,2),(46,1),(56,1),(64,3),(72,3)],f);chest=curve([(1,3),(25,-5),(31,-8),(40,-2),(46,5),(56,6),(64,3),(72,3)],f)
 walking=sm(74,84,f);low+=walking*1.0*math.sin((f-78)*math.pi/15);chest+=walking*1.8*math.sin((f-78)*math.pi/15+.6)
 return math.radians(low),math.radians(chest)
def up(angle):return Vector((math.sin(angle),0,math.cos(angle)))
def down(angle):return Vector((math.sin(angle),0,-math.cos(angle)))
def arm_angles(who,side,f):
 offset=(0 if side=='near' else math.pi)+(0 if who=='BOY' else .1);early=2*math.pi*(f-13)/24+offset;late=2*math.pi*(f-(94 if who=='BOY' else 98))/30+offset;blend=sm(68,82,f);walk=-12*math.cos(early)*(1-blend)-12*math.cos(late)*blend;bend=18+3*(math.sin(early-.5)*(1-blend)+math.sin(late-.5)*blend)
 if who=='BOY' and side=='near':a=curve([(20,walk),(24,25),(28,45),(31,55),(36,43),(40,25),(44,-12),(50,-10),(57,-6),(65,5),(74,walk)],f);b=curve([(20,bend),(30,25),(40,30),(44,42),(52,42),(60,28),(74,bend)],f)
 elif who=='BOY':a=curve([(20,walk),(25,-25),(30,-40),(36,-28),(43,-15),(50,-7),(64,-2),(74,walk)],f);b=22
 elif side=='near':a=curve([(23,walk),(28,35),(35,30),(42,12),(49,-15),(57,-9),(65,-4),(75,walk)],f);b=curve([(23,bend),(32,24),(42,30),(51,28),(65,20),(75,bend)],f)
 else:a=curve([(23,walk),(29,-25),(36,-23),(43,-8),(52,-2),(65,4),(75,walk)],f);b=16
 env=sm(20 if who=='BOY' else 23,25 if who=='BOY' else 28,f)*(1-sm(65,77,f));return math.radians(walk+(a-walk)*env),math.radians(bend+(b-bend)*env)
def sample(who,f):
 prop=PROPORTIONS[who];x=trajectory(ROOTS[who],f);feet={side:foot(who,side,f) for side in ['near','far']};desired=desired_hip_z(who,f);ceiling=10.
 for ft in feet.values():
  dx=x-ft['ankle'].x;length=sum(prop['leg'])-.002
  if abs(dx)>length:raise ValueError((who,f,'horizontal reach',dx,length))
  ceiling=min(ceiling,ft['ankle'].z+math.sqrt(length*length-dx*dx)-.002)
 z=softmin(desired,ceiling);H=Vector((x,0,z));low,high=angles(who,f);L=H+up(low)*prop['torso'][0];neck=L+up(high)*prop['torso'][1];_,lagged=angles(who,max(1,f-2));headangle=lagged*.52+(math.radians(3)*sm(35,45,f)*(1-sm(62,75,f)) if who=='GIRL' else 0)
 joints={'pelvis':H,'lumbar':L,'neck':neck,'head_tip':neck+up(headangle)*(prop['head'][1]*2)};segments={'pelvis':(H,H+up(low)*.10),'lumbar':(H,L),'chest':(L,neck),'head':(neck,joints['head_tip'])}
 for side in ['near','far']:
  dep=-.052 if side=='near' else .052;hip=H+Vector((0,dep,0));A=feet[side]['ankle'];K=two_bone(hip,A,*prop['leg']);K.y=dep;joints['knee_'+side]=K;joints['ankle_'+side]=A;segments['thigh_'+side]=(hip,K);segments['shin_'+side]=(K,A)
  S=neck+Vector((-.035 if side=='near' else .035,dep,-.065));aa,bb=arm_angles(who,side,f);E=S+down(aa)*prop['arm'][0];W=E+down(aa+bb)*prop['arm'][1];T=W+down(aa+bb+.03)*prop['hand'];joints['shoulder_'+side]=S;joints['elbow_'+side]=E;joints['wrist_'+side]=W;segments['upper_arm_'+side]=(S,E);segments['forearm_'+side]=(E,W);segments['hand_'+side]=(W,T)
 # Geometric mass proxy only, not a dynamics/force solve.
 com=(H*.22+(H+neck)*.5*.38+(neck+joints['head_tip'])*.5*.18+sum(((H+joints['knee_'+s])*.5 for s in ['near','far']),Vector())*.055+sum(((joints['knee_'+s]+joints['ankle_'+s])*.5 for s in ['near','far']),Vector())*.035+sum(((joints['shoulder_'+s]+joints['wrist_'+s])*.5 for s in ['near','far']),Vector())*.025)
 return {'root_x':x,'desired_hip_z':desired,'reach_ceiling_z':ceiling,'hip_z':z,'feet':feet,'joints':joints,'segments':segments,'com_proxy':com/1.01,'head_angle':headangle}
def phase(f):
 return 'APPROACH' if f<23 else 'TOE SCUFF / MOMENTUM' if f<30 else 'CATCH STEP / COMPRESSION' if f<45 else 'WEIGHT OVER FRONT FOOT' if f<66 else 'RESTART' if f<83 else 'CONTINUE WALK'
