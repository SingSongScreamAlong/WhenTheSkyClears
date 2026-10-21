"""Finish the bounded v0.1.2 room study after real packaged tests and captures."""
from pathlib import Path
import collections, datetime, hashlib, json, shutil, subprocess, zipfile
from PIL import Image
import imageio_ffmpeg
R=Path(__file__).resolve().parents[1];E=R/'Evidence';B=R.parent/'WTSC_Survival_Prototype_v0_1_1'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,obj):(E/n).write_text(json.dumps(obj,indent=2),encoding='utf8')
old=read(B/'Evidence/EditableProjectCheckpoint.json')
assert all(sha(B/x['file'])==x['sha256'] for x in old['files'])
zipold=B/'Deliverables/WTSC_Shelter_Study_Win64_v0.1.1_ObjectiveFix.zip'
assert sha(zipold)=='7a9707ef5f04fefe2aee57e320820ce6ec28de87348b41c83f189b60a92dde0f'
raw=[]
for p in sorted((B/'SourceAssets').rglob('*')):
    if p.is_file():
        q=R/p.relative_to(B);assert sha(p)==sha(q);raw.append({'relative':str(p.relative_to(B)),'sha256':sha(q),'bytes':q.stat().st_size})
before=read(E/'ArtBefore/GameplayReplay.json');after=read(E/'ArtAfter/GameplayReplay.json');overview=read(E/'ArtFull/GameplayReplay.json')
test=read(E/'Regression/PackagedGameplayReplay.json');video=read(E/'ActualVideoReceipt.json')
assert test['passed'] and len(test['events'])==11 and all(x['passed'] and x['objective_passed'] for x in test['events'])
assert after['art_study'] and video['art_study'] and video['full_decode_passed']
assert video['decoded_video_frames']==after['recorded_frames']
fields=['player_x','camera_location','ortho_width','orthographic','head_world','hand_world']
camera={k:{'before':before['events'][0][k],'after':after['events'][0][k],'matches':before['events'][0][k]==after['events'][0][k]} for k in fields}
assert all(x['matches'] for x in camera.values())
assert Image.open(E/'ArtBefore/RoomStudy.png').size==Image.open(E/'ArtAfter/RoomStudy.png').size==(1600,900)
for name in ['ArtAfter','ArtFull']:
    log=(E/name/'ArtStudy.log').read_text(errors='ignore')
    assert 'Failed to compile Material' not in log
for src,dest in [('ArtBefore/RoomStudy.png','WTSC_v0_1_2_Room_Before.png'),('ArtAfter/RoomStudy.png','WTSC_v0_1_2_Room_After.png'),('ArtFull/ArtOverview.png','WTSC_v0_1_2_Shelter_Context.png')]:shutil.copy2(E/src,E/dest)
basecpp=(B/'Source/WTSCSurvival/WTSC.cpp').read_text();newcpp=(R/'Source/WTSCSurvival/WTSC.cpp').read_text()
def rig(s):return s[s.index('AWTSCChild::AWTSCChild()'):s.index('static AWTSCGameMode* Mode')]
assert rig(basecpp)==rig(newcpp)
assert sha(B/'Content/WTSC/Materials/M_Backdrop.uasset')==sha(R/'Content/WTSC/Materials/M_Backdrop.uasset')
save('MatchedCameraComparison.json',{'size':[1600,900],'camera_and_character_fields':camera,'matched':True,'before_provenance':'Unchanged ObjectiveFix art captured in v0.1.2 test-only camera harness before room edits','after_provenance':'Final packaged v0.1.2 executable','full_context':'BeforeFullShelter.png is the actual v0.1.1 overview; ArtFull/ArtOverview.png uses the same overview framing; HUD version differs','rig_code_unchanged':True,'backdrop_material_unchanged':True,'art_approval':False})
save('BaselinePreservationFinal.json',{'baseline_project':str(B),'baseline_checkpoint_files_unchanged':len(old['files']),'objective_fix_zip_unchanged':True,'source_asset_files_byte_identical':len(raw),'source_assets':raw,'child_rig_code_byte_identical':True,'backdrop_material_byte_identical':True})
native=read(E/'WestRoomNativeImport.json')
# Decode and inspect the entire video for blank scene segments, retaining actual timing.
ff=imageio_ffmpeg.get_ffmpeg_exe();movie=E/'WTSC_v0_1_2_Room_Motion.mp4'
run=subprocess.run([ff,'-hide_banner','-i',str(movie),'-vf','crop=1600:760:0:90,blackdetect=d=0.15:pix_th=0.02:pic_th=0.98','-an','-f','null','-'],capture_output=True,text=True)
assert run.returncode==0
segments=[x for x in run.stderr.splitlines() if 'black_start:' in x];assert not segments
(E/'VideoSceneBlankCheck.log').write_text(run.stderr,encoding='utf8')
for t,n in [(2,'DecodedRoomWalk.png'),(7,'DecodedRoomArc.png')]:
    x=subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1',str(E/n)],capture_output=True,text=True);assert x.returncode==0
