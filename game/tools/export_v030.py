from pathlib import Path
import subprocess,json,hashlib,argparse
P=Path(__file__).resolve().parents[1]; E=P/'evidence/v030';E.mkdir(parents=True,exist_ok=True)
engine=P/'tools/godot/Godot_v4.6-stable_win64_console.exe'
a=argparse.ArgumentParser();a.add_argument('--candidate',action='store_true');args=a.parse_args()
exe=P/('build/v0.3.0-candidate/When the Sky Clears.exe' if args.candidate else 'build/v0.3.0/When the Sky Clears.exe')
exe.parent.mkdir(parents=True,exist_ok=True)
for name,extra in [('import',['--editor','--import','--quit']),('export',['--export-release','Windows Desktop',str(exe)])]:
    command=[str(engine),'--headless','--path',str(P)]+extra
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
    (E/f'{name}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf8')
    if r.returncode or 'SCRIPT ERROR' in r.stderr or 'Parse Error' in r.stderr:print(r.stdout[-2000:],r.stderr);raise SystemExit(r.returncode or 1)
    print(name,'OK')
data={'build':'0.3.0','executable':str(exe.relative_to(P)),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'bytes':exe.stat().st_size,'source':{str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['scripts','levels'] for p in sorted((P/folder).glob('*')) if p.suffix in ['.gd','.json']}}
(E/'EXPORT_IDENTITY.json').write_text(json.dumps(data,indent=2))
print('EXPORTED',data['bytes'],data['sha256'])
