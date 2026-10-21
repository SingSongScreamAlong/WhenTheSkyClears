"""Editable code/vector sources for the v0.1.2 west-room art study.

Authors actual bevelled geometry and material surfaces, not a flattened room image.
The SVG and recipe JSON are editable sources; PNGs rasterize those authored marks.
No existing publisher texture pixels or established WTSC paintings are modified.
"""
from pathlib import Path
import collections, hashlib, json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/AuthoredWestRoom';OUT.mkdir(parents=True,exist_ok=True)
parts=[];primitives=collections.defaultdict(lambda: {'p':[],'n':[],'uv':[],'idx':[]})
palette={
 'LimePlaster':(.46,.48,.42,1),'PlasterBreak':(.38,.36,.29,1),
 'Mortar':(.24,.26,.24,1),'BrickA':(.30,.28,.23,1),'BrickB':(.35,.31,.25,1),'BrickC':(.27,.29,.27,1),
 'Timber':(.31,.29,.23,1),'TimberEdge':(.39,.36,.28,1),'EndGrain':(.25,.26,.23,1),
 'FloorOak':(.28,.29,.25,1),'FloorEdge':(.35,.35,.29,1),
 'SashPaint':(.14,.21,.20,1),'SashWear':(.26,.27,.21,1),
 'Iron':(.10,.13,.13,1),'IronEdge':(.19,.22,.21,1),'Ceramic':(.56,.59,.53,1),
 'Cloth':(.34,.37,.34,1),'Rug':(.31,.33,.28,1),'Paper':(.64,.61,.48,1),
 'GlassDim':(.10,.18,.19,1),'LampInner':(.55,.44,.28,1),
}

def face(points,mat,normal=None,uv=None):
 p=np.array(points,float)
 keep=[i for i in range(len(p)) if not any(np.linalg.norm(p[i]-p[j])<1e-8 for j in range(i))]
 if len(keep)<3:return
 p=p[keep]
 if uv is not None:uv=[uv[i] for i in keep]
 n=np.cross(p[1]-p[0],p[2]-p[0]);n/=max(np.linalg.norm(n),1e-10)
 if normal is not None and np.dot(n,normal)<0:
  p=p[::-1];n=-n
  if uv is not None:uv=list(reversed(uv))
 if uv is None:
  axis=np.argmax(np.abs(n));inds=[i for i in range(3) if i!=axis]
  uv=[(v[inds[0]]/110, -v[inds[1]]/110) for v in p]
 d=primitives[mat];start=len(d['p']);d['p']+=p.tolist();d['n']+=[n.tolist()]*len(p);d['uv']+=list(uv)
 for i in range(1,len(p)-1):d['idx'] += [start,start+i,start+i+1]

def bevel(name,center,size,mat='Timber',b=1.0,rot=0,edge=None):
 h=np.array(size,float)/2;b=min(b,float(h.min())*.7);center=np.array(center,float)
 edge=edge or ('TimberEdge' if mat in ['Timber','FloorOak'] else mat)
 a=math.radians(rot);M=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 def emit(pts,normal,m):
  q=np.array(pts);gn=np.argmax(size)
  others=[i for i in range(3) if i!=gn and abs(normal[i])<.9]
  vn=others[0] if others else (gn+1)%3
  uv=[(v[gn]/(size[gn] or 1),v[vn]/(size[vn] or 1)) for v in q]
  face(q@M.T+center,m,np.array(normal)@M.T,uv)
 for axis in range(3):
  u,v=[i for i in range(3) if i!=axis]
  for sign in [-1,1]:
   pts=[]
   for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    p=np.zeros(3);p[axis]=sign*h[axis];p[u]=su*(h[u]-b);p[v]=sv*(h[v]-b);pts.append(p)
   normal=np.zeros(3);normal[axis]=sign
   emit(pts,normal,'EndGrain' if mat=='Timber' and axis==np.argmax(size) else mat)
 for free in range(3):
  u,v=[i for i in range(3) if i!=free]
  for su in [-1,1]:
   for sv in [-1,1]:
    pts=[]
    for pu,pv,pf in [(h[u],h[v]-b,-h[free]+b),(h[u],h[v]-b,h[free]-b),(h[u]-b,h[v],h[free]-b),(h[u]-b,h[v],-h[free]+b)]:
     p=np.zeros(3);p[u]=pu*su;p[v]=pv*sv;p[free]=pf;pts.append(p)
    normal=np.zeros(3);normal[u]=su;normal[v]=sv;emit(pts,normal,edge)
 for sx in [-1,1]:
  for sy in [-1,1]:
   for sz in [-1,1]:
    pts=[[sx*h[0],sy*(h[1]-b),sz*(h[2]-b)],[sx*(h[0]-b),sy*h[1],sz*(h[2]-b)],[sx*(h[0]-b),sy*(h[1]-b),sz*h[2]]]
    emit(pts,[sx,sy,sz],edge)
 parts.append({'name':name,'kind':'bevelled solid','center':center.tolist(),'size':size,'bevel_cm':b,'pitch_deg':rot,'material':mat})

