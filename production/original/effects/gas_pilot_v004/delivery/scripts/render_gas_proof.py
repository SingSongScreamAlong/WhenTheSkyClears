import bpy,time,json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['GAS_PROOF_v004 |48div120frames | held framing'];bpy.context.window.scene=s
mode=sys.argv[-1] if sys.argv[-1] in ['keys','motion','preroll','cpu_keys','cpu_motion'] else 'keys'
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.resolution_percentage=100
start=time.perf_counter();frames=[]
if mode in ['cpu_keys','cpu_motion']:
    factor=1/3 if mode=='cpu_motion' else .5
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=2 if mode=='cpu_motion' else 4;s.cycles.use_denoising=mode=='cpu_motion';s.cycles.max_bounces=2;s.cycles.volume_bounces=0;s.cycles.transparent_max_bounces=32;s.render.resolution_percentage=100;s.render.resolution_x=round(1920*factor);s.render.resolution_y=round(1080*factor);s.render.threads=1
    if hasattr(s.cycles,'volume_step_rate'):s.cycles.volume_step_rate=3 if mode=='cpu_motion' else 2
    if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
    nt=s.compositing_node_group
    for n in list(nt.nodes):
        if n.type=='IMAGE' and n.name!='Held real project shot at frame1825':
            for socket_name in ['Image','Alpha']:
                for link in list(n.outputs[socket_name].links):
                    dst=link.to_socket;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=factor;scale.inputs['Y'].default_value=factor;nt.links.new(n.outputs[socket_name],scale.inputs['Image']);nt.links.new(scale.outputs[0],dst)
        elif n.type=='SCALE':n.inputs['X'].default_value=.5*factor;n.inputs['Y'].default_value=.5*factor
if mode in ['motion','cpu_motion','preroll']:
    folder=P/('previews/cpu_proof_frames' if mode=='cpu_motion' else 'previews/proof_frames');folder.mkdir(exist_ok=True);s.render.filepath=str(folder)+'/'
    # Scene.frame_start clamps negative values to0. Step actual negative
    # still frames explicitly to retain the full second of pre-roll.
    selected=range(-23,0) if mode=='preroll' else range(-23,97)
    for frame in selected:
        s.frame_set(frame)
        basename=('-'+f'{abs(frame):04d}') if frame<0 else f'{frame:04d}'
        s.render.filepath=str(folder/(basename+'.png'))
        bpy.ops.render.render(write_still=True,scene=s.name)
else:
    for frame in [6,24,60,108]:
        s.frame_set(frame);prefix='proof_CPUkey' if mode=='cpu_keys' else 'proof_key';s.render.filepath=str(P/f'previews/{prefix}_{frame:04}.png');begin=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);frames.append({'frame':frame,'equivalent_v003_frame':1823+frame,'render_seconds':time.perf_counter()-begin})
report={'mode':mode,'frames':frames,'wall_seconds':time.perf_counter()-start,'pixels':[1920,1080],'fps':24,'range':[-23,-1] if mode=='preroll' else ([-23,96] if mode=='motion' else [1,120]),'renderer':'Eevee32samples, volume96steps/32shadowsteps,4pixel tiles, custom depth18-34metres','cpu_threads':2}
if mode in ['cpu_keys','cpu_motion']:report.update({'pixels':[s.render.resolution_x,s.render.resolution_y],'renderer':f'Cycles CPU{s.cycles.samples}samples, denoise{s.cycles.use_denoising}, no volume bounces','cpu_threads':1,'range':[-23,96] if mode=='cpu_motion' else[1,120]})
(P/f'evidence/render_{mode}.json').write_text(json.dumps(report,indent=2));print('GAS_RENDER_COMPLETE',json.dumps(report),flush=True)
