"""Targeted native contour corrections on v016 art and control dependencies.
Original images/UVs, skeleton, contacts and hand drawings are not replaced.
"""
import bpy,math
from mathutils import Matrix,Vector
def attr(me,name,values):
 if me.attributes.get(name):me.attributes.remove(me.attributes[name])
 a=me.attributes.new(name,'FLOAT','POINT');a.data.foreach_set('value',values)
def joint(rig,bone,tail,collection,name):
 o=bpy.data.objects.new(name,None);collection.objects.link(o);o.empty_display_size=.008
 c=o.constraints.new('COPY_LOCATION');c.target=rig;c.subtarget=bone;c.head_tail=float(tail)
 return o
class Graph:
 def __init__(self,mesh,name):
  self.mesh=mesh;self.g=bpy.data.node_groups.new(name,'GeometryNodeTree');self.g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');self.g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');self.n=self.g.nodes;self.l=self.g.links;self.i=self.n.new('NodeGroupInput');self.o=self.n.new('NodeGroupOutput')
 def a(self,name):
  n=self.n.new('GeometryNodeInputNamedAttribute');n.data_type='FLOAT';n.inputs['Name'].default_value=name;return n.outputs['Attribute']
 def val(self,x):
  n=self.n.new('ShaderNodeValue');n.outputs[0].default_value=x;return n.outputs[0]
 def math(self,op,a,b=None):
  n=self.n.new('ShaderNodeMath');n.operation=op;self.l.new(a,n.inputs[0])
  if b is not None:self.l.new(b,n.inputs[1])
  return n.outputs[0]
 def vec(self,op,a,b=None):
  n=self.n.new('ShaderNodeVectorMath');n.operation=op;self.l.new(a,n.inputs[0])
  if b is not None:self.l.new(b,n.inputs[3] if op=='SCALE' else n.inputs[1])
  return n.outputs['Value'] if op in ['LENGTH','DOT_PRODUCT','DISTANCE'] else n.outputs['Vector']
 def loc(self,o):
  n=self.n.new('GeometryNodeObjectInfo');n.transform_space='RELATIVE';n.inputs['Object'].default_value=o;return n.outputs['Location']
 def normal(self,t):
  s=self.n.new('ShaderNodeSeparateXYZ');self.l.new(t,s.inputs[0]);n=self.n.new('ShaderNodeCombineXYZ');self.l.new(self.math('MULTIPLY',s.outputs['Z'],self.val(-1)),n.inputs['X']);self.l.new(s.outputs['X'],n.inputs['Z']);return self.vec('NORMALIZE',n.outputs[0])
 def flat_depth(self,p,depth):
  s=self.n.new('ShaderNodeSeparateXYZ');self.l.new(p,s.inputs[0]);n=self.n.new('ShaderNodeCombineXYZ');self.l.new(s.outputs['X'],n.inputs['X']);self.l.new(depth,n.inputs['Y']);self.l.new(s.outputs['Z'],n.inputs['Z']);return n.outputs[0]
 def finish(self,p):
  n=self.n.new('GeometryNodeSetPosition');self.l.new(self.i.outputs['Geometry'],n.inputs['Geometry']);self.l.new(p,n.inputs['Position']);self.l.new(n.outputs['Geometry'],self.o.inputs['Geometry']);mod=self.mesh.modifiers.new('V017 live corrective contour','NODES');mod.node_group=self.g
