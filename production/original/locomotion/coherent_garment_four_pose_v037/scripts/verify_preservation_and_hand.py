import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=[1,4,11,20,27]
def ah(a):return hashlib.sha256(repr([(fc.data_path,fc.array_index,fc.extrapolation,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points],[(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None)) for m in fc.modifiers]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
def mh(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[[tuple(p.co) for p in k.data] for k in m.shape_keys.key_blocks] if m.shape_keys else [],[tuple(v.uv) for v in m.uv_layers.active.data] if m.uv_layers.active else [])).encode()).hexdigest()
def load(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);S=bpy.context.scene;return S,bpy.data.objects['LOCO_BOY | RIG'],S.view_layers['V025 | original foreground']
def pts(o,vl):vl.update();e=o.evaluated_get(vl.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
S,rig,fore=load(P/'reference/PRESERVED_v036.blend');actions={a.name:ah(a) for a in bpy.data.actions};meshes={m.name:mh(m) for m in bpy.data.meshes};images={i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file};fg={o.name for o in bpy.data.collections['V025 | retained foreground identity'].all_objects};names=[o.name for o in S.objects if o.type=='MESH' and not o.hide_render and ('BOY' in o.name or 'V024 continuous' in o.name or 'V033 |' in o.name)];cache={};motion={}
for f in range(1,95):
 S.frame_set(f);bpy.context.view_layer.update();motion[f]={'bones':{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones},'root':rig.parent.matrix_world.copy(),'wrists':{s:bpy.data.objects['BOY | WRIST_'+s].matrix_world.copy() for s in ['near','far']}}
 if f in F:
  fore.update();cache[f]={'meshes':{n:pts(bpy.data.objects[n],fore if n in fg else bpy.context.view_layer) for n in names},'cameras':{n:bpy.data.objects[n].matrix_world.copy() for n in ['V024 | CLOSE portrait','V020 | CHILD | SHOT']}}
S,rig,fore=load(P/'native/WTSC_Connected_Garment_Retained_Fabric_v037.blend');errors={'all_bone_world_matrices':0.,'root_matrix':0.,'wrist_world_matrices':0.,'original_visible_mesh_vertices_m':0.,'camera_world_matrices':0.}
def me(A,B):return max(abs(A[a][b]-B[a][b]) for a in range(4) for b in range(4))
for f in range(1,95):
 S.frame_set(f);bpy.context.view_layer.update();r=motion[f];errors['root_matrix']=max(errors['root_matrix'],me(rig.parent.matrix_world,r['root']))
 for b in rig.pose.bones:errors['all_bone_world_matrices']=max(errors['all_bone_world_matrices'],me(rig.matrix_world@b.matrix,r['bones'][b.name]))
 for s in ['near','far']:errors['wrist_world_matrices']=max(errors['wrist_world_matrices'],me(bpy.data.objects['BOY | WRIST_'+s].matrix_world,r['wrists'][s]))
 if f in F:
  fore.update();r=cache[f]
  for n,V in r['meshes'].items():errors['original_visible_mesh_vertices_m']=max(errors['original_visible_mesh_vertices_m'],max((a-b).length for a,b in zip(pts(bpy.data.objects[n],fore if n in fg else bpy.context.view_layer),V)))
  for n,M in r['cameras'].items():errors['camera_world_matrices']=max(errors['camera_world_matrices'],me(bpy.data.objects[n].matrix_world,M))
changedactions=[n for n,h in actions.items() if ah(bpy.data.actions[n])!=h];changedmeshes=[n for n,h in meshes.items() if mh(bpy.data.meshes[n])!=h];changedimages=[n for n,h in images.items() if hashlib.sha256(bytes(bpy.data.images[n].packed_file.data)).hexdigest()!=h];report={'scope':'Cold native technical preservation, not artistic acceptance','original_actions_changed':changedactions,'original_mesh_coordinate_shape_UV_data_changed':changedmeshes,'original_packed_image_bytes_changed':changedimages,'all_original_bone_root_wrist_checks_integer_frames':[1,94],'protected_mesh_camera_frames':F,'protected_visible_mesh_names':names,'errors':errors,'static_garment_pose_scope':'Only new coat has five constant held shape samples. No garment animation or inbetweens have been authored.','blender_version':bpy.app.version_string,'images_packed':all(bool(i.packed_file) for i in bpy.data.images if i.type=='IMAGE')};(P/'evidence/COLD_PRESERVATION_AND_SCOPE.json').write_text(json.dumps(report,indent=2));assert not(changedactions or changedmeshes or changedimages) and max(errors.values())<2e-5
S.frame_set(27);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;o=bpy.data.objects['V007_BOY | articulated drawn hand near'];m=bpy.data.materials.new('V037 diagnostic hand ID');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.9,.01,.3,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs[0]);o.material_slots[0].link='OBJECT';o.material_slots[0].material=m;folder=P/'previews/F27_ID';folder.mkdir(exist_ok=True)
for mode in ['FULL','ISOLATED']:
 if mode=='ISOLATED':
  for q in S.objects:
   if q.type in ['MESH','GREASEPENCIL','CURVE'] and q!=o:q.hide_render=True
 S.render.filepath=str(folder/(mode+'.png'));bpy.ops.render.render(write_still=True)
print('V037_COLD_PRESERVATION_COMPLETE',json.dumps({'errors':errors,'changed_actions':changedactions,'changed_original_meshes':changedmeshes,'changed_original_paint':changedimages}),flush=True)
