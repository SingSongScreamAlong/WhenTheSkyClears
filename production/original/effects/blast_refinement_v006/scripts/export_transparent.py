"""Working-resolution straight-alpha middle blast, with no scene masks or bloom."""
import bpy, json, time, math, os, csv, subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.context.scene
for label in ['NEAR','FAR','TRACER_MID','TRACER_FAR']:
    bpy.data.collections['FXv006 | LAYER | '+label].hide_render=True
bpy.data.collections['FXv006 | GROUND IMPACT | MID'].hide_render=True
root=bpy.data.objects['FXv006 | MID | Blast controls']
camera=s.camera;camera.data.type='ORTHO';camera.data.ortho_scale=7.0;camera.data.shift_x=0;camera.data.shift_y=0
camera.location=(root.location.x,root.location.y-8,root.location.z+1.65);camera.rotation_euler=(math.pi/2,0,0)
s.render.resolution_x=960;s.render.resolution_y=540;s.eevee.taa_render_samples=16
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
folder=P/'sequences/MID_unbloomed_960_RGBA';folder.mkdir(parents=True,exist_ok=True)
start=time.perf_counter();records=[]
for local in range(120):
    file=folder/f'{local+1:04d}.png'
    if file.exists() and file.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    process_rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
    others=[int(row[1]) for row in process_rows if row and row[0].lower()=='blender.exe' and int(row[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Transparent export yielded to other Blender PIDs '+str(others))
    s.frame_set(1824+local);bpy.context.view_layer.update();s.render.filepath=str(folder/f'{local+1:04d}.png')
    t=time.perf_counter();bpy.ops.render.render(write_still=True);records.append(time.perf_counter()-t)
report={'folder':str(folder.relative_to(P)),'pixels':[960,540],'frames':[1,120],'fps':24,'alpha':'straight/unassociated RGBA PNG','color':'Standard view, display-referred sRGB 8-bit','premultiplied_internal_render_converted_by_Blender_PNG_writer':True,'bloom':False,'ground_impact':False,'occlusion_masks':False,'native_start_frame':1824,'local_frame1_age':0,'camera_projection':'orthographic, forward +Y, up +Z','camera_width_m':7.0,'camera_height_m':3.9375,'ground_anchor_uv':[.5,(1.96875-1.65)/3.9375],'render_seconds':time.perf_counter()-start,'per_frame_seconds':records,'purpose':'Working-resolution import proxy. Use native collection for final-resolution integration and separable persistent ground.'}
(P/'evidence/transparent_sequence.json').write_text(json.dumps(report,indent=2));print('TRANSPARENT_SEQUENCE_COMPLETE',json.dumps({k:v for k,v in report.items() if k!='per_frame_seconds'}),flush=True)
