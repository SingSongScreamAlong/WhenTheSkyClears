@echo off
cd /d "%~dp0"
if not exist "tools\godot\Godot_v4.6-stable_win64.exe" (
  echo Install the development engine with python tools\setup_godot.py
  pause
  exit /b 1
)
start "" "tools\godot\Godot_v4.6-stable_win64.exe" --path "%~dp0." -- --story-preview
