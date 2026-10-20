"""Controlled noncyclic inbetweens for the retained v014 story keys.
Explicit catch/load/gather/push breakdowns author the motion. Bounded cubics
join these selected controls; feet and the brace use contact-specific solves.
No whole-clip uniform automatic Bezier easing or recurring gait phase.
"""
import math,bisect
from mathutils import Vector
import pose_solver as K
FPS=24;N=72;PROPORTIONS=K.PROPORTIONS;POSES=K.POSES;KEYS=K.KEYS
BAKE_FRAMES=[1+i*.25 for i in range((N-1)*4+1)]
class Curve:
 def __init__(self,points):
  self.x,self.y=map(list,zip(*sorted(points.items())));n=len(self.x);h=[self.x[i+1]-self.x[i] for i in range(n-1)];d=[(self.y[i+1]-self.y[i])/h[i] for i in range(n-1)];m=[d[0]]+[0.]*(n-2)+[d[-1]]
  for i in range(1,n-1):
   if d[i-1]*d[i]>0:
    a=2*h[i]+h[i-1];b=h[i]+2*h[i-1];m[i]=(a+b)/(a/d[i-1]+b/d[i])
  self.m=m
 def __call__(self,f):
  if f<=self.x[0]:return self.y[0]
  if f>=self.x[-1]:return self.y[-1]
  i=bisect.bisect_right(self.x,f)-1;h=self.x[i+1]-self.x[i];u=(f-self.x[i])/h
  return (2*u**3-3*u*u+1)*self.y[i]+(u**3-2*u*u+u)*h*self.m[i]+(-2*u**3+3*u*u)*self.y[i+1]+(u**3-u*u)*h*self.m[i+1]

# Each addition is a selected breakdown, not a repeating movement recipe.
BODY={
 'BOY':{4:((.067,.620),(5,7,0)),8:((.165,.606),(7.5,12,1)),9:((.191,.599),(9,16,4)),11:((.257,.573),(16,32,9)),12:((.298,.554),(18,42,11)),14:((.382,.520),(20,51,15)),15:((.423,.505),(21,52,16)),17:((.505,.493),(19,47,18)),18:((.547,.491),(18,43,21)),20:((.612,.447),(23,47,26)),21:((.641,.410),(27,54,31)),24:((.672,.397),(24,62,26)),28:((.690,.408),(18,60,5)),30:((.706,.415),(16,57,0)),34:((.739,.423),(12,57,-6)),36:((.756,.423),(10,57,-8)),40:((.780,.443),(7,54,-8)),41:((.788,.466),(5,49,-7)),42:((.795,.491),(4,45,-6)),44:((.802,.517),(2.5,41,-4)),45:((.805,.532),(1,38,-3)),46:((.808,.545),(0,34,-1)),47:((.811,.558),(-1,29,0)),48:((.813,.572),(-2.5,24,1)),50:((.816,.586),(-4,17,4)),52:((.817,.599),(-4,12,7)),54:((.817,.604),(-3.5,9,8)),60:((.812,.598),(0,10,6))},
 'GIRL':{4:((1.298,.604),(1,3,1)),10:((1.425,.577),(-3,-5,-8)),14:((1.511,.543),(-9,-9,-10)),15:((1.525,.535),(-10,-8,-8)),19:((1.549,.531),(-8,-7,-9)),20:((1.554,.538),(-5,-10,-12)),24:((1.574,.577),(1,-13,-17)),26:((1.579,.589),(2,-14,-18)),30:((1.566,.587),(-1,-16,-22)),38:((1.554,.586),(-4,-17,-23)),47:((1.569,.594),(-1,-12,-12)),50:((1.575,.598),(0,-10,-8)),59:((1.581,.598),(0,-9,-8))}}
FOOT={
 ('BOY','near'):{14:(.07,40,.12),15:(.43,10,.17),17:(.80,-5,.070),18:(.865,-7,.025),20:(.88,-4.5,0),21:(.88,-1,0)},
 ('BOY','far'):{3:(.17,14,.035),4:(.23,12,.065),6:(.33,9,.060),8:(.385,13,.040),9:(.40,23,.040),14:(.40,36,.025),15:(.40,17,.008),17:(.40,5,0),18:(.40,14,0),20:(.40,28,0),24:(.40,49,0),27:(.40,57,.020),28:(.43,49,.055),30:(.56,28,.080),34:(.64,7,.028),36:(.65,2,.006),40:(.65,4,0),41:(.65,8,0),45:(.65,12,0),47:(.65,5,0),48:(.65,2,0)},
 ('GIRL','near'):{2:(1.105,17,.018),4:(1.17,12,.065),6:(1.25,7,.070),9:(1.43,3,.045),10:(1.52,-3,.025),11:(1.585,-6,.008),14:(1.61,-3,0),16:(1.61,-.5,0)},
 ('GIRL','far'):{14:(1.39,12,0),16:(1.39,29,0),18:(1.39,34,0),19:(1.40,31,.025),20:(1.43,25,.055),21:(1.46,15,.055),23:(1.48,6,.030),24:(1.475,3,.015),25:(1.47,1,.006),26:(1.47,0,0)}}
