"""Native binding/projection gap: imagegen-derived GP rigid parts to a 2D rig.
This is an authored kinematic walk test, not stock mocap or an approved gait.
Run only after the typed drawing and armature tools created the exact targets.
"""
import bpy
import math
import json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
scene=bpy.context.scene
rig=bpy.data.objects['Girl_Walk_Rig']
assert len([o for o in scene.objects if o.type=='GREASEPENCIL'])==13
assert not rig.get('bound_imagegen_parts',False), 'Already bound; inspect instead of replaying'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/WTSC_Girl_PreBind_Checkpoint_v001.blend'))

# The factory scene is exclusively owned by this test.
for name in ['Cube','Light','Camera']:
    obj=bpy.data.objects.get(name)
    if obj: bpy.data.objects.remove(obj,do_unlink=True)
scene.name='01_GIRL_WALK_CLEAN'
scene['approval']='PROVISIONAL / movement and drawing proportions need review'
scene['motion_source']='Custom authored 2D joint trajectories; no external mocap'
scene['frame_1_seconds']=0.0
scene['project']='When the Sky Clears'
scene['trailer_duration_seconds']=100
scene['master_resolution']='3840 x 2160 UHD'

def collection(name,owner):
    col=bpy.data.collections.new(name);owner.collection.children.link(col);return col

art=collection('CHARACTER | editable Grease Pencil',scene)
helpers=collection('RIG | authored guide and controls',scene)
setcol=collection('GROUND | neutral walk test',scene)
def relocate(obj,col):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    col.objects.link(obj)
relocate(rig,helpers)
rig.show_in_front=True
rig['design_status']='UNAPPROVED'
rig['walk_cycle_frames']=24
rig['forward_speed_m_per_second']=.72
rig['reference_type']='authored kinematic guide'
rig.hide_render=True

# Convert each actual traced outline to its rest bone coordinates. Native bone
# parenting keeps the drawings editable and avoids unsupported GP skin weights.
binding={name:name for name in ['head','braid','thigh_near','thigh_far','shin_near','shin_far','shoe_near','shoe_far','upper_arm_near','upper_arm_far','forearm_near','forearm_far']}
binding['dress']='body'
for name,bn in binding.items():
    obj=bpy.data.objects['GP_Girl_'+name]
    inv=rig.data.bones[bn].matrix_local.inverted()
    for layer in obj.data.layers:
        for frame in layer.frames:
            for stroke in frame.drawing.strokes:
                for p in stroke.points:p.position=inv@p.position
            frame.drawing.tag_positions_changed()
    obj.parent=rig;obj.parent_type='BONE';obj.parent_bone=bn
    obj.matrix_parent_inverse=Matrix.Identity(4)
    obj.matrix_basis=Matrix.Translation((0,-rig.data.bones[bn].length,0))
    obj['art_source']='GPT imagegen Girl_Parts_Imagegen_v001.png alpha outline'
    obj['editable_drawing']=True
    relocate(obj,art)
rig['bound_imagegen_parts']=True

def pose(bn,head,tail):
    delta=Vector(tail)-Vector(head)
    angle=math.atan2(-delta.x,delta.y)
    pb=rig.pose.bones[bn]
    pb.rotation_mode='XYZ'
    pb.matrix=Matrix.Translation(Vector(head))@Matrix.Rotation(angle,4,'Z')
    bpy.context.view_layer.update()
    pb.keyframe_insert('location');pb.keyframe_insert('rotation_euler')

def foot(phase):
    phase=phase%1
    stance=.60
    if phase<stance:
        return Vector((.216-.72*phase,.09,0)),True
    u=(phase-stance)/(1-stance)
    # Hermite swing retains the stance tangential velocity at toe-off/landing.
    h00=2*u**3-3*u*u+1; h10=u**3-2*u*u+u
    h01=-2*u**3+3*u*u; h11=u**3-u*u
    x=h00*(-.216)+h10*(-.288)+h01*.216+h11*(-.288)
    return Vector((x,.09+.10*math.sin(math.pi*u)**1.25,0)),False

def knee(hip,ankle):
    delta=ankle-hip;d=delta.length
    assert d<.64,('unreachable foot',d)
    midpoint=(hip+ankle)*.5
    right=Vector((-delta.y,delta.x,0)).normalized()
    return midpoint+right*math.sqrt(.32*.32-(d*.5)**2)

