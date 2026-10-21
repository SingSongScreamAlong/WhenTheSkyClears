# Repository contents and reproducibility

This repository contains the When the Sky Clears Godot game. The original production workspace also holds a separate Blender trailer, which is outside this repository's scope. The original narrative handoff is preserved in `docs/story/` as a reference; its film timing, music direction, and production instructions are not the game's implementation contract.

## Included

- Current editable Godot project, all runtime paintings, character art, motion data, terrain, levels, audio, fonts, scenes, and controllers under `game/`.
- Native source snapshots under `game/previous/v0.1.0/`, `v0.2.0/`, and `v0.3.0/`. These preserve prior development states without inventing historical Git commits.
- Level authoring, engine setup, packaging, and native verification tools. Python media helpers additionally use Pillow and FFmpeg where their imports/commands require them.
- Development notes, source receipts, exact third-party license texts, reports, captured scenes, review movies, and build identity manifests.
- Standalone Windows and editable-source ZIPs through GitHub Releases. Versions 0.1.0, 0.2.0, and 0.3.0 are retained. The verified [v0.4.0 release](releases/v0.4.0.md) adds the physical mill sequence, route choices, controller work, freight rehearsal, and art consistency pass.
- The verified [v0.4.1 release](releases/v0.4.1.md) develops bespoke interaction props, regional staging and mill feedback, with separate build and evidence locations. The v0.4.0 evidence and packages remain frozen.
- [v0.4.2](releases/v0.4.2.md) adds an optional two-child woods footbridge, dedicated girl clothing, distinct work/contact acting, gradual logging-gate physics and revised timber/rope staging. The existing campaign length remains unchanged. The build passed final delivery verification; earlier releases stay preserved.
- [v0.4.3](releases/v0.4.3.md) integrates the optional school handcart shelter, separate child cover tests, physical dock/hatch and finite reward, boy cloth and character performance revisions. Final native verification passed; earlier verified releases remain available.
- [v0.4.4](releases/v0.4.4.md) adds an optional weighted orchard ramp, freight cargo lift, two-child rope ferry and drawn intermediate head angles. The frozen build passed 557 native checks, a separate 27-check source animation fixture, 27 native 4K captures, full navigation and three movie validations. Earlier releases remain preserved.

## Local/generated material

Godot's `.godot/` import cache, downloaded engines/export templates, exported executables, ZIP duplicates, Python caches, and intermediate `motion_frames/`, `craft_motion_frames/`, `sluice_motion_frames/`, `trolley_motion_frames/`, `performance_motion_frames/`, `physical_v044_motion_frames/`, `garden_v044_motion_frames/` and `character_v044_motion_frames/` image sequences regenerate locally. Encoded review movies preserve the reviewed sequences; the editable-source ZIP includes its validated v0.4.4 board and three movies after final media checks.

Unused third-party raw reference packs remain local. Receipts, publisher links, and license evidence are included instead of redistributing standalone vendor libraries. Download-page HTML snapshots are excluded because they can contain session material. Normal player save directories are outside the checkout. Earlier evidence may retain isolated capture-state backups; those are diagnostic records rather than saves to install or resume.

## Open and export

Any Godot 4.6 Standard installation can import `game/project.godot` and run it. Editor play requires no export templates. To build Windows with the provided portable tools, run from the repository root:

```powershell
python game/tools/setup_godot.py
python game/tools/build_v044.py export
```

The helper checks official archive SHA-512 values recorded in `game/tools/ENGINE_PROVENANCE.json`. It downloads large development dependencies on demand. `--check` only reports local tool availability. Existing local tool files are retained unless explicitly replaced.

On macOS, use the matching Standard editor to import and run the same project. Export templates are unnecessary for editor play. The Windows portable setup helper and `.cmd` files are optional platform conveniences; see [macOS setup and verification limits](MACOS.md). No Mac runtime validation is implied by Windows results.

The checked-in preset keeps both custom-template fields empty. `build_v044.py export` temporarily selects portable Windows templates and v0.4.4 product metadata, then restores the preset byte for byte in a `finally` block. It writes `game/build/v0.4.4/When the Sky Clears.exe` and an identity under `game/evidence/v044/`, hashing the restored runtime source, assets and UID sidecars. For manual editor or direct command-line exports, install matching Godot 4.6 export templates through Godot. Editor play needs neither export templates nor Windows tool files.

