"""Verify current preserved checkpoint hashes without repeating completed movie QC."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];old=json.loads((R/'notes/world_v016/full_completed_v037.json').read_text());editable=json.loads((R/'notes/world_v016/final_editable_v038.json').read_text());study=json.loads((R/'notes/world_v016/camp_comparison_completed_v039.json').read_text())
checks=[(old['source'],old['source_sha256']),(old['movie'],old['movie_sha256']),(old['viewing_copy']['path'],old['viewing_copy']['sha256']),(editable['editable'],editable['editable_sha256']),(study['source'],study['source_sha256']),(study['comparison'],study['comparison_sha256'])];verified={}
for path,expected in checks:
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert actual==expected,(path,actual);verified[path]=actual
p=R/'notes/world_v016/full_verification_v040.json';qa=json.loads(p.read_text());qa['preserved_checkpoints_v037_v038_v039']=verified;p.write_text(json.dumps(qa,indent=2));print('PRESERVED_CHECKPOINT_HASHES_VERIFIED',len(verified),flush=True)
