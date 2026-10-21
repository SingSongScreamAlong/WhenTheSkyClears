"""Run in Blender Text Editor, then configure('WALK'). No installation needed.
Appended collections preserve all four clips as native NLA tracks.
"""
import bpy

def configure(clip='WALK',start=1,repeat=3,time_scale=1.,root_motion=False,root=None):
    if root is None:
        roots=[o for o in bpy.context.scene.objects if o.get('loco_pack')=='WTSC_LOCO_v001']
        if len(roots)!=1:raise ValueError('Pass root=the exact LOCO_PAIR CONTROLS object when more than one pack is appended')
        root=roots[0]
    riglist=[o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')]
    if len(riglist)!=2:raise ValueError('Expected the two original painted children under this root')
    chosen=[]
    for rig in riglist:
        rig.animation_data.action=None
        for track in rig.animation_data.nla_tracks:
            matches=[s for s in track.strips if s.action and '__'+clip+'__' in s.action.name]
            track.mute=not bool(matches)
            if matches:
                st=matches[0];N=int(st.action['period_frames'])
                st.action_frame_start=1;st.action_frame_end=N+1;st.repeat=repeat if st.action['loop'] else 1
                st.scale=time_scale;st.frame_start=start;st.extrapolation='NOTHING';st.blend_type='REPLACE'
                chosen.append(st)
    if len(chosen)!=2:raise ValueError('Clip missing: '+clip)
    root['start_frame']=float(start);root['root_motion']=float(root_motion)
    root['ground_speed_mps']=float(chosen[0].action['speed_mps'])/time_scale
    root.update_tag(refresh={'OBJECT'})
    for ob in root.children_recursive:ob.update_tag(refresh={'OBJECT'})
    bpy.context.view_layer.update()
    return {'clip':clip,'start':start,'end':max(s.frame_end for s in chosen),'root_speed_mps':root['ground_speed_mps'],'time_scale':time_scale,'root_motion':root_motion}

if __name__=='__main__':
    print('configure loaded. Call configure("WALK", repeat=3, time_scale=1, root_motion=False)')
