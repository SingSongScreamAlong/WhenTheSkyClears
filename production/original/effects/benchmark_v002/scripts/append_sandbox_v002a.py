"""Append-only technical check in a new scene; never loads production scenes."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]
source = P / 'native/WTSC_Hero_Eruption_Collection_v002a.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'FX_APPEND_TEST_v002a | isolated technical sandbox'
with bpy.data.libraries.load(str(source), link=False) as (available, requested):
    requested.collections = ['FXv002 | Detailed painterly ground eruption']
collection = requested.collections[0]
scene.collection.children.link(collection)
root = bpy.data.objects['FXv002 | fixed ground origin and controls']
# Complete the collection's exposed uniform size control; its default of one
# preserves the already rendered benchmark. Production files are never loaded.
for axis in range(3):
    f = root.driver_add('scale', axis)
    f.driver.expression = 'max(0.01,s)'
    variable = f.driver.variables.new()
    variable.name = 's'
    variable.type = 'SINGLE_PROP'
    variable.targets[0].id = root
    variable.targets[0].data_path = '["size"]'
root['size'] = 1.0
root['status'] = 'Unaccepted artistic benchmark. Append and driver checks are technical only.'
bpy.data.libraries.write(str(source), {collection}, fake_user=True, compress=True)

root.location = (0, 0, 0)
root['start_frame'] = 10.0
root['size'] = 1.2
root.update_tag()
states = []
for frame in [0, 10, 22, 60]:
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    states.append({'frame': frame, 'age': root['age'], 'position': list(root.matrix_world.translation), 'scale': list(root.scale)})
    assert abs(root['age'] - (frame - 10)) < 1e-5
    assert max(abs(x - 1.2) for x in root.scale) < 1e-5
    assert root.matrix_world.translation.length < 1e-6

ids = list(collection.all_objects)
ids += [o.data for o in collection.all_objects if o.data is not None]
ids += list(bpy.data.shape_keys)
ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
bad = []
for owner in ids:
    if owner.animation_data:
        bad += [{'id': owner.name, 'path': f.data_path, 'expression': f.driver.expression} for f in owner.animation_data.drivers if not f.driver.is_valid]
assert not bad, bad
images = [{'name': im.name, 'packed': bool(im.packed_file), 'pixels': list(im.size), 'alpha': im.alpha_mode} for im in bpy.data.images if im.type != 'RENDER_RESULT']
assert len(images) == 2 and all(im['packed'] for im in images), images
assert all(o.parent == root for o in collection.all_objects if o != root)

camera_data = bpy.data.cameras.new('Sandbox camera | +Y')
camera = bpy.data.objects.new(camera_data.name, camera_data)
scene.collection.objects.link(camera)
camera.location = (0, -18, 2.0)
camera.rotation_euler = Vector((0, 1, 0)).to_track_quat('-Z', 'Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 6.5
scene.camera = camera
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 16
scene.render.threads_mode = 'FIXED'
scene.render.threads = 2
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.film_transparent = True
scene.render.image_settings.media_type = 'IMAGE'
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.frame_start = 0
scene.frame_end = 77
scene.frame_set(22)
scene.render.filepath = str(P / 'previews/Native_Append_Test_RGBA_v002a.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P / 'native/WTSC_FX_Append_Test_v002a.blend'), compress=True)
bpy.ops.render.render(write_still=True)
production = json.loads((P / 'evidence/benchmark_build.json').read_text())
report = {
    'blender': bpy.app.version_string,
    'appended_source': str(source),
    'collection': collection.name,
    'objects': len(collection.all_objects),
    'packed_dependencies': images,
    'samples': states,
    'invalid_drivers': bad,
    'all_children_parented_to_anchor': True,
    'uniform_size_control': 'Connected to native anchor scale; default one leaves benchmark unchanged.',
    'source_unchanged': hashlib.sha256(Path(production['source']).read_bytes()).hexdigest() == production['source_sha256'],
    'artistic_status': 'Technical append/render success does not establish cinematic motion quality.',
}
assert report['source_unchanged']
(P / 'evidence/append_test_v002a.json').write_text(json.dumps(report, indent=2))
print('FX_APPEND_TEST_COMPLETE', json.dumps(report), flush=True)