Use `game/PLAY.cmd` for the full game, `game/MILL_PLAYTEST.cmd` for the isolated unsaved mill (`-- --mill-preview`), or `game/CANAL_PLAYTEST.cmd` for the isolated unsaved canal approach (`-- --canal-preview`). The canal starts with zero salvage and retains the authored approach tool roll. `game/FREIGHT_CROSSING.cmd` (`-- --freight-crossing`) opens the freight rehearsal and its own save. `game/SLUICE_PLAYTEST.cmd` (`-- --sluice-preview`) opens an isolated, unsaved two-child footbridge rehearsal. Its physical weight, bridge and ratchet use the same runtime mechanism as the optional woods encounter. `game/TROLLEY_PLAYTEST.cmd` (`-- --trolley-preview`) opens the optional school handcart near its start. Mill/canal/sluice/trolley previews retain audio and pause on focus loss, while the smoke-mode save guard keeps campaign writes disabled. Campaign progress remains compatible with v0.4.0, using `journey_v4.json` in `WhenTheSkyClears/v040`.

After source and artwork are frozen, run `python game/tools/build_v044.py test all`, then `test capture`, `verify`, and `package`. Each subcommand follows the helper path. `verify` writes nothing; `package` writes the v0.4.4 manifest, Windows/source ZIPs and artifact hashes. Only recognized scenario outputs and known numeric frame files are cleared. Fresh output/frame hashes reject missing, changed or stale evidence. Capture fails if any sluice, trolley, physical-puzzle or garden state report is incomplete. The source ZIP flattens `game/`, keeps docs/licenses under `docs/`, and declares its archive-only empty-template/v0.4.4 preset transform.

Install `game/requirements-dev.txt` for the Python image/movie tools. Record with `python game/tools/build_v044.py test physical-playthrough garden-playthrough character-playthrough`, then `python game/tools/make_review_v044.py all`. Each media mode can run independently. `test motion` explicitly launches `scenes/animation_review.tscn` for its separate close study.

## Current v0.4.4 evidence and workflow

The frozen executable passed **557 native functional checks across 19 suites**, including physical 30, garden 26 and character 18. The separate **27/27 source animation fixture** is excluded. The identity covers **189 runtime files**; the executable is **150,662,592 bytes**, SHA-256 `62b4c50f600632a1886759a912cfaa22d33405782a625ef0db92478476d22fed`. Native-input navigation completed **all five chapters in 732.55 simulated seconds**, with **one school checkpoint recovery**, health 100, rations four, medicine two and no failure. This is not measured human playtime. Final logs contain no engine/script errors or leak/resource warnings.

The isolated helper uses `game/build/v0.4.4/` and `game/evidence/v044/`. Required reports include `physical_puzzles_v044.json`, `garden_puzzle_v044.json` and `character_checks_v044.json`, retained functional suites, `continuous_traversal.json` and the separately counted source animation fixture. `EXPORT_IDENTITY.json`, `DELIVERY_MANIFEST_v044.json`, per-scenario invocations and fresh hash inventories bind the delivery.

All **27 native 3840 × 2160 views** passed: 19 earlier scenes, two orchard states, two lift states, three ferry states and a clean character attention view. The new physical/garden and retained sluice/trolley semantic reports all reached their exact sequences. `V044_PLAYABLE_REVIEW.jpg`, `review_board_validation.json` and `VISUAL_REVIEW_v044.json` document exact-export captures and sampled visual review, with artistic acceptance separate.

Three silent 1440 × 810 / 30 fps movies passed full decode and independent frame-count/duration checks: `WTSC_Physical_Puzzles_Review_v044.mp4` (913 frames / 30.4333 seconds), `WTSC_Garden_Puzzle_Review_v044.mp4` (487 / 16.2333), and `WTSC_Character_Review_v044.mp4` (457 / 15.2333). Matching validation JSON files bind exact native invocations, reports and frame inventories.