def smooth(a,b,t):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def arms(mesh,collection,controls):
 rig=mesh.parent;who=rig['character'];side='near' if mesh.name.endswith('near') else 'far';role=mesh['v007_role'];skin='drawn skin' in mesh.name
 H=joint(rig,'upper_arm_'+side,0,collection,mesh.name+' | V017 shoulder');E=joint(rig,'forearm_'+side,0,collection,mesh.name+' | V017 elbow');W=joint(rig,'forearm_'+side,1,collection,mesh.name+' | V017 wrist')
 count=len(mesh.data.vertices)//2;ts=[(i//2)/(count-1) for i in range(count*2)]
 if role=='drawn_cuff':ts=[(15+i//2)/18 for i in range(count*2)]
 widths=[abs(p.value) for p in mesh.data.attributes['V016_width'].data]
 for m in list(mesh.modifiers):mesh.modifiers.remove(m)
 g=Graph(mesh,'V017 rounded painted arm | '+mesh.name);h,e,w=[g.loc(o) for o in [H,E,W]];u=g.vec('NORMALIZE',g.vec('SUBTRACT',e,h));v=g.vec('NORMALIZE',g.vec('SUBTRACT',w,e))
 if not skin:
  ru=min(.043,rig.data.bones['upper_arm_'+side].length*.14);rl=min(.025,rig.data.bones['forearm_'+side].length*.16)
  hs=[];es=[];us=[];vs=[];dus=[];dvs=[]
  for t in ts:
   if t<.72:
    q=t/.72;hs.append(1-q);es.append(q);us.append(-ru*q);vs.append(0);dus.append(1);dvs.append(0)
   else:
    q=(t-.72)/.28;hs.append(0);es.append(1);us.append(-ru*(1-q)**2);vs.append(rl*q*q);dus.append(ru*(1-q));dvs.append(rl*q)
  for name,values in [('H',hs),('E',es),('U',us),('V',vs),('DU',dus),('DV',dvs)]:attr(mesh.data,'V017_'+name,values)
  center=g.vec('ADD',g.vec('ADD',g.vec('SCALE',h,g.a('V017_H')),g.vec('SCALE',e,g.a('V017_E'))),g.vec('ADD',g.vec('SCALE',u,g.a('V017_U')),g.vec('SCALE',v,g.a('V017_V'))))
  tangent=g.vec('ADD',g.vec('SCALE',u,g.a('V017_DU')),g.vec('SCALE',v,g.a('V017_DV')))
  widths=[x*(1-.22*smooth(.74,1,t)) for x,t in zip(widths,ts)]
 else:
  # A slight anatomical bow and a quieter taper into the actual hand root.
  attr(mesh.data,'V017_t',ts);attr(mesh.data,'V017_sag',[.004*math.sin(math.pi*t) for t in ts])
  length=g.vec('LENGTH',g.vec('SUBTRACT',w,e));travel=g.math('ADD',g.math('MULTIPLY',g.math('ADD',length,g.val(.014)),g.a('V017_t')),g.val(-.008))
  center=g.vec('ADD',e,g.vec('SCALE',v,travel));center=g.vec('ADD',center,g.vec('SCALE',g.normal(v),g.a('V017_sag')));tangent=v
  widths=[x*(1-.22*smooth(.55,1,t))*(.94+.08*math.sin(math.pi*t)) for x,t in zip(widths,ts)]
 attr(mesh.data,'V017_width',[x*(-1 if i%2==0 else 1) for i,x in enumerate(widths)])
 depth=g.a('V016_depth')
 if side=='far':
  wrist=controls[who,'WRIST_far'];node=g.n.new('ShaderNodeValue');node.name='V017 far arm front layer override';fc=node.outputs[0].driver_add('default_value');v=fc.driver.variables.new();v.name='front';v.targets[0].id=wrist;v.targets[0].data_path='["FrontLayer"]';fc.driver.expression='max(0,min(1,front))'
  frontdepth=-.035 if skin else -.033 if role=='drawn_cuff' else -.032
  depth=g.math('ADD',depth,g.math('MULTIPLY',g.math('SUBTRACT',g.val(frontdepth),depth),node.outputs[0]))
 p=g.vec('ADD',center,g.vec('SCALE',g.normal(tangent),g.a('V017_width')));p=g.flat_depth(p,depth);g.finish(p)
 sub=mesh.modifiers.new('V017 soft contour corners / original UV','SUBSURF');sub.subdivision_type='CATMULL_CLARK';sub.levels=2;sub.render_levels=2;sub.show_only_control_edges=True
 mesh['v017_corrective']='Rounded elbow path shared by sleeve/cuff; tapered bowed forearm; native subdivision rounds exposed strip corners. Original UV/image/material retained.'
 return {'mesh':mesh.name,'method':'shared rounded elbow path' if not skin else 'bowed tapered forearm','source_rows':count,'subdivision':2}
def legs(mesh):
 # Preserve the existing thigh support station and exact boot-entry anchors.
 # Correct only the central knee/upper-shin region; native contacts stay live.
 rig=mesh.parent;side='near' if mesh.name.endswith('near') else 'far';g=next(m.node_group for m in mesh.modifiers if m.type=='NODES');nodes=g.nodes;links=g.links
 if rig['character']!='BOY':return {'mesh':mesh.name,'method':'retained source skin contour; compression handled in skirt'}
 infos=[n for n in nodes if n.bl_idname=='GeometryNodeObjectInfo'];locs=[]
 for tag in [' | H',' | K',' | boot collar']:
  locs.append(next(n.outputs['Location'] for n in infos if n.inputs['Object'].default_value and n.inputs['Object'].default_value.name.endswith(tag)))
 def vec(op,a,b=None):
  n=nodes.new('ShaderNodeVectorMath');n.operation=op;links.new(a,n.inputs[0])
  if b is not None:links.new(b,n.inputs[1])
  return n.outputs['Value'] if op=='DOT_PRODUCT' else n.outputs['Vector']
 def mathnode(op,a,b=None):
  n=nodes.new('ShaderNodeMath');n.operation=op;links.new(a,n.inputs[0])
  if b is not None:
   if isinstance(b,(int,float)):n.inputs[1].default_value=b
   else:links.new(b,n.inputs[1])
  return n.outputs[0]
 un=vec('NORMALIZE',vec('SUBTRACT',locs[1],locs[0]));vn=vec('NORMALIZE',vec('SUBTRACT',locs[2],locs[1]));dot=vec('DOT_PRODUCT',un,vn);one=nodes.new('ShaderNodeValue');one.outputs[0].default_value=1
 bend=mathnode('MINIMUM',mathnode('MAXIMUM',mathnode('SUBTRACT',one.outputs[0],dot),0),1.5)
 weights=[]
 for i in range(len(mesh.data.vertices)):
  t=(i//2)/32;env=smooth(.34,.46,t)*(1-smooth(.61,.79,t));notch=math.exp(-((t-.50)/.055)**2);weights.append(env*(.04 if i%2 else -.25-.10*notch))
 attr(mesh.data,'V017_compression_width',weights);a=nodes.new('GeometryNodeInputNamedAttribute');a.data_type='FLOAT';a.inputs['Name'].default_value='V017_compression_width'
 scale=mathnode('ADD',one.outputs[0],mathnode('MULTIPLY',bend,a.outputs['Attribute']))
 widthnode=next(n for n in nodes if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value=='V016_width');original_links=list(widthnode.outputs['Attribute'].links);corrected=mathnode('MULTIPLY',widthnode.outputs['Attribute'],scale)
 for link in original_links:links.new(corrected,link.to_socket)
 mesh['v017_corrective']='Pose-driven knee compression: quieter inner fold, fuller outer cap; thigh brace station and boot entry unchanged.'
 return {'mesh':mesh.name,'method':'bend-driven asymmetric knee width','brace_station_unchanged':True}
def garment(mesh,controls):
 rig=mesh.parent;who=rig['character'];mesh.shape_key_add(name='Basis');key=mesh.shape_key_add(name='V017 compression / lifted cloth hem')
 for i,v in enumerate(mesh.data.vertices):
  p=v.co
  if who=='GIRL':
   # Keep the front cloth over the loaded knee rather than lifting it away
   # into a visible triangular gap. Tuck the slack rear hem toward the body.
   env=smooth(.70,.30,p.z);front=smooth(-.10,.22,p.x);key.data[i].co.z+=env*(.030-.012*front);key.data[i].co.x+=env*(.020+.010*front)
  else:
   env=smooth(.80,.58,p.z);front=smooth(-.12,.18,p.x);key.data[i].co.z+=env*(.009+.012*front)
 fc=key.driver_add('value');d=fc.driver
 for name,side in [('dn','near'),('df','far')]:
  v=d.variables.new();v.name=name;v.type='LOC_DIFF';v.targets[0].id=controls[who,'HIP'];v.targets[1].id=controls[who,'ANKLE_'+side]
 d.expression='max(0,min(1,(0.50-(dn+df)*0.5)/0.15))'
 mesh['v017_corrective']='Distance-driven hem compression drawing; neutral source paint/weights retained; no performance clock.'
 return {'mesh':mesh.name,'method':'native distance-driven hem corrective','max_front_lift_m':.018 if who=='GIRL' else .021}
