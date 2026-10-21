"""Local release receipt for the separately built, tested v0.1.1 refinement."""
from pathlib import Path
import collections, datetime, hashlib, json, zipfile

R=Path(__file__).resolve().parents[1]
E=R/'Evidence'
baseline=R.parent/'WTSC_Survival_Prototype'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,obj):
    (E/name).write_text(json.dumps(obj,indent=2),encoding='utf8')
old=json.loads((baseline/'Evidence/EditableProjectCheckpoint.json').read_text(encoding='utf-8-sig'))
changed=[x['file'] for x in old['files'] if sha(baseline/x['file'])!=x['sha256']]
assert not changed,changed
raw=json.loads((E/'Baseline_SourceStaging.json').read_text(encoding='utf-8-sig'))
sources=[]
for x in raw['files']:
    original=Path(x['original']);staged=R/x['staged']
    sources.append({'original':str(original),'staged':str(staged),'sha256':x['sha256'],'original_unchanged':sha(original)==x['sha256'],'refinement_copy_matches':sha(staged)==x['sha256']})
assert all(x['original_unchanged'] and x['refinement_copy_matches'] for x in sources)
write('SourceAndBaselinePreservation.json',{'baseline_files_verified':len(old['files']),'baseline_changed':changed,'raw_sources_verified':len(sources),'files':sources})
test=json.loads((E/'PackagedGameplayReplay.json').read_text(encoding='utf-8-sig'))
video=json.loads((E/'ActualVideoReceipt.json').read_text())
assert test['passed'] and len(test['events'])==10 and video['full_decode_passed']
native=json.loads((E/'NativeSceneReadback.json').read_text())
pkg=R/'Saved/Packaged/Windows'
(pkg/'WTSC_README.txt').write_text('When The Sky Clears - Shelter Study v0.1.1\n\nLaunch WTSC_Survival.exe. A/D or arrows walk; hold E at the shop crate; E by shelter shelves unpacks. F meal, G water, H bandage, Tab framing, R reset, F5 save, F9 load, Esc pause.\n\nBounded provisional prototype: authored 2D cutout interpolation and foot IK, not mocap or hand-drawn frame animation. Companion presence only. Collapsed upstairs is inaccessible. No final cinematic quality claim.\n\nProps: seven Poly Haven CC0 models (https://polyhaven.com/license). Established character/village artwork belongs to the existing WTSC production. Engine third-party notices remain with the runtime. No Quaternius or KayKit animation is used.\n',encoding='utf8')
deliver=R/'Deliverables';deliver.mkdir(exist_ok=True)
archive=deliver/'WTSC_Shelter_Study_Win64_v0.1.1.zip'
files=[p for p in sorted(pkg.rglob('*')) if p.is_file() and p.suffix.lower()!='.pdb' and not {'Evidence','Saved'}.intersection(p.relative_to(pkg).parts)]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(pkg).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
release={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'0.1.1','engine':test['engine'],'project':str(R/'WTSC_Survival.uproject'),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'runtime_file_count':len(files),'runtime_uncompressed_bytes':sum(p.stat().st_size for p in files),'archive_crc_verified':True,'packaged_replay_passed':True,'acceptance_events':10,'game_seconds':test['game_seconds'],'actual_capture_fps':video['actual_capture_fps'],'actual_runtime_fps_including_capture':video['actual_runtime_fps_including_capture'],'video_decoded_frames':video['decoded_video_frames'],'native_asset_classes':dict(collections.Counter(x['class'] for x in native['assets'])),'imported_prop_references':len(native['prop_meshes']),'baseline_files_unchanged':len(old['files']),'raw_sources_unchanged':len(sources),'remaining_limitations':['Provisional interpolated cutouts, not finished cinematic child animation','Companion presence only; no following or carrying behavior','Collapsed upper floor deliberately inaccessible; no vertical traversal','No audio','Simulated native engine key events, not a human or OS-keyboard playtest','Downloaded skeletal animations incompatible directly with static cutout artwork; none applied']}
write('Release_v0_1_1.json',release)
write('BUILD_STATUS.json',{'utc':release['utc'],'version':'0.1.1','stage':'built, native scene reopened, packaged gameplay passed, actual video fully decoded','validated':True,'editor_build':'Succeeded','native_refinement':'Succeeded, 0 errors and 0 warnings on final commandlet','win64_package':'Succeeded','packaged_replay_events':10,'packaged_replay_passed':True,'actual_capture_fps':video['actual_capture_fps'],'actual_runtime_fps_including_capture':video['actual_runtime_fps_including_capture'],'source_and_baseline_preservation':'Verified','limitations':release['remaining_limitations']})
doc=f'''# v0.1.1 verification

Built with Unreal {test['engine']} using installed Visual Studio Build Tools. The final native map was saved, reopened and read back: {len(native['assets'])} resources and seven real imported static-mesh prop references. The final material/map commandlet returned zero errors and zero warnings.

The packaged Windows executable passed all ten checks in {test['game_seconds']:.2f} game seconds: initial storage/cache; walk to cache; crouched reach with grounded feet; finite search; no duplicated loot; visible deposit before inventory commit; return/deposit; save/readback; food/water consumption; fresh reset. This uses real native engine simulated key events, not OS keyboard delivery or a human playtest. Full structured evidence is in PackagedGameplayReplay.json. Preliminary run evidence is retained in Pass1.

Actual viewport capture produced {video['source_jpeg_count']} unique engine-frame samples at {video['actual_capture_fps']:.2f} samples per second, {video['width']}×{video['height']}. Runtime averaged {video['actual_runtime_fps_including_capture']:.2f} FPS during recording. The MP4 preserves measured wall-clock timing as variable-rate playback. No generated intermediate frames or duplicate-frame smoothing were added. Full decode returned {video['decoded_video_frames']} frames in {video['decoded_seconds']:.3f} seconds. The target was 30Hz; the measured rate is reported separately. Exact frame timestamps, engine frame IDs, sizes and checksums are in ActualCaptureFrames.csv.

The cutout rig bends knees/elbows in the visible X/Z plane and locks stance feet in world space. Search and deposit use authored pose keys and limb IK. These are interpolated cutouts, not mocap, hand-drawn frame animation or imported skeletal animation. MotionCompatibility.json records the actual 65-joint Quaternius rig and relevant clips inspected; no direct binding exists to the static plane artwork.

The girl has a separate long slate tunic/skirt silhouette and retains her original face/braid. The boy retains his original painted atlas. The companion remains a shelter presence. The upper floor is clearly closed by collapsed stairs, a broken landing and barricade; no traversal is promised. Primitive dressing, lighting, transitions, facial expression and environmental art still need substantial art work before any final cinematic claim.

All {len(old['files'])} files in the v0.1.0 checkpoint remain byte-identical. All {len(sources)} source originals and their copies match their original hashes. The original trailer/Blender/Godot production and Rod & Staff were not operated or edited. SourceAndBaselinePreservation.json provides evidence.

Runtime ZIP: {archive.name}, {archive.stat().st_size:,} bytes; {len(files)} runtime files, CRC checked. SHA-256: `{release['archive_sha256']}`. Launch via Scripts/PlayPackaged.cmd or the packaged WTSC_Survival.exe. Private preview Library identifiers are recorded separately in LibraryDeliveryConfirmed.json once saved. Raw third-party assets and the runtime ZIP are not uploaded to Library.
'''
(R/'Docs/VERIFICATION.md').write_text(doc,encoding='utf8')
checkpoint=[]
for folder in ['Source','Config','Content','Scripts','Docs']:
    for p in sorted((R/folder).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:checkpoint.append({'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
for name in ['README.md','AGENTS.md','WTSC_Survival.uproject','.gitignore']:
    p=R/name
    if p.exists():checkpoint.append({'file':name,'bytes':p.stat().st_size,'sha256':sha(p)})
write('EditableProjectCheckpoint.json',{'utc':release['utc'],'files':checkpoint})
print(json.dumps(release,indent=2))