def triangulate(poly):
 pts=np.array(poly,float);order=list(range(len(pts)));tris=[]
 if sum(pts[i,0]*pts[(i+1)%len(pts),1]-pts[(i+1)%len(pts),0]*pts[i,1] for i in order)<0:order.reverse()
 def cross(a,b,c):
  v=b-a;w=c-a;return float(v[0]*w[1]-v[1]*w[0])
 def inside(p,a,b,c):return cross(a,b,p)>=-1e-6 and cross(b,c,p)>=-1e-6 and cross(c,a,p)>=-1e-6
 for _ in range(len(poly)**2):
  if len(order)<=3:break
  for j,b in enumerate(order):
   a=order[j-1];c=order[(j+1)%len(order)]
   if cross(pts[a],pts[b],pts[c])>1e-8 and not any(inside(pts[k],pts[a],pts[b],pts[c]) for k in order if k not in [a,b,c]):
    tris.append([a,b,c]);order.pop(j);break
  else:raise ValueError('Non-simple plaster polygon')
 tris.append(order);return tris

def plaster(name,poly,yfront=272,yback=294):
 for tri in triangulate(poly):
  pts=[(poly[i][0],yfront,poly[i][1]) for i in tri]
  uv=[((p[0]+980)/900,1-p[2]/325) for p in pts]
  face(pts,'LimePlaster',[0,-1,0],uv)
 for a,b in zip(poly,poly[1:]+poly[:1]):face([(a[0],yfront,a[1]),(b[0],yfront,b[1]),(b[0],yback,b[1]),(a[0],yback,a[1])],'PlasterBreak')
 parts.append({'name':name,'kind':'extruded irregular plaster boundary','polygon_xz':poly,'front_y':yfront,'back_y':yback})

def tube(name,path,radius,mat='Iron',segments=12):
 p=np.array(path,float);rings=[]
 for i,pos in enumerate(p):
  direction=p[min(i+1,len(p)-1)]-p[max(0,i-1)];direction/=np.linalg.norm(direction)
  tangent=np.cross(direction,[0,1,0] if abs(direction[1])<.8 else [1,0,0]);tangent/=np.linalg.norm(tangent);other=np.cross(direction,tangent)
  rings.append([pos+radius*(math.cos(j*2*math.pi/segments)*tangent+math.sin(j*2*math.pi/segments)*other) for j in range(segments)])
 for i in range(len(rings)-1):
  for j in range(segments):face([rings[i][j],rings[i][(j+1)%segments],rings[i+1][(j+1)%segments],rings[i+1][j]],mat)
 parts.append({'name':name,'kind':'joined tube','path':p.tolist(),'radius':radius})

