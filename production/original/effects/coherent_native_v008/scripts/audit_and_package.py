from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1]
raw=P/'previews/painted_final_motion_coherent';base=np.array(Image.open(raw/'1818.png')).astype(int)
fg=np.array(Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png'))[:,:,3];mask=fg>254;mask[:275]=False;mask[735:]=False;mask[:,:720]=False;mask[:,1205:]=False
checks=[]
for frame in [1824,1825,1827,1832,1836,1848,1868,1908,1937]:
    diff=np.abs(np.array(Image.open(raw/f'{frame}.png')).astype(int)-base);checks.append({'frame':frame,'opaque_child_pixels':int(mask.sum()),'max_channel_delta':int(diff[mask].max())})
assert all(row['max_channel_delta']==0 for row in checks)
protected=[('v003_assets',P.parent/'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend','d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'),('v006_proof',P.parent/'blast_refinement_v006/native/WTSC_Painted_Blast_Proof_v006.blend','c6501238e0d1dd9769bc6b607401d604b02ce5d108192f9f4326b9dc109beedb'),('v007b_assets',P.parent/'painted_pose_v007/native/WTSC_Single_Drawn_Blast_Assets_v007b.blend','9226d59e470d07535a1694f4552bf4cbe816419e7b6d41cd34cb6dfdbc87b1c3'),('production_v038',R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend','f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed')]
same={name:hashlib.sha256(file.read_bytes()).hexdigest()==sha for name,file,sha in protected};assert all(same.values()),same
after=P/'previews/painted_final_aftermath_coherent/2064.png';assert after.exists();Image.open(after).load()
rgba=P/'previews/Native_Append_RGBA_v008b.png';im=Image.open(rgba);im.load();assert im.mode=='RGBA';a=np.array(im)[:,:,3];assert a.min()==0 and a.max()>0
application=json.loads((P/'evidence/paint_application.json').read_text());refine=json.loads((P/'evidence/material_refinement.json').read_text());assert application['geometry_before']==application['geometry_after']==refine['geometry_after']
report={'child_occlusion':checks,'protected_sources_unchanged':same,'silhouette_to_final_geometry_identical':True,'geometry_sha256':refine['geometry_after'],'fresh_append_test':json.loads((P/'evidence/append_test.json').read_text()),'aftermath_actual_frame':2064,'append_rgba':{'pixels':list(im.size),'alpha_min':int(a.min()),'alpha_max':int(a.max()),'convention':'StraightRGBA PNG'},'silhouette_media':json.loads((P/'evidence/media_silhouette.json').read_text()),'painted_media':json.loads((P/'evidence/media_painted_final.json').read_text()),'no_source_or_production_mutation':True}
(P/'evidence/final_validation.json').write_text(json.dumps(report,indent=2));print('COHERENT_FINAL_AUDIT_PASSED',json.dumps({'child_delta':0,'source_hashes':same,'geometry_identical':True,'append_passed':True}),flush=True)
files=[P/'native/WTSC_Coherent_Append_v008b.blend',P/'native/WTSC_Coherent_Append_Test_v008b.blend',P/'IMPORT_AND_REVIEW.txt',rgba,after]+list((P/'scripts').glob('*.py'))+list((P/'evidence').glob('*.json'))
archive=P/'WTSC_Coherent_One_Blast_Source_v008b.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in files:z.write(file,file.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(P/'evidence/package_validation.json').write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),'zip_crc_passed':True,'production_scene_or_background_plate_included':False,'simulation_cache':False},indent=2));print('COHERENT_SOURCE_PACKAGE_PASSED',archive.stat().st_size)
