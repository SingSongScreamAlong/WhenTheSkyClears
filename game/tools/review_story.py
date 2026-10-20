"""Record the actual source and run a bounded native story/UI review."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--capture', action='store_true', help='Render staged 4K views with the actual GPU renderer')
parser.add_argument('--executable', type=Path, help='Check an exported review build instead of source')
parser.add_argument('--tag', default='verified')
args = parser.parse_args()
output = ROOT/'evidence/story_direction_v1'/args.tag
output.mkdir(parents=True, exist_ok=True)
engine = ROOT/'tools/godot/Godot_v4.6-stable_win64_console.exe'
exe = args.executable.resolve() if args.executable else engine
command = [str(exe)] + ([] if args.executable else ['--path', str(ROOT)])
if not args.capture:
    command.append('--headless')
command += ['--fixed-fps', '60', '--log-file', str(output/'engine.log'), '--',
            '--evidence-dir', str(output), '--capture-story' if args.capture else '--story-checks']

def identity():
    paths = [p for folder in ['scripts', 'levels', 'story'] for p in (ROOT/folder).rglob('*')
             if p.suffix in ['.gd', '.json']]
    paths += [ROOT/'project.godot', ROOT/'export_presets.cfg']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

before = identity()
started = time.monotonic()
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                        encoding='utf-8', errors='replace', timeout=300,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
(output/'stdout.log').write_text(result.stdout, encoding='utf-8')
(output/'stderr.log').write_text(result.stderr, encoding='utf-8')
after = identity()
errors = [line for line in (result.stdout+'\n'+result.stderr).splitlines()
          if 'ERROR:' in line or 'SCRIPT ERROR' in line]
record = dict(command=command, native_exit_code=result.returncode,
              elapsed_seconds=round(time.monotonic()-started, 2), errors=errors,
              source_before=before, source_after=after, source_unchanged=before==after,
              executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
(output/'invocation.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
report = json.loads((output/'story_checks.json').read_text(encoding='utf-8')) if (output/'story_checks.json').exists() else {}
success = result.returncode==0 and not errors and report.get('all_passed', False)
print(json.dumps(dict(passed=success, checks=len(report.get('checks', [])),
                     source_unchanged=before==after, output=str(output))))
if not success:
    print(result.stderr[-4000:])
raise SystemExit(0 if success else 1)
