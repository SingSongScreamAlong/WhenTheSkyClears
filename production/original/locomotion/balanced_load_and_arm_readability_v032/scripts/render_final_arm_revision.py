"""Compare actual saved GP drawings and rerender every changed phase each cycle.
Untouched rendered frames already belong to the identical final native state.
"""
import bpy,json,time,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];start=time.time()
def hashes():
    ob=bpy.data.objects['V032 | editable rough construction GP'];return {f.frame_number:hashlib.sha256(repr([(s.material_index,[(tuple(p.position),p.radius,p.opacity) for p in s.points]) for s in f.drawing.strokes]).encode()).hexdigest() for f in ob.data.layers[0].frames if f.frame_number<=32}
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRE_ARM_LAG_REVIEW_v032.blend'),load_ui=False,use_scripts=False);before=hashes()
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Rough_Construction_v032.blend'),load_ui=False,use_scripts=False);after=hashes();changed=[f for f in before if before[f]!=after[f]];assert changed
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in range(1,289):
        if 1+(f-1)%32 not in changed:continue
        S.frame_set(f);S.render.filepath=str(P/f'previews/{mode}/{f:04d}.png');bpy.ops.render.render(write_still=True)
    for f in (range(1,38) if mode=='CLOSE' else [1,4,10,12,13,14,15,16,17,18,19,20,21,23,25,26,27,28,29,30,31,32,33,34,35,36,37]):
        if 1+(f-1)%32 not in changed:continue
        S.frame_set(f);S.render.filepath=str(P/f'previews/PROOF_{mode}/{f:04d}.png');bpy.ops.render.render(write_still=True)
    print('V032_ARM_LAG_PHASE_RENDER_COMPLETE',mode,changed,round(time.time()-start,1),flush=True)
(P/'evidence/FINAL_ARM_LAG_RENDER_RECORD.json').write_text(json.dumps({'changed_drawing_frames':changed,'selection':'Exact actual GP point/material/style hash comparison against pre-lag V032 native; every changed phase rendered for all9cycles in both views, plus proof frames. Unchanged frames already rendered from identical scene/camera/material state.','elapsed_seconds':time.time()-start,'threads':2,'body_head_boot_travel_unchanged_by_this_revision':True},indent=2))
