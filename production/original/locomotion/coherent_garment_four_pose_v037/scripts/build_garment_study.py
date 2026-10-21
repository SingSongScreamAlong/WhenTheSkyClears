"""Five static review poses: four construction poses plus F27 overlap check.
Native connected coat surface; retained image UV painting; original motion untouched.
"""
import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P/'reference/PRESERVED_v036.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];old=bpy.data.objects['V025 | COAT drawings | editable GP'];A=json.loads((P/'evidence/COAT_SOURCE_INSPECTION.json').read_text());F=[1,4,11,20,27];R=33;C=17
def action_hash(a):return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
actions={a.name:action_hash(a) for a in bpy.data.actions}
def interp(t,K):
 for (a,v),(b,w) in zip(K,K[1:]):
  if t<=b:return v+(w-v)*((t-a)/(b-a))
 return K[-1][1]
def cat(t,K):
 i=next((j for j in range(len(K)-1) if t<=K[j+1][0]),len(K)-2);a,b=K[i],K[i+1];q=(t-a[0])/(b[0]-a[0]);p0=K[max(0,i-1)][1];p1=a[1];p2=b[1];p3=K[min(len(K)-1,i+2)][1]
 return .5*((2*p1)+(-p0+p2)*q+(2*p0-5*p1+4*p2-p3)*q*q+(-p0+3*p1-3*p2+p3)*q*q*q)
back=[(0,-.050),(.12,-.097),(.28,-.099),(.46,-.084),(.64,-.074),(.80,-.083),(1,-.110)]
front=[(0,.033),(.12,.080),(.28,.110),(.46,.106),(.64,.084),(.80,.079),(1,.076)]
uvrows=[(0,258,620,657,674),(.12,294,578,685,699),(.28,350,576,681,708),(.46,405,572,679,716),(.64,455,560,675,724),(.80,495,552,670,730),(1,535,546,666,734)]
image=bpy.data.images['Pair_Painterly_Near_Age_v015.png'];W,H=image.size;pixels=np.empty(W*H*4,dtype=np.float32);image.pixels.foreach_get(pixels);alpha=pixels.reshape(H,W,4)[:,:,3];uv=[];alpha_initial=[];clamped=0
for row in range(R):
 t=row/(R-1);py=interp(t,[(r[0],r[1]) for r in uvrows]);left,seam,right=[interp(t,[(r[0],r[k]) for r in uvrows]) for k in [2,3,4]]
 for col in range(C):
  s=col/(C-1);px=left+(seam-left)*s/.75 if s<=.75 else seam+(right-seam)*(s-.75)/.25;v=1-py/H;aa=float(alpha[min(H-1,max(0,int(v*H))),min(W-1,max(0,int(px)))])
  alpha_initial.append(aa)
  if aa<.9:
   # Pull a perimeter UV into opaque retained fabric; no bitmap changes/tiling.
   for q in range(1,21):
    candidate=px+(seam-px)*q/20;aa=float(alpha[min(H-1,max(0,int(v*H))),min(W-1,max(0,int(candidate)))])
    if aa>=.9:px=candidate;clamped+=1;break
  uv.append((px/W,v))
