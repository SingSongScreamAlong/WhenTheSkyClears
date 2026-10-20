"""Run isolated native QA, retaining exact invocation, logs and exit status."""
from pathlib import Path
import subprocess, argparse, json, time, hashlib
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser()
a.add_argument('kind', choices=['smoke','survival','encounters','journey-checks','traverse','capture-new','motion','side-routes'])
a.add_argument('--release',action='store_true')
a.add_argument('--candidate',action='store_true')
a.add_argument('--evidence-tag')
args=a.parse_args()
d=P/'evidence/v030'/(args.evidence_tag or ('candidate_' if args.candidate else ('packaged_' if args.release else 'source_')))/args.kind
d.mkdir(parents=True,exist_ok=True)
cmd=[str(P/('build/v0.3.0-candidate/When the Sky Clears.exe' if args.candidate else 'build/v0.3.0/When the Sky Clears.exe'))] if args.release or args.candidate else [str(P/'tools/godot/Godot_v4.6-stable_win64_console.exe'),'--path',str(P)]
if args.kind not in ['capture-new','motion']:cmd+=['--headless']
cmd+=['--fixed-fps','30' if args.kind=='motion' else '60','--log-file',str(d/'engine.log'),'--','--evidence-dir',str(d),'--'+args.kind]
start=time.monotonic()
executable_sha256=hashlib.sha256(Path(cmd[0]).read_bytes()).hexdigest()
try:
    r=subprocess.run(cmd,cwd=P,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
    (d/'stdout.log').write_text(r.stdout,encoding='utf8');(d/'stderr.log').write_text(r.stderr,encoding='utf8')
    logged_errors=any(s in r.stderr for s in ['ERROR:','SCRIPT ERROR'])
    code=r.returncode or (1 if logged_errors else 0)
    report=dict(command=cmd,exe_sha256=executable_sha256,exit_code=code,native_exit_code=r.returncode,elapsed_seconds=round(time.monotonic()-start,2))
    (d/'invocation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
    if code: print(r.stderr[-3000:]);print(r.stdout[-2000:])
    raise SystemExit(code)
except subprocess.TimeoutExpired as e:
    (d/'timeout.json').write_text(json.dumps({'seconds':600,'command':cmd},indent=2))
    print('QA_TIMEOUT',args.kind);raise SystemExit(124)
