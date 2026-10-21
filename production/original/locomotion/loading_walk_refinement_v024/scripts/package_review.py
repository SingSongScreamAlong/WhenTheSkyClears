from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1]
files=[]
for folder in ['native','reference','scripts','evidence']:
    files.extend(p for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_MANIFEST.json','PACKAGE_RESULT.json'])
files.extend(P/p for p in ['README_REVIEW_FIRST.txt','V024_IMPORT_TIMING_AND_EDIT_GUIDE.txt','V024_VISUAL_ASSESSMENT.txt','V024_COAT_REPLACEMENT_ART_BRIEF.txt','V024_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv'])
files.extend(p for p in (P/'previews').iterdir() if p.is_file())
rows=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))]
manifest=P/'evidence/PACKAGE_MANIFEST.json';manifest.write_text(json.dumps({'status':'TECHNICAL_PASS_ART_NOT_PASSED','files':rows},indent=2))
z=P/'WTSC_Continuous_Loading_Walk_v024_REVIEW.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[manifest])):archive.write(p,'loading_walk_refinement_v024/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    for r in rows:
        data=archive.read('loading_walk_refinement_v024/'+r['path']);assert hashlib.sha256(data).hexdigest()==r['sha256']
result={'package':str(z),'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'files':len(rows)+1,'zip_crc_and_every_file_hash':'PASS','raw_review_frame_directories_included':False,'artistically_approved':False}
(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
