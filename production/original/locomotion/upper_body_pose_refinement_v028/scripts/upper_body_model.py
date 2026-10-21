"""Authored v028 upper-body pose/spacing. Feet, pelvis and head are not inputs to edit.
Global sagittal arm directions are measured from down: positive points forward.
Angles below are degrees. q=frame-1, period31 at30fps; +X forward, Z up.
"""
import math
PER=31.
def pchip(xs,ys,x):
    n=len(xs);h=[xs[i+1]-xs[i] for i in range(n-1)];d=[(ys[i+1]-ys[i])/h[i] for i in range(n-1)];m=[0.]*n
    for i in range(1,n-1):
        if d[i-1]*d[i]>0:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i])
    m[0]=d[0];m[-1]=d[-1];i=max(0,min(n-2,next((i for i in range(n-1) if x<=xs[i+1]),n-2)));t=max(0,min(1,(x-xs[i])/h[i]))
    return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h[i]*m[i+1]
def cyclic(knots,q):
    xs=[k[0] for k in knots];ys=[k[1] for k in knots];return pchip([x-PER for x in xs]+xs+[x+PER for x in xs],ys*3,q%PER)
TRUNK=[(0,0),(3.75,-1.6),(5.5,-1.35),(9.5,.45),(12.5,.65),(16,0),(20,-1.4),(21.5,-1.2),(25.5,.55),(28.5,.45)]
UPPER={
 'near':[(0,-18),(3.5,-23.5),(8,-9),(12,9),(16.25,18),(19,17),(25,1.5),(28,-9.5)],
 'far':[(0,14),(2,15.5),(6,13),(10,-1),(14,-14),(18.75,-19),(21,-16),(26,5),(29,12)]}
FLEX={
 'near':[(0,19),(3.75,16),(8.5,30),(12,28),(16.5,23),(20,25),(25.5,31),(28.5,24)],
 'far':[(0,23),(4,21),(9.5,27),(14,22),(19,18),(23.5,27),(27,29)]}
DELAY={'near':1.5,'far':1.0};HAND_DELAY={'near':.75,'far':.5}
def trunk_delta(q):return math.radians(cyclic(TRUNK,q))
def forearm_degrees(side,q):return cyclic(UPPER[side],q-DELAY[side])+cyclic(FLEX[side],q)
def arm(side,q):
    return tuple(math.radians(v) for v in [cyclic(UPPER[side],q),forearm_degrees(side,q),forearm_degrees(side,q-HAND_DELAY[side])-3.])
def extra_hem_lag(q):
    # Linear damped response to the changed trunk bend. Old v027 response remains.
    dt=1/240;omega=15.;damping=.84;theta=trunk_delta(q-12*PER);velocity=0.
    for i in range(12*248):
        t=q-12*PER+(i+1)/8;velocity+=(omega*omega*(trunk_delta(t)-theta)-2*damping*omega*velocity)*dt;theta+=velocity*dt
    return theta-trunk_delta(q)
