"""Original metric set geometry; numeric data goes through native typed mesh tools.
No third-party model data. Seed and recipes persist with the editable project.
"""
import math,random,json
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work/living_world_meshes';OUT.mkdir(exist_ok=True)
R=random.Random(93161016)
G={};META={};COUNTS=defaultdict(int)

def height(x,y=0):
    wall=.27*max(0,min(1,(x-13)/.7,(20-x)/.7)) if 13<x<20 else 0
    crater=-.62*math.sin((x-44)/5*math.pi)**2 if 44<x<49 else 0
    title=.10*max(0,math.sin((x-67)*1.8)) if 67<x<94 else 0
    terrain=(.16*math.sin(x*.43+y*.37)+.10*math.cos(x*.21-y*.6))*min(1,abs(y)/3)
    return wall+crater+title+terrain

def group(region,kind,motion=None):
    key=(region,kind);i=COUNTS[key];name=f'LW_{region}_{kind}_{i:02d}'
    if name in G and len(G[name]['vertices'])>27000:
        COUNTS[key]+=1;return group(region,kind,motion)
    if name not in G:
        G[name]={'name':name,'vertices':[],'faces':[]}
        META[name]={'region':region,'material':kind,'motion':motion,'face_tints':[]}
    return name

def add(region,kind,verts,faces,motion=None,tint=None):
    n=group(region,kind,motion);g=G[n];o=len(g['vertices'])
    g['vertices'].extend([[round(v,5) for v in p] for p in verts]);g['faces'].extend([[o+i for i in f] for f in faces])
    META[n]['face_tints'].extend([tint if tint is not None else R.uniform(.82,1.12)]*len(faces))
    return n

def box(region,kind,center,size,angle=0,tint=None):
    cx,cy,cz=center;w,d,h=[s/2 for s in size];c=math.cos(angle);s=math.sin(angle)
    pts=[]
    for x,y,z in [(-w,-d,-h),(w,-d,-h),(w,d,-h),(-w,d,-h),(-w,-d,h),(w,-d,h),(w,d,h),(-w,d,h)]:
        pts.append((cx+x*c-y*s,cy+x*s+y*c,cz+z))
    return add(region,kind,pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],tint=tint)

def tube(region,kind,a,b,r1,r2=None,sides=8,motion=None):
    r2=r1*.65 if r2 is None else r2
    dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
    if length<.0001:return
    d=(dx/length,dy/length,dz/length);u=(-d[1],d[0],0)
    ul=math.hypot(u[0],u[1]);u=(1,0,0) if ul<.001 else tuple(v/ul for v in u)
    v=(d[1]*u[2]-d[2]*u[1],d[2]*u[0]-d[0]*u[2],d[0]*u[1]-d[1]*u[0])
    verts=[]
    for p,r in [(a,r1),(b,r2)]:
        for j in range(sides):
            q=j*math.tau/sides;verts.append(tuple(p[k]+r*(math.cos(q)*u[k]+math.sin(q)*v[k]) for k in range(3)))
    faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(j,(j+1)%sides,(j+1)%sides+sides,j+sides) for j in range(sides)]
    return add(region,kind,verts,faces,motion)

def rock(region,c,scale,kind='Stone'):
    x,y,z=c;sx,sy,sz=scale;n=7
    ring=[(x+sx*math.cos(j*math.tau/n)*R.uniform(.75,1.1),y+sy*math.sin(j*math.tau/n)*R.uniform(.75,1.1),z+sz*R.uniform(-.08,.15)) for j in range(n)]
    top=[(x+(p[0]-x)*.65,y+(p[1]-y)*.65,z+sz*R.uniform(.6,1.05)) for p in ring]
    return add(region,kind,ring+top,[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]+[tuple(range(n,2*n))])

