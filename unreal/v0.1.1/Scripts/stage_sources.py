"""Copy authorized sources into this separate project; never edit the originals."""
from pathlib import Path
import hashlib, json, shutil, datetime, os

ROOT=Path(__file__).resolve().parents[1]
COLLECTION=Path(os.environ.get('WTSC_ASSET_LIBRARY', str(ROOT.parent/'WTSC_Survival_Game_Assets')))
REPOSITORY=next(p for p in ROOT.parents if (p/'game/project.godot').is_file())
OLD=REPOSITORY/'game/assets'
records=[]
def stage(src,dst,source,rights):
    assert src.is_file(),src
    dst.parent.mkdir(parents=True,exist_ok=True)
    a=hashlib.sha256(src.read_bytes()).hexdigest()
    shutil.copy2(src,dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==a
    records.append({'original':str(src),'staged':str(dst.relative_to(ROOT)),'bytes':dst.stat().st_size,'sha256':a,'source_url':source,'rights_evidence':rights,'native_unreal_imported':False})

for folder in sorted((COLLECTION/'PolyHaven').iterdir()):
    if not folder.is_dir():continue
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.suffix.lower() in ('.gltf','.bin','.jpg','.png'):
            stage(p,ROOT/'SourceAssets'/'PolyHaven'/folder.name/p.relative_to(folder),'https://polyhaven.com/a/'+folder.name,'CC0; ../WTSC_Survival_Game_Assets/evidence/polyhaven_license.txt')
for category,name in [('characters','boy_atlas.png'),('characters','girl_profile.png'),('environments','Village_Empty_v001.png')]:
    stage(OLD/category/name,ROOT/'SourceAssets'/'EstablishedWTSC'/name,'Existing user WTSC production asset; local authorized reuse','Preserve original face/profile direction; no external source upload')
e=ROOT/'Evidence';e.mkdir(exist_ok=True)
(e/'SourceStaging.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':records,'copied_files':len(records),'copied_bytes':sum(x['bytes'] for x in records),'originals_changed':False,'native_import_status':'NOT_RUN'},indent=2),encoding='utf8')
print(json.dumps({'staged_files':len(records),'staged_bytes':sum(x['bytes'] for x in records),'native_import_status':'NOT_RUN'}))
