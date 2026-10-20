import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039'];bpy.context.window.scene=w
camp=w.objects['v016 | Camp | pinned canvas and ropes'];nt=camp.data.materials[0].node_tree
for n in nt.nodes:
 if n.type=='VECT_MATH' and n.operation=='NORMALIZE' and not n.inputs[0].is_linked and abs(n.inputs[0].default_value[0]-.35)<.001:n.inputs[0].default_value[0]=-.35
for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
 nt=w.objects[name].data.materials[0].node_tree;noise=next(n for n in nt.nodes if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-.42)<.001);maps=[n for n in nt.nodes if n.type=='MAP_RANGE' and n.inputs['Value'].is_linked and n.inputs['Value'].links[0].from_node==noise]
 target=next(n for n in nt.nodes if n.name.startswith('v039 restrained foreground value'))
 if maps:nt.links.new(maps[0].outputs[0],target.inputs[7]);target.inputs[0].default_value=.65
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');samples=[]
for f in [1537,1609,1656]:
 w.frame_set(f);bpy.context.view_layer.update();p=[world_to_camera_view(w,w.camera,pair.matrix_world@v.vector) for v in pair.data.layers[0].frames[0].drawing.attributes['position'].data];c=[(min(v.x for v in p)+max(v.x for v in p))/2,(min(v.y for v in p)+max(v.y for v in p))/2];assert all(abs(x-.5)<1e-5 for x in c);samples.append({'frame':f,'pair_center':c})
bad=[]
for mat in bpy.data.materials:
 if mat.name.startswith('v039') and mat.node_tree and mat.node_tree.animation_data:
  for d in mat.node_tree.animation_data.drivers:
   if not d.is_valid:bad.append({'material':mat.name,'path':d.data_path,'expression':d.driver.expression})
for ob in w.objects:
 if ob.parent and 'Camp hearth | fixed emitter' in ob.parent.name and hasattr(ob.data,'materials'):
  for mat in ob.data.materials:
   if mat.node_tree and mat.node_tree.animation_data:
    for d in mat.node_tree.animation_data.drivers:
     if not d.is_valid:bad.append({'material':mat.name,'path':d.data_path,'expression':d.driver.expression})
assert not bad,bad
assert not any('FX0' in c.name and 'v001' in c.name for c in w.collection.children)
e.frame_set(1609);w.frame_set(1609);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'benchmark_frames':[1537,1656],'samples':samples,'invalid_benchmark_drivers':bad,'key_direction':'Upper camera-left, consistent with existing motivated area source','v001_pack_imports':False,'character_geometry_or_pose_change':False,'render_status':'No substantive benchmark render started;037production preserved.'}
(R/'notes/world_v016/camp_benchmark_native_v039.json').write_text(json.dumps(report,indent=2));print('BENCHMARK_NATIVE_SETUP_CHECKED',json.dumps(report),flush=True)
