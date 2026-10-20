@echo off
cd /d "%~dp0"
if exist "build\v0.5.3\When the Sky Clears.exe" (
    start "" "build\v0.5.3\When the Sky Clears.exe"
) else if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0."
) else (
    echo Open project.godot in Godot 4.6 to play this editable source.
    pause
)
