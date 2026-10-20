"""Ground-only correction after actual keyframe review. No smoke."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s
root=bpy.data.objects['FXv009 | impact anchor and controls'];asset=bpy.data.collections['FXv009 | GROUND IMPACT | baked Bullet and crater']
def drive(owner,path,expression,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for n,k in [('t','age'),('start','start_frame'),('speed','speed')]:
        import re
        if not re.search(r'\b'+n+r'\b',expression):continue
        v=f.driver.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+k+'"]'
    f.driver.expression=expression
# Contact sits immediately behind the real foreground edge, rather than above it.
root.location.z-=.047385;root.update_tag(refresh={'OBJECT'})
for matname,lo,hi in [
('cold broken soil',(.010,.014,.014),(.041,.046,.043)),
('fresh torn rim',(.022,.027,.025),(.082,.086,.072)),
('deep charcoal inner wall',(.002,.004,.004),(.010,.014,.014)),
('broken dusty plaster',(.065,.067,.058),(.16,.16,.135))]:
    mat=bpy.data.materials['FXv009 | '+matname];r=next(n for n in mat.node_tree.nodes if n.type=='VALTORGB');r.color_ramp.elements[0].color=(*lo,1);r.color_ramp.elements[1].color=(*hi,1)
ground=bpy.data.objects['FXv009 | persistent excavated bowl and raised rim']
# Drop the front lip and open the visible inner wall. Keep irregular 3D torn crest.
for v in ground.data.vertices:
    if v.co.y<0:v.co.z-=min(.065,-v.co.y*.14)
    v.co.x*=.83
for ob in asset.objects:
    if 'attached broken rim piece' in ob.name:ob.location.x*=.83
# Dense finite granular dirt jet. Each clod keeps a rigid tetrahedral shape.
# Native absolute keys bake ballistic paths, with coherent vertex identities.
rng=random.Random(10093);verts=[];faces=[];spec=[]
for i in range(340):
    birth=rng.choice([0,0,0,1,1,2]);vz=rng.uniform(3.2,7.4);vx=rng.uniform(-2.2,2.0);vy=rng.uniform(-.35,.50);rad=rng.uniform(.006,.020);origin=(rng.uniform(-.12,.12),rng.uniform(-.10,.08),.02)
    # Bias the fine dirt around the actual ascending jet, not a uniform sky confetti field.
    vx*=.45+.55*(1-vz/8)
    template=[(-rad,-rad*.5,-rad*.6),(rad,-rad*.4,-rad*.4),(0,rad,0),(0,0,rad*1.3)]
    start=len(verts);verts.extend(template);faces.extend([(start,start+1,start+2),(start,start+3,start+1),(start+1,start+3,start+2),(start+2,start+3,start)])
    spec.append((birth,vx,vy,vz,origin,template))
me=bpy.data.meshes.new('FXv009 | 340 rigid granular ejecta');me.from_pydata(verts,[],faces);me.update();me.materials.append(bpy.data.materials['FXv009 | cold broken soil']);me.materials.append(bpy.data.materials['FXv009 | fresh torn rim'])
for poly in me.polygons:poly.material_index=1 if poly.index//4%5==0 else 0
ob=bpy.data.objects.new('FXv009 | finite connected granular earth jet',me);asset.objects.link(ob);ob.parent=root
for age in range(97):
    key=ob.shape_key_add(name=f'EARTH_AGE_{age:03d}');key.interpolation='KEY_LINEAR'
    for j,(birth,vx,vy,vz,origin,template) in enumerate(spec):
        t=max(0,age-birth)/24;land=(vz+math.sqrt(vz*vz+2*9.81*origin[2]))/9.81;u=min(t,land);x=origin[0]+vx*u;y=origin[1]+vy*u;z=max(.003,origin[2]+vz*u-4.905*u*u)
        fade=1 if age>=birth else 0
        if t>land:fade=max(0,1-(t-land)/.35)
        a=t*9;c=math.cos(a);sn=math.sin(a)
        for k,(px,py,pz) in enumerate(template):key.data[j*4+k].co=(x+fade*(c*px+sn*pz),y+fade*py,z+fade*(-sn*px+c*pz))
me.shape_keys.use_relative=False;drive(me.shape_keys,'eval_time','10*max(0,min(96,t))')
ob['motion']='Finite 3-frame emission; 340 rigid tetrahedra follow gravity arcs; fine grains disappear only after ground contact. Not painted cloud mesh.'
# Soft local contact shadow, separate from sculpted bowl. Does not relight the plate.
N=48;V=[(0,0,.004)];F=[];weights=[1.]
for ring in [1,2,3]:
    r=ring/3
    for i in range(N):a=2*math.pi*i/N;rr=1+.06*math.sin(a*7);V.append((1.0*r*math.cos(a)*rr,.70*r*math.sin(a)*rr,.004));weights.append(max(0,1-r)**.6)
for i in range(N):F.append((0,1+i,1+(i+1)%N))
for r in [1,2]:
    for i in range(N):a=1+(r-1)*N+i;b=1+(r-1)*N+(i+1)%N;F.append((a,a+N,b+N,b))
me=bpy.data.meshes.new('FXv009 | contact shadow geometry');me.from_pydata(V,[],F);attr=me.attributes.new('shadow','FLOAT','POINT')
for d,w in zip(attr.data,weights):d.value=w
mat=bpy.data.materials.new('FXv009 | soft contact shadow');mat.use_nodes=True;mat.surface_render_method='BLENDED';nt=mat.node_tree;nt.nodes.clear();a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='shadow';mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(a.outputs['Fac'],mul.inputs[0]);drive(mul.inputs[1],'default_value','.48 if t>=1 else 0');tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.004,.006,.006,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mul.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);me.materials.append(mat);ob=bpy.data.objects.new('FXv009 | persistent local contact shadow',me);asset.objects.link(ob);ob.parent=root
s.frame_set(20);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Ground_Debris_Proof_v009b.blend'),compress=True)
(P/'evidence/refinement.json').write_text(json.dumps({'basis':'Actual keyframe review showed polygonal plate and sparse onset. Corrected source in separate v009b; v009 retained.','changes':['lowered anchor to real foreground edge','darker cold pigments','lowered front crater lip','340 fine coherent ballistic grains','soft anchored contact shadow'],'smoke':False,'gas':False,'new_generated_art':False,'pending':'Actual v009b visual review'},indent=2));print('GROUND_REFINED_NO_SMOKE',flush=True)
