# WTSC shelter study verification

Verified 2026-10-19 20:59 UTC in **5.8.3-58210709+++UE5+Release-5.8** on this Windows machine.

The separate editable project is `WTSC_LOCAL_WORKSPACE\WTSC_Survival_Prototype\WTSC_Survival.uproject`. Native map: `/Game/Maps/ShelterDawn`. The current Win64 executable is `WTSC_LOCAL_WORKSPACE\WTSC_Survival_Prototype\Saved\Packaged\Windows\WTSC_Survival\Binaries\Win64\WTSC_Survival.exe`. Launch through `Scripts/PlayPackaged.cmd`, or extract the complete playable ZIP and run its `PLAY_WTSC.cmd`.

## Actual native results

- Seven Poly Haven props imported, including all source parts. The vice's default-pose skin was baked for static use. Source textures retain their exact hashes.
- **61 native resources**: one World, seven StaticMeshes, seven MaterialInstanceConstants, 22 Materials and 24 Texture2Ds. Paths, native file sizes and SHA-256 hashes are in `NativeAssetInventory.csv/json`.
- The native map reopened, rebuilt and saved with zero errors and zero warnings. Static attachment, clipping/exposure, orthographic framing, ground depth/foot contact, upper-room lighting and shop visibility were repaired from actual engine captures.
- The final packaged game passed **all eight checks** in **38.804 simulated game seconds**, walking **49.13 metres**. `PackagedGameplayReplay.json` is the acceptance authority; the earlier editor receipt is retained separately.

| Packaged gameplay event | Result | Game seconds |
|---|---|---:|
| fresh_state | PASS | 4.002 |
| walked_to_cache | PASS | 20.029 |
| searched_finite_cache | PASS | 23.176 |
| cache_cannot_duplicate_loot | PASS | 24.206 |
| returned_and_deposited | PASS | 37.281 |
| saved_checkpoint_readback | PASS | 37.281 |
| food_and_water_consumption | PASS | 38.303 |
| fresh_restart_restores_cache_and_storage | PASS | 38.804 |

The replay uses the engine's `FInputKeyEventArgs::CreateSimulated` path and normal gameplay bindings, movement, collisions and interactions. It does not claim a human playtest or operating-system keyboard delivery. Save/readback exercises the project-specific native save slot. R restarts the day and restores the cache, original storage and player position.

## Actual previews

`ShelterView.png`, `CacheView.png` and `ReturnedView.png` are unedited **1600 x 900 packaged-game viewport captures**. The MP4 is encoded from **176 actual Unreal frames at 5 fps**, lasting **35.2 seconds**. The initial settle is omitted. It is silent and represents the first playable study, not an audio-production pass. No AI-generated concept was substituted for gameplay footage.

Video: `WTSC_LOCAL_WORKSPACE\WTSC_Survival_Prototype\Evidence\WTSC_Shelter_Playable_Preview.mp4`. SHA-256: `388324660e1cd221eb3c696c24556855cfbaae2cc232256a84efee2de97accc5`.

Playable ZIP: `WTSC_LOCAL_WORKSPACE\WTSC_Survival_Prototype\Deliverables\WTSC_Shelter_Study_Win64_v0.1.0.zip`. **355,308,734 bytes**. SHA-256: `5a603707b7ffb1f249bc372c505ed621fa72f2508490a9e17a36e79d25f4a4c7`. Every ZIP member passed CRC. Debug symbols and generated test-frame dumps are excluded from that transport archive; the local project retains evidence and debug data.

## Preservation, limits and remaining blockers

All **38 copied publisher/original-workspace source files** still match their initial hashes. `SourcePreservationFinal.json` records read-only verification. Existing WTSC trailer, Blender and Godot productions were not modified. Rod & Staff remained parked; only WTSC task-owned engine/game processes were launched after the explicit resource release.

The age-ten faces remain the established boy/girl studies. Painted puppets, procedural limb motion, the girl's body/garment registration and custom geometry remain provisional, as labelled in the HUD and design notes. There is no finished 3D child rig, Quaternius retarget, companion carrying, combat, campaign or authored audio. This first visual pass is a playable foundation for the cinematic direction, not final cinematic fidelity.

Fab's three listings and the bounded Mixamo selection remain unacquired. The detailed service/session/backend blockers and source licenses remain in `../WTSC_Survival_Game_Assets/`. No new login, explicit agreement acceptance, purchase, software installation, permission/security change or private source upload occurred. Quaternius's archive CC0/current QAL conflict is preserved; those animation sources were not imported into this game.

The initial prepared-upload helper failed before preparation. After explicit authorization to use the direct save route, **ShelterView.png and WTSC_Shelter_Playable_Preview.mp4 were both saved to private Library**. Exact file IDs, Library IDs, byte sizes and MIME types are in `LibraryDeliveryConfirmed.json` and `LibraryRetention.json`. The entire MP4 decoded successfully; scene-crop black detection found no blank intervals, and sampled frames were visually inspected. Originals were not recompressed or overwritten. The local xattr helper is unsupported on Windows (`os.setxattr` absent), so metadata is retained in the receipt instead; remote saves are confirmed. The game ZIP was not uploaded.

## Retained repair evidence

`Run01_BlackScene` preserves the functional pass with failed visual exposure. Later numbered runs preserve rear/front/framing iterations. `BuildEditor_08.log` records a repaired 5.8 API-name compile failure; subsequent builds succeeded. The first relative-path readback launch failed and the exact absolute-path retry succeeded. The first skinned-vice conversion rejection and invalid partial-check success line are explicitly retained in `StaticGeometryBake_01Failure.txt`; the repaired seven-asset readback is the current evidence. No failed or historical run is silently labelled as current visual acceptance.
