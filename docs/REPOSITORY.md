# Repository contents and reproducibility

This repository contains the When the Sky Clears Godot game. The original production workspace also holds a separate Blender trailer, which is outside this repository's scope. The original narrative handoff is preserved in `docs/story/` as a reference; its film timing, music direction, and production instructions are not the game's implementation contract.

## Included

- Current editable Godot project, all runtime paintings, character art, motion data, terrain, levels, audio, fonts, scenes, and controllers under `game/`.
- Native source snapshots under `game/previous/v0.1.0/`, `v0.2.0/`, and `v0.3.0/`. These preserve prior development states without inventing historical Git commits.
- Level authoring, engine setup, packaging, and native verification tools. Python media helpers additionally use Pillow and FFmpeg where their imports/commands require them.
- Development notes, source receipts, exact third-party license texts, reports, captured scenes, review movies, and build identity manifests.
- Standalone Windows and editable-source ZIPs through GitHub Releases. Versions 0.1.0, 0.2.0, and 0.3.0 are retained. The verified [v0.4.0 release](releases/v0.4.0.md) adds the physical mill sequence, route choices, controller work, freight rehearsal, and art consistency pass.

## Local/generated material

Godot's `.godot/` import cache, downloaded engines/export templates, exported executables, ZIP duplicates, Python caches, and intermediate `motion_frames/` image sequences are ignored. The checked-in motion review movies preserve the reviewed sequences. Re-run the motion fixture to regenerate frames.

Unused third-party raw reference packs remain local. Receipts, publisher links, and license evidence are included instead of redistributing standalone vendor libraries. Download-page HTML snapshots are excluded because they can contain session material. Normal player save directories are outside the checkout. Earlier evidence may retain isolated capture-state backups; those are diagnostic records rather than saves to install or resume.

## Open and export

Any Godot 4.6 Standard installation can import `game/project.godot` and run it. Editor play requires no export templates. To build Windows with the provided portable tools, run from the repository root:

```powershell
python game/tools/setup_godot.py
python game/tools/export_v040.py
```

The helper checks official archive SHA-512 values recorded in `game/tools/ENGINE_PROVENANCE.json`. It downloads large development dependencies on demand. `--check` only reports local tool availability. Existing local tool files are retained unless explicitly replaced.

On macOS, use the matching Standard editor to import and run the same project. Export templates are unnecessary for editor play. The Windows portable setup helper and `.cmd` files are optional platform conveniences; see [macOS setup and verification limits](MACOS.md). No Mac runtime validation is implied by Windows results.

The checked-in preset keeps both custom-template fields empty. `export_v040.py` temporarily fills them with the portable Windows templates under `game/tools/` for the export and restores the clean preset in a `finally` block. It writes `game/build/v0.4.0/When the Sky Clears.exe`, then hashes the restored source and exported executable. For manual export through the editor or a direct `--export-release` command, install matching Godot 4.6 export templates through Godot. Editor play itself needs neither export templates nor Windows tool files.

`python game/tools/export_v040.py` performs the import and export and writes a source/executable identity record. Use `game/PLAY.cmd` for the full game or `game/MILL_PLAYTEST.cmd` for the isolated, unsaved mill playtest (`-- --mill-preview`). `game/FREIGHT_CROSSING.cmd` (`-- --freight-crossing`) opens the separate freight rehearsal and its own save. Normal v0.4.0 campaign progress uses `journey_v4.json` in the separate `WhenTheSkyClears/v040` Godot user-data directory and preserves earlier journey files.

After source, artwork and evidence are frozen, `python game/tools/package_v040.py --verify-only` verifies the delivery without writing artifacts. Run it without that flag to write the manifest, Windows ZIP, editable-source ZIP, and release artifact hashes. The source ZIP places `project.godot` at its root and includes story/runtime assets and development tools. Its custom-template fields stay empty; normalizing the already-empty checked-in fields makes no functional change. Repository-reference docs explain that their `game/` prefix is flattened in that ZIP.

## Evidence interpretation

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

The release source includes the story and animation dependencies present in the tested snapshot. Their presence does not establish full artistic approval or a finished film adaptation. Current release scope and verification belong to the manifest and [release notes](releases/v0.4.0.md).

The current art consistency pass uses the painted tent's material clarity as the benchmark, with readable painted faces and clothing, revised material tints, softer contact shadows, and restrained environmental darkness. The [rendered comparison](../game/evidence/v040/ART_READABILITY_BEFORE_AFTER.jpg) supports craft review independently of reachability and controller checks. It does not establish artistic acceptance or AAA completion.
