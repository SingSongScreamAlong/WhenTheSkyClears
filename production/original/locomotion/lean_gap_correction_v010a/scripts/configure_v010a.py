import bpy
def configure_v010a(start=1801,duration_scale=1.,root_motion=True,root=None,first=1,last=168):
 if root is None:
  roots=[o for o in bpy.context.scene.objects if o.get('motion_revision')=='v010a_lean_gap_correction'];assert len(roots)==1;root=roots[0]
 assert 1<=first<last<=168 and duration_scale>0
 ids=[]
 for ob in [root,*root.children_recursive]:
  if ob.animation_data and ob.animation_data.nla_tracks:ids.append(ob)
  if ob.type=='MESH' and ob.data.shape_keys and ob.data.shape_keys.animation_data:ids.append(ob.data.shape_keys)
 seen=set()
 for id in ids:
  if id.as_pointer() in seen:continue
  seen.add(id.as_pointer());id.animation_data.action=None
  for track in id.animation_data.nla_tracks:
   track.mute=False
   for st in track.strips:
    st.frame_end=max(st.frame_end,start+168*duration_scale+1);st.frame_start=start;st.action_frame_start=first;st.action_frame_end=last;st.repeat=1;st.scale=duration_scale;st.frame_end=start+(last-first)*duration_scale;st.extrapolation='HOLD'
 root['start_frame']=float(start);root['duration_frames']=(last-first)*duration_scale;root['root_motion']=float(root_motion);root['use_distance_curve']=1.;root['ground_speed_mps']=.288/duration_scale
 for ob in [root,*root.children_recursive]:
  ob.update_tag(refresh={'OBJECT'})
  if ob.animation_data:
   for fc in ob.animation_data.drivers:fc.driver.expression=str(fc.driver.expression)
 bpy.context.view_layer.update()
 return {'start':start,'last':start+(last-first)*duration_scale,'boundary':start+(last-first+1)*duration_scale,'source_range':[first,last],'duration_scale':duration_scale}
