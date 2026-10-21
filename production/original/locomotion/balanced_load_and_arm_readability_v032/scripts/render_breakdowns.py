import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Rough_Construction_v032.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;t=time.time();record={}
for mode,camera,size,frames in [('CLOSE','V024 | CLOSE portrait',(480,720),list(range(1,38))),('SHOT','V020 | CHILD | SHOT',(1280,720),[1,4,10,12,13,14,15,16,17,18,19,20,21,23,25,26,27,28,29,30,31,32,33,34,35,36,37])]:
    S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100;folder=P/'previews'/('PROOF_'+mode);folder.mkdir(exist_ok=True)
    for f in frames:S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
    record[mode]={'frames':frames,'size':size}
(P/'evidence/BREAKDOWN_RENDER_RECORD.json').write_text(json.dumps({'actual_rendered':record,'elapsed_seconds':time.time()-t,'threads':2},indent=2));print('V032_PROOF_RENDER_DONE',time.time()-t,flush=True)

