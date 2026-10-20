import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parents[1];expected=json.loads((P/'evidence/build_coherent.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);source=P/'native/WTSC_Coherent_Append_v008b.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):
    loaded.collections=['FXv008 | ONE COHERENT NATIVE BLAST'];loaded.node_groups=['FXv008 | FX-only restrained bloom over']
s=bpy.context.scene;s.name='FXv008 | Fresh Append test';asset=loaded.collections[0];s.collection.children.link(asset);root=bpy.data.objects['FXv008 | fixed world impact and controls']
assert not [o for o in asset.all_objects if o.type in {'CAMERA','LIGHT'}]
images=[im for im in bpy.data.images if im.source=='FILE'];assert images and all(im.packed_file for im in images)
left=bpy.data.objects['FXv008 | tracked LEFT pressure mass'];samples=[]
for frame in [1824,1827,1836,1848,1868,1937]:
    s.frame_set(frame);bpy.context.view_layer.update();ev=left.evaluated_get(bpy.context.evaluated_depsgraph_get());samples.append({'frame':frame,'age':root['age'],'top_local':max(v.co.z for v in ev.data.vertices),'anchor':list(root.matrix_world.translation)})
assert samples[2]['top_local']>samples[4]['top_local']*1.25
assert len(set(tuple(row['anchor']) for row in samples))==1
root['start_frame']=2000.;root['speed']=.5;root['size']=1.2;root.update_tag(refresh={'OBJECT'});s.frame_set(2024);bpy.context.view_layer.update();ev=left.evaluated_get(bpy.context.evaluated_depsgraph_get());retime_error=abs(max(v.co.z for v in ev.data.vertices)-samples[2]['top_local']);print('APPEND_CONTROL_DIAGNOSTIC',root['age'],root.scale[:],retime_error,flush=True);assert root['age']==12 and retime_error<.0001;assert abs(root.scale.x-1.2)<.0001
root['start_frame']=1824.;root['speed']=1.;root['size']=1.
root.update_tag(refresh={'OBJECT'})
invalid=[];outside=[];owners=set();ids=set(asset.all_objects)
for ob in asset.all_objects:
    owners.add(ob)
    if ob.type=='MESH':
        if ob.data.shape_keys:owners.add(ob.data.shape_keys)
        owners.update(m.node_tree for m in ob.data.materials if m and m.node_tree)
for owner in owners:
    if owner.animation_data:
        for f in owner.animation_data.drivers:
            if not f.driver.is_valid:invalid.append([owner.name,f.data_path])
            for var in f.driver.variables:
                for target in var.targets:
                    if target.id and target.id not in ids:outside.append(target.id.name)
assert not invalid and not outside,(invalid,outside)
camera_data=bpy.data.cameras.new('Append test camera');camera=bpy.data.objects.new('Append test camera',camera_data);s.collection.objects.link(camera);camera.matrix_world=Matrix(json.loads((P/'evidence/paint_application.json').read_text())['same_camera']);camera_data.lens=100;camera_data.shift_x=-.30000022;camera_data.shift_y=-.2670553;s.camera=camera
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.fps=24;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.frame_start=1818;s.frame_end=1937;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0
s.frame_set(1836);bpy.context.view_layer.update();s.render.filepath=str(P/'previews/Native_Append_RGBA_v008b.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Coherent_Append_Test_v008b.blend'),compress=True)
report={'factory_empty_scene':True,'append_source':source.name,'objects':len(asset.all_objects),'packed_images':[im.name for im in images],'invalid_drivers':invalid,'outside_driver_targets':outside,'continuous_native_geometry_evaluated':samples,'retime_test':{'start':2000,'speed':.5,'frame':2024,'expected_age':12,'top_error':retime_error,'passed':True},'scale_test_passed':True,'fixed_world_anchor':True,'rgba_render':'Native_Append_RGBA_v008b.png','source_has_no_cameras_or_lights':True,'no_production_scene_read':True}
(P/'evidence/append_test.json').write_text(json.dumps(report,indent=2));print('COHERENT_APPEND_TEST_PASSED',json.dumps(report),flush=True)
