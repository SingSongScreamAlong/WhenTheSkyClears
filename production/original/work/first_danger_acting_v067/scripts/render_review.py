"""Render explicit candidate frames; never save or alter production sources."""
import bpy,json,sys,time,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());S=Path(B['native']);H=hashlib.sha256(S.read_bytes()).hexdigest()
assert H==B['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes[B['world_scene']];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];oc=bpy.data.scenes['V065 | actual foreground oak alpha']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['keys']
mode=args[0]
if mode=='keys':frames=[913,937,957,966,979,990,1016,1056,1080];size=[1280,720]
elif mode in ['blink','blink2']:frames=[957,966];size=[1280,720]
elif mode=='movie':frames=list(range(int(args[1]),int(args[2])+1));size=[1280,720]
elif mode=='early':frames=list(range(int(args[1]),int(args[2])+1));size=[1280,720]
elif mode=='witness':frames=[990,1016];size=[1280,720]
elif mode=='uhd':frames=[957,990,1016];size=[3840,2160]
else:raise ValueError(mode)
base=O/'renders'/(mode+'_C')
for d in ['final','world']:(base/d).mkdir(parents=True,exist_ok=True)
for sc in [w,m,oc]:
 sc.render.resolution_x=size[0];sc.render.resolution_y=size[1];sc.render.resolution_percentage=100
 sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.use_sequencer=False
 sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.image_settings.compression=15
 sc.render.dither_intensity=0;sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
 if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=24 if mode in ['movie','early','witness'] else 32
for node in w.compositing_node_group.nodes:
 if node.type=='OUTPUT_FILE':
  node.mute=node.name!='V065 | world export'
  if not node.mute:node.directory=str(base/'world');node.file_name='frame_####'
record=O/f'evidence/RENDER_{mode}_C_{frames[0]}_{frames[-1]}.json'
assert not record.exists(),'Inspect prior job before reusing a recorded range'
rows=[]
for g in frames:
 target=base/'final'/f'{g:04d}.png';world=base/'world'/f'{g:04d}.png'
 assert not target.exists() and not world.exists(),'Refusing to overwrite rendered frames'
 for sc in [m,oc,w]:sc.frame_set(g)
 bpy.context.window.scene=w;bpy.context.view_layer.update();t=time.monotonic();w.render.filepath=str(target)
 bpy.ops.render.render(write_still=True,scene=w.name)
 raw=base/'world'/f'frame_{g:04d}Image.png';assert raw.exists();raw.replace(world)
 ctrl=bpy.data.objects['V065 | both children | global full-cut color time'];u=((g-1)/24)/96;expected=3*u*u-2*u*u*u
 assert abs(ctrl['charcoal_progress']-expected)<2e-6
 rows.append({'frame':g,'seconds':round(time.monotonic()-t,3),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'world_sha256':hashlib.sha256(world.read_bytes()).hexdigest()})
 record.write_text(json.dumps({'native_sha256':H,'mode':mode,'resolution':size,'range':[frames[0],frames[-1]],'expected':len(frames),'completed':len(rows),'rows':rows,'status':'rendering'},indent=2))
 print('V067_FRAME',g,len(rows),len(frames),rows[-1]['seconds'],flush=True)
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
record.write_text(json.dumps({'native_sha256':H,'mode':mode,'resolution':size,'range':[frames[0],frames[-1]],'expected':len(frames),'completed':len(rows),'rows':rows,'status':'complete'},indent=2))
print('V067_RENDER_COMPLETE',mode,frames[0],frames[-1],flush=True)
