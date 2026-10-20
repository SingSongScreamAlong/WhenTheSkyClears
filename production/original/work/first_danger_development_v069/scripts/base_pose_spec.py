"""Shot-specific replacement drawings, in metres in the camera-facing X/Z plane.

The explicit acting keys are the authoring source. The old rig/cycle is not used
to construct these drawings. Intermediate contours are exposed on twos; travel
and foot contact corrections are sampled every production frame.
"""
import math,json
from pathlib import Path
G0,G1=913,1080
RATE=.73125/24

def clamp(x,a=0,b=1):return max(a,min(b,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def track(g,keys,ease=True):
 if g<=keys[0][0]:return keys[0][1]
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if g<=b:return lerp(x,y,smooth((g-a)/(b-a)) if ease else (g-a)/(b-a))
 return keys[-1][1]
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def mul(a,v):return (a[0]*v,a[1]*v)
def length(a):return math.hypot(*a)
def unit(a):return mul(a,1/max(1e-8,length(a)))
def mix(a,b,t):return (lerp(a[0],b[0],t),lerp(a[1],b[1],t))
def perp(a):return (-a[1],a[0])
def rotate(a,degrees):
 t=math.radians(degrees);return (math.cos(t)*a[0]-math.sin(t)*a[1],math.sin(t)*a[0]+math.cos(t)*a[1])
def up(degrees,L):return (math.sin(math.radians(degrees))*L,math.cos(math.radians(degrees))*L)

# distance, pelvis-height, chest pitch, head pitch, head facing, torso opening,
# near-hand search, free-arm guard. Facing1 = right profile; -1 = left profile.
# Changes are whole-body decisions, with deliberately different timings.
KEYS={
 'GIRL':[
 (913,0,.731,2,0,1,0,0,0),
 (929,.4875,.739,1,-1,1,0,0,0),
 (945,.975,.733,3,0,1,0,0,0),
 (951,1.145,.735,0,-6,1,0,0,.10),
 (955,1.230,.705,-12,-14,1,.10,0,.55),
 (961,1.260,.650,-17,-9,.85,.18,.05,.95),
 (967,1.255,.645,-8,3,.40,.48,.28,1),
 (973,1.260,.674,-4,14,-.35,.85,.75,.90),
 (979,1.280,.681,-3,19,-.82,1,1,.85),
 (985,1.325,.667,1,20,-.70,.85,1,.72),
 (991,1.395,.643,7,17,-.35,.65,1,.65),
 (997,1.500,.663,12,4,.35,.30,1,.60),
 (1003,1.660,.699,14,-6,1,.05,1,.55),
 (1009,1.880,.727,12,-4,1,.03,1,.50),
 (1021,2.370,.716,9,1,1,.02,1,.40),
 (1033,2.820,.733,7,0,1,.02,1,.30),
 (1045,3.300,.725,7,-2,1,.02,1,.25),
 (1061,4.100,.737,6,0,1,.02,1,.20),
 (1080,5.089,.732,6,0,1,.02,1,.20)],
 'BOY':[
 (913,0,.738,2,0,1,0,0,0),
 (929,.4875,.746,1,-1,1,0,0,0),
 (945,.975,.740,3,0,1,0,0,0),
 (955,1.280,.738,3,0,1,0,0,0),
 (961,1.410,.715,-5,-6,1,.05,0,.20),
 (967,1.470,.669,-10,-3,.8,.20,.03,.65),
 (973,1.470,.659,-4,11,.65,.38,.20,.85),
 (979,1.465,.678,4,22,.55,.62,.65,.90),
 (985,1.480,.681,9,26,.5,.68,1,.80),
 (991,1.490,.645,14,22,.65,.5,1,.70),
 (997,1.530,.657,14,10,.85,.35,1,.65),
 (1003,1.640,.683,8,-5,1,.12,1,.80),
 (1009,1.860,.720,12,-3,1,.08,1,.80),
 (1021,2.360,.723,11,0,1,.05,1,.65),
 (1033,2.820,.739,8,-1,1,.03,1,.45),
 (1045,3.300,.732,8,0,1,.02,1,.35),
 (1061,4.100,.744,7,0,1,.02,1,.30),
 (1080,5.089,.739,7,0,1,.02,1,.30)]}

# Independently scheduled contact drawings. Holds over the hesitation are
# explicit, rather than a slowed repeated walk cycle.
CONTACT={
 'GIRL':{'near':[891,923,955,1009,1025,1041,1057,1073,1089],'far':[907,939,1001,1017,1033,1049,1065,1081,1097]},
 'BOY':{'near':[899,931,963,1011,1027,1043,1059,1075,1091],'far':[883,915,947,1003,1019,1035,1051,1067,1083,1099]}}
LIFT_OVERRIDE={('GIRL','far',939):989,('GIRL','near',955):1002,('BOY','far',947):991,('BOY','near',963):1004}
def distance(w,g):
 if g<913:return (g-913)*RATE
 if g>1080:return 5.089+(g-1080)*RATE
 return track(g,[(p[0],p[1]) for p in KEYS[w]],False)
def foot(w,side,g):
 contacts=CONTACT[w][side];a=max(t for t in contacts if t<=g);b=min(t for t in contacts if t>a)
 other='far' if side=='near' else 'near';opp=min(t for t in CONTACT[w][other] if t>a)
 lift=LIFT_OVERRIDE.get((w,side,a),min(b-7,opp+(1 if a>=1001 else 3)));u=clamp((g-lift)/(b-lift))
 x0=distance(w,a)+.18;x1=distance(w,b)+.18
 x=lerp(x0,x1,1-(1-u)**2);h=.075*math.sin(math.pi*u)**1.15
 beta=0 if u==0 else -14*math.sin(math.pi*u)+8*math.sin(2*math.pi*u)
 return (x,.095+h),{'contact':u==0,'anchor':x0,'plant':a,'lift':lift,'next':b,'phase':u,'pitch':beta,'clearance':h}
def ik(a,b,l1,l2,sign=1):
 d=sub(b,a);L=min(length(d),l1+l2-.0001);U=unit(d);x=(l1*l1-l2*l2+L*L)/(2*L);h=math.sqrt(max(0,l1*l1-x*x))
 return add(add(a,mul(U,x)),mul(perp(U),h*sign))

def pose(w,g):
 ps=KEYS[w];values=[track(g,[(p[0],p[i]) for p in ps],i!=1) for i in range(1,9)]
 d,h,ch,head,facing,turn,reach,guard=values
 # On twos for contour acting; no blanket sine-driven torso animation.
 hip=(d,h);feet={};fm={}
 for side in ['far','near']:feet[side],fm[side]=foot(w,side,g)
 for side in ['far','near']:
  if fm[side]['contact']:
   dx=feet[side][0]-hip[0];maxh=feet[side][1]+math.sqrt(max(.0001,.647**2-dx*dx))
   hip=(hip[0],min(hip[1],maxh))
 for side in ['far','near']:
  if not fm[side]['contact'] and length(sub(feet[side],hip))>.643:
   feet[side]=add(hip,mul(unit(sub(feet[side],hip)),.643));fm[side]['clearance']=feet[side][1]-.095
 waist=add(hip,up(-ch*.24,.10));S=add(waist,up(ch,.292))
 neck=add(S,up(ch*.5,.051));H=add(neck,up(head*facing,.103))
 shoulder_near=add(S,(-.045*turn,.008*turn));shoulder_far=add(S,(.055*turn,-.008*turn))
 P={'hip':hip,'waist':waist,'shoulder':S,'head':H,'neck':neck,'chest_pitch':ch,'head_pitch':head,'facing':facing,'turn':turn,'reach':reach,'guard':guard,'feet':fm}
 for side in ['far','near']:
  A=feet[side];K=ik(add(hip,(-.018 if side=='far' else .018,0)),A,.333,.318)
  P['hip_'+side]=add(hip,(-.018 if side=='far' else .018,0));P['knee_'+side]=K;P['ankle_'+side]=A
  sh=shoulder_near if side=='near' else shoulder_far
  if side=='far':
   # Raised close guard, then deliberate lowering. Its silhouette stays separate
   # from the reaching arm and from the torso edge.
   E=add(sh,(lerp(-.055,.105,guard),lerp(-.224,-.195,guard)))
   W=add(E,(lerp(.02,.080,guard),lerp(-.195,.067,guard)))
   if g<951:
    q=(g-913+(3 if w=='GIRL' else 0))/32*math.tau
    E=add(sh,(-.075*math.cos(q),-.22));W=add(E,(-.075*math.cos(q-.3),-.185))
  else:
   q=(g-913+(3 if w=='GIRL' else 0))/32*math.tau
   E=add(sh,(.073*math.cos(q),-.219));W=add(E,(.070*math.cos(q-.3),-.185))
  P['shoulder_'+side]=sh;P['elbow_'+side]=E;P['wrist_'+side]=W
 return P

def paired(g):
 P={w:pose(w,g) for w in ['BOY','GIRL']};offset={'BOY':-.4,'GIRL':.4}
 shoulders={w:add(P[w]['shoulder_near'],(offset[w],0)) for w in P}
 mid=mix(shoulders['BOY'],shoulders['GIRL'],.5)
 centre=(mid[0]+track(g,[(913,0),(973,-.02),(983,-.035),(991,-.015),(997,.025),(1009,0),(1080,0)]),mid[1]-track(g,[(913,.22),(979,.26),(985,.245),(991,.215),(997,.255),(1009,.26),(1080,.24)]))
 # Once both palms meet, solve a shared reachable grip height. Independent
 # wrist clamping would open the clasp whenever the shoulders separate.
 if g>=983:
  floor=[]
  for w,sh in shoulders.items():
   sign=1 if w=='BOY' else -1;dx=centre[0]-sign*.045-sh[0]
   floor.append(sh[1]-math.sqrt(max(.001,.426**2-dx*dx))+.008)
  centre=(centre[0],max(centre[1],*floor))
 for w,p in P.items():
  sign=1 if w=='BOY' else -1;reach=p['reach'];sh=p['shoulder_near']
  target=(centre[0]-offset[w]-sign*.045,centre[1]+(.006 if w=='BOY' else -.006))
  W=mix(p['wrist_near'],target,reach)
  # The searching girl's palm pauses short of contact, then the boy receives.
  if w=='GIRL':W=add(W,(track(g,[(913,0),(973,-.018),(979,.018),(985,0),(1080,0)]),0))
  if length(sub(W,sh))>.430:W=add(sh,mul(unit(sub(W,sh)),.430))
  E=ik(sh,W,.233,.199,sign=-1 if w=='BOY' else 1)
  p['elbow_near']=mix(p['elbow_near'],E,reach)
  p['wrist_near']=W
  p['hand_close']=track(g,[(913,0),(985 if w=='GIRL' else 987,0),(991 if w=='GIRL' else 995,1),(1080,1)])
  p['offset']=offset[w];p['contact_centre']=centre
 return P

PALETTE={'ink':'#252925','skin':'#b69276','skin_light':'#c5a184','skin_shadow':'#9c7a61','boy_cloth':'#35443f','boy_light':'#536057','boy_shadow':'#27312e','pants':'#716e57','pants_light':'#89836a','pants_shadow':'#504f40','girl_cloth':'#2d3531','girl_light':'#454d44','girl_shadow':'#202824','stocking':'#373c32','stocking_shadow':'#242b26','boot':'#655240','boot_light':'#826d52','boot_shadow':'#403c30','boy_hair':'#4e392b','boy_hair_light':'#74533a','girl_hair':'#242925','girl_hair_light':'#44473a','contact':'#3c4033'}

def resample(points,n=36,closed=True):
 """Centripetal-ish cubic contour through explicitly placed drawing landmarks."""
 out=[];N=len(points)
 for i in range(N if closed else N-1):
  a=points[(i-1)%N] if closed or i else points[0];b=points[i];c=points[(i+1)%N];d=points[(i+2)%N] if closed or i+2<N else points[-1]
  for j in range(5):
   t=j/5;t2=t*t;t3=t2*t
   out.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t2+(-a[k]+3*b[k]-3*c[k]+d[k])*t3) for k in [0,1]))
 if not closed:out.append(points[-1])
 return out

