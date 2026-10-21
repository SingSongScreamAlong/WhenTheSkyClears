import bpy
def configure_battlefield(start=1,time_scale=116/95,lead_in_frames=3,root_motion=True,root=None):
    if root is None:
        roots=[o for o in bpy.context.scene.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005']
        if len(roots)!=1:raise ValueError('Pass the exact appended BATTLEFIELD controls object as root')
        root=roots[0]
    riglist=[o for o in root.children_recursive if o.type=='ARMATURE'];distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE')
    for obj in riglist+[distance]:
        obj.animation_data.action=None
        for track in obj.animation_data.nla_tracks:
            track.mute=False;st=track.strips[0];target=start+lead_in_frames;end=target+95*time_scale
            # Enlarge the end first so Blender cannot clamp a far timeline start
            # against the strip's old local end. Then set the final scale/range.
            st.frame_end=max(float(st.frame_end),float(end)+1);st.frame_start=target
            st.action_frame_start=1;st.action_frame_end=96;st.repeat=1;st.scale=time_scale;st.frame_end=end;st.extrapolation='HOLD'
            if abs(st.frame_start-target)>.001 or abs(st.frame_end-end)>.001:raise ValueError('NLA range did not resolve: '+obj.name)
    root['root_motion']=float(root_motion);root['start_frame']=float(start+lead_in_frames);root['ground_speed_mps']=.28/time_scale;root['duration_frames']=95*time_scale;root['use_distance_curve']=1.
    for o in [root,*root.children_recursive]:
        o.update_tag(refresh={'OBJECT'})
        if o.animation_data:
            for f in o.animation_data.drivers:f.driver.expression=str(f.driver.expression)
    bpy.context.view_layer.update()
    return {'start':start,'action_start':start+lead_in_frames,'last_preview_frame':start+119,'boundary_frame':start+120,'time_scale':time_scale,'root_motion':root_motion,'total_local_distance_m':.5616666667}

