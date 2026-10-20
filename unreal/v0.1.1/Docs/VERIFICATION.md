# Objective-state correction to v0.1.1

The top HUD now changes from travel to crate arrival, active search, return home, shelf arrival, deposit in progress, and completed states. Deposit text remains active until the deposit action ends, even after its inventory commit.

The corrected editor/game code and Windows package built successfully. The packaged executable passed all 11 replay assertions in 57.43 game seconds: the original ten regressions plus shelf arrival. Every event records the actual displayed objective and its expected value; all 11 match. This is native simulated engine input, not an OS-keyboard or human playtest.

No new screenshots, video, or Library upload were made; the test recorded zero frames. All 149 preserved native/source/prior-delivery files matched their pre-fix hashes after testing. The previous screenshot and video predate this text correction. Previous sources, test harness, documentation, checkpoint and complete packaged recording evidence are retained under Evidence/ObjectiveFix/Before.

Changed code/test files: Source/WTSCSurvival/WTSC.cpp (objective selection, actual-state assertions, separate no-capture receipt support) and Scripts/accept_packaged.ps1 (no-capture mode and 11-event acceptance). No character, geometry, material, map, source asset, input control, or inventory behavior changed.

Corrected package: Deliverables/WTSC_Shelter_Study_Win64_v0.1.1_ObjectiveFix.zip, 354,043,505 bytes, CRC verified; SHA-256 `7a9707ef5f04fefe2aee57e320820ce6ec28de87348b41c83f189b60a92dde0f`. The original v0.1.1 ZIP remains unchanged. Scripts/PlayPackaged.cmd launches the corrected packaged executable. Exact state observations, artifact hashes and result: Evidence/ObjectiveFix/Result.json and PackagedGameplayReplay.json.

## Prior v0.1.1 delivery verification

# v0.1.1 verification

Built with Unreal 5.8.3-58210709+++UE5+Release-5.8 using installed Visual Studio Build Tools. The final native map was saved, reopened and read back: 72 resources and seven real imported static-mesh prop references. The final material/map commandlet returned zero errors and zero warnings.

The packaged Windows executable passed all ten checks in 57.48 game seconds: initial storage/cache; walk to cache; crouched reach with grounded feet; finite search; no duplicated loot; visible deposit before inventory commit; return/deposit; save/readback; food/water consumption; fresh reset. This uses real native engine simulated key events, not OS keyboard delivery or a human playtest. Full structured evidence is in PackagedGameplayReplay.json. Preliminary run evidence is retained in Pass1.

Actual viewport capture produced 1614 unique engine-frame samples at 29.63 samples per second, 1600Ã—900. Runtime averaged 121.50 FPS during recording. The MP4 preserves measured wall-clock timing as variable-rate playback. No generated intermediate frames or duplicate-frame smoothing were added. Full decode returned 1614 frames in 54.470 seconds. The target was 30Hz; the measured rate is reported separately. Exact frame timestamps, engine frame IDs, sizes and checksums are in ActualCaptureFrames.csv.

The cutout rig bends knees/elbows in the visible X/Z plane and locks stance feet in world space. Search and deposit use authored pose keys and limb IK. These are interpolated cutouts, not mocap, hand-drawn frame animation or imported skeletal animation. MotionCompatibility.json records the actual 65-joint Quaternius rig and relevant clips inspected; no direct binding exists to the static plane artwork.

The girl has a separate long slate tunic/skirt silhouette and retains her original face/braid. The boy retains his original painted atlas. The companion remains a shelter presence. The upper floor is clearly closed by collapsed stairs, a broken landing and barricade; no traversal is promised. Primitive dressing, lighting, transitions, facial expression and environmental art still need substantial art work before any final cinematic claim.

All 87 files in the v0.1.0 checkpoint remain byte-identical. All 38 source originals and their copies match their original hashes. The original trailer/Blender/Godot production and Rod & Staff were not operated or edited. SourceAndBaselinePreservation.json provides evidence.

Runtime ZIP: WTSC_Shelter_Study_Win64_v0.1.1.zip, 354,039,808 bytes; 48 runtime files, CRC checked. SHA-256: `bc8377adb44ace0b686293417d385b553421c826a1bb44b9998b9da909fb9ee8`. Launch via Scripts/PlayPackaged.cmd or the packaged WTSC_Survival.exe. Private preview Library identifiers are recorded separately in LibraryDeliveryConfirmed.json once saved. Raw third-party assets and the runtime ZIP are not uploaded to Library.
