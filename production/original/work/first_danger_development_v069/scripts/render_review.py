import bpy,json,sys,time,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());N=Path(B['native']);H=hashlib.sha256(N.read_bytes()).hexdigest();assert H==B['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False)
W=bpy.data.scenes[B['world_scene']];T=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];C=bpy.data.scenes['V065 | actual foreground oak alpha']
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['keys'];mode=args[0]
if mode=='keys':frames=[913,951,961,973,985,991,1003,1021,1080];size=[1280,720]
elif mode=='movie':frames=list(range(int(args[1]),int(args[2])+1));size=[1280,720]
elif mode=='uhd':frames=[973,991,1003];size=[3840,2160]
else:raise ValueError(mode)
tag=N.stem.split('_')[-1]
base=O/'renders'/(mode+'_'+tag)
for d in ['final','world']:(base/d).mkdir(parents=True,exist_ok=True)
for sc in [W,T,C]:
 sc.render.resolution_x=size[0];sc.render.resolution_y=size[1];sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.use_sequencer=False
 sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.image_settings.compression=15;sc.render.dither_intensity=0
 sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
 if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=24
for node in W.compositing_node_group.nodes:
 if node.type=='OUTPUT_FILE':
  node.mute=node.name!='V065 | world export'
  if not node.mute:node.directory=str(base/'world');node.file_name='frame_####'
record=O/f'evidence/RENDER_{mode}_{tag}_{frames[0]}_{frames[-1]}.json';assert not record.exists(),'Inspect recorded jobs before retry'
rows=[]
for g in frames:
 target=base/'final'/f'{g:04d}.png';world=base/'world'/f'{g:04d}.png';assert not target.exists() and not world.exists()
 for sc in [T,C,W]:sc.frame_set(g)
 bpy.context.window.scene=W;bpy.context.view_layer.update();t=time.monotonic();W.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=W.name)
 raw=base/'world'/f'frame_{g:04d}Image.png';assert raw.exists();raw.replace(world)
 visible=[o for o in W.objects if o.name in B['new_drawing_objects'] and not o.hide_render];assert len(visible)==2
 heads=[o for o in W.objects if o.name in B['head_objects'] and not o.hide_render];assert len(heads)==2
 assert all(o.hide_render for o in W.objects if o.name in B.get('hidden_original_objects',[]))
 rows.append({'frame':g,'seconds':round(time.monotonic()-t,3),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'world_sha256':hashlib.sha256(world.read_bytes()).hexdigest(),'visible_drawings':[o.name for o in visible]})
 record.write_text(json.dumps({'native_sha256':H,'mode':mode,'resolution':size,'range':[frames[0],frames[-1]],'expected':len(frames),'completed':len(rows),'rows':rows,'status':'rendering'},indent=2))
 print('V069_FRAME',g,len(rows),len(frames),rows[-1]['seconds'],flush=True)
assert hashlib.sha256(N.read_bytes()).hexdigest()==H
data=json.loads(record.read_text());data['status']='complete';record.write_text(json.dumps(data,indent=2));print('V069_RENDER_COMPLETE',flush=True)
