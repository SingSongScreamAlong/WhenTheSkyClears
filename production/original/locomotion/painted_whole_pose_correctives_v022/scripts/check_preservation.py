"""Fresh native checks of the explicitly preserved v021 support and artwork."""
import bpy,json,sys,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
sol=json.loads((P/'reference/coherent_pose_solution_v021.json').read_text())
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def state(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY'];out={}
 for p in sol['poses']:
  f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
  out[p['name']]={'bones':{b.name:[list(v) for v in rig.matrix_world@b.matrix] for b in rig.pose.bones},'boots':{o.name:pts(o) for o in rig.children if o.get('v007_role')=='support_boot'},'meshes':{o.name:pts(o) for o in rig.children if o.type=='MESH' and (o.get('v007_role')!='drawn_leg' or p['name'] not in ['L_LOADING','L_PASSING'])},'travel':list(rig.parent.location),'IK':api.reach_report(),'art_visible':[o.name for o in bpy.data.collections.get('V022 | editable pose replacement drawings',[]).all_objects if o.type=='MESH' and not o.hide_render] if bpy.data.collections.get('V022 | editable pose replacement drawings') else []}
 original={o.name:{'vertices':[list(v.co) for v in o.data.vertices],'uv':[[list(v.uv) for v in l.data] for l in o.data.uv_layers]} for o in rig.children if o.type=='MESH'}
 images={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
 return out,original,images
A,base_data,base_images=state(P/'reference/BASE_COHERENT_SUPPORT_v021_COPY.blend')
B,new_data,new_images=state(P/'native/WTSC_Painted_Whole_Pose_Correctives_v022.blend')
bones=max(abs(A[n]['bones'][b][i][j]-B[n]['bones'][b][i][j]) for n in A for b in A[n]['bones'] for i in range(4) for j in range(4))
boots=max((a-b).length for n in A for o in A[n]['boots'] for a,b in zip(A[n]['boots'][o],B[n]['boots'][o]))
other=max((a-b).length for n in A if n not in ['L_LOADING','L_PASSING'] for o in A[n]['meshes'] for a,b in zip(A[n]['meshes'][o],B[n]['meshes'][o]))
unchanged_extras=max((a-b).length for n in A for o in A[n]['meshes'] if o!='LOCO_BOY | PAINT body' for a,b in zip(A[n]['meshes'][o],B[n]['meshes'][o]))
report={'support_bone_world_matrix_max_delta':bones,'boot_vertices_max_delta_m':boots,'other_six_selected_poses_original_mesh_max_delta_m':other,'head_arms_hands_original_mesh_max_delta_m':unchanged_extras,'base_vertex_and_UV_data_unchanged':base_data==new_data,'packed_paint_image_bytes_unchanged':base_images==new_images,'all_chains_reachable':all(k['reachable'] for v in B.values() for k in v['IK']),'replacement_drawing_visibility':{n:v['art_visible'] for n,v in B.items()},'actual_boot_minimum_z_by_phase':{n:{o:min(v.z for v in vv) for o,vv in v['boots'].items()} for n,v in B.items()},'scope':'Selected native pose/asset preservation, not visual acceptance or an in-between/cloth simulation pass','status':'PASS' if bones<1e-7 and boots<1e-7 and other<1e-7 and unchanged_extras<1e-7 and base_data==new_data and base_images==new_images and all(k['reachable'] for v in B.values() for k in v['IK']) else 'FAIL'}
(P/'evidence/fresh_native_preservation_check.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['replacement_drawing_visibility','actual_boot_minimum_z_by_phase']}))
if report['status']!='PASS':raise RuntimeError('Native preservation failed')

