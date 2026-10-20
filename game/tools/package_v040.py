"""Package only the verified v040 executable and editable Godot game source."""
from pathlib import Path
import json,hashlib,zipfile,shutil
P=Path(__file__).resolve().parents[1];E=P/'evidence/v040';B=P/'build/v0.4.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
exe=B/'When the Sky Clears.exe';binary_hash=sha(exe)
files={'crossing-checks':'crossing_checks.json','smoke':'runtime_smoke.json','survival':'survival_consequences.json','encounters':'encounter_checks.json','journey-checks':'journey_checks.json','side-routes':'side_route_checks.json','traverse':'continuous_traversal.json'}
reports={}
for kind,name in files.items():
 d=E/'packaged'/kind;inv=json.loads((d/'invocation.json').read_text());report=json.loads((d/name).read_text())
 assert inv['exit_code']==0 and not inv['logged_errors'] and inv['exe_sha256']==binary_hash,kind
 assert report.get('all_passed',report.get('completed',False)),kind
 assert not any(x in ((d/'engine.log').read_text(encoding='utf8')+(d/'stderr.log').read_text(encoding='utf8')) for x in ['ERROR:','SCRIPT ERROR','WARNING:']),kind
 reports[kind]=report
source={}
for folder in ['scripts','levels','scenes','assets']:
 for p in sorted((P/folder).rglob('*')):
  if p.is_file() and p.suffix not in ['.import']:source[str(p.relative_to(P)).replace('\\','/')]=sha(p)
for name in ['project.godot','export_presets.cfg']:source[name]=sha(P/name)
capture=json.loads((E/'packaged/crossing-capture/capture_report.json').read_text())
assert capture['reached_gate'] and capture['deaths']==0
manifest={'version':'0.4.0','base_commit':'a59d984fea4420b1761f23e2f932d852129a6670','engine':'Godot 4.6 stable official','executable':{'bytes':exe.stat().st_size,'sha256':binary_hash},'checks':{k:len(v.get('checks',[])) for k,v in reports.items() if 'checks' in v},'journey':reports['traverse'],'crossing_capture':capture,'source_sha256':source,'preview_validation':json.loads((E/'preview_validation.json').read_text()),'limits':['Input-driven automation is not human playtesting or art approval.','No completed new motion export was integrated; existing assets retained.','Isolated save directory; no original personal save was present to migrate.','No GitHub push from this development checkout; repository consolidation is concurrent.']}
(E/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(E/'DELIVERY_MANIFEST.json',B/'BUILD_MANIFEST.json')
shutil.copy2(P/'DEVELOPMENT_v0.4.0.txt',B/'READ_ME.txt')
(B/'PLAY.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "When the Sky Clears.exe"\n')
(B/'FREIGHT_CROSSING.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "When the Sky Clears.exe" -- --freight-crossing\n')
if not (B/'licenses').exists():shutil.copytree(P.parent/'docs/licenses',B/'licenses')
for p in (P/'assets/fonts').rglob('*'):
 if p.is_file() and ('license' in p.name.lower() or 'ofl' in p.name.lower()):shutil.copy2(p,B/'licenses'/p.name)
shutil.copy2(P.parent/'docs/ASSET_SOURCES.md',B/'licenses/ASSET_SOURCES.md')
deliver=P.parent.parent/'deliverables';deliver.mkdir(exist_ok=True)
for kind in ['Windows','Editable_Source']:
 target=deliver/f'When_The_Sky_Clears_{kind}_v0.4.0.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  if kind=='Windows':
   for p in sorted(B.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(B))
  else:
   for folder in ['assets','scripts','scenes','levels']:
    for p in sorted((P/folder).rglob('*')):
     if p.is_file() and p.suffix!='.import':z.write(p,p.relative_to(P))
   for name in ['project.godot','PLAY.cmd','FREIGHT_CROSSING.cmd','EDIT.cmd','DEVELOPMENT_v0.4.0.txt','SOURCE_SETUP.txt','.gitignore']:
    z.write(P/name,name)
   config=(P/'export_presets.cfg').read_text().replace('custom_template/debug="res://tools/windows_debug_x86_64.exe"','custom_template/debug=""').replace('custom_template/release="res://tools/windows_release_x86_64.exe"','custom_template/release=""')
   z.writestr('export_presets.cfg',config)
   for name in ['qa_v040.py','package_v040.py','setup_godot.py']:z.write(P/'tools'/name,'tools/'+name)
   z.write(P.parent/'docs/ASSET_SOURCES.md','docs/ASSET_SOURCES.md')
   for p in sorted((P.parent/'docs/licenses').glob('*')):
    if p.is_file():z.write(p,'docs/licenses/'+p.name)
   z.write(E/'DELIVERY_MANIFEST.json','evidence/v040/DELIVERY_MANIFEST.json')
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'sha256':sha(target)}),flush=True)
print('V040_DELIVERY_READY',json.dumps(manifest['checks']),flush=True)
