"""Deliberately authored complete poses, not recurring locomotion curves.
Keys are exposed as stepped blocking. IK only constructs fixed-length limbs.
All coordinates are metres in the side-view XZ plane. No auto height clamping.
"""
import math
from mathutils import Vector,Matrix
FPS=24;N=72
PROPORTIONS={'BOY':{'leg':(.285,.285),'arm':(.225,.215),'torso':(.18,.24),'neck':.03,'head':(.155,.185),'ankle':.09,'hand':.070},'GIRL':{'leg':(.27,.27),'arm':(.21,.20),'torso':(.17,.21),'neck':.03,'head':(.145,.17),'ankle':.085,'hand':.067}}
def pose(f,intent,hip,spine,near,far,hands,poles=(1,-1),face=1):
 return {'frame':f,'intent':intent,'hip':hip,'spine':spine,'near_foot':near,'far_foot':far,'hands':hands,'elbow_poles':poles,'face':face}
# Foot tuple = flat-ankle-X, roll degrees, sole lift, pivot ('toe' or 'heel').
# Hands = wrist world-XZ, or BRACE (wrist offset above front-thigh support).
BOY=[
 pose(1,'He is still trying to keep up',(0,.620),(4,6,0),(-.15,20,0,'toe'),(.12,0,0,'toe'),((.13,.64),(-.08,.67))),
 pose(7,'Arriving toe / momentum still forward',(.14,.610),(7,11,0),(-.15,32,0,'toe'),(.36,8,.035,'toe'),((.29,.68),(.00,.72))),
 pose(10,'Toe stopped / leading arm reaches, trailing arm stays low',(.22,.585),(14,24,8),(-.15,43,0,'toe'),(.40,35,.040,'toe'),((.72,.82),(.18,.59)),(-1,-1)),
 pose(13,'Forward loss / unequal extended reach and backsweep',(.34,.540),(19,48,14),(-.15,57,0,'toe'),(.40,46,.040,'toe'),((.94,.75),(.31,.55)),(-1,-1)),
 pose(16,'Catch foot shoots / leading arm follows the fall downward',(.46,.500),(20,50,16),(.72,-3,.11,'heel'),(.40,0,0,'toe'),((1.065,.64),(.39,.56)),(-1,-1)),
 pose(19,'Heel catches / reach descends toward loaded thigh',(.58,.490),(18,40,22),(.88,-7,0,'heel'),(.40,23,0,'toe'),((1.12,.585),(.46,.61)),(-1,-1)),
 pose(22,'Deep load / near hand finds the thigh',(.66,.395),(28,56,32),(.88,0,0,'toe'),(.40,40,0,'toe'),('BRACE',(.58,.65)),(1,1)),
 pose(26,'Stay low / head checks footing, shoulder bears down',(.68,.405),(20,62,12),(.88,0,0,'toe'),(.40,57,0,'toe'),('BRACE',(.58,.68)),(1,1)),
 pose(32,'Gather the trailing foot / do not rise yet',(.72,.420),(14,55,-4),(.88,0,0,'toe'),(.62,14,.050,'toe'),('BRACE',(.61,.63)),(1,1)),
 pose(38,'Feet underneath / gather effort over the front leg',(.77,.435),(8,56,-8),(.88,0,0,'toe'),(.65,0,0,'toe'),('BRACE',(.65,.65)),(1,1)),
 pose(43,'Leg pushes / shoulder and chest still hang',(.80,.510),(3,42,-5),(.88,0,0,'toe'),(.65,14,0,'toe'),('BRACE',(.65,.75)),(1,1)),
 pose(49,'Hips recover / chest follows and hand unloads',(.815,.580),(-4,20,2),(.88,0,0,'toe'),(.65,0,0,'toe'),((.99,.60),(.69,.78)),(1,-1)),
 pose(56,'Release the brace / head and shoulder settle separately',(.815,.605),(-3,8,8),(.88,0,0,'toe'),(.65,0,0,'toe'),((.96,.65),(.67,.72)),(1,-1)),
 pose(64,'Recovered but weary / accept the pause',(.81,.595),(2,12,4),(.88,0,0,'toe'),(.65,0,0,'toe'),((.97,.68),(.66,.70)),(1,-1)),
 pose(72,'End on a supported pause, not another walk step',(.81,.595),(2,12,4),(.88,0,0,'toe'),(.65,0,0,'toe'),((.97,.68),(.66,.70)),(1,-1))]