`test physical-playthrough garden-playthrough character-playthrough` records three separate 30 fps native fixtures. `python game/tools/make_review_v044.py all` validates/composes their movies and the nine-panel board. Preparation and character scene cuts are excluded; this footage differs from full-campaign navigation. `package` rejects stale optional media identities/hashes/bindings, rechecks required evidence before promotion, and includes the validated board and three movies in the editable-source ZIP with manifest hashes. Engines, caches and intermediate frames remain outside that ZIP. Its declared archive-only preset transform preserves empty custom templates and sets v0.4.4 output/version metadata.

The Windows package adds `ORCHARD_PLAYTEST.cmd` (`-- --orchard-preview`), `FREIGHT_LIFT_PLAYTEST.cmd` (`-- --freight-lift-preview`) and `GARDEN_FERRY_PLAYTEST.cmd` (`-- --garden-preview`). Source play can use those native user flags directly. These isolated previews are unsaved, retain sound and pause on focus loss. Earlier preview launchers and campaign-save compatibility remain.

The routes stay optional within the 79,200-unit campaign. The orchard's actual chock raises a hinged ramp; the lift needs the waiting boy's native platform contact and arrests descent above either child; the ferry needs both aboard and low before real velocity carries them to the far dock. The lower cold-water route remains available. Fresh extraction, archive/path/hash validation and native startup complete the delivery workflow before publication. Technical verification, sampled native review, human playtesting and artistic acceptance remain distinct.

## Preserved v0.4.3 evidence

The v0.4.3 runtime is frozen. Its export identity covers **169 runtime files**; the executable is **145,721,376 bytes**, SHA-256 `d99fb0152e947c0fb9848c64548f7cb886d678d11bc9507f468e6aade4efb2d3`. The executable passed **481 native functional checks across 16 suites**, plus a separate **27/27 source animation fixture** excluded from that total. Continuous traversal completed all five chapters in **730.4167 simulated seconds with one checkpoint recovery**, final health 100 and no failure. This is not measured human playtime. All 19 native 4K captures and both fresh movie validations passed. Runtime modules use `shelter_trolley`, `trolley_checks.json` and `performance_checks.json`.

Normal close now stops active audio, releases its streams and permits a short asynchronous drain before engine shutdown.

The cart's real rigid body, parking brake and dock contact open a right-hinged physical cabinet lid. Each child needs their own crouched position beneath the moving canopy to receive cover. The finite cabinet offers one medicine and one salvage through the existing partial-cache/inventory rules. Pause holds the body, hatch and visible work contacts; recovery resets unsolved progress and save/resume restores a solved dock and spent cache. The original static-cover route remains available, and the route remains 79,200 units across five chapters.

Final records are under `game/evidence/v043/`; packaging collects them into the delivery manifest:

- `EXPORT_IDENTITY.json` and `DELIVERY_MANIFEST_v043.json` bind all runtime assets/source/UIDs to the exact standalone binary.
- `release_final/<scenario>/invocation.json` records binary/source binding, exit status and fresh output/frame hashes. The separate source animation fixture stays outside the native total.
- `release_final/capture/` contains 19 verified native 3840 × 2160 PNGs plus successful `sluice_capture.json` and `trolley_capture.json` reports. Trolley views 17–19 cover shelter, dock and reunion.
- `V043_PLAYABLE_REVIEW.jpg` selects nine labelled scenes from that capture set.
- `WTSC_Trolley_Playthrough_v043.mp4` / `trolley_movie_validation.json`: 530 frames / 17.6667 seconds, 1440 × 810, 30 fps, silent.
- `WTSC_Character_Performance_Review_v043.mp4` / `performance_movie_validation.json`: 522 frames / 17.4 seconds, 1440 × 810, 30 fps, silent. Both passed complete decode and independent frame-count/duration checks, binding their exact fresh frame inventories to the current d99f… executable.

