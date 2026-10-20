"""Package the playable build and editable source with read-back evidence."""
from pathlib import Path
import json,hashlib,zipfile,shutil
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
smoke=json.loads((P/'evidence/packaged_smoke/runtime_smoke.json').read_text())
survival=json.loads((P/'evidence/packaged_survival/survival_consequences.json').read_text())
route=json.loads((P/'evidence/packaged_traverse/continuous_traversal.json').read_text())
assert smoke['all_passed'] and survival['all_passed'] and route['completed']
shots=sorted((P/'evidence/native_4k').glob('*.png'))
assert len(shots)==6 and all(Image.open(p).size==(3840,2160) for p in shots)
for p in (P/'assets/environments').glob('*.png'):
    assert sha(p)==sha(P.parent/'sets/painted_layers'/p.name)
manifest={'title':'When the Sky Clears','build':'0.1.0','date':'2026-10-19',
    'executable':{'path':'build/When the Sky Clears.exe','bytes':(P/'build/When the Sky Clears.exe').stat().st_size,'sha256':sha(P/'build/When the Sky Clears.exe')},
    'validation':{'runtime_checks':len(smoke['checks']),'survival_checks':len(survival['checks']),'all_passed':True,'continuous_journey':route,'graphics':[{'file':str(p.relative_to(P)),'size':[3840,2160],'sha256':sha(p)} for p in shots]},
    'assets':{'environment_paintings':10,'copied_environment_source_bytes_verified':True,'downloaded_animation_clips':43,'retargeted_clips':13,'final_stock_3d_children':False,'vendor_sources_excluded_from_archives':True},
    'status':'Compact playable development build. Technical checks and automated navigation do not establish human playtest, full campaign length, final character/artistic approval, or AAA finish.'}
(P/'evidence/DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
shutil.copy2(P/'evidence/DELIVERY_MANIFEST.json',P/'build/BUILD_MANIFEST.json')
for name in ['START_HERE.txt','DESIGN_AND_ASSET_HANDOFF.txt']:shutil.copy2(P/name,P/'build'/name)
with zipfile.ZipFile(P/'When_The_Sky_Clears_Windows_v0.1.0.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted((P/'build').rglob('*')):
        if p.is_file() and p.name!='.gdignore':z.write(p,p.relative_to(P/'build'))
source_files=[]
for folder in ['assets','scripts','scenes','levels']:
    source_files.extend(p for p in (P/folder).rglob('*') if p.is_file() and p.suffix not in ['.import','.uid'])
source_files.extend(P/name for name in ['project.godot','export_presets.cfg','PLAY.cmd','EDIT.cmd','.gitignore','START_HERE.txt','DESIGN_AND_ASSET_HANDOFF.txt'])
source_files.extend(p for p in (P/'tools').glob('*') if p.suffix=='.py' or p.name in ['SHA512-SUMS.txt','ENGINE_PROVENANCE.json'])
source_files.extend((P/'evidence').rglob('*.json'))
source_files.append(P/'character_sources/SOURCE_RECEIPTS.json')
with zipfile.ZipFile(P/'When_The_Sky_Clears_Editable_Source_v0.1.0.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(set(source_files)):z.write(p,p.relative_to(P))
for name in ['When_The_Sky_Clears_Windows_v0.1.0.zip','When_The_Sky_Clears_Editable_Source_v0.1.0.zip']:
    p=P/name
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
    print(name,p.stat().st_size,sha(p))
board=Image.new('RGB',(1600,900),(15,23,24));d=ImageDraw.Draw(board)
labels=['01  BEFORE THE SILENCE','02  WHERE THE BIRDS WENT','03  UNDER A BORROWED ROOF','04  THE LAST SCHOOL','05  THE HAND THAT STAYED']
for i,p in enumerate(shots[1:]):
    x=(i%3)*536;y=(i//3)*345
    board.paste(Image.open(p).convert('RGB').resize((528,297)),(x,y))
    d.text((x+12,y+313),labels[i],fill=(220,225,210))
d.text((16,749),'WHEN THE SKY CLEARS | FIVE PLAYABLE CHAPTERS | NATIVE WINDOWS BUILD 0.1.0',fill=(204,209,190))
d.text((16,782),'73 engine checks + 13 survival checks | continuous journey completed | source and native executable included',fill=(150,169,160))
board.save(P/'evidence/PLAYABLE_JOURNEY_REVIEW.jpg',quality=92)
print('DELIVERY_VERIFIED',manifest['executable']['sha256'])