def lathe(name,x,y,z,profile,mat='Ceramic',n=32):
 for i in range(len(profile)-1):
  r0,h0=profile[i];r1,h1=profile[i+1]
  for j in range(n):
   a=j*2*math.pi/n;b=(j+1)*2*math.pi/n
   face([(x+r0*math.cos(a),y+r0*math.sin(a),z+h0),(x+r0*math.cos(b),y+r0*math.sin(b),z+h0),(x+r1*math.cos(b),y+r1*math.sin(b),z+h1),(x+r1*math.cos(a),y+r1*math.sin(a),z+h1)],mat)
 parts.append({'name':name,'kind':'lathed rimmed shell','center':[x,y,z],'profile':profile})

# Masonry is physically recessed behind broken plaster. The window is a true opening.
bevel('RecessedMortarBacking',[-530,307,163],[900,12,326],'Mortar',.7)
for row in range(28):
 z=8+row*11.4
 for col in range(23):
  x=-978+col*42+(21 if row%2 else 0)
  if x>-83 or (x>-782 and x<-541 and 141<z<289):continue
  bevel(f'BondedBrick_{row}_{col}',[x,296,z],[39.8,20,9.8],['BrickA','BrickB','BrickC'][(row+col*2)%3],.65)
# Keep actual sight through the window: mortar panels outside opening, no backing in its aperture.
# Remove the first backing primitive by regenerating it as four bounded panels below.
primitives.clear();parts.clear()
for center,size in [([-872,307,163],[196,12,326]),([-310,307,163],[460,12,326]),([-660,307,72],[230,12,144]),([-660,307,308],[230,12,36])]:bevel('RecessedMortarPanel',center,size,'Mortar',.6)
for row in range(28):
 z=8+row*11.4
 for col in range(23):
  x=-978+col*42+(21 if row%2 else 0)
  if x>-83 or (x>-782 and x<-541 and 141<z<289):continue
  bevel(f'BondedBrick_{row}_{col}',[x,296,z],[39.8,20,9.8],['BrickA','BrickB','BrickC'][(row+col*2)%3],.65)
plaster('WestPlaster',[[-962,23],[-905,23],[-909,53],[-894,55],[-899,75],[-868,72],[-874,98],[-838,108],[-843,135],[-775,148],[-775,286],[-962,310]])
plaster('SillPlaster',[[-962,23],[-905,23],[-909,53],[-894,55],[-899,75],[-868,72],[-874,98],[-838,108],[-843,135],[-775,148],[-550,148],[-550,112],[-533,102],[-538,84],[-520,74],[-520,24]])
plaster('StoveWall',[[-550,148],[-550,286],[-90,310],[-90,24],[-520,24],[-520,74],[-538,84],[-533,102],[-550,112]])
plaster('WindowHead',[[-962,310],[-90,310],[-90,324],[-962,324]])
# Brick returns and a cut-through left wall show believable wall depth.
for z in range(10,322,12):bevel('LeftWallReturn',[-966,64,z],[29,423,10.5],'BrickC',.8)
for x in [-964,-88]:bevel('RoomDoorJamb',[x,250,156],[19,42,312],'Timber',1.3)
bevel('BackWallSkirting',[-528,253,18],[855,12,29],'Timber',1.1)
bevel('WornSkirtingCap',[-528,245,34],[855,13,5],'TimberEdge',.8)
# Joinery: exposed joist ends, a scarfed front beam, visible boards above it.
for x in range(-930,-85,105):
 bevel('CeilingJoist',[x,65,308],[13,430,25],'Timber',1.0)
 bevel('JoistSeatBlock',[x,253,289],[19,33,12],'Timber',.8)
bevel('FrontHeaderWest',[-752,-146,308],[435,27,28],'Timber',1.5)
bevel('FrontHeaderEast',[-307,-146,308],[455,27,28],'Timber',1.5)
for x in [-946,-542,-103]:
 bevel('RepairIronStrap',[x,-162,308],[11,1.6,29],'Iron',.35)
 for z in [299,317]:lathe('BeamBolt',x,-163,z,[(0,0),(1.4,0),(1.4,1),(0,1)],'IronEdge',10)
