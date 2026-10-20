from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=P.parents[1]/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend'
previous=P.parent/'compact_impact_v011/native/WTSC_Compact_Impact_Append_v011.blend'
sources={'production_v038':{'path':str(original),'sha256':H(original),'matches_before':H(original)=='f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed'},'previous_v011_append':{'path':str(previous),'sha256':H(previous),'matches_before':H(previous)=='8633f95653eb867d1fbf6b6b0211fe028e37711800919df34d919373b4d58861'}}
assert all(v['matches_before'] for v in sources.values())
(P/'evidence/source_preservation.json').write_text(json.dumps(sources,indent=2))
review={'status':'Review candidate; artistic acceptance pending; no production integration.','visually_inspected':'Actual consecutive onset keys, actual contact sheet frames 14–25,28,30,32,72, full shot frames 8,9,10,22,30,72.','continuous_speed_playback_observed':False,'changes':'Distinct native contour exposures grow outward then tear apart. Seven differently sized debris pieces, terrain alpha sampled contact heights, four brief contact drawing events, broken soil marks. No volume or plume.','remaining_artistic_limits':['Onset remains angular/star-like and more graphic than the painted scene.','Small contact puffs remain subtle at full shot size.','Terrain alignment and geometry are verified, but perceived grounded weight and impact force need independent artistic review.'],'tutorial_limit':'No verified tutorial motion was accessible. This construction is our proposed workflow, not a demonstrated reproduction.','scope':'One isolated compact impact revision following v011 review. Earlier broad FX prototypes are preserved; a production-ready broad pack is not claimed.'}
(P/'evidence/artistic_review_status.json').write_text(json.dumps(review,indent=2))
files=[]
for folder in ['native','scripts','evidence','rgba']:
    files += [p for p in (P/folder).rglob('*') if p.is_file() and p.suffix not in {'.blend1','.pyc'} and '__pycache__' not in p.parts and not p.name.startswith('library_')]
files += [P/'IMPORT_AND_REVIEW.txt']
files += [p for p in (P/'previews').glob('*') if p.is_file() and p.suffix in {'.jpg','.mp4'}]
manifest={str(p.relative_to(P)):{'bytes':p.stat().st_size,'sha256':H(p)} for p in files}
(P/'evidence/package_manifest.json').write_text(json.dumps(manifest,indent=2));files.append(P/'evidence/package_manifest.json')
dest=P/'WTSC_Drawn_Compact_Impact_Review_Source_v012.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sorted(set(files)):z.write(p,'WTSC_Drawn_Compact_Impact_v012/'+str(p.relative_to(P)).replace('\\','/'))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
result={'path':str(dest),'bytes':dest.stat().st_size,'sha256':H(dest),'file_count':len(set(files)),'crc_test':'passed'}
(P/'evidence/package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
