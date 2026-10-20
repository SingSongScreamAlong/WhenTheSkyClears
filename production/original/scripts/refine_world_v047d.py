"""World-fixed foreground repaint and rooted native wind wisps; retain v047c acting."""
import bpy,json,math,random,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';prior=json.loads((N/'build_v047c.json').read_text())
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v047d.blend';assert not out.exists()
s=bpy.data.scenes[prior['world_scene']];m=bpy.data.scenes[prior['master_scene']];bpy.context.window.scene=s;s.frame_set(1901);bpy.context.view_layer.update()
bank=s.objects['v020 | Foreground bank | continuous blended paint'];old_material=bank.data.materials[0]
mat=old_material.copy();mat.name='v047d | original fixed bank with bespoke painted variation';bank.data.materials[0]=mat
nt=mat.node_tree;uv=bank.data.uv_layers.new(name='v047 | fixed bank projection from1901')
for loop in bank.data.loops:
 p=world_to_camera_view(s,s.camera,bank.matrix_world@bank.data.vertices[loop.vertex_index].co)
 uv.data[loop.index].uv=(p.x,p.y)
uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map=uv.name
paint=R/'sets/refinement_v047/Foreground_Bank_Paintover_v047.png'
im=bpy.data.images.load(str(paint),check_existing=True);im.pack()
tex=nt.nodes.new('ShaderNodeTexImage');tex.name='v047 | new original bank paint only';tex.image=im;tex.extension='EXTEND';nt.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
separate=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uvnode.outputs['UV'],separate.inputs[0])
def ramp(value,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
 nt.links.new(value,n.inputs['Value'])
 for name,v in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=v
 return n.outputs[0]
def multiply(a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation='MULTIPLY';nt.links.new(a,n.inputs[0]);nt.links.new(b,n.inputs[1]);return n.outputs[0]
fac=multiply(ramp(separate.outputs['X'],.0,.09,0,1),ramp(separate.outputs['X'],.91,1,1,0))
fac=multiply(fac,ramp(separate.outputs['Y'],.215,.26,1,0))
fac=multiply(fac,ramp(separate.outputs['Y'],-.025,0,0,1))
receiver=nt.nodes['v041 DORMANT | source-bound local warmth'];target=receiver.inputs[6];original=target.links[0].from_socket
mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='v047 | fixed ground paint mask; event light downstream'
nt.links.new(fac,mix.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(tex.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],target)
bank['v047_paint_scope']='Existing bank material RGB only. UVs baked at1901; no camera-driven mapping, tracking or image-wide overlay. Original bank alpha unchanged. Original physical light receiver stays downstream.'

collection=bpy.data.collections.new('v047d | rooted charcoal grass, native wind');s.collection.children.link(collection)
rng=random.Random(4721);tufts=[];sample_co=None
def project(p):return world_to_camera_view(s,s.camera,Vector(p))
def solve(axis,target,point):
 lo,hi=(90.,130.) if axis==0 else (-15.,10.)
 for _ in range(36):
  mid=(lo+hi)/2;point[axis]=mid;q=project(point);value=q.x if axis==0 else q.y
  if value<target:lo=mid
  else:hi=mid
 point[axis]=(lo+hi)/2
 return point
for idx,u in enumerate([.025,.113,.181,.305,.449,.593,.728,.843,.967]):
 p=[108.,-4.97,.4];solve(2,rng.uniform(.105,.185),p);solve(0,u,p)
 root=bpy.data.objects.new(f'v047d | fixed grass root{idx:02d}',None);collection.objects.link(root);root.location=p
 tuft={'root':root.name,'world_location':list(p),'blade_count':0}
 material=bpy.data.materials.new(f'v047d | subdued dry charcoal blade{idx:02d}');material.use_nodes=True
 tree=material.node_tree;tree.nodes.clear();em=tree.nodes.new('ShaderNodeEmission');value=rng.uniform(.008,.018);em.inputs[0].default_value=(value*.90,value,value*.93,1);output=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(em.outputs[0],output.inputs[0])
 for blade in range(rng.randint(4,7)):
  data=bpy.data.curves.new(f'v047d | grass {idx:02d} blade{blade:02d}','CURVE');data.dimensions='3D';data.resolution_u=8;data.bevel_depth=rng.uniform(.00055,.0010);data.bevel_resolution=1
  sp=data.splines.new('BEZIER');sp.bezier_points.add(3);height=rng.uniform(.035,.115);lean=rng.uniform(-.06,.06);spread=rng.uniform(-.025,.025);phase=rng.uniform(0,math.tau);amp=rng.uniform(.002,.007)
  for k,bp in enumerate(sp.bezier_points):
   t=k/3;bp.co=(spread*(1-t)+lean*t*t,0,height*t);bp.radius=1-.85*t
   bp.handle_left_type=bp.handle_right_type='AUTO'
   if k:
    curve=bp.driver_add('co',0);curve.driver.expression=f'{bp.co.x:.9f}+{amp*t*t:.9f}*sin((frame-1801)/23+{phase:.8f})'
   elif sample_co is None:sample_co=bp
  ob=bpy.data.objects.new(data.name,data);collection.objects.link(ob);ob.parent=root;data.materials.append(material);tuft['blade_count']+=1
 tufts.append(tuft)
bpy.context.view_layer.update()
root_before={o.name:o.matrix_world.copy() for o in collection.objects if o.type=='EMPTY'}
motion=[]
for f in [1801,1844,1881,1920]:
 s.frame_set(f);bpy.context.view_layer.update()
 error=max(max(abs(o.matrix_world[i][j]-root_before[o.name][i][j]) for i in range(4) for j in range(4)) for o in collection.objects if o.type=='EMPTY')
 assert error==0;motion.append({'frame':f,'root_matrix_error':error})
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047d';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v047d'
report=dict(prior);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,
 'foreground':{'source':str(paint),'source_resolution':list(im.size),'source_sha256':hashlib.sha256(paint.read_bytes()).hexdigest(),
  'reference':str(R/'renders/refinement_v047b/Full_1901_4K.png'),'object':bank.name,'original_material':old_material.name,'material':mat.name,
  'method':'Original built-in imagegen bank paintover consumed only through bank RGB on fixed native UVs; untouched original alpha and event-light receiver. No generated character/background pixels used.',
  'texture_limit':'Generated bank painting1672x941; output is natively rendered4K, source paint is not4K.',
  'new_rooted_tufts':tufts,'native_root_error_samples':motion,'artistic_review_pending':True},
 'scope':'Retained v047c head/arm corrections plus fixed bank repaint and subtle rooted native Bezier grass wind. Existing source images, alpha, body/feet/camera, FXv003 and full-trailer source retained.',
 'artistic_acceptance':False,'full_trailer_propagated':False})
text=bpy.data.texts.new('CURRENT v047d | Foreground iteration provenance');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1901);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v047d.json').write_text(json.dumps(report,indent=2))
print('V047D_NATIVE_BUILT',json.dumps({'native':str(out),'sha256':report['sha256'],'tufts':len(tufts),'paint_size':list(im.size)}),flush=True)
