from pathlib import Path
import json,hashlib,zipfile,ast
P=Path(__file__).resolve().parents[1]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for f in (P/'scripts').glob('*.py'):ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
preview=json.loads((P/'evidence/preview_verification.json').read_text());movie=P/'previews/WTSC_v021_Support_Pose_Correction_and_Art_Study_5s.mp4'
assert sha(movie)==preview['sha256'] and movie.stat().st_size<20_000_000
ann=json.loads((P/'evidence/native_annotation_check.json').read_text());assert all(r['pose_change_m']==0 for r in ann)
hf=P/'evidence/FINAL_HANDOFF_v021.json';handoff=json.loads(hf.read_text());handoff['native_sha256']={f.name:sha(f) for f in (P/'native').glob('*.blend')};handoff['package']='WTSC_Child_Coherent_Poses_and_Art_Study_v021.zip';handoff['native_annotation_pose_change_m']=0.;hf.write_text(json.dumps(handoff,indent=2))
files=list(P.glob('V021_*.txt'))+list(P.glob('V021_*.csv'))+list((P/'scripts').glob('*.py'))+list((P/'native').glob('*.blend'))+[f for f in (P/'reference').rglob('*') if f.is_file()]
files +=[f for f in (P/'evidence').glob('*.json') if f.name not in ['initial_direction_only_solution.json','PACKAGE_v021.json','DELIVERABLE_MANIFEST_v021.json']]
files +=[P/'evidence/dcc_agent_workflows.md',P/'evidence/ENCODED_UNIQUE_SLIDE_REVIEW.jpg']
files +=list((P/'previews').glob('WTSC_v021*'))
for sub in ['SOURCE_CLOSE','SOURCE_SHOT','CHILD_SKELETON_CLOSE','CHILD_SKELETON_SHOT','PAINTED_CLOSE','PAINTED_SHOT','ART_VARIANT']:
 files+=list((P/'previews'/sub).glob('*.png'))
files=sorted(set(files))
manifest={'scope':'Bounded eight-pose correction and separate one-pose art variant; no continuous cycle','files':[{'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]}
mf=P/'evidence/DELIVERABLE_MANIFEST_v021.json';mf.write_text(json.dumps(manifest,indent=2));files.append(mf)
out=P/'WTSC_Child_Coherent_Poses_and_Art_Study_v021.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:
  assert f.resolve().is_relative_to(P.resolve())
  z.write(f,f.relative_to(P).as_posix())
with zipfile.ZipFile(out) as z:
 bad=z.testzip();count=len(z.infolist());assert bad is None
report={'path':str(out.resolve()),'bytes':out.stat().st_size,'sha256':sha(out),'file_count':count,'crc_test':'PASS','python_scripts_ast':'PASS','preview_under_20mb':True,'native_notes_did_not_change_poses':True,'scope':'Eight selected phases plus duplicate bookend; art corrective one passing pose; continuous animation/integration NOT_STARTED'}
(P/'evidence/PACKAGE_v021.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))

