"""Project-specific 2.5D receiver: actual native contact shadows over original paint."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;root=bpy.data.objects['FXv010 | fixed impact anchor and timing'];asset=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST']
terrain=bpy.data.objects['FXv010 | true depressed ground and irregular cut wall'];m=terrain.data.materials[0];nt=m.node_tree
# Original paint remains the albedo. White diffuse is used only as a shadow factor.
white=nt.nodes.new('ShaderNodeBsdfDiffuse');white.inputs['Color'].default_value=(1,1,1,1);white.inputs['Roughness'].default_value=1
rgb=nt.nodes.new('ShaderNodeShaderToRGB');nt.links.new(white.outputs[0],rgb.inputs[0]);bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(rgb.outputs[0],bw.inputs[0]);shadow=nt.nodes.new('ShaderNodeMapRange');shadow.clamp=True;shadow.inputs['From Min'].default_value=.08;shadow.inputs['From Max'].default_value=.65;shadow.inputs['To Min'].default_value=.20;shadow.inputs['To Max'].default_value=1;nt.links.new(bw.outputs[0],shadow.inputs[0])
em=next(n for n in nt.nodes if n.type=='EMISSION');color=em.inputs[0].links[0].from_socket;mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;nt.links.new(color,mul.inputs[1]);nt.links.new(shadow.outputs[0],mul.inputs[2]);nt.links.new(mul.outputs[0],em.inputs[0])
bg=next(n.image for n in nt.nodes if n.type=='TEX_IMAGE')
# Large exact-projection apron catches shadows at all validated landing points.
N=96;rings=[1.24,1.75,2.5,3.5,4.5];V=[];F=[];coverage=[]
for ring,r in enumerate(rings):
    for j in range(N):
        a=2*math.pi*j/N;V.append((.65*r*math.cos(a),.55*r*math.sin(a),-.002));coverage.append(0 if ring==len(rings)-1 else 1)
for k in range(len(rings)-1):
    for j in range(N):a=k*N+j;b=k*N+(j+1)%N;F.append((a,a+N,b+N,b))
me=bpy.data.meshes.new('FXv010 | projected shadow receiver apron');me.from_pydata(V,[],F);me.update()
for name,values in [('ground_coverage',coverage),('ground_shade',[1.]*len(V))]:
    attr=me.attributes.new(name,'FLOAT','POINT')
    for d,v in zip(attr.data,values):d.value=v
uv=me.uv_layers.new(name='Exact held-camera original paint')
for l in me.loops:q=world_to_camera_view(s,s.camera,root.location+me.vertices[l.vertex_index].co);uv.data[l.index].uv=(q.x,q.y)
me.materials.append(m);o=bpy.data.objects.new('FXv010 | projected ground shadow receiver | local proof',me);asset.objects.link(o);o.parent=root
o['purpose']='Native cast/contact shadows multiply exact original painted ground. Required in this held-camera proof because the background painting cannot receive 3D shadows.'
s.frame_set(120);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Earth_Rupture_Shadow_v010f.blend'),compress=True)
(P/'evidence/contact_shadow_construction.json').write_text(json.dumps({'method':'Native white-diffuse ShaderToRGB shadow factor multiplies original projected paint; exact albedo retained in unshadowed regions.','receiver_radii_metres':[.65*4.5,.55*4.5],'original_sources_mutated':False,'status':'Actual final-camera keyframe comparison required.','limitation':'Ground texture projection is specific to the held camera; this is not automatic moving-camera integration.'},indent=2));print('PROJECTED_CONTACT_RECEIVER_READY',flush=True)
