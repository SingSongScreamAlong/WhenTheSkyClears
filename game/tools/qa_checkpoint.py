from pathlib import Path
import subprocess,json,argparse,time,hashlib
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('kinds',nargs='+');a.add_argument('--version',default='0.4.1');a.add_argument('--release',action='store_true');a.add_argument('--tag',default='source');args=a.parse_args()
for kind in args.kinds:
 d=P/('evidence/v'+args.version.replace('.',''))/args.tag/kind;d.mkdir(parents=True,exist_ok=True)
 exe=P/('build/v'+args.version+'/When the Sky Clears.exe' if args.release else 'tools/godot/Godot_v4.6-stable_win64_console.exe')
 cmd=[str(exe)]+([] if args.release else ['--path',str(P)])
 if kind not in ['crossing-capture','capture-new','motion','slice-capture','slice-shop-capture','access-checks','access-capture','audio-capture']:cmd+=['--headless']
 cmd+=([] if kind=='audio-capture' else ['--fixed-fps','30' if kind=='motion' else '60'])+['--log-file',str(d/'engine.log'),'--','--evidence-dir',str(d)]
 cmd+=(['--slice-capture','--shop-route'] if kind=='slice-shop-capture' else ['--'+kind])
 start=time.monotonic()
 with (d/'stdout.log').open('w',encoding='utf8') as out,(d/'stderr.log').open('w',encoding='utf8') as err:
  try:r=subprocess.run(cmd,cwd=P,stdout=out,stderr=err,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 errors=(d/'stderr.log').read_text(encoding='utf8');result={'kind':kind,'command':cmd,'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'exit_code':code,'logged_errors':'SCRIPT ERROR' in errors or 'ERROR:' in errors,'elapsed_seconds':round(time.monotonic()-start,2)}
 (d/'invocation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
 if code or result['logged_errors']:print(errors[-2500:],flush=True);raise SystemExit(1)
