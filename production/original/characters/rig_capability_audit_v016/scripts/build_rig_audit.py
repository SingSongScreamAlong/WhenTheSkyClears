"""Reversible technical linkage study using existing painted rigs and art.
No production edits; no proxy meshes; no new story performance.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Matrix, Vector
P=Path(__file__).resolve().parents[1]
R=P.parents[1]
SRC=R/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'
SHA=hashlib.sha256(SRC.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update()
rigs={o['character']:o for o in S.objects if o.type=='ARMATURE' and o.get('character')}
rest={w:{b.name:b.matrix_local.copy() for b in rig.data.bones} for w,rig in rigs.items()}
pose1={w:{b.name:b.matrix.copy() for b in rig.pose.bones} for w,rig in rigs.items()}
source_foot=json.loads((R/'locomotion/performance_v003/art/native_overlap_sources.json').read_text())['feet']
report={'source_sha256':SHA,'repairs':[],'design_changes':False}
source_contours={o.name:[p.co.copy() for p in o.data.shape_keys.key_blocks['POSE_001'].data] for rig in rigs.values() for o in rig.children if o.get('v007_role') in ['drawn_leg','drawn_arm','drawn_cuff']}
keep=[]
for w,rig in rigs.items():
    for o in rig.children:
        if o.type=='MESH' and (not o.hide_render or o.name=='PERF_GIRL | original head and attached braid'):
            keep.append(o)
# Existing unreflected head is the supported design. The failed exposure is
# rendered separately as a defect witness, never substituted by the proxy.
keep=[o for o in keep if o.get('v007_role') not in ['look_back_original_paint'] and 'passing back-view' not in o.name]
for o in keep:
    if o.animation_data:o.animation_data_clear()
    o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
    role=o.get('v007_role');rig=o.parent;w=rig['character']
    if role in ['drawn_leg','drawn_arm','drawn_cuff']:
        coords=[p.co.copy() for p in o.data.shape_keys.key_blocks['POSE_001'].data]
        o.shape_key_clear();o.vertex_groups.clear()
        side='near' if o.name.endswith('near') else 'far'
        if role=='drawn_leg':names=['thigh_'+side,'shin_'+side]
        else:names=[('forearm_' if 'drawn skin' in o.name else 'upper_arm_')+side]
        groups={n:o.vertex_groups.new(name=n) for n in names}
        mats={n:pose1[w][n]@rest[w][n].inverted() for n in names}
        for i,p in enumerate(coords):
            if len(names)==2:
                t=(i//2)/(len(coords)//2-1);u=max(0,min(1,(t-.28)/.44));u=u*u*(3-2*u)
                weights=[1-u,u]
            else:weights=[1.]
            mix=Matrix([[sum(mats[n][a][b]*wt for n,wt in zip(names,weights)) for b in range(4)] for a in range(4)])
            o.data.vertices[i].co=mix.inverted()@p
            for n,wt in zip(names,weights):
                if wt>0:groups[n].add([i],wt,'REPLACE')
        mod=o.modifiers.new('V016 live painted bone deformation','ARMATURE');mod.object=rig
        # Linear blend is deliberately used because the rest reconstruction is
        # its exact inverse. Deep bend visual limits are tested, not assumed.
        mod.use_deform_preserve_volume=False
        o['v016_linkage']='Native armature skin; rest reconstructed from original POSE_001; UV/topology/material retained. No old drawing clock.'
        report['repairs'].append({'mesh':o.name,'role':role,'bones':names,'vertices':len(coords)})
    elif o.data.shape_keys:
        # Boot basis is the source contour. Hand poses are repurposed as
        # independent shape choices below. Body breathing is not performance.
        if role=='drawn_hand':
            choices={name:[p.co.copy() for p in o.data.shape_keys.key_blocks[f'POSE_{f:03d}'].data] for name,f in [('Relax',1),('Reach',38),('Brace',58)]}
            o.shape_key_clear()
            for v,p in zip(o.data.vertices,choices['Relax']):v.co=p
            o.shape_key_add(name='Basis')
            for name in ['Reach','Brace']:
                k=o.shape_key_add(name=name)
                for v,p in zip(k.data,choices[name]):v.co=p
        else:o.shape_key_clear()
for o in list(bpy.data.objects):
    if o not in keep and o not in rigs.values():bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.users==0:bpy.data.collections.remove(c)
PACK=bpy.data.collections.new('WTSC_PAINTED_RIG_CAPABILITY_v016');S.collection.children.link(PACK)
for o in [*rigs.values(),*keep]:
    for c in list(o.users_collection):c.objects.unlink(o)
    PACK.objects.link(o)
travel=bpy.data.objects.new('V016 | WORLD_TRAVEL | diagnostic zero',None);PACK.objects.link(travel);travel.empty_display_size=.1
travel['contract']='Separate world travel from HIP. Zero travel in this diagnostic. Do not integrate these test Actions into production.'
for rig in rigs.values():
    rig.animation_data_clear();rig.parent=None;rig.location=(0,0,0);rig.rotation_euler=(0,0,0);rig.scale=(1,1,1)
    rig.hide_render=False;rig.hide_viewport=False;rig.hide_set(False);rig.show_in_front=True
    rig.data.display_type='STICK'
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    # Retain all original deform bones. Parenting adds dependencies without
    # changing a single rest matrix or replacing the body's existing weights.
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    e=rig.data.edit_bones
    for n in ['chest','thigh_near','thigh_far','skirt_front','skirt_back']:
        if n in e:e[n].parent=e['pelvis'];e[n].use_connect=False
    e['head'].parent=e['chest']
    if 'braid' in e:e['braid'].parent=e['head']
    for side in ['near','far']:
        e['shin_'+side].parent=e['thigh_'+side];e['shin_'+side].use_connect=True
        e['upper_arm_'+side].parent=e['chest']
        e['forearm_'+side].parent=e['upper_arm_'+side];e['forearm_'+side].use_connect=True
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    rig['rig_revision']='v016 painted linkage audit';rig['art_acceptance']='UNPASSED; see capability report and head defect witness'
    rig['motion_status']='v016 technical linkage study; final-art readiness UNPASSED; no performance approval'
    rig['performance_version']='Performance paused; v016 rig capability tests only'
    rig['review']='Actual retained painting and original rig. Review cuffs, deep cloth shapes, occlusion and missing head turn before any final-art claim.'
    rig.parent=travel
CONTROLS=bpy.data.collections.new('V016 | NATIVE WORLD TARGETS');PACK.children.link(CONTROLS)
LINKS=bpy.data.collections.new('V016 | LIVE CONTOUR ANCHORS');PACK.children.link(LINKS)
controls={}
def empty(w,name,M,parent=None,size=.045):
    o=bpy.data.objects.new(w+' | '+name,None);CONTROLS.objects.link(o);o.empty_display_type='CIRCLE';o.empty_display_size=size
    o.parent=parent if parent else rigs[w];o.matrix_local=M;o.show_in_front=True;o['v016_control']=name
    controls[w,name]=o;return o
def copy_transform(pb,target):
    c=pb.constraints.new('COPY_TRANSFORMS');c.name='V016 native target';c.target=target;c.target_space='WORLD';c.owner_space='WORLD'
for w,rig in rigs.items():
    hip=empty(w,'HIP',rest[w]['pelvis']);chest=empty(w,'CHEST',rest[w]['pelvis'].inverted()@rest[w]['chest'],hip)
    head=empty(w,'HEAD_PROFILE',rest[w]['chest'].inverted()@rest[w]['head'],chest)
    copy_transform(rig.pose.bones['pelvis'],hip);copy_transform(rig.pose.bones['chest'],chest);copy_transform(rig.pose.bones['head'],head)
    head['supported_view']='Original right profile; in-plane tilt only. No yaw/reflection/turnaround approval.'
    for side in ['near','far']:
        ft=empty(w,'ANKLE_'+side,rest[w]['foot_'+side]);copy_transform(rig.pose.bones['foot_'+side],ft)
        wrist=empty(w,'WRIST_'+side,rest[w]['hand_'+side]);copy_transform(rig.pose.bones['hand_'+side],wrist)
        for limb,end,target in [('LEG','shin',ft),('ARM','forearm',wrist)]:
            name=end+'_'+side;pb=rig.pose.bones[name]
            pole=empty(w,limb+'_POLE_'+side,Matrix.Translation(pb.head+Vector((1,0,0))),size=.025)
            # A small preferred bend avoids the straight source chain's IK singularity.
            pb.rotation_mode='XYZ';pb.rotation_euler.z=.05
            ik=pb.constraints.new('IK');ik.name='V016 fixed-length '+limb;ik.target=target;ik.chain_count=2;ik.use_stretch=False;ik.pole_target=pole;ik.pole_angle=0
        wrist['Reach']=0.;wrist['Brace']=0.;wrist['BraceFollow']=0.;wrist['TorsoFollow']=1.
        carry=empty(w,'RELAXED_HAND_TORSO_ANCHOR_'+side,rest[w]['chest'].inverted()@rest[w]['hand_'+side],chest,size=.012)
        follow=wrist.constraints.new('COPY_TRANSFORMS');follow.name='V016 relaxed hand follows torso';follow.target=carry
        fc=follow.driver_add('influence');v=fc.driver.variables.new();v.name='carry';v.targets[0].id=wrist;v.targets[0].data_path='["TorsoFollow"]';fc.driver.expression='carry'
        wrist.id_properties_ui('TorsoFollow').update(min=0,max=1,description='1: relaxed hand follows chest.0: explicit wrist target/contact in rig space.')
        wrist.id_properties_ui('Reach').update(min=0,max=1);wrist.id_properties_ui('Brace').update(min=0,max=1)
        hand=next(o for o in keep if o.parent==rig and o.get('v007_role')=='drawn_hand' and o.name.endswith(side))
        hand.location.y=-.039 if side=='near' else .024
        for key in ['Reach','Brace']:
            fc=hand.data.shape_keys.key_blocks[key].driver_add('value');d=fc.driver;d.type='SCRIPTED'
            for pname in ['Reach','Brace']:
                v=d.variables.new();v.name=pname.lower();v.type='SINGLE_PROP';v.targets[0].id=wrist;v.targets[0].data_path='["'+pname+'"]'
            d.expression='max(0,'+key.lower()+')/max(1,max(0,reach)+max(0,brace))'
        ft['contact_api']='Use rig_pose_api.set_foot for sole-aware placement and roll. Then native ankle target and IK remain editable.'
    # Bone shape matrices stay native. Original braid/skirt weights are kept.
    rig['control_method']='Native world targets +2-bone IK; hip/chest/head independent. Foot pivot placement and contact shapes via embedded rig_pose_api.py.'
sys.path.insert(0,str(P/'scripts'))
import live_contours
report['repairs']=[]
for w,rig in rigs.items():
    for side in ['near','far']:
        boot=next(o for o in keep if o.parent==rig and o.get('v007_role')=='support_boot' and o.name.endswith(side))
        source_foot[w+'_'+side]['actual_native_vertices']=[list(v.co) for v in boot.data.vertices]
for mesh in keep:
    if mesh.name not in source_contours:continue
    rig=mesh.parent;side='near' if mesh.name.endswith('near') else 'far'
    boot=next(o for o in keep if o.parent==rig and o.get('v007_role')=='support_boot' and o.name.endswith(side))
    report['repairs'].append(live_contours.setup(mesh,rig,LINKS,source_contours[mesh.name],boot))
# Simple diagnostic stage; emission art keeps original appearance independent
# of lights. The camera is the final-art side view, never an edge-on card.
STAGE=bpy.data.collections.new('V016 | DIAGNOSTIC STAGE');S.collection.children.link(STAGE)
def emission(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();a=n.new('ShaderNodeEmission');a.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],out.inputs[0]);return m
ground=emission('V016 ground rule',(.26,.29,.30))
me=bpy.data.meshes.new('Ground rule');me.from_pydata([(-5,.1,-.008),(5,.1,-.008),(5,.1,0),(-5,.1,0)],[],[(0,1,2,3)]);me.materials.append(ground);ob=bpy.data.objects.new('GROUND z0',me);STAGE.objects.link(ob)
camdata=bpy.data.cameras.new('V016 side-view orthographic');cam=bpy.data.objects.new('V016 inspection camera',camdata);STAGE.objects.link(cam);cam.location=(.0,-7,.76);cam.rotation_euler=(math.pi/2,0,0);camdata.type='ORTHO';camdata.ortho_scale=3.0;S.camera=cam
S.world.color=(.68,.66,.62);S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.66,.62,1)
S.render.engine='CYCLES' if False else 'CYCLES'
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=32
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.fps=24
S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=0;S.view_settings.gamma=1
S.render.film_transparent=False
S.frame_start=1;S.frame_end=240;S.name='V016 | PAINTED RIG DIAGNOSTIC | NOT PERFORMANCE'
for a in list(bpy.data.actions):
    a.use_fake_user=False
    if a.users==0:bpy.data.actions.remove(a)
for old in list(bpy.data.texts):bpy.data.texts.remove(old)
for fn in ['build_rig_audit.py','rig_pose_api.py','diagnostic_poses.py','live_contours.py']:
    if (P/'scripts'/fn).exists():t=bpy.data.texts.new(fn);t.write((P/'scripts'/fn).read_text())
bpy.context.view_layer.update()
sys.path.insert(0,str(P/'scripts'))
import rig_pose_api,diagnostic_poses
rig_pose_api.initialize(rigs,controls,source_foot)
diagnostic_poses.author(rigs,controls)
S.frame_set(1);bpy.context.view_layer.update()
for im in bpy.data.images:
    if im.source=='FILE' and not im.packed_file:
        try:im.pack()
        except Exception:pass
S['audit_scope']='Actual source-painted rigs, technical posing/contact diagnostics only. Head turn and silhouette quality remain review gates.'
(P/'evidence/linkage_repair.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'))
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
print('V016_PAINTED_LINKAGE_BUILT',len(keep),len(report['repairs']))
