"""Build editable planar replacement drawings in a separate native shot."""
import bpy,sys,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
O=Path(__file__).resolve().parents[1];R=O.parents[1];sys.path.insert(0,str(O/'scripts'))
import pose_spec as M
SRC=R/'work/first_danger_acting_v067/native/WTSC_First_Danger_Acting_v067e.blend'
DEST=O/'native/WTSC_First_Danger_Rough_Acting_v068e.blend'
assert not DEST.exists(),'New candidate path must be unused'
SH=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_FIRST_DANGER_ACTING_WORLD_v067'];S.name='WTSC_FIRST_DANGER_ROUGH_WORLD_v068';bpy.context.window.scene=S
S.frame_set(913);bpy.context.view_layer.update()
ROOT=bpy.data.objects['V047 | shared travel | steady .73125mps'];X0=ROOT.matrix_world.translation.x;Z0=.778
ART={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
RIGS=[bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']]
old=[]
for ob in S.objects:
 if ob.parent in RIGS or ob in RIGS or ob.name.startswith('V060 contact'):
  old.append(ob.name);ob.hide_render=True;ob.hide_viewport=True
COL=bpy.data.collections.new('V068 | ROUGH REPLACEMENT DRAWINGS | on twos | no full-film integration');S.collection.children.link(COL)
CONTROL=bpy.data.objects['V065 | both children | global full-cut color time']
MATS={}
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
for name,hx in M.PALETTE.items():
 rgb=tuple(linear(int(hx[i:i+2],16)/255) for i in [1,3,5])
 mat=bpy.data.materials.new('V068 | rough ink-wash | '+name);mat.use_nodes=True
 N=mat.node_tree.nodes;L=mat.node_tree.links;N.clear()
 out=N.new('ShaderNodeOutputMaterial');out.location=(650,0)
 em=N.new('ShaderNodeEmission');em.location=(440,0);L.new(em.outputs[0],out.inputs[0])
 tex=N.new('ShaderNodeTexCoord');tex.location=(-850,0)
 noise=N.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=155;noise.inputs['Detail'].default_value=2.2;noise.inputs['Roughness'].default_value=.72;L.new(tex.outputs['UV'],noise.inputs['Vector']);noise.location=(-650,0)
 ramp=N.new('ShaderNodeValToRGB');ramp.location=(-430,0)
 for e,k in zip(ramp.color_ramp.elements,[.84,1.13]):e.color=(*[v*k for v in rgb],1)
 L.new(noise.outputs['Fac'],ramp.inputs[0])
 # Keep the original full-cut desaturation clock, evaluated independently for
 # the newly drawn surfaces. No new time remap or color arc is introduced.
 bw=N.new('ShaderNodeRGBToBW');bw.location=(-180,-130);L.new(ramp.outputs['Color'],bw.inputs[0])
 mix=N.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.location=(210,0);L.new(ramp.outputs['Color'],mix.inputs[1]);L.new(bw.outputs[0],mix.inputs[2])
 fc=mix.inputs[0].driver_add('default_value');d=fc.driver;v=d.variables.new();v.name='progress';v.type='SINGLE_PROP';v.targets[0].id=CONTROL;v.targets[0].data_path='["charcoal_progress"]';d.expression='min(1,max(0,progress))'
 L.new(mix.outputs[0],em.inputs['Color']);mat.diffuse_color=(*rgb,1);MATS[name]=mat

def curves(block):
 ad=block.animation_data
 return [f for l in ad.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves] if ad and ad.action else []

NEW=[];ROWS=[]
def make_drawing(w,g):
 d,p=M.draw_actor(w,g);V=[];F=[];MI=[];GROUP=[];matnames=list(MATS);mi={n:i for i,n in enumerate(matnames)}
 for layer,q in enumerate(d.paths):
  pts=q['points'];y=-.385-layer*.00025-(.001 if w=='GIRL' else 0);start=len(V)
  if q['fill']:
   poly=[Vector((x,0,z)) for x,z in pts]
   tris=tessellate_polygon([poly]);lookup={id(v):i for i,v in enumerate(poly)}
   # tessellate_polygon preserves point values, but its wrappers may differ.
   key={tuple(v):i for i,v in enumerate(poly)}
   V.extend((x,y,z) for x,z in pts)
   for tri in tris:F.append(tuple(start+(a if isinstance(a,int) else key[tuple(a)]) for a in tri));MI.append(mi[q['fill']])
  if q['stroke']:
   line=list(pts)+([pts[0]] if q['closed'] else []);off=len(V);n=len(line)
   for i,a in enumerate(line):
    before=line[i-1] if i else (line[-2] if q['closed'] else a)
    after=line[i+1] if i<n-1 else (line[1] if q['closed'] else a)
    tang=M.unit(M.sub(after,before));normal=M.perp(tang)
    for sign in [-1,1]:
     b=M.add(a,M.mul(normal,q['width']*.5*sign));V.append((b[0],y-.00009,b[1]))
   for i in range(n-1):
    a=off+i*2;F.append((a,a+1,a+3,a+2));MI.append(mi[q['stroke']])
  GROUP.append((q['layer'],start,len(V)))
 me=bpy.data.meshes.new(f'V068 {w} | drawing G{g:04d} | flat contour layers');me.from_pydata(V,[],F);me.update()
 for m in MATS.values():me.materials.append(m)
 for poly,m in zip(me.polygons,MI):poly.material_index=m
 uv=me.uv_layers.new(name='Drawing-local wash coordinates')
 for l in me.loops:
  co=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(co.x-p['hip'][0]-p['offset'],co.z)
 ob=bpy.data.objects.new(me.name,me);COL.objects.link(ob);ob.location=(X0,0,Z0)
 for name,a,b in GROUP:
  if b>a:ob.vertex_groups.new(name=name).add(list(range(a,b)),1,'REPLACE')
 for prop in ['hide_render','hide_viewport']:
  for frame,val in [(912,True),(g,False),(min(1081,g+2),True)]:setattr(ob,prop,val);ob.keyframe_insert(prop,frame=frame)
 for fc in curves(ob):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 ob.animation_data.action.name=f'V068 | {w} | drawing exposure G{g}-{min(1080,g+1)}'
 ob['drawing_source']=f'../drawings/{w}_{g:04d}.svg';ob['drawing_frame']=g;ob['character']=w
 ob['method']='New 2D contour drawing from explicit whole-body acting keys. Flat layered mesh faces and ink; no visible volumetric character or old rig deformation.'
 ob['rough_status']='Acting/drawing review. Painted finishing, likeness refinement and clean-up remain provisional.'
 NEW.append(ob.name)
 return p,ob

for g in range(913,1081,2):
 pp={}
 for w in ['BOY','GIRL']:
  p,ob=make_drawing(w,g);pp[w]=p
 ROWS.append({'frame':g,'children':pp})
 if (g-913)%16==0:print('V068_NATIVE_DRAWINGS',g,len(NEW),flush=True)

# Contact ink is part of the rough drawing, with the actual new planted boot
# schedule. A separate flat mesh per drawing is retained as an editable layer.
for row in ROWS:
 g=row['frame'];verts=[];faces=[]
 for w,p in row['children'].items():
  for side in ['far','near']:
   fm=p['feet'][side]
   if not fm['contact']:continue
   x=p['ankle_'+side][0]+p['offset']+.015
   ids=[]
   for i in range(32):
    t=i*math.tau/32;ids.append(len(verts));verts.append((x+.09*math.cos(t),-.31,.0015*math.sin(t)))
   faces.append(tuple(ids))
 if not verts:continue
 me=bpy.data.meshes.new(f'V068 | contact drawing G{g}');me.from_pydata(verts,[],faces);me.materials.append(MATS['contact']);ob=bpy.data.objects.new(me.name,me);COL.objects.link(ob);ob.location=(X0,0,Z0-.001)
 for prop in ['hide_render','hide_viewport']:
  for frame,val in [(912,True),(g,False),(min(1081,g+2),True)]:setattr(ob,prop,val);ob.keyframe_insert(prop,frame=frame)
 for fc in curves(ob):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'

crypto=S.compositing_node_group.nodes.get('V065 | existing children | visible drawing matte')
assert crypto is not None
crypto.matte_id=','.join(NEW)
S.frame_start=913;S.frame_end=1080;S.render.fps=24
S.timeline_markers.clear()
for f,label in M.BEATS:S.timeline_markers.new('V068 | '+label,frame=f)
S['V068_scope']='Seven-second rough acting candidate only. Existing layered environment/camera/audio clock. Do not integrate into full trailer before review.'
S['V068_drawing_method']='84 new exposed drawings per child on twos; explicit new whole-body acting keys, turning head/torso contours and open/search/receiving/grip hand drawings. Native face layers and vertex groups; source SVGs.'
for sc in bpy.data.scenes:
 if sc==S or 'V065' in sc.name or 'v065' in sc.name:
  sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100
  sc.render.threads_mode='FIXED';sc.render.threads=2;sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
  if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=24

report={'source':str(SRC),'source_sha256':SH,'native':str(DEST),'world_scene':S.name,'range':[913,1080],'fps':24,'resolution':[3840,2160],'new_drawings_per_child':84,'new_drawing_objects':NEW,'hidden_original_objects':old,'drawing_registration':{'x':X0,'ground_z':Z0},'rows':ROWS,'artwork_hashes':ART,'rough_status':'New replacement contour drawing pass for acting review. Muted ink/wash color studies; not final painted cleanup or approved likeness.','scope':'No full-trailer sources modified or integrated.'}
assert ART=={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SH
text=bpy.data.texts.new('START HERE | V068 | ROUGH ACTING DRAWINGS');text.write(json.dumps({k:v for k,v in report.items() if k not in ['rows','artwork_hashes','new_drawing_objects']},indent=2))
spec=bpy.data.texts.new('AUTHORING SOURCE | pose_spec.py | V068');spec.write((O/'scripts/pose_spec.py').read_text())
S.frame_set(979);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
report['native_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest();(O/'evidence/BUILD.json').write_text(json.dumps(report,indent=2))
print('V068_NATIVE_SAVED',DEST,len(NEW),flush=True)
