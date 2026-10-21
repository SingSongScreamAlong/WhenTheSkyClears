"""Owned-copy upper-body and small contour trials; never edits sealed files."""
import bpy,math,re,json,hashlib
from mathutils import Quaternion,Vector

def curves(action):return [f for l in action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]
def correct_upper_body(root):
    report=[]
    for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
        strip=next(t.strips[0] for t in rig.animation_data.nla_tracks if not t.mute);original=strip.action;action=original.copy();action.name='v043 OWNED | upper-body timing wrist and living settle | '+rig.name;strip.action=action;fc=curves(action);values={(f.data_path,f.array_index):[f.evaluate(i) for i in range(1,97)] for f in fc};girl='GIRL' in rig.name;upper={'chest','head','upper_arm_near','upper_arm_far','forearm_near','forearm_far','hand_near','hand_far','braid'}
        protected=[f for f in fc if any('"'+b in f.data_path for b in ['pelvis','thigh_','shin_','foot_'])];before=hashlib.sha256(json.dumps([[f.data_path,f.array_index,[list(k.co) for k in f.keyframe_points]] for f in protected]).encode()).hexdigest()
        if girl:
            for f in fc:
                name=re.search(r'pose.bones\["([^\"]+)"\]',f.data_path)
                if name and name[1] in upper:
                    for key in f.keyframe_points:key.co.y=original_channel(original,f.data_path,f.array_index).evaluate(max(1,key.co.x-3.2))
        for bone in ['chest','head','hand_near','hand_far','braid']:
            if bone not in rig.pose.bones:continue
            path=f'pose.bones["{bone}"].rotation_quaternion';channels=[next((f for f in fc if f.data_path==path and f.array_index==i),None) for i in range(4)]
            if not all(channels):continue
            for i in range(1,97):
                q=Quaternion([f.evaluate(i) for f in channels]);reach=max(0,min(1,(i-21)/8,(53-i)/8));settle=max(0,min(1,(i-64)/32));breath=math.sin(settle*math.pi*.85)*(1 if settle>0 else 0);angle=0
                if bone.startswith('hand_'):angle=math.radians((-9 if bone=='hand_near' else -5)*reach+(1.5 if girl else -.8)*breath)
                if bone=='chest':angle=math.radians((.55 if girl else -.42)*breath)
                if bone=='head':angle=math.radians((-.45 if girl else .6)*math.sin(max(0,settle-.07)*math.pi*.85))
                if bone=='braid':angle=math.radians(.7*breath)
                q=q@Quaternion((0,1,0),angle)
                for channel,value in zip(channels,q):
                    key=next((k for k in channel.keyframe_points if abs(k.co.x-i)<.01),None)
                    if key:key.co.y=value;key.interpolation='LINEAR'
        after=hashlib.sha256(json.dumps([[f.data_path,f.array_index,[list(k.co) for k in f.keyframe_points]] for f in protected]).encode()).hexdigest();assert before==after
        report.append({'rig':rig.name,'owned_action':action.name,'girl_upper_body_delay_source_frames':3.2 if girl else 0,'leg_pelvis_and_foot_channels_unchanged':True,'corrections':'Small wrist curl during reach, distinctsubdegree chest/head/braid breath in finalsettle; no cameraY/Z or foot edits.'})
    return report

def original_channel(action,path,index):return next(f for f in curves(action) if f.data_path==path and f.array_index==index)

def add_contour_overlaps(root,collection):
    rows=[]
    for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
        for side in ['near','far']:
            for role,bone,radius in [('knee','shin_'+side,.047),('wrist','hand_'+side,.023)]:
                if role=='knee' and 'GIRL' in rig.name:continue
                rest=rig.data.bones[bone].head_local.copy();meshes=[o for o in rig.children_recursive if o.type=='MESH' and ((role=='knee' and 'PAINT '+side+'_leg' in o.name) or (role=='wrist' and 'original hand '+side in o.name))];assert meshes,(rig.name,role,side);reference=meshes[0];uv=reference.data.uv_layers.active;tex=next((n for m in reference.data.materials if m and m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None);assert tex
                loops={loop.vertex_index:uv.data[loop.index].uv.copy() for loop in reference.data.loops};nearest=min(reference.data.vertices,key=lambda v:(Vector((v.co.x,0,v.co.z))-Vector((rest.x,0,rest.z))).length);center_uv=loops[nearest.index];depth=min(v.co.y for v in reference.data.vertices)-.0006
                N=18;verts=[(rest.x,depth,rest.z)]+[(rest.x+radius*math.cos(i*2*math.pi/N),depth,rest.z+radius*(.9 if role=='knee' else .82)*math.sin(i*2*math.pi/N)) for i in range(N)];faces=[(0,i+1,(i+1)%N+1) for i in range(N)];mesh=bpy.data.meshes.new('v043 local rounded '+role);mesh.from_pydata(verts,[],faces);layer=mesh.uv_layers.new(name='Originalpaint tiny contact patch')
                for loop in mesh.loops:
                    point=Vector(verts[loop.vertex_index]);layer.data[loop.index].uv=(center_uv.x+(point.x-rest.x)/2.58,center_uv.y+(point.z-rest.z)/1.45)
                mat=bpy.data.materials.new('v043 OWNED | source-painted '+role+' overlap');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();t=nt.nodes.new('ShaderNodeTexImage');t.image=tex.image;t.extension='EXTEND';em=nt.nodes.new('ShaderNodeEmission');nt.links.new(t.outputs['Color'],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);mesh.materials.append(mat);ob=bpy.data.objects.new('v043 rounded '+role+' | '+rig.name+' '+side,mesh);collection.objects.link(ob);ob.parent=rig;ob.matrix_parent_inverse.identity();group=ob.vertex_groups.new(name=bone);group.add(list(range(len(verts))),1,'REPLACE');mod=ob.modifiers.new('Native jointfollow','ARMATURE');mod.object=rig
                rows.append({'object':ob.name,'joint':bone,'radius_m':radius,'method':'Small native polygon overlap using original packedsource RGB, rigidly follows same bone; no source pixel or legpose change.'})
    return rows