Trolley success starts from one explicit near-bank setup, then uses actual crouching, held input, slope travel, docking, reunion and finite searching. Exposure/refusal/pause/save fixtures are separate. Character performance uses bounded setups for stance/turn, actual warnings, cold and moving cart contact; preparation is excluded. The recording adds three checks across the complete rendered push/release for live grips and forearm/face clearance, separately from the ordinary functional performance suite. These silent labelled studies have different scopes from uninterrupted campaign traversal and artistic acceptance. The ordinary performance report has 19 passing checks; its recorded report has 22 including 3 additional render-time checks. Those scopes overlap and are not added together.

## Preserved v0.4.2 evidence

The frozen v0.4.2 executable passed **431 native functional checks across 14 suites**, with **157 runtime files** in its identity. All **16 native 4K captures** passed, including the successful wait/crossing/reunion report. A separate **27/27 source animation fixture** passed and remains outside the native total. Full traversal completed all five chapters in **730.45 simulated seconds with one checkpoint recovery**, final health 100 and no failure; this is not measured human playtime. The required new reports are `sluice-checks/sluice_checks.json`, `craft-checks/craft_checks.json` and `world-craft-checks/world_craft_checks.json`. These cover both-child cooperation and real bridge contacts; moving pump-hand grips, pause and work release; and gradual gate collision, safety, persistence and grass response. Deliberate fixture setup remains separate from full campaign traversal.

The independent output locations are `game/build/v0.4.2/` and `game/evidence/v042/`. The current evidence index contains:

- `EXPORT_IDENTITY.json`, tying 157 runtime files to the 142,500,064-byte standalone executable. Its SHA-256 is `0ecef38b7ea9544734d86e86fc3263ded0514a739e36f4fdd3a9e570e6a4da91`. `DELIVERY_MANIFEST_v042.json` collects the final verified delivery evidence during packaging.
- `release_final/<scenario>/invocation.json`, with the native executable/source binding, exit status and per-run output inventory.
- `release_final/animation-checks/movement_checks.json` records the 27 passing source checks; `release_final/traverse/continuous_traversal.json` records the completed five-chapter native journey.
- `release_final/capture/`, containing 16 native 3840 × 2160 PNGs and `sluice_capture.json`; the puzzle report identifies only views 13–15, while view 16 stages the moving logging gate.
- `V042_PLAYABLE_REVIEW.jpg`, selecting nine labelled native views: character, pump, three puzzle states, logging gate, village, school and ash region.
- `WTSC_Character_Craft_Review_v042.mp4` / `craft_movie_validation.json`: 686 frames, 22.8667 seconds, 1440 × 810, 30 fps, silent.
- `WTSC_Sluice_Playthrough_v042.mp4` / `sluice_movie_validation.json`: 313 frames, 10.4333 seconds, 1440 × 810, 30 fps, silent. Both movies passed full decode and independent frame-count/duration checks and bind their exact source-frame inventories to the final native invocation.

The character movie uses staged locomotion, cold/care, pump, cradle, warming and searching sections; setup and scene changes are excluded. The sluice movie is a bounded authored encounter with explicit starting conditions and earlier hazards disabled. Both are silent review footage, separate from continuous campaign navigation. The expanded source animation fixture remains outside the native total because it overlaps baseline checks. Source files, diagnostics and screenshots alone establish neither user artistic acceptance nor AAA finish.

## Preserved verification

The final v0.4.1 executable passed **386 native functional checks**, plus a separately reported **27-check source animation fixture**, and verified **12 fresh native 4K captures**. Continuous navigation completed all five chapters in **730.45 simulated seconds with one checkpoint recovery**. This is not measured human playtime. The frozen identity covers **143 runtime files**. Records are under:

- `game/evidence/v041/EXPORT_IDENTITY.json` and `DELIVERY_MANIFEST_v041.json`.
- `game/evidence/v041/release_final/<scenario>/invocation.json`, with exact binary/source binding and per-run generated-output hashes.
- `game/evidence/v041/release_final/refinement-checks/refinement_checks.json`, covering authored partial caches, pump work, pause, interruption and water transition.
- `game/evidence/v041/release_final/capture/` and `V041_PLAYABLE_REVIEW.jpg`, for the 12 actual-renderer scenes and explicitly staged close views.
- `game/evidence/v041/WTSC_Mill_Playthrough_v041.mp4` and `mill_movie_validation.json`, for the fully decoded silent native recording: 18 seconds, 1440 × 810, 30 fps and 540 frames. Its invocation matches the exact final executable.

