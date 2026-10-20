"""Combine reviewed painted impact collection with retained character refinement.

Execute only after the isolated impact's actual key/consecutive-frame review.
No source is overwritten. Existing light, choreography and world are preserved.
"""
import bpy,json,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048'
a=json.loads((N/'build_v048a.json').read_text());selection=json.loads((R/'effects/main_impact_v015/evidence/selected_candidate.json').read_text());fx=json.loads(Path(selection['build_report']).read_text())
source=Path(bpy.data.filepath);assert str(source)==a['native'];assert hashlib.sha256(source.read_bytes()).hexdigest()==a['sha256']
assert (R/'effects/main_impact_v015/evidence/visual_review.json').exists(),'Review the actual impact first'
review=json.loads((R/'effects/main_impact_v015/evidence/visual_review.json').read_text());assert review['combine_candidate'],review
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v048b.blend';assert not out.exists()
s=bpy.data.scenes[a['world_scene']];m=bpy.data.scenes[a['master_scene']];bpy.context.window.scene=s
old=s.objects['FXv003 | fixed ground origin and controls'];old_visuals=[o for o in old.children_recursive if o.type in {'MESH','CURVE','GREASEPENCIL','VOLUME'}]
protected=set(s.objects)-set(old_visuals)
defs=ast.parse((R/'scripts/build_art_study_v045.py').read_text());defs.body=[n for n in defs.body if isinstance(n,ast.FunctionDef) and n.name in {'stable','props','curves','action_data','protected_fingerprint'}];exec(compile(defs,'native_protected_scope.py','exec'),globals())
fingerprint=protected_fingerprint()
staging=[];root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');rigs=[o for o in root.children_recursive if o.type=='ARMATURE'];light=s.objects['v043 OWNED | Brief eruption light']
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();staging.append({'frame':f,'camera':[list(v) for v in s.camera.matrix_world],'root':[list(v) for v in root.matrix_world],'FX':[list(v) for v in old.matrix_world],'light':[list(v) for v in light.matrix_world],'watts':light.data.energy,'bones':{r.name:{p.name:[list(v) for v in p.matrix] for p in r.pose.bones} for r in rigs}})
append=Path(fx['native_append']);append_sha=hashlib.sha256(append.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(append),link=False) as (src,dst):
 assert fx['collection'] in src.collections;dst.collections=[fx['collection']]
collection=dst.collections[0];s.collection.children.link(collection)
for ob in old_visuals:ob.animation_data_clear();ob.hide_render=True;ob.hide_viewport=True
assert protected_fingerprint()==fingerprint,'Unexpected change outside old visible FX'
errors={'camera':0.,'root':0.,'old_FX_controller':0.,'light_matrix':0.,'light_watts':0.,'all_pose_bones':0.}
for row in staging:
 s.frame_set(row['frame']);bpy.context.view_layer.update()
 for key,mat,ref in [('camera',s.camera.matrix_world,'camera'),('root',root.matrix_world,'root'),('old_FX_controller',old.matrix_world,'FX'),('light_matrix',light.matrix_world,'light')]:errors[key]=max(errors[key],max(abs(mat[i][j]-row[ref][i][j]) for i in range(4) for j in range(4)))
 errors['light_watts']=max(errors['light_watts'],abs(light.data.energy-row['watts']))
 for rig in rigs:
  for p in rig.pose.bones:errors['all_pose_bones']=max(errors['all_pose_bones'],max(abs(p.matrix[i][j]-row['bones'][rig.name][p.name][i][j]) for i in range(4) for j in range(4)))
assert max(errors.values())==0,errors
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v048b';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v048b'
report=dict(a);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,'parent_native':str(source),'parent_sha256':a['sha256'],'painted_impact_append':str(append),'painted_impact_sha256':append_sha,'painted_impact_collection':collection.name,'painted_impact_root':fx['root'],'disabled_old_FX_visuals':[o.name for o in old_visuals],'protected_original_ids':sorted(o.name for o in protected),'protected_original_fingerprint':fingerprint,'original_staging_all120':staging,'all120_staging_errors':errors,'scope':'Retained v048a shoulder/charcoal corrections plus original imagegen-painted soil rupture, native painted debris and persistent ground disturbance. Existing world, camera, actor acting, foot placement and original physical event light preserved.','artistic_acceptance':False,'full_trailer_propagated':False})
t=bpy.data.texts.new('CURRENT v048b | Painted impact review candidate');t.write(json.dumps({k:v for k,v in report.items() if k!='original_staging_all120'},indent=2))
bpy.context.window.scene=m;m.frame_set(1833);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v048b.json').write_text(json.dumps(report,indent=2))
assert hashlib.sha256(source.read_bytes()).hexdigest()==a['sha256'];assert hashlib.sha256(append.read_bytes()).hexdigest()==append_sha
print('V048B_COMBINED_NATIVE_SAVED',json.dumps({'native':str(out),'sha256':report['sha256'],'all120_errors':errors}),flush=True)
