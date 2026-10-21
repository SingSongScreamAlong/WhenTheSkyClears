from pathlib import Path
import zipfile,hashlib,json,ast
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for f in (P/'scripts').glob('*.py'):ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
note=json.loads((P/'evidence/native_note_save_check.json').read_text());assert note['pose_geometry_digest_unchanged']
hf=P/'evidence/FINAL_HANDOFF_v022.json';h=json.loads(hf.read_text());h['native_sha256']=sha(P/h['native']);h['package']='WTSC_Whole_Painted_Pose_Correctives_v022.zip';hf.write_text(json.dumps(h,indent=2))
files=list(P.glob('V022_*.txt'))+list((P/'scripts').glob('*.py'))+list((P/'native').glob('*.blend'))+[f for f in (P/'reference').rglob('*') if f.is_file()]
files+=[f for f in (P/'evidence').glob('*.json') if f.name not in ['PACKAGE_v022.json','DELIVERABLE_MANIFEST_v022.json','native_structure_and_four_poses.json','original_uv_row_values.json']]
files+=[P/'evidence/dcc_agent_workflows.md',P/'evidence/ACTUAL_ENCODED_THREE_SLIDE_REVIEW.jpg']
files+=list((P/'previews').glob('WTSC_v022*'))+list((P/'previews').glob('*/*.png'));files=sorted(set(files))
manifest={'scope':'Two native painted poses only; no continuous animation','files':[{'path':f.relative_to(P).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]}
mf=P/'evidence/DELIVERABLE_MANIFEST_v022.json';mf.write_text(json.dumps(manifest,indent=2));files.append(mf)
archive=P/'WTSC_Whole_Painted_Pose_Correctives_v022.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:
  assert f.resolve().is_relative_to(P.resolve());z.write(f,f.relative_to(P).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;count=len(z.infolist())
p=json.loads((P/'evidence/preview_verification.json').read_text());assert sha(P/'previews/WTSC_v022_Whole_Painted_Pose_Comparison_8s.mp4')==p['sha256'] and p['bytes']<20_000_000
report={'archive':str(archive.resolve()),'bytes':archive.stat().st_size,'sha256':sha(archive),'file_count':count,'crc':'PASS','scripts_ast':'PASS','preview_bytes':p['bytes'],'preview_seconds':p['seconds'],'artistic_status':'PARTIAL_VISUAL_GAIN_UNAPPROVED','production_integration':'NOT_STARTED'}
(P/'evidence/PACKAGE_v022.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

