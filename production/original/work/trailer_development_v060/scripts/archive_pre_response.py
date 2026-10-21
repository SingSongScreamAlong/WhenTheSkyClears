from pathlib import Path
import json,shutil
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060')
assert b'V060_UHD_WITNESS_COMPLETE' in (O/'evidence/render_sequences.log').read_bytes().replace(bytes([0]),b'')
r=json.loads((O/'evidence/DUAL_SEQUENCE_RENDER.json').read_text());assert r['actual_rendered_frames']==120
for name in ['frames_world','frames_title','native4K']:
 A=O/'previews'/name;B=O/'previews'/('pre_response_'+name)
 assert not B.exists();A.rename(B)
shutil.copy2(O/'native/WTSC_First_Danger_Trailer_Development_v060.blend',O/'reference/PRESERVED_PRE_RESPONSE_WORLD_v060.blend')
shutil.copy2(O/'evidence/DUAL_SEQUENCE_RENDER.json',O/'evidence/PRE_RESPONSE_DUAL_SEQUENCE_RENDER.json')
shutil.copy2(O/'evidence/WORLD_BUILD.json',O/'evidence/PRE_RESPONSE_WORLD_BUILD.json')
print('PRE_RESPONSE_EVIDENCE_PRESERVED',flush=True)
