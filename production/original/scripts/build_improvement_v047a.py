"""Native painterly replacement drawings and rounded wrist transitions on v046."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector

R=Path(__file__).resolve().parents[1]
N=R/'notes/improvement_v047';N.mkdir(exist_ok=True)
BASE=R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'
OUT=R/'shots/world/WTSC_Open_Battlefield_Refinement_v047a.blend'
assert not OUT.exists()
expected='f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==expected
assert Path(bpy.data.filepath).resolve()==BASE.resolve()
s=bpy.data.scenes['WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046']
m=bpy.data.scenes['WTSC_OPEN_5S_SUPPORTED_MASTER_v046']
bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
girl=rigs['GIRL']
old_head=next(o for o in girl.children if 'original head and attached braid' in o.name)
turned=next(o for o in girl.children if 'original-painted look toward boy' in o.name)
disc=next(o for o in girl.children if 'passing back-view drawing' in o.name)
before=[]
for f in range(1801,1921):
    s.frame_set(f);bpy.context.view_layer.update()
    before.append({'frame':f,'camera':[list(r) for r in s.camera.matrix_world],
                   'bones':{who:{b.name:[list(r) for r in b.matrix] for b in rig.pose.bones} for who,rig in rigs.items()}})

collection=bpy.data.collections.new('v047 | Painterly turn drawings and connected wrists')
s.collection.children.link(collection)
guidecol=bpy.data.collections.new('v047 | Editable Grease Pencil contour guides')
s.collection.children.link(guidecol)
headrest=girl.data.bones['head'].matrix_local.copy()

def exposure(ob,start,end):
    ob.animation_data_clear()
    for f,hidden in [(1801,True),(start,False),(end+1,True),(1921,True)]:
        ob.hide_render=hidden;ob.keyframe_insert('hide_render',frame=f)
    for layer in ob.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='CONSTANT'

exposure(old_head,1801,1841)
exposure(turned,1848,1920)
disc.animation_data_clear();disc.hide_render=True;disc.hide_viewport=True
contours=json.loads((R/'characters/head_turn_v047/contours.json').read_text())
headrows=[]
# Pixel neck-root anchors register drawings against the existing head bone.
specs=[('Girl_Three_Quarter_Right_v047.png',1842,1843,682,1080,.000413),
       ('Girl_Front_v047.png',1844,1845,600,1070,.000421),
       ('Girl_Three_Quarter_Left_v047.png',1846,1847,584,1044,.000434)]
for name,start,end,ax,ay,scale in specs:
    source=R/'characters/head_turn_v047'/name
    im=bpy.data.images.load(str(source),check_existing=True);im.pack()
    info=contours[name];W,H=info['size'];outline=info['contour']
    verts=[(headrest.translation.x+(x-ax)*scale,-.047,headrest.translation.z+(ay-y)*scale) for x,y in outline]
    mesh=bpy.data.meshes.new('v047 | '+source.stem+' | editable contour mesh')
    mesh.from_pydata(verts,[],[tuple(range(len(verts)))]);mesh.update()
    ob=bpy.data.objects.new('v047 | '+source.stem,mesh);collection.objects.link(ob);ob.parent=girl
    uv=mesh.uv_layers.new(name='Generated original paint registered to editable contour')
    for loop in mesh.loops:
        x,y=outline[loop.vertex_index];uv.data[loop.index].uv=(x/W,1-y/H)
    material=old_head.data.materials[0].copy();material.name='v047 | '+source.stem+' | existing event light response'
    nt=material.node_tree
    images=[n for n in nt.nodes if n.type=='TEX_IMAGE']
    assert len(images)==1
    images[0].image=im
    mesh.materials.append(material)
    group=ob.vertex_groups.new(name='head');group.add(list(range(len(verts))),1,'REPLACE')
    modifier=ob.modifiers.new('Existing head bone; unchanged performance','ARMATURE');modifier.object=girl
    ob['v047_role']='painted_head_exposure';ob['source_image']=str(source)
    exposure(ob,start,end)
    # Real native Grease Pencil contours are retained as editable drawing layers.
    gp=bpy.data.grease_pencils.new('v047 | GP contour | '+source.stem)
    gpo=bpy.data.objects.new(gp.name,gp);guidecol.objects.link(gpo);gpo.parent=girl
    layer=gp.layers.new('Original alpha-derived editable contour',set_active=True)
    drawing=layer.frames.new(1).drawing;drawing.add_strokes([len(verts)])
    stroke=drawing.strokes[0];stroke.cyclic=True
    for point,co in zip(stroke.points,verts):
        point.position=headrest.inverted()@Vector(co);point.radius=.0004;point.opacity=1
    line=bpy.data.materials.new('v047 | charcoal contour editing ink');bpy.data.materials.create_gpencil_data(line)
    line.grease_pencil.color=(.012,.012,.012,1);gp.materials.append(line)
    constraint=gpo.constraints.new('COPY_TRANSFORMS');constraint.target=girl;constraint.subtarget='head'
    gpo.hide_render=True;gpo.hide_viewport=True
    gpo['purpose']='Editable native GP contour source; paint mesh owns the rendered contour. Unhide for contour editing.'
    headrows.append({'object':ob.name,'image':str(source),'exposure':[start,end],
                     'neck_pixel_anchor':[ax,ay],'metres_per_pixel':scale,'contour_vertices':len(verts),'GP_guide':gpo.name})

def copy_clock(source,target):
    old=source.animation_data;new=target.animation_data_create()
    assert old and not old.action
    for t in old.nla_tracks:
        track=new.nla_tracks.new();track.name=t.name
        for st in t.strips:
            n=track.strips.new(st.name,int(st.frame_start),st.action)
            n.action_slot=st.action_slot;n.action_frame_start=st.action_frame_start;n.action_frame_end=st.action_frame_end
            n.scale=st.scale;n.frame_end=st.frame_end;n.extrapolation=st.extrapolation

skin_materials={};rounded=[]
for who,rig in rigs.items():
    for side in ['near','far']:
        arm=next(o for o in rig.children if o.name==f'V007_{who} | drawn skin {side}')
        oldmat=arm.data.materials[0]
        if oldmat.name not in skin_materials:
            material=oldmat.copy();material.name='v047 | subtle charcoal arm paint | '+who
            nt=material.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION')
            original=em.inputs[0].links[0].from_socket
            tex=nt.nodes.new('ShaderNodeTexNoise');tex.name='v047 | restrained charcoal grain';tex.inputs['Scale'].default_value=170
            gain=nt.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';gain.inputs[1].default_value=.002
            nt.links.new(tex.outputs['Fac'],gain.inputs[0])
            mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='ADD';mix.inputs[0].default_value=1
            nt.links.new(original,mix.inputs[1]);nt.links.new(gain.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],em.inputs[0])
            skin_materials[oldmat.name]=material
        material=skin_materials[oldmat.name];arm.data.materials[0]=material
        for end in ['elbow','wrist']:
            bykey={}
            for key in arm.data.shape_keys.key_blocks:
                p=[v.co.copy() for v in key.data]
                ids=(0,1) if end=='elbow' else (len(p)-2,len(p)-1)
                center=(p[ids[0]]+p[ids[1]])*.5
                radius=(p[ids[0]]-p[ids[1]]).length*.47
                bykey[key.name]=[(center.x+radius*math.cos(i*math.tau/32),center.y-.0004,
                                  center.z+radius*math.sin(i*math.tau/32)) for i in range(32)]
            mesh=bpy.data.meshes.new('v047 | soft painted '+end+' '+who+' '+side)
            mesh.from_pydata(bykey['Basis'],[],[tuple(range(32))]);mesh.update()
            cap=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(cap);cap.parent=rig;mesh.materials.append(material)
            uv=mesh.uv_layers.new()
            for loop in mesh.loops:
                i=loop.vertex_index;uv.data[loop.index].uv=(.51+math.cos(i*math.tau/32)*.001,.46+math.sin(i*math.tau/32)*.001)
            for keyname,verts in bykey.items():
                k=cap.shape_key_add(name=keyname);k.data.foreach_set('co',[c for p in verts for c in p])
            copy_clock(arm.data.shape_keys,cap.data.shape_keys)
            cap['v047_role']='rounded_drawn_arm_transition'
            rounded.append(cap.name)

errors={'camera':0.,'all_rig_bone_matrices':0.}
head_exposures=[]
allheads=[old_head,turned]+[s.objects[row['object']] for row in headrows]
for row in before:
    f=row['frame'];s.frame_set(f);bpy.context.view_layer.update()
    errors['camera']=max(errors['camera'],max(abs(s.camera.matrix_world[i][j]-row['camera'][i][j]) for i in range(4) for j in range(4)))
    for who,rig in rigs.items():
        for bone in rig.pose.bones:
            original=row['bones'][who][bone.name]
            errors['all_rig_bone_matrices']=max(errors['all_rig_bone_matrices'],max(abs(bone.matrix[i][j]-original[i][j]) for i in range(4) for j in range(4)))
    visible=[o.name for o in allheads if not o.hide_render]
    assert len(visible)==1,(f,visible)
    head_exposures.append({'frame':f,'head':visible[0]})
assert max(errors.values())==0,errors
assert (m.render.resolution_x,m.render.resolution_y,m.render.resolution_percentage,m.render.fps)==(3840,2160,100,24)
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047a';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v047a'
report={'base':str(BASE),'base_sha256':expected,'native':str(OUT),'world_scene':s.name,'master_scene':m.name,
        'head_drawings':headrows,'head_exposures_all120':head_exposures,'rounded_arm_transitions':rounded,
        'all120_errors':errors,'GP_contour_objects':len(headrows),'range':[1801,1920],'fps':24,'native_resolution':[3840,2160],
        'scope':'Three generated painted head exposures on2s at1842..1847, replacing disc. Native contour meshes, SVGs and GP editing guides. Rounded wrist/elbow caps with subtle charcoal grain. Existing foot/body actions, world, light and FXv003 untouched.',
        'limits':'Candidate requires actual key and motion review. New facial details may differ subtly; offered touch and unresolved restart remain. Foreground repetitions and FX refinements are separate remaining work.',
        'artistic_acceptance':False,'full_trailer_propagated':False}
text=bpy.data.texts.new('CURRENT v047a | Iteration provenance');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1844)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report['sha256']=hashlib.sha256(OUT.read_bytes()).hexdigest()
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==expected
(N/'build_v047a.json').write_text(json.dumps(report,indent=2))
print('V047A_NATIVE_BUILT',json.dumps({'native':str(OUT),'sha256':report['sha256'],'errors':errors}),flush=True)