col=bpy.data.collections.new('V037 | connected coat | FIVE STATIC REVIEW POSES');S.collection.children.link(col);fore.layer_collection.children[col.name].exclude=True
ctrl=bpy.data.objects.new('V037 | garment review values | static pose selector',None);col.objects.link(ctrl);ctrl['painted']=0.;ctrl['compression']=0.;ctrl.empty_display_size=.02
coords={};records=[]
for f in F:
 S.frame_set(f);bpy.context.view_layer.update();r=A['frames'][str(f)];h=Vector(r['H']);n=Vector(r['N']);U=(n-h).normalized();N=Vector((U.z,0,-U.x));compression=max(0,min(1,(A['frames']['1']['H'][2]-h.z)/.015));arr=[]
 for row in range(R):
  t=row/(R-1);z=.510*(1-t);a=cat(t,back);b=cat(t,front)
  # Lower edge follows existing bend and support compression; no separate flap clock.
  hemweight=max(0,(t-.65)/.35);a+=.004*compression*hemweight;b-=.003*compression*hemweight
  for c in range(C):
   s=c/(C-1);x=a+(b-a)*s;corner=max(0,min(1,(t-.96)/.04));x+=.003*corner*((1-s)**12-s**12);hemrise=(.004*abs(2*s-1)**4+.008*math.exp(-((s-.80)/.075)**2))*t**8;localz=z+hemrise;fold=.17+.22*x;d=math.exp(-((localz-fold)/.018)**2);p=h+U*localz+N*x;p.y=-.017-.0035*math.sin(math.pi*s)**2-.0018*compression*d;arr.append(p)
 # Exact original garment vertical extent per pose. Body/head/limbs are not moved.
 oldmin,oldmax=r['bounds'][2];mn=min(p.z for p in arr);mx=max(p.z for p in arr)
 for p in arr:p.z=oldmin+(p.z-mn)*(oldmax-oldmin)/(mx-mn)
 coords[f]=arr;records.append({'frame':f,'hip':list(h),'neck':list(n),'compression_from_existing_hip_drop':compression,'old_vertical_extent_m':[oldmin,oldmax],'new_vertical_extent_m':[min(p.z for p in arr),max(p.z for p in arr)],'new_horizontal_extent_m':[min(p.x for p in arr),max(p.x for p in arr)]});ctrl['compression']=compression;ctrl.keyframe_insert('["compression"]',frame=f)
faces=[]
for r in range(R-1):
 for c in range(C-1):i=r*C+c;faces.append((i,i+1,i+1+C,i+C))
