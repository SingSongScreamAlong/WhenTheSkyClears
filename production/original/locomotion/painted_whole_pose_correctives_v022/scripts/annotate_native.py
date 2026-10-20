import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];f=P/'native/WTSC_Painted_Whole_Pose_Correctives_v022.blend';bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False,use_scripts=False);S=bpy.context.scene
def pose_digest():
 deps=bpy.context.evaluated_depsgraph_get();rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('rig_revision')=='v016 painted linkage audit' and 'BOY' in o.name)
 data={o.name:[list(o.evaluated_get(deps).matrix_world@v.co) for v in o.evaluated_get(deps).data.vertices] for o in rig.children if o.type=='MESH'}
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
S.frame_set(25,subframe=.25);bpy.context.view_layer.update();before=pose_digest()
for name in ['V022_REVIEW_AND_EDIT_GUIDE.txt','V022_VISUAL_ASSESSMENT.txt']:
 t=bpy.data.texts.get(name) or bpy.data.texts.new(name);t.clear();t.write((P/name).read_text(encoding='utf-8'))
S['V022_artist_acceptance']='PARTIAL VISUAL GAIN / UNAPPROVED';S['V022_guide']='V022_REVIEW_AND_EDIT_GUIDE.txt';S['V022_continuous_cycle']='NOT_AUTHORED';S['V022_private_preview']='Saved; exact identity in external handoff receipt'
S.camera=bpy.data.objects['V022 | whole painted pose close'];after=pose_digest();assert before==after
bpy.ops.wm.save_as_mainfile(filepath=str(f),compress=True)
(P/'evidence/native_note_save_check.json').write_text(json.dumps({'native':f.name,'pose_geometry_digest_unchanged':before==after,'notes_embedded':2,'startup_frame':25.25,'blender':bpy.app.version_string},indent=2));print('V022_NATIVE_NOTES_SAVED')

