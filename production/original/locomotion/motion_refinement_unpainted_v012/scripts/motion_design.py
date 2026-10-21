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
 'BOY':[(1,0,.0225),(13,.27,.0225),(23,.495,.025),(27,.60,.026),(30,.68,.026),(33,.76,.024),(36,.83,.018),(40,.89,.006),(48,.935,.005),(58,1.,.007),(66,1.055,.012),(78,1.20,.015),(94,1.45,.017),(109,1.71,.017),(124,1.96,.017),(139,2.21,.017),(144,2.293,.017)],
 'GIRL':[(1,.88,.0225),(13,1.15,.0225),(23,1.375,.022),(26,1.48,.014),(31,1.56,.006),(38,1.60,.0015),(47,1.615,.0012),(57,1.63,.0015),(66,1.645,.002),(72,1.68,.012),(83,1.81,.016),(99,2.06,.017),(114,2.31,.017),(129,2.56,.017),(144,2.81,.017)]}
PROPORTIONS={'BOY':{'height':1.45,'leg':(.285,.285),'arm':(.225,.215),'torso':(.18,.24),'neck':.03,'head':(.155,.185),'ankle':.09,'hand':.070},'GIRL':{'height':1.369917744,'leg':(.27,.27),'arm':(.21,.20),'torso':(.17,.21),'neck':.03,'head':(.145,.17),'ankle':.085,'hand':.067}}
# (toe-off,arrival,world ankle-X at flat,clearance). Toe scuff is a special first far arrival.
STEPS={('BOY','near'):[(3,13,.36,.040),(27,36,.98,.085),(82,94,1.52,.040),(111,124,2.02,.035),(141,154,2.52,.035)],('BOY','far'):[(16,24,.62,.045),(66,78,1.28,.070),(97,109,1.78,.038),(126,139,2.28,.035),(156,169,2.78,.035)],('GIRL','near'):[(2,13,1.24,.037),(70,83,1.88,.043),(102,114,2.38,.035),(132,144,2.88,.035),(162,174,3.38,.035)],('GIRL','far'):[(16,26,1.62,.040),(87,99,2.13,.038),(117,129,2.63,.035),(147,159,3.13,.035)]}
INITIAL={('BOY','near'):-.17,('BOY','far'):.10,('GIRL','near'):.71,('GIRL','far'):.98}
def roll_point(p,angle,pivot):return Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-pivot)@p
def foot(who,side,f):
 previous=INITIAL[who,side];events=STEPS[who,side];prev_end=-100;angle=0;pivot=Vector((.135,0,0));lift=0;state='flat';x=previous
 for i,(start,end,target,height) in enumerate(events):
  scuff=who=='BOY' and side=='far' and i==0
  if f<start:
   x=previous;state='flat';angle=.48*sm(start-7,start,f);pivot=Vector((.135,0,0))
   if prev_end>-100 and f<prev_end+3:angle=-.12*(1-sm(prev_end,prev_end+3,f));pivot=Vector((-.075,0,0));state='heel'
   if who=='BOY' and side=='far' and 30<=f<66:angle=.90*sm(41,62,f);state='toe' if angle>1e-7 else 'flat'
   if who=='GIRL' and side=='near' and 26<=f<70:angle=1.02*sm(24,40,f);state='toe' if angle>1e-7 else 'flat'
   if angle>.01:state='toe'
   break
  if f<=end:
   u=(f-start)/(end-start);progress=sm(.12,.90,u)**.65 if who=='BOY' and side=='far' and i==1 else sm(0,1,u)**.70 if who=='GIRL' and side=='near' and i==1 else sm(0,1,u);x=previous+(target-previous)*progress;lift=height*math.sin(math.pi*u)**(.75 if who=='BOY' and side=='far' and i==1 else 1.1);state='swing'
   initial=.90 if who=='BOY' and side=='far' and i==1 else 1.02 if who=='GIRL' and side=='near' and i==1 else .48
   angle=curve([(0,initial),(.40,.035),(.72,.01),(1,.20 if scuff else -.12)],u);pivot=Vector((.135,0,0)).lerp(Vector((-.075,0,0)),sm(.35,.8,u)) if not scuff else Vector((.135,0,0))
   if scuff:
    # Non-zero incoming speed, then abrupt interruption at the low test obstacle.
    x=trajectory([(16,previous,0),(24,target,.080)],f);lift+=.035*sm(.65,1,u)
   if f==end:state='toe_block' if scuff else 'heel'
   break
  previous=target;prev_end=end;x=target;nextstart=events[i+1][0] if i+1<len(events) else 1000
  if f<nextstart:
   if scuff and f<=30:
    angle=curve([(24,.20),(25,.55),(26,.80),(27,.74),(28,.55),(29,.28),(30,0)],f);lift=.035*(1-sm(26,30,f));pivot=Vector((.135,0,0));state='toe_block' if f<30 else 'flat';break
   # Continue loop to evaluate flat/roll interval before the following step.
   continue
 else:
  x=previous;angle=-.12*(1-sm(prev_end,prev_end+3,f));pivot=Vector((-.075,0,0));state='heel' if f<prev_end+3 else 'flat'
 transform=Matrix.Translation(Vector((x,0,lift)))@Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-pivot)
 ankle=transform@Vector((0,0,PROPORTIONS[who]['ankle']));ankle.y=-.052 if side=='near' else .052
 return {'x':x,'lift':lift,'angle':angle,'state':state,'matrix':transform,'ankle':ankle,'heel':transform@Vector((-.075,0,0)),'toe':transform@Vector((.135,0,0))}