for row in range(16):
 y=-139+row*27.1
 for a,b in [(-976,-600+(row%2)*80),(-598+(row%2)*80,-89)]:bevel('UpperFloorTongueBoard',[(a+b)/2,y,326],[b-a-1.2,26.1,6],'FloorOak',.5)
# Lower boards meet the existing walkable plane at Z=3 cm; collision is unchanged.
for row in range(16):
 y=-138+row*27
 joints=[-978,-810+(row%3)*27,-580+(row%2)*43,-355+(row%3)*18,-87]
 for a,b in zip(joints,joints[1:]):bevel('WornFloorboard',[(a+b)/2,y,.4],[b-a-1.0,26,5.2],'FloorOak',.55,edge='FloorEdge')
for x in range(-958,-85,92):bevel('FrontPlinthStone',[x,-173,-12],[90,47,22],'BrickC',1.4)
# Recessed casement: frame, shaped sill and thin old sash, never a painted flat window.
for x in [-771,-549]:
 bevel('WindowReveal',[x,281,218],[15,56,144],'SashPaint',1.2,edge='SashWear')
 bevel('WindowInnerBead',[x+(-5 if x<-600 else 5),247,218],[5,10,135],'Timber',.7)
bevel('WindowSill',[-660,252,146],[250,85,10],'Timber',1.3)
bevel('SillNose',[-660,206,146],[254,8,8],'SashPaint',1.1,edge='SashWear')
bevel('WindowLintel',[-660,278,291],[248,48,16],'Timber',1.5)
for x in [-760,-662,-558]:bevel('SashStile',[x,287,219],[5,8,133],'SashPaint',.6)
for z in [155,220,282]:bevel('SashRail',[-660,287,z],[207,8,5],'SashPaint',.5)
# One missing lower pane and a purposeful diagonal repair board.
bevel('WindowRepairBoard',[-710,265,197],[105,8,15],'Timber',.9,rot=13)
# Curtains are folded fabric surfaces with an irregular torn hem.
for side,x0 in [('left',-771),('right',-570)]:
 for j in range(8):
  x1=x0+j*4.2;x2=x1+4.2;y1=239+3*math.sin(j*math.pi/2);y2=239+3*math.sin((j+1)*math.pi/2)
  h1=158+[0,4,1,9,3,0,5,2][j];h2=158+[4,1,9,3,0,5,2,0][j]
  face([(x1,y1,284),(x2,y2,284),(x2,y2-4,h2),(x1,y1-4,h1)],'Cloth',[0,-1,0],[(j/8,0),((j+1)/8,0),((j+1)/8,1),(j/8,1)])
tube('CurtainRod',[[-790,228,289],[-524,228,289]],1.3)
# Stove hearth tiles, elbow pipe and seated collars all have actual thickness.
for i,(x,y,sx,sy,angle) in enumerate([(-229,162,48,70,-2),(-183,162,43,70,1),(-142,162,40,70,0),(-223,102,56,46,1),(-170,102,48,46,-1)]):
 bevel('HearthFlag',[x,y,4],[sx,sy,7],'BrickC',1.4,rot=angle*.2)
tube('StoveFlue',[[-185,182,105],[-185,182,230],[-185,185,240],[-185,199,250],[-185,268,250],[-185,299,250]],8.4)
for z in [119,195,228]:lathe('PipeCollar',-185,182,z,[(8.4,0),(9.5,1),(9.5,4),(8.4,5)],'IronEdge',16)
# Pendant reflector, wire and hook link to the timber above, rather than floating.
tube('LampCable',[[-435,120,294],[-435,120,254]],.65)
lathe('PendantShade',-435,120,245,[(2.5,11),(6,9),(18,-1),(20,-5),(18.5,-6),(5,7),(2.5,9)],'Iron',32)
lathe('PendantReflector',-435,120,245,[(3,7),(17,-2),(18,-4)],'LampInner',32)
# A pulled-out stool has tapered legs, seated cross braces and rounded seat edges.
bevel('StoolSeat',[-432,36,43],[39,34,6],'Timber',2.0)
for dx in [-14,14]:
 for dy in [-11,11]:bevel('StoolLeg',[-432+dx,36+dy,21],[5,5,40],'Timber',.6,rot=dx/14*2)
