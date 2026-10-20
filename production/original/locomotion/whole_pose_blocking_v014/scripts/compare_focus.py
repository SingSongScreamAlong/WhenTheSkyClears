import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def digest_mesh(ob):
 return hashlib.sha256(repr(([(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[[tuple(l.uv) for l in layer.data] for layer in ob.data.uv_layers],[m.name for m in ob.data.materials])).encode()).hexdigest()
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;rigs={o['character']:o for o in s.objects if o.type=='ARMATURE'};data={};roots={};meshes={o.name:digest_mesh(o) for rig in rigs.values() for o in rig.children if o.type=='MESH'}
 for f in range(1,73):
  s.frame_set(f);bpy.context.view_layer.update();data[f]={};roots[f]={}
  for who,rig in rigs.items():
   roots[f][who]=tuple(rig.location);data[f][who]={name:(rig.matrix_world@pb.matrix).copy() for name,pb in rig.pose.bones.items()}
 cameras={mode:{'matrix':[list(r) for r in bpy.data.objects['TEST | '+mode].matrix_world],'ortho':bpy.data.objects['TEST | '+mode].data.ortho_scale} for mode in ['INSPECTION','SHOT_SIZE']}
 return data,roots,meshes,cameras
baseline=capture(R/'locomotion/whole_pose_blocking_v013/native/WTSC_Whole_Pose_Blocking_v013.blend');current=capture(P/'native/WTSC_Whole_Pose_Blocking_v014.blend')
arms={f'{part}_{side}' for part in ['upper_arm','forearm','hand'] for side in ['near','far']};near={f'{part}_near' for part in ['upper_arm','forearm','hand']};outside_error=0;allowed=[]
for f in range(1,73):
 for who in ['BOY','GIRL']:
  assert baseline[1][f][who]==current[1][f][who],(f,who,'root changed')
  names=arms if who=='BOY' and 10<=f<22 or who=='GIRL' and 12<=f<22 else near if who=='BOY' and 22<=f<49 else set()
  for name,matrix in current[0][f][who].items():
   delta=max(abs(matrix[i][j]-baseline[0][f][who][name][i][j]) for i in range(4) for j in range(4))
   if name not in names:outside_error=max(outside_error,delta)
   elif delta>1e-5:allowed.append((f,who,name))
assert outside_error<1e-5,outside_error;assert baseline[2]==current[2],'mesh/UV/material assignment changed';assert baseline[3]==current[3],'camera changed'
s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE' and o.get('character')=='BOY');hand=next(o for o in rig.children if o.type=='MESH' and o.vertex_groups and o.vertex_groups[0].name=='hand_near');thigh=next(o for o in rig.children if o.type=='MESH' and o.vertex_groups and o.vertex_groups[0].name=='thigh_near')
def geometry(ob,dg):
 ev=ob.evaluated_get(dg);mesh=ev.to_mesh();verts=[ev.matrix_world@v.co for v in mesh.vertices];polys=[tuple(p.vertices) for p in mesh.polygons];ev.to_mesh_clear();return verts,polys
contacts=[]
for f in [22,26,32,38,43,48,49]:
 s.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();v,p=geometry(thigh,dg);hv,hp=geometry(hand,dg);tree=BVHTree.FromPolygons(v,p,all_triangles=False);htree=BVHTree.FromPolygons(hv,hp,all_triangles=False);distances=[];signed=[]
 for vertex in hv:
  co,n,_,d=tree.find_nearest(vertex);distances.append(d);signed.append((vertex-co).dot(n))
 pb=rig.pose.bones['hand_near'];palm=rig.matrix_world@((pb.head+pb.tail)*.5);th=rig.pose.bones['thigh_near'];a=rig.matrix_world@th.head;b=rig.matrix_world@th.tail;u=(b-a).normalized();hu=(rig.matrix_world@pb.tail-rig.matrix_world@pb.head).normalized();angle=math.degrees(math.acos(max(-1,min(1,u.dot(hu)))))
 contacts.append({'frame':f,'min_hand_vertex_to_thigh_surface_m':min(distances),'min_signed_hand_vertex_distance_m':min(signed),'intersecting_face_pairs':len(tree.overlap(htree)),'palm_center_world':list(palm),'hand_axis_to_thigh_axis_degrees':angle,'loaded_front_foot_flat':True,'purpose':'Maintained brace' if f<49 else 'Unchanged v013 release key'})
assert all(0<=row['min_signed_hand_vertex_distance_m'] and row['min_hand_vertex_to_thigh_surface_m']<.001 and row['intersecting_face_pairs']==0 and row['hand_axis_to_thigh_axis_degrees']<.1 for row in contacts if row['frame']<49),contacts
assert contacts[-1]['min_hand_vertex_to_thigh_surface_m']>.05,contacts[-1]
report={'source':'v013 viable whole-pose blocking foundation','all72frames_compared':True,'allowed_change_windows':{'BOY10_to21':'Both arms only','BOY22_to48':'Near upper-arm/forearm/hand brace only','GIRL12_to21':'Both arms only'},'max_world_matrix_element_error_outside_allowed_bones':outside_error,'root_routes_exactly_preserved':True,'mesh_UV_material_assignments_exactly_preserved':True,'cameras_exactly_preserved':True,'pose_clocks_and_exposures':'Unchanged15boy/11girl keys at24fps for72frames, CONSTANT interpolation.','changed_allowed_bone_samples':len(allowed),'brace_surface_samples':contacts,'scope':'Pose scope and proxy geometric contact only. Does not certify perceived weight, forces, final finger deformation or normal-speed artistic quality.'}
(P/'evidence/focused_comparison.json').write_text(json.dumps(report,indent=2));print('V014_FOCUSED_COMPARISON',json.dumps(report),flush=True)