def walk_phase(who,f):
 contacts=[78,94,109,124,139,154] if who=='BOY' else [83,99,114,129,144,159]
 contacts=[contacts[0]-15]+contacts
 for a,b in zip(contacts,contacts[1:]):
  if f<=b:return max(0.,(f-a)/(b-a))
 return (f-contacts[-1])/15
def walk_hip(who,f):
 # The load follows heel arrival; extension peaks near mid-stance, before push-off.
 u=walk_phase(who,f)
 return (.634 if who=='BOY' else .614)+curve([(0,-.008),(.13,-.032),(.52,.014),(.80,.005),(1,-.008)],u)
def desired_hip_z(who,f):
 early=(.636 if who=='BOY' else .616)-.023*math.exp(-((f-15)/2.9)**2)
 z=early+(walk_hip(who,f)-early)*sm(65,80,f)
 if who=='BOY':
  env=sm(21,24,f)*(1-sm(66,76,f));performance=curve([(21,.630),(24,.605),(26,.585),(29,.565),(33,.550),(36,.545),(40,.455),(44,.475),(50,.520),(58,.580),(64,.610),(72,.625)],f)
 else:
  # One brake/settle, fourteen frames before his main load, then a supported wait.
  env=sm(23,26,f)*(1-sm(66,79,f));performance=curve([(23,.612),(26,.587),(29,.550),(33,.578),(38,.601),(46,.598),(53,.606),(61,.601),(66,.606),(74,.615)],f)
 return z*(1-env)+performance*env
def softmin(a,b,k=.012):return min(a,b)-.25*k*max(0,1-abs(a-b)/k)**2
def two_bone(H,A,L1,L2):
 d=A-H;d.y=0;D=d.length
 if D>=L1+L2:raise ValueError(('leg reach violation',D,L1+L2))
 u=d.normalized();along=(L1*L1-L2*L2+D*D)/(2*D);h=math.sqrt(max(0,L1*L1-along*along));n=Vector((-u.z,0,u.x));return H+u*along+n*h
def angles(who,f):
 if who=='BOY':
  low=curve([(1,2),(21,4),(24,7),(27,16),(30,19),(36,14),(40,17),(44,14),(50,10),(58,6),(66,4.5),(76,4.5)],f);chest=curve([(1,4),(21,6),(24,11),(26,23),(29,32),(33,32),(36,28),(40,25),(44,24),(50,17),(58,11),(66,8),(76,7)],f)
 else:low=curve([(1,1.5),(23,1),(26,-5),(30,-4),(36,-1),(42,2),(49,3),(56,1.5),(66,3),(78,4.5)],f);chest=curve([(1,3),(23,1),(26,-10),(30,-9),(35,-4),(40,1),(46,5),(54,7),(62,4),(70,5),(80,7)],f)
 walking=sm(69 if who=='BOY' else 74,86 if who=='BOY' else 91,f);u=walk_phase(who,f)
 walklow=4.5+3.5*math.sin(2*math.pi*(u-.15));walkchest=7+3.0*math.sin(2*math.pi*(u-.15)-1.0)
 return math.radians(low*(1-walking)+walklow*walking),math.radians(chest*(1-walking)+walkchest*walking)
