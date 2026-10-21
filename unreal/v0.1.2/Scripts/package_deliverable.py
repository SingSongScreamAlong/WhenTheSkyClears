from pathlib import Path
import zipfile,json,hashlib,datetime

root=Path(__file__).resolve().parents[1];package=root/'Saved/Packaged/Windows';ev=root/'Evidence';out=root/'Deliverables';out.mkdir(exist_ok=True)
test=json.loads((ev/'PackagedGameplayReplay.json').read_text());assert test['passed'] and len(test['events'])==8
archive=out/'WTSC_Shelter_Study_Win64_v0.1.0.zip'
files=[p for p in sorted(package.rglob('*')) if p.is_file() and p.suffix.lower()!='.pdb' and not any(part in ('Evidence','Saved') for part in p.relative_to(package).parts)]
assert package/'WTSC_Survival.exe' in files
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in files:z.write(p,p.relative_to(package))
    z.writestr('PLAY_WTSC.cmd','@echo off\r\nstart "WTSC Shelter Study" "%~dp0WTSC_Survival.exe" -windowed -ResX=1600 -ResY=900\r\n')
    z.writestr('README_WTSC.txt','WHEN THE SKY CLEARS - SHELTER STUDY v0.1.0\n\nExtract this entire ZIP, then run PLAY_WTSC.cmd or WTSC_Survival.exe.\nA/D or arrows walk. Hold E beside the shop crate to search; E beside the shelter shelves deposits supplies. F/G/H use food/water/bandages beside storage. R starts a fresh day. F5/F9 save/load. Esc pauses.\n\nTested in Unreal 5.8.3. Eight native engine input-replay checks passed in this packaged executable, including reset and save/readback. This is not a human playtest or proof of OS keyboard delivery.\n\nThe age-ten leads use established painted faces on provisional puppets with procedural motion. Girl body/garments, architecture and art/animation refinement remain unfinished. One shelter and one shop; no campaign or combat. Audio is not authored in this first study.\n\nSeven Poly Haven CC0 prop models are incorporated. Fab/Mixamo entries were not acquired. Quaternius/KayKit animation downloads remain source candidates and are not imported/retargeted in this build.\n')
    z.write(ev/'PackagedGameplayReplay.json','AcceptanceReceipt.json')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
h=hashlib.sha256()
with archive.open('rb') as f:
    for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':str(archive),'bytes':archive.stat().st_size,'sha256':h.hexdigest(),'zip_crc_verified':True,'runtime_files':len(files),'runtime_uncompressed_bytes':sum(p.stat().st_size for p in files),'debug_pdb_and_test_frame_dumps_excluded':True,'tested_package':str(package),'packaged_acceptance_passed':True}
(ev/'PlayableArchiveReceipt.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(json.dumps(record,indent=2))
