import bpy,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PROOF_v004 |48div120frames | held framing'];bpy.context.window.scene=s
domain=next(o for o in s.objects if o.name.startswith('GasPilotv004 |48div gas domain'))
f=domain.driver_add('hide_render');f.driver.expression='frame < 1'
s.frame_start=-23;s.frame_end=96;s.render.filepath=str(P/'previews/proof_frames')+'/'
domain['timeline_mapping']='local1 == production1824 (76s); proof local-23..96 == production1800..1919 (75-80s). Cached tail extends to local120.'
states=[]
for frame in [6,24,60,96,108]:
    s.frame_set(frame);bpy.context.view_layer.update();d=domain.evaluated_get(bpy.context.evaluated_depsgraph_get()).modifiers['GasPilotv004 | native Mantaflow GAS'].domain_settings
    values=list(d.density_grid);res=list(getattr(d,'domain_resolution',[]));total=sum(values);bbox=None;boundary=0
    if len(res)==3 and math.prod(res)==len(values):
        points=[];nx,ny,nz=res
        for i,v in enumerate(values):
            if v>.01:points.append((i%nx,(i//nx)%ny,i//(nx*ny)))
            if i%nx in [0,nx-1] or (i//nx)%ny in [0,ny-1] or i//(nx*ny) in [0,nz-1]:boundary+=v
        if points:bbox={'minimum_cell':[min(p[k] for p in points) for k in range(3)],'maximum_cell':[max(p[k] for p in points) for k in range(3)]}
    states.append({'local_frame':frame,'production_frame':1823+frame,'grid_resolution':res,'density_max':max(values,default=0),'density_sum':total,'cells':len(values),'positive_cells':sum(v>.001 for v in values),'dense_bbox':bbox,'outer_boundary_mass_fraction':boundary/total if total else 0})
s.frame_set(-23);bpy.context.view_layer.update();assert domain.hide_render
s.frame_set(1);bpy.context.view_layer.update();assert not domain.hide_render
s.frame_set(60);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
v3=P.parent/'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend';v3hash=hashlib.sha256(v3.read_bytes()).hexdigest();assert v3hash=='d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'
report={'proof_local_frames':[-23,96],'production_frames':[1800,1919],'production_ignition':1824,'local_ignition':1,'fps':24,'all120_frames_will_be_actual_renders':True,'first_output':s.render.frame_path(frame=-23),'last_output':s.render.frame_path(frame=96),'native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'v003_source_sha256_unchanged':v3hash,'density_states':states,'status':'Native technique proof; visual acceptance pending.'}
(P/'evidence/proof_scene_validation.json').write_text(json.dumps(report,indent=2));print('GAS_PROOF_FINALIZED',json.dumps(report),flush=True)
