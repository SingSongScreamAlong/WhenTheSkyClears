"""Technical evidence only. A numerical pass is not artistic acceptance."""
import bpy,math,json,hashlib,sys,struct
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];R=P.parents[1]
N=P/'native/WTSC_Painted_Rig_Capability_v016.blend'
SOURCE=R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'
bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False)
S=bpy.context.scene;sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
rigs,controls=api.initialize_from_scene();pack=bpy.data.collections['WTSC_PAINTED_RIG_CAPABILITY_v016'];meshes=[o for o in pack.all_objects if o.type=='MESH']
def points(o):
    bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [o.matrix_world@v.co for v in e.data.vertices]
def local_points(o,r):return [r.matrix_world.inverted()@v for v in points(o)]
def maxdelta(a,b):return max((x-y).length for x,y in zip(a,b))
def ik_errors():
    result=[]
    for w,r in rigs.items():
        for side in ['near','far']:
            for bone,ctrl in [('shin','ANKLE_'),('forearm','WRIST_')]:
                b=r.pose.bones[bone+'_'+side];goal=r.matrix_world.inverted()@controls[w,ctrl+side].matrix_world.translation
                result.append({'who':w,'bone':b.name,'error_m':(b.tail-goal).length})
    return result
def sole_checks():
    return [{'who':o.parent['character'],'side':o.name.rsplit(' ',1)[-1],'lowest_world_z_m':min(v.z for v in points(o))} for o in meshes if o.get('v007_role')=='support_boot']
def palm_gap(w):
    r=rigs[w];leg=next(o for o in meshes if o.parent==r and o.get('v007_role')=='drawn_leg' and o.name.endswith('near'));hand=next(o for o in meshes if o.parent==r and o.get('v007_role')=='drawn_hand' and o.name.endswith('near'))
    vs=local_points(leg,r);t=((vs[20]+vs[21])-(vs[12]+vs[13])).normalized();t.y=0;t.normalize();n=Vector((-t.z,0,t.x));surface=vs[17].copy();surface.y=0
    palm=local_points(hand,r)[:8]
    return min((v-surface).dot(n) for v in palm)
report={'scope':'TECHNICAL TESTS ONLY; no final-art or performance approval','blender':bpy.app.version_string,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'structure':{'armatures':len(rigs),'bones':{w:len(r.data.bones) for w,r in rigs.items()},'painted_meshes':len(meshes),'live_contour_meshes':sum(any(m.type=='NODES' for m in o.modifiers) for o in meshes),'old_POSE_shape_keys':sum(sum(k.name.startswith('POSE_') for k in o.data.shape_keys.key_blocks) for o in meshes if o.data.shape_keys)},'diagnostic_poses':[]}
boots=[o for o in meshes if o.get('v007_role')=='support_boot']
for f in range(1,222,20):
    S.frame_set(f);bpy.context.view_layer.update()
    report['diagnostic_poses'].append({'frame':f,'ik':ik_errors(),'soles':sole_checks(),'hand_shapes':{w:{s:{k:controls[w,'WRIST_'+s][k] for k in ['Reach','Brace','BraceFollow']} for s in ['near','far']} for w in rigs}})
S.frame_set(41);bpy.context.view_layer.update()
saved=[]
for o in [*controls.values(),*rigs.values()]:
    if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
before={o.name:points(o) for o in meshes};footbefore={o.name:points(o) for o in boots}
for w in rigs:
    ob=controls[w,'HIP'];M=ob.matrix_world.copy();M.translation+=Vector((.012,0,-.015));ob.matrix_world=M
