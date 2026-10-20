"""Export the focused movement candidate without replacing previous builds."""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parents[1]
E = P / 'evidence/v040/animation_movement'
OUT = P / 'build/animation_movement_v040'
ENGINE = P / 'tools/godot/Godot_v4.6-stable_win64_console.exe'
OUT.mkdir(parents=True, exist_ok=True)
E.mkdir(parents=True, exist_ok=True)

def identity():
    files = [p for name in ['scripts', 'levels', 'scenes', 'story'] for p in (P/name).glob('*')
             if p.suffix in ['.gd', '.json', '.tscn']]
    files += [P/'project.godot', P/'export_presets.cfg']
    return {p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}

for stage, extra in [('import', ['--editor', '--import', '--quit']),
                     ('export', ['--export-release', 'Windows Desktop', str(OUT/'When the Sky Clears.exe')])]:
    before = identity()
    result = subprocess.run([str(ENGINE), '--headless', '--path', str(P)] + extra,
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=240)
    log = result.stdout+'\n'+result.stderr
    (E/f'{stage}.log').write_text(log, encoding='utf-8')
    if result.returncode or 'ERROR:' in log or 'SCRIPT ERROR' in log:
        raise SystemExit(log[-6000:])
    if before != identity():
        raise SystemExit('Source changed during export; rerun to record a stable candidate.')
    print(stage, 'OK', flush=True)

exe = OUT/'When the Sky Clears.exe'
manifest = dict(candidate='Focused animation and movement pass, 20 October 2026',
                executable=exe.relative_to(P).as_posix(), bytes=exe.stat().st_size,
                exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(), source=identity())
(E/'BUILD_IDENTITY.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(OUT/'READ_ME.txt').write_text(
    'WHEN THE SKY CLEARS - ANIMATION AND MOVEMENT CANDIDATE\n\n'
    'Run When the Sky Clears.exe. No Godot or Python installation is required.\n'
    'A/D or arrows: move. Shift: run. Space/W/Up: jump (tap or hold).\n'
    'S/Down: crouch. Hold E: interact or push. Q: companion wait/call.\n'
    'Esc: pause. Tab: pack. R: checkpoint recovery.\n\n'
    'This candidate includes the current local v0.4.0 campaign.\n'
    'The focused pass changes character movement, grounding and pose transitions.\n'
    'Artistic approval and wider game production remain separate.\n', encoding='utf-8')
(OUT/'Movement Practice.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "When the Sky Clears.exe" res://scenes/animation_review.tscn\n')
print(json.dumps(manifest, indent=2))
