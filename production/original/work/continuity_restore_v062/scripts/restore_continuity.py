import bpy,json,hashlib,runpy
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/continuity_restore_v062';S=R/'work/trailer_development_v060/native/WTSC_First_Danger_Trailer_Development_v060.blend'
source_sha=hashlib.sha256(S.read_bytes()).hexdigest();assert source_sha=='e0f8f0b6c5434856f7dfe3d8dd5fcdff1586a858f16b8781b94f2b0b12757685'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];bpy.context.window.scene=s
H=runpy.run_path(str(R/'work/production_look_v061/scripts/validate_flat_stage_v061.py'));before=H['snapshot'](s)
root=bpy.data.objects['V047 | shared travel | steady .73125mps'];inverse=[list(v) for v in root.matrix_parent_inverse]
world_before={o.name:{'hidden':o.hide_render,'matrix':[list(v) for v in o.matrix_world],'data':o.data.name if o.data else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in s.objects}
actors=[o for o in root.children_recursive if o.type=='MESH' and not o.hide_render]
copies={};changed=[]
for ob in actors:
 for i,slot in enumerate(ob.material_slots):
  old=slot.material
  if not old or old.surface_render_method!='BLENDED':continue
  if old.as_pointer() not in copies:
   new=old.copy();new.name='V062 | original paint | correct alpha depth | '+old.name;new.surface_render_method='DITHERED';copies[old.as_pointer()]=new
  slot.link='OBJECT';slot.material=copies[old.as_pointer()];changed.append({'object':ob.name,'slot':i,'source':old.name,'copy':slot.material.name})
after=H['snapshot'](s)
checks={k:before[k]==after[k] for k in ['meshes','rig_rest','transforms','actions','drivers','modifiers','materials','images','boots','camera','stage_world_matrix']}
checks['actor_root_inverse_unchanged']=inverse==[list(v) for v in root.matrix_parent_inverse]
world_after={o.name:{'hidden':o.hide_render,'matrix':[list(v) for v in o.matrix_world],'data':o.data.name if o.data else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in s.objects}
checks['world_objects_visibility_transforms_data_materials_exact']=world_before==world_after
checks['no_v061_objects']=not any(o.name.startswith('V061') for o in s.objects)
assert all(checks.values()),checks
s.name='WTSC_PAINTED_CONTINUITY_RESTORED_v062'
s['V062_scope']='Restore exact v060 painted world, palette, camera and paired motion. Only copied actor BLENDED material render method changes to DITHERED for correct DOF alpha depth. No v061 set, shader grade, wash artwork or physical-stage changes.'
note=bpy.data.texts.new('START HERE | V062 | restore visual continuity');note.write(s['V062_scope'])
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
s.frame_set(981);bpy.context.window.scene=s
native=O/'native/WTSC_Painted_Continuity_Restored_v062.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
r={'source_native':str(S),'source_sha256':source_sha,'native':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'checks':checks,'all_checks_pass':all(checks.values()),'only_material_render_mode_changes':changed,'intent':'Visual continuity restoration, not a new art direction. Current character colours pending clarification; sourcev060pair retained exactly.'}
(O/'evidence/RESTORATION_VALIDATION.json').write_text(json.dumps(r,indent=2))
for g in [937,981,1056]:
 s.frame_set(g);s.render.resolution_x=1280;s.render.resolution_y=720;s.render.filepath=str(O/('previews/restored_%04d.png'%g));bpy.ops.render.render(write_still=True,scene=s.name)
print('V062_CONTINUITY_RESTORED_KEYS_READY',flush=True)
