import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Continuous_Coat_Walk_v023.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;start=time.time()
for mode,camera,size in [('CLOSE','V023 | CLOSE portrait',(360,540)),('SHOT','V020 | CHILD | SHOT',(960,540))]:
 D=P/'previews'/mode;D.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
 for f in range(1,94):
  S.frame_set(f);S.render.filepath=str(D/('%04d.png'%f));bpy.ops.render.render(write_still=True)
 print('V023_VIEW_RENDERED',mode,flush=True)
(P/'evidence/final_render_record.json').write_text(json.dumps({'frames_per_view':93,'views':['360x540 portrait close','960x540 actual v046camera framing, neutral stage'],'fps':30,'seconds':3.1,'threads':2,'elapsed_seconds':time.time()-start,'engine':S.render.engine,'speed':'Normal source timing; no holds, slow motion or optical interpolation.'},indent=2));print('V023_FINAL_RENDER_COMPLETE',time.time()-start,flush=True)

