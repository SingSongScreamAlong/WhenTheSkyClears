"""Small garment/hand construction corrections; no bone or motion edits."""
import math
from mathutils import Vector
def smooth(u):u=max(0,min(1,u));return u*u*(3-2*u)
def interp(t,keys):
 if t<=keys[0][0]:return float(keys[0][1])
 if t>=keys[-1][0]:return float(keys[-1][1])
 i=next(i for i in range(len(keys)-1) if keys[i][0]<=t<=keys[i+1][0]);x0,y0=keys[i];x1,y1=keys[i+1];h=x1-x0;u=(t-x0)/h;m0=(y1-y0)/h if i==0 else (keys[i+1][1]-keys[i-1][1])/(keys[i+1][0]-keys[i-1][0]);m1=(y1-y0)/h if i==len(keys)-2 else (keys[i+2][1]-keys[i][1])/(keys[i+2][0]-keys[i][0]);return y0*(2*u**3-3*u*u+1)+m0*h*(u**3-2*u*u+u)+y1*(-2*u**3+3*u*u)+m1*h*(u**3-u*u)
def torso_delta(who,t,s):
 if who=='BOY':bk=[(0,0),(.12,.007),(.28,.006),(.55,-.014),(.8,.005),(1,0)];fr=[(0,0),(.12,-.005),(.28,-.015),(.55,.005),(.8,-.007),(1,0)]
 else:bk=[(0,0),(.12,.005),(.27,.005),(.5,-.012),(.72,0),(1,0)];fr=[(0,0),(.12,-.006),(.27,-.020),(.5,.003),(.72,0),(1,0)]
 return (1-s)*interp(t,bk)+s*interp(t,fr)
def forearm_radius(t):return interp(t,[(0,.030),(.25,.0295),(.65,.025),(.9,.022),(1,.021)])
def hand_x(x,px,py):
 # Keep every original vertical coordinate/length. Group existing fingers and
 # thumb locally; taper the wrist into the forearm rather than scaling the hand.
 factor=interp(py,[(940,.80),(980,.80),(1030,.94),(1090,.92),(1200,.94)])
 thumb=.005*smooth((px-265)/50)*smooth((py-990)/65)*(1-smooth((py-1100)/65))
 little=.0025*smooth((200-px)/45)*smooth((py-1040)/65)*(1-smooth((py-1140)/60))
 return x*factor-thumb+little
def sleeve_radius(t):return interp(t,[(0,.012),(.06,.034),(.18,.047),(.5,.044),(.85,.035),(1,.0375)])
def rounded(H,K,A,l1,d,radius):
 U=(K-H).normalized();V=(A-K).normalized()
 if d<l1-radius:return H+U*d,U
 if d>l1+radius:return K+V*(d-l1),V
 u=(d-l1+radius)/(2*radius);p=K-U*radius;q=K+V*radius;m=U*2*radius;n=V*2*radius;pos=p*(2*u**3-3*u*u+1)+m*(u**3-2*u*u+u)+q*(-2*u**3+3*u*u)+n*(u**3-u*u);der=p*(6*u*u-6*u)+m*(3*u*u-4*u+1)+q*(-6*u*u+6*u)+n*(3*u*u-2*u);return pos,der.normalized()
def limb_vertices(r,pose,side,kind,refined=True):
 n1=('upper_arm_' if kind=='sleeve' else 'thigh_')+side;n2=('forearm_' if kind=='sleeve' else 'shin_')+side;l1=r.data.bones[n1].length;total=l1+r.data.bones[n2].length;start=(-.018 if refined else -.008) if kind=='sleeve' else -.025;end=l1+.027 if kind=='sleeve' else total-.030;rows=49 if kind=='sleeve' else 65;who='BOY' if 'BOY' in r.name else 'GIRL';H=pose[n1]['head'];K=pose[n1]['tail'];A=pose[n2]['tail'];verts=[]
 for row in range(rows):
  t=row/(rows-1);d=start+(end-start)*t
  rad=(sleeve_radius(t) if refined else interp(t,[(0,.038),(.12,.049),(.5,.045),(.85,.034),(1,.041)])) if kind=='sleeve' else interp(t,[(0,.060),(.13,.063),(.4,.052),(.56,.043),(.77,.044),(.92,.034),(1,.040)]) if who=='BOY' else interp(t,[(0,.043),(.45,.036),(.56,.031),(.78,.033),(1,.024)])
  for col in range(9):
   s=col/8;dd=d+(.004*math.sin(math.pi*s)*smooth((t-.85)/.15) if kind=='sleeve' and refined else 0);center,tangent=rounded(H,K,A,l1,dd,.018 if kind=='sleeve' else .022);normal=Vector((-tangent.z,0,tangent.x));p=center+normal*((s*2-1)*rad);p.y=0
   if kind=='leg':w=smooth((dd-(total-.095))/.065);rest=Vector(((s*2-1)*rad,0,r.data.bones[n1].head_local.z-dd));bound=pose['foot_'+side]['matrix']@r.data.bones['foot_'+side].matrix_local.inverted()@rest;p=p.lerp(bound,w);p.y=0
   verts.append(p)
 return verts
