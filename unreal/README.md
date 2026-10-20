# Archived Unreal shelter study

This independent Unreal 5.8.3 C++ prototype studies one cutaway shelter, one nearby supply shop, finite search/return/deposit interactions, food/water/health, and save/reset behavior. The boy is controlled; the girl is a stationary shelter companion presence. Godot in `../game/` is the owner's selected active game project.

Checkpoints are preserved as separate editable folders:

- `v0.1.0/WTSC_Survival.uproject`: first shelter study.
- `v0.1.1/WTSC_Survival.uproject`: refinement and objective fixes. Both original Windows package variants are preserved in the archival release.
- `v0.1.2/WTSC_Survival.uproject`: later room art study.

Open the desired `.uproject` with a compatible installed Unreal Engine and C++ toolchain, or use that checkpoint's `Scripts/Unreal.ps1 -Action BuildEditor -EngineRoot <installed-engine>` helper. Native Content is included. Generated binaries, intermediates, engine dependencies and saved games are omitted. No engine installation or new EULA acceptance is performed by these archival files.

For standalone play, extract the corresponding `WTSC_Shelter_Study_Win64_*.zip` from the [preservation release](https://github.com/SingSongScreamAlong/WhenTheSkyClears/releases/tag/wtsc-preservation-2026-10-20). Preserve its complete directory tree. `Scripts/PlayPackaged.cmd` in source expects a locally generated `Saved/Packaged` build; the released ZIP supplies its own launcher.

`SourceAssets/EstablishedWTSC` preserves authorized project artwork, and `SourceAssets/AuthoredWestRoom` preserves custom room sources where present. Seven Poly Haven CC0 props are incorporated in native game Content with source attribution. Standalone raw vendor packs and static-source derivatives remain local; source URLs and checksums are in `../docs/acquisition/`. Optional re-staging requires a separately acquired collection via the `WTSC_ASSET_LIBRARY` environment variable. Building the existing native Content does not require that optional re-staging step.

Distribution config omits the editor-only Android file-server section. Private Library receipts were omitted and private identifiers in published textual evidence were redacted. Historical machine paths are replaced with `WTSC_LOCAL_WORKSPACE`/`WTSC_LOCAL_USER`; incidental archival helpers may require path adaptation. Native source and visible artwork were not developed further during preservation.

## Known v0.1.2 limitations

The pale jug floats near the table edge; bedding is blurred/stretched; shoulder gaps and stiff cutout motion remain; adjoining rooms, upper floor and exterior remain unfinished. Companion following/carrying and finished child animation are unimplemented. Prior eleven-check regression evidence and actual room captures are retained with their original scope; preservation did not rerun gameplay or establish artistic acceptance.
