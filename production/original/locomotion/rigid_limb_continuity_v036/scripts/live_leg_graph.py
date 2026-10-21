"""Live piecewise leg drawing axes. Existing paint, topology and cuff remain."""
import bpy,math
class G:
 def __init__(self,o):
  self.g=bpy.data.node_groups.new('V036 | rigid thigh shin drawing | '+o.name,'GeometryNodeTree');self.g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');self.g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');self.n=self.g.nodes;self.l=self.g.links;self.i=self.n.new('NodeGroupInput');self.o=self.n.new('NodeGroupOutput');self.pos=self.n.new('GeometryNodeInputPosition').outputs[0]
 def val(self,x):n=self.n.new('ShaderNodeValue');n.outputs[0].default_value=x;return n.outputs[0]
 def socket(self,x):return self.val(x) if isinstance(x,(int,float)) else x
 def m(self,op,a,b=None):
  n=self.n.new('ShaderNodeMath');n.operation=op;self.l.new(self.socket(a),n.inputs[0])
  if b is not None:self.l.new(self.socket(b),n.inputs[1])
  return n.outputs[0]
 def v(self,op,a,b=None):
  n=self.n.new('ShaderNodeVectorMath');n.operation=op;self.l.new(a,n.inputs[0])
  if b is not None:self.l.new(self.socket(b),n.inputs[3] if op=='SCALE' else n.inputs[1])
  return n.outputs['Value'] if op in ['DOT_PRODUCT','LENGTH'] else n.outputs['Vector']
 def add(self,a,b):return self.v('ADD',a,b)
 def sub(self,a,b):return self.v('SUBTRACT',a,b)
 def scale(self,a,b):return self.v('SCALE',a,b)
 def lerp(self,a,b,t):return self.add(self.scale(a,self.m('SUBTRACT',1,t)),self.scale(b,t))
 def attr(self,name):n=self.n.new('GeometryNodeInputNamedAttribute');n.data_type='FLOAT';n.inputs['Name'].default_value=name;return n.outputs['Attribute']
 def sample(self,index):
  n=self.n.new('GeometryNodeSampleIndex');n.data_type='FLOAT_VECTOR';n.domain='POINT';self.l.new(self.i.outputs['Geometry'],n.inputs['Geometry']);self.l.new(self.pos,n.inputs['Value']);self.l.new(self.socket(index),n.inputs['Index']);return n.outputs['Value']
 def loc(self,o):
  n=self.n.new('GeometryNodeObjectInfo');n.transform_space='RELATIVE';n.inputs['Object'].default_value=o;return n.outputs['Location']
 def normal(self,a):
  n=self.n.new('ShaderNodeSeparateXYZ');self.l.new(a,n.inputs[0]);c=self.n.new('ShaderNodeCombineXYZ');self.l.new(self.m('MULTIPLY',n.outputs['Z'],-1),c.inputs['X']);self.l.new(n.outputs['X'],c.inputs['Z']);return c.outputs[0]
 def flat(self,a,y):
  n=self.n.new('ShaderNodeSeparateXYZ');self.l.new(a,n.inputs[0]);c=self.n.new('ShaderNodeCombineXYZ');self.l.new(n.outputs['X'],c.inputs['X']);self.l.new(self.socket(y),c.inputs['Y']);self.l.new(n.outputs['Z'],c.inputs['Z']);return c.outputs[0]
 def switch(self,a,b,test):
  n=self.n.new('GeometryNodeSwitch');n.input_type='VECTOR';self.l.new(test,n.inputs['Switch']);self.l.new(a,n.inputs['False']);self.l.new(b,n.inputs['True']);return n.outputs[0]
 def finish(self,o,p):
  n=self.n.new('GeometryNodeSetPosition');self.l.new(self.i.outputs['Geometry'],n.inputs['Geometry']);self.l.new(p,n.inputs['Position']);self.l.new(n.outputs[0],self.o.inputs['Geometry']);m=o.modifiers.new('V036 | live rigid segment contours','NODES');m.node_group=self.g
