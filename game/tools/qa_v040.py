"""Bounded native source/release checks with exact invocations and logs."""
from pathlib import Path
import argparse, subprocess, json, time, hashlib
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('kinds',nargs='+');a.add_argument('--release',action='store_true');a.add_argument('--tag',default='source');args=a.parse_args()
results=[]
for kind in args.kinds:
 d=P/'evidence/v040'/args.tag/kind;d.mkdir(parents=True,exist_ok=True)
 exe=P/('build/v0.4.0/When the Sky Clears.exe' if args.release else 'tools/godot/Godot_v4.6-stable_win64_console.exe')
 cmd=[str(exe)] + ([] if args.release else ['--path',str(P)])
 if kind not in ['crossing-capture','capture-new','motion']:cmd+=['--headless']
 cmd+=['--fixed-fps','60','--log-file',str(d/'engine.log'),'--','--evidence-dir',str(d),'--'+kind]
 start=time.monotonic()
 with (d/'stdout.log').open('w',encoding='utf8') as out,(d/'stderr.log').open('w',encoding='utf8') as err:
  try:r=subprocess.run(cmd,cwd=P,stdout=out,stderr=err,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 stderr=(d/'stderr.log').read_text(encoding='utf8')
 result={'kind':kind,'command':cmd,'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'exit_code':code,'elapsed_seconds':round(time.monotonic()-start,2),'logged_errors':'SCRIPT ERROR' in stderr or 'ERROR:' in stderr}
 (d/'invocation.json').write_text(json.dumps(result,indent=2));results.append(result)
 print(json.dumps(result),flush=True)
 if code or result['logged_errors']:print(stderr[-2400:],flush=True);break
raise SystemExit(1 if any(x['exit_code'] or x['logged_errors'] for x in results) else 0)