GIRL=[
 pose(1,'Ahead, still travelling',(1.24,.600),(2,4,2),(1.10,17,0,'toe'),(1.39,0,0,'toe'),((1.36,.63),(1.14,.67))),
 pose(8,'Notice the interruption / interrupt her own stride',(1.38,.580),(0,1,-4),(1.32,6,.05,'toe'),(1.39,0,0,'toe'),((1.20,.70),(1.62,.75)),(1,-1)),
 pose(12,'Brake and attend / one low available hand, other arm settles',(1.47,.565),(-6,-8,-12),(1.61,-6,0,'heel'),(1.39,0,0,'toe'),((1.16,.68),(1.57,.55)),(1,-1),-1),
 pose(17,'Controlled load / quiet low offer with other hand by hip',(1.54,.530),(-10,-4,-6),(1.61,0,0,'toe'),(1.39,34,0,'toe'),((1.22,.67),(1.64,.51)),(1,-1),-1),
 pose(22,'Collect the trailing foot / choice to stay',(1.56,.550),(0,-12,-15),(1.61,0,0,'toe'),(1.48,8,.045,'toe'),((1.42,.68),(1.66,.68)),(1,-1),-1),
 pose(27,'Both heels down / settle, not a frozen lunge',(1.58,.590),(2,-14,-18),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.38,.70),(1.73,.75)),(1,-1),-1),
 pose(34,'Incline toward him / hold a clear space for the offered hand',(1.55,.585),(-4,-18,-24),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.34,.73),(1.63,.68)),(1,-1),-1),
 pose(43,'Attend to his effort / hand waits, no helping load',(1.56,.590),(-2,-14,-16),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.36,.76),(1.64,.70)),(1,-1),-1),
 pose(54,'Follow his rising head / stay planted',(1.58,.600),(0,-8,-6),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.38,.80),(1.65,.72)),(1,-1),-1),
 pose(64,'Let the offer soften / remain with him',(1.58,.595),(0,-10,-10),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.41,.71),(1.66,.73)),(1,-1),-1),
 pose(72,'End attending, both feet settled',(1.58,.595),(0,-10,-10),(1.61,0,0,'toe'),(1.47,0,0,'toe'),((1.41,.71),(1.66,.73)),(1,-1),-1)]
POSES={'BOY':BOY,'GIRL':GIRL}
KEYS=sorted({p['frame'] for rows in POSES.values() for p in rows})
def up(deg):a=math.radians(deg);return Vector((math.sin(a),0,math.cos(a)))
def solve_two(A,B,l1,l2,pole):
 d=B-A;D=d.length
 if D>=l1+l2-.00001 or D<=abs(l1-l2)+.00001:raise ValueError(('unreachable authored pose',tuple(A),tuple(B),D,l1+l2))
 u=d/D;along=(l1*l1-l2*l2+D*D)/(2*D);h=math.sqrt(l1*l1-along*along)
 if isinstance(pole,Vector):n=(pole-u*pole.dot(u)).normalized()
 else:n=Vector((-u.z,0,u.x))*pole
 return A+u*along+n*h
