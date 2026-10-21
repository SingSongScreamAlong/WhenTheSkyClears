import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P.parent/'loading_walk_refinement_v024/scripts'))
import motion_model as M
import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_GP_FIRST_ROUGH_v025.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];coat=bpy.data.objects['V025 | COAT drawings | editable GP'];api.initialize_from_scene();rows=[]
for i in range(61):
    f=17+i/4;q=f-1;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
    before=(rig.matrix_world@rig.pose.bones['chest'].tail).z
    delta=float(M.evaluate(q-1)['H'][1]-M.evaluate(q)['H'][1])
    for name in ['CHEST','WRIST_near','WRIST_far','ARM_POLE_near','ARM_POLE_far']:
        o=bpy.data.objects['BOY | '+name];mat=o.matrix_world.copy();mat.translation.z+=delta;o.matrix_world=mat;o.keyframe_insert('location',frame=f)
    bpy.context.view_layer.update();after=(rig.matrix_world@rig.pose.bones['chest'].tail).z
    rows.append({'frame':f,'pelvis_z':(rig.matrix_world@rig.pose.bones['pelvis'].head).z,'sternum_before_z':before,'sternum_after_z':after,'offset_m':delta,'unreachable':[x for x in api.reach_report() if not x['reachable']]})
for fr in coat.data.layers[0].frames:
    q=fr.frame_number-1;delta=float(M.evaluate(q-1)['H'][1]-M.evaluate(q)['H'][1]);S.frame_set(fr.frame_number);bpy.context.view_layer.update();H=rig.pose.bones['pelvis'].head
    for st in fr.drawing.strokes:
        for point in st.points:
            v=point.position.copy();t=max(0,min(1,(v.z-H.z)/.487));v.z+=delta*t*t*(3-2*t);point.position=v
    fr.drawing.tag_positions_changed()
diag=bpy.data.objects['V025 | bare torso diagnostic | optional'];layer=diag.data.layers[0]
for f in list(layer.frames):layer.frames.remove(f.frame_number)
def line(d,V,closed=False):
    d.add_strokes([len(V)]);s=d.strokes[-1];s.cyclic=closed
    for p,v in zip(s.points,V):p.position=(v.x,-.05,v.z);p.radius=.002;p.opacity=1
for f in range(17,33):
    S.frame_set(f);bpy.context.view_layer.update();d=layer.frames.new(f).drawing;H=rig.pose.bones['pelvis'].head;ch=rig.pose.bones['chest'].tail
    line(d,[H,H.lerp(ch,.5),ch]);line(d,[rig.pose.bones['upper_arm_near'].head,rig.pose.bones['upper_arm_far'].head])
    for centre,rx,rz in [(H,.055,.04),(H.lerp(ch,.72),.085,.125)]:line(d,[centre+Vector((rx*math.cos(a*2*math.pi/32),0,rz*math.sin(a*2*math.pi/32))) for a in range(32)],True)
    d.tag_positions_changed()
report={'samples':rows,'max_offset_m':max(abs(r['offset_m']) for r in rows),'pelvis_min_frame':min(rows,key=lambda r:r['pelvis_z'])['frame'],'sternum_before_min_frame':min(rows,key=lambda r:r['sternum_before_z'])['frame'],'sternum_after_min_frame':min(rows,key=lambda r:r['sternum_after_z'])['frame'],'unreachable_samples':sum(bool(r['unreachable']) for r in rows),'status':'CHECKS_ONLY_NOT_ART_PASS'}
(P/'evidence/UPPER_LOADING_v025b.json').write_text(json.dumps(report,indent=2));assert not report['unreachable_samples']
S['V025b_upper_loading']='Upper mass follows actual hipZ1frame later through small chest-origin translation; wrists/poles translate with upper body. Feet/root/rest bones retained; no separate head-bob curve.'
S.frame_set(21);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_GP_Upper_Loading_v025b.blend'),compress=True)
print(json.dumps({k:v for k,v in report.items() if k!='samples'}))
