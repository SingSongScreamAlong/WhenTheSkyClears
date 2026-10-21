"""Develop v068 whole-body action using painted layers and full-frame drawings."""
import base_pose_spec as M
from base_pose_spec import *
from pathlib import Path
import json
PALETTE=M.PALETTE
PALETTE['linen']='#bdb8a3'
def paired(g):
 P={w:M.pose(w,g) for w in ['BOY','GIRL']};offset={'BOY':-.37,'GIRL':.37}
 shoulders={w:add(P[w]['shoulder_near'],(offset[w],0)) for w in P};mid=mix(shoulders['BOY'],shoulders['GIRL'],.5)
 centre=(mid[0]+track(g,[(913,0),(973,-.02),(983,-.035),(991,-.015),(997,.025),(1009,0),(1080,0)]),mid[1]-track(g,[(913,.25),(979,.30),(985,.285),(991,.255),(997,.29),(1009,.30),(1080,.285)]))
 if g>=983:
  floor=[]
  for w,sh in shoulders.items():
   sign=1 if w=='BOY' else -1;dx=centre[0]-sign*.045-sh[0]
   floor.append(sh[1]-math.sqrt(max(.001,.426**2-dx*dx))+.008)
  centre=(centre[0],max(centre[1],*floor))
 for w,p in P.items():
  sign=1 if w=='BOY' else -1;reach=p['reach'];sh=p['shoulder_near'];target=(centre[0]-offset[w]-sign*.045,centre[1]+(.006 if w=='BOY' else -.006))
  W=mix(p['wrist_near'],target,reach)
  if w=='GIRL':W=add(W,(track(g,[(913,0),(973,-.018),(979,.018),(985,0),(1080,0)]),0))
  if length(sub(W,sh))>.430:W=add(sh,mul(unit(sub(W,sh)),.430))
  E=ik(sh,W,.233,.199,sign=-1 if w=='BOY' else 1)
  p['elbow_near']=mix(p['elbow_near'],E,reach);p['wrist_near']=W
  p['hand_close']=track(g,[(913,0),(985 if w=='GIRL' else 987,0),(991 if w=='GIRL' else 995,1),(1080,1)])
  # Let the free hand settle open after the linked move-off, retaining the
  # distinct protecting gesture around the notice/reach rather than a fist.
  relax=track(g,[(913,0),(991,0),(1011,1),(1080,1)])
  p['wrist_far']=add(p['wrist_far'],(-.018*relax,-.045*relax));p['elbow_far']=add(p['elbow_far'],(-.012*relax,-.012*relax))
  p['offset']=offset[w];p['contact_centre']=centre
 return P

def head_column(w,g,p):
 if g<(951 if w=='GIRL' else 961):return 0
 f=p['facing']
 return 1 if f>.80 else 2 if f>.28 else 3 if f>-.28 else 4 if f>-.78 else 5

def draw_actor(w,g,P=None):
 pp=P or paired(g);d,p=M.draw_actor(w,g,pp)
 d.paths=[q for q in d.paths if not q['layer'].startswith(('head |','face |','neck |'))]
 for q in d.paths:
  q['width']*=.65
  if q['layer'].startswith('collar |'):q['fill']='linen'
  if q['layer'].startswith('braid |'):
   f=p['facing'];lag=track(g,[(913,0),(955,.015),(963,-.045),(977,.035),(989,-.015),(1009,.025),(1080,0)])
   anchor=add(p['head'],(p['offset']-.065*f,-.060));U=unit((-.105*f+lag,-.180));N=perp(U);out=[]
   for x,z in q['points']:
    v=sub((x,z),anchor);a=v[0]*U[0]+v[1]*U[1];b=v[0]*N[0]+v[1]*N[1];v=add(anchor,add(mul(U,a*1.12),mul(N,b*1.65)));out.append((v[0],v[1]+.029))
   q['points']=out
 return d,p

if __name__=='__main__':
 O=Path(__file__).resolve().parents[1]
 for g in range(913,1081):
  pp=paired(g)
  for w in ['BOY','GIRL']:
   d,p=draw_actor(w,g,pp);save_svg(d,O/'drawings'/f'{w}_{g:04d}.svg')
 (O/'evidence/ACTING_KEYS.json').write_text(json.dumps({'base_keys':KEYS,'new_offset_m':{'BOY':-.37,'GIRL':.37},'changes':['Full24fps body/drawing exposures instead of a held drawing every two frames','Lower coupled grip, reduced shoulder spacing, naturally bent receiving arms','Free hands relax after contact; preserved staggered notice/reach/receive rhythm','Painted generated head-angle atlas selected by actual turn; original cloth/skin/leather painting reused on the new contour layers'],'contact_schedule':CONTACT,'beats':BEATS,'artistic_acceptance':False},indent=2))
 print('V069_DRAWINGS_READY',336,flush=True)
