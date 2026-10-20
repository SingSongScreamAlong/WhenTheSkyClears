import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=json.loads((P/'evidence/FOUR_POSE_ANATOMY_AND_SCOPE.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Four_Pose_Silhouette_Rebuild_v029.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;start=time.time()
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100;folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
    for f in R['selected_frames']:S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/RENDER_RECORD.json').write_text(json.dumps({'frames':R['selected_frames'],'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'actual_Blender_renders':8,'threads':2,'elapsed_seconds':time.time()-start,'no_cycle_rendered':True},indent=2));print('V029_EIGHT_POSE_RENDERS_COMPLETE',time.time()-start,flush=True)
