import bpy,json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
rows=[]
for path in sorted((P/'native').glob('*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    for t in list(bpy.data.texts):
        if t.name!='configure_performance.py':bpy.data.texts.remove(t)
    for name in ['IMPORT_GUIDE.txt','ARTISTIC_REVIEW.txt','MOTION_STATUS.txt']:
        t=bpy.data.texts.new(name);t.write((P/name).read_text())
    for rig in [o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('character')]:
        rig['motion_status']='v003 cleanup study; native/contact tests pass. Artistic review open; see embedded guide.'
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    rows.append({'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actions':[a.name for a in bpy.data.actions],'packed_images':[i.name for i in bpy.data.images if i.packed_file]})
(P/'evidence/final_native_files.json').write_text(json.dumps(rows,indent=2))
before=json.loads((P/'evidence/preservation_before.json').read_text());preserved={n:hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in before.items()};assert all(preserved.values())
(P/'evidence/preservation_after.json').write_text(json.dumps(preserved,indent=2))
archive=P/'WTSC_Performance_Cleanup_Pack_v003.zip';files=[]
for folder in ['native','scripts','art']:
    files.extend(p for p in (P/folder).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.pyc'])
files.extend(p for p in (P/'evidence').glob('*.json') if 'library' not in p.name)
files.extend(P/n for n in ['IMPORT_GUIDE.txt','ARTISTIC_REVIEW.txt','MOTION_STATUS.txt','WTSC_PLAYFUL_SKIP_Reel_v003.mp4','WTSC_WEARY_STUMBLE_RECOVER_Reel_v003.mp4','WTSC_PLAYFUL_SKIP_Contact_Sheet_v003.jpg','WTSC_WEARY_STUMBLE_RECOVER_Contact_Sheet_v003.jpg'])
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'members':len(files),'native':rows,'preserved':preserved}
(P/'evidence/package_validation.json').write_text(json.dumps(report,indent=2));print('V003_NATIVE_PACKAGED',json.dumps(report),flush=True)
