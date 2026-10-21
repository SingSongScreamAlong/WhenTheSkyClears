from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=P.parents[1]/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend';previous=P.parent/'drawn_impact_v012/native/WTSC_Drawn_Impact_Append_v012.blend'
sources={}
for key,p,expect in [('production_v038',original,'f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed'),('previous_v012_append',previous,'282fc921de1c501a042e2bedba7ad8080ccd76971523bc5d6f2894a286e6b30c')]:
    digest=H(p);sources[key]={'path':str(p),'sha256':digest,'matches_before':digest==expect}
assert all(v['matches_before'] for v in sources.values());(P/'evidence/source_preservation.json').write_text(json.dumps(sources,indent=2))
review=json.loads((P/'evidence/artistic_review_status.json').read_text());review.update({'status':'Authored, rendered, actual keys inspected and native-tested. Independent artistic review pending; grounded weight/contact-puff readability remains unresolved.','visually_inspected':'Full shot onset 9, contact 24 and actual onset/contact comparison sheets, including four exact contact-peak sequences.','contact_correction':'B/C contours 1.15x wider and 1.65x higher. Peak B exposure increased to three frames, C shifted to two following frames. Local cues remain subtle in the wide shot.','scope':'One same-shot compact impact correction only. No broad pack expansion or production integration.','software_blocker':None})
(P/'evidence/artistic_review_status.json').write_text(json.dumps(review,indent=2))
files=[]
for folder in ['native','scripts','evidence','rgba']:
    files += [p for p in (P/folder).rglob('*') if p.is_file() and p.suffix not in {'.blend1','.pyc'} and '__pycache__' not in p.parts and not p.name.startswith('library_') and p.name not in ['package_manifest.json','package_validation.json']]
files += [P/'IMPORT_AND_REVIEW.txt']+[p for p in (P/'previews').glob('*') if p.is_file() and p.suffix in {'.jpg','.mp4'}]
manifest={str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':H(p)} for p in files};(P/'evidence/package_manifest.json').write_text(json.dumps(manifest,indent=2));files.append(P/'evidence/package_manifest.json')
dest=P/'WTSC_Drawn_Compact_Impact_Review_Source_v013.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sorted(set(files)):z.write(p,'WTSC_Drawn_Compact_Impact_v013/'+str(p.relative_to(P)).replace('\\','/'))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
result={'path':str(dest),'bytes':dest.stat().st_size,'sha256':H(dest),'file_count':len(set(files)),'crc_test':'passed'};(P/'evidence/package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
