@echo off
cd /d "%~dp0"
if exist "build\v0.4.2\When the Sky Clears.exe" (
    start "" "build\v0.4.2\When the Sky Clears.exe" -- --sluice-preview
) else if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0." -- --sluice-preview
) else (
    echo Open project.godot in Godot 4.6 or extract the Windows 0.4.2 ZIP.
    pause
)
