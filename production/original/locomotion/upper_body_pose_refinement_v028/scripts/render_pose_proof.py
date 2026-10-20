import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];r=json.loads((P/'evidence/UPPER_BODY_AND_PRESERVATION_CHECKS.json').read_text());assert not r['unreachable_samples']
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Upper_Body_Pose_Refinement_v028.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;start=time.time()
for mode,camera,size,frames in [('CLOSE','V024 | CLOSE portrait',(480,720),range(1,33)),('SHOT','V020 | CHILD | SHOT',(1280,720),[1,4,6,9,11,13,17,20,22,25,27,29,32])]:
    D=P/'previews'/('PROOF_'+mode);D.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in frames:S.frame_set(f);S.render.filepath=str(D/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V028_MATCHED_POSE_PROOF_COMPLETE',time.time()-start,flush=True)
