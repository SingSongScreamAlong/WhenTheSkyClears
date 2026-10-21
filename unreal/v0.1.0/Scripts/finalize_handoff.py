from pathlib import Path
import hashlib,json,csv,datetime,collections

root=Path(__file__).resolve().parents[1];ev=root/'Evidence'
status=json.loads((ev/'BUILD_STATUS.json').read_text());test=json.loads((ev/'PackagedGameplayReplay.json').read_text());video=json.loads((ev/'VideoReceipt.json').read_text());archive=json.loads((ev/'PlayableArchiveReceipt.json').read_text());native=json.loads((ev/'NativeAssetInventory.json').read_text())
assert status['packaged_acceptance_passed'] and archive['zip_crc_verified']
events='\n'.join('| '+x['event']+' | '+('PASS' if x['passed'] else 'FAIL')+' | '+f"{x['game_seconds']:.3f}"+' |' for x in test['events'])
text=f'''# WTSC shelter study verification

Verified {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} in **{test['engine']}** on this Windows machine.

The separate editable project is `{root/'WTSC_Survival.uproject'}`. Native map: `/Game/Maps/ShelterDawn`. The current Win64 executable is `{status['packaged_executable']}`. Launch through `Scripts/PlayPackaged.cmd`, or extract the complete playable ZIP and run its `PLAY_WTSC.cmd`.

## Actual native results

- Seven Poly Haven props imported, including all source parts. The vice's default-pose skin was baked for static use. Source textures retain their exact hashes.
- **{len(native)} native resources**: one World, seven StaticMeshes, seven MaterialInstanceConstants, 22 Materials and 24 Texture2Ds. Paths, native file sizes and SHA-256 hashes are in `NativeAssetInventory.csv/json`.
- The native map reopened, rebuilt and saved with zero errors and zero warnings. Static attachment, clipping/exposure, orthographic framing, ground depth/foot contact, upper-room lighting and shop visibility were repaired from actual engine captures.
- The final packaged game passed **all eight checks** in **{test['game_seconds']:.3f} simulated game seconds**, walking **{test['distance_walked_cm']/100:.2f} metres**. `PackagedGameplayReplay.json` is the acceptance authority; the earlier editor receipt is retained separately.

| Packaged gameplay event | Result | Game seconds |
|---|---|---:|
{events}

The replay uses the engine's `FInputKeyEventArgs::CreateSimulated` path and normal gameplay bindings, movement, collisions and interactions. It does not claim a human playtest or operating-system keyboard delivery. Save/readback exercises the project-specific native save slot. R restarts the day and restores the cache, original storage and player position.

## Actual previews

`ShelterView.png`, `CacheView.png` and `ReturnedView.png` are unedited **1600 x 900 packaged-game viewport captures**. The MP4 is encoded from **{video['frame_count']} actual Unreal frames at 5 fps**, lasting **{video['video_seconds']:.1f} seconds**. The initial settle is omitted. It is silent and represents the first playable study, not an audio-production pass. No AI-generated concept was substituted for gameplay footage.

Video: `{video['file']}`. SHA-256: `{video['sha256']}`.

Playable ZIP: `{archive['archive']}`. **{archive['bytes']:,} bytes**. SHA-256: `{archive['sha256']}`. Every ZIP member passed CRC. Debug symbols and generated test-frame dumps are excluded from that transport archive; the local project retains evidence and debug data.

## Preservation, limits and remaining blockers

All **38 copied publisher/original-workspace source files** still match their initial hashes. `SourcePreservationFinal.json` records read-only verification. Existing WTSC trailer, Blender and Godot productions were not modified. Rod & Staff remained parked; only WTSC task-owned engine/game processes were launched after the explicit resource release.

The age-ten faces remain the established boy/girl studies. Painted puppets, procedural limb motion, the girl's body/garment registration and custom geometry remain provisional, as labelled in the HUD and design notes. There is no finished 3D child rig, Quaternius retarget, companion carrying, combat, campaign or authored audio. This first visual pass is a playable foundation for the cinematic direction, not final cinematic fidelity.

Fab's three listings and the bounded Mixamo selection remain unacquired. The detailed service/session/backend blockers and source licenses remain in `../WTSC_Survival_Game_Assets/`. No new login, explicit agreement acceptance, purchase, software installation, permission/security change or private source upload occurred. Quaternius's archive CC0/current QAL conflict is preserved; those animation sources were not imported into this game.

Private Library retention failed **before preparation**: the canonical upload helper reported `Library prepare_uploads is not available` in its execution context. No attachments were created and no attachment IDs are claimed. The rendered files remain local. See `LibraryRetention.json`.

## Retained repair evidence

`Run01_BlackScene` preserves the functional pass with failed visual exposure. Later numbered runs preserve rear/front/framing iterations. `BuildEditor_08.log` records a repaired 5.8 API-name compile failure; subsequent builds succeeded. The first relative-path readback launch failed and the exact absolute-path retry succeeded. The first skinned-vice conversion rejection and invalid partial-check success line are explicitly retained in `StaticGeometryBake_01Failure.txt`; the repaired seven-asset readback is the current evidence. No failed or historical run is silently labelled as current visual acceptance.
'''
(root/'Docs/VERIFICATION.md').write_text(text,encoding='utf8')
props=json.loads((ev/'NativeImportReceipt.json').read_text())['prop_meshes']
lines=['# Actual game asset manifest','', 'Only these verified sources are incorporated. Full native file inventory and hashes: `Evidence/NativeAssetInventory.csv/json`.','', '| Source | License/provenance | Native mesh |','|---|---|---|']
for key,path in props.items():lines.append(f'| [{key}](https://polyhaven.com/a/{key}) | CC0; publisher files verified; multipart static derivative retains textures/materials | `{path}` |')
lines+=['','The established boy atlas, girl profile and village painting were copied from the existing user WTSC game without changing originals. They remain provisional painted character parts and a background matte. No third-party character/animation pack was imported.','', 'Walls, cutaway floors/beams, boarded windows, street, rubble, counter, crate and lighting are custom source-authored prototype geometry/components. Engine BasicShapes are native primitives. Painterly surface variation is a native material graph; background art is an existing matte, not terrain geometry.','', 'Fab/Mixamo sources remain blocked. The full download collection, source URLs, exact archive checksums and Quaternius CC0/QAL conflict are documented at `../WTSC_Survival_Game_Assets/MANIFEST.md`. Source archives stay local.']
(root/'Docs/ASSET_MANIFEST.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
checkpoint=[]
for folder in ['Source','Config','Content','Scripts','Docs']:
    for p in sorted((root/folder).rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:checkpoint.append({'file':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ['WTSC_Survival.uproject','AGENTS.md','README.md']:
    p=root/name;checkpoint.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ev/'EditableProjectCheckpoint.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':checkpoint},indent=2),encoding='utf8')
status.update(playable_zip=archive['archive'],playable_zip_bytes=archive['bytes'],playable_zip_sha256=archive['sha256'],preview_video_bytes=video['bytes'],preview_video_sha256=video['sha256'],editable_checkpoint_files=len(checkpoint),final_handoff='READY - tested Win64 package and separate editable project; Library blocked; four downloads unacquired')
(ev/'BUILD_STATUS.json').write_text(json.dumps(status,indent=2),encoding='utf8')
print(json.dumps({'playable_zip':archive['archive'],'zip_bytes':archive['bytes'],'zip_sha256':archive['sha256'],'checkpoint_files':len(checkpoint),'packaged_checks_passed':len(test['events']),'video_seconds':video['video_seconds']},indent=2))
