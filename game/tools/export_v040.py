"""Export the Windows development build and record the exact source identity."""
from pathlib import Path
import hashlib
import json
import subprocess

P = Path(__file__).resolve().parents[1]
E = P/'evidence/v040'
E.mkdir(parents=True, exist_ok=True)
engine = P/'tools/godot/Godot_v4.6-stable_win64_console.exe'
exe = P/'build/v0.4.0/When the Sky Clears.exe'
exe.parent.mkdir(parents=True, exist_ok=True)
presets=P/"export_presets.cfg"
portable_presets=presets.read_text(encoding="utf-8")
try:
    for stage, extra in [('import', ['--editor', '--import', '--quit']),
                         ('export', ['--export-release', 'Windows Desktop', str(exe)])]:
        if stage == "export":
            presets.write_text(portable_presets.replace('custom_template/debug=""', 'custom_template/debug="res://tools/windows_debug_x86_64.exe"').replace('custom_template/release=""', 'custom_template/release="res://tools/windows_release_x86_64.exe"'), encoding="utf-8")
        command = [str(engine), '--headless', '--path', str(P)]+extra
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
            errors='replace', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        log = result.stdout+'\n'+result.stderr
        (E/(stage+'.log')).write_text(log, encoding='utf-8')
        if result.returncode or 'ERROR:' in log or 'SCRIPT ERROR' in log:
            print(log[-5000:]); raise SystemExit(result.returncode or 1)
        print(stage, 'OK', flush=True)
finally:
    presets.write_text(portable_presets, encoding="utf-8")
files = [p for name in ['scripts', 'levels', 'scenes'] for p in (P/name).rglob('*') if p.suffix in ['.gd', '.json', '.tscn']]
files += [P/'project.godot', P/'export_presets.cfg']
files += [p for folder in ['assets', 'story'] for p in (P/folder).rglob('*') if p.is_file()]
identity = dict(build='0.4.0', executable=exe.relative_to(P).as_posix(), bytes=exe.stat().st_size,
    sha256=hashlib.sha256(exe.read_bytes()).hexdigest(), source={
        p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
(E/'EXPORT_IDENTITY.json').write_text(json.dumps(identity, indent=2), encoding='utf-8')
print('EXPORTED', identity['bytes'], identity['sha256'])