bevel('StoolBrace',[-432,24,16],[31,4,4],'Timber',.6)
bevel('StoolBrace',[-432,48,16],[31,4,4],'Timber',.6)
# Bedside care cabinet: open shelf, a supported top, four feet, and a separate bandage box prop.
for z in [8,30,54]:bevel('BedsideShelf',[-856,180,z],[56,43,5],'Timber',.9)
for x in [-881,-831]:bevel('BedsideSide', [x,180,31],[5,43,47],'Timber',.8)
bevel('BedsideBack',[-856,203,31],[51,4,47],'Timber',.6)
# Two places for a shared meal; the open bowls have proper inner surfaces and rolled lips.
for x,y in [(-458,130),(-402,153)]:lathe('SharedMealBowl',x,y,91.8,[(0,0),(4,0),(8.7,4),(10.3,8),(10,9),(9.2,8.8),(7.9,4.7),(3.4,1.4),(0,1.4)],'Ceramic')
lathe('TinCup',-374,165,91.8,[(0,0),(4.6,0),(5.5,10),(5.8,10.5),(5.1,11),(4.6,10),(4,1),(0,1)],'IronEdge',24)
tube('CupHandle',[[-368,165,101],[-365,165,101],[-364,165,97],[-368,165,94]],.65,'IronEdge',8)
# Folded cloth on the repair side of the table, plus a two-layer rug by the bed.
bevel('RepairCloth',[-443,180,92.5],[36,25,2.1],'Cloth',.8)
face([(-790,35,3.4),(-560,38,3.4),(-555,114,3.8),(-786,111,3.4)],'Rug',[0,0,1],[(0,0),(1,0),(1,1),(0,1)])
# A single pinned note (no invented photographic reference) supplies a domestic focal detail.
face([(-889,268,170),(-855,268,173),(-853,264,211),(-890,264,208)],'Paper',[0,-1,0],[(0,1),(1,1),(1,0),(0,0)])

# Editable SVG surfaces rendered from the same recipe. These are authored graphics, not AI paintings.
def svg_canvas(name,w,h,bg):
 return {'name':name,'w':w,'h':h,'bg':bg,'marks':[]}
def mark(c,kind,points,color,width=1,opacity=1):c['marks'].append({'kind':kind,'points':points,'color':color,'width':width,'opacity':opacity})
wall=svg_canvas('WestRoom_Plaster',2048,768,(132,135,118))
mark(wall,'polygon',[(0,512),(210,505),(430,518),(650,511),(820,506),(1110,512),(1400,508),(1690,514),(2048,505),(2048,768),(0,768)],(77,94,90))
for x,y,l,h in [(10,39,480,19),(510,66,430,21),(1000,42,670,16),(1550,93,470,28),(84,132,590,23),(760,152,480,27),(1310,181,610,19),(11,250,390,25),(450,278,520,31),(1030,253,470,24),(1510,320,490,21),(29,386,570,20),(670,418,570,26),(1320,442,590,20),(75,472,640,17),(1400,482,470,16)]:
 mark(wall,'polygon',[(x,y),(x+l,y-4),(x+l-30,y+h),(x+26,y+h+5)],(149,148,126),opacity=.18)
 mark(wall,'line',[(x+6,y+h+8),(x+l*.44,y+h+3),(x+l-14,y+h+9)],(98,110,101),width=2,opacity=.16)
