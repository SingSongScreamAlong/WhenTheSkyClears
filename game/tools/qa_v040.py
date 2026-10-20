"""Run an isolated native QA scenario with executable identity and complete logs."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import time

P = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('kind', choices=['smoke', 'survival', 'encounters', 'journey-checks',
    'side-routes', 'development-checks', 'movement-checks', 'mill-checks', 'mill-playthrough', 'story-checks', 'traverse', 'capture-v040', 'motion', 'crossing-checks', 'crossing-capture', 'animation-checks'])
parser.add_argument('--release', action='store_true')
parser.add_argument('--evidence-tag', default=None)
parser.add_argument('--engine', type=Path, default=P/'tools/godot/Godot_v4.6-stable_win64_console.exe')
args = parser.parse_args()
folder = P/'evidence/v040'/(args.evidence_tag or ('packaged' if args.release else 'source'))/args.kind
folder.mkdir(parents=True, exist_ok=True)
native_release = args.release and args.kind != 'animation-checks'
executable = P/'build/v0.4.0/When the Sky Clears.exe' if native_release else args.engine
command = [str(executable)] + ([] if native_release else ['--path', str(P)])
if args.kind not in ['capture-v040', 'motion', 'mill-playthrough', 'crossing-capture']:
    command += ['--headless']
else:
    command += ['--position', '-20000,-20000']
if args.kind == 'animation-checks':
    command += ['--script', 'res://scripts/animation_movement_checks.gd']
command += ['--fixed-fps', '30' if args.kind in ['motion', 'mill-playthrough'] else '60', '--log-file', str(folder/'engine.log'),
    '--', '--evidence-dir', str(folder), '--'+('mill-checks' if args.kind == 'mill-playthrough' else args.kind)]
if args.kind == 'mill-playthrough':
    command += ['--record-mill']
start = time.monotonic()
with executable.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
try:
    result = subprocess.run(command, cwd=P, capture_output=True, text=True, encoding='utf-8',
        errors='replace', timeout=900, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
except subprocess.TimeoutExpired:
    (folder/'timeout.json').write_text(json.dumps({'command': command, 'timeout_seconds': 900}, indent=2))
    raise SystemExit(124)
(folder/'stdout.log').write_text(result.stdout, encoding='utf-8')
(folder/'stderr.log').write_text(result.stderr, encoding='utf-8')
log = result.stdout+'\n'+result.stderr
errors = [line for line in log.splitlines() if 'ERROR:' in line or 'SCRIPT ERROR' in line]
code = result.returncode or (1 if errors else 0)
invocation = dict(command=command, exe_sha256=digest, exit_code=code,
    native_exit_code=result.returncode, elapsed_seconds=round(time.monotonic()-start, 2), engine_errors=errors)
if args.kind == 'animation-checks' and args.release:
    identity_path=P/'evidence/v040/EXPORT_IDENTITY.json'
    identity=json.loads(identity_path.read_text(encoding='utf-8'))
    assert all(hashlib.sha256((P/name).read_bytes()).hexdigest() == source_hash for name, source_hash in identity['source'].items())
    invocation['source']=identity['source']
    invocation['export_identity_sha256']=hashlib.sha256(identity_path.read_bytes()).hexdigest()
(folder/'invocation.json').write_text(json.dumps(invocation, indent=2), encoding='utf-8')
print(json.dumps({key:value for key,value in invocation.items() if key != "source"}))
if code:
    print(result.stdout[-4000:]); print(result.stderr[-4000:])
raise SystemExit(code)
