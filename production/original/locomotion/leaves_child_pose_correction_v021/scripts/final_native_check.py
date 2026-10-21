import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def load(name):
 bpy.ops.wm.open_mainfile(filepath=str(P/'native'/name),load_ui=False,use_scripts=False);rigs,ctrl=api.initialize_from_scene();return bpy.context.scene,rigs['BOY'],ctrl
S,r,c=load('WTSC_Child_Coherent_Support_Eight_Poses_v021.blend');sol=json.loads((P/'evidence/coherent_pose_solution.json').read_text());rest=json.loads((P/'reference/child_rest_bones.json').read_text());S.frame_set(1);bpy.context.view_layer.update();base={o.name:pts(o) for o in r.children if o.type=='MESH'};S.frame_set(32);bpy.context.view_layer.update();stride=sol['cycle_stride_m'];loop_error=max((a+Vector((stride,0,0))-b).length for o in r.children if o.type=='MESH' for a,b in zip(base[o.name],pts(o)));length_error=max(abs(r.data.bones[n].length-v['length']) for n,v in rest.items());poses={}
for p in sol['poses']:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();poses[p['index']]={'bones':{b.name:[list(v) for v in b.matrix] for b in r.pose.bones},'boots':{o.name:pts(o) for o in r.children if o.get('v007_role')=='support_boot'}}
S,r,c=load('WTSC_Child_Passing_Whole_Pose_Art_Study_v021.blend');bone_error=boot_error=0.;all_reach=True
for p in sol['poses']:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();base=poses[p['index']];bone_error=max(bone_error,max(abs(b.matrix[i][j]-base['bones'][b.name][i][j]) for b in r.pose.bones for i in range(4) for j in range(4)));boot_error=max(boot_error,max((a-b).length for o in r.children if o.get('v007_role')=='support_boot' for a,b in zip(base['boots'][o.name],pts(o))));all_reach &=all(v['reachable'] for v in api.reach_report())
report={'duplicate_bookend_relative_mesh_error_m':loop_error,'rest_bone_length_change_m':length_error,'art_variant_skeleton_matrix_max_delta':bone_error,'art_variant_boot_vertices_max_delta_m':boot_error,'all_variant_native_chains_reachable':all_reach,'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'scope':'Eight selected poses and duplicate bookend only. No continuous gait, mass simulation or blend acceptance.','status':'PASS' if loop_error<.0001 and length_error<1e-8 and bone_error<1e-7 and boot_error<1e-7 and all_reach else 'FAIL'}
(P/'evidence/final_native_variants_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if report['status']!='PASS':raise RuntimeError('Final native preservation check failed')
