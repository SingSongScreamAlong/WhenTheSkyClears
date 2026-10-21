"""Shared full-picture color arc on the restored layered 2D cast."""
import bpy,json,hashlib,runpy,math
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/color_arc_v063';S=R/'work/continuity_restore_v062/native/WTSC_Painted_Continuity_Restored_v062.blend';F=R/'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend'
assert hashlib.sha256(S.read_bytes()).hexdigest()=='bc6036961f0b557fcf9e33dd04f3a2b8118dc2726534cf0d6016cc0ca3ad3514'
assert hashlib.sha256(F.read_bytes()).hexdigest()=='1721ae5ce9146e9d0379419d153c64ef09a122074a972a8e4bd68fb1953d176e'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_PAINTED_CONTINUITY_RESTORED_v062'];bpy.context.window.scene=s;s.frame_set(981)
H=runpy.run_path(str(R/'work/production_look_v061/scripts/validate_flat_stage_v061.py'));before=H['snapshot'](s)
root=bpy.data.objects['V047 | shared travel | steady .73125mps'];old_inverse=[list(v) for v in root.matrix_parent_inverse]
existing={o.name:{'hide':o.hide_render,'matrix':[list(v) for v in o.matrix_world],'data':o.data.name if o.data else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in s.objects}
names=['V050 GIRL | registered face paint, original hair braid and alpha','V050 GIRL | original painted skin in matching skin finish','V050 GIRL | original painted hand in matching skin finish']
with bpy.data.libraries.load(str(F),link=False) as (a,b):b.materials=names
mats=dict(zip(['head','skin','hand'],b.materials));assert all(mats.values())
actors=[o for o in root.children_recursive if o.type=='MESH']
assignments=[];changed=[]
for ob in actors:
 if 'GIRL' not in ob.name:continue
 kind='head' if ob.name=='V044 GIRL | head' else ob.get('wardrobe_role')
 if kind not in mats:continue
 mat=mats[kind]
 for node in mat.node_tree.nodes:
  if node.type=='UVMAP':assert node.uv_map in ob.data.uv_layers,(ob.name,node.uv_map)
 for slot in ob.material_slots:slot.link='OBJECT';slot.material=mat
 assignments.append({'object':ob.name,'kind':kind,'material':mat.name});changed.append(ob)
# Preserve the already-authored localized flash/settle on the imported girl paint.
# This temporary material-authoring scene contains no world receivers.
tmp=bpy.data.scenes.new('V063 temporary material authoring')
for ob in changed:tmp.collection.objects.link(ob)
event=bpy.data.objects['V060 | one offscreen distant flash | painted response']
light_report=runpy.run_path(str(R/'work/trailer_development_v060/scripts/add_painted_light.py'))['apply'](tmp,changed,event,prefix='V063')
bpy.data.scenes.remove(tmp)
arc=runpy.run_path(str(O/'scripts/add_color_arc.py'))['apply'](s,actors)
after=H['snapshot'](s)
checks={k:before[k]==after[k] for k in ['meshes','rig_rest','transforms','actions','drivers','modifiers','materials','boots','camera','stage_world_matrix']}
checks['original_source_images_unchanged']=all(after['images'].get(k)==v for k,v in before['images'].items())
checks['root_inverse_unchanged']=old_inverse==[list(v) for v in root.matrix_parent_inverse]
now={name:{'hide':s.objects[name].hide_render,'matrix':[list(v) for v in s.objects[name].matrix_world],'data':s.objects[name].data.name if s.objects[name].data else None,'materials':[m.name if m else None for m in s.objects[name].data.materials] if s.objects[name].type=='MESH' else []} for name in existing}
checks['established_world_objects_camera_visibility_material_data_exact']=now==existing
checks['no_v061_set_objects']=not any(o.name.startswith('V061') for o in s.objects)
assert all(checks.values()),checks
s.name='WTSC_SHARED_COLOR_TO_CHARCOAL_v063'
s['V063_scope']='Restored layered2D first-danger shot with shared global0-100s color arc for BOTH children. Latest matching girl face/skin material fromv050. No set/camera/body shape/UV/motion changes. Current movie integration remains39-44s; matched palette witness holds pose and scene atG981.'
s['V063_full_cut_limit']='The existing full v040 movie is preserved, not silently replaced or declared conformed.'
note=bpy.data.texts.new('START HERE | V063 | both children color to charcoal');note.write(s['V063_scope']+'\n'+s['V063_full_cut_limit']+'\n'+json.dumps(arc,indent=2,default=str))
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s,'eevee'):s.eevee.taa_render_samples=64
s.frame_set(981);bpy.context.window.scene=s
bpy.ops.file.pack_all();native=O/'native/WTSC_Shared_Color_To_Charcoal_v063.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'source_v062':str(S),'source_v050':str(F),'native':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'checks':checks,'all_checks_pass':all(checks.values()),'girl_color_source_assignments':assignments,'local_paint_response':light_report,'arc':arc,'dark_costume_note':'Original dark dress/hair/stockings retained as costume colors. Full-color opening restores authored exposed-skin pigment; no invented bright outfit recolor.','full_cut_status':s['V063_full_cut_limit']}
(O/'evidence/COLOR_ARC_BUILD.json').write_text(json.dumps(report,indent=2,default=str))
for g in [937,981,1056]:
 s.frame_set(g);s.render.resolution_x=1280;s.render.resolution_y=720;s.render.filepath=str(O/('previews/actual_first_danger_%04d.png'%g));bpy.ops.render.render(write_still=True,scene=s.name)
print('V063_SHARED_COLOR_ARC_NATIVE_READY',flush=True)
