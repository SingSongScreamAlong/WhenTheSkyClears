import bpy,json,time,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['HYBRID_v005 | matched control and ONE candidate'];bpy.context.window.scene=s
mode=sys.argv[-1] if sys.argv[-1] in ['control_keys','hybrid_keys','motion'] else 'hybrid_keys'
root=bpy.data.objects['FXv003 | fixed ground origin and controls'];control=mode=='control_keys';root['hybrid_enabled']=0.0 if control else 1.0;root.update_tag()
for ob in s.objects:
    if ob.name.startswith('FXv003 | rolling smoke '):ob.hide_render=False
    if ob.name.startswith('FXv003 | weighted debris '):ob.hide_render=not control
    if ob.name.startswith('GasParticlesv004 |'):ob.hide_render=control
    if ob.name.startswith('GasPilotv004 PREVIEW |'):ob.hide_render=True
folder=P/'previews/hybrid_frames';folder.mkdir(exist_ok=True)
selected=range(-23,97) if mode=='motion' else [6,24,60,90]
start=time.perf_counter();frames=[]
for frame in selected:
    s.frame_set(frame);bpy.context.view_layer.update()
    basename=('-'+f'{abs(frame):04d}') if frame<0 else f'{frame:04d}'
    s.render.filepath=str(folder/(basename+'.png')) if mode=='motion' else str(P/f'previews/{mode}_{frame:04d}.png')
    t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name)
    if mode!='motion':frames.append({'local_frame':frame,'production_frame':1823+frame,'seconds':time.perf_counter()-t})
report={'mode':mode,'control':control,'frames':frames,'render_calls_seconds':time.perf_counter()-start,'frame_count':len(selected),'renderer':s.render.engine,'samples':s.eevee.taa_render_samples,'pixels':[s.render.resolution_x,s.render.resolution_y],'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'camera_matrix':[list(row) for row in s.camera.matrix_world],'cpu_threads':s.render.threads,'new_bake':False}
(P/f'evidence/render_{mode}.json').write_text(json.dumps(report,indent=2));print('HYBRID_RENDER_COMPLETE',json.dumps(report),flush=True)
