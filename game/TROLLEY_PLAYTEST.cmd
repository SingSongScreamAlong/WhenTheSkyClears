@echo off
cd /d "%~dp0"
if exist "build\v0.4.3\When the Sky Clears.exe" (
    start "" "build\v0.4.3\When the Sky Clears.exe" -- --trolley-preview
) else if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0." -- --trolley-preview
) else (
    echo Extract the Windows build ZIP and use TROLLEY_PLAYTEST.cmd.
    echo To edit this source, open project.godot in Godot 4.6 or run python tools\setup_godot.py.
    pause
)