samples=[]
for f in range(1,50):
    scene.frame_set(f)
    t=(f-1)/24
    phase=t%1
    rootx=.72*t
    bob=.006*math.cos(4*math.pi*phase)
    hip=Vector((0,.68+bob,0))
    neck=Vector((.006,1.085+bob,0))
    rig.location=(rootx,0,0);rig.keyframe_insert('location')
    pose('ROOT',(0,0,0),(0,.1,0))
    pose('body',hip,neck)
    pose('head',(.005,1.09+bob,0),(.005,1.39+bob,0))
    braid_angle=.08*math.sin(2*math.pi*phase-.5)
    braid_head=Vector((-.108,1.265+bob,0))
    pose('braid',braid_head,braid_head+Vector((-.23*math.sin(braid_angle),-.23*math.cos(braid_angle),0)))
    record={'frame':f,'root_x':rootx,'feet':{}}
    for side,offset in [('far',.5),('near',0)]:
        ankle,contact=foot(phase+offset)
        kn=knee(hip,ankle)
        pose('thigh_'+side,hip,kn)
        pose('shin_'+side,kn,ankle)
        swing=(phase+offset)%1
        footangle=0 if contact else .14*math.sin(math.pi*(swing-.6)/.4)
        pose('shoe_'+side,ankle,ankle+Vector((.15*math.cos(footangle),.15*math.sin(footangle),0)))
        armphase=2*math.pi*(phase+offset)
        shoulder=Vector((.015 if side=='near' else -.015,1.045+bob,0))
        angle=.26*math.cos(armphase)
        elbow=shoulder+Vector((.23*math.sin(angle),-.23*math.cos(angle),0))
        wrist=elbow+Vector((.24*math.sin(angle+.12),-.24*math.cos(angle+.12),0))
        pose('upper_arm_'+side,shoulder,elbow)
        pose('forearm_'+side,elbow,wrist)
        record['feet'][side]={'world_x':rootx+ankle.x,'ankle_y':ankle.y,'stance':contact}
    samples.append(record)

def emission(name,color):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
    nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value=(*color,1);nt.links.new(em.outputs[0],out.inputs[0]);return mat

groundmat=emission('Ground neutral warm gray',(.48,.48,.45))
def rect(name,x0,x1,y0,y1,z,col,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj);obj.data.materials.append(mat);return obj
rect('Ground strip',-20,20,-3,-.003,-.20,setcol,groundmat)
tickmat=emission('Ground stride marks',(.28,.30,.29))
for i in range(-12,34):rect('Contact mark %02d'%i,i*.18,i*.18+.006,-.05,-.008,-.19,setcol,tickmat)

def settings(s):
    s.render.engine='BLENDER_EEVEE'
    s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
    s.render.fps=24;s.render.fps_base=1;s.frame_start=1;s.frame_end=48
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
    s.render.film_transparent=False
    s.world=bpy.data.worlds.new(s.name+' world');s.world.color=(.68,.68,.64)
    s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.68,.64,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
    s.view_settings.view_transform='Standard';s.view_settings.look='None'
    if hasattr(s,'eevee'):s.eevee.taa_render_samples=16

def camera(s,name,offset,scale):
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=scale;data.clip_end=100
    obj=bpy.data.objects.new(name,data);s.collection.objects.link(obj)
    obj.rotation_euler=(0,0,0)
    for f in [1,49]:
        obj.location=(.72*(f-1)/24+offset,.64,10);obj.keyframe_insert('location',frame=f)
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    s.camera=obj;return obj

settings(scene);camera(scene,'Clean side camera',0,2.90)
scene.render.filepath='//../renders/girl_walk_clean_4k/frame_'

