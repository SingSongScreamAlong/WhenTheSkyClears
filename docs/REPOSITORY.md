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

## Local/generated material

Godot's `.godot/` import cache, downloaded engines/export templates, exported executables, ZIP duplicates, Python caches, and intermediate `motion_frames/`, `craft_motion_frames/` and `sluice_motion_frames/` image sequences are ignored. The checked-in motion review movies preserve the reviewed sequences. Re-run the motion fixture to regenerate frames.

Unused third-party raw reference packs remain local. Receipts, publisher links, and license evidence are included instead of redistributing standalone vendor libraries. Download-page HTML snapshots are excluded because they can contain session material. Normal player save directories are outside the checkout. Earlier evidence may retain isolated capture-state backups; those are diagnostic records rather than saves to install or resume.

## Open and export

Any Godot 4.6 Standard installation can import `game/project.godot` and run it. Editor play requires no export templates. To build Windows with the provided portable tools, run from the repository root:

```powershell
python game/tools/setup_godot.py
python game/tools/build_v042.py export
```

The helper checks official archive SHA-512 values recorded in `game/tools/ENGINE_PROVENANCE.json`. It downloads large development dependencies on demand. `--check` only reports local tool availability. Existing local tool files are retained unless explicitly replaced.

On macOS, use the matching Standard editor to import and run the same project. Export templates are unnecessary for editor play. The Windows portable setup helper and `.cmd` files are optional platform conveniences; see [macOS setup and verification limits](MACOS.md). No Mac runtime validation is implied by Windows results.

The checked-in preset keeps both custom-template fields empty. `build_v042.py export` temporarily selects portable Windows templates and v0.4.2 product metadata, then restores the preset byte for byte in a `finally` block. It writes `game/build/v0.4.2/When the Sky Clears.exe` and an identity under `game/evidence/v042/`, hashing the restored runtime source, assets and UID sidecars. For manual editor or direct command-line exports, install matching Godot 4.6 export templates through Godot. Editor play needs neither export templates nor Windows tool files.

Use `game/PLAY.cmd` for the full game, `game/MILL_PLAYTEST.cmd` for the isolated unsaved mill (`-- --mill-preview`), or `game/CANAL_PLAYTEST.cmd` for the isolated unsaved canal approach (`-- --canal-preview`). The canal starts with zero salvage and retains the authored approach tool roll. `game/FREIGHT_CROSSING.cmd` (`-- --freight-crossing`) opens the freight rehearsal and its own save. `game/SLUICE_PLAYTEST.cmd` (`-- --sluice-preview`) opens an isolated, unsaved two-child footbridge rehearsal. Its physical weight, bridge and ratchet use the same runtime mechanism as the optional woods encounter. Campaign progress remains compatible with v0.4.0, using `journey_v4.json` in `WhenTheSkyClears/v040`.

After source and artwork are frozen, run `python game/tools/build_v042.py test all`, then `test capture`, `verify`, and `package`. Each subcommand follows the helper path. `verify` writes nothing; `package` writes the v0.4.2 manifest, Windows/source ZIPs and artifact hashes. Only recognized report/capture files and numeric JPGs in the scenario's known recording folder are cleared before a test. Its invocation records fresh output and frame hashes; verification rejects missing, changed or stale evidence. Capture also fails immediately if its sluice state report did not reach wait, crossing and reunion. The source ZIP places `project.godot` at its root, keeps custom-template fields empty, and uses a v0.4.2 export path/product version through a declared archive-only configuration transform. Repository-reference `game/` paths are flattened in that ZIP; documentation and licenses remain under its own `docs/`.

Install `game/requirements-dev.txt` for the Python image/movie tools. Optional native recordings use `python game/tools/build_v042.py test craft-playthrough sluice-playthrough`; `python game/tools/make_review_v042.py all` builds the labelled board and silent movies after their checks pass. `test motion` explicitly launches `scenes/animation_review.tscn` for the separate staged close study.

## Current v0.4.2 evidence

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

The release source includes the story and animation dependencies present in its snapshot. Their presence does not establish full artistic approval or a finished film adaptation. Current work and final verification status belong to the [v0.4.2 notes](releases/v0.4.2.md); the [v0.4.0 notes](releases/v0.4.0.md) retain the earlier verified scope.

The current art consistency pass uses the painted tent's material clarity as the benchmark, with readable painted faces and clothing, revised material tints, softer contact shadows, and restrained environmental darkness. The [rendered comparison](../game/evidence/v040/ART_READABILITY_BEFORE_AFTER.jpg) supports craft review independently of reachability and controller checks. It does not establish artistic acceptance or AAA completion.
