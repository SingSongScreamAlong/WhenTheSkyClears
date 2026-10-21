"""Fresh factory scene, native collection Append, reversible controls and RGBA render."""
import bpy, json, math, time
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parents[1]
evidence=json.loads((P/'evidence/build_refinement.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
source=P/'native/WTSC_Painted_Blast_Assets_v006.blend'
collection_name='FXv006 | APPEND ASSETS | painted blasts impacts tracers'
helper_name='FXv006 | HDR FX bloom over | append helper'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
    assert collection_name in available.collections
    assert helper_name in available.node_groups
    loaded.collections=[collection_name];loaded.node_groups=[helper_name]
s=bpy.context.scene;s.name='FXv006 | Fresh Append sandbox | RGBA'
asset=loaded.collections[0];s.collection.children.link(asset)
assert not [o for o in asset.all_objects if o.type in {'CAMERA','LIGHT'}]
roots={label:next(o for o in asset.all_objects if o.name=='FXv006 | '+label+' | Blast controls') for label in ['MID','NEAR','FAR']}
root=roots['MID'];start=root['start_frame'];speed=root['speed'];size=root['size']
root['start_frame']=2000.;root['speed']=.5;root['size']=1.25
s.frame_set(2012);bpy.context.view_layer.update()
assert abs(root['age']-6)<.0001
assert all(abs(v-1.25)<.0001 for v in root.scale)
root['start_frame']=start;root['speed']=speed;root['size']=size
ground=next(o for o in asset.all_objects if o.name=='FXv006 | MID | Ground impact controls')
gouge=next(o for o in asset.all_objects if o.parent==ground and o.get('asset_role')=='persistent_ground_gouge')
anchor=list(ground.matrix_world.translation)
s.frame_set(2300);bpy.context.view_layer.update()
alpha=gouge.data.materials[0].node_tree.nodes['Persistent/temporal alpha'].inputs[1].default_value
assert alpha>.9 and list(ground.matrix_world.translation)==anchor
invalid=[];outside=[];owners=set();asset_ids=set(asset.all_objects)
for ob in asset.all_objects:
    owners.add(ob)
    if ob.type=='MESH':
        if ob.data.shape_keys:owners.add(ob.data.shape_keys)
        owners.update(m.node_tree for m in ob.data.materials if m and m.node_tree)
for owner in owners:
    if owner.animation_data:
        for f in owner.animation_data.drivers:
            if not f.driver.is_valid:invalid.append([owner.name,f.data_path])
            for v in f.driver.variables:
                for target in v.targets:
                    if target.id and target.id not in asset_ids:outside.append(target.id.name)
assert not invalid and not outside,(invalid,outside)
images=[im for im in bpy.data.images if im.source=='FILE']
assert images and all(im.packed_file for im in images)
camera_data=bpy.data.cameras.new('Sandbox camera | matched project fixture')
camera=bpy.data.objects.new(camera_data.name,camera_data);s.collection.objects.link(camera)
camera.matrix_world=Matrix(evidence['camera_matrix']);camera_data.type='PERSP';camera_data.lens=100;camera_data.shift_x=-.30000022;camera_data.shift_y=-.2670553;s.camera=camera
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16
s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.fps=24;s.frame_start=1800;s.frame_end=1919
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.frame_set(1826);bpy.context.view_layer.update()
folder=P/'sandbox';folder.mkdir(exist_ok=True)
s.render.filepath=str(folder/'Append_Test_RGBA_1826.png')
t=time.perf_counter();bpy.ops.render.render(write_still=True);seconds=time.perf_counter()-t
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'WTSC_Fresh_Append_Sandbox_v006.blend'),compress=True)
report={'factory_empty':True,'append_source':source.name,'collection':asset.name,'native_helper':loaded.node_groups[0].name,'objects':len(asset.all_objects),'packed_images':[{ 'name':im.name,'size':list(im.size),'alpha_mode':im.alpha_mode} for im in images],'retime_test':{'start':2000,'speed':.5,'frame':2012,'expected_age':6,'passed':True},'scale_test':{'size':1.25,'passed':True},'persistent_impact_test':{'frame':2300,'alpha':alpha,'fixed_anchor':anchor,'passed':True},'invalid_drivers':invalid,'outside_driver_targets':outside,'rgba_render':s.render.filepath,'render_pixels':[960,540],'render_seconds':seconds,'source_contains_camera_or_lights':False,'blender':bpy.app.version_string,'no_production_source_used':True}
(P/'evidence/append_sandbox.json').write_text(json.dumps(report,indent=2));print('APPEND_SANDBOX_PASSED',json.dumps(report),flush=True)
