@echo off
cd /d "%~dp0"
if exist "build\v0.4.3\When the Sky Clears.exe" (
    start "" "build\v0.4.3\When the Sky Clears.exe"
) else if exist "build\v0.4.2\When the Sky Clears.exe" (
    start "" "build\v0.4.2\When the Sky Clears.exe"
) else if exist "build\v0.4.1\When the Sky Clears.exe" (
    start "" "build\v0.4.1\When the Sky Clears.exe"
) else if exist "build\v0.4.0\When the Sky Clears.exe" (
    start "" "build\v0.4.0\When the Sky Clears.exe"
) else if exist "build\v0.3.0\When the Sky Clears.exe" (
    start "" "build\v0.3.0\When the Sky Clears.exe"
) else if exist "build\v0.2.0\When the Sky Clears.exe" (
    start "" "build\v0.2.0\When the Sky Clears.exe"
) else if exist "build\When the Sky Clears.exe" (
    start "" "build\When the Sky Clears.exe"
) else if exist "tools\godot\Godot_v4.6-stable_win64.exe" (
    start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0."
) else (
    echo Extract the Windows build ZIP and run When the Sky Clears.exe.
    echo To edit this source, open project.godot in Godot 4.6.
    pause
)
