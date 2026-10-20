# When The Sky Clears — Shelter Study

Separate editable Unreal C++ prototype, targeting the installed **Unreal 5.8.3**. Original trailer, Blender, Godot and Rod & Staff productions remain separate.

The native editor module compiled against Unreal 5.8.3. Seven props, their textures/materials, and the established paintings are real imported Unreal assets; the editable cutaway map reopened and saved cleanly. The rendered editor loop passed all eight checks. The Win64 package built successfully and its separate executable acceptance run is tracked in `Evidence/PackagedGameplayReplay.json` and `Evidence/BUILD_STATUS.json`. See [verification](Docs/VERIFICATION.md) for the exact tested state.

The first scope is one cutaway shelter, one small supply shop, and a walk/search/return/deposit loop. The established age-ten boy/girl faces are reused on clearly labelled provisional painted puppets. Motion, the girl's garment/body registration, custom architecture and lighting require real engine review. No ready-made child rig or companion carrying is claimed.

Run `Scripts/PlayPackaged.cmd` to play the local Win64 preview, or open `WTSC_Survival.uproject` in the installed Unreal 5.8.3 to edit the source/map. Actual engine screenshots and a short recorded MP4 are in `Evidence/`. `Scripts/Unreal.ps1 -Action BuildEditor` compiles; `-Action AuthorContent -ResourcesReleased` rebuilds the native content from copied sources; `-Action Replay -ResourcesReleased` runs the engine key-event acceptance route and records actual viewport frames. `-Action Package -ResourcesReleased` creates the Win64 build. The scripts use this exact project identity and never attach to another editor.

A/D or arrows walk; hold E at the supply cache; E deposits at shelter shelves. F/G/H use food/water/bandages at storage. R starts a fresh day; F5/F9 save/load; Esc pauses.

[Design](Docs/DESIGN.md) explains scope and unfinished character work. [Reuse and rights](Docs/REUSE_AND_RIGHTS.md) records the verified source assets, Fab/Mixamo blockers and Quaternius license conflict. The original download manifest is in `../WTSC_Survival_Game_Assets/MANIFEST.md`.
