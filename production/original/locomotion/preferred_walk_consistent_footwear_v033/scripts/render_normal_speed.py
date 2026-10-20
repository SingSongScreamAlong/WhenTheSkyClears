import bpy,json,time,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];gate=json.loads((P/'evidence/PROOF_VISUAL_REVIEW.json').read_text());assert gate['proceed_to_matched_normal_speed_review'];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Preferred_Walk_Consistent_Shoes_v033.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.threads_mode='FIXED';S.render.threads=2;t=time.time()
# Actual saved far-shoe contact anchors, including later cycles: no visual-slide
# claim based only on floor height. Expected anchors come from its rigid hull.
report=json.loads((P/'evidence/CONSISTENT_FOOTWEAR_BUILD.json').read_text());boot=bpy.data.objects['V033 | far | canonical painted shoe'];V=[(v.co.x*boot.scale.x,v.co.z*boot.scale.z) for v in boot.data.vertices]
def rot(v,a):return (math.cos(a)*v[0]+math.sin(a)*v[1],-math.sin(a)*v[0]+math.cos(a)*v[1])
def active(a):return min(range(len(V)),key=lambda j:rot(V[j],a)[1])
seqs={}
for sg in [-1,1]:
    j=active(sg*1e-7);anc=V[j][0];seq=[(0,j,anc)];last=j
    for i in range(1,5001):
        a=sg*math.radians(85)*i/5000;j=active(a)
        if j==last:continue
        dv=(V[j][0]-V[last][0],V[j][1]-V[last][1]);edge=math.atan2(dv[1],dv[0])
        while edge>math.pi/2:edge-=math.pi
        while edge<-math.pi/2:edge+=math.pi
        anc+=rot(dv,edge)[0];seq.append((edge,j,anc));last=j
    seqs[sg]=seq
mx=0.;count=0
for i in range(557):
    q=i/2;tphase=(q-16)%31
    if tphase>19.25+1e-9:continue
    f=q+1;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();a=boot.rotation_euler.y;seq=seqs[1 if a>=0 else -1];_,j,anc=seq[0]
    for edge,k,b in seq[1:]:
        if abs(a)+1e-9>=abs(edge):j,anc=k,b
        else:break
    expected=report['far_flat_ankle_contact_origin_m']+math.floor((q-16)/31)*report['stride_m']+anc;actual=(boot.matrix_world@boot.data.vertices[j].co).x;mx=max(mx,abs(actual-expected));count+=1
(P/'evidence/LATER_CYCLE_CONTACT_ANCHOR_CHECK.json').write_text(json.dumps({'actual_contact_samples':count,'through_frame':279,'max_horizontal_active_contact_anchor_error_m':mx,'scope':'Native shared far-shoe rocker anchor preservation over9cycles, not artistic acceptance'},indent=2));assert mx<.0004
t=time.time()
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    folder=P/'previews'/mode;folder.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in range(1,280):
        S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        if f%31==0:print('V033_PROGRESS',mode,f,'/279',round(time.time()-t,1),flush=True)
(P/'evidence/NORMAL_SPEED_RENDER_RECORD.json').write_text(json.dumps({'frames_per_view':279,'actual_candidate_renders':558,'fps':30,'cycles_per_view':9,'seconds_per_view':9.3,'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'baseline':'Original V028 actual279-frame renders from its existing CLOSE/SHOT folders, unchanged','matching':'Same native frame numbers, camera, lens, duration and30fps; no phase alignment/retiming','threads':2,'elapsed_seconds':time.time()-t},indent=2));print('V033_NORMAL_SPEED_RENDER_COMPLETE',time.time()-t,flush=True)