WRISTS={
 ('BOY','near'):{8:(.34,.69),9:(.52,.77),11:(.81,.80),12:(.89,.78),14:(.985,.71),15:(1.035,.665),17:(1.09,.615),18:(1.11,.600),20:(1.01,.540),21:(.90,.485),50:(.98,.615),52:(.965,.638)},
 ('BOY','far'):{8:(.05,.68),9:(.12,.63),11:(.22,.57),12:(.27,.55),14:(.34,.55),15:(.365,.55),17:(.41,.57),18:(.44,.59),20:(.51,.62),21:(.55,.64),24:(.58,.66),28:(.585,.66),34:(.625,.625),40:(.645,.68),45:(.66,.76),47:(.68,.775),52:(.68,.755)},
 ('GIRL','near'):{10:(1.17,.68),14:(1.235,.705),15:(1.25,.700),16:(1.245,.690),19:(1.28,.675),20:(1.33,.680),24:(1.41,.69),30:(1.36,.70),47:(1.37,.78),59:(1.395,.76)},
 ('GIRL','far'):{10:(1.595,.65),14:(1.585,.525),15:(1.605,.515),19:(1.65,.540),20:(1.655,.600),24:(1.70,.73),30:(1.69,.72),47:(1.645,.71)}}
SHOULDER={1:(0,0),43:(0,0),44:(.002,-.004),45:(.004,-.008),46:(.008,-.014),47:(.012,-.020),48:(.015,-.025),49:(0,0),72:(0,0)}
SWIVEL_EXTRA={('BOY','near'):{8:.7,9:2.0,20:2.3,21:1.6,48:.988,48.25:.84,48.5:.55,48.75:.22},('BOY','far'):{20:2.3,21:.7,45:.6,46:1.3,47:2.0,48:2.7}}
def component_curves(base,extras):
 count=len(next(iter(base.values())));out=[]
 for i in range(count):out.append(Curve({**{f:v[i] for f,v in base.items()},**{f:v[i] for f,v in extras.items()}}))
 return out
BODY_CURVES={};FOOT_CURVES={};WRIST_CURVES={};SWIVELS={}
for who,keys in POSES.items():
 base={p['frame']:(*p['hip'],*p['spine']) for p in keys};extra={f:(*hip,*spine) for f,(hip,spine) in BODY[who].items()};BODY_CURVES[who]=component_curves(base,extra)
 for index,side in enumerate(['near','far']):
  FOOT_CURVES[who,side]=component_curves({p['frame']:p[side+'_foot'][:3] for p in keys},FOOT[who,side])
  wrists={p['frame']:tuple(K.sample_key(who,p)['joints']['wrist_'+side][i] for i in [0,2]) for p in keys};WRIST_CURVES[who,side]=component_curves(wrists,WRISTS.get((who,side),{}))
  angles={p['frame']:(math.atan2(.835,.55) if p['hands'][index]=='BRACE' else 0 if p['elbow_poles'][index]>0 else math.pi) for p in keys};angles.update(SWIVEL_EXTRA.get((who,side),{}));SWIVELS[who,side]=Curve(angles)
SC=component_curves(SHOULDER,{})
def raw_control(who,f):
 exact=next((p for p in POSES[who] if abs(p['frame']-f)<1e-8),None)
 if exact:return dict(exact)
 x,z,lo,ch,head=[c(f) for c in BODY_CURVES[who]];feet=[]
 for side in ['near','far']:
  fx,roll,lift=[c(f) for c in FOOT_CURVES[who,side]];feet.append((fx,roll,max(0.,lift),'toe' if roll>=0 else 'heel'))
 hands=[tuple(c(f) for c in WRIST_CURVES[who,side]) for side in ['near','far']];control=K.pose(f,'Controlled breakdown / '+max((p for p in POSES[who] if p['frame']<=f),key=lambda p:p['frame'])['intent'],(x,z),(lo,ch,head),feet[0],feet[1],hands,face=-1 if who=='GIRL' and f>=12 else 1)
 control['arm_swivels']=[SWIVELS[who,side](f) for side in ['near','far']]
 if who=='BOY':
  control['near_shoulder']=tuple(c(f) for c in SC)
  if 21<=f<22:control['hands'][0]='BRACE_APPROACH';control['brace_approach']=.024*(22-f)
  if 22<=f<=48:control['hands'][0]='BRACE'
  if 19<f<21:control['hand_axes']=(-15.,None)
 return control
def sample(who,f):
 control=raw_control(who,f)
 try:row=K.sample_key(who,control)
 except ValueError as e:raise ValueError((who,f,control,str(e))) from e
 row['key_frame']=max(p['frame'] for p in POSES[who] if p['frame']<=f);return row
