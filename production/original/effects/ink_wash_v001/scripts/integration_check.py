"""Read-only production world load; never saves the production file."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes.get('WTSC_WORLD_CORRECTED_v037') or bpy.data.scenes['WTSC_WORLD_CORRECTED_v036'];bpy.context.window.scene=s;F=1801;s.frame_set(F)
source_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
pair=next(o for o in s.objects if o.type=='GREASEPENCIL');points=pair.data.layers[0].frames[0].drawing.attributes['position'].data
sole=min((pair.matrix_world@p.vector).z for p in points);depth=min((pair.matrix_world@p.vector).y for p in points);slope=(3-sole)/(16+depth)
settings=[('FX01_Explosion_Tall_Charcoal',102.7,6,.8,F-28),('FX03_Explosion_Distant_Muted',106.8,6,.65,F-46),('FX04_Incoming_Left_To_Right',106.7,5,.65,F-5)]
rows=[]
for name,x,y,size,start in settings:
    with bpy.data.libraries.load(str(P/'native'/f'{name}_v001.blend'),link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith(name)]
    c=dst.collections[0];s.collection.children.link(c);root=next(o for o in c.objects if 'CONTROLS' in o.name);root.location=(x,y,3-slope*(y+16));root['size']=size;root['start_frame']=float(start)
    rows.append({'collection':name,'emitter':list(root.location),'size':size,'start_frame':start,'age':F-start})
s.frame_set(F);bpy.context.view_layer.update()
from bpy_extras.object_utils import world_to_camera_view
for row in rows:
    root=s.objects[row['collection']+' | CONTROLS'];row['evaluated_age']=root['age'];row['projected_anchor']=list(world_to_camera_view(s,s.camera,root.matrix_world.translation))
s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(P/'previews/WTSC_FX_Actual_World_Integration_v001.png');s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.max_bounces=1;s.cycles.transparent_max_bounces=48;s.render.threads_mode='FIXED';s.render.threads=2
bpy.ops.render.render(write_still=True,scene=s.name)
source_unchanged=source_sha==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();assert source_unchanged
(P/'evidence/integration_check.json').write_text(json.dumps({'source_read_only':bpy.data.filepath,'source_sha256':source_sha,'source_unchanged_after_render':source_unchanged,'frame':F,'output_pixels':[480,270],'effects':rows,'placement':'Measured projected floor ray from existing camera and GP sole depth; native meshes appended into world at actual scale. Production file not saved.','production_file_save_called':False,'engine':'Cycles CPU, 8 samples; low-cost integration check. Native GP renderer support differs from production Eevee.'},indent=2))
print('FX_ACTUAL_WORLD_INTEGRATION_RENDERED',flush=True)
