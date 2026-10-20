"""Tie source, native binary, engine QA and rendered review to a versioned delivery."""
from pathlib import Path
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];E=P/'evidence/v030';B=P/'build/v0.3.0';C=E/'candidate_';F=E/'final_native_verified'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exe=B/'When the Sky Clears.exe';identity=json.loads((E/'EXPORT_IDENTITY.json').read_text())
assert sha(exe)==identity['sha256'],'Final executable differs from the verified candidate'
for name,expected in identity['source'].items(): assert sha(P/name)==expected,name
reports={}
files={'smoke':'runtime_smoke.json','survival':'survival_consequences.json','encounters':'encounter_checks.json','journey-checks':'journey_checks.json','side-routes':'side_route_checks.json','traverse':'continuous_traversal.json'}
for name,file in files.items():
    report=json.loads((C/name/file).read_text());invocation=json.loads((C/name/'invocation.json').read_text())
    assert report.get('all_passed',report.get('completed',False)),name
    assert invocation['exit_code']==0 and invocation['exe_sha256']==sha(exe),name
    log=(C/name/'engine.log').read_text(encoding='utf8')+(C/name/'stderr.log').read_text(encoding='utf8')
    assert not any(s in log for s in ['ERROR:','SCRIPT ERROR','WARNING:']),name
    reports[name]=report
for name in ['capture-new','motion']:
    invocation=json.loads((F/name/'invocation.json').read_text())
    assert invocation['exit_code']==0 and invocation['exe_sha256']==sha(exe),name
    log=(F/name/'engine.log').read_text(encoding='utf8')+(F/name/'stderr.log').read_text(encoding='utf8')
    assert not any(s in log for s in ['ERROR:','SCRIPT ERROR','WARNING:']),name
shots=sorted((F/'capture-new').glob('*.png'));assert len(shots)==6
assert all(Image.open(p).size==(3840,2160) for p in shots)
motion=json.loads((F/'motion/motion_review.json').read_text());video=json.loads((E/'motion_movie_validation.json').read_text())
assert video['decoded_frames']==360
levels=[json.loads((P/'levels'/f'{i:02}.json').read_text(encoding='utf8')) for i in range(1,6)]
art=P/'assets/environments/Rail_Yard_v030.png'
original=Path('C:/Users/conra/.codex/generated_images/01a155ac-2feb-7b40-9efe-28c1a20d8840/exec-846591ba-feeb-486d-b7ec-2230197ed5d2.png')
assert sha(art)==sha(original)
manifest={'build':'0.3.0','date':'2026-10-19','executable':{'file':str(exe.relative_to(P)),'bytes':exe.stat().st_size,'sha256':sha(exe)},'source':identity['source'],
    'journey_design':{'route_units':sum(l['width'] for l in levels),'previous_route_units':27600,'new_timed_lanes':sum(len(l['hazard_lanes']) for l in levels),'new_held_actions':sum(p['kind'] in ['relay','clear','brace'] for l in levels for p in l['interact']),'optional_supply_spurs':len(reports['side-routes']['routes'])},
    'checks':{name:len(r['checks']) for name,r in reports.items() if 'checks' in r},'journey':reports['traverse'],'motion_study':motion,'motion_movie':video,'terrain_geometry_audit':json.loads((E/'terrain_polygon_audit_current.json').read_text()),
    'graphics':{'renderer':'Vulkan Forward Mobile / RTX 5070 Ti Laptop GPU','msaa_2d':4,'captures':[{'file':str(p.relative_to(P)),'size':[3840,2160],'sha256':sha(p),'scope':'Character close study' if p.name.startswith('06_') else 'Native gameplay scene capture'} for p in shots]},
    'new_art':{'file':str(art.relative_to(P)),'sha256':sha(art),'size':list(Image.open(art).size),'generated_mode':'built-in ImageGen','source_pixels_preserved':True,'prompt':'assets/environments/Rail_Yard_PROVENANCE_v030.txt'},
    'notes':['All test invocations identify the exact binary hash copied to the final playable path.','Targeted setups and optional route fixtures are distinguished from continuous campaign navigation.','Original paintings, earlier builds and journey saves remain preserved in the workspace.','Source archive clears custom engine-template paths for standard Godot 4.6 templates; see SOURCE_SETUP.txt.','Route length is measured data; human playtime and artistic acceptance are not established.','Expanded development build; no claim of AAA production completion.']}
