import bpy, json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
out = R / 'notes/improvement_v047'
out.mkdir(exist_ok=True)
s = bpy.data.scenes['WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046']
bpy.context.window.scene = s
root = next(o for o in s.objects if o.get('motion_revision') == 'v007_drawn_pose_corrections')
rows = []
for rig in [o for o in root.children_recursive if o.type == 'ARMATURE']:
    objects = []
    for o in rig.children_recursive:
        if o.type != 'MESH':
            continue
        verts = [v.co for v in o.data.vertices]
        objects.append({'name': o.name, 'visible_1901': not o.hide_render,
                        'vertices': len(o.data.vertices), 'faces': len(o.data.polygons),
                        'first_faces': [list(p.vertices) for p in list(o.data.polygons)[:2]],
                        'bounds_local': [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)],
                        'materials': [m.name for m in o.data.materials],
                        'groups': [g.name for g in o.vertex_groups],
                        'modifiers': [m.type for m in o.modifiers],
                        'shape_keys': [k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [],
                        'properties': {k: str(o[k]) for k in o.keys()}})
    row = {'name': rig.name, 'character': rig.get('character'), 'objects': objects,
           'bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local),
                              'matrix': [list(v) for v in b.matrix_local]} for b in rig.data.bones}, 'poses': {}}
    for f in [1843, 1844, 1845, 1846, 1889, 1901, 1920]:
        s.frame_set(f)
        bpy.context.view_layer.update()
        row['poses'][str(f)] = {b.name: {'head': list(b.head), 'tail': list(b.tail),
                                        'matrix': [list(v) for v in b.matrix]} for b in rig.pose.bones}
    rows.append(row)
result = {'rigs': rows,
          'world_objects': [{'name': o.name, 'type': o.type, 'location': list(o.location),
                             'visible': not o.hide_render} for o in s.objects
                            if any(word in o.name.lower() for word in ['path |', 'bank', 'grass', 'foreground'])]}
(out / 'native_inspection.json').write_text(json.dumps(result, indent=2))
print('V047_INSPECTION_COMPLETED', [(r['character'], len(r['objects'])) for r in rows], flush=True)
for row in rows:
    for o in row['objects']:
        if any(w in o['name'] for w in ['original head', 'look toward', 'drawn skin', 'drawn sleeve']):
            print(json.dumps({k: o[k] for k in ['name', 'bounds_local', 'vertices', 'faces', 'first_faces', 'shape_keys']}), flush=True)
    print('HEAD_REST', row['character'], row['bones']['head'], flush=True)
