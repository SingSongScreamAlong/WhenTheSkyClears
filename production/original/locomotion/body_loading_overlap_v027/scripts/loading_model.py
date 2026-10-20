"""v027 body spacing. Feet, stride, root and rest lengths remain v026 exactly.
Frame 1 is contact; q=frame-1; 31 frames at 30fps. Metres, X forward, Z up.
Only pelvis spacing and upper mass loading are authored here. No leg stretch.
"""
import math
import numpy as np
import baseline_motion_model as B

XQ=[0.,2.75,9.5,15.5,19.5,25.,28.5]
XV=[0.,-.009,.030,.045,.023,.004,-.003]
ZQ=[0.,2.75,4.5,8.,10.5,13.,16.,18.75,20.5,24.,26.75,29.]
ZV=[.5897787668503744,.5748,.578,.600,.608,.603,.5861138282500814,.5748,.5785,.600,.608,.602]
AQ=[0.,3.75,5.5,9.5,13.,16.,20.,21.5,25.,28.5]
AV=[3.0,7.4,7.0,3.3,2.2,3.2,7.0,6.4,3.0,2.1]
STRIDE=B.STRIDE
PER=B.PER

def hip(q):return np.array([STRIDE*q/PER+B.cyclic(XV,q,XQ),B.cyclic(ZV,q,ZQ)])
def chest_angle(q):return math.radians(B.cyclic(AV,q,AQ))
def upper_origin(q):
    # The torso keeps descending after the pelvis arrests; it then recovers.
    # This is a small spring-like compression at the trunk, not a head bob.
    h=hip(q);delayed=hip(q-1.0)
    return h+np.array([0.,.85*(delayed[1]-h[1])])

def evaluate(q):
    r=B.evaluate(q);r['H']=hip(q);r['upper_origin']=upper_origin(q);r['chest']=chest_angle(q)
    r['knees']={};r['angles']={};r['margins']={}
    for s in ['near','far']:
        off=B.M.rotate(B.M.v2(B.M.REST['thigh_'+s]['head'])-B.M.v2(B.M.REST['pelvis']['head']),r['pelvis'])
        a,k,d=B.M.ik(r['H']+off,r['feet'][s]['A'],s)
        r['knees'][s]=k;r['angles'][s]=a;r['margins'][s]=sum(B.M.LENS[s])-d
    return r

def cloth_response(q):
    # Settled damped follower. Its only input is the authored trunk direction.
    # Re-simulate twelve cycles at 240Hz so no first-cycle transient enters.
    dt=1/240;omega=15.;damping=.84;theta=chest_angle(q-12*PER);velocity=0.
    for i in range(12*248):
        t=q-12*PER+(i+1)/8
        velocity+=(omega*omega*(chest_angle(t)-theta)-2*damping*omega*velocity)*dt
        theta+=velocity*dt
    return theta-chest_angle(q)

if __name__=='__main__':
    import json
    rows=[evaluate(i/8) for i in range(249)]
    print(json.dumps({'min_margin':min(v for r in rows for v in r['margins'].values()),'bad':[(r['q'],s,v) for r in rows for s,v in r['margins'].items() if v<.0008],
        'hip':[[q,hip(q).tolist(),math.degrees(chest_angle(q))] for q in [0,2.75,4.5,8,10.5,16,18.75,20.5,24,26.75,29,31]]},indent=2))