class Drawing:
 def __init__(self,w,g):self.w=w;self.g=g;self.paths=[]
 def shape(self,name,pts,color,ink=True,smooth=True,width=.0017):
  self.paths.append({'layer':name,'points':resample(pts) if smooth else pts,'fill':color,'stroke':'ink' if ink else None,'width':width,'closed':True})
 def line(self,name,pts,color='ink',width=.0014,smooth=True):
  self.paths.append({'layer':name,'points':resample(pts,closed=False) if smooth and len(pts)>2 else pts,'fill':None,'stroke':color,'width':width,'closed':False})
 def oval(self,name,c,rx,ry,color,ink=False,angle=0):
  pts=[add(c,rotate((rx*math.cos(i*math.tau/22),ry*math.sin(i*math.tau/22)),angle)) for i in range(22)]
  self.shape(name,pts,color,ink,False)

def ribbon(d,name,a,b,c,widths,color):
 # Purpose-shaped continuous contour: shoulder/hip mass, joint compression,
 # narrowing cuff/ankle. The contour is authored afresh for each drawing.
 U=unit(sub(b,a));V=unit(sub(c,b));N=perp(U);Q=perp(V);bis=unit(add(N,Q))
 left=[add(a,mul(N,widths[0])),add(mix(a,b,.53),mul(N,widths[1])),add(b,mul(bis,widths[2])),add(mix(b,c,.58),mul(Q,widths[3])),add(c,mul(Q,widths[4]))]
 right=[add(c,mul(Q,-widths[4])),add(mix(b,c,.58),mul(Q,-widths[3])),add(b,mul(bis,-widths[2]*.88)),add(mix(a,b,.53),mul(N,-widths[1])),add(a,mul(N,-widths[0]))]
 d.shape(name,left+right,color)
 return left,right

