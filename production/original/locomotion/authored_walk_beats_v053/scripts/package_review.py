import hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
old=ROOT/'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend';new=P/'native/WTSC_Authored_Walk_Beats_v053.blend';production=ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'
cold=json.loads((E/'COLD_CHECK.json').read_text());ab=json.loads((E/'ENCODED_MOTION_VALIDATION.json').read_text());full=json.loads((E/'FULLSIZE_ENCODED_VALIDATION.json').read_text())
assert sha(old)=='e888f7b7ab4c01040e675fc7d974e575a09df5e16f991897cae63629ec7dfd4f'
assert sha(new)==cold['source_hashes'][str(new)]
assert sha(production)=='f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'
for movie in (ab,full):assert sha(V/movie['file_name'])==movie['sha256'] and movie['decoded_frames']==257 and movie['bytes']<20_000_000
verified=[]
for kind,count in [('STATIC',1),('MOTION',2)]:
 v=json.loads((E/f'LIBRARY_VERIFIED_LIBRARY_{kind}_CREATE_RESULT.json').read_text());assert len(v)==count and all(x['metadata_verified'] and x['version']==0 for x in v);verified+=v
review={'status':'better visible pose contrast than v052; still a working study, no artistic approval',
 'observed_at_full_size':'The boy loads forward more clearly and both children have less matching elbow rhythm. The planted boots and painted shapes remain continuous in sampled full-size/native frames. Repeated cycles and side-on cutouts still make the movement feel constructed, especially the quiet girl and static expressions.',
 'actual_timing_change':"Explicit 0/3/8/12 and16/19/24/28 contact/loading/passing/push-off key phases. Appropriate opposite upper-arm swing retained. Boy/girl distinct amplitude and the girl's existing2frame lead retained.",
 'remaining_limits':'No recovery-to-walking restart, clasp, or acting across the full 75–80second scene. Static faces/hands, planar upper bodies, girl dress/braid and an exact repeating32frame stride restrict expressive quality. User Arcane-level target not met.',
 'continuous_player_observed_by_agent':False,'technical_export_not_artistic_approval':True}
delivery={'version':'v053','source_v051_sha256':sha(old),'candidate_sha256':sha(new),'source_and_production_unchanged':True,'contact_validation':cold,'movies':[ab,full],'private_library':[{k:r[k] for k in ('file_name','library_file_id','version','metadata_verified')} for r in verified],'review':review}
(E/'DELIVERY_METADATA.json').write_text(json.dumps(delivery,indent=2))
names=[
 'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend',
 'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend',
 'locomotion/connected_model_fit_v049/scripts/model_spec.py',
 'locomotion/authored_walk_beats_v053/IMPORT_TIMING_AND_ASSESSMENT_v053.txt',
 'locomotion/authored_walk_beats_v053/TRAVEL_CURVE_v053.csv',
]
names += [f'locomotion/authored_walk_beats_v053/scripts/{x}' for x in ('build_beats.py','cold_check.py','render_static.py','assemble_static.py','render_motion.py','encode_motion.py','encode_fullsize.py')]
names += [f'locomotion/authored_walk_beats_v053/evidence/{x}' for x in ('BEATS_BUILD.json','COLD_CHECK.json','STATIC_RENDER.json','ACTUAL_MOTION_RENDER.json','ENCODED_MOTION_VALIDATION.json','FULLSIZE_ENCODED_VALIDATION.json','DELIVERY_METADATA.json')]
names += [f'locomotion/authored_walk_beats_v053/previews/{x}' for x in ('WTSC_v051_v053_Matched_Pose_Beats.jpg','WTSC_v051_v053_Decoded_Motion_Review.jpg','WTSC_v051_vs_v053_Authored_Walk_Beats_NormalSpeed.mp4','WTSC_Authored_Walk_Beats_v053_Full_Size_NormalSpeed.mp4')]
assert len(names)==len(set(names));files=[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)} for n in names]
out=P/'WTSC_Authored_Walk_Beats_v053_Review.zip';assert not out.exists()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in files:z.write(ROOT/x['path'],x['path'])
 z.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':files},indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
assert sha(old)==delivery['source_v051_sha256'] and sha(new)==delivery['candidate_sha256']
delivery['archive']={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'zip_crc_verified':True,'file_count':len(files)+1}
(E/'FINAL_HANDOFF.json').write_text(json.dumps(delivery,indent=2))
print(json.dumps({'archive':delivery['archive'],'private_library':delivery['private_library']},indent=2))
