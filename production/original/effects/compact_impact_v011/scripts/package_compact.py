import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];project=P.parents[1]
checks=[]
for name,expected in [('shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend','f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed'),('effects/rupture_mass_v010/native/WTSC_Earth_Rupture_Append_v010h.blend','504d71606650c36abaebce6797bf3803a9b17ee9035d301e778b0f24f24da8fa'),('effects/ground_impact_v009/native/WTSC_Ground_Debris_Append_v009d.blend','a0d3859e4d4fa793d47195fc5540b25e3412a5dff0e413c3465426ecdae73d48')]:
    actual=hashlib.sha256((project/name).read_bytes()).hexdigest();assert actual==expected,(name,actual);checks.append({'path':name,'sha256':actual,'unchanged':True})
(P/'evidence/source_preservation.json').write_text(json.dumps(checks,indent=2))
report=json.loads((P/'evidence/append_test.json').read_text());assert report['append_geometry_error']==0 and report['offset100_geometry_error']==0
files=[P/'REVIEW_IMPORT.txt']+[P/'native'/n for n in ['WTSC_Compact_Impact_Append_v011.blend','WTSC_Compact_Impact_Append_Test_v011.blend','WTSC_Compact_Impact_Proof_v011.blend']]+sorted((P/'cache/data').glob('*.vdb'))+sorted((P/'scripts').glob('*.py'))
files+=[P/'evidence'/n for n in ['build_compact.json','painted_flash_finish.json','cache_path_repair.json','append_test.json','visual_assessment.json','media_validation.json','source_preservation.json','render_motion_final.json']]
archive=P/'WTSC_Compact_Impact_Source_v011.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:assert f.is_file(),f;z.write(f,'WTSC_Compact_Impact_v011/'+f.relative_to(P).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
paths=[P/'previews/WTSC_Compact_Low_Smoke_Test_v011.mp4',archive,P/'previews/WTSC_Compact_Actual_Frame_Sheet_v011.jpg',P/'previews/WTSC_Compact_Aftermath_v011.png']
manifest=[{'path':str(f.resolve()),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths];(P/'evidence/delivery_manifest.json').write_text(json.dumps(manifest,indent=2))
uploads=[{'local_path':str(f.resolve()),'purpose':'create_library_file','directory_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','library_artifact_type':'other' if i<2 else 'image'} for i,f in enumerate(paths)];(P/'evidence/library_upload_request.json').write_text(json.dumps({'uploads':uploads},indent=2));print(json.dumps({'status':'One compact low-smoke test for review. No production integration.','deliverables':manifest},indent=2))
