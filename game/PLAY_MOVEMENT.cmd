@echo off
cd /d "%~dp0"
if exist "build\animation_movement_v040\When the Sky Clears.exe" (
    start "" "build\animation_movement_v040\When the Sky Clears.exe"
) else if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0."
) else (
    echo Build this movement candidate with python tools\build_movement.py.
    pause
)