def hand(d,name,W,direction,close,skin='skin',behind=False):
 # Drawn palm, a distinct thumb, and four individually grouped fingers. The
 # thumb changes silhouette after the fingers make contact.
 U=unit(direction);N=perp(U)
 def p(x,y):return add(W,add(mul(U,x),mul(N,y)))
 if close>.58:
  # Separate authored grip drawing. Grouped bent fingers wrap under the other
  # palm; the thumb lies diagonally across it, rather than leaving four claws.
  d.shape(name+' grip palm',[p(-.010,-.017),p(.018,-.025),p(.047,-.022),p(.063,-.012),p(.065,.004),p(.053,.023),p(.026,.026),p(-.009,.018)],skin)
  for i in range(3):
   x=.027+i*.010
   d.line(name+' wrapped finger crease',[p(x,-.018),p(x+.008,-.022),p(x+.014,-.013)],'skin_shadow',.0012)
  d.shape(name+' grip thumb',[p(.008,.015),p(.019,.033),p(.037,.036),p(.054,.022),p(.050,.012),p(.035,.020),p(.025,.016)],'skin_light',width=.0012)
  d.line(name+' grip wrist fold',[p(.006,-.013),p(.015,.000),p(.010,.014)],'skin_shadow',.0012)
  return
 palm=[p(-.010,-.018),p(.024,-.027),p(.053,-.025),p(.063,-.010),p(.057,.019),p(.029,.026),p(-.008,.019)]
 d.shape(name+' palm',palm,skin)
 for i,(sy,L) in enumerate([(-.020,.035),(-.006,.044),(.008,.041),(.021,.030)]):
  base=p(.044,sy);tip=p(.044+L*(1-close*.65),sy-close*(.018+i*.001))
  bend=p(.044+L*.65,sy+close*.012)
  tangent=unit(sub(tip,base));normal=perp(tangent);r=.0042
  d.shape(name+f' finger {i+1}',[add(base,mul(N,-r)),add(bend,mul(N,-r)),add(tip,mul(normal,-r)),add(tip,mul(normal,r)),add(bend,mul(N,r)),add(base,mul(N,r))],skin,width=.0010)
 thumb=[p(.009,.018),p(.018,.039),p(.033,.051-close*.027),p(.045,.048-close*.037),p(.039,.035-close*.018),p(.028,.014)]
 d.shape(name+' opposed thumb',thumb,'skin_light',width=.0012)
 d.line(name+' palm crease',[p(.018,-.011),p(.032,-.004),p(.040,.006)],'skin_shadow',.0013)

