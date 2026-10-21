"""Read-only inspection of the frozen v053 girl wardrobe paint and UVs."""
import bpy
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
SOURCE = ROOT / 'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
rig = bpy.data.objects['V044 GIRL | estimated joint centres']
wardrobe = bpy.data.collections['V046 | restored original painted wardrobe']
out = {}
for obj in wardrobe.objects:
    if obj.parent != rig or obj.get('wardrobe_role') not in ('body', 'sleeve'):
        continue
    d = {'role': obj.get('wardrobe_role'), 'matrix_local': [list(row) for row in obj.matrix_local],
         'materials': [], 'uv': {}, 'bounds': [[min(v.co[j] for v in obj.data.vertices), max(v.co[j] for v in obj.data.vertices)] for j in range(3)]}
    for material in obj.data.materials:
        m = {'name': material.name, 'nodes': []}
        if material.use_nodes:
            for node in material.node_tree.nodes:
                n = {'name': node.name, 'type': node.type}
                if node.type == 'TEX_IMAGE' and node.image:
                    img = node.image
                    n['image'] = {'name': img.name, 'size': list(img.size), 'filepath': img.filepath, 'packed': bool(img.packed_file), 'colorspace': img.colorspace_settings.name}
                    if obj.get('wardrobe_role') == 'body':
                        path = P / 'evidence' / ('SOURCE_%s.png' % node.name.replace(' ', '_').replace('|','_'))
                        path.parent.mkdir(exist_ok=True, parents=True)
                        try:
                            img.save_render(str(path))
                            n['exported'] = str(path)
                        except Exception as exc:
                            n['export_error'] = str(exc)
                m['nodes'].append(n)
        d['materials'].append(m)
    for layer in obj.data.uv_layers:
        u = [x.uv.x for x in layer.data]; v = [x.uv.y for x in layer.data]
        d['uv'][layer.name] = {'range': [min(u),max(u),min(v),max(v)], 'sample': [[round(x.uv.x,4),round(x.uv.y,4)] for x in list(layer.data)[:12]]}
    out[obj.name] = d
(P/'evidence'/'PAINT_INSPECTION.json').write_text(json.dumps(out, indent=2))
print('V055_PAINT_INSPECTED', list(out))
