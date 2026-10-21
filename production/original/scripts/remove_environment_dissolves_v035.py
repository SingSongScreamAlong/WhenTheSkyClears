import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');target=R/'shots/world/WTSC_World_Spatial_Corrections_v035.blend';assert not target.exists()
s=bpy.data.scenes['WTSC_WORLD_CENTERED_v034'];bpy.context.window.scene=s
before=json.loads((R/'notes/world_v016/fade_audit_before_v035.json').read_text());removed=[]
for row in before['materials_with_animation']:
 m=bpy.data.materials[row['material']];nt=m.node_tree
 # Persistent sets always exist in physical space. Smoke keeps particle age
 # opacity but does not disappear due to a region-wide timeline switch.
 is_set=any('Regional painted sets' in c.name for name in row['users'] for c in s.objects[name].users_collection)
 is_smoke='wisp' in m.name.lower()
 paths=[a['path'] for a in row['animation'] if a['affects_alpha'] and a['driver'] is None and (is_set or is_smoke)]
 if not paths:continue
 for layer in nt.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in list(bag.fcurves):
     if fc.data_path in paths:
      socket=nt.path_resolve(fc.data_path.rsplit('.',1)[0]);bag.fcurves.remove(fc);socket.default_value=1
      removed.append({'material':m.name,'path':fc.data_path if False else paths[0],'scope':'persistent set' if is_set else 'smoke regional gate','preserved':'source cutout alpha and particle-age driver, if present'})
# Remove the old whole-world98–100 picture fade. Typography controls the reveal;
# no new duration or title keys/audio are set while the answer is pending.
nt=s.compositing_node_group
if nt:
 for n in nt.nodes:
  if n.type=='EXPOSURE':
   n.inputs['Exposure'].default_value=0
   try:n.inputs['Exposure'].keyframe_delete('default_value')
   except RuntimeError:pass
   if nt.animation_data:nt.animation_data_clear()
for x in [s,bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v034'],bpy.data.scenes['WTSC_MASTER_4K_103S_v034']]:x.name=x.name.replace('v034','v035')
s['duration_status']='PENDING USER ANSWER:100-second original1:40 versus literal140. Do not export final or retime music/traversal yet.'
s['world_change_v035']='Removed seven persistent regional alpha fades plus15 regional smoke gates; original image alpha and natural particle opacity preserved. Architecture visibility changes only by camera travel.'
note=bpy.data.texts.new('CURRENT v035 | Spatial sets - final duration pending');note.write(json.dumps({'duration_status':s['duration_status'],'removed':removed,'next':'Audit spatial layer coverage and enhance emitter-attached smoke/fire/light; final entire-trailer knockout traversal waits for duration.'},indent=2))
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'source':str(target),'source_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'world_scene':s.name,'removed_alpha_curves':removed,'persistent_materials_corrected':len([r for r in removed if r['scope']=='persistent set']),'smoke_region_gates_removed':len([r for r in removed if r['scope']=='smoke regional gate']),'static_cutout_alpha_preserved':True,'natural_smoke_age_opacity_preserved':True,'whole_world_picture_fade_removed':True,'music_and_final_title_timing_unchanged_pending_answer':True}
(R/'notes/world_v016/spatial_corrections_v035.json').write_text(json.dumps(report,indent=2));print('SPATIAL_SETS_SAVED',json.dumps(report),flush=True)
s.render.resolution_percentage=50;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [193,481,769,1057,1417,1777,2257]:
 s.frame_set(f);s.render.filepath=str(R/f'renders/world_v016/spatial_checks_v035/{f}.png');bpy.ops.render.render(write_still=True,scene=s.name)