# A separate comparison scene contains a visible original motion guide.
compare=bpy.data.scenes.new('02_GUIDE_COMPARISON')
for col in [art,helpers,setcol]:compare.collection.children.link(col)
settings(compare);camera(compare,'Comparison side camera',-.72,3.60)
compare['reference_status']='AUTHORED MOTION GUIDE, not captured human gait'
guidecol=collection('REFERENCE | comparison only - excluded from clean scene',compare)
ref=rig.copy();ref.data=rig.data.copy();guidecol.objects.link(ref);ref.name='REFERENCE_Authored_Walk_Rig'
ref.animation_data_clear()
ref.location=(0,0,0)
ref.animation_data_create();ref.animation_data.action=rig.animation_data.action
ref.animation_data.action_slot=rig.animation_data.action_slot
# Shared object action includes travel; add an offset through a parent.
offset=bpy.data.objects.new('REFERENCE_offset',None);guidecol.objects.link(offset);offset.location=(-1.35,0,0);ref.parent=offset
bluemat=emission('Reference guide blue',(.10,.30,.40))
for bn in ['body','head','thigh_near','shin_near','thigh_far','shin_far','upper_arm_near','forearm_near','upper_arm_far','forearm_far','shoe_near','shoe_far']:
    bone=ref.data.bones[bn];length=bone.length
    mesh=bpy.data.meshes.new('Guide '+bn)
    width=.018 if bn!='body' else .027
    mesh.from_pydata([(-width,0,0),(width,0,0),(width,length,0),(-width,length,0)],[],[(0,1,2,3)]);mesh.update()
    ob=bpy.data.objects.new('Guide '+bn,mesh);guidecol.objects.link(ob);ob.data.materials.append(bluemat)
    ob.parent=ref;ob.parent_type='BONE';ob.parent_bone=bn;ob.matrix_basis=Matrix.Translation((0,-length,0))
compare.render.filepath='//../renders/girl_walk_comparison_4k/frame_'

# User-supplied music and exact treatment markers; picture work remains blank.
master=bpy.data.scenes.new('00_TRAILER_MASTER_4K_100s')
settings(master);master.frame_end=2400
master['status']='TIMELINE SETUP ONLY - not a full trailer animatic'
master['picture_fade']='Last two seconds, frames 2353 to 2401 boundary; pending picture'
master['music']='User supplied exact 100.000 second WAV'
seq=master.sequence_editor_create()
sound=seq.strips.new_sound('USER MUSIC | 100 seconds',str(ROOT/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1)
sound.volume=1.0;sound.keyframe_insert('volume',frame=2161)
sound.volume=0.0;sound.keyframe_insert('volume',frame=2401)
for label,frame in [('BEFORE',1),('SOMETHING CHANGES',433),('PLAY BECOMES CAUTION',841),('WORLD BEHIND THEM',1201),('KEEP GOING',1609),('TITLE TERRAIN',1921),('AUDIO FADE START',2161),('SMALL AGAIN',2161),('QUIET',2305),('PICTURE FADE START',2353),('END boundary',2401)]:
    master.timeline_markers.new(label,frame=frame)

# Source references are packed, hidden from all renders and kept separate.
refcol=collection('SOURCE | imagegen references - hidden',scene);refcol.hide_render=True
for fname in ['Girl_Profile_Imagegen_v001.png','Girl_Parts_Imagegen_v001.png']:
    im=bpy.data.images.load(str(ROOT/'characters'/fname));im.pack()
    ob=bpy.data.objects.new('SOURCE_'+fname,None);refcol.objects.link(ob);ob.empty_display_type='IMAGE';ob.data=im;ob.hide_render=True;ob.hide_viewport=True
    im.filepath='//../characters/'+fname
sound.sound.filepath='//../edit/When_The_Sky_Clears_Trailer_Music_100s.wav'

readme=bpy.data.texts.new('READ ME - provisional walk test')
readme.write('When the Sky Clears\n4K UHD 3840x2160, 24 fps\n\n01_GIRL_WALK_CLEAN: 48-frame, 2-second native Grease Pencil test.\n02_GUIDE_COMPARISON: same movement with an authored joint guide.\n00_TRAILER_MASTER_4K_100s: 2400 frames, music and treatment markers only.\n\n13 editable GP parts, bone parenting, 24-frame authored walk.\nNot imported mocap. No artistic approval or production-ready claim.\nDress correction drawings, joint cleanup, richer gait, Girl approval, Boy and pair contact still pending.\nImagegen raster sources are packed as hidden references. All final character pixels render from GP.\nMusic is user supplied; release permission has not been established here.\n')
scene.frame_set(1);compare.frame_set(1);master.frame_set(1)
bpy.context.window.scene=scene
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
scene.render.filepath='//../renders/girl_walk_clean_4k/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/WTSC_Girl_Walk_Proof_v001.blend'))
(ROOT/'notes/walk_contact_samples.json').write_text(json.dumps(samples,indent=2),encoding='utf-8')
print('WTSC_NATIVE_BUILD_COMPLETE',len(binding),'GP parts; 4K; 48 frames; 100s music master')
