from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];A=json.loads((P/'evidence/BOTH_CHARACTERS_AND_WORLD_NATIVE.json').read_text())
for o in A['cases']['pair_v007']['object_inventory']:
 if o['type']=='MESH' and ('GIRL' in o['name']) and not o['hide_render']:print(o['name'])