def head(d,p,w,g):
 H=p['head'];pitch=p['head_pitch'];f=p['facing'];girl=w=='GIRL'
 head_angle=-pitch*f
 def q(x,z):return add(H,rotate((x,z),head_angle))
 # Skull / jaw silhouette keeps head volume while nose and facial planes turn.
 face=[]
 for i in range(40):
  t=i/40*math.tau;x=.087*math.cos(t);z=.119*math.sin(t)
  if z<-.03:x*=1-.23*clamp((-z-.03)/.09)
  # Nose projects out of the appropriate contour as it reaches profile.
  side=1 if f>=0 else -1
  bump=abs(f)**2*.026*math.exp(-((z+.009)/.018)**2)*max(0,side*x/.087)**10
  x+=side*bump
  face.append(q(x,z))
 d.shape('head | new turning skull and jaw',face,'skin',True,False)
 # Cheek shadow and a narrow forehead wash retain the established muted paint.
 side=1 if f>=0 else -1
 d.shape('head | cheek plane',[q(-f*.061,.052),q(-f*.075,-.018),q(-f*.039,-.083),q(.005*f,-.096),q(-f*.008,-.035)],'skin_shadow',False)
 d.shape('head | forehead plane',[q(-.025,.079),q(.027,.082),q(.045,.042),q(.021,.014),q(-.016,.036)],'skin_light',False)
 # Hair is a replacement silhouette; girl retains the swept dark cap/braid,
 # boy retains the short irregular brown crown.
 if girl:
  hp=[(-.086,-.047),(-.099,.024),(-.089,.083),(-.060,.123),(-.009,.136),(.047,.116),(.087,.083),(.095,.024),(.080,-.036),(.060,-.026),(.056,.035),(.026,.061),(.004,.070),(-.037,.057),(-.060,.020),(-.057,-.040)]
 else:
  hp=[(-.083,-.026),(-.097,.012),(-.095,.059),(-.103,.079),(-.082,.090),(-.083,.110),(-.062,.109),(-.049,.125),(-.030,.118),(-.007,.132),(.009,.120),(.040,.125),(.052,.111),(.078,.108),(.075,.088),(.083,.071),(.066,.047),(.036,.057),(.007,.083),(-.023,.052),(-.050,.034),(-.055,-.024)]
  if f<0:hp=[(-x,z) for x,z in hp]
 d.shape('head | drawn hair silhouette',[q(x,z) for x,z in hp],'girl_hair' if girl else 'boy_hair',True,False)
 hairlight='girl_hair_light' if girl else 'boy_hair_light'
 for i in range(5):
  a=-.065+i*.024
  d.line('head | hair sweep',[q(a,.100),q(a+.020*side,.082),q(a+.028*side,.057)],hairlight,.0015)
 # Ear occupies the back plane; features travel over the skull in the turn.
 earx=-f*.050
 d.oval('head | ear',q(earx,-.010),.014,.021,'skin',True,head_angle)
 d.line('head | ear fold',[q(earx-.004,.000),q(earx+.005,.005),q(earx+.006,-.013)],'skin_shadow',.0011)
 nearx=lerp(.035,.051,abs(f))*(1 if f>=0 else -1);eyez=.020
 blink=track(g,[(913,0),(953 if girl else 963,0),(955 if girl else 965,1),(957 if girl else 967,1),(961 if girl else 971,0),(1080,0)])
 worry=track(g,[(913,0),(951 if girl else 961,0),(961 if girl else 973,1),(1009,.7),(1080,.5)])
 for idx,ex in enumerate([nearx]+([-nearx*.66] if abs(f)<.74 else [])):
  d.line('face | upper eye',[q(ex-.012,eyez),q(ex,eyez+.003*(1-blink)),q(ex+.012,eyez-.002)],'ink',.0017)
  if blink<.75:
   d.oval('face | iris',q(ex+f*.004,eyez-.004-clamp(pitch/26)*.003),.003,.0045,'ink')
   d.line('face | lower eye',[q(ex-.009,eyez-.007),q(ex+.009,eyez-.008)],'skin_shadow',.0009)
  d.line('face | worried brow',[q(ex-.014,eyez+.021+worry*.004),q(ex+.010,eyez+.016-worry*.003)],'ink',.0018)
 nx=f*.076
 d.line('face | turning nose plane',[q(nx-f*.010,.013),q(nx+f*.009,-.012),q(nx-f*.003,-.020)],'skin_shadow',.0013)
 d.line('face | mouth',[q(f*.045-.012,-.047-worry*.008),q(f*.045,-.049),q(f*.045+.011,-.047-worry*.009)],'ink',.0012)
 d.line('face | lower lip',[q(f*.043-.005,-.057),q(f*.043+.009,-.058)],'skin_shadow',.001)

