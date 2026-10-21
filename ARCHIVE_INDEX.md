# When the Sky Clears: preserved implementations and production

**Godot is the active development project**, as selected by the owner on 20 October 2026. Its existing `game/` layout, history, version tags and releases are preserved. This consolidation does not change any Godot source or establish new Godot test results.

| Location | Purpose |
| --- | --- |
| [`game/`](game/) | Existing Godot game and its recorded development history |
| [`unreal/`](unreal/) | Separate Unreal shelter prototype, with v0.1.0, v0.1.1 and v0.1.2 checkpoints |
| [`production/`](production/) | Separate Blender/art/film production scripts, notes and design sources |
| [Preservation release](https://github.com/SingSongScreamAlong/WhenTheSkyClears/releases/tag/wtsc-preservation-2026-10-20) | Large screened Blender sources, stills, silent review movies, and four original Unreal Windows ZIPs |
| [`docs/acquisition/`](docs/acquisition/) | Asset source URLs, notices, checksums and local acquisition inventory; standalone vendor packs are omitted |
| [`docs/consolidation/`](docs/consolidation/) | File-level inclusion/exclusion inventory and release archive checksums |

The version numbers belong to independent implementations. Unreal v0.1.2 is not a later Godot build. No code or save format has been merged between them, and the Unreal material is retained as an archive rather than the selected game direction.

## What was preserved and screened

The editable Unreal native `Content`, source, config, scripts, artwork and selected evidence are included. Distribution copies omit the editor-only Android file-server config and private Library receipts/identifiers; the original local project files remain intact. The optional Unreal source-staging script now locates the repository's existing Godot artwork and accepts `WTSC_ASSET_LIBRARY` for a separately acquired local vendor collection.

Large production media are in independently extractable ZIP parts, each under GitHub's 2 GiB per-asset limit. GitHub documents no total release-size or bandwidth limit in [About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases). No Git LFS objects, paid plan, new access grant or billing change is used by this consolidation. The preservation release is a prerelease so it does not replace the existing Godot latest release.

See [`INVENTORY.csv`](docs/consolidation/INVENTORY.csv) for each known source path, byte size, disposition, and hashes of included files. Source roots are recorded as relative aliases rather than private machine paths. [`INVENTORY_SUMMARY.json`](docs/consolidation/INVENTORY_SUMMARY.json) aggregates every disposition. [`SHA256SUMS.txt`](docs/consolidation/SHA256SUMS.txt) identifies release archives.

## Intentionally local and pending material

- **214 files, 11,835,303,002 bytes:** original trailer audio, audio-bearing video, or Blender scenes with soundtrack sound datablocks. Soundtrack redistribution rights were not established; many scenes contain packed music, so omitting only the standalone WAV would be insufficient.
- **87 Blender files, 490,290,116 bytes:** embedded text contains private Library references or sensitive identifiers. These need sanitized distribution copies before public archival.
- **Two reference FBX files, 754,672 bytes:** standalone model/animation rights were not established.
- Standalone vendor libraries, including Quaternius's unresolved archive CC0/current QAL conflict, remain local. Acquisition receipts and instructions are preserved instead. No Fab/Mixamo acquisition is newly claimed.
- Engine installations, build/debug products, saves, simulation caches, backups, numbered render frames, silent assembly segments, duplicate packages, control/session records, and four 48-byte failed MP4 placeholders remain local. Exact paths and counts are accounted for in the inventory.

No original file was moved, deleted or edited. Original code, story and artwork retain their owner's rights; this preservation work grants no blanket open-source license. Third-party notices remain applicable.

## Evidence limits

The source, archive identity, privacy/rights screens and ZIP CRC checks were performed for preservation. Blender was inspected in background with embedded Python disabled, loading selected sound/text/image metadata without saving scenes. The included cleared scenes use packed image dependencies. Movies in the production archive were checked for video streams and the absence of audio streams.

Recorded gameplay tests and render studies remain historical evidence with their original scope. No engine playtest, Godot development pass, new art approval, companion carrying, or finished cinematic-quality claim is made by this consolidation.
