"""Native-material key proof of the original girl's painted shoulder yoke.

RAM-only key test, preserving the v053 blend. The mesh samples the existing
Pair_Painterly_Near_Age_v015 painting and follows the actual torso armature.
"""
import bpy,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'/'keys';E.mkdir(exist_ok=True,parents=True);V.mkdir(exist_ok=True,parents=True)
SRC=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend';SHA='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
PAIR=ROOT/'characters/Pair_Painterly_Near_Age_v015.png';psha=hashlib.sha256(PAIR.read_bytes()).hexdigest()
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V053 | AUTHORED WALK BEATS | v051 grounded feet'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=1;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
rig=bpy.data.objects['V044 GIRL | estimated joint centres'];C=bpy.data.collections['V046 | restored original painted wardrobe']
image=next(i for i in bpy.data.images if 'Pair_Painterly_Near_Age_v015' in i.name and i.size[0]==1672)
assert tuple(image.size)==(1672,941)
mat=bpy.data.materials.new('V056 GIRL | inherited yoke paint');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='V056 | original yoke registration'
tx=nodes.new('ShaderNodeTexImage');tx.image=image;tx.interpolation='Linear'
em=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial')
links.new(uvnode.outputs['UV'],tx.inputs['Vector']);links.new(tx.outputs['Color'],em.inputs['Color']);links.new(em.outputs[0],out.inputs['Surface'])
# Fabric panel is traced in the existing age-ten dress coordinates. UV source
# follows an entirely opaque portion of the ORIGINAL painting at the collar,
# shoulder and upper dress. No old raster is retouched or repainted.
NROW=17;NCOL=11;verts=[];tex=[];faces=[]
for row in range(NROW):
    t=row/(NROW-1);bend=math.sin(math.pi*t)
    rear=-.047-.028*bend-.033*t
    front=.050+.055*t+.003*bend
    source_left=949+20*t
    source_right=1018+54*t
    for col in range(NCOL):
        s=col/(NCOL-1)
        x=rear+(front-rear)*s
        zz=1.164-.175*t+.005*bend+.046*(1-s)**1.4*t*t
        source_y=307+(66+38*s)*t
        verts.append((x,-.0275-.002*math.sin(math.pi*s),zz))
        tex.append(((source_left+(source_right-source_left)*s)/1672,1-source_y/941))
for row in range(NROW-1):
    for col in range(NCOL-1):
        a=row*NCOL+col;faces.append((a,a+1,a+1+NCOL,a+NCOL))
mesh=bpy.data.meshes.new('V056 | painted yoke with editable posed grid');mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='V056 | original yoke registration')
for lp in mesh.loops:uv.data[lp.index].uv=tex[lp.vertex_index]
mesh.materials.append(mat)
obj=bpy.data.objects.new('V056 GIRL | pose-specific original painted shoulder yoke',mesh);C.objects.link(obj);obj.parent=rig
chest=obj.vertex_groups.new(name='chest');pelvis=obj.vertex_groups.new(name='pelvis')
for row in range(NROW):
    t=row/(NROW-1);w=1-.17*t*t
    for col in range(NCOL):
        index=row*NCOL+col;chest.add([index],w,'REPLACE');pelvis.add([index],1-w,'REPLACE')
mod=obj.modifiers.new('Actual torso joint centres','ARMATURE');mod.object=rig
obj['source_paint']='characters/Pair_Painterly_Near_Age_v015.png, original pixels/UV sampling only'
obj['study_status']='RAM-only key-shape proof, not approved native animation'
base=[v.co.copy() for v in mesh.vertices]
frames={4:'loading_near',9:'passing_near',13:'push_near',20:'loading_far',25:'passing_far',29:'push_far'}
def shape(kind):
    phase=kind.split('_')[0];far=kind.endswith('far');factor=.9 if far else 1.
    if phase=='loading':return (-.006*factor,-.010*factor,-.010*factor,.002*factor)
    if phase=='passing':return (.002*factor,.008*factor,.004*factor,-.002*factor)
    return (-.002*factor,.012*factor,.007*factor,-.003*factor)
records=[]
for f,kind in frames.items():
    rear_x,front_x,lower_z,front_z=shape(kind)
    shifted=[]
    for index,p in enumerate(base):
        row,col=divmod(index,NCOL);t=row/(NROW-1);s=col/(NCOL-1)
        q=p.copy();q.x+=t*t*(rear_x*(1-s)+front_x*s);q.z+=t*t*lower_z+math.sin(math.pi*t)*s*front_z;shifted.append(q)
    mesh.vertices.foreach_set('co',[n for q in shifted for n in q]);mesh.update()
    S.frame_set(f);bpy.context.view_layer.update()
    path=V/f'V056_YOKE_{kind.upper()}_F{f:03d}.png';S.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=S.name)
    records.append({'frame':f,'phase':kind,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rear_x_m':rear_x,'front_x_m':front_x,'lower_z_m':lower_z,'front_z_m':front_z})
mesh.vertices.foreach_set('co',[n for q in base for n in q]);mesh.update()
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA and hashlib.sha256(PAIR.read_bytes()).hexdigest()==psha
(E/'YOKE_KEY_PROOF.json').write_text(json.dumps({'source':str(SRC),'source_sha256':SHA,'paint_source':str(PAIR),'paint_sha256':psha,'saved_new_native':False,'source_unchanged':True,'raster_changed':False,'yoke_grid':[NROW,NCOL],'frames':records},indent=2))
print('V056_ORIGINAL_PAINT_YOKE_KEYS_RAM_ONLY',len(records),flush=True)