def build(o,rig,col,side):
 def probe(bone,tail,name):
  p=bpy.data.objects.new('V036 | '+side+' | '+name,None);col.objects.link(p);p.empty_display_size=.009;c=p.constraints.new('COPY_LOCATION');c.target=rig;c.subtarget=bone;c.head_tail=tail;return p
 H=probe('thigh_'+side,0,'actual HIP');K=probe('shin_'+side,0,'actual KNEE');A=probe('shin_'+side,1,'actual ANKLE')
 def attr(name,V):
  a=o.data.attributes.get(name) or o.data.attributes.new(name,'FLOAT','POINT');a.data.foreach_set('value',V)
 ts=[(i//7)/96 for i in range(len(o.data.vertices))];attr('V036_t',ts);attr('V036_row_base',[(i//7)*7 for i in range(len(ts))]);attr('V036_width_scale',[1-.085*math.exp(-((t-.58)/.12)**2)-.025*math.exp(-((t-.28)/.24)**2) for t in ts]);attr('V036_cuff_mix',[max(0,min(1,(t-.79)/.13))**2*(3-2*max(0,min(1,(t-.79)/.13))) for t in ts])
 g=G(o);h,k,a=[g.loc(p) for p in [H,K,A]];h=g.flat(h,0);k=g.flat(k,0);a=g.flat(a,0);u=g.v('NORMALIZE',g.sub(k,h));v=g.v('NORMALIZE',g.sub(a,k));oldh=g.scale(g.add(g.sample(0),g.sample(6)),.5);olde=g.scale(g.add(g.sample(672),g.sample(678)),.5);hs=g.add(h,g.scale(u,g.v('DOT_PRODUCT',g.sub(oldh,h),u)));es=g.add(k,g.scale(v,g.v('DOT_PRODUCT',g.sub(olde,k),v)));t=g.attr('V036_t');r=.022;lu=g.v('LENGTH',g.sub(k,hs));lv=g.v('LENGTH',g.sub(es,k));ta=g.m('MULTIPLY',.58,g.m('SUBTRACT',1,g.m('DIVIDE',r,lu)));tb=g.m('ADD',.58,g.m('MULTIPLY',.42,g.m('DIVIDE',r,lv)));q=g.m('MINIMUM',1,g.m('MAXIMUM',0,g.m('DIVIDE',g.m('SUBTRACT',t,ta),g.m('SUBTRACT',tb,ta))));oneq=g.m('SUBTRACT',1,q)
 upper=g.lerp(hs,k,g.m('DIVIDE',t,.58));lower=g.lerp(k,es,g.m('DIVIDE',g.m('SUBTRACT',t,.58),.42));is_lower=g.m('GREATER_THAN',t,.58);lin=g.switch(upper,lower,is_lower);tan=g.switch(u,v,is_lower)
 c1=g.sub(k,g.scale(u,r));c2=g.add(k,g.scale(v,r));curve=g.add(g.add(g.scale(c1,g.m('MULTIPLY',oneq,oneq)),g.scale(k,g.m('MULTIPLY',2,g.m('MULTIPLY',q,oneq)))),g.scale(c2,g.m('MULTIPLY',q,q)));inside=g.m('MULTIPLY',g.m('GREATER_THAN',t,ta),g.m('LESS_THAN',t,tb));center=g.switch(lin,curve,inside);tan=g.switch(tan,g.v('NORMALIZE',g.lerp(u,v,q)),inside);normal=g.normal(tan)
 base=g.attr('V036_row_base');left=g.sample(base);right=g.sample(g.m('ADD',base,6));oldc=g.scale(g.add(left,right),.5);oldn=g.v('NORMALIZE',g.sub(right,left));oldt=g.scale(g.normal(oldn),-1);d=g.sub(g.pos,oldc);width=g.m('MULTIPLY',g.v('DOT_PRODUCT',d,oldn),g.attr('V036_width_scale'));axial=g.v('DOT_PRODUCT',d,oldt);new=g.add(g.add(center,g.scale(normal,width)),g.scale(tan,axial));sep=g.n.new('ShaderNodeSeparateXYZ');g.l.new(g.pos,sep.inputs[0]);new=g.flat(new,sep.outputs['Y']);new=g.lerp(new,g.pos,g.attr('V036_cuff_mix'));g.finish(o,new)
 o['V036_contour']='Live actual thigh/shin axes;22mm local knee transition;8.5percent local knee-width reduction; original UV/paint; blend to inherited rolled-cuff rows79–92percent. No skeleton or timing changes.'
 return {'object':o.name,'node_count':len(g.n),'knee_transition_radius_m':r,'knee_width_reduction_fraction':.085,'cuff_retained_from_t':.92}
