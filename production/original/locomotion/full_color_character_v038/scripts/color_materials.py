"""Native painterly color treatment. No bitmap edits or geometry/head turns."""
import bpy,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
PALETTES={
 'skin':{'range':.055,'stops':[(0,'744b36'),(.20,'a97754'),(.60,'c99b73'),(1,'dfba92')]},
 'hair':{'range':.09,'stops':[(0,'1a1513'),(.25,'473326'),(.65,'795b40'),(1,'a48660')]},
 'coat':{'range':.065,'stops':[(0,'17292e'),(.20,'3f6267'),(.55,'6c8988'),(1,'9ca99b')]},
 'linen':{'range':.055,'stops':[(0,'4d554f'),(.25,'8b9382'),(.65,'b8bba3'),(1,'d8d3b7')]},
 'trousers':{'range':.085,'stops':[(0,'252d28'),(.25,'4d5747'),(.65,'777d62'),(1,'a2a087')]},
 'shoes':{'range':.10,'stops':[(0,'201d1b'),(.25,'49372a'),(.65,'766049'),(1,'a38c68')]}}
def linear_hex(s):
 v=[int(s[i:i+2],16)/255 for i in [0,2,4]];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
class Nodes:
 def __init__(self,m):self.m=m;self.n=m.node_tree.nodes;self.l=m.node_tree.links
 def math(self,op,a,b=None):
  n=self.n.new('ShaderNodeMath');n.operation=op
  for x,k in [(a,0),(b,1)]:
   if x is None:continue
   if isinstance(x,(int,float)):n.inputs[k].default_value=x
   else:self.l.new(x,n.inputs[k])
  return n.outputs[0]
 def mix(self,a,b,f):
  n=self.n.new('ShaderNodeMixRGB')
  for x,k in [(f,0),(a,1),(b,2)]:
   if isinstance(x,tuple):n.inputs[k].default_value=x
   elif isinstance(x,(float,int)):n.inputs[k].default_value=x
   else:self.l.new(x,n.inputs[k])
  return n.outputs[0]
 def ramp(self,gray,role):
  spec=PALETTES[role];v=self.math('DIVIDE',gray,spec['range']);n=self.n.new('ShaderNodeValToRGB');n.name='V038 '+role+' painterly palette';n.color_ramp.interpolation='EASE'
  while len(n.color_ramp.elements)>2:n.color_ramp.elements.remove(n.color_ramp.elements[-1])
  for i,(position,color) in enumerate(spec['stops']):
   e=n.color_ramp.elements[i] if i<2 else n.color_ramp.elements.new(position);e.position=position;e.color=linear_hex(color)
  self.l.new(v,n.inputs[0]);return n.outputs[0]
 def polygon(self,x,y,poly):
  V=[Vector((a,b,0)) for a,b in poly];tris=tessellate_polygon([V]);inside=None
  for triangle in tris:
   tri=tuple(V[i] for i in triangle) if isinstance(triangle[0],int) else tuple(triangle)
   orient=(tri[1].x-tri[0].x)*(tri[2].y-tri[0].y)-(tri[1].y-tri[0].y)*(tri[2].x-tri[0].x);sign=1 if orient>0 else -1;mask=None
   for a,b in zip(tri,tri[1:]+tri[:1]):
    cross=self.math('SUBTRACT',self.math('MULTIPLY',b.x-a.x,self.math('SUBTRACT',y,a.y)),self.math('MULTIPLY',b.y-a.y,self.math('SUBTRACT',x,a.x)));q=self.math('GREATER_THAN',self.math('MULTIPLY',cross,sign),-.00001);mask=q if mask is None else self.math('MULTIPLY',mask,q)
   inside=mask if inside is None else self.math('MAXIMUM',inside,mask)
  return inside
def recolor(original,role,name,head=False,garment=False):
 m=original.copy();m.name='V038 COLOR | '+name;original.use_fake_user=True;G=Nodes(m);tex=next(n for n in G.n if n.type=='TEX_IMAGE' and n.image);bw=G.n.new('ShaderNodeRGBToBW');G.l.new(tex.outputs['Color'],bw.inputs[0]);gray=bw.outputs[0]
 if head:
  uv=G.n.new('ShaderNodeTexCoord');sep=G.n.new('ShaderNodeSeparateXYZ');G.l.new(uv.outputs['UV'],sep.inputs[0]);x=G.math('MULTIPLY',sep.outputs['X'],1672);y=G.math('MULTIPLY',G.math('SUBTRACT',1,sep.outputs['Y']),941)
  # Follow the existing forehead/fringe, ear, jaw and exposed neck. The source
  # alpha/profile/hair outline remains the original packed painting.
  poly=[(737,143),(739,155),(734,167),(733,181),(744,192),(744,202),(738,210),(738,220),(732,232),(723,241),(708,242),(691,238),(681,235),(674,249),(669,269),(650,257),(627,245),(638,231),(639,217),(646,206),(650,200),(641,195),(639,184),(641,174),(647,169),(655,173),(660,183),(665,183),(673,173),(682,167),(691,161),(705,157),(719,149)]
  face=G.polygon(x,y,poly);color=G.mix(G.ramp(gray,'hair'),G.ramp(gray,'skin'),face)
  white=G.math('GREATER_THAN',gray,.65);dx=G.math('DIVIDE',G.math('SUBTRACT',x,716),1.0);dy=G.math('DIVIDE',G.math('SUBTRACT',y,175.1),2.25);rr=G.math('ADD',G.math('MULTIPLY',dx,dx),G.math('MULTIPLY',dy,dy));iris=G.math('LESS_THAN',rr,1);eye=G.mix(linear_hex('e7e1cc'),linear_hex('30221b'),iris);color=G.mix(color,eye,G.math('MULTIPLY',white,face));m['V038_face_region_source_pixels']=str(poly);m['V038_eye']='Original eye opening retained; tiny static in-opening dark iris for the natural-color study. No eye/head transform or opening-shape edit.'
 else:color=G.ramp(gray,role)
 if garment:
  # Recolor the existing fabric source before its native construction shading,
  # retaining compression, broad lower turn and the original UV registration.
  targets=[l.to_socket for l in list(tex.outputs['Color'].links) if l.to_node!=bw]
  assert targets
  for socket in targets:
   for link in list(socket.links):G.l.remove(link)
   G.l.new(color,socket)
 else:
  for em in G.n:
   if em.type=='EMISSION':
    for link in list(em.inputs['Color'].links):G.l.remove(link)
    G.l.new(color,em.inputs['Color'])
 m['V038_scope']='Native painterly full-color material; original packed image/alpha/UV retained. No generated/repainted bitmap, diagnostic limb colors or lighting changes.'
 return m
