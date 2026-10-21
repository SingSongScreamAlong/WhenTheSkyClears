"""Read-only world witness: append static age-ten assets in RAM; never save world."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];WORLD=ROOT/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend';ASSET=P/'native/WTSC_Age10_Static_Proportion_Candidate_v044.blend';before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [WORLD,ASSET]};bpy.ops.wm.open_mainfile(filepath=str(WORLD),load_ui=False,use_scripts=False);S=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];bpy.context.window.scene=S;oldpair=S.objects['v016 | CHILDREN | held painterly near-age pair'];oldobjects=[oldpair,*oldpair.children_recursive]
with bpy.data.libraries.load(str(ASSET),link=False) as (src,dst):dst.collections=['V044 | age10 editable profile anatomy']
C=dst.collections[0];S.collection.children.link(C);rigs={o.name.split()[1]:o for o in C.objects if o.type=='ARMATURE'};assert set(rigs)=={'BOY','GIRL'}
S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.eevee.taa_render_samples=32
M=bpy.data.materials.new('AUDIT ONLY | same plane calibration ink');M.use_nodes=True;ns=M.node_tree.nodes;ns.clear();em=ns.new('ShaderNodeEmission');em.inputs[0].default_value=(.15,.19,.18,1);out=ns.new('ShaderNodeOutputMaterial');M.node_tree.links.new(em.outputs[0],out.inputs[0])
mc=bpy.data.collections.new('AUDIT ONLY |2m same-depth calibration');S.collection.children.link(mc)
def line(n,verts):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],[(0,1,2,3)]);me.materials.append(M);ob=bpy.data.objects.new(n,me);mc.objects.link(ob);return ob
bar=line('AUDIT ONLY |2.00m calibrated vertical',[(-.003,0,0),(.003,0,0),(.003,0,2),(-.003,0,2)])
top=line('AUDIT ONLY | calibrator top',[(-.08,0,1.997),(.08,0,1.997),(.08,0,2.003),(-.08,0,2.003)])
cu=bpy.data.curves.new('AUDIT ONLY label','FONT');cu.body='2.00 m\nsame-depth guide';cu.size=.045;cu.materials.append(M);label=bpy.data.objects.new('AUDIT ONLY label',cu);mc.objects.link(label);label.rotation_euler=(math.pi/2,0,0)
rows=[]
for f in [241,1201]:
 S.frame_set(f);bpy.context.view_layer.update();base=oldpair.matrix_world.translation.copy();base.y=-.36
 for who,r in rigs.items():r.location=(base.x+(-.4 if who=='BOY' else .4),base.y,base.z)
 for o in [bar,top]:o.location=(base.x-1.15,base.y-.12,base.z)
 label.location=(base.x-1.27,base.y-.13,base.z+2.04)
 for o in C.objects:o.hide_render=True
 for o in oldobjects:o.hide_render=False
 S.render.filepath=str(P/'previews'/f'WORLD_BEFORE_{f:04d}_1280.png');bpy.ops.render.render(write_still=True,scene=S.name)
 for o in C.objects:o.hide_render=False
 for o in oldobjects:o.hide_render=True
 S.render.filepath=str(P/'previews'/f'WORLD_AGE10_STATIC_{f:04d}_1280.png');bpy.ops.render.render(write_still=True,scene=S.name)
 rows.append({'frame':f,'world_camera':S.camera.name,'camera_matrix':[list(r) for r in S.camera.matrix_world],'source_held_pair_base':list(oldpair.matrix_world.translation),'candidate_root_positions':{w:list(r.location) for w,r in rigs.items()},'same_depth_calibration_height_m':2.0,'candidate_is_neutral_static_not_integrated_motion':True})
unchanged={p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()};assert all(unchanged.values());(P/'evidence/WORLD_STATIC_SCALE_WITNESS.json').write_text(json.dumps({'sources_before_sha256':before,'source_hashes_unchanged':unchanged,'world_saved':False,'new_light_added':False,'source_lights_camera_world_art_changed':False,'caveat':'Read-only neutral placement witness. New character material painting is unbound to parent world light response; no animation/hand contacts or production integration acceptance claimed. Background painted doors are at different depth from this calibration bar.','samples':rows},indent=2));print('WORLD_STATIC_WITNESS_COMPLETE_NO_SAVE',flush=True)
