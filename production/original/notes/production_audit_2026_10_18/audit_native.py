"""Open one Blender project without saving; emit independent structural evidence."""
import bpy
import collections
import hashlib
import json
import sys
from pathlib import Path

source, target = map(Path, sys.argv[sys.argv.index('--') + 1:])
before = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)

def curves(block):
    ad = getattr(block, 'animation_data', None)
    action = ad.action if ad else None
    if not action:
        return []
    return [f for layer in action.layers for strip in layer.strips
            for bag in strip.channelbags for f in bag.fcurves]

def animation(block):
    fc = curves(block)
    return {'channels': len(fc), 'keys': sum(len(f.keyframe_points) for f in fc),
            'key_range': [min((k.co.x for f in fc for k in f.keyframe_points), default=None),
                          max((k.co.x for f in fc for k in f.keyframe_points), default=None)]}

def packed(block):
    return bool(getattr(block, 'packed_file', None) or getattr(block, 'packed_files', None))

images = [{'name': i.name, 'source': i.source, 'size': list(i.size), 'packed': packed(i),
           'path': i.filepath,
           'external_path_exists': Path(bpy.path.abspath(i.filepath)).is_file() if i.filepath else None,
           'users': i.users}
          for i in bpy.data.images if i.source in {'FILE', 'TILED', 'SEQUENCE', 'MOVIE'}]
scene_rows = []
for scene in bpy.data.scenes:
    bpy.context.window.scene = scene
    scene_rows.append({'name': scene.name, 'frames': [scene.frame_start, scene.frame_end],
                       'fps': scene.render.fps / scene.render.fps_base,
                       'output': [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
                       'output_path': scene.render.filepath, 'engine': scene.render.engine,
                       'color_view': scene.view_settings.view_transform,
                       'objects': len(scene.objects), 'types': dict(collections.Counter(o.type for o in scene.objects)),
                       'camera': scene.camera.name if scene.camera else None,
                       'markers': [{'name': m.name, 'frame': m.frame} for m in scene.timeline_markers],
                       'strips': [{'name': s.name, 'type': s.type, 'start': s.frame_final_start,
                                   'end_exclusive': s.frame_final_end,
                                   'scene': s.scene.name if s.type == 'SCENE' and s.scene else None,
                                   'sound': s.sound.filepath if s.type == 'SOUND' and s.sound else None,
                                   'sound_packed': packed(s.sound) if s.type == 'SOUND' and s.sound else None}
                                  for s in scene.sequence_editor.strips] if scene.sequence_editor else []})
    # Evaluate only a few representative frames; no render, save or timeline edits persist.
    for f in [scene.frame_start, (scene.frame_start + scene.frame_end) // 2, scene.frame_end]:
        scene.frame_set(f)
        bpy.context.view_layer.update()

blocks = []
for group in [bpy.data.objects, bpy.data.materials, bpy.data.meshes, bpy.data.shape_keys,
              bpy.data.scenes, bpy.data.node_groups, bpy.data.worlds, bpy.data.lights, bpy.data.cameras]:
    for block in group:
        blocks.append(block)
        if getattr(block, 'node_tree', None):
            blocks.append(block.node_tree)
driver_rows = []
seen = set()
for block in blocks:
    key = block.as_pointer()
    if key in seen:
        continue
    seen.add(key)
    ad = getattr(block, 'animation_data', None)
    for driver in ad.drivers if ad else []:
        missing = [{'name': v.name, 'id_type': t.id_type, 'path': t.data_path}
                   for v in driver.driver.variables for t in v.targets
                   if v.type in {'SINGLE_PROP', 'TRANSFORMS', 'ROTATION_DIFF', 'LOC_DIFF'} and t.id is None]
        driver_rows.append({'owner': block.name, 'path': driver.data_path,
                            'is_valid_after_sample_evaluation': driver.is_valid,
                            'expression': driver.driver.expression, 'missing_targets': missing})

actors = []
for o in bpy.data.objects:
    if o.type == 'ARMATURE' or o.type == 'GREASEPENCIL':
        row = {'name': o.name, 'type': o.type, 'object_animation': animation(o),
               'data_animation': animation(o.data), 'hide_render': o.hide_render}
        if o.type == 'ARMATURE':
            row['bones'] = len(o.data.bones)
        else:
            row['layers'] = [{'name': layer.name, 'drawing_frames': [f.frame_number for f in layer.frames]}
                             for layer in o.data.layers]
        actors.append(row)

controller = next((o for o in bpy.data.objects if 'charcoal_progress' in o), None)
color_samples = []
if controller:
    sc = next(s for s in bpy.data.scenes if controller.name in s.objects)
    bpy.context.window.scene = sc
    for f in [1, 433, 841, 1201, 1609, 1921, 2161, 2305, 2401]:
        sc.frame_set(f)
        bpy.context.view_layer.update()
        color_samples.append({'frame': f, 'progress': controller['charcoal_progress']})

result = {'file': str(source), 'blender': bpy.app.version_string, 'sha256': before,
          'scenes': scene_rows, 'images': images,
          'unpacked_missing_images': [i for i in images if i['users'] and not i['packed'] and not i['external_path_exists']],
          'libraries': [{'path': lib.filepath, 'exists': Path(bpy.path.abspath(lib.filepath)).exists()} for lib in bpy.data.libraries],
          'sounds': [{'name': s.name, 'packed': packed(s), 'path': s.filepath} for s in bpy.data.sounds],
          'fonts': [{'name': f.name, 'packed': packed(f), 'path': f.filepath} for f in bpy.data.fonts],
          'actors': actors, 'actions': len(bpy.data.actions), 'driver_count': len(driver_rows),
          'drivers_with_missing_targets': [r for r in driver_rows if r['missing_targets']],
          'invalid_drivers_after_samples': [r for r in driver_rows if not r['is_valid_after_sample_evaluation']],
          'color_controller': controller.name if controller else None, 'color_samples': color_samples,
          'source_sha256_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == before,
          'inspection_limits': 'Read-only native sample; auto-run source scripts disabled. No claim of all-frame render, playback quality, or artistic approval.'}
target.write_text(json.dumps(result, indent=2), encoding='utf-8')
print('AUDIT_NATIVE_OK', target.name, len(scene_rows), len(images), len(driver_rows), flush=True)
