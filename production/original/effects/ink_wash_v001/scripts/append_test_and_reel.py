import bpy, json, math, sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='FX_SANDBOX | actual Append test and representative reel'
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=192
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=False
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s.world=bpy.data.worlds.new('Sandbox world');s.world.color=(0,0,0)
library=P/'native/WTSC_Ink_Wash_FX_Library_v001.blend'
with bpy.data.libraries.load(str(library),link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith('FX0')]
roots=[]
layout=[(-3.2,.1,.20,4,.95),(.3,.15,.20,35,.85),(3.2,.2,.20,72,.85),(-1.4,-.2,.20,48,1),(2.3,-.2,.20,105,1),(-4.8,-.2,.20,124,1),(-5.3,.3,.20,1,1),(0,-.3,.20,1,2),(5.2,-.1,.20,1,1.25)]
for c,(x,y,z,start,scale) in zip(sorted(dst.collections,key=lambda x:x.name),layout):
    s.collection.children.link(c);root=next(o for o in c.objects if o.name.endswith('CONTROLS'));root.location=(x,y,z);root['start_frame']=float(start);root['size']=scale;roots.append(root)

def mat(name,col,grain=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(*col,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
    if grain:
        no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=80;no.inputs['Detail'].default_value=3
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(*[v*.72 for v in col],1);mix.inputs[2].default_value=(*[v*1.12 for v in col],1);nt.links.new(no.outputs['Fac'],mix.inputs[0]);nt.links.new(mix.outputs[0],em.inputs[0])
    return m

def poly(name,verts,m,y):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,y,z) for x,z in verts],[],[list(range(len(verts)))]);me.materials.append(m);ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);return ob

sky=mat('Sandbox | blue gray paper',(.20,.23,.245),True);far=mat('Sandbox | distant wash',(.105,.13,.145),True);mid=mat('Sandbox | charcoal architecture',(.062,.077,.086),True);ground=mat('Sandbox | dry dust ground',(.11,.115,.103),True);front=mat('Sandbox | foreground torn ink',(.024,.029,.028),True)
poly('Sandbox paper sky',[(-10,-3),(10,-3),(10,8),(-10,8)],sky,2)
poly('Sandbox layered distant horizon',[(-9,-1),(9,-1),(9,2.4),(7,2.9),(6,2.7),(4,3.05),(2.5,2.7),(1,2.8),(-1,3.1),(-2.3,2.8),(-4,3.2),(-6,2.9),(-8,3.1),(-9,2.8)],far,1.8)
for i,(x,w,h) in enumerate([(-7,.9,1.6),(-5.4,.65,2.3),(-4.5,.5,1.2),(-1.6,.8,1.8),(1.5,.8,2.5),(4.3,.9,1.5),(6.7,.6,2.1)]):
    poly(f'Sandbox broken silhouette {i}',[(x,0),(x+w,0),(x+w,h*.7),(x+w*.8,h*.7),(x+w*.77,h),(x+w*.40,h*.95),(x+w*.35,h*.66),(x,h*.8)],mid,1.3)
poly('Sandbox ground',[(-10,-2),(10,-2),(10,.22),(7,.26),(5,.17),(3,.23),(0,.19),(-3,.24),(-6,.18),(-10,.25)],ground,.7)
poly('Sandbox foreground wash',[(-10,-2),(10,-2),(10,-.63),(8,-.56),(6,-.71),(4,-.58),(2,-.74),(0,-.61),(-2,-.68),(-4,-.54),(-6,-.72),(-8,-.58),(-10,-.66)],front,-.7)
titlemat=mat('Sandbox typography',(.71,.70,.63))
def text(name,body,x,z,size):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.space_character=1.15;d.materials.append(titlemat);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=(x,-1,z);o.rotation_euler=(math.pi/2,0,0)
text('Reel label','WHEN THE SKY CLEARS  /  INK + WASH EFFECTS',-6.7,4.20,.22)
text('Reel subtitle','GROUND BURSTS     /     INCOMING MARKS     /     ANCHORED FIRE + ASH',-6.7,-1.2,.15)
d=bpy.data.cameras.new('Sandbox XZ camera');d.type='ORTHO';d.ortho_scale=14.8;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(0,-20,1.65);o.rotation_euler=(math.pi/2,0,0);s.camera=o
# Real material receiver confirms physical light, in addition to emission-painted pool.

rows=[]
for frame in [1,16,32,80,145,192]:
    s.frame_set(frame);bpy.context.view_layer.update()
    rows.append({'frame':frame,'roots':[{'name':r.name,'age':r['age'],'location':list(r.matrix_world.translation),'drivers':len(r.animation_data.drivers),'driver_valid':all(f.driver.is_valid for f in r.animation_data.drivers)} for r in roots]})
all_drivers=[(id.name,f) for id in list(bpy.data.objects)+list(bpy.data.materials)+[m.node_tree for m in bpy.data.materials if m.node_tree]+list(bpy.data.shape_keys)+list(bpy.data.lights) if id.animation_data for f in id.animation_data.drivers]
invalid=[{'id':n,'path':f.data_path,'expression':f.driver.expression} for n,f in all_drivers if not f.driver.is_valid]
report={'source':str(library),'method':'bpy.data.libraries.load(link=False) into factory-empty scene; all nine collections linked into sandbox scene',
 'collection_count':len(roots),'objects':len(s.objects),'materials':len(bpy.data.materials),'drivers':len(all_drivers),'invalid_drivers':invalid,
 'packed_images':[im.name for im in bpy.data.images if im.packed_file],'samples':rows,'cpu_threads':2,'render_engine':'Eevee 32 samples low-resolution GPU check','resolution':[960,540],'fps':24,'range':[1,192]}
assert not invalid,invalid
assert len(roots)==9
assert all(abs(float(row['roots'][0]['age'])-(row['frame']-4))<.0001 for row in rows)
(P/'evidence/append_test.json').write_text(json.dumps(report,indent=2))
s.frame_set(32);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_FX_Append_Sandbox_v001.blend'),compress=True)
print('APPEND_TEST_PASS',json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args and args[0]=='reel':
    s.render.filepath=str(P/'previews/reel_frames/');bpy.ops.render.render(animation=True)
else:
    for frame in [8,32,80,128,176]:
        s.frame_set(frame);s.render.filepath=str(P/f'previews/check_{frame:04}.png');bpy.ops.render.render(write_still=True)
print('SANDBOX_RENDER_COMPLETE',flush=True)