The animation fixture remains outside the native total because it includes baseline movement checks. The mill movie begins after explicit initial fixture setup, then uses physical input for the safe crossing. The risk and pause fixtures are tested separately. Runtime report version strings may retain an earlier label; the wrapper identity and source/binary hashes establish this pass. No new offline terrain audit is claimed. These technical results and reviewed native artifacts remain distinct from user artistic acceptance and AAA completion.

The final v0.4.0 executable passed 371 native functional checks and completed all five chapters in 730.45 simulated seconds with one checkpoint recovery. The separate 27-check source animation fixture includes the baseline 13 movement checks and is excluded from that total. Begin with these final records:

- `game/evidence/v040/DELIVERY_MANIFEST_v040.json` and `EXPORT_IDENTITY.json`: selected evidence, source hashes, and executable identity.
- `game/evidence/v040/release_final/<scenario>/invocation.json`: the exact packaged invocation, executable SHA-256, exit status and engine errors. Scenarios cover smoke, survival, encounters, journey, optional routes, movement, development branches, the mill, freight crossing, story dependencies, and continuous traversal. The separate `animation-checks` invocation binds its native editor fixture and full source hash map to the frozen export identity.
- `game/evidence/v040/V040_PLAYABLE_REVIEW.jpg`: selected actual-renderer scenes from nine 3840 × 2160 captures, including a staged character close view.
- `game/evidence/v040/ART_READABILITY_BEFORE_AFTER.jpg`: earlier native views compared with revised actual captures from the final executable.
- `game/evidence/v040/WTSC_Mill_Playthrough_v040.mp4` and `mill_movie_validation.json`: an 18-second silent, 1440 × 810 / 30 fps / 540-frame native mill playthrough, fully decoded. This is distinct from continuous full-journey navigation.
- `game/evidence/v040/terrain_polygon_audit_current.json`: 627,876 current geometry checks with zero failed polygons.

The final manifest selects the valid runs. Folder names alone do not establish that a report matches the delivered executable. Earlier `source`, `packaged`, `integration`, `title_route` and diagnostic iterations remain as development history, including failures.

For the retained v0.3.0 package:

- `game/evidence/v030/DELIVERY_MANIFEST_v030.json` and `EXPORT_IDENTITY.json`.
- `game/evidence/v030/candidate_/{smoke,survival,encounters,journey-checks,side-routes,traverse}/`: the six passing functional/navigation invocations that identify the final executable hash.
- `game/evidence/v030/final_native_verified/{capture-new,motion}/`: the final native rendered captures and motion records.
- `game/evidence/v030/V030_PLAYABLE_REVIEW.jpg`, `WTSC_Movement_Study_v030.mp4`, and `motion_movie_validation.json`.

Earlier iterations are retained for development history, including failed attempts. Names such as `final_native`, `final_native_v2`, `candidate_/capture-new`, `candidate_/motion`, `packaged_`, `source_`, and `character_material` do not establish current validity. Consult each invocation's executable hash, exit status, and engine logs. The verified paths above are authoritative for v0.3.0.

Reports retain original machine paths and timestamps as historical evidence. They are not required installation paths. QA helpers write new reports when re-run. Continuous navigation uses native input and records any actual recovery; targeted encounter/optional-route tests and staged visual fixtures have separate scopes. The historical v0.3.0 traversal used one checkpoint recovery. These checks establish technical behavior, not AAA artistic acceptance.

The release source includes the story and animation dependencies present in its snapshot. Their presence does not establish full artistic approval or a finished film adaptation. Current work and final verification status belong to the [v0.4.3 notes](releases/v0.4.3.md); the [v0.4.0 notes](releases/v0.4.0.md) retain the earlier verified scope.

The current art consistency pass uses the painted tent's material clarity as the benchmark, with readable painted faces and clothing, revised material tints, softer contact shadows, and restrained environmental darkness. The [rendered comparison](../game/evidence/v040/ART_READABILITY_BEFORE_AFTER.jpg) supports craft review independently of reachability and controller checks. It does not establish artistic acceptance or AAA completion.
