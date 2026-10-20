# Work on the Godot game on macOS

Use **Godot 4.6 stable, Standard edition**. The project uses GDScript; the .NET
edition, Python, C++, Unreal, and Windows executables are not required to edit or
play it. Download the matching macOS editor from the
[official Godot 4.6 archive](https://godotengine.org/download/archive/4.6-stable/).

```sh
git clone --branch dev/last-house-before-crossing https://github.com/SingSongScreamAlong/WhenTheSkyClears.git
cd WhenTheSkyClears
```

Open Godot's Project Manager, choose **Import**, and select
`WhenTheSkyClears/game/project.godot`. Allow the initial asset import to finish,
then use **Run Project** (F5). The main scene is `game/scenes/main.tscn`.
The title screen offers **Last House before the Crossing**, the full journey and
**Freight crossing rehearsal**. Last House resumes its own checkpoint; pause and
choose **Begin Last House again** to restart that section.

The editable content is in `game/scripts`, `game/scenes`, `game/levels`, and
`game/assets`. Paintings, character atlases, fonts, motion JSON, and runtime audio
are included in Git. No asset service, account, plugin, or download is needed at
runtime. Asset provenance and third-party notices are in
[ASSET_SOURCES.md](ASSET_SOURCES.md) and `docs/licenses`.

Godot rebuilds the untracked `game/.godot` import cache on your Mac. Saves use
Godot's portable `user://` location in the separate `WhenTheSkyClears/v050`
user-data directory. Last House, rehearsal and full journey use separate save
files. Existing original/v040/v041 save folders are untouched.

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
refinement; see [the motion/composition notes](../game/DEVELOPMENT_v0.5.3.txt). Scripted route
durations are not human playtime estimates. This branch is a verified route
checkpoint; further art, animation, audio and accessibility work is pending.
