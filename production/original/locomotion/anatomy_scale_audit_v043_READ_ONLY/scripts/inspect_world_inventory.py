from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[1];A=json.loads((P/'evidence/BOTH_CHARACTERS_AND_WORLD_NATIVE.json').read_text())
for label in ['world_v046','world_v058']:
 r=A['cases'][label];print(label,r['active_scene'],len(r['object_inventory']),'rigs',len(r['rigs']))
 for o in r['object_inventory']:
  if re.search('pair|child|ground|road|path|village|school|facade|v049',o['name'],re.I) and o['type'] not in ['FONT','CURVE']:
   if re.search('tick|needle|rubble|wisp|fire|ember|smoke|grass|cap|shadow',o['name'],re.I):continue
   print(o['name'],'type',o['type'],'hide',o['hide_render'],'size',[round(x,4) for x in o['dimensions']],'xyz',[round(x,4) for x in o['location']])
 for f,d in r['frames'].items():
  print('FRAME',f,'cam',d['camera']['name'] if d['camera'] else None,'cam_xyz',d['camera']['world_translation'] if d['camera'] else None)
  for g in d['rigs']:print('RIG',g['name'],'xyz',g['world_translation'],'scale',g['world_scale'])
  print('GROUND_HITS',json.dumps(d['ground_raycast_Y0']))
