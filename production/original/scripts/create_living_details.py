"""Create original dimensional dressing and continuous tapered tree curves."""
import json,subprocess,math,random
from pathlib import Path
from collections import defaultdict
import generate_living_world_geometry as K
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/living_world_details';OUT.mkdir(exist_ok=True)
CLI=r'WTSC_LOCAL_USER\AppData\Local\dcc-mcp\bin\dcc-mcp-cli.exe'
receipts=ROOT/'notes/living_world/typed_details_v009.jsonl'
assert not receipts.exists(),'Inspect native state and receipts before any replay'
def call(kind,args):
    path=OUT/(args['name']+'.json');path.write_text(json.dumps(args,separators=(',',':')))
    p=subprocess.run([CLI,'call',kind,'--json-file',str(path),'--gateway','local','--transport','mcp','--output','json'],capture_output=True,text=True)
    r=json.loads(p.stdout);native=r.get('result',{}).get('structuredContent',{})
    with receipts.open('a',encoding='utf-8') as f:f.write(json.dumps({'tool':kind,'name':args['name'],'request_id':r.get('request_id'),'result':native})+'\n')
    assert p.returncode==0 and r.get('success') and native.get('success'),(args['name'],r)
curves=json.loads((ROOT/'work/living_world_meshes/v008/branch_curves.json').read_text())
for region,entry in curves.items():
    call('blender.dda6f921.blender_data_geometry__create_curve_from_points',{'name':'LWC_'+region+'_OrganicTrees','splines':entry['splines'],'closed':False,'dimensions':'3D','bevel_depth':.35,'bevel_resolution':2})
    print('Native continuous branch curves',region,len(entry['splines']),flush=True)

K.G={};K.META={};K.COUNTS=defaultdict(int);K.R=random.Random(9316)
def wheel(x,y,z,r=.49):
    for j in range(28):
        a=j*math.tau/28;b=(j+1)*math.tau/28
        K.tube('VillageProps','Wood',(x+r*math.cos(a),y,z+r*math.sin(a)),(x+r*math.cos(b),y,z+r*math.sin(b)),.035,.035,7)
    for j in range(12):
        a=j*math.tau/12;K.tube('VillageProps','Wood',(x,y,z),(x+(r-.04)*math.cos(a),y,z+(r-.04)*math.sin(a)),.017,.017,6)
    K.tube('VillageProps','Metal',(x,y-.09,z),(x,y+.09,z),.07,.07,10)
def barrel(x,y,z,r=.30,h=.75):
    verts=[];faces=[];n=16;m=8
    for j in range(m+1):
        q=j/m;rr=r*(.84+.16*math.sin(q*math.pi))
        for k in range(n):
            a=k*math.tau/n;verts.append((x+rr*math.cos(a),y+rr*math.sin(a),z+q*h))
    for j in range(m):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
    faces.append(tuple(range(m*n,(m+1)*n)));K.add('VillageProps','Wood',verts,faces)
    for zz in [.16,.60]:
        rr=r*(.84+.16*math.sin(zz/h*math.pi))+.008
        for k in range(n):
            a=k*math.tau/n;b=(k+1)*math.tau/n
            K.tube('VillageProps','Metal',(x+rr*math.cos(a),y+rr*math.sin(a),z+zz),(x+rr*math.cos(b),y+rr*math.sin(b),z+zz),.018,.018,6)
wheel(-4.75,5.1,.60);wheel(-4.75,6.45,.60)
K.box('VillageProps','Wood',(-4.75,5.8,.88),(1.8,1.18,.15))
for a in [-1,1]:K.box('VillageProps','Wood',(-4.75+a*.89,5.8,1.08),(.10,1.2,.42))
for a in [-1,1]:K.tube('VillageProps','Wood',(-4.75,5.8+a*.40,.80),(-2.75,5.8+a*.40,.43),.045,.035)
barrel(.35,5.0,K.height(.35,5));barrel(4.4,5.6,K.height(4.4,5.6),.25,.65)

# A bell over the damaged classroom distinguishes the school from a house.
x=41.6;y=6.05;z=K.height(42,8.8)
K.box('SchoolProps','Stone',(x,y,z+4.45),(1.2,.5,.24))
for side in [-1,1]:K.box('SchoolProps','Stone',(x+side*.45,y,z+5.02),(.20,.40,1.0))
K.arch('SchoolProps','Stone',x,y-.03,z+4.52,.7,1.18,.38)
verts=[];faces=[];n=20
for j,(rr,zz) in enumerate([(.23,4.79),(.20,4.84),(.15,5.01),(.11,5.17),(.06,5.25)]):
    for k in range(n):a=k*math.tau/n;verts.append((x+rr*math.cos(a),y+rr*math.sin(a),z+zz))
for j in range(4):
    for k in range(n):a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
K.add('SchoolProps','Bronze',verts,faces)
K.tube('SchoolProps','Metal',(x,y,z+4.78),(x,y,z+5.4),.02,.02,6)
# Faint nonverbal chalk traces on the back wall board.
for j in range(5):
    zz=z+1.4+j*.13
    K.tube('SchoolProps','Chalk',(40.95,10.93,zz),(42.6-(j%2)*.2,10.93,zz+.025),.008,.008,5)

# Bedrolls and simple camp seating give the shelters a human scale.
for xx,yy in [(50.6,7.4),(55.3,10.6),(57.4,5.8)]:
    K.tube('CampProps','TentCanvas',(xx-.5,yy+.3,K.height(xx,yy)+.15),(xx+.5,yy+.3,K.height(xx,yy)+.15),.14,.14,12)
    K.box('CampProps','Wood',(xx-.9,yy-1.5,K.height(xx,yy)+.25),(.65,.4,.12))

# Small original bird meshes. Wings will receive native shape keys.
for j in range(4):
    region='Bird'+str(j)
    K.add(region,'Bird',[(-.16,0,0),(0,-.055,.015),(.16,0,0),(0,.055,.015),(0,0,-.045),(-.26,0,.10),(0,0,0),(.26,0,.10)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,1),(1,3,2),(0,5,6),(6,7,2)])
details=[]
for name,payload in K.G.items():
    call('blender.dda6f921.blender_data_geometry__create_mesh_from_data',payload)
    meta=K.META[name];meta['name']=name;details.append(meta)

wire=[]
for j in range(241):
    t=j/240;a=t*math.tau*14
    wire.append((61+t*8,2.8+.27*math.cos(a),.60+.27*math.sin(a)))
call('blender.dda6f921.blender_data_geometry__create_curve_from_points',{'name':'LWC_BarbedWire_Coil','splines':[wire],'closed':False,'dimensions':'3D','bevel_depth':.008,'bevel_resolution':1})
(OUT/'details_recipe.json').write_text(json.dumps({'mesh_entries':details,'tree_curves':curves},separators=(',',':')))
print(json.dumps({'detail_meshes':len(details),'tree_curve_regions':len(curves),'wire_points':len(wire)}),flush=True)
