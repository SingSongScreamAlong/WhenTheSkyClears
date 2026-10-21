"""Bounded continuation of the reviewed v037/v038 coat, not a new design."""
import math
from mathutils import Vector
PER=31.;FPS=30.;ROWS=33;COLS=17
BACK=[(0,-.050),(.12,-.097),(.28,-.099),(.46,-.084),(.64,-.074),(.80,-.083),(1,-.110)]
FRONT=[(0,.033),(.12,.080),(.28,.110),(.46,.106),(.64,.084),(.80,.079),(1,.076)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def cat(t,K):
 i=next((j for j in range(len(K)-1) if t<=K[j+1][0]),len(K)-2);a,b=K[i],K[i+1];q=(t-a[0])/(b[0]-a[0]);p0=K[max(0,i-1)][1];p1=a[1];p2=b[1];p3=K[min(len(K)-1,i+2)][1]
 return .5*((2*p1)+(-p0+p2)*q+(2*p0-5*p1+4*p2-p3)*q*q+(-p0+3*p1-3*p2+p3)*q*q*q)
def periodic(values,x):
 n=len(values);i=math.floor(x);t=x-i;a,b,c,d=[values[j%n] for j in [i-1,i,i+1,i+2]];return .5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
def settled_lag(quarter_angles):
 # Actual trunk direction drives a damped angular follower. Twelve warm cycles
 # remove startup transients; the accepted silhouette receives only a small lag.
 dt=1/240;omega=15.;damping=.84;theta=quarter_angles[0];vel=0.;out=[];raw=[]
 for cycle in range(13):
  for step in range(248):
   q=step/8;target=periodic(quarter_angles,q*4)
   if cycle==12:
    delta=theta-target;raw.append(delta);out.append(math.radians(1.6)*math.tanh(delta*.75/math.radians(1.6)))
   vel+=(omega*omega*(target-theta)-2*damping*omega*vel)*dt;theta+=vel*dt
 return out,{'omega_radians_per_second':omega,'damping_ratio':damping,'integration_hz':240,'warm_cycles':12,'max_raw_difference_degrees':max(abs(math.degrees(v)) for v in raw),'max_applied_difference_degrees':max(abs(math.degrees(v)) for v in out),'method':'Settled response to actual existing pelvis-to-neck direction, smoothly limited with tanh. No independent flap clock or body action changes.'}
def points(h,n,zmin,zmax,compression,lag):
 U=(n-h).normalized();N=Vector((U.z,0,-U.x));arr=[];unlagged=[]
 for row in range(ROWS):
  t=row/(ROWS-1);z=.510*(1-t);a=cat(t,BACK);b=cat(t,FRONT);hemweight=max(0,(t-.65)/.35);a+=.004*compression*hemweight;b-=.003*compression*hemweight;free=smooth((t-.42)/.58)**2;angle=lag*free;cs=math.cos(angle);sn=math.sin(angle)
  for c in range(COLS):
   s=c/(COLS-1);x=a+(b-a)*s;corner=max(0,min(1,(t-.96)/.04));x+=.003*corner*((1-s)**12-s**12);hemrise=(.004*abs(2*s-1)**4+.008*math.exp(-((s-.80)/.075)**2))*t**8;zz=z+hemrise;fold=.17+.22*x;d=math.exp(-((zz-fold)/.018)**2);base=h+U*zz+N*x;unlagged.append(base);xx=cs*x+sn*(zz-.20);zl=-sn*x+cs*(zz-.20)+.20;p=h+U*zl+N*xx;p.y=-.017-.0035*math.sin(math.pi*s)**2-.0018*compression*d;arr.append(p)
 mn=min(p.z for p in arr);mx=max(p.z for p in arr)
 for p in arr:p.z=zmin+(p.z-mn)*(zmax-zmin)/(mx-mn)
 return arr
