import json,zipfile,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];files=[]
for folder in ['native','scripts','evidence','reference']:
 for p in (P/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'library_helpers' not in p.parts and p.name!='dcc_agent_workflows.md' and p.name!='PACKAGE_v020.json' and not p.name.endswith('.blend1'):files.append(p)
files.extend([P/'V020_REFERENCE_TO_CHILD_REPORT.txt',P/'V020_IMPORT_AND_SOURCE_TIME_GUIDE.txt',P/'V020_CORRECTIVES_NOT_STARTED.csv'])
files.extend(p for p in (P/'previews').iterdir() if p.is_file() and p.name.startswith('WTSC_v020_') and p.suffix in ['.jpg','.mp4'])
archive=P/'WTSC_Leaves_Reference_Child_Eight_Pose_Checkpoint_v020.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in sorted(set(files)):z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:bad=z.testzip();count=len(z.namelist())
out={'path':str(archive.resolve()),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'file_count':count,'bad_zip_member':bad,'native_sha256':hashlib.sha256((P/'native/WTSC_Leaves_Reference_Child_Eight_Poses_v020.blend').read_bytes()).hexdigest(),'contents':'Eight-pose primary native; cached original source native; byte-copied project-owned rig/boot bases for isolated rebuild; scripts/evidence/source timing; comparison movie/boards and candid corrective list. Raw FBX and intermediate renders/helper runtime excluded.'};(P/'evidence/PACKAGE_v020.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
if bad:raise RuntimeError('ZIP integrity failure')
