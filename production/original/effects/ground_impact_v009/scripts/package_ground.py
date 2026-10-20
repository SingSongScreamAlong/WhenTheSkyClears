import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];project=P.parents[1]
preserve={
 'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend':'f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed',
 'effects/benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend':'d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868',
 'effects/coherent_native_v008/native/WTSC_Coherent_Append_v008b.blend':'c992fb8247a968299350cc8e2f9db4b4ee6f38ae2ede28742d11398036b7fa2e'}
checked=[]
for path,expected in preserve.items():
    actual=hashlib.sha256((project/path).read_bytes()).hexdigest();assert actual==expected,(path,actual);checked.append({'path':path,'sha256':actual,'unchanged':True})
(P/'evidence/preserved_sources_v009d.json').write_text(json.dumps(checked,indent=2))
report=json.loads((P/'evidence/append_test_v009d.json').read_text());assert report['append_position_error']==0 and report['start_frame_offset_test']['max_error']==0
assert report['speed_test']['max_error']<1e-4
files=[P/'REVIEW_AND_IMPORT.txt',P/'STATUS_PROTOTYPE_INCOMPLETE.txt',P/'native/WTSC_Ground_Debris_Append_v009d.blend',P/'native/WTSC_Ground_Debris_Append_Test_v009d.blend']
files+=sorted((P/'scripts').glob('*.py'))
for name in ['build_ground.json','rigid_keys.json','append_test_v009d.json','media_validation_v009d.json','construction_decision.txt','visual_assessment_v009d.json','refinement.json','crater_correction.json','retime_probe.json','preserved_sources_v009d.json','render_v009d_motion.json']:
    files.append(P/'evidence'/name)
archive=P/'WTSC_Ground_First_Prototype_Source_v009d.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:
        assert f.is_file(),f;z.write(f,arcname='WTSC_Ground_First_v009d/'+f.relative_to(P).as_posix())
paths=[P/'previews/WTSC_Ground_First_Impact_Debris_Proof_v009d.mp4',archive,P/'previews/WTSC_Ground_Proof_Actual_Frame_Sheet_v009d.jpg',P/'previews/WTSC_Ground_Proof_Aftermath_v009d.png']
manifest=[{'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths]
(P/'evidence/delivery_manifest_v009d.json').write_text(json.dumps(manifest,indent=2))
uploads=[{'local_path':str(f.resolve()),'purpose':'create_library_file','directory_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','library_artifact_type':'other' if i<2 else 'image'} for i,f in enumerate(paths)]
(P/'evidence/library_upload_request_v009d.json').write_text(json.dumps({'uploads':uploads},indent=2))
print(json.dumps({'prototype_status':'Visual goal incomplete. Native tests pass; no smoke or integration.','archive_files':len(files),'deliverables':manifest},indent=2))