def arch(region,kind,x,y,z,w,h,thick=.13):
    # Radiating voussoirs make actual arched stone window/door surrounds.
    r=w/2
    for j in range(11):
        a=j*math.pi/11;b=(j+1)*math.pi/11
        verts=[]
        for yy in [y-thick/2,y+thick/2]:
            verts.extend([(x+rr*math.cos(q),yy,z+h-r+rr*math.sin(q)) for rr,q in [(r,a),(r,b),(r+.16,b),(r+.16,a)]])
        add(region,kind,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    for side in [-1,1]:box(region,kind,(x+side*(r+.08),y,z+(h-r)/2),(.16,thick,h-r))

def window(region,x,y,z,w=1.0,h=1.4,shutters=True,lit=False,broken=False):
    if not broken:box(region,'WindowGlow' if lit else 'Glass',(x,y+.05,z+h/2),(w,.055,h))
    for xx in [-w/2,w/2]:box(region,'Stone',(x+xx,y-.07,z+h/2),(.13,.23,h+.22))
    for zz in [z-.06,z+h+.06]:box(region,'Stone',(x,y-.08,zz),(w+.25,.25,.13))
    for xx in [-w/2,w/2,0]:box(region,'Wood',(x+xx,y-.16,z+h/2),(.055,.07,h))
    box(region,'Wood',(x,y-.18,z+h*.5),(w,.07,.055))
    if shutters:
        for side in [-1,1]:
            sx=x+side*(w/2+.29);box(region,'Shutter',(sx,y-.12,z+h/2),(.43,.09,h+.04),angle=side*.08)
            for j in range(7):box(region,'Shutter',(sx,y-.19,z+.12+j*(h-.12)/7),(.42,.065,.045))
    if broken:
        for j in [0,2,5]:
            sx=x-w*.35+j*w*.12;zz=z+h*.58+(j%2)*.14
            add(region,'Glass',[(sx,y-.18,zz),(sx+.16,y-.18,zz+.23),(sx+.22,y-.18,zz-.08)],[(0,1,2)])

def roof(region,x,y,z,w,d,rise,damage=False):
    # Each overlapping barrel tile has curvature and thickness; no roof billboard.
    cols=max(1,int(w/.29));rows=max(1,int((d/2)/.29))
    for side in [-1,1]:
        for row in range(rows+1):
            p=row/max(rows,1);yy=y+side*(d/2+.25)*(1-p);zz=z+rise*p
            for col in range(cols+1):
                if damage and col>cols*.52 and row>rows*.18 and R.random()<.82:continue
                xx=x-w/2+col*w/cols
                verts=[]
                for along in [0,.34]:
                    for j in range(5):
                        q=j*math.pi/4
                        verts.append((xx+(j/4-.5)*.33,yy-side*along,zz+along*rise/(d/2+.25)+math.sin(q)*.045+R.uniform(-.006,.006)))
                add(region,'Roof',verts,[(j,j+1,j+6,j+5) for j in range(4)])
    for side in [-1,1]:
        for xx in [x-w/2-.15,x+w/2+.15]:tube(region,'Wood',(xx,y+side*(d/2+.3),z-.05),(xx,y,z+rise+.07),.055,.055,6)
    tube(region,'Roof',(x-w/2-.25,y,z+rise+.06),(x+w/2+.25,y,z+rise+.06),.105,.105,8)

def house(region,x,y,w=4.8,d=3.7,h=4.6,bakery=False,abandoned=False):
    base=height(x,y);front=y-d/2
    # Thick wall slabs deliberately leave the openings empty.
    openings=[(x-w*.28,.5,1.0,1.5),(x+w*.27,.5,1.1,1.5),(x-w*.27,2.75,1.0,1.35),(x+w*.27,2.75,1.0,1.35)]
    if bakery:openings=[(x-w*.25,.25,.95,2.2),(x+w*.18,.6,2.15,1.6),(x,2.9,1.05,1.35)]
    else:openings.append((x,.15,.86,2.0))
    xs=sorted(set([x-w/2,x+w/2]+[a+side*c/2 for a,b,c,d0 in openings for side in [-1,1]]))
    zs=sorted(set([0,h]+[b+side*d0 for a,b,c,d0 in openings for side in [0,1]]))
    for a,b in zip(xs,xs[1:]):
        for c,e in zip(zs,zs[1:]):
            midx=(a+b)/2;midz=(c+e)/2
            if any(abs(midx-ox)<ow/2-.001 and oz<midz<oz+oh for ox,oz,ow,oh in openings):continue
            box(region,'Plaster',(midx,front,base+midz),(b-a,.30,e-c))
    for side in [-1,1]:box(region,'Plaster',(x+side*w/2,y,base+h/2),(.3,d,h))
    box(region,'Plaster',(x,y+d/2,base+h/2),(w,.3,h))
    box(region,'Stone',(x,y,base+.14),(w+.18,d+.18,.28))
    for ox,oz,ow,oh in openings:
        if oh>1.8:
            box(region,'Wood',(ox,front+.06,base+oz+oh/2),(ow,.13,oh));arch(region,'Stone',ox,front-.18,base+oz,ow,oh)
            rock(region,(ox+ow*.32,front-.17,base+.95),(.035,.035,.035),'Metal')
        else:window(region,ox,front-.18,base+oz,ow,oh,shutters=not bakery or oz>2,lit=bakery and not abandoned)
    for side in [-1,1]:
        # Front gable is visible in 3D; painted masonry, real thickness.
        add(region,'Plaster',[(x-w/2,front,base+h),(x+w/2,front,base+h),(x,front,base+h+1.65)],[(0,1,2)]) if side==1 else None
    roof(region,x,y,base+h,w+.35,d+.55,1.65)
    box(region,'Stone',(x+w*.3,y+.65,base+h+1.6),(.5,.53,1.45))
    box(region,'Stone',(x+w*.3,y+.65,base+h+2.34),(.63,.66,.14))
    for ox in [x-w/2+.1,x+w/2-.1]:
        for zz in range(9):box(region,'Stone',(ox,front-.07,base+.25+zz*.47),(.38,.23,.28))
    if bakery:
        box(region,'Wood',(x+w*.2,front-.6,base+.39),(2.4,.8,.13))
        for sx in [-.8,0,.8]:
            tube(region,'Wood',(x+sx,front-.5,base+.12),(x+sx,front-.5,base+.42),.045,.045)
        for j in range(9):rock(region,(x-.2+(j%5)*.4,front-.7+(j//5)*.24,base+.46),(.17,.095,.12),'Bread')
    return base,front

def cloth(name,x,y,z,w,h,region='Village'):
    verts=[];faces=[];nx=12;nz=10
    for j in range(nz+1):
        for i in range(nx+1):
            u=i/nx;v=j/nz;verts.append((x+(u-.5)*w,y+.055*math.sin(u*17)*v,z-v*h+.035*math.sin(u*8)*v))
    for j in range(nz):
        for i in range(nx):k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
    add(region,name,verts,faces,'Cloth')
    META[group(region,name)]['material']='Cloth'

def tree(region,x,y,h=6,canopy=True,foreground=False):
    z=height(x,y);top=(x+.2,y+.06,z+h*.83)
    tube(region,'Bark',(x,y,z),(x+.06,y-.08,z+h*.35),h*.054,h*.038,10)
    tube(region,'Bark',(x+.06,y-.08,z+h*.35),top,h*.038,.035,9,'Branches')
    # Roots, long trunks and tapering limbs all have real depth.
    for k in range(5):
        a=k*math.tau/5
        tube(region,'Bark',(x+math.cos(a)*.65,y+math.sin(a)*.65,z-.015),(x,y,z+.45),.08,.14,7)
    ends=[]
    for k in range(10):
        a=k*2.4+R.random()*.4;level=.38+k*.037
        start=(x+.05,y,z+h*level);reach=h*R.uniform(.22,.4)
        end=(x+math.cos(a)*reach,y+math.sin(a)*reach*.75,z+h*R.uniform(.68,.97))
        mid=tuple(start[i]+(end[i]-start[i])*.58 for i in range(3))
        tube(region,'Bark',start,mid,.09,.05,7,'Branches');tube(region,'Bark',mid,end,.05,.013,6,'Branches')
        for j in range(3):
            q=a+(j-1)*.65
            e=(end[0]+math.cos(q)*h*.11,end[1]+math.sin(q)*h*.10,end[2]+h*R.uniform(.08,.16))
            tube(region,'Bark',mid,e,.037,.007,5,'Branches');ends.append(e)
    if canopy:
        for ex,ey,ez in ends:
            for j in range(2):
                center=(ex+R.uniform(-.3,.3),ey+R.uniform(-.25,.25),ez+R.uniform(-.15,.25))
                a=R.uniform(-.5,.5);w=h*R.uniform(.23,.34);hh=w*.69
                ux=(math.cos(a),math.sin(a),0);vz=(.10,-.18,1)
                verts=[tuple(center[k]+ux[k]*sx*w/2+vz[k]*sz*hh/2 for k in range(3)) for sx,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                add(region,'Leaves',verts,[(0,1,2,3)],'Canopy')

def fence(region,x1,x2,y):
    n=max(2,int((x2-x1)/.28))
    for j in range(n+1):
        x=x1+(x2-x1)*j/n;z=height(x,y)
        box(region,'Wood',(x,y,z+.5),(.12,.12,R.uniform(.85,1.06)),R.uniform(-.07,.07))
    for zz in [.27,.72]:box(region,'Wood',((x1+x2)/2,y,height((x1+x2)/2,y)+zz),(x2-x1,.1,.09))

def ruin(region,x,y,w,h,d=3):
    z=height(x,y);front=y-d/2
    for row in range(int(h/.32)):
        for col in range(int(w/.43)):
            xx=x-w/2+(col+.5)*.43+(row%2)*.17;zz=(row+.5)*.32
            silhouette=h*(.62+.2*math.sin((xx-x)*1.9)+.15*math.cos((xx-x)*4.1))
            hole=(abs(xx-x)<.62 and 1.2<zz<2.6)
            if zz>silhouette or hole or (row>3 and R.random()<.08):continue
            box(region,'Stone',(xx,front+R.uniform(-.03,.03),z+zz),(.42,.38,.30),R.uniform(-.025,.025))
    for side in [-1,1]:
        for j in range(6):box(region,'Stone',(x+side*w/2,y-d/2+j*.44,z+.3+.08*j),(.4,.45,.65+R.random()*.4))
    for j in range(65):
        xx=x+R.uniform(-w*.7,w*.7);yy=front+R.uniform(-1.4,1.2)
        rock(region,(xx,yy,height(xx,yy)),(R.uniform(.09,.34),R.uniform(.1,.25),R.uniform(.08,.24)))
    for j in range(5):
        a=(x-w/2+j*w/5,front+.3,z+R.uniform(.25,1))
        b=(a[0]+R.uniform(.5,1.6),front+R.uniform(.2,1.5),z+R.uniform(.3,1.2))
        tube(region,'Charred',a,b,.065,.045,6)

def tent(x,y,w=3.7,d=3.5):
    region='Camp';z=height(x,y);peak=2.55;eave=1.0
    for side in [-1,1]:
        verts=[];faces=[];n=16;m=12
        for j in range(m+1):
            v=j/m
            for i in range(n+1):
                u=i/n
                verts.append((x+(u-.5)*w,y+side*v*d/2,z+peak-v*(peak-eave)-.11*math.sin(u*math.pi)*math.sin(v*math.pi)))
        for j in range(m):
            for i in range(n):k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
        add(region,'TentCanvas',verts,faces,'Tent')
        for xx in [x-w/2,x+w/2]:
            tube(region,'Wood',(xx,y,z),(xx,y,z+peak),.045,.045)
            tube(region,'Rope',(xx,y+side*d/2,z+eave),(xx+(.35 if xx>x else -.35),y+side*(d/2+.6),z+.03),.011,.011,5)
    for xx in [x-w/2,x+w/2]:
        # Partial end walls leave a real dark open mouth.
        for a,b in [(-1,-.25),(.25,1)]:
            yy1=y+a*d/2;yy2=y+b*d/2
            add(region,'TentCanvas',[(xx,yy1,z),(xx,yy2,z),(xx,yy2,z+peak-abs(b)*(peak-eave)),(xx,yy1,z+peak-abs(a)*(peak-eave))],[(0,1,2,3)],'Tent')

# Continuous mesh with a real verge and gentle depth variation, preserving route height.
verts=[];faces=[];nx=260;ny=44
for j in range(ny+1):
    y=-9+j*47/ny
    for i in range(nx+1):
        x=-17+i*134/nx;verts.append((x,y,height(x,y)))
for j in range(ny):
    for i in range(nx):k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1))
add('Terrain','Earth',verts,faces)

# A narrow worn performance path, cobbles and water break the broad ground surface.
for i in range(246):
    x=-10+i*.48
    for j in [-1,1]:
        y=j*R.uniform(1.15,1.55)
        rock('Terrain',(x,y,height(x,y)-.035),(R.uniform(.13,.22),.17,R.uniform(.06,.11)))
for i in range(650):
    x=R.uniform(-10,28);y=R.choice([-1,1])*R.uniform(1.55,6.5);z=height(x,y)
    for k in range(3):
        a=k*2.1+R.random();h=R.uniform(.11,.34);w=.025
        add('Village','Grass',[(x-w,y,z),(x+w,y,z),(x+.07*math.cos(a),y+.06*math.sin(a),z+h*.66),(x+.1*math.cos(a),y+.1*math.sin(a),z+h)],[(0,1,2),(0,2,3)],'Grass')
    if i%9==0:
        tube('Village','Grass',(x,y,z),(x+.015,y,z+.36),.007,.003,5)
        for k in range(5):
            q=k*math.tau/5
            add('Village','Flower',[(x,y,z+.36),(x+math.cos(q-.5)*.07,y+math.sin(q-.5)*.07,z+.38),(x+math.cos(q+.5)*.07,y+math.sin(q+.5)*.07,z+.38)],[(0,1,2)])

house('Village',-4,7.5,4.6,3.7,4.2)
house('Village',2.0,7.2,5.2,4.0,4.8,True)
house('Village',9.0,8.0,4.6,4.0,4.2)
house('Departure',16.5,7.5,4.9,4.0,4.4,abandoned=True)
house('Departure',22.6,10.5,4.2,3.8,4.0,abandoned=True)
fence('Village',-8,-6,3.9);fence('Village',5.1,6.1,4.9);fence('Village',10.8,13.6,4.9)
fence('Departure',18.2,21.0,4.8)
tube('Village','Rope',(4.9,5.1,2.8),(7.4,5.6,2.65),.014,.014,6)
for i in range(3):cloth(f'Washing{i}',5.35+i*.66,5.15+i*.13,2.76-i*.04,.52,R.uniform(.65,1.1))

for x,y,h in [(-9,8,7.5),(-6,13,8),(6,13,7.2),(12.5,13,7.5),(17,15,7.7),(20.5,17,8.4),(-6,-4.0,7.3),(15.8,-3.5,6.4)]:tree('Village' if x<14 else 'Departure',x,y,h)
for x in [24.5,28.5,32.5,36.5]:
    for y in [5.3,11.0,18.0,26.0]:tree('Woods',x+R.uniform(-1,1),y+R.uniform(-.6,.6),R.uniform(6.8,9.8))
tree('Woods',37.9,-3.8,6.7)
for i in range(210):
    x=R.uniform(23,38);y=R.uniform(2,18);z=height(x,y)
    rock('Woods',(x,y,z),(.10,.09,.07))

# School: broken facade, actual classroom depth, chalkboard, desks and roof rafters.
sx=42;sy=8.8;sz=height(sx,sy)
box('School','Plaster',(sx,sy+2.4,sz+2.2),(7.5,.30,4.4))
box('School','Plaster',(sx-3.6,sy,sz+2.2),(.3,4.8,4.4))
box('School','Plaster',(sx+3.6,sy+1.0,sz+1.3),(.3,2.8,2.6))
box('School','Stone',(sx,sy,sz+.12),(7.7,5.0,.24))
for xx in [-3.4,-1.35,.35,1.95,3.4]:box('School','Plaster',(sx+xx,sy-2.4,sz+1.8),(.38,.38,3.6+R.uniform(-.2,.3)))
box('School','Stone',(sx,sy-2.4,sz+.5),(7.5,.4,1.0))
for xx in [-2.35,1.1,2.65]:window('School',sx+xx,sy-2.63,sz+1.15,1.2,1.75,False,False,True)
for j in range(7):
    xx=sx-3.5+j*1.1
    tube('School','Wood',(xx,sy-2.7,sz+4.0),(xx,sy+.1,sz+5.2),.075,.055)
    if j<4:tube('School','Wood',(xx,sy+.1,sz+5.2),(xx,sy+2.7,sz+4.0),.075,.055)
roof('School',sx,sy,sz+4.0,7.8,5.2,1.25,True)
box('School','Chalkboard',(sx,sy+2.17,sz+1.65),(2.5,.05,1.15))
for j in range(4):
    xx=sx-2.3+(j%2)*2;yy=sy+.5+(j//2)*1.35
    box('School','Wood',(xx,yy,sz+.78),(1.4,.65,.09))
    box('School','Wood',(xx,yy-.55,sz+.43),(1.4,.27,.09))
    for a in [-.56,.56]:
        for b in [-.23,.23]:tube('School','Metal',(xx+a,yy+b,sz+.05),(xx+a,yy+b,sz+.75),.028,.028,5)
for j in range(120):
    xx=R.uniform(38.4,46.5);yy=R.uniform(3.6,7)
    rock('School',(xx,yy,height(xx,yy)),(R.uniform(.08,.3),R.uniform(.08,.24),R.uniform(.08,.25)))

tent(50.8,7.4,3.6,3.3);tent(55.4,10.7,3.8,3.6);tent(57.4,5.7,3.2,3.3)
for xx,yy in [(48.7,3.8),(53.3,4.6),(56.3,4.0)]:
    box('Camp','Wood',(xx,yy,height(xx,yy)+.36),(.75,.66,.72))
    for zz in [.12,.62]:box('Camp','Wood',(xx,yy-.35,height(xx,yy)+zz),(.8,.06,.06))
for xx in [49.1,53.7,58.5]:
    z=height(xx,3.3);tube('Camp','Wood',(xx,3.3,z),(xx+.08,3.3,z+2.15),.055,.04)
for j in range(2):tube('Camp','Rope',(49.1,3.3,1.7+j*.25),(58.5,3.3,1.45+j*.25),.012,.012,5)
cloth('CampHangingCanvas',54,4.1,2.0,1.1,1.25,'Camp')

for args in [(63.4,9.2,5.2,4.9),(69.7,11,5.6,4.2),(75,15,4.8,3.6),(59.7,20,4.9,4.0)]:ruin('Battlefield',*args)
for xx,yy,hh in [(61,3.5,5.1),(65,17,6.2),(72.1,5.8,4.7),(78,20,5.4)]:tree('Battlefield',xx,yy,hh,False)
for xx in [61.0,63.4,65.8]:
    z=height(xx,3.2)
    for side in [-1,1]:tube('Battlefield','Charred',(xx-.45,3.1,z+.1),(xx+side*.65,3.2,z+1.3),.07,.05,6)
for j in range(380):
    xx=R.uniform(59,101);yy=R.uniform(1.3,18)
    rock('Battlefield' if xx<79 else 'Ash',(xx,yy,height(xx,yy)),(R.uniform(.05,.3),R.uniform(.06,.24),R.uniform(.035,.18)))

# Export explicit native payloads and a native assembly recipe.
entries=[]
for name,payload in G.items():
    assert len(payload['vertices'])<=30000 and len(payload['faces'])<=50000,name
    path=OUT/(name+'.json');path.write_text(json.dumps(payload,separators=(',',':')),encoding='utf-8')
    meta=META[name];meta['name']=name;meta['payload']=str(path)
    entries.append(meta)
manifest={'seed':93161016,'units':'meters','authoring':'Original geometry, typed native mesh creation','entries':entries,
 'counts':{'meshes':len(G),'vertices':sum(len(g['vertices']) for g in G.values()),'faces':sum(len(g['faces']) for g in G.values())}}
(OUT/'assembly.json').write_text(json.dumps(manifest,separators=(',',':')),encoding='utf-8')
print(json.dumps(manifest['counts']))
