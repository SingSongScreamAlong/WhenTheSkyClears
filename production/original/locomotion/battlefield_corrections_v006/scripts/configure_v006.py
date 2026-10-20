import bpy
def configure_v006(start=1801,duration_scale=1.,root_motion=True,root=None):
    if root is None:
        roots=[o for o in bpy.context.scene.objects if o.get('motion_revision')=='v006_drawn_pose_corrections']
        if len(roots)!=1:raise ValueError('Pass exact appended correction controls object as root')
        root=roots[0]
    ids=[]
    for ob in [root,*root.children_recursive]:
        if ob.animation_data and ob.animation_data.nla_tracks:ids.append(ob)
        if ob.type=='MESH' and ob.data.shape_keys and ob.data.shape_keys.animation_data:ids.append(ob.data.shape_keys)
    seen=set()
    for id in ids:
        if id.as_pointer() in seen:continue
        seen.add(id.as_pointer());id.animation_data.action=None
        for track in id.animation_data.nla_tracks:
            track.mute=False;st=track.strips[0];end=start+119*duration_scale
            st.frame_end=max(st.frame_end,end+1);st.frame_start=start;st.action_frame_start=1;st.action_frame_end=120;st.repeat=1;st.scale=duration_scale;st.frame_end=end;st.extrapolation='HOLD'
    root['start_frame']=float(start);root['duration_frames']=119*duration_scale;root['root_motion']=float(root_motion);root['use_distance_curve']=1.;root['ground_speed_mps']=.5616666667/(119/24*duration_scale)
    for ob in [root,*root.children_recursive]:
        ob.update_tag(refresh={'OBJECT'})
        if ob.animation_data:
            for fc in ob.animation_data.drivers:fc.driver.expression=str(fc.driver.expression)
    bpy.context.view_layer.update()
    return {'start':start,'last_frame':start+119*duration_scale,'boundary':start+120*duration_scale,'root_motion':root_motion,'duration_scale':duration_scale,'distance_m':.5616666667}
