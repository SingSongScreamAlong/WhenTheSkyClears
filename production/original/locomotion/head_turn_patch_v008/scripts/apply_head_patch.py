"""In-memory narrow patch. Never saves a file or changes body/root actions."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix
def apply_head_patch_v008(root,patch_path=None):
 if root.get('motion_revision')!='v007_drawn_pose_corrections':raise ValueError('Pass the exact existing v007 controls object')
 rig=next(o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')=='GIRL');target=next(o for o in rig.children if 'passing back-view drawing' in o.name)
 if target.get('head_turn_patch')=='WTSC_v008_2FRAME_HEAD':return {'already_applied':True,'target':target.name}
 if patch_path is None:patch_path=Path(__file__).resolve().parents[1]/'native/WTSC_Girl_Head_Turn_Patch_v008.blend'
 with bpy.data.libraries.load(str(patch_path),link=False) as (available,loaded):loaded.collections=['WTSC_GIRL_HEAD_TURN_PATCH_v008']
 collection=loaded.collections[0];source=next(o for o in collection.objects if o.get('head_turn_patch')=='WTSC_v008_2FRAME_HEAD')
 expected=json.loads(source['reference_head_rest_matrix']);actual=rig.data.bones['head'].matrix_local;error=max(abs(actual[i][j]-expected[i][j]) for i in range(4) for j in range(4));assert error<.00003,error
 start=float(root['start_frame']);scale=float(root['duration_frames'])/119.;s=bpy.context.scene;old_frame=s.frame_current;old_subframe=s.frame_subframe;pose_error=0
 for f,rows in json.loads(source['reference_head_pose_matrices']).items():
  t=start+(int(f)-1)*scale;s.frame_set(math.floor(t),subframe=t%1);bpy.context.view_layer.update();pose_error=max(pose_error,max(abs(rig.pose.bones['head'].matrix[i][j]-rows[i][j]) for i in range(4) for j in range(4)))
 assert pose_error<.00003,('Existing head pose differs from v007 source',pose_error)
 original=next(o for o in rig.children if 'original head and attached braid' in o.name);hairmat=original.data.materials[0];facemat=hairmat.copy();facemat.name='V008 | existing physical light, original charcoal face RGB';nt=facemat.node_tree;mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');value=nt.nodes.new('ShaderNodeValue');value.outputs[0].default_value=1;nt.links.new(value.outputs[0],mix.inputs[0])
 newdata=source.data;newdata.materials[0]=hairmat;newdata.materials[1]=facemat;old_data=target.data.name;target.data=newdata;target.vertex_groups.clear();group=target.vertex_groups.new(name='head');group.add(list(range(len(newdata.vertices))),1,'REPLACE')
 if len(newdata.materials)>3:newdata.materials[3]=facemat
 for mod in target.modifiers:
  if mod.type=='ARMATURE':mod.object=rig
 anim=newdata.shape_keys.animation_data
 for track in anim.nla_tracks:
  st=track.strips[0];end=start+119*scale;st.frame_end=max(st.frame_end,end+1);st.frame_start=start;st.action_frame_start=1;st.action_frame_end=120;st.scale=scale;st.repeat=1;st.frame_end=end;st.extrapolation='HOLD'
 target['head_turn_patch']='WTSC_v008_2FRAME_HEAD';target['v008_scope']='Mesh data and head weights only. Existing v007 object exposure1..120 and all body/root/foot actions retained.'
 for ob in list(collection.objects):bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(collection);s.frame_set(old_frame,subframe=old_subframe);bpy.context.view_layer.update()
 return {'already_applied':False,'target':target.name,'old_mesh_data':old_data,'new_mesh_data':newdata.name,'source_frames':[44,45],'global_frames':[start+43*scale,start+44*scale],'head_rest_error':error,'head_pose_error':pose_error,'scope':'Only the existing girl passing-head mesh, its weights and two-pose drawing clock. All original object exposures/rig/body/root/foot/hand/FX actions untouched.','materials':'Hair reuses actual target original-head material, face copies its physical-light response with native silhouette alpha; eye marks use measured original warm-white color.'}
