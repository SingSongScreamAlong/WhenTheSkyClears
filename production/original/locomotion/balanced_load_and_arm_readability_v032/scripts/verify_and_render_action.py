import bpy,sys,json,math,time
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import construction_motion as M
gate=json.loads((P/'evidence/BREAKDOWN_VISUAL_REVIEW.json').read_text());assert gate['proceed_to_short_construction_test'] is True
# Compare actual saved V031 boot transforms, not merely their evaluator.
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_BASELINE_v031.blend'),load_ui=False,use_scripts=False)
prior=bpy.context.scene;baseline={}
for j in range(513):
    f=1+j/16;prior.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
    baseline[j]={s:[(float(v.x),float(v.z)) for v in [bpy.data.objects['V031 | original painted '+s+' boot'].matrix_world@p.co for p in bpy.data.objects['V031 | original painted '+s+' boot'].data.vertices]] for s in ['near','far']}
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Rough_Construction_v032.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;fore=S.view_layers['V025 | original foreground'];root=bpy.data.objects['V032 | CONSTRUCTION TRAVEL'];body=bpy.data.objects['V032 | editable rough construction GP'];maxboot=0.;maxsole=0.;maxroot=0.;maxcontactx=0.;maxhead=0.;maxprior=0.;maxcuff=0.
for i in range(2049):
    f=1+i/64;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();fore.update();p,r,m=M.evaluate(f-1)
    maxroot=max(maxroot,abs(root.location.x-r['D']))
    h=bpy.data.objects['V032 | retained painted head'].evaluated_get(fore.depsgraph);hw=h.matrix_world.translation;maxhead=max(maxhead,abs(hw.x-r['D']-p['neck'][0]),abs(hw.z-p['neck'][1]))
    for s in ['near','far']:
        ob=bpy.data.objects['V032 | original painted '+s+' boot'];L=r['legs'][s];VV=[ob.matrix_world@v.co for v in ob.data.vertices];expected=[[x+r['D'],z] for x,z in L['boot_vertices']]
        maxboot=max(maxboot,max(math.hypot(v.x-x,v.z-z) for v,(x,z) in zip(VV,expected)))
        if i%4==0:maxprior=max(maxprior,max(math.hypot(v.x-x,v.z-z) for v,(x,z) in zip(VV,baseline[i//4][s])))
        if i%64==0:
            fr=next(fr for fr in body.data.layers[0].frames if fr.frame_number==int(f));st=fr.drawing.strokes[13 if s=='near' else 8];C=sum((Vector(p.position) for p in st.points),Vector())/len(st.points);K=L['knee'];A=L['ankle'];w=Vector((A[0]-K[0],0,A[1]-K[1])).normalized();join=body.matrix_world@(C+w*.0185);BA=ob.matrix_world.translation;maxcuff=max(maxcuff,math.hypot(join.x-BA.x,join.z-BA.z))
        if L['mode']=='CONTACT':
            maxsole=max(maxsole,abs(min(v.z for v in VV)));j=L['contact']['vertex'];maxcontactx=max(maxcontactx,abs(VV[j].x-L['contact']['anchor_x']))
report={'scope':'Cold-reopened native transformation/contact checks, including between transform keys. Does not establish convincing motion.','sample_count':2049,'sample_interval_frames':1/64,'native_transform_key_interval_frames':1/16,'max_root_error_m':maxroot,'max_boot_vertex_error_against_analytic_m':maxboot,'max_support_sole_height_error_m':maxsole,'max_active_contact_world_x_error_m':maxcontactx,'max_head_neck_interpolation_error_m':maxhead,'max_actual_boot_change_from_saved_v031_m':maxprior,'max_integer_frame_cuff_join_error_m':maxcuff,'cuff_measurement':'Actual GP cuff-point center, undo authored18.5mm centerline inset, compare X/Z to actual saved boot transform origin.33integer frames both feet.','GP_sampling':'Body drawings are on ones; integer native-frame cuff/boot relation is exact. Production24fps requires a unified resample from construction_motion.py.','normal_speed_render':'F1..288 uninterrupted per view, nine full32-frame periods,30fps'}
(P/'evidence/COLD_REOPEN_AND_RENDER_CHECK.json').write_text(json.dumps(report,indent=2))
assert maxroot<1e-6 and maxboot<.0003 and maxsole<.0003 and maxcontactx<.0003 and maxhead<.0003 and maxprior<1e-6 and maxcuff<1e-6
if '--verify-only' in sys.argv:
    print('V032_COLD_NATIVE_CHECK_PASS',json.dumps(report),flush=True);sys.exit(0)
S.render.threads_mode='FIXED';S.render.threads=2;t=time.time()
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100;folder=P/'previews'/mode;folder.mkdir(exist_ok=True)
    for f in range(1,289):
        S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        if f%32==0:print('V032_NORMAL_SPEED_PROGRESS',mode,f,'/288',round(time.time()-t,1),flush=True)
(P/'evidence/NORMAL_SPEED_RENDER_RECORD.json').write_text(json.dumps({'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'frames_per_view':288,'total_actual_renders':576,'fps':30,'seconds_per_view':9.6,'cycles_per_view':9,'threads':2,'elapsed_seconds':time.time()-t,'status':'Construction test only; visual acceptance pending independent/human playback review'},indent=2));print('V032_NORMAL_SPEED_RENDER_COMPLETE',time.time()-t,flush=True)
