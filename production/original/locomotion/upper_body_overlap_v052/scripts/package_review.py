import hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
cold=json.loads((E/'COLD_CHECK.json').read_text());movie=json.loads((E/'ENCODED_MOTION_VALIDATION.json').read_text())
old=ROOT/'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend';new=P/'native/WTSC_Support_Linked_Upper_Body_v052.blend';production=ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'
assert sha(old)=='e888f7b7ab4c01040e675fc7d974e575a09df5e16f991897cae63629ec7dfd4f'
assert sha(new)==cold['source_hashes'][str(new)]
assert sha(production)=='f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'
assert sha(V/movie['file_name'])==movie['sha256'] and movie['decoded_frames']==129 and movie['bytes']<20_000_000
verified=[]
for kind in ('STATIC','MOTION'):
 v=json.loads((E/f'LIBRARY_VERIFIED_LIBRARY_{kind}_CREATE_RESULT.json').read_text());assert len(v)==1 and v[0]['metadata_verified'] and v[0]['version']==0;verified+=v
review={'status':'technical candidate; no substantial artistic improvement established',
 'observed_at_shot_size':'The chest and elbow response is visually subtle in the matched stills and decoded normal-speed frames. The regular loop and flat character acting remain. Preserve v051 as the stronger visually confirmed baseline until this is judged in a player.',
 'actual_timing_change':'Boy near/far elbow correlation 1.00 to0.66; girl1.00 to0.60. Appropriate opposite arm swing retained. Pelvis/leg/boot trajectories exact.',
 'next_animation_work':'Author stronger, non-identical pose intent across the pair and across the recovery beat, with clear preparation/load/release and a true restart step. Keep foot contacts tied to world travel; review at final shot size.',
 'continuous_player_observed_by_agent':False,'technical_export_not_artistic_approval':True}
delivery={'version':'v052','source_v051_sha256':sha(old),'candidate_sha256':sha(new),'source_and_production_unchanged':True,'contacts':cold,'movie':movie,'private_library':[{k:r[k] for k in ('file_name','library_file_id','version','metadata_verified')} for r in verified],'review':review}
(E/'DELIVERY_METADATA.json').write_text(json.dumps(delivery,indent=2))
names=[
 'locomotion/upper_body_overlap_v052/native/WTSC_Support_Linked_Upper_Body_v052.blend',
 'locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend',
 'locomotion/connected_model_fit_v049/scripts/model_spec.py',
 'locomotion/upper_body_overlap_v052/IMPORT_TIMING_AND_ASSESSMENT_v052.txt',
 'locomotion/upper_body_overlap_v052/TRAVEL_CURVE_v052.csv',
]
names += [f'locomotion/upper_body_overlap_v052/scripts/{x}' for x in ('build_overlap.py','cold_check.py','render_static.py','assemble_static.py','render_motion.py','encode_motion.py')]
names += [f'locomotion/upper_body_overlap_v052/evidence/{x}' for x in ('UPPER_BODY_BUILD.json','COLD_CHECK.json','STATIC_RENDER.json','ACTUAL_MOTION_RENDER.json','ENCODED_MOTION_VALIDATION.json','DELIVERY_METADATA.json')]
names += [f'locomotion/upper_body_overlap_v052/previews/{x}' for x in ('WTSC_v051_v052_Matched_Static_Proof.jpg','WTSC_v051_v052_Decoded_Motion_Review.jpg','WTSC_v051_vs_v052_Support_Linked_Upper_Body_NormalSpeed.mp4')]
assert len(set(names))==len(names)
files=[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)} for n in names]
out=P/'WTSC_Support_Linked_Upper_Body_v052_Review.zip';assert not out.exists()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in files:z.write(ROOT/x['path'],x['path'])
 z.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':files},indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
assert sha(old)==delivery['source_v051_sha256'] and sha(new)==delivery['candidate_sha256']
delivery['archive']={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'zip_crc_verified':True,'file_count':len(files)+1}
(E/'FINAL_HANDOFF.json').write_text(json.dumps(delivery,indent=2))
print(json.dumps({'archive':delivery['archive'],'library_previews':delivery['private_library']},indent=2))
