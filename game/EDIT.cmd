@echo off
cd /d "%~dp0"
if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --editor --path "%~dp0."
) else (
    echo Open project.godot from the Godot 4.6 project manager.
    echo The editable source ZIP does not bundle the Godot editor.
    pause
)
