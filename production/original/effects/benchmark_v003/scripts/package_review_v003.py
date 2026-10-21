import json,hashlib,zipfile,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1]
# Original byte-for-byte dependencies, copied only into this new effects folder.
for name in ['Hero_Explosion_Paint_v002.png','Ground_Dust_Paint_v002.png']:
    target=P/'assets'/name
    if not target.exists():shutil.copy2(P.parent/'benchmark_v002/assets'/name,target)
names=['IMPORT_AND_REVIEW_v003.txt','native/WTSC_Evolving_Eruption_Collection_v003.blend',
       'assets/Cold_Smoke_Atlas_4Forms_v003.png','assets/Hero_Explosion_Paint_v002.png','assets/Ground_Dust_Paint_v002.png',
       'scripts/build_evolution_v003.py','scripts/render_evolution_v003.py','scripts/validate_append_v003.py','scripts/finish_review_v003.py',
       'evidence/evolution_build_v003.json','evidence/append_validation_v003.json','evidence/media_validation_v003.json','evidence/visual_audit_v003.json',
       'evidence/render_motion_v003.json','evidence/reuse_and_budget_v003.json','evidence/smoke_atlas_prompt.txt']
manifest={'status':'Targeted defects corrected; separate integrated-proof candidate, not overall cinematic acceptance.','files':[],'no_lights':True,'no_production_files_modified':True}
for name in names:
    data=(P/name).read_bytes();manifest['files'].append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(P/'evidence/package_manifest_v003.json').write_text(json.dumps(manifest,indent=2))
target=P/'WTSC_Evolving_Eruption_Source_v003.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in names:z.write(P/name,arcname=name)
    z.write(P/'evidence/package_manifest_v003.json',arcname='evidence/package_manifest_v003.json')
with zipfile.ZipFile(target) as z:assert z.testzip() is None
report={'path':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'zip_crc_test':'passed','members':len(names)+1,'excluded':'Production scene files, held scene plate/maps, caches, raw120frames, base64 transfer and uncalled reference-render script. Native append-test scene is retained locally; packed source collection is included.'}
(P/'evidence/package_validation_v003.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