save('VideoSceneBlankCheck.json',{'full_decode_passed':True,'blank_scene_segments':segments,'decoded_sample_seconds':[2,7]})
pkg=R/'Saved/Packaged/Windows'
(pkg/'WTSC_README.txt').write_text('When The Sky Clears - Shelter Study v0.1.2\nOne west sleeping/heating room art pass, existing shelter/shop loop retained.\nA/D walk; E search/deposit; F/G/H supplies; R reset; F5/F9 save/load; Tab framing; Esc pause.\nAuthored cutouts remain provisional. No cinematic art approval, child animation fix, companion carrying or upstairs traversal is claimed.\nRoom architecture and SVG surfaces have editable Python/JSON/SVG/glTF sources in the editable project. Seven existing Poly Haven CC0 props reused; established character/background paintings unchanged.\n',encoding='utf8')
out=R/'Deliverables';out.mkdir(exist_ok=True);archive=out/'WTSC_Shelter_Study_Win64_v0.1.2_ArtStudy.zip';assert not archive.exists()
files=[p for p in sorted(pkg.rglob('*')) if p.is_file() and p.suffix.lower()!='.pdb' and not {'Evidence','Saved'}.intersection(p.relative_to(pkg).parts)]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(pkg).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
release={'utc':now,'version':'0.1.2 art study','project':str(R/'WTSC_Survival.uproject'),'package':str(archive),'package_bytes':archive.stat().st_size,'package_sha256':sha(archive),'package_crc_verified':True,'runtime_files':len(files),'tests_passed':11,'test_game_seconds':test['game_seconds'],'test_type':'Actual native engine simulated key events, not an OS/human playtest','matched_before_after':True,'room_geometry':native['source_geometry_stats'],'retained_detailed_props':len(native['original_prop_keys']),'video_bytes':movie.stat().st_size,'video_seconds':video['decoded_seconds'],'real_video_frames':video['decoded_video_frames'],'actual_capture_fps':video['actual_capture_fps'],'runtime_fps_during_art_capture':video['actual_runtime_fps_including_capture'],'no_duplicated_smoothing_frames':True,'art_approved':False,'source_provenance':'Code-authored geometry and SVG surface graphics with editable sources, not imagegen mockups or artist hand-painted frames','remaining_gaps':['Child cutout shoulder gaps, stiffness, expression and companion behavior remain unresolved','One room only: upper floor, other rooms, shop and exterior remain at previous prototype quality','Foreground/photo-prop/painted-backdrop style integration is still an art study requiring user review','No new gameplay systems or map expansion; upstairs remains inaccessible'],'interruption':'First packaged regression lost its process connection and stopped before a final receipt; log retained; complete rerun passed through existing Desktop Commander background route'}
save('Release_v0_1_2.json',release)
save('BUILD_STATUS.json',{'utc':now,'version':'0.1.2','stage':'packaged; eleven regressions passed; matched actual-engine comparison and realtime clip ready for review','validated_gameplay':True,'art_approval':False,'release':release,'private_library':'Prior interim matched images saved; final private IDs added separately once saved'})
(R/'Docs/VERIFICATION.md').write_text('# v0.1.2 room-study verification\n\n'+json.dumps(release,indent=2)+'\n\nThe eleven checks preserve ObjectiveFix: fresh state, cache arrival, crouched reach, finite search, no duplicate loot, home arrival objective, deposit before commit, completed storage, save/readback, food/water use, reset. Full event-level objectives and inventory states are in Evidence/Regression/PackagedGameplayReplay.json.\n\nMatchedCameraComparison.json proves identical focus-camera and initial character fields for the actual before/after stills. The old full shelter view remains beside a final overview at its original framing. Art-study completion is not a regression pass or art approval.\n\nActualCaptureFrames.csv retains each real viewport sample, wall timestamp, engine frame ID, dimensions, size and checksum. VFR movie timing preserves those real intervals; full decode counts match. No fake high-rate interpolation or duplicated-frame smoothing is used. The clip is silent.\n\nBaselinePreservationFinal.json verifies the prior 102-file checkpoint and original source copies. All v0.1.1 deliverables remain untouched. Recovery logs and earlier failed-material review remain in Evidence.\n',encoding='utf8')
(R/'README.md').write_text('# WTSC Shelter Study v0.1.2\n\nOpen WTSC_Survival.uproject in installed Unreal 5.8.3 or run Scripts/PlayPackaged.cmd. The sibling v0.1.1 ObjectiveFix remains preserved.\n\nThis bounded pass rebuilds one west sleeping/heating room with actual bevelled construction, a casement opening, localized damage, deliberate domestic prop arrangement and motivated light. Existing gameplay, map size, detailed props, paintings and provisional child rig remain.\n\nControls: A/D walk; hold E at the shop crate; E at shelter shelves deposits; F/G/H use supplies; Tab frames; R resets; F5/F9 save/load; Esc pauses.\n\nEleven native gameplay regressions passed. See Docs/ART_STUDY.md and Docs/VERIFICATION.md for exact provenance, matched camera evidence and remaining art gaps. The before/after stills and short motion clip are real Unreal output, not concept images. This is a reviewable art study, not final cinematic approval.\n',encoding='utf8')
tracked=[]
for folder in ['Source','Config','Content','Scripts','Docs']:
    for p in sorted((R/folder).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:tracked.append({'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
for n in ['WTSC_Survival.uproject','README.md','AGENTS.md','.gitignore']:
    p=R/n
    if p.exists():tracked.append({'file':n,'bytes':p.stat().st_size,'sha256':sha(p)})
save('EditableProjectCheckpoint.json',{'utc':now,'files':tracked})
print(json.dumps(release,indent=2))
