import bpy,sys,time,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_PROOF_v003 | 75-80s held shot evolution'];bpy.context.window.scene=s
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];mode=args[0] if args else 'keys'
start=time.perf_counter();report={'mode':mode,'frames':[],'pixels':[1920,1080],'fps':24,'samples':32,'cpu_threads':2,'renderer':s.render.engine,'cache_bake':False}
if mode=='cpu_keys':
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.use_denoising=False;s.cycles.max_bounces=2;s.cycles.transparent_max_bounces=32
    s.render.resolution_percentage=50;s.render.threads=1
    if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
    # Held background is already1080p; render it at the same half size.
    nt=s.compositing_node_group
    for n in list(nt.nodes):
        if n.type=='IMAGE' and n.name!='Held real project shot at frame1825':
            for link in list(n.outputs['Image'].links):
                dst=link.to_socket;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(n.outputs['Image'],scale.inputs['Image']);nt.links.new(scale.outputs[0],dst)
            for link in list(n.outputs['Alpha'].links):
                dst=link.to_socket;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(n.outputs['Alpha'],scale.inputs['Image']);nt.links.new(scale.outputs[0],dst)
        elif n.type=='SCALE':
            n.inputs['X'].default_value=.25;n.inputs['Y'].default_value=.25
    report.update({'pixels':[960,540],'samples':4,'cpu_threads':1,'renderer':'CYCLES CPU','compositor':'CPU'})
if mode=='motion':
    folder=P/'previews/motion_frames';folder.mkdir(exist_ok=True);s.render.filepath=str(folder)+'/'
    s.frame_start=1800;s.frame_end=1919;bpy.ops.render.render(animation=True,scene=s.name)
else:
    for frame in [1825,1830,1842,1860,1890,1919]:
        s.frame_set(frame);prefix='CPUkey' if mode=='cpu_keys' else 'key';s.render.filepath=str(P/f'previews/{prefix}_{frame}_v003.png');t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);report['frames'].append({'frame':frame,'seconds':time.perf_counter()-t})
report['elapsed_seconds']=time.perf_counter()-start
(P/f'evidence/render_{mode}_v003.json').write_text(json.dumps(report,indent=2));print('FX_EVOLUTION_RENDER_COMPLETE',json.dumps(report),flush=True)
