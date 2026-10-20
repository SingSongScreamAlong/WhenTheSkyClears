"""Render actual native v065 title/world/actor-matte outputs on one global clock."""
import bpy,json,hashlib,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
build_start=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build_start['world_render_native'] if '--world-source' in sys.argv else build_start['native']);H=hashlib.sha256(S.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];bpy.context.window.scene=w
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['pilots']
mode=args[0]
if mode.startswith('pilots'):frames=[913,936,937,957,981,1033,1056,1057,1080];width,height=1280,720
elif mode=='movie':frames=range(int(args[1]),int(args[2])+1) if len(args)>2 else range(913,1081);width,height=3840,2160
elif mode=='keys4k':frames=[913,937,981,1056,1080];width,height=3840,2160
else:raise ValueError(mode)
base=O/('renders/'+mode if mode.startswith('pilots') else 'renders/native4K' if mode=='keys4k' else 'renders/sequence4K')
tag=mode.upper()+(('_'+str(min(frames))+'_'+str(max(frames))) if mode=='movie' and len(args)>2 else '')
for folder in ['final','world','inherited','matte','glyph']:(base/folder).mkdir(parents=True,exist_ok=True)
for sc in [w,m]:
 sc.render.resolution_x=width;sc.render.resolution_y=height;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.use_sequencer=False;sc.render.use_compositing=True;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.image_settings.compression=15;sc.render.dither_intensity=0
 if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=32
folder_map={'V065 | world export':'world','V065 | inherited title export':'inherited','V065 | visible actor matte':'matte','V065 | original glyph alpha':'glyph'}
for node in w.compositing_node_group.nodes:
 if node.type=='OUTPUT_FILE':
  node.mute=node.name not in folder_map
  if not node.mute:node.directory=str(base/folder_map[node.name]);node.file_name='frame_####'
rows=[]
build=json.loads((O/'evidence/BUILD.json').read_text())
actor_mats={slot.material for name in build['matte_objects'] if name in w.objects for slot in w.objects[name].material_slots if slot.material and slot.material.get('V063_color_arc')}
mix_nodes=[n for mat in actor_mats for n in mat.node_tree.nodes if n.name.startswith('V063 | shared color to charcoal /')]
assert mix_nodes,'No active color materials inspected'
for g in frames:
 target=base/'final'/f'{g:04d}.png'
 if mode=='movie' and target.exists():
  assert all((base/folder/f'{g:04d}.png').exists() for folder in ['world','inherited','matte','glyph'])
  rows.append({'frame':g,'resumed_existing':True});continue
 start=time.monotonic();bpy.context.window.scene=w;w.frame_set(g);bpy.context.view_layer.update()
 ctrl=bpy.data.objects['V065 | both children | global full-cut color time'];u=((g-1)/24)/96;expected=3*u*u-2*u*u*u
 assert abs(ctrl['charcoal_progress']-expected)<.000002,(g,ctrl['charcoal_progress'],expected)
 m.frame_set(g);bpy.context.view_layer.update();w.render.filepath=str(target)
 bpy.ops.render.render(write_still=True,scene=w.name)
 for folder in ['world','inherited','matte','glyph']:
  raw=base/folder/f'frame_{g:04d}Image.png';dest=base/folder/f'{g:04d}.png'
  assert raw.exists(),str(raw);raw.replace(dest)
 ctrl=bpy.data.objects['V065 | both children | global full-cut color time']
 assert abs(ctrl['charcoal_progress']-expected)<.000002,(g,'render kept stale palette',ctrl['charcoal_progress'],expected)
 live=[float(n.inputs[0].default_value) for n in mix_nodes];assert max(abs(v-expected) for v in live)<.000002,(g,'material clock stale',min(live),max(live),expected)
 row={'frame':g,'world_clock':w.frame_current,'title_clock':m.frame_current,'charcoal_progress':ctrl['charcoal_progress'],'material_progress_min':min(live),'material_progress_max':max(live),'camera_x':w.camera.matrix_world.translation.x,'seconds_to_render':round(time.monotonic()-start,3),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()};rows.append(row)
 (O/f'evidence/RENDER_{tag}_PROGRESS.json').write_text(json.dumps({'completed':len(rows),'total':len(frames),'last_frame':g,'rows':rows},indent=2));print('V065_RENDER',mode,g,len(rows),len(frames),row['seconds_to_render'],flush=True)
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
(O/f'evidence/RENDER_{tag}_COMPLETE.json').write_text(json.dumps({'native':str(S),'native_sha256':H,'native_unchanged':True,'mode':mode,'frames':len(rows),'resolution':[width,height],'global_range':[min(frames),max(frames)],'rows':rows},indent=2));print('V065_RENDER_COMPLETE',mode,flush=True)