def draw_actor(w,g,P=None):
 p=(P or paired(g))[w];d=Drawing(w,g);girl=w=='GIRL';hip=p['hip'];wa=p['waist'];S=p['shoulder'];turn=p['turn']
 cloth='girl_cloth' if girl else 'boy_cloth';light='girl_light' if girl else 'boy_light';shade='girl_shadow' if girl else 'boy_shadow'
 # Drawing stack is far limbs, far arm, dress/shirt, near limbs/arms, neck,
 # hair/face. The braid is behind the shoulder and follows the head turn late.
 if girl:
  f=p['facing'];anchor=add(p['head'],(-.065*f,-.060));lag=track(g,[(913,0),(955,.015),(963,-.045),(977,.035),(989,-.015),(1009,.025),(1080,0)])
  end=add(anchor,(-.105*f+lag,-.180));mid=mix(anchor,end,.5)
  ribbon(d,'braid | turning nape',anchor,mid,end,[.017,.018,.015,.014,.009],'girl_hair')
  for i in range(7):
   c=mix(anchor,end,i/7);d.line('braid | interlace',[add(c,(-.013,.004)),add(c,(.012,-.010)),add(c,(-.008,-.022))],'girl_hair_light',.0014)
 for side in ['far','near']:
  H=p['hip_'+side];K=p['knee_'+side];A=p['ankle_'+side]
  col='stocking' if girl else 'pants';shcol='stocking_shadow' if girl else 'pants_shadow'
  if side=='far':col=shcol
  ribbon(d,'legs | '+side,H,K,A,[.050 if not girl else .038,.056 if not girl else .033,.040 if not girl else .027,.039 if not girl else .028,.027 if not girl else .020],col)
  # Fold lines follow the compressed knee and taper down the shin.
  U=unit(sub(K,H));V=unit(sub(A,K));N=perp(U);Q=perp(V)
  if not girl:
   for t in [.85,1.02]:
    c=mix(H,K,min(1,t));d.line('trouser | knee compression '+side,[add(c,mul(N,-.033)),add(c,(-.008,.012)),add(c,mul(N,.025))],'pants_shadow',.0015)
   d.line('trouser | shin fold '+side,[add(mix(K,A,.16),mul(Q,.022)),add(mix(K,A,.55),mul(Q,.010)),add(mix(K,A,.9),mul(Q,.018))],'pants_light',.0015)
  beta=p['feet'][side]['pitch'];sole=add(A,(0,-.095))
  def boot(x,z):return add(sole,rotate((x,z),beta))
  pts=[(-.065,.005),(-.071,.056),(-.051,.123),(.035,.122),(.045,.067),(.121,.036),(.139,.015),(.130,.003),(.038,0)]
  d.shape('boots | '+side,[boot(x,z) for x,z in pts],'boot' if side=='near' else 'boot_shadow')
  d.line('boots | sole '+side,[boot(-.061,.013),boot(.040,.011),boot(.126,.014)],'boot_light',.002)
  d.line('boots | cuff '+side,[boot(-.049,.107),boot(.031,.108)],'boot_light',.0016)
  for z in [.053,.067,.080]:d.line('boots | laces '+side,[boot(-.010,z),boot(.034,z-.005)],'boot_shadow',.0013)
 # Far arm is intentionally separated from torso by the raised guarding shape.
 for side in ['far']:
  sh=p['shoulder_'+side];E=p['elbow_'+side];W=p['wrist_'+side]
  C=mix(E,W,.12);ribbon(d,'far arm | rolled sleeve',sh,mix(sh,E,.55),C,[.043,.046,.042,.036,.035],shade)
  ribbon(d,'far arm | forearm',E,mix(E,W,.5),W,[.029,.027,.026,.022,.018],'skin_shadow')
  d.line('far arm | cuff',[add(C,(-.030,.003)),add(C,(.030,-.003))],light,.004)
  hand(d,'far hand | guard',W,sub(W,E),.1+p['guard']*.25,'skin_shadow',True)
 # Torso contour and planes are redrawn for twist and compression. Opening the
 # shoulders broadens the chest and moves the shirt/dress seam across its face.
 U=unit(sub(S,wa));N=(U[1],-U[0]);half=.089+.024*turn
 def tc(t,x):return add(mix(hip,S,t),mul(N,x))
 torso=[tc(1,-half*.73),tc(.94,-half),tc(.71,-half*.95),tc(.38,-.074),tc(.08,-.079),tc(-.07,-.095),tc(-.07,.101),tc(.20,.085),tc(.55,.084),tc(.88,half),tc(1,half*.72)]
 if girl:
  lag=track(g,[(913,0),(955,.012),(963,.05),(975,-.03),(989,.02),(1003,-.04),(1013,.018),(1080,0)])
  hemz=hip[1]-.275
  torso=[tc(1,-half*.72),tc(.92,-half),tc(.6,-half*.92),tc(.20,-.073),(hip[0]-.125+lag,hip[1]-.10),(hip[0]-.17+lag,hemz+.017),(hip[0]-.09+lag,hemz-.003),(hip[0]+.012+lag,hemz+.006),(hip[0]+.12+lag,hemz-.005),(hip[0]+.164+lag,hemz+.014),(hip[0]+.116,hip[1]-.10),tc(.2,.075),tc(.70,half*.93),tc(.95,half),tc(1,half*.67)]
 d.shape('costume | whole torso contour',torso,cloth)
 d.shape('costume | broad shadow plane',[tc(.94,-half*.85),tc(.62,-half*.88),tc(.15,-.065),tc(.03,.005),tc(.6,-.013),tc(.98,-.018)],shade,False)
 d.shape('costume | light plane',[tc(.96,.015),tc(.83,.073),tc(.5,.060),tc(.22,.045),tc(.35,.005)],light,False)
 d.line('costume | turning centre seam',[tc(.94,.014+turn*.030),tc(.6,.016+turn*.023),tc(.21,.010+turn*.012)],shade,.002)
 for t in [.23,.33,.72]:d.line('costume | compression fold',[tc(t,-.055),tc(t+.025,-.008),tc(t-.01,.040)],shade,.0017)
 if girl:
  for x in [-.090,-.025,.046,.105]:
   d.line('dress | hanging fold',[(hip[0]+x*.50,hip[1]-.04),(hip[0]+x*.82+lag*.6,hip[1]-.16),(hip[0]+x+lag,hemz+.02)],light,.0017)
  d.line('dress | belt',[tc(.20,-.075),tc(.20,.075)],'boot_shadow',.010)
  d.line('dress | belt highlight',[tc(.205,-.071),tc(.205,.071)],'boot_light',.0020)
 else:
  for t in [.76,.58,.41]:d.oval('shirt | button',tc(t,.025+turn*.023),.0034,.0034,'boot_shadow')
 # Neck and collar bridge are new drawing contours, not a detached head card.
 neck=p['neck'];d.shape('neck | twist',[add(S,(-.032,-.012)),add(neck,(-.027,.045)),add(neck,(.034,.040)),add(S,(.045,-.010))],'skin')
 if not girl:
  d.shape('collar | far leaf',[add(S,(-.051,.009)),add(neck,(-.025,.023)),add(S,(-.008,-.042))],'skin_light')
  d.shape('collar | near leaf',[add(neck,(.024,.024)),add(S,(.052,-.008)),add(S,(.025,-.042))],'skin_light')
 # Near arm makes the reaching silhouette. Upper sleeve and bare forearm share
 # a drawn elbow overlap, with the rolled cuff following its actual orientation.
 sh=p['shoulder_near'];E=p['elbow_near'];W=p['wrist_near'];C=mix(E,W,.12)
 ribbon(d,'near arm | reaching sleeve',sh,mix(sh,E,.55),C,[.044,.047,.044,.037,.035],cloth)
 U=unit(sub(W,E));N=perp(U)
 d.shape('near arm | rolled cuff',[add(C,mul(N,-.037)),add(C,mul(N,.037)),add(C,add(mul(U,.016),mul(N,.037))),add(C,add(mul(U,.016),mul(N,-.037)))],light)
 ribbon(d,'near arm | forearm',mix(E,W,.10),mix(E,W,.56),W,[.027,.026,.024,.021,.018],'skin')
 d.line('near arm | forearm plane',[add(mix(E,W,.25),mul(N,-.012)),add(mix(E,W,.72),mul(N,-.009)),add(W,mul(N,-.010))],'skin_shadow',.0025)
 # Reach fingers align toward the partner; before that they hang naturally.
 direction=mix(unit(sub(W,E)),(1 if w=='BOY' else -1,.08 if w=='BOY' else .10),p['reach'])
 hand(d,'near hand | search receive close',W,direction,p['hand_close'])
 head(d,p,w,g)
 # Root offsets kept separate from the native scene registration.
 for path in d.paths:path['points']=[(x+p['offset'],z) for x,z in path['points']]
 return d,p