(E/'DELIVERY_MANIFEST_v030.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(E/'DELIVERY_MANIFEST_v030.json',B/'BUILD_MANIFEST.json')
(B/'READ_ME.txt').write_text('PLAY THIS WINDOWS PACKAGE\nExtract the entire ZIP, then double-click When the Sky Clears.exe.\nGodot and Python are not needed to play.\nDevelopment-note paths refer to the editable source project.\n\n'+(P/'DEVELOPMENT_v0.3.0.txt').read_text(encoding='utf8'),encoding='utf8')
shutil.copy2(P/'JOURNEY_v0.3.0.txt',B/'JOURNEY_DESIGN.txt')
report_dirs=[C/name for name in reports]+[F/'capture-new',F/'motion']
for name in ['When_The_Sky_Clears_Windows_v0.3.0.zip','When_The_Sky_Clears_Editable_Source_v0.3.0.zip']:
    target=P/name
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        if 'Windows' in name:
            for p in sorted(B.rglob('*')):
                if p.is_file() and p.suffix not in ['.tmp','.log']:z.write(p,p.relative_to(B))
        else:
            files=[]
            for folder in ['assets','scripts','scenes','levels','previous/v0.2.0/levels','previous/v0.1.0/levels']:
                files.extend(p for p in (P/folder).rglob('*') if p.is_file())
            files.extend(P/n for n in ['project.godot','export_presets.cfg','PLAY.cmd','EDIT.cmd','.gitignore','START_HERE.txt','SOURCE_SETUP.txt','DEVELOPMENT_v0.3.0.txt','JOURNEY_v0.3.0.txt','previous/.gdignore'])
            files.extend(p for p in (P/'tools').glob('*') if p.suffix in ['.py','.gd'] or p.name in ['ENGINE_PROVENANCE.json','SHA512-SUMS.txt'])
            for folder in report_dirs: files.extend(folder.glob('*.json'))
            files.extend([E/'EXPORT_IDENTITY.json',E/'DELIVERY_MANIFEST_v030.json',E/'motion_movie_validation.json',E/'terrain_polygon_audit_current.json'])
            for p in sorted(set(files)):
                if p.name=='export_presets.cfg':
                    config=p.read_text(encoding='utf8').replace('custom_template/debug="res://tools/windows_debug_x86_64.exe"','custom_template/debug=""').replace('custom_template/release="res://tools/windows_release_x86_64.exe"','custom_template/release=""')
                    z.writestr(p.relative_to(P).as_posix(),config)
                else:z.write(p,p.relative_to(P))
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    print(name,target.stat().st_size,sha(target))
board=Image.new('RGB',(1600,1010),(12,20,22));d=ImageDraw.Draw(board)
labels=['ORCHARD RIDGE / PROFILED COLLISION','RAIL PATH / NEW PAINTED STATION','FREIGHT ROUTE / SHARED WORK','COURTYARD / HOLLOW AND WATCHED EXIT','ASH GARDEN / THE LAST APPROACH','CHARACTER STUDY / CLOSER CAMERA']
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
for i,p in enumerate(shots):
    x=i%3*536;y=i//3*340
    board.paste(Image.open(p).convert('RGB').resize((528,297)),(x,y));d.text((x+8,y+310),labels[i],font=font,fill=(211,224,208))
d.text((20,744),'WHEN THE SKY CLEARS / DEVELOPMENT 0.3.0',font=font,fill=(216,225,209))
d.text((20,780),'Expanded authored journey | painted articulated children | collision-matched slopes | shared work | timed hazards',font=font,fill=(159,178,168))
d.text((20,815),'Native 4K scene captures. Last image is a character study at a closer camera zoom.',font=font,fill=(159,178,168))
board.save(E/'V030_PLAYABLE_REVIEW.jpg',quality=94)
print('V030_DELIVERY_READY',json.dumps(manifest['checks']),manifest['journey']['simulated_seconds'])