# Window water tracks and sill staining align with actual geometry in world coordinates.
for x in [505,542,567,602,649,706,755,815,860,918]:
 mark(wall,'polygon',[(x,408),(x+12,413),(x+5,524+(x%5)*8),(x-3,565-(x%3)*11)],(77,99,96),opacity=.21)
# The flue stain rises exactly behind the stove pipe; no global noise layer.
for k,(x,y,rw,rh,op) in enumerate([(1809,120,174,370,.12),(1822,150,118,360,.16),(1818,208,77,280,.18),(1819,295,42,165,.16)]):
 mark(wall,'polygon',[(x-rw*.45,y),(x+rw*.43,y+12),(x+rw*.55,y+rh*.5),(x+rw*.34,y+rh),(x-rw*.35,y+rh-10),(x-rw*.55,y+rh*.5)],(37,48,47),opacity=op);wall['marks'][-1]['blur']=15
mark(wall,'line',[(987,113),(1035,141),(1018,175),(1050,201),(1059,246)],(66,77,72),width=2.4,opacity=.65)
mark(wall,'line',[(1034,141),(1074,125),(1090,104)],(73,83,76),width=1.5,opacity=.55)
for x in [200,227,254,281]:mark(wall,'line',[(x,472),(x+2,489)],(183,182,151),2,.6)
wood=svg_canvas('WestRoom_Timber',1024,256,(113,111,91))
for j in range(24):
 y=4+j*10.6;pts=[(0,y),(128,y+2),(260,y-3),(420,y+2),(600,y-4),(790,y+1),(1024,y-2)]
 mark(wood,'line',pts,(70,80,71) if j%3 else (158,150,118),1.5 if j%4 else 3,.26)
mark(wood,'line',[(0,94),(260,92),(430,97),(530,121),(600,129),(680,120),(760,100),(1024,94)],(54,66,58),2,.6)
mark(wood,'line',[(400,94),(500,79),(585,72),(648,80),(710,97)],(170,154,116),3,.4)
cloth=svg_canvas('WestRoom_Cloth',512,512,(112,121,113))
for j in range(0,512,16):
 mark(cloth,'line',[(j,0),(j+5,512)],(167,169,145),1,.10);mark(cloth,'line',[(0,j),(512,j+2)],(66,83,80),1,.10)
for x in [22,36,474,489]:mark(cloth,'line',[(x,0),(x,512)],(67,91,91),4,.5)
rug=svg_canvas('WestRoom_Rug',1024,512,(92,104,93))
for y in [28,44,468,484]:mark(rug,'line',[(14,y),(1010,y)],(143,130,99),5,.8)
for x in [25,43,980,997]:mark(rug,'line',[(x,20),(x,490)],(143,130,99),5,.8)
for x in range(100,980,95):mark(rug,'polygon',[(x,256),(x+40,187),(x+80,256),(x+40,325)],(114,112,87),opacity=.7)
paper=svg_canvas('WestRoom_Note',256,320,(186,178,145))
mark(paper,'line',[(29,125),(126,46),(224,124),(209,124),(209,267),(47,267),(47,124)],(77,90,80),6,.8)
mark(paper,'line',[(111,267),(111,186),(154,186),(154,267)],(77,90,80),5,.8)
for x in [69,175]:mark(paper,'polygon',[(x,145),(x+24,145),(x+24,173),(x,173)],(110,121,103),opacity=.7)

