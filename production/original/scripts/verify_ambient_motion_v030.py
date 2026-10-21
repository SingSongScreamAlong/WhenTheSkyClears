import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v030'
names=['v023 | Opening oak roots fence and path | one coherent surface','v016 | Woods | near rooted oaks','v016 | Woods | far silver canopy','v016 | Camp | pinned canvas and ropes','v030 | High crown foreground oak 0','v016 | Rooted grass 000','v016 | Bakery chimney | wisp 0']
points={};values={}
for frame in [1,73]:
    s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
    for name in names:
        ob=s.objects[name];ev=ob.evaluated_get(dg);mesh=ev.to_mesh();rows[name]=[tuple(v.co) for v in mesh.vertices];ev.to_mesh_clear()
    points[frame]=rows
    mat=s.objects['v015 | Painted village'].data.materials[0];nt=mat.node_tree
    values[str(frame)]={'window_flicker':nt.nodes['Warm pane flicker'].outputs[0].default_value,'wall_shadow_time':next(n for n in nt.nodes if n.type=='TEX_NOISE').inputs['W'].default_value}
changes=[]
for name in names:
    a,b=points[1][name],points[73][name];shift=max(sum((x-y)**2 for x,y in zip(p,q))**.5 for p,q in zip(a,b));assert shift>1e-7,(name,shift);changes.append({'object':name,'max_native_vertex_change_m':shift})
assert values['1']!=values['73']
invalid=[]
for ob in s.objects:
    if ob.type=='MESH' and ob.data.shape_keys and ob.data.shape_keys.animation_data:
        invalid += [ob.name+':'+f.data_path for f in ob.data.shape_keys.animation_data.drivers if not f.is_valid]
assert not invalid,invalid
report={'source':bpy.data.filepath,'frames':[1,73],'actual_evaluated_mesh_changes':changes,'actual_shader_values':values,'invalid_shape_drivers':invalid,'scope':'Native evaluated geometry and shader state, separate from camera parallax. Artistic motion quality remains subject to review.'}
(R/'notes/world_v016/ambient_motion_verified_v030.json').write_text(json.dumps(report,indent=2));print('NATIVE_AMBIENT_MOTION_PASSED',json.dumps(report),flush=True)
