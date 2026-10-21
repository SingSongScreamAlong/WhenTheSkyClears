import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
O=Path(__file__).resolve().parents[1];R=O.parents[1];sys.path.insert(0,str(O/'scripts'));import pose_spec as M
SRC=R/'work/first_danger_rough_v068/native/WTSC_First_Danger_Rough_Acting_v068e.blend'
DEST=O/'native/WTSC_First_Danger_Development_v069c.blend';assert not DEST.exists()
SH=hashlib.sha256(SRC.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_FIRST_DANGER_ROUGH_WORLD_v068'];S.name='WTSC_FIRST_DANGER_DEVELOPMENT_WORLD_v069';bpy.context.window.scene=S;S.frame_set(913);bpy.context.view_layer.update()
X0=bpy.data.objects['V047 | shared travel | steady .73125mps'].matrix_world.translation.x;Z0=.778
ART={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
for col in list(bpy.data.collections):
 if col.name.startswith('V068 | ROUGH REPLACEMENT'):
  for ob in list(col.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.collections.remove(col)
COL=bpy.data.collections.new('V069 | PAINTED DEVELOPMENT | separate layered2D drawings');S.collection.children.link(COL)
atlas=bpy.data.images.load(str(O/'textures/WTSC_Painted_Head_Angles_v069.png'),check_existing=False);atlas.name='V069 | generated painted head-angle atlas | RGBA';atlas.alpha_mode='STRAIGHT';atlas.pack()
REG=json.loads((O/'evidence/HEAD_REGISTRATION.json').read_text());HREG={(r['character'],r['column']):r for r in REG['heads']}
BOY=bpy.data.images['WTSC_Boy_Painted_Parts_Atlas_v040.png'];PAIR=bpy.data.images['Pair_Painterly_Near_Age_v015.png'];CTRL=bpy.data.objects['V065 | both children | global full-cut color time']
HEADMAT=bpy.data.objects['V044 BOY | head'].data.materials[0].copy();HEADMAT.name='V069 | painted head angles | original layered alpha shader'
for n in HEADMAT.node_tree.nodes:
 if n.type=='TEX_IMAGE':n.image=atlas;n.interpolation='Linear';n.extension='CLIP'
 if n.type=='UVMAP':n.uv_map='V069 | registered head-angle window'

# Safe opaque interior regions of the established painted parts. Original
# brush values/pigment are sampled without altering any image pixels.
PATCH={
 'boy':(BOY,(620,280,665,405)),
 'girl':(PAIR,(982,454,1077,620)),
 'pants':(BOY,(592,760,652,965)),
 'skin':(BOY,(192,716,238,887)),
 'boot':(BOY,(1120,1090,1190,1130)),
 'boy_hair':(BOY,(170,130,250,200)),
 'girl_hair':(PAIR,(960,150,1010,195)),
 'stocking':(PAIR,(918,755,944,785)),
 'linen':(BOY,(1040,510,1100,535))}
ROLE={
 'boy_cloth':('boy',1.0),'boy_light':('boy',1.25),'boy_shadow':('boy',.60),
 'girl_cloth':('girl',1.0),'girl_light':('girl',1.3),'girl_shadow':('girl',.62),
 'pants':('pants',.95),'pants_light':('pants',1.2),'pants_shadow':('pants',.65),
 'skin':('skin',1),'skin_light':('skin',1.08),'skin_shadow':('skin',.78),
 'boot':('boot',.85),'boot_light':('boot',1.1),'boot_shadow':('boot',.6),
 'boy_hair':('boy_hair',.90),'boy_hair_light':('boy_hair',1.3),
 'girl_hair':('girl_hair',1.0),'girl_hair_light':('girl_hair',1.6),
 'stocking':('stocking',1.0),'stocking_shadow':('stocking',.62),'linen':('linen',1.0)}
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
MATS={}
for name,hx in M.PALETTE.items():
 rgb=tuple(linear(int(hx[i:i+2],16)/255) for i in [1,3,5]);mat=bpy.data.materials.new('V069 | retained pigment | '+name);mat.use_nodes=True;N=mat.node_tree.nodes;L=mat.node_tree.links;N.clear()
 out=N.new('ShaderNodeOutputMaterial');em=N.new('ShaderNodeEmission');L.new(em.outputs[0],out.inputs[0]);em.inputs['Color'].default_value=(*rgb,1)
 if name in ROLE:
  key,factor=ROLE[name];im,box=PATCH[key];x0,y0,x1,y1=box;W,H=im.size
  uv=N.new('ShaderNodeUVMap');uv.uv_map='V069 | per-part original pigment'
  mul=N.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=((x1-x0)/W,(y1-y0)/H,1);L.new(uv.outputs[0],mul.inputs[0])
  add=N.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(x0/W,1-y1/H,0);L.new(mul.outputs[0],add.inputs[0])
  tex=N.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';L.new(add.outputs[0],tex.inputs[0])
  tint=N.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(factor,factor,factor,1);L.new(tex.outputs['Color'],tint.inputs[1]);L.new(tint.outputs[0],em.inputs[0])
 mat.diffuse_color=(*rgb,1);MATS[name]=mat
def curves(block):
 ad=block.animation_data
 return [f for l in ad.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves] if ad and ad.action else []
def expose(ob,g):
 for prop in ['hide_render','hide_viewport']:
  for frame,val in [(912,True),(g,False),(g+1,True)]:setattr(ob,prop,val);ob.keyframe_insert(prop,frame=frame)
 for fc in curves(ob):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
 ob.animation_data.action.name=f'V069 | native drawing exposure G{g}'
NEW=[];HEADS=[];CONTACTS=[];ROWS=[]
def drawing(w,g):
 d,p=M.draw_actor(w,g);V=[];F=[];MI=[];UV=[];GROUP=[];mi={n:i for i,n in enumerate(MATS)}
 for layer,q in enumerate(d.paths):
  pts=q['points'];y=-.385-layer*.00025-(.001 if w=='GIRL' else 0);start=len(V)
  xmin=min(x for x,z in pts);xmax=max(x for x,z in pts);zmin=min(z for x,z in pts);zmax=max(z for x,z in pts)
  def uv(a):return ((a[0]-xmin)/max(.001,xmax-xmin),(a[1]-zmin)/max(.001,zmax-zmin))
  if q['fill']:
   poly=[Vector((x,0,z)) for x,z in pts];key={tuple(v):i for i,v in enumerate(poly)};V.extend((x,y,z) for x,z in pts);UV.extend(uv(a) for a in pts)
   for tri in tessellate_polygon([poly]):F.append(tuple(start+(a if isinstance(a,int) else key[tuple(a)]) for a in tri));MI.append(mi[q['fill']])
  if q['stroke']:
   line=list(pts)+([pts[0]] if q['closed'] else []);off=len(V);n=len(line)
   for i,a in enumerate(line):
    before=line[i-1] if i else (line[-2] if q['closed'] else a);after=line[i+1] if i<n-1 else (line[1] if q['closed'] else a);normal=M.perp(M.unit(M.sub(after,before)))
    for sign in [-1,1]:
     b=M.add(a,M.mul(normal,q['width']*.5*sign));V.append((b[0],y-.00009,b[1]));UV.append(uv(b))
   for i in range(n-1):
    a=off+i*2;F.append((a,a+1,a+3,a+2));MI.append(mi[q['stroke']])
  GROUP.append((q['layer'],start,len(V)))
 me=bpy.data.meshes.new(f'V069 {w} | body drawing G{g:04d}');me.from_pydata(V,[],F);me.update()
 for m in MATS.values():me.materials.append(m)
 for poly,m in zip(me.polygons,MI):poly.material_index=m
 uv=me.uv_layers.new(name='V069 | per-part original pigment')
 for l in me.loops:uv.data[l.index].uv=UV[l.vertex_index]
 ob=bpy.data.objects.new(me.name,me);COL.objects.link(ob);ob.location=(X0,0,Z0)
 for name,a,b in GROUP:
  if b>a:ob.vertex_groups.new(name=name).add(list(range(a,b)),1,'REPLACE')
 ob['character']=w;ob['drawing_frame']=g;ob['stage']='Developed layered2D contour with retained source painting; not hand-painted or final approved animation.';expose(ob,g);NEW.append(ob.name)
 # A genuinely separate painted head layer; no crossfade/ghost faces. Neck
 # landmarks register the angle drawings to a common pivot and scale.
 col=M.head_column(w,g,p);r=HREG[w,col];x0,y0,x1,y1=r['bounds_pixels'];ax,ay=r['neck_anchor_pixels'];scale=.00084
 angle=-p['head_pitch']*p['facing']*(.55 if col in [2,4] else 1)
 anchor=M.add(p['shoulder'],(p['offset'],.020));xy=[]
 for x,y in [(x0,y1),(x1,y1),(x1,y0),(x0,y0)]:xy.append(M.add(anchor,M.rotate(((x-ax)*scale,(ay-y)*scale),angle)))
 hm=bpy.data.meshes.new(f'V069 {w} | painted head G{g:04d} | angle {col}');hm.from_pydata([(x,-.452,z) for x,z in xy],[],[(0,1,2,3)]);hm.materials.append(HEADMAT);hu=hm.uv_layers.new(name='V069 | registered head-angle window')
 W,H=REG['size'];values=[(x0/W,1-y1/H),(x1/W,1-y1/H),(x1/W,1-y0/H),(x0/W,1-y0/H)]
 for l in hm.loops:hu.data[l.index].uv=values[l.vertex_index]
 head=bpy.data.objects.new(hm.name,hm);COL.objects.link(head);head.location=(X0,0,Z0);head['character']=w;head['drawing_frame']=g;head['atlas_column']=col;head['head_source']='textures/WTSC_Painted_Head_Angles_v069.png';expose(head,g);HEADS.append(head.name)
 return p
for g in range(913,1081):
 pp={w:drawing(w,g) for w in ['BOY','GIRL']};ROWS.append({'frame':g,'children':pp,'head_columns':{w:M.head_column(w,g,p) for w,p in pp.items()}})
 # Soft, small painted contact mark for the actual new planted soles.
 V=[];F=[]
 for w,p in pp.items():
  for side,fm in p['feet'].items():
   if not fm['contact']:continue
   x=p['ankle_'+side][0]+p['offset']+.015;ids=[]
   for i in range(32):
    t=i*math.tau/32;ids.append(len(V));V.append((x+.085*math.cos(t),-.31,.0015*math.sin(t)))
   F.append(tuple(ids))
 if V:
  me=bpy.data.meshes.new(f'V069 | contact drawing G{g}');me.from_pydata(V,[],F);me.materials.append(MATS['contact']);ob=bpy.data.objects.new(me.name,me);COL.objects.link(ob);ob.location=(X0,0,Z0-.001);expose(ob,g);CONTACTS.append(ob.name)
 if (g-913)%16==0:print('V069_DRAWING',g,len(NEW),len(HEADS),flush=True)
crypto=S.compositing_node_group.nodes['V065 | existing children | visible drawing matte'];crypto.matte_id=','.join(NEW+HEADS)
S.frame_start=913;S.frame_end=1080;S.render.fps=24;S.timeline_markers.clear()
for f,label in M.BEATS:S.timeline_markers.new('V069 | '+label,frame=f)
S['V069_scope']='Separate7-second development candidate; no full-trailer integration.'
S['V069_changes']='168 body drawings per child, painted head-angle layers, original cloth/skin/leather pigments, lower bent linked arms and relaxing free hands. Heads remain generated likeness studies.'
for sc in bpy.data.scenes:
 if sc==S or 'V065' in sc.name or 'v065' in sc.name:
  sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2
  sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
  if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=24
assert all(hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h for n,h in ART.items())
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SH
report={'source':str(SRC),'source_sha256':SH,'native':str(DEST),'world_scene':S.name,'range':[913,1080],'fps':24,'native_resolution':[3840,2160],'body_objects':NEW,'head_objects':HEADS,'contact_objects':CONTACTS,'new_drawing_objects':NEW,'original_painting_hashes':ART,'new_atlas':str(O/'textures/WTSC_Painted_Head_Angles_v069.png'),'atlas_sha256':hashlib.sha256((O/'textures/WTSC_Painted_Head_Angles_v069.png').read_bytes()).hexdigest(),'head_source':'Built-in imagegen reference-led atlas; original identities/paintings used as references; generated studies unapproved.','drawing_registration':{'x':X0,'ground_z':Z0},'rows':ROWS,'status':'Separate development review; no final artistic acceptance or full-trailer integration.'}
for name,file in [('AUTHORING | V069 | developed pose and timing','pose_spec.py'),('AUTHORING | V069 | frozen v068 contour construction','base_pose_spec.py')]:bpy.data.texts.new(name).write((O/'scripts'/file).read_text())
bpy.data.texts.new('START HERE | V069 | development review').write(json.dumps({k:v for k,v in report.items() if k not in ['rows','original_painting_hashes','body_objects','head_objects','new_drawing_objects','contact_objects']},indent=2))
S.frame_set(979);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True);report['native_sha256']=hashlib.sha256(DEST.read_bytes()).hexdigest();(O/'evidence/BUILD.json').write_text(json.dumps(report,indent=2));print('V069_NATIVE_SAVED',DEST,flush=True)
