import bpy,json,time,sys,os,csv,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_PROOF_v006 | painted impulse depth tracers and ground'];bpy.context.window.scene=s
s.render.use_single_layer=False
mode=sys.argv[-1] if sys.argv[-1] in ['keys','motion','no_bloom','persistence','diagnostics'] else 'keys'
start=time.perf_counter();records=[]
if mode=='motion':
    folder=P/'previews/motion_frames';folder.mkdir(exist_ok=True);s.render.filepath=str(folder)+'/'
    s.frame_start=1800;s.frame_end=1919
    def complete_png(file):
        if not file.exists():return False
        data=file.read_bytes()
        return data[:8]==b'\x89PNG\r\n\x1a\n' and data[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82'
    for frame in range(1800,1920):
        file=folder/f'{frame:04d}.png'
        if complete_png(file):continue
        process_rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
        others=[int(row[1]) for row in process_rows if row and row[0].lower()=='blender.exe' and int(row[1]) not in [39896,os.getpid()]]
        if others:raise RuntimeError('Effects render yielded before next frame to other Blender PIDs '+str(others))
        if (P/'evidence/yield_render.request').exists():raise RuntimeError('Effects render yielded to production before next frame')
        s.frame_set(frame);bpy.context.view_layer.update();s.render.filepath=str(file);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':frame,'seconds':time.perf_counter()-t})
else:
    frames=[1824,1826,1832,1848,1884,1919] if mode=='keys' else ([2064,1826] if mode=='diagnostics' else ([2064] if mode=='persistence' else [1826]))
    if mode=='no_bloom':
        for node in s.compositing_node_group.nodes:
            if node.type=='GROUP' and node.node_tree and 'HDR FX bloom over' in node.node_tree.name:
                node.inputs['Bloom gain'].driver_remove('default_value');node.inputs['Bloom gain'].default_value=0
    for frame in frames:
        if mode=='diagnostics' and frame==1826:
            for node in s.compositing_node_group.nodes:
                if node.type=='GROUP' and node.node_tree and 'HDR FX bloom over' in node.node_tree.name:
                    node.inputs['Bloom gain'].driver_remove('default_value');node.inputs['Bloom gain'].default_value=0
        stem=('no_bloom' if frame==1826 else 'persistence') if mode=='diagnostics' else mode
        s.frame_set(frame);bpy.context.view_layer.update();s.render.filepath=str(P/f'previews/{stem}_{frame:04d}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':frame,'seconds':time.perf_counter()-t})
report={'mode':mode,'renderer':s.render.engine,'samples':s.eevee.taa_render_samples,'view_layers':[v.name for v in s.view_layers if v.use],'pixels':[1920,1080],'fps':24,'range':[1800,1919],'this_session_seconds':time.perf_counter()-start,'records':records,'threads':2,'new_bake':False,'resumption':'Complete PNGs reused; partial run yielded to production at frame1894. All delivered motion frames are actual renders of this native source.'}
(P/f'evidence/render_{mode}.json').write_text(json.dumps(report,indent=2));print('V006_RENDER_COMPLETE',json.dumps(report),flush=True)
