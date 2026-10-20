import hashlib,json,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
src=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend';prod=ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'
assert sha(src)=='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
assert sha(prod)=='f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'
study=json.loads((E/'KEY_SHAPE_STUDY.json').read_text());boards=json.loads((E/'KEY_BOARD_ASSEMBLY.json').read_text())
assert study['source_unchanged'] and not study['saved_new_native'] and study['cell_inversions']==0 and len(study['records'])==6
assert sha(Path(boards['board']))==boards['sha256'] and sha(Path(boards['shot_size_board']))==boards['shot_size_sha256']
verified=json.loads((E/'LIBRARY_VERIFIED_LIBRARY_BOARDS_CREATE_RESULT.json').read_text());assert len(verified)==2 and all(x['metadata_verified'] and x['version']==0 for x in verified)
delivery={'version':'v054 key-shape visual study','source_sha256':sha(src),'source_and_production_unchanged':True,'native_v054_saved':False,'inbetweens_authored':False,'artistic_result':'Rejected: contour deformation remains barely visible at 1280x720 despite a16.16mm maximum local displacement. The dark sleeve/body painting obscures the shoulder transition. Preserve v053 as baseline.','technical_result':{'actual_key_pairs':6,'collar_and_skirt_anchors_unchanged':True,'cell_inversions':0,'max_body_vertex_displacement_m':study['body_max_vertex_delta_m']},'private_library_boards':[{k:x[k] for k in ('file_name','library_file_id','version','metadata_verified')} for x in verified]}
(E/'DELIVERY_METADATA.json').write_text(json.dumps(delivery,indent=2))
names=['locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend','locomotion/girl_torso_pose_v054/VISUAL_FINDING_v054.txt']
names += [f'locomotion/girl_torso_pose_v054/scripts/{n}' for n in ('inspect_girl.py','pose_shape_study.py','assemble_key_board.py')]
names += [f'locomotion/girl_torso_pose_v054/evidence/{n}' for n in ('GIRL_MESH_INSPECTION.json','KEY_SHAPE_STUDY.json','KEY_BOARD_ASSEMBLY.json','DELIVERY_METADATA.json')]
names += [f'locomotion/girl_torso_pose_v054/previews/{n}' for n in ('WTSC_v053_v054_Girl_Torso_Key_Shape_Board.jpg','WTSC_v053_v054_Girl_Torso_Actual_Shot_Size.jpg')]
for r in study['records']:
 for key in ('source','key_study'):
  path=Path(r[key]);assert path.is_relative_to(ROOT) and sha(path)==r[key+'_sha256' if key=='key_study' else 'source_sha256'];names.append(str(path.relative_to(ROOT)).replace('\\','/'))
assert len(names)==len(set(names));files=[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha(ROOT/n)} for n in names]
out=P/'WTSC_Girl_Torso_KeyShape_v054_Visual_Study.zip';assert not out.exists()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in files:z.write(ROOT/x['path'],x['path'])
 z.writestr('ARCHIVE_MANIFEST.json',json.dumps({'files':files},indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None and len(z.namelist())==len(files)+1
assert sha(src)==delivery['source_sha256']
delivery['archive']={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'zip_crc_verified':True,'file_count':len(files)+1}
(E/'FINAL_HANDOFF.json').write_text(json.dumps(delivery,indent=2));print(json.dumps({'archive':delivery['archive'],'boards':delivery['private_library_boards']},indent=2))
