"""Read-only production geometry -> frozen native alpha by depth."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1]
source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest()
world=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];bpy.context.window.scene=world;world.frame_set(1825);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
hidden=set(json.loads((P.parent/'benchmark_v002/evidence/benchmark_build.json').read_text())['old_fx_hidden_in_copy'])
s=bpy.data.scenes.new('FXv006 | frozen native depth alpha ONLY')
cam=world.camera.copy();cam.data=world.camera.data.copy();cam.animation_data_clear();cam.parent=None;cam.matrix_world=world.camera.matrix_world.copy();s.collection.objects.link(cam);s.camera=cam
objects=[];cache={};skipped=[]
for ob in world.objects:
    if ob.type!='MESH' or ob.hide_render or ob.name in hidden:continue
    points=[ob.matrix_world@Vector(p) for p in ob.bound_box]
    if not points or max(p.x for p in points)<103 or min(p.x for p in points)>120 or min(p.y for p in points)>=24:continue
    if any(word in ob.name.lower() for word in ['sky','horizon','mountain','backdrop']):skipped.append(ob.name);continue
    evaluated=ob.evaluated_get(dg);mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dg)
    clone=bpy.data.objects.new('Depth alpha | '+ob.name,mesh);s.collection.objects.link(clone);clone.matrix_world=ob.matrix_world.copy()
    for i,material in enumerate(list(mesh.materials)):
        if not material or not material.node_tree:continue
        if material.name not in cache:
            m=material.copy();m.name='v006 alpha | '+material.name;nt=m.node_tree;nt.animation_data_clear()
            white=nt.nodes.new('ShaderNodeEmission');white.inputs['Color'].default_value=(1,1,1,1);white.inputs['Strength'].default_value=1
            for old in [n for n in nt.nodes if n.type in {'EMISSION','BSDF_PRINCIPLED','BSDF_DIFFUSE','HOLDOUT'} and n!=white]:
                for link in list(old.outputs[0].links):nt.links.new(white.outputs[0],link.to_socket)
            cache[material.name]=m
        mesh.materials[i]=cache[material.name]
    objects.append((clone,min(p.y for p in points),ob.name))
bpy.context.window.scene=s;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='Standard';s.view_settings.look='None'
s.frame_set(1825);results=[]
for depth in [4,9,10,11.5,14]:
    for ob,y,name in objects:ob.hide_render=y>=depth-.03
    label=f'{int(depth):02d}' if depth==int(depth) else str(depth).replace('.','p')
    s.render.filepath=str(P/f'assets/Native_Depth_Alpha_Y{label}_v006.png');bpy.ops.render.render(write_still=True,scene=s.name)
    results.append({'depth_y':depth,'objects':[name for ob,y,name in objects if not ob.hide_render]})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
# The current native Glare socket schema is recorded rather than guessed.
nt=bpy.data.node_groups.new('v006 Glare schema','CompositorNodeTree');glare=nt.nodes.new('CompositorNodeGlare')
schema={'inputs':[{'name':v.name,'type':v.type,'default':str(getattr(v,'default_value',None))} for v in glare.inputs],'outputs':[v.name for v in glare.outputs]}
report={'source':str(source),'source_hash_unchanged':before,'frame':1825,'pixels':[1920,1080],'depths':results,'background_role_exclusions':skipped,'method':'Frozen evaluated native meshes; original alpha chains retained and surface shaders replaced by white emission. Source never saved.','glare_schema':schema}
(P/'evidence/depth_mask_capture.json').write_text(json.dumps(report,indent=2));print('DEPTH_MASKS_CAPTURED',json.dumps({'objects':len(objects),'depths':[v['depth_y'] for v in results],'glare_schema':schema,'source_unchanged':True}),flush=True)