bpy.context.view_layer.update()
report['off_cache_native_hip_edit']={'edit_m':[.012,0,-.015],'no_pose_api_or_handler_used':True,'mesh_response_m':{o.name:maxdelta(before[o.name],points(o)) for o in meshes if o.get('v007_role') in ['drawn_leg','drawn_arm','drawn_cuff']},'paint_body_response_m':{o.name:maxdelta(before[o.name],points(o)) for o in meshes if o.get('skin_region') in ['body','dress']},'boot_drift_m':{o.name:maxdelta(footbefore[o.name],points(o)) for o in boots},'ik':ik_errors()}
S.render.filepath=str(P/'previews/pose_OFF_CACHE_CONTROL_EDIT.png');bpy.ops.render.render(write_still=True)
for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
S.frame_set(161);bpy.context.view_layer.update();saved=[]
for o in [*controls.values(),*rigs.values()]:
    if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
brace=[];basefeet={o.name:points(o) for o in boots}
for dx,delta in [(0,0),(-.005,-.012),(.005,.009),(0,0)]:
    if not brace:basemats={w:controls[w,'HIP'].matrix_world.copy() for w in rigs}
    for w in rigs:
        M=basemats[w].copy();M.translation.z+=delta;M.translation.x+=dx;controls[w,'HIP'].matrix_world=M
    bpy.context.view_layer.update();brace.append({'hip_delta_x_m':dx,'hip_delta_z_m':delta,'projected_palm_edge_gap_m':{w:palm_gap(w) for w in rigs},'ik':ik_errors(),'boot_drift_m':{o.name:maxdelta(basefeet[o.name],points(o)) for o in boots}})
report['native_brace_follow']=brace
for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
S.frame_set(1);bpy.context.view_layer.update();saved=[]
for o in [*controls.values(),*rigs.values()]:
    if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
roll=[]
for w in rigs:
    for side in ['near','far']:
        boot=next(o for o in boots if o.parent==rigs[w] and o.name.endswith(side));baseline=[(a-b).length for a,b in zip(points(boot),points(boot)[1:])]
        for deg in [-15,-10,0,10,20,30,35,20,0,-10]:
            api.set_foot(w,side,-.10 if side=='far' else .13,deg,0)
            pp=points(boot);edge=[(a-b).length for a,b in zip(pp,pp[1:])]
            roll.append({'who':w,'side':side,'roll_degrees':deg,'min_world_z_m':min(v.z for v in pp),'rigid_edge_error_m':max(abs(a-b) for a,b in zip(baseline,edge))})
report['painted_boot_roll']=roll
for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
S.frame_set(1);bpy.context.view_layer.update();saved=[]
for o in [*controls.values(),*rigs.values()]:
    if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
headtests=[]
for w,r in rigs.items():
    head=next(o for o in meshes if o.parent==r and ('original head' in o.name));before=points(head);ctrl=controls[w,'HEAD_PROFILE'];base=ctrl.matrix_world.copy();D=Matrix.Translation(base.translation)@Matrix.Rotation(math.radians(12),4,'Y')@Matrix.Translation(-base.translation);ctrl.matrix_world=D@base;bpy.context.view_layer.update();after=points(head)
    headtests.append({'who':w,'in_plane_delta_degrees':12,'rigid_head_and_attached_braid_error_m':max((p-D@q).length for p,q in zip(after,before)),'head_mesh':head.name,'yaw_test':'NOT SUPPORTED; deliberately no edge-on card or reflected view substitution'})
    ctrl.matrix_world=base