def foot(who,side,key):
 x,deg,lift,pivot=key;v=Vector((.135 if pivot=='toe' else -.075,0,0));M=Matrix.Translation((x,0,lift))@Matrix.Translation(v)@Matrix.Rotation(math.radians(deg),4,'Y')@Matrix.Translation(-v);dep=-.052 if side=='near' else .052;A=M@Vector((0,dep,PROPORTIONS[who]['ankle']))
 return {'matrix':M,'ankle':A,'x':x,'angle':math.radians(deg),'lift':lift,'pivot':pivot,'state':'swing' if lift>.0401 else 'toe_block' if lift>.001 else 'flat' if abs(deg)<.01 else 'toe' if pivot=='toe' else 'heel','toe':M@Vector((.135,dep,0)),'heel':M@Vector((-.075,dep,0))}
def sample_key(who,key):
 prop=PROPORTIONS[who];H=Vector((key['hip'][0],0,key['hip'][1]));low,high,headangle=key['spine'];L=H+up(low)*prop['torso'][0];C=L+up(high)*prop['torso'][1];neck=C+up((headangle-high)*.35)*prop['neck'];T=neck+up(headangle)*(prop['head'][1]*2)
 segments={'pelvis':(H,H+up(low)*.10),'lumbar':(H,L),'chest':(L,C),'neck':(C,neck),'head':(neck,T)};joints={'pelvis':H,'lumbar':L,'collar':C,'neck':neck,'head_tip':T};feet={}
 for i,side in enumerate(['near','far']):
  dep=-.052 if side=='near' else .052;feet[side]=ft=foot(who,side,key[side+'_foot']);hip=H+Vector((0,dep,0));A=ft['ankle'];K=solve_two(hip,A,*prop['leg'],1);joints['knee_'+side]=K;joints['ankle_'+side]=A;segments['thigh_'+side]=(hip,K);segments['shin_'+side]=(K,A)
 for i,side in enumerate(['near','far']):
  dep=-.052 if side=='near' else .052;S=C+Vector((-.035 if side=='near' else .035,dep,-.035));hand=key['hands'][i]
  if hand=='BRACE':
   # Rest the middle of the existing hand along the thigh's upper surface.
   # Both native meshes are ellipsoids: derive the thigh radius at this pad,
   # then leave the palm's .024m radius outside it instead of stabbing inward.
   hip=H+Vector((0,dep,0));knee=joints['knee_near'];tangent=(knee-hip).normalized();top=Vector((-tangent.z,0,tangent.x)).normalized();station=.70;target=hip.lerp(knee,station);thigh_length=(knee-hip).length;axis_length=thigh_length+.016;axis_u=2*((station*thigh_length+.008)/axis_length)-1;skin_radius=.043*math.sqrt(1-axis_u*axis_u);pad=target+top*(skin_radius+.024+.0005);W=pad-tangent*(prop['hand']*.5);tip=pad+tangent*(prop['hand']*.5)
  else:
   W=Vector((hand[0],dep,hand[1]));handdir=Vector((-.066,0,.01)).normalized() if who=='GIRL' and side=='near' and key['face']<0 else (W-S).normalized();tip=W+handdir*prop['hand']
  arm_pole=key['elbow_poles'][i]
  if hand=='BRACE':
   u=(W-S).normalized();arm_pole=Vector((-u.z,0,u.x))*.55+Vector((0,-.835,0))
  E=solve_two(S,W,*prop['arm'],arm_pole);tip=W+(tip-W).normalized()*prop['hand'];segments['upper_arm_'+side]=(S,E);segments['forearm_'+side]=(E,W);segments['hand_'+side]=(W,tip);joints['shoulder_'+side]=S;joints['elbow_'+side]=E;joints['wrist_'+side]=W;joints['fingertip_'+side]=tip
 return {'root_x':H.x,'hip_z':H.z,'segments':segments,'joints':joints,'feet':feet,'face':key['face'],'intent':key['intent'],'key_frame':key['frame']}
def sample(who,f):return sample_key(who,max((p for p in POSES[who] if p['frame']<=f),key=lambda p:p['frame']))
