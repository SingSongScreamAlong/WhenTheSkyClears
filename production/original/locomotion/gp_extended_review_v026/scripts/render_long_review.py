import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];report=json.loads((P/'evidence/FULL_CYCLE_AND_TRAVEL_CHECK.json').read_text());assert report['preserved_v025_frames_17_32_exact'] and not report['unreachable_chains']
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_GP_Extended_Review_v026.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;start=time.time()
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    folder=P/'previews'/mode;folder.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in range(1,280):
        S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        if f%31==0:print('V026_RENDER_PROGRESS',mode,'cycle',f//31,'/9','seconds',round(time.time()-start,1),flush=True)
    print('V026_VIEW_DONE',mode,flush=True)
(P/'evidence/LONG_RENDER_RECORD.json').write_text(json.dumps({'frames_per_view':279,'fps':30,'cycles_per_view':9,'seconds_per_view':9.3,'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'threads':2,'elapsed_seconds':time.time()-start,'engine':S.render.engine,'normal_speed':True,'boundary_sample_policy':'31 samples per cycle, no extra duplicate bookend; sequence is nativeF1..279'},indent=2));print('V026_LONG_REVIEW_RENDER_COMPLETE',time.time()-start,flush=True)