report['head_profile_attachment']=headtests
for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
# Compare unmodified artwork, UVs, original body weights and rest bones using
# an in-memory library read; the source file is never saved or executed.
newmeshes={(o.parent['character'],o.name):o for o in meshes}
with bpy.data.libraries.load(str(SOURCE),link=False) as (a,b):b.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v007']
oldcol=b.collections[0];oldrigs={o['character']:o for o in oldcol.all_objects if o.type=='ARMATURE'}
def flat_uv(o):return [tuple(o.data.uv_layers.active.data[l.index].uv) for l in o.data.loops]
def weights(o):return [[(o.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in o.data.vertices]
reuse=[]
for w,oldr in oldrigs.items():
    for old in oldr.children:
        new=newmeshes.get((w,old.name))
        if not new:continue
        reuse.append({'mesh':new.name,'original_UV_exact':flat_uv(old)==flat_uv(new),'original_topology_exact':[tuple(p.vertices) for p in old.data.polygons]==[tuple(p.vertices) for p in new.data.polygons],'body_weights_exact':weights(old)==weights(new) if old.get('skin_region') in ['body','dress'] else None,'original_materials_same_names':[m.name for m in new.data.materials]==[m.name.removesuffix('.001') for m in old.data.materials]})
report['original_art_reuse']=reuse
report['rest_bones_exact']={w:all((r.data.bones[n].head_local-oldrigs[w].data.bones[n].head_local).length<1e-8 and (r.data.bones[n].tail_local-oldrigs[w].data.bones[n].tail_local).length<1e-8 for n in r.data.bones.keys()) for w,r in rigs.items()}
report['painting_packed_original_hash']=[{'image':i.name,'packed':bool(i.packed_file),'sha256':hashlib.sha256(i.packed_file.data).hexdigest() if i.packed_file else None} for i in bpy.data.images if i.name.startswith('Pair_Painterly_Near_Age')]
# Verify an appendable native collection rather than just one authoring scene.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(N),link=False) as (a,b):b.collections=['WTSC_PAINTED_RIG_CAPABILITY_v016']
app=b.collections[0];bpy.context.scene.collection.children.link(app);bpy.context.scene.frame_set(41);bpy.context.view_layer.update()
objects=set(app.all_objects);bad=[]
for o in objects:
    for c in o.constraints:
        if hasattr(c,'target') and c.target and c.target not in objects:bad.append([o.name,c.name,c.target.name])
    for m in o.modifiers:
        if m.type=='NODES':
            for node in m.node_group.nodes:
                if node.type=='OBJECT_INFO' and node.inputs['Object'].default_value not in objects:bad.append([o.name,node.name,'external anchor'])
report['fresh_collection_append']={'objects':len(objects),'painted_meshes':sum(o.type=='MESH' for o in objects),'armatures':sum(o.type=='ARMATURE' for o in objects),'external_constraint_or_contour_targets':bad}
report['source_hash_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
report['technical_gates']={
 '16_live_contours':report['structure']['live_contour_meshes']==16,
 'no_old_pose_clock':report['structure']['old_POSE_shape_keys']==0,
 'all12_native_IK_under0_1mm':max(a['error_m'] for p in report['diagnostic_poses'] for a in p['ik'])<.0001,
 'all16_respond_to_new_native_hip_edit':all(v>1e-5 for v in report['off_cache_native_hip_edit']['mesh_response_m'].values()),
 'new_edit_planted_boot_drift_under1micron':max(report['off_cache_native_hip_edit']['boot_drift_m'].values())<1e-6,
 'all_rolls_floor_under1micron':max(abs(p['min_world_z_m']) for p in roll)<1e-6,
 'boots_rigid_under1micron':max(p['rigid_edge_error_m'] for p in roll)<1e-6,
 'brace_projected_gap0_to2mm_in_test_range':all(0<=v<.002 for p in brace for v in p['projected_palm_edge_gap_m'].values()),
 'head_and_braid_profile_rigid_under1micron':all(p['rigid_head_and_attached_braid_error_m']<1e-6 for p in headtests),
 'original_UVs_and_topology_exact':all(p['original_UV_exact'] and p['original_topology_exact'] for p in reuse),
 'original_body_weights_exact':all(p['body_weights_exact'] is not False for p in reuse),
 'original_rest_bones_exact':all(report['rest_bones_exact'].values()),
 'self_contained_append':not bad and report['fresh_collection_append']['painted_meshes']==28,
 'source_hash_unchanged':report['source_sha256']==report['source_hash_after']}
report['art_readiness']='UNPASSED. Head turn drawings missing; cuffs, garment compression, hand style/contact and silhouettes require visual review. No performance acceptance inferred.'
(P/'evidence/technical_validation.json').write_text(json.dumps(report,indent=2))
print('V016_TECHNICAL_GATES',json.dumps(report['technical_gates']))