def up(angle):return Vector((math.sin(angle),0,math.cos(angle)))
def down(angle):return Vector((math.sin(angle),0,-math.cos(angle)))
def arm_angles(who,side,f):
 offset=(0 if side=='near' else math.pi)+(0 if who=='BOY' else .20);early=2*math.pi*(f-13)/24+offset;late=2*math.pi*(f-(94 if who=='BOY' else 99))/30+offset;blend=sm(68,84,f);walk=-12*math.cos(early)*(1-blend)+(-14*math.cos(late)+2*math.sin(2*late+.4))*blend;bend=18+3*math.sin(early-.5)*(1-blend)+(2+7*math.sin(late-.9))*blend
 if who=='BOY' and side=='near':a=curve([(20,walk),(24,25),(27,50),(30,57),(36,35),(40,-8),(46,-15),(53,-10),(62,1),(74,walk)],f);b=curve([(20,bend),(28,25),(36,32),(40,43),(48,42),(60,28),(74,bend)],f)
 elif who=='BOY':a=curve([(20,walk),(25,-25),(29,-43),(36,-25),(42,-16),(50,-7),(64,-2),(74,walk)],f);b=22
 elif side=='near':a=curve([(23,walk),(27,34),(32,24),(38,4),(44,-24),(51,-18),(60,-10),(69,-3),(80,walk)],f);b=curve([(23,bend),(29,25),(38,31),(45,37),(54,30),(67,22),(80,bend)],f)
 else:a=curve([(23,walk),(27,-28),(33,-17),(40,-1),(48,11),(58,7),(69,1),(80,walk)],f);b=16
 env=sm(20 if who=='BOY' else 23,25 if who=='BOY' else 28,f)*(1-sm(65,77,f));return math.radians(walk+(a-walk)*env),math.radians(bend+(b-bend)*env)
def sample(who,f):
 prop=PROPORTIONS[who];u=walk_phase(who,f);x=trajectory(ROOTS[who],f)+.008*math.sin(2*math.pi*u+.6)*sm(69,86,f);feet={side:foot(who,side,f) for side in ['near','far']};desired=desired_hip_z(who,f);ceiling=10.
 for ft in feet.values():
  dx=x-ft['ankle'].x;length=sum(prop['leg'])-.002
  if abs(dx)>length:raise ValueError((who,f,'horizontal reach',dx,length))
  ceiling=min(ceiling,ft['ankle'].z+math.sqrt(length*length-dx*dx)-.002)
 z=softmin(desired,ceiling);H=Vector((x,0,z));low,high=angles(who,f);L=H+up(low)*prop['torso'][0];collar=L+up(high)*prop['torso'][1];_,lagged=angles(who,max(1,f-3));headangle=lagged*.38+(math.radians(7)*sm(34,41,f)*(1-sm(46,61,f)) if who=='GIRL' else 0);neckangle=headangle*.70-high*.30;neck=collar+up(neckangle)*prop['neck']
 joints={'pelvis':H,'lumbar':L,'collar':collar,'neck':neck,'head_tip':neck+up(headangle)*(prop['head'][1]*2)};segments={'pelvis':(H,H+up(low)*.10),'lumbar':(H,L),'chest':(L,collar),'neck':(collar,neck),'head':(neck,joints['head_tip'])}
 for side in ['near','far']:
  dep=-.052 if side=='near' else .052;hip=H+Vector((0,dep,0));A=feet[side]['ankle'];K=two_bone(hip,A,*prop['leg']);K.y=dep;joints['knee_'+side]=K;joints['ankle_'+side]=A;segments['thigh_'+side]=(hip,K);segments['shin_'+side]=(K,A)
  S=collar+Vector((-.035 if side=='near' else .035,dep,-.035));aa,bb=arm_angles(who,side,f);E=S+down(aa)*prop['arm'][0];W=E+down(aa+bb)*prop['arm'][1];T=W+down(aa+bb+.03)*prop['hand'];joints['shoulder_'+side]=S;joints['elbow_'+side]=E;joints['wrist_'+side]=W;segments['upper_arm_'+side]=(S,E);segments['forearm_'+side]=(E,W);segments['hand_'+side]=(W,T)
 # Geometric mass proxy only, not a dynamics/force solve.
 com=(H*.22+(H+neck)*.5*.38+(neck+joints['head_tip'])*.5*.18+sum(((H+joints['knee_'+s])*.5 for s in ['near','far']),Vector())*.055+sum(((joints['knee_'+s]+joints['ankle_'+s])*.5 for s in ['near','far']),Vector())*.035+sum(((joints['shoulder_'+s]+joints['wrist_'+s])*.5 for s in ['near','far']),Vector())*.025)
 return {'root_x':x,'desired_hip_z':desired,'reach_ceiling_z':ceiling,'hip_z':z,'feet':feet,'joints':joints,'segments':segments,'com_proxy':com/1.01,'head_angle':headangle}
def phase(f):
 return 'APPROACH' if f<23 else 'TOE INTERRUPTION / MOMENTUM' if f<30 else 'CATCH STEP / COMPRESSION' if f<41 else 'WEIGHT OVER FRONT FOOT' if f<66 else 'RESTART' if f<84 else 'CONTINUE WALK'