def render(c):
 w,h=c['w'],c['h'];im=Image.new('RGB',(w,h),c['bg']);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<defs><filter id="soft"><feGaussianBlur stdDeviation="15"/></filter></defs><rect width="{w}" height="{h}" fill="rgb{c["bg"]}"/>']
 for m in c['marks']:
  layer=Image.new('RGBA',(w,h));draw=ImageDraw.Draw(layer);points=[tuple(p) for p in m['points']];color=(*m['color'],round(255*m['opacity']))
  coords=' '.join(f'{x},{y}' for x,y in points);rgb=','.join(str(x) for x in m['color'])
  if m['kind']=='polygon':
   draw.polygon(points,fill=color);filt=' filter="url(#soft)"' if m.get('blur') else '';svg.append(f'<polygon points="{coords}" fill="rgb({rgb})" opacity="{m["opacity"]}"{filt}/>')
  else:draw.line(points,fill=color,width=max(1,round(m['width'])),joint='curve');svg.append(f'<polyline points="{coords}" fill="none" stroke="rgb({rgb})" stroke-width="{m["width"]}" opacity="{m["opacity"]}"/>')
  if m.get('blur'):layer=layer.filter(ImageFilter.GaussianBlur(m['blur']))
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 svg.append('</svg>');(OUT/(c['name']+'.svg')).write_text('\n'.join(svg),encoding='utf8');im.save(OUT/(c['name']+'.png'))
for c in [wall,wood,cloth,rug,paper]:render(c)

# glTF mapping is verified from the installed UE5.8 GLTF ConvertVec3: UE=(x,z,y).
blob=bytearray();views=[];accessors=[]
def buffer(a,typ,ctype):
 while len(blob)%4:blob.append(0)
 a=np.asarray(a,dtype='<f4' if ctype==5126 else '<u4');raw=a.tobytes();vi=len(views);views.append({'buffer':0,'byteOffset':len(blob),'byteLength':len(raw)});blob.extend(raw)
 d={'bufferView':vi,'componentType':ctype,'count':len(a),'type':typ}
 if typ=='VEC3':d.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 accessors.append(d);return len(accessors)-1
materials=[];prims=[]
for name,d in primitives.items():
 positions=np.asarray(d['p'])[:,[0,2,1]]/100;normals=np.asarray(d['n'])[:,[0,2,1]]
 indices=np.asarray(d['idx']).reshape(-1,3)[:,[0,2,1]].reshape(-1)
 attr={'POSITION':buffer(positions,'VEC3',5126),'NORMAL':buffer(normals,'VEC3',5126),'TEXCOORD_0':buffer(d['uv'],'VEC2',5126)}
 prims.append({'attributes':attr,'indices':buffer(indices,'SCALAR',5125),'material':len(materials)})
 materials.append({'name':'AR_'+name,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':palette[name],'metallicFactor':0,'roughnessFactor':.94}})
g={'asset':{'version':'2.0','generator':'WTSC v0.1.2 authored bevelled room; editable Python/recipe/SVG sources retained'},'buffers':[{'uri':'WestRoom_Assembly.bin','byteLength':len(blob)}],'bufferViews':views,'accessors':accessors,'materials':materials,'meshes':[{'name':'WestRoom_Assembly','primitives':prims}],'nodes':[{'name':'WestRoom_Assembly','mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
(OUT/'WestRoom_Assembly.bin').write_bytes(blob);(OUT/'WestRoom_Assembly.gltf').write_text(json.dumps(g,indent=2),encoding='utf8')
recipe={'scope':'One west shelter sleeping/heating room; no new map or gameplay system','units':'centimeters in recipe; glTF meters; X right, Y into shelter, Z up','parts':parts,'palette':palette,'surface_sources':[wall,wood,cloth,rug,paper],'surface_provenance':'Code-authored SVG marks and matching rasterization; no imagegen, no photo edits, no global noise overlay','construction':'Bevelled solid timber and masonry, extruded plaster boundaries, real window aperture/reveals, exposed joists, shaped pipe and rimmed vessels','geometry_stats':{'parts':len(parts),'vertices':sum(len(d['p']) for d in primitives.values()),'triangles':sum(len(d['idx'])//3 for d in primitives.values()),'material_slots':len(materials)},'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'WestRoom_Recipe.json').write_text(json.dumps(recipe,indent=2),encoding='utf8')
print(json.dumps(recipe['geometry_stats'],indent=2))
