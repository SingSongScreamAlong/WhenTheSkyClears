from pathlib import Path
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];E=P/'evidence/v020';B=P/'build/v0.2.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={}
for name,file in [('smoke','runtime_smoke.json'),('survival','survival_consequences.json'),('encounters','encounter_checks.json'),('traverse','continuous_traversal.json')]:
    reports[name]=json.loads((E/('packaged_'+name)/file).read_text())
    assert reports[name].get('all_passed',reports[name].get('completed',False)),name
shots=sorted((E/'native_4k_final').glob('*.png'))
assert len(shots)==6 and all(Image.open(p).size==(3840,2160) for p in shots)
motion=json.loads((E/'motion_review.json').read_text());video=json.loads((E/'motion_movie_validation.json').read_text())
assert video['decoded_frames']==360
prop=P/'assets/props/painted_survival_atlas_v020.png'
original=Path('C:/Users/conra/.codex/generated_images/01a155ac-2feb-7b40-9efe-28c1a20d8840/exec-2e04d90e-65bf-4d11-b49b-86932018dc99.png')
assert sha(prop)==sha(original)
manifest={'build':'0.2.0','date':'2026-10-19','executable':{'file':'build/v0.2.0/When the Sky Clears.exe','sha256':sha(B/'When the Sky Clears.exe'),'bytes':(B/'When the Sky Clears.exe').stat().st_size},
    'checks':{name:len(r['checks']) for name,r in reports.items() if 'checks' in r},'journey':reports['traverse'],'motion_study':motion,
    'graphics':{'renderer':'Vulkan Forward Mobile, RTX 5070 Ti Laptop GPU','msaa_2d':4,'captures':[{'file':str(p.relative_to(P)),'size':[3840,2160],'sha256':sha(p)} for p in shots]},
    'art':{'foreground_kit':str(prop.relative_to(P)),'generated_mode':'built-in ImageGen','actual_size':[1254,1254],'sha256':sha(prop),'source_pixels_preserved':True,'prompt':'assets/props/PROVENANCE_v020.txt'},
    'notes':['Prior build and original trailer sources preserved.','Native rigid-body crates, held/cancellable work, bridge collision, wetness, pump and shelter roof checks pass.','Continuous route includes one strength-related recovery; no actor repositioning or resource grants during the traversal.','Motion study is on an isolated flat fixture and does not establish artistic acceptance.','Development iteration; no claim of AAA finish, human playtest acceptance or full-length campaign.']}
(E/'DELIVERY_MANIFEST_v020.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(E/'DELIVERY_MANIFEST_v020.json',B/'BUILD_MANIFEST.json')
(B/'READ_ME.txt').write_text('PLAY THIS WINDOWS PACKAGE\nExtract the entire ZIP, then double-click When the Sky Clears.exe.\nGodot and Python are not needed to play.\nThe paths in the development notes below refer to the editable source project.\n\n'+(P/'DEVELOPMENT_v0.2.0.txt').read_text(encoding='utf-8'),encoding='utf-8')
for name in ['When_The_Sky_Clears_Windows_v0.2.0.zip','When_The_Sky_Clears_Editable_Source_v0.2.0.zip']:
    target=P/name
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        if 'Windows' in name:
            for p in sorted(B.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(B))
        else:
            files=[]
            for folder in ['assets','scripts','scenes','levels','previous/v0.1.0/levels']:
                files.extend(p for p in (P/folder).rglob('*') if p.is_file())
            files.extend(P/n for n in ['project.godot','export_presets.cfg','PLAY.cmd','EDIT.cmd','.gitignore','START_HERE.txt','DEVELOPMENT_v0.2.0.txt'])
            files.extend(p for p in (P/'tools').glob('*') if p.suffix=='.py' or p.name in ['SHA512-SUMS.txt','ENGINE_PROVENANCE.json'])
            files.extend(E.rglob('*.json'));files.append(P/'previous/.gdignore')
            for p in sorted(set(files)):z.write(p,p.relative_to(P))
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    print(name,target.stat().st_size,sha(target))
board=Image.new('RGB',(1600,900),(15,23,25));draw=ImageDraw.Draw(board)
labels=['VILLAGE / PUSHABLE CRATE','WOODS / CROSSING & LOGGING GATE','CAMP / COVER & SHELTER REPAIR','SCHOOL / FLOOD & DRAINAGE','ASH / THE LAST DOORWAY']
for i,p in enumerate(shots[1:]):
    x=i%3*536;y=i//3*340
    board.paste(Image.open(p).convert('RGB').resize((528,297)),(x,y));draw.text((x+10,y+311),labels[i],fill=(218,224,212))
draw.text((18,754),'WHEN THE SKY CLEARS | DEVELOPMENT 0.2.0 | AUTHORED LOCOMOTION AND REVISED SURVIVAL ENCOUNTERS',fill=(214,222,207))
draw.text((18,789),'Painted foreground kit | native pushed crates | held work and interruption | wetness and shelter | 4K runtime captures',fill=(152,173,164))
board.save(E/'V020_PLAYABLE_REVIEW.jpg',quality=93)
print('V020_DELIVERY_READY',json.dumps(manifest['checks']))
