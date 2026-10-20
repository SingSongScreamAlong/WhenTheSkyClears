import bpy,json,hashlib,runpy,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
native=P/'native/WTSC_Battlefield_Weary_Stumble_5s_v005.blend'
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False)
for name in ['BATTLEFIELD_HANDOFF.txt','configure_battlefield.py']:
    text=bpy.data.texts.get(name) or bpy.data.texts.new(name);text.clear();text.write((P/name if name.endswith('.txt') else P/'scripts'/name).read_text())
root=next(o for o in bpy.context.scene.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');root['review_status']='Candidate for75-80s integrated proof. Waist/shoe/braid cleanup checked; cutout stiffness remains. Not cinematic acceptance.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
sha=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(native),link=False) as (src,dst):dst.collections=['WTSC_BATTLEFIELD_WEARY_PAIR_v005']
s.collection.children.link(dst.collections[0]);configure=runpy.run_path(str(P/'scripts/configure_battlefield.py'))['configure_battlefield'];config=configure(start=1801,root_motion=True)
root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');tr=next(o for o in root.children if 'TRAVEL' in o.name)
rows=[]
for f in [1801,1804,1825,1844,1881,1920]:
    s.frame_set(f);bpy.context.view_layer.update();rows.append({'frame':f,'time_s':(f-1)/24,'distance_m':tr.location.x})
assert len(bpy.data.actions)==3 and abs(rows[0]['distance_m'])<.00001 and abs(rows[-1]['distance_m']-.5616666667)<.00001
ranges=[{'object':o.name,'track':t.name,'start':t.strips[0].frame_start,'end':t.strips[0].frame_end,'scale':t.strips[0].scale,'extrapolation':t.strips[0].extrapolation} for o in root.children_recursive if o.animation_data for t in o.animation_data.nla_tracks]
assert all(abs(r['start']-1804)<.001 and abs(r['end']-1920)<.001 for r in ranges)
source=R/'locomotion/performance_v003/native/WTSC_Performance_Library_v003.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest();prior=json.loads((R/'locomotion/performance_v003/evidence/package_validation.json').read_text());expected=next(x['sha256'] for x in prior['native'] if x['file']==source.name);assert source_hash==expected
v=json.loads((P/'evidence/native_validation.json').read_text());v['native_sha256']=sha;v['fresh_append']={'actions':len(bpy.data.actions),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'config':config,'ranges':ranges,'travel_samples':rows};(P/'evidence/native_validation.json').write_text(json.dumps(v,indent=2))
archive=P/'WTSC_Battlefield_Weary_5s_Pack_v005.zip';files=[native,P/'BATTLEFIELD_HANDOFF.txt',P/'WTSC_BATTLEFIELD_WEARY_STUMBLE_Reel_v005.mp4',P/'WTSC_BATTLEFIELD_WEARY_STUMBLE_Contact_Sheet_v005.jpg']
files.extend((P/'scripts').glob('*.py'));files.extend((P/'evidence').glob('*.json'))
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
report={'native':str(native),'native_sha256':sha,'native_bytes':native.stat().st_size,'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'source_v003_preserved':source_hash==expected,'frames':[1801,1920],'seconds':[75,80],'review':'Motion candidate; remaining cutout stiffness, no cinematic-quality claim; parent handles placement/light/FX; child materials are emission.'}
(P/'evidence/final_handoff.json').write_text(json.dumps(report,indent=2));print('BATTLEFIELD_HANDOFF_FINAL',json.dumps(report),flush=True)
