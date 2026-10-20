import bpy,json,time,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];r=json.loads((P/'evidence/UPPER_BODY_AND_PRESERVATION_CHECKS.json').read_text());gate=json.loads((P/'evidence/POSE_REVIEW_GATE.json').read_text());assert not r['unreachable_samples'] and gate['status']=='POSE_CHANGE_WARRANTS_NORMAL_SPEED_COMPARISON_NOT_ART_ACCEPTANCE'
baseline='--baseline' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(P/('reference/PRESERVED_BASELINE_v027.blend' if baseline else 'native/WTSC_Upper_Body_Pose_Refinement_v028.blend')),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;start=time.time()
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    D=P/'previews'/('BASELINE' if baseline else '')/mode;D.mkdir(exist_ok=True,parents=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in range(1,280):
        S.frame_set(f);S.render.filepath=str(D/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        if f%31==0:print('V028_LONG_PROGRESS',mode,'cycle',f//31,'/9','elapsed',round(time.time()-start,1),flush=True)
record={'frames_per_view':279,'cycles_per_view':9,'fps':30,'seconds_per_view':9.3,'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'threads':2,'elapsed_seconds':time.time()-start,'engine':S.render.engine,'normal_speed':True,'baseline_render_source':'../body_loading_overlap_v027/previews: same two cameras and resolutions; all279frames reused unchanged','native_sequence':'F1..279, no duplicate bookend, holds, retiming or optical interpolation'}
(P/('evidence/BASELINE_REPRO_RENDER_RECORD.json' if baseline else 'evidence/LONG_RENDER_RECORD.json')).write_text(json.dumps(record,indent=2));print('V028_LONG_RENDER_COMPLETE',json.dumps(record),flush=True)
