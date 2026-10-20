import bpy,json,hashlib,datetime
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060');P=O/'native/WTSC_First_Danger_Trailer_Development_v060.blend'
H=hashlib.sha256(P.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060'];bpy.context.window.scene=m
D=O/'previews';W=D/'frames_world';T=D/'frames_title';W.mkdir(exist_ok=True);T.mkdir(exist_ok=True)
fo=m.compositing_node_group.nodes['V060 | actual native unmasked world export'];fo.directory=str(W);fo.file_name='world_####';fo.mute=False
for sc in [s,m]:
 sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.dither_intensity=0;sc.eevee.taa_render_samples=32;sc.render.use_sequencer=False;sc.render.use_compositing=True
rows=[]
for f in range(937,1057):
 s.frame_set(f);m.frame_set(f);bpy.context.view_layer.update()
 assert s.frame_current==m.frame_current==f
 m.render.filepath=str(T/f'{f:04d}.png');bpy.ops.render.render(write_still=True,scene=m.name)
 A=W/f'world_{f:04d}Image.png';assert A.exists(),str(A)
 B=W/f'{f:04d}.png';A.replace(B)
 rows.append({'frame':f,'source_character_frame':1+(f-937)*1.25,'world_clock':s.frame_current,'glyph_clock':m.frame_current,'root_x':bpy.data.objects['V047 | shared travel | steady .73125mps'].matrix_world.translation.x,'camera_x':s.camera.matrix_world.translation.x,'world_png_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'title_png_sha256':hashlib.sha256((T/f'{f:04d}.png').read_bytes()).hexdigest()})
 if (f-937)%12==0:
  (O/'evidence/RENDER_PROGRESS.json').write_text(json.dumps({'last_frame':f,'completed':len(rows),'total':120,'native_sha256':H,'synchronized_clocks':True},indent=2))
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
r={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':str(P),'native_sha256':H,'native_unchanged':True,'actual_rendered_frames':120,'frame_range':[937,1056],'fps':24,'resolution':[1280,720],'synchronized_world_and_glyph_clocks':True,'world_is_native_compositor_branch':True,'no_synthetic_overlay':True,'rows':rows}
(O/'evidence/DUAL_SEQUENCE_RENDER.json').write_text(json.dumps(r,indent=2));print('V060_BOTH_NATIVE_SEQUENCES_COMPLETE',flush=True)
# One actual UHD witness, saved separately from the viewing sequence.
Q=O/'previews/native4K';Q.mkdir(exist_ok=True);fo.directory=str(Q)
for sc in [s,m]:sc.render.resolution_x=3840;sc.render.resolution_y=2160
s.frame_set(981);m.frame_set(981);m.render.filepath=str(Q/'Title_0981_4K.png');bpy.ops.render.render(write_still=True,scene=m.name)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
print('V060_UHD_WITNESS_COMPLETE',flush=True)
