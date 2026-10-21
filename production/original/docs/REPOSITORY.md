# Repository contents and reproducibility

This repository contains the When the Sky Clears Godot game. The working directory also holds a separate Blender trailer production, which is outside this repository's scope. The original narrative handoff is preserved in `docs/story/` as a reference; its film timing, music direction, and production instructions are not the game's implementation contract.

## Included

- Current editable Godot project, all runtime paintings, character art, motion data, terrain, levels, audio, fonts, scenes, and controllers under `game/`.
- Native source snapshots under `game/previous/v0.1.0/` and `v0.2.0/`. This initial repository import preserves those snapshots without inventing historical Git commits.
- Level authoring, engine setup, packaging, and native verification tools. Python media helpers additionally use Pillow and FFmpeg where their imports/commands require them.
- Development notes, source receipts, exact third-party license texts, reports, captured scenes, review movies, and build identity manifests.
- Standalone Windows and editable-source ZIPs for versions 0.1.0, 0.2.0, and 0.3.0 in GitHub Releases. These are the previously packaged versions; the repository also adds setup and documentation improvements.

## Local/generated material

Godot's `.godot/` import cache, downloaded engines/export templates, exported executables, ZIP duplicates, Python caches, and intermediate `motion_frames/` image sequences are ignored. The checked-in motion review movies preserve the reviewed sequences. Re-run the motion fixture to regenerate frames.

Unused third-party raw reference packs remain local. Receipts, publisher links, and license evidence are included instead of redistributing standalone vendor libraries. Download-page HTML snapshots are excluded because they can contain session material. No player saves are part of this repository.

## Open and export

Any Godot 4.6 Standard installation can import `game/project.godot` and run it. For the included Windows portable-tool paths, run:

```powershell
python game/tools/setup_godot.py
game/tools/godot/Godot_v4.6-stable_win64_console.exe --headless --path game --import
New-Item -ItemType Directory -Force game/build/v0.3.0
game/tools/godot/Godot_v4.6-stable_win64_console.exe --headless --path game --export-release "Windows Desktop"
```

The helper checks official archive SHA-512 values recorded in `game/tools/ENGINE_PROVENANCE.json`. It downloads large development dependencies on demand. `--check` only reports local tool availability. Existing local tool files are retained unless explicitly replaced.

The repository's export preset points to portable Windows templates in `game/tools/`. To use templates installed through another editor instead, clear the two custom-template fields in the export preset. Previously distributed editable-source ZIPs already clear those fields, as described in `game/SOURCE_SETUP.txt`.

## Evidence interpretation

For the current v0.3.0 package, begin with:

- `game/evidence/v030/DELIVERY_MANIFEST_v030.json` and `EXPORT_IDENTITY.json`.
- `game/evidence/v030/candidate_/{smoke,survival,encounters,journey-checks,side-routes,traverse}/`: the six passing functional/navigation invocations that identify the final executable hash.
- `game/evidence/v030/final_native_verified/{capture-new,motion}/`: the final native rendered captures and motion records.
- `game/evidence/v030/V030_PLAYABLE_REVIEW.jpg`, `WTSC_Movement_Study_v030.mp4`, and `motion_movie_validation.json`.

Earlier iterations are retained for development history, including failed attempts. Names such as `final_native`, `final_native_v2`, `candidate_/capture-new`, `candidate_/motion`, `packaged_`, `source_`, and `character_material` do not establish current validity. Consult each invocation's executable hash, exit status, and engine logs. The verified paths above are authoritative for v0.3.0.

Reports retain original machine paths and timestamps as historical evidence. They are not required installation paths. QA helpers write new reports when re-run. Continuous navigation used native input and one checkpoint recovery; targeted encounter/optional-route tests and staged visual fixtures have separate scopes. These checks establish technical behavior, not AAA artistic acceptance.
