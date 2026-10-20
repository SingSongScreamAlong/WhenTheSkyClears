"""Remove NLA strip evaluation lag; retain exact baked Bullet rigid transforms."""
import bpy,math,json,re
from pathlib import Path
from mathutils import Matrix,Quaternion,Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s;root=bpy.data.objects['FXv009 | impact anchor and controls'];root['start_frame']=7;root['speed']=1;root['size']=1
infos=json.loads((P/'evidence/build_ground.json').read_text())['debris'];report=[]
def drive(owner,path,expression,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    v=f.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["age"]';f.driver.expression=expression
for info in infos:
    ob=bpy.data.objects[info['name']];strip=ob.animation_data.nla_tracks[0].strips[0];action=strip.action;curves=[]
    for layer in action.layers:
        for st in layer.strips:
            for bag in st.channelbags:curves+=list(bag.fcurves)
    loc=[next(f for f in curves if f.data_path=='location' and f.array_index==i) for i in range(3)];rot=[next(f for f in curves if f.data_path=='rotation_quaternion' and f.array_index==i) for i in range(4)]
    verts=[v.co.copy() for v in ob.data.vertices];ob.animation_data_clear();ob.location=(0,0,0);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=(1,0,0,0);ob.scale=(1,1,1)
    errors=[]
    for age in range(114):
        fr=age+7;pos=Vector([f.evaluate(fr) for f in loc]);q=Quaternion([f.evaluate(fr) for f in rot]).normalized();mat=Matrix.Translation(pos)@q.to_matrix().to_4x4();k=ob.shape_key_add(name=f'RIGID_BULLET_AGE_{age:03d}');k.interpolation='KEY_LINEAR'
        for d,v in zip(k.data,verts):d.co=mat@v
        if age in [0,6,12,24,40,113]:
            original=(verts[0]-verts[-1]).length;actual=(k.data[0].co-k.data[-1].co).length;errors.append(abs(actual-original))
    ob.data.shape_keys.use_relative=False;drive(ob.data.shape_keys,'eval_time','10*max(0,min(113,t))')
    for a in range(3):drive(ob,'scale',f'1 if t>={info["launch_frame"]-7} else .0001',a)
    ob['construction']='Exact native Bullet rigid transforms sampled directly from original action curves and baked as absolute geometry keys; no NLA evaluation latency, no cloud deformation.'
    report.append({'object':ob.name,'keys':114,'max_rigid_edge_length_error':max(errors)})
    assert max(errors)<1e-5,report[-1]
root['construction']='Ground-first geometry. Exact Bullet clod transforms in age-driven native mesh keys; finite ballistic fine dirt. No smoke. Earlier NLA-based preview timings invalid and superseded.'
s.frame_set(20);root.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Ground_Debris_Proof_v009d.blend'),compress=True)
(P/'evidence/rigid_keys.json').write_text(json.dumps({'reason':'NLA strip_time driver evaluated after action sampling; offset test caught stale transforms despite valid driver flags. Earlier A/B/C previews are diagnostics, superseded.','source':'Original stored Bullet action FCurves evaluated directly, not the lagged NLA output.','pieces':report,'smoke':False},indent=2));print('RIGID_KEYS_DIRECT',len(report),flush=True)