def save_svg(d,path):
 # Human-editable vector source at1,000 units/metre, with named part layers.
 from xml.sax.saxutils import escape
 lines=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="-1000 -1550 7500 1750">']
 for q in d.paths:
  pts=q['points'];cmd='M '+' L '.join(f'{x*1000:.3f},{-z*1000:.3f}' for x,z in pts)+(' Z' if q['closed'] else '')
  fill=PALETTE.get(q['fill'],'none');stroke=PALETTE.get(q['stroke'],'none')
  lines.append(f'<path data-layer="{escape(q["layer"])}" d="{cmd}" fill="{fill}" stroke="{stroke}" stroke-width="{q["width"]*1000}" stroke-linejoin="round" stroke-linecap="round"/>')
 lines.append('</svg>');path.write_text('\n'.join(lines))

BEATS=[(913,'Walk into the passage'),(951,'Girl sees danger'),(961,'Girl checks the planted step'),(973,'Turns back and searches'),(979,'Open palm waits for a response'),(985,'Boy receives the offered hand'),(991,'Both absorb contact'),(1003,'Girl looks ahead; boy takes the cue'),(1021,'First committed linked steps'),(1080,'Continue with changed posture')]

if __name__=='__main__':
 O=Path(__file__).resolve().parents[1]
 for g in range(G0,G1+1,2):
  pp=paired(g)
  for w in ['BOY','GIRL']:
   d,p=draw_actor(w,g,pp);save_svg(d,O/'drawings'/f'{w}_{g:04d}.svg')
 (O/'evidence/ACTING_KEYS.json').write_text(json.dumps({'keys':KEYS,'columns':['frame','distance_m','pelvis_height_m','chest_pitch_deg','head_pitch_deg','head_facing','torso_opening','reach','guard'],'contact_schedule':CONTACT,'lift_overrides':[{'actor':w,'side':s,'plant':p,'lift':v} for (w,s,p),v in LIFT_OVERRIDE.items()],'beats':BEATS,'exposure':'New contour drawings on twos;24fps render with per-frame contact and travel correction. Native drawing paths editable.'},indent=2))
 print('DRAWING_SOURCES_READY',168,flush=True)
