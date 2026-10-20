import bpy,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];SRC=Path('WTSC_LOCAL_USER/Documents/Codex/2026-10-15/thi/outputs/The_War_on_Leaves_v13/assets/A_Walk_F_RootMotion_Masc.fbx')
operators={}
for id,op in [('import_scene.fbx',bpy.ops.import_scene.fbx),('wm.fbx_import',bpy.ops.wm.fbx_import)]:
 try:operators[id]=[p.identifier for p in op.get_rna_type().properties]
 except Exception as e:operators[id]={'error':str(e)}
print('FBX_OPERATORS',json.dumps(operators))
if isinstance(operators.get('import_scene.fbx'),list):bpy.ops.import_scene.fbx(filepath=str(SRC),use_anim=True)
else:raise RuntimeError('Verified legacy native FBX importer unavailable; inspect actual operator before continuing')
S=bpy.context.scene;rigs=[o for o in S.objects if o.type=='ARMATURE'];arm=rigs[0];action=arm.animation_data.action
keys=[]
for layer in action.layers:
 for st in layer.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:keys.extend(float(k.co.x) for k in fc.keyframe_points)
start,end=min(keys),max(keys);out={'source':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'fps':S.render.fps,'fps_base':S.render.fps_base,'scene_range':[S.frame_start,S.frame_end],'key_range':[start,end],'armature':arm.name,'object_matrix':[list(x) for x in arm.matrix_world],'action':action.name,'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length,'parent':b.parent.name if b.parent else None} for b in arm.data.bones},'objects':[{'name':o.name,'type':o.type} for o in S.objects],'samples':[]}
for i in range(int(round((end-start)*4))+1):
 f=start+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();out['samples'].append({'frame':f,'seconds':(f-start)/S.render.fps*S.render.fps_base,'armature_matrix':[list(x) for x in arm.matrix_world],'bones':{b.name:{'head':list(arm.matrix_world@b.head),'tail':list(arm.matrix_world@b.tail),'matrix':[list(x) for x in arm.matrix_world@b.matrix]} for b in arm.pose.bones}})
(P/'evidence/fbx_source_inspection.json').write_text(json.dumps(out,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/Leaves_Walk_Source_Inspection_v020.blend'),compress=True)
print('FBX_INSPECTION',json.dumps({k:v for k,v in out.items() if k not in ['samples','bones']}));print('BONES',list(out['bones']))
