"""Render six real Blender keys with phase-specific charcoal cloth paint.

This is a RAM-only visual gate. No v055 animation is saved unless the key board
reads at actual shot size. All source assets are frozen and hashed.
"""
import bpy, json, hashlib, math
from pathlib import Path

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
V=P/'previews'/'key_shapes';E=P/'evidence';V.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend'
SHA='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
texture_paths={kind:P/'textures'/f'WTSC_Girl_Bodice_{kind}_v055.png' for kind in ('loading','passing','push')}
texture_hashes={kind:hashlib.sha256(path.read_bytes()).hexdigest() for kind,path in texture_paths.items()}
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V053 | AUTHORED WALK BEATS | v051 grounded feet'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.threads_mode='FIXED';S.render.threads=1;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
rig=bpy.data.objects['V044 GIRL | estimated joint centres'];wardrobe=bpy.data.collections['V046 | restored original painted wardrobe']
body=next(o for o in wardrobe.objects if o.parent==rig and o.get('wardrobe_role')=='body')
assert len(body.data.vertices)==1105
sleeves={side:next(o for o in wardrobe.objects if o.parent==rig and o.get('wardrobe_role')=='sleeve' and o.name.endswith(side)) for side in ('near','far')}
original=[v.co.copy() for v in body.data.vertices]

# The original main UV and quiet original-paint UV still drive the base.
uv=body.data.uv_layers.new(name='V055 | pose cloth registration')
for lp in body.data.loops:
    row,col=divmod(lp.vertex_index,17)
    uv.data[lp.index].uv=(col/16,1-row/64)
mat=body.data.materials[0].copy();mat.name='V055 GIRL | phase cloth proof'
body.data.materials[0]=mat
nodes=mat.node_tree.nodes;links=mat.node_tree.links
em=next(n for n in nodes if n.type=='EMISSION')
base=em.inputs['Color'].links[0].from_socket
links.remove(em.inputs['Color'].links[0])
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name
paintnode=nodes.new('ShaderNodeTexImage');paintnode.name='V055 phase drawing';paintnode.interpolation='Linear'
links.new(uvnode.outputs['UV'],paintnode.inputs['Vector'])
blend=nodes.new('ShaderNodeMixRGB');blend.name='V055 pose painting over original charcoal';blend.blend_type='MIX';blend.use_clamp=True
links.new(paintnode.outputs['Alpha'],blend.inputs[0]);links.new(base,blend.inputs[1]);links.new(paintnode.outputs['Color'],blend.inputs[2]);links.new(blend.outputs[0],em.inputs['Color'])
paint_images={k:bpy.data.images.load(str(p),check_existing=False) for k,p in texture_paths.items()}
for im in paint_images.values():im.alpha_mode='STRAIGHT'

frames={4:'loading_near',9:'passing_near',13:'push_near',20:'loading_far',25:'passing_far',29:'push_far'}
params={
 'loading_near':(.014,-.008,-.005,.010,-.015,.006,.003,-.004),
 'loading_far':(.013,-.009,-.006,.009,-.014,.006,.003,-.004),
 'passing_near':(-.004,.004,.002,-.004,.005,-.002,-.002,.001),
 'passing_far':(-.003,.004,.002,-.004,.004,-.002,-.002,.001),
 'push_near':(-.007,.006,.003,-.005,.005,-.002,-.003,.001),
 'push_far':(-.006,.005,.002,-.004,.005,-.002,-.003,.001),
}
def bump(t,a,b):return math.sin(math.pi*(t-a)/(b-a))**2 if a<t<b else 0.
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def deform(p):
    out=[]
    for i,v in enumerate(original):
        row,col=divmod(i,17);t=row/64;s=col/16
        sh=bump(t,.02,.37) if row>2 else 0
        wa=bump(t,.25,.66) if row<43 else 0
        q=v.copy();q.x+=sh*(p[0]*(1-s)+p[1]*s)+wa*(p[3]*(1-s)+p[4]*s)
        q.z+=sh*p[2]+wa*p[5];out.append(q)
    return out
def signs(verts):
    out=[]
    for row in range(64):
        for col in range(16):
            a=verts[row*17+col];b=verts[row*17+col+1];c=verts[(row+1)*17+col]
            out.append((b.x-a.x)*(c.z-a.z)-(b.z-a.z)*(c.x-a.x))
    return out
base_signs=signs(original);assert min(abs(s) for s in base_signs)>1e-9
records=[];max_delta=0.;min_area=1e9
for f,kind in frames.items():
    phase=kind.split('_')[0];p=params[kind];S.frame_set(f)
    paintnode.image=paint_images[phase]
    changed=deform(p);areas=signs(changed);assert all(a*b>0 for a,b in zip(base_signs,areas))
    min_area=min(min_area,min(abs(a) for a in areas));max_delta=max(max_delta,max((a-b).length for a,b in zip(changed,original)))
    body.data.vertices.foreach_set('co',[c for q in changed for c in q]);body.data.update()
    saved=[]
    for side,obj in sleeves.items():
        key=obj.data.shape_keys.key_blocks[4*(f-1)];old=[q.co.copy() for q in key.data];saved.append((key,old))
        shifted=[]
        for j,q in enumerate(old):
            row,col=divmod(j,9);w=(1-smooth(row/17))**2 if row<17 else 0.
            r=q.copy();r.x+=p[6]*w;r.z+=p[7]*w;shifted.append(r)
        key.data.foreach_set('co',[c for r in shifted for c in r]);obj.data.update()
    bpy.context.view_layer.update()
    dest=V/f'V055_GIRL_PAINTED_{kind.upper()}_F{f:03d}.png'
    S.render.filepath=str(dest);bpy.ops.render.render(write_still=True,scene=S.name)
    records.append({'frame':f,'phase':kind,'render':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    body.data.vertices.foreach_set('co',[c for q in original for c in q]);body.data.update()
    for key,old in saved:key.data.foreach_set('co',[c for q in old for c in q])
    for obj in sleeves.values():obj.data.update()
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
(E/'PAINTED_KEY_PROOF.json').write_text(json.dumps({'source':str(SRC),'source_sha256':SHA,'source_unchanged':True,'saved_new_native':False,'new_uv_layer':'V055 | pose cloth registration','paint_sha256':texture_hashes,'frames':records,'dress_max_vertex_delta_m':max_delta,'min_cell_area_m2':min_area,'cell_inversions':0},indent=2))
print('V055_PAINTED_KEYS_RAM_ONLY',len(records),max_delta,min_area,flush=True)
