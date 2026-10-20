import json
from pathlib import Path
P=Path(__file__).resolve().parents[1];E=P/'evidence';f=E/'FINAL_HANDOFF.json';r=json.loads(f.read_text());a=json.loads((E/'LIBRARY_VERIFIED_LIBRARY_REVIEW_ARCHIVE_CREATE_RESULT.json').read_text());assert len(a)==1 and a[0]['metadata_verified'];r['archive_library_file']=a[0];f.write_text(json.dumps(r,indent=2));print('v050 candidate delivered privately: two verified static proofs, two verified actual movies and verified native package. No technical blocker. All our Blender jobs exited.')
