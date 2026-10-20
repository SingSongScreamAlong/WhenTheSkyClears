from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
A=json.loads((P/'evidence/BOTH_CHARACTERS_AND_WORLD_NATIVE.json').read_text())
for name,r in A['cases'].items():
 print(name,'scene',r['active_scene'],'allscenes',r['all_scenes'],'units',r['unit_system'],r['scale_length'])
 for g in r['rigs']:
  print('RIG',g['name'],g['properties'],'worldscale',g['world_scale'])
  print('BONES',json.dumps({n:round(b['length'],7) for n,b in g['rest_bones'].items()}))
 for o in r['architecture_objects']:print('ARCH',o['name'],o.get('world_bbox_geometry_canvas_not_painted_occupancy'),o['properties'])
 for o in r['ground_objects']:
  if any(t in o['name'].lower() for t in ['ground top','walking path','road','floor']):print('GROUND',o['name'],o.get('world_bbox_geometry_canvas_not_painted_occupancy'),o['properties'])
