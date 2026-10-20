# Work on the Godot game on macOS

Use **Godot 4.6 stable, Standard edition**. The project uses GDScript; the .NET
edition, Python, C++, Unreal, and Windows executables are not required to edit or
play it. Download the matching macOS editor from the
[official Godot 4.6 archive](https://godotengine.org/download/archive/4.6-stable/).

```sh
git clone https://github.com/SingSongScreamAlong/WhenTheSkyClears.git
cd WhenTheSkyClears
```

Open Godot's Project Manager, choose **Import**, and select
`WhenTheSkyClears/game/project.godot`. Allow the initial asset import to finish,
then use **Run Project** (F5). The main scene is `game/scenes/main.tscn`.
The title screen offers the full journey and **Freight crossing rehearsal**.

The editable content is in `game/scripts`, `game/scenes`, `game/levels`, and
`game/assets`. Paintings, character atlases, fonts, motion JSON, and runtime audio
are included in Git. No asset service, account, plugin, or download is needed at
runtime. Asset provenance and third-party notices are in
[ASSET_SOURCES.md](ASSET_SOURCES.md) and `docs/licenses`.

Godot rebuilds the untracked `game/.godot` import cache on your Mac. Saves use
Godot's portable `user://` location in the separate `WhenTheSkyClears/v041`
user-data directory. The rehearsal has a separate save from the full journey.

The included export preset targets Windows, but its custom template paths are
empty so the source does not depend on a developer's Windows files. Export
templates are unnecessary for editor play. For a macOS application export,
install the matching Godot 4.6 export templates and create a macOS preset in the
editor; no macOS package is supplied or validated here.

The `.cmd` launchers, portable-engine setup helper, and QA/package/movie Python
helpers are conveniences for the MSI Windows workflow. Use the Godot editor to
run on macOS. Optional cross-platform native functional checks can be run with
your Godot command, for example:

```sh
godot --headless --path game --fixed-fps 60 -- --smoke
```

**Verification limits:** this checkpoint passed native Godot 4.6 checks and a
complete automated journey on Windows. Filename case and source dependencies
were checked for portability. No Mac runtime test was performed, and no Mac was
accessed. The procedural character animation and encounter timing still need
refinement; see [the pass notes](../game/DEVELOPMENT_v0.4.0.txt).
