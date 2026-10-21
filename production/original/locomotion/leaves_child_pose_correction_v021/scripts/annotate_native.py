"""Embed v021 scope/timing notes and inspectable support metadata; no pose edit/render."""
import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
sol=json.loads((P/'evidence/coherent_pose_solution.json').read_text())
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def snapshots(r):
 out={}
 for p in sol['poses']:
  f=p['study_frame_30fps'];bpy.context.scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();out[p['index']]={o.name:pts(o) for o in r.children if o.type=='MESH'}
 return out
reports=[]
for name in ['WTSC_Child_Coherent_Support_Eight_Poses_v021.blend','WTSC_Child_Passing_Whole_Pose_Art_Study_v021.blend']:
 path=P/'native'/name;bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY'];before=snapshots(rig)
 for side in ['near','far']:
  pivot=bpy.data.objects['V020 | '+side+' | ACTUAL_SOLE_PIVOT']
  for p in sol['poses']+[dict(sol['poses'][0],study_frame_30fps=32)]:
   d=p['feet'][side];pivot['active_vertex']=d.get('vertex',-1);pivot.keyframe_insert('["active_vertex"]',frame=p['study_frame_30fps'])
  for l in pivot.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      if fc.data_path=='["active_vertex"]':
       for k in fc.keyframe_points:k.interpolation='CONSTANT'
 def hide_previews(lc):
  if lc.name.startswith('V020 |') and 'skeleton render' in lc.name:lc.hide_viewport=True
  for ch in lc.children:hide_previews(ch)
 for vl in S.view_layers:hide_previews(vl.layer_collection)
 bpy.data.objects['V020 | SOURCE52 | exact FBX sampled poses'].hide_set(True)
 for fn in ['V021_IMPORT_AND_REVIEW_GUIDE.txt','V021_RESOLVED_AND_REMAINING_REPORT.txt','V021_PHASE_TRAVEL_AND_SUPPORT_KEYS.csv','V021_REFERENCE_ANGLE_RESIDUALS.csv']:
  text=bpy.data.texts.get(fn) or bpy.data.texts.new(fn);text.clear();text.write((P/fn).read_text(encoding='utf-8'))
 S['V021_review_guide']='V021_IMPORT_AND_REVIEW_GUIDE.txt';S['V021_art_acceptance']='UNPASSED';S['V021_continuous_animation']='NOT_AUTHORED';S['V021_private_library_movie']='[PRIVATE_LIBRARY_REFERENCE_REMOVED]'
 after=snapshots(rig);err=max((a-b).length for i in before for n in before[i] for a,b in zip(before[i][n],after[i][n]))
 if err>1e-9:raise RuntimeError('Metadata annotation altered actual pose '+str(err))
 art='Art_Study' in name;f=25.25 if art else 1.;S.frame_set(int(f),subframe=f-int(f));S.camera=bpy.data.objects['V021 | ART WHOLE POSE CLOSE' if art else 'V020 | CHILD | CLOSE'];bpy.context.view_layer.update()
 col=bpy.data.collections['WTSC_CHILD_PASSING_ART_VARIANT_v021' if art else 'WTSC_CHILD_SUPPORT_POSES_v021']
 entry={'file':name,'pose_change_m':err,'viewport_pose_frame':f,'top_level_collection_objects':[{'name':o.name,'type':o.type} for o in col.all_objects if o.parent is None],'embedded_guides':4,'blender_version':bpy.app.version_string,'blender_build_hash':bpy.app.build_hash.decode(),'packed_images':[im.name for im in bpy.data.images if im.packed_file]}
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 reports.append(entry)
(P/'evidence/native_annotation_check.json').write_text(json.dumps(reports,indent=2))
print('V021_ANNOTATION',json.dumps([{'file':r['file'],'pose_change_m':r['pose_change_m'],'embedded_guides':r['embedded_guides'],'version':r['blender_version']} for r in reports]))