mesh=bpy.data.meshes.new('V037 | one attached shoulder rib waist hem surface');mesh.from_pydata(coords[1],[],faces);mesh.update();ob=bpy.data.objects.new('V037 | coherent charcoal coat | five pose study',mesh);col.objects.link(ob);ob.parent=T;uvlayer=mesh.uv_layers.new(name='Retained full fabric region | no repeating grain')
for l in mesh.loops:uvlayer.data[l.index].uv=uv[l.vertex_index]
for name,values in [('V037_s',[(i%C)/(C-1) for i in range(R*C)]),('V037_t',[(i//C)/(R-1) for i in range(R*C)])]:a=mesh.attributes.new(name,'FLOAT','POINT');a.data.foreach_set('value',values)
ob.shape_key_add(name='Basis | CONTACT F1')
for f in F[1:]:
 kb=ob.shape_key_add(name='STATIC garment pose F'+str(f));kb.data.foreach_set('co',[v for p in coords[f] for v in p])
 for keyframe in F:kb.value=float(keyframe==f);kb.keyframe_insert('value',frame=keyframe)
for id in [mesh.shape_keys,ctrl]:
 for l in id.animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='CONSTANT'
mat=bpy.data.materials.new('V037 | retained fabric on connected garment | flat-paint switch');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();lk=mat.node_tree.links
def mathnode(op,a,b=None):
 nd=ns.new('ShaderNodeMath');nd.operation=op
 for x,socket in [(a,nd.inputs[0]),(b,nd.inputs[1])]:
  if x is None:continue
  if isinstance(x,(float,int)):socket.default_value=x
  else:lk.new(x,socket)
 return nd.outputs[0]
def attr(name):n=ns.new('ShaderNodeAttribute');n.attribute_name=name;return n.outputs['Fac']
s=attr('V037_s');t=attr('V037_t');roundshade=mathnode('ADD',.88,mathnode('MULTIPLY',.15,mathnode('SINE',mathnode('MULTIPLY',s,math.pi))))
comp=ns.new('ShaderNodeValue');comp.name='V037 existing compression';fc=comp.outputs[0].driver_add('default_value');v=fc.driver.variables.new();v.name='compression';v.targets[0].id=ctrl;v.targets[0].data_path='["compression"]';fc.driver.expression='compression'
center=mathnode('SUBTRACT',.665,mathnode('MULTIPLY',.075,mathnode('SUBTRACT',s,.5)))
def gaussian(center,width):
 d=mathnode('DIVIDE',mathnode('SUBTRACT',t,center),width);return mathnode('EXPONENT',mathnode('MULTIPLY',mathnode('MULTIPLY',d,d),-1))
crease=mathnode('SUBTRACT',1,mathnode('MULTIPLY',.20,mathnode('MULTIPLY',comp.outputs[0],gaussian(center,.026))));ridge=mathnode('MULTIPLY',.075,mathnode('MULTIPLY',comp.outputs[0],gaussian(mathnode('SUBTRACT',center,.028),.021)));shade=mathnode('MULTIPLY',roundshade,mathnode('ADD',crease,ridge))
# Broad garment-local lower-front turn. It is fixed to cloth coordinates in
# every pose, not a hand-following halo or scene lighting change.
lower=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',t,.68),.24)));sd=mathnode('DIVIDE',mathnode('SUBTRACT',s,.60),.25);side=mathnode('EXPONENT',mathnode('MULTIPLY',mathnode('MULTIPLY',sd,sd),-1));shade=mathnode('MULTIPLY',shade,mathnode('SUBTRACT',1,mathnode('MULTIPLY',.18,mathnode('MULTIPLY',lower,side))))
tex=ns.new('ShaderNodeTexImage');tex.name='V037 original full fabric painting';tex.image=image;tex.extension='EXTEND';tex.interpolation='Linear';paint=ns.new('ShaderNodeMixRGB');paint.blend_type='MULTIPLY';paint.inputs[0].default_value=1;paint.inputs[2].default_value=(.95,.95,.95,1);lk.new(tex.outputs['Color'],paint.inputs[1]);switch=ns.new('ShaderNodeMixRGB');switch.name='V037 CONSTRUCTION0 PAINT1';switch.inputs[1].default_value=(.014,.015,.014,1);lk.new(paint.outputs[0],switch.inputs[2]);fc=switch.inputs[0].driver_add('default_value');v=fc.driver.variables.new();v.name='painted';v.targets[0].id=ctrl;v.targets[0].data_path='["painted"]';fc.driver.expression='painted';mul=ns.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;lk.new(switch.outputs[0],mul.inputs[1]);lk.new(shade,mul.inputs[2]);em=ns.new('ShaderNodeEmission');lk.new(mul.outputs[0],em.inputs['Color']);out=ns.new('ShaderNodeOutputMaterial');lk.new(em.outputs[0],out.inputs['Surface']);mesh.materials.append(mat)
old.hide_render=True;old.hide_viewport=True;ob['V037_scope']='Five static garment review poses only:1,4,11,20 plus27 overlap check. No inbetweens or full cycle. Connected shoulder/rib/waist/hem construction; exact original vertical length; retained image UV, no grain tiling. Original character motion/parts unchanged.'
S['V037_status']='STATIC garment construction/art study only. Preferred v036 movement and identity preserved; garment inbetweens NOT authored. Review selected marked frames only.';S.frame_start=1;S.frame_end=27
for f,label in [(1,'CONTACT | STATIC COAT'),(4,'LOADED DOWN | STATIC COAT'),(11,'PASSING | STATIC COAT'),(20,'LOADED RECOVERY | STATIC COAT'),(27,'HAND HEM OVERLAP CHECK')]:S.timeline_markers.new(label,frame=f)
S.frame_set(11);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
changed=[n for n,h in actions.items() if action_hash(bpy.data.actions[n])!=h];assert not changed
report={'scope':'Bounded native garment construction/art study; static poses only','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'frames':F,'main_review_frames':[1,4,11,20],'extra_overlap_frame':27,'original_actions_changed':changed,'vertices':len(mesh.vertices),'quads':len(mesh.polygons),'connected_surface':True,'records':records,'original_paint_image':image.name,'original_image_packed':bool(image.packed_file),'UV_reference_rows_t_y_left_seam_right':uvrows,'UV_points_pulled_into_opaque_fabric':clamped,'source_UV_alpha_min_before_clamp':min(alpha_initial),'texture_repeated_or_new_raster':False,'construction':'One continuous garment surface follows existing pelvis/neck pose. Reduced triangular side flare; continuous front opening/placket mapping; one compression crease derived from existing hip drop; no separate rounded panel overlays.','vertical_extent_max_error_m':max(abs(a-b) for r in records for a,b in zip(r['old_vertical_extent_m'],r['new_vertical_extent_m']))};(P/'evidence/GARMENT_STUDY_BUILD.json').write_text(json.dumps(report,indent=2))
ctrl['painted']=0.;ctrl.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Connected_Garment_Construction_v037.blend'),compress=True);ctrl['painted']=1.;ctrl.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Connected_Garment_Retained_Fabric_v037.blend'),compress=True);print('V037_GARMENT_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['records','UV_reference_rows_t_y_left_seam_right']}),flush=True)
