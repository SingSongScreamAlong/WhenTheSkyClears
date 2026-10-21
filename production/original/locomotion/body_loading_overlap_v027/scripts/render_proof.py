import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1]
r=json.loads((P/'evidence/LOADING_AND_CONTACT_CHECKS.json').read_text());assert not r['unreachable_samples']
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Body_Loading_Overlap_v027.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540;S.render.resolution_percentage=100
D=P/'previews/PROOF';D.mkdir(exist_ok=True);start=time.time()
for f in range(1,33):
    S.frame_set(f);S.render.filepath=str(D/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V027_SMALL_PROOF_COMPLETE',time.time()-start,flush=True)
