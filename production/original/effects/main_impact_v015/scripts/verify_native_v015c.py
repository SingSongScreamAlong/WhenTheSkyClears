"""Cold native source/context compare. Read-only; no rendering or saves."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];build=json.loads((P/'evidence/build_main_impact_v015c.json').read_text())
def matrix(m):return [float(v) for row in m for v in row]
def snapshot(s):
    bpy.context.window.scene=s
    root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
    rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
    light=bpy.data.objects['v043 OWNED | Brief eruption light']
    rows=[]
    for frame in range(1801,1921):
        s.frame_set(frame);bpy.context.view_layer.update()
        vals=matrix(s.camera.matrix_world)+matrix(root.matrix_world)+matrix(light.matrix_world)+[float(light.data.energy)]
        for who,rig in sorted(rigs.items()):
            for bone in sorted(rig.pose.bones,key=lambda p:p.name):vals+=matrix(bone.matrix)
        rows.append(vals)
    return rows
source=Path(build['source']);native=Path(build['native_context'])
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(source,native)}
bpy.ops.wm.open_mainfile(filepath=str(source));base=snapshot(bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047g'])
bpy.ops.wm.open_mainfile(filepath=str(native));new=snapshot(bpy.data.scenes[build['scene']])
error=max(abs(a-b)for aa,bb in zip(base,new)for a,b in zip(aa,bb));assert error==0,error
c=bpy.data.collections[build['collection']]
gp=[o for o in c.all_objects if o.type=='GREASEPENCIL']
assert len(gp)==4
assert not [o for o in c.all_objects if o.type in{'LIGHT','CAMERA','VOLUME'}]
invalid=[]
for owner in [*c.all_objects,*[o.data.shape_keys for o in c.all_objects if o.type=='MESH' and o.data.shape_keys]]:
    if owner.animation_data:
        invalid += [owner.name+':'+f.data_path for f in owner.animation_data.drivers if not f.driver.is_valid]
assert not invalid,invalid
preserved=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items());assert preserved
report={'cold_reopened_source_and_context':True,'all120_camera_root_bone_actual_light_max_error':error,
 'actual_light_energy_and_world_matrix_included':True,'source_and_context_hashes_preserved':preserved,
 'hidden_real_GP_objects':len(gp),'GP_contour_points':[sum(len(st.points)for l in o.data.layers for f in l.frames for st in f.drawing.strokes)for o in gp],
 'no_new_light_camera_volume':True,'invalid_native_drivers':invalid,
 'actual_render_review_separate':True,'artistic_acceptance':False}
(P/'evidence/cold_verification_v015c.json').write_text(json.dumps(report,indent=2))
print('PAINTED_IMPACT_COLD_VERIFIED',json.dumps(report),flush=True)
