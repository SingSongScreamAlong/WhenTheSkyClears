import bpy
def configure(clip='PLAYFUL_SKIP',start=1,repeat=3,time_scale=1,root_motion=False,root=None):
    if root is None:
        roots=[o for o in bpy.context.scene.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v002']
        if len(roots)!=1:raise ValueError('Pass exact controls object as root')
        root=roots[0]
    riglist=[o for o in root.children_recursive if o.type=='ARMATURE'];travel=next(o for o in root.children if 'TRAVEL' in o.name);distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE')
    isloop=clip=='PLAYFUL_SKIP';N=40 if isloop else 96;v=.60 if isloop else .28
    for obj in riglist+[distance]:
        if not obj.animation_data:continue
        obj.animation_data.action=None
        for track in obj.animation_data.nla_tracks:
            track.mute=clip not in track.name
            if not track.mute:
                st=track.strips[0];st.action_frame_start=1;st.action_frame_end=N+1 if isloop else N;st.repeat=repeat if isloop else 1;st.scale=time_scale;st.frame_start=start;st.extrapolation='HOLD_FORWARD'
    if isloop:distance.location.x=0
    root['use_distance_curve']=0. if isloop else 1.
    root['root_motion']=float(root_motion);root['start_frame']=float(start);root['ground_speed_mps']=v/time_scale;root['duration_frames']=float((N*repeat if isloop else N-1)*time_scale)
    root.update_tag(refresh={'OBJECT'});travel.update_tag(refresh={'OBJECT'})
    for o in [root,*root.children_recursive]:
        o.update_tag(refresh={'OBJECT'})
        if o.animation_data:
            for fc in o.animation_data.drivers:fc.driver.expression=str(fc.driver.expression)
    bpy.context.view_layer.update()
    return {'clip':clip,'start':start,'frames':N,'repeat':repeat if isloop else 1,'time_scale':time_scale,'root_motion':root_motion}
