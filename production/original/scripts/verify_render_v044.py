"""Fresh-open verification, then an actual native probe or120frame4K export."""
import bpy,json,hashlib,sys
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');report=json.loads((R/'notes/world_v016/motion_trial_build_v044.json').read_text());p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()==report['source_sha256']
s=bpy.data.scenes[report['world_scene']];m=bpy.data.scenes[report['master_scene']];bpy.context.window.scene=s
assert s.render.engine==report['engine']=='BLENDER_EEVEE'
for scene in [s,m]:assert (scene.frame_start,scene.frame_end,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps)==(1801,1920,3840,2160,100,24)
new=next(o for o in s.objects if o.get('motion_revision')=='v006_drawn_pose_corrections');old=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');travel=next(o for o in new.children if 'TRAVEL' in o.name);oldtravel=next(o for o in old.children if 'TRAVEL' in o.name)
assert all(o.hide_render for o in old.children_recursive);caps=[o for o in s.objects if o.name.startswith(('v043 rounded knee |','v043 rounded wrist |'))];assert len(caps)==6 and all(o.hide_render for o in caps)
contacts=[o for o in s.objects if o.name.startswith('v041 sole contact |')];assert len(contacts)==4 and all(not o.hide_render and o.get('v044_new_boot_reference') in s.objects for o in contacts)
fx=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];event=s.objects['v041 | Live event binding | awaiting verified FX'];frozen=json.loads((R/'notes/world_v016/frozen_staging_v043.json').read_text());error=0
for row in frozen['samples']:
 s.frame_set(row['frame']);bpy.context.view_layer.update();error=max(error,max(abs(s.camera.matrix_world[i][j]-row['camera_matrix'][i][j]) for i in range(4) for j in range(4)),(travel.matrix_world.translation-oldtravel.matrix_world.translation).length,abs(light.data.energy-row['physical_light_watts']),abs(fx['age']-row['fx_age']),abs(fx['hot_envelope']-row['hot_envelope']),abs(event['power_watts']-row['receiver_watts']))
assert error<1e-6,error
for key,value in frozen['camera_data'].items():assert getattr(s.camera.data,key)==value,(key,getattr(s.camera.data,key),value)
for key,value in frozen['fx_controls'].items():assert fx[key]==value
picture=next(x for x in m.sequence_editor.strips if x.type=='SCENE');sound=next(x for x in m.sequence_editor.strips if x.type=='SOUND');assert picture.scene==s and picture.frame_final_duration==120 and sound.frame_final_start==1801 and sound.frame_final_end==1921 and sound.sound.packed_file
assert not any(n.bl_idname=='CompositorNodeImage' for n in s.compositing_node_group.nodes)
reopen={'source':str(p),'source_sha256':report['source_sha256'],'fresh_open_verified':True,'frozen_staging_max_error':error,'original_engine':s.render.engine,'frame_count':120,'fps':24,'resolution':[3840,2160],'native_scene_strip':s.name,'audio_native_packed_original_range':[75,80],'single_new_pair_visible':True,'all6_old_caps_hidden':True,'four_existing_contacts_retained':True,'new_motion_clock':[1801,1920],'old_retime_applied':False,'render_status':'Native verification complete; rendering pending.'}
(R/'notes/world_v016/fresh_open_v044.json').write_text(json.dumps(reopen,indent=2));print('V044_COLD_REOPEN_VERIFIED',json.dumps(reopen),flush=True)
bpy.context.window.scene=m
if '--probe' in sys.argv:
 m.render.image_settings.media_type='IMAGE';m.render.image_settings.file_format='PNG';m.frame_set(1837);m.render.filepath=str(R/'renders/world_v016/integration_v044/Native_Probe_1837_4K.png');bpy.ops.render.render(write_still=True,scene=m.name);print('V044_ACTUAL_4K_PROBE_COMPLETED',flush=True)
else:
 output=R/'renders/world_v016/integration_v044/WTSC_Drawn_Open_75_80_4K_v044.mp4';assert not output.exists();m.render.filepath=str(output)
 assert m.render.image_settings.media_type=='VIDEO' and m.render.ffmpeg.codec=='H264' and m.render.ffmpeg.audio_codec=='AAC'
 print('V044_NATIVE_120F_EXPORT_STARTED',str(output),flush=True);bpy.ops.render.render(animation=True,scene=m.name);assert output.exists();print('V044_NATIVE_120F_EXPORT_COMPLETED',str(output),flush=True)
assert hashlib.sha256(p.read_bytes()).hexdigest()==report['source_sha256']
