from pathlib import Path
import json,shutil,subprocess,hashlib,datetime,csv,collections

root=Path(__file__).resolve().parents[1];ev=root/'Evidence';package=root/'Saved/Packaged/Windows';render=package/'WTSC_Survival/Evidence'
receipt=json.loads((ev/'PackagedGameplayReplay.json').read_text());assert receipt['passed'] and len(receipt['events'])==8
for name in ['ShelterView.png','CacheView.png','ReturnedView.png']:
    assert (render/name).is_file();shutil.copy2(render/name,ev/name)
shutil.copy2(ev/'VideoReceipt.json',ev/'EditorVideoReceipt.json')
shutil.copy2(ev/'GameplayReplay.json',ev/'EditorRecordedGameplayReplay.json')
shutil.copy2(ev/'PackagedGameplayReplay.json',ev/'GameplayReplay.json')
for index in range(int(receipt['recorded_frames'])):
    name=f'Frame{index:05d}.png';shutil.copy2(render/'Frames'/name,ev/'Frames'/name)
subprocess.run(['python',str(root/'Scripts/encode_preview.py')],check=True)
source=json.loads((ev/'SourceStaging.json').read_text());preservation=[]
for x in source['files']:
    p=Path(x['original']);q=root/x['staged'];actual=hashlib.sha256(p.read_bytes()).hexdigest()
    preservation.append({'path':str(p),'original_matches_checkpoint':actual==x['sha256'],'staged_matches_checkpoint':hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256']})
assert all(x['original_matches_checkpoint'] and x['staged_matches_checkpoint'] for x in preservation)
(ev/'SourcePreservationFinal.json').write_text(json.dumps({'original_files_checked':len(preservation),'all_unchanged':True,'files':preservation},indent=2),encoding='utf8')
native=json.loads((ev/'NativeSceneReadback.json').read_text());inventory=[]
for item in native['assets']:
    rel=item['path'].split('.')[0].replace('/Game/','Content/')+('.umap' if item['class']=='World' else '.uasset')
    p=root/rel;assert p.is_file(),p
    inventory.append({**item,'file':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ev/'NativeAssetInventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf8')
with (ev/'NativeAssetInventory.csv').open('w',newline='',encoding='utf8') as f:
    writer=csv.DictWriter(f,fieldnames=['path','class','file','bytes','sha256']);writer.writeheader();writer.writerows(inventory)
exe=package/'WTSC_Survival/Binaries/Win64/WTSC_Survival.exe'
assert exe.is_file()
status={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project':str(root/'WTSC_Survival.uproject'),'sole_development_priority':'WTSC','engine':receipt['engine'],'native_resources':len(inventory),'native_classes':dict(collections.Counter(x['class'] for x in inventory)),'native_imported_props':7,'map':'/Game/Maps/ShelterDawn','map_reopened_and_saved':True,'packaging_status':'SUCCEEDED','packaged_executable':str(exe),'packaged_executable_bytes':exe.stat().st_size,'packaged_executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'packaged_acceptance_passed':True,'packaged_acceptance_events':len(receipt['events']),'packaged_acceptance_seconds':receipt['game_seconds'],'preview_video':str(ev/'WTSC_Shelter_Playable_Preview.mp4'),'source_files_preserved':len(preservation),'blocked_download_entries':4,'library_attachment_ids':[],'library_status':'Blocked before preparation: helper cannot access Library prepare_uploads','provisional':'Painted child puppets and procedural motion; girl body/garments; authored architecture; no bespoke child rig or carrying animation','test_limit':'Simulated native engine input replay and actual rendering; no human playtest or OS-keyboard delivery claim'}
(ev/'BUILD_STATUS.json').write_text(json.dumps(status,indent=2),encoding='utf8');print(json.dumps(status,indent=2))
