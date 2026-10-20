"""Registered source-paint construction, not camera-following line overdraw."""
import bpy,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_architecture_v049');SRC=R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend';OUT=O/'WTSC_Registered_School_Depth_v049c.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC'];bpy.context.window.scene=S;school=S.objects['v016 | School | broken windows and plaster'];original_mat=school.data.materials[0];reference=1225;random.seed(49023)
S.render.resolution_percentage=25;S.render.image_settings.media_type='IMAGE';S.render.image_settings.file_format='PNG';S.render.threads_mode='FIXED';S.render.threads=2;S.eevee.taa_render_samples=16
C=bpy.data.collections.new('v049 | REGISTERED SCHOOL | physical aperture and broken wall');S.collection.children.link(C);created=[]
def P(px,py,y=10.):return Vector((65.+(px/1672.-.5)*22.,y,3.29222369194+(.5-py/941.)*12.3815793991))
def make(name,pixels,ys,faces,mats,mi=None):
 me=bpy.data.meshes.new('v049 '+name);verts=[P(x,y,ys if isinstance(ys,(float,int)) else ys[i]) for i,(x,y) in enumerate(pixels)];me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='Paint UV')
 for loop in me.loops:
  x,y=pixels[loop.vertex_index];uv.data[loop.index].uv=(x/1672,1-y/941)
 o=bpy.data.objects.new('v049 | '+name,me);C.objects.link(o)
 for m in mats:me.materials.append(m)
 if mi:
  for poly,index in zip(me.polygons,mi):poly.material_index=index
 o['source_registration']='School_v001.png pixels / exact original card affine transform';o['world_fixed']=True;created.append(o.name);return o
def pigment(name,dark,light,grain=(12,12,12),emission=.78):
 m=bpy.data.materials.new('v049 | '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tc=nt.nodes.new('ShaderNodeTexCoord');v=nt.nodes.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=grain;nt.links.new(tc.outputs['Object'],v.inputs[0]);no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=1;no.inputs['Detail'].default_value=2;no.inputs['Roughness'].default_value=.62;nt.links.new(v.outputs[0],no.inputs[0]);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.22;r.color_ramp.elements[0].color=(*dark,1);r.color_ramp.elements[1].position=.78;r.color_ramp.elements[1].color=(*light,1);nt.links.new(no.outputs['Fac'],r.inputs[0]);em=nt.nodes.new('ShaderNodeEmission');nt.links.new(r.outputs[0],em.inputs[0]);diff=nt.nodes.new('ShaderNodeBsdfDiffuse');diff.inputs['Roughness'].default_value=.6;nt.links.new(r.outputs[0],diff.inputs[0]);mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=emission;nt.links.new(diff.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m
woodV=pigment('worn green sash vertical pigment',(.016,.023,.021),(.044,.054,.043),(52,12,2));woodH=pigment('worn green sash horizontal pigment',(.016,.023,.021),(.044,.054,.043),(2,12,52));woodSide=pigment('wood cut return shadow',(.011,.016,.015),(.026,.033,.027),(20,10,5));stone=pigment('exposed masonry cross section',(.061,.069,.068),(.15,.16,.145),(11,8,13));stoneShadow=pigment('deep cool masonry reveal',(.024,.033,.036),(.069,.079,.078),(10,10,10));chalk=pigment('fracture mineral facets',(.12,.135,.125),(.23,.24,.21),(22,22,22));glass=pigment('painted slate glass',(.042,.057,.064),(.085,.109,.115),(10,10,10),.85);glassEdge=pigment('broken glass cut edge',(.13,.165,.173),(.22,.26,.26),(16,16,16),.9);room=pigment('unlit room depth',(.006,.010,.013),(.018,.025,.027),(3,3,3),.95)
frontPaint=original_mat.copy();frontPaint.name='v049 | registered original painted stone front'
def mathn(nt,op,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,(int,float)):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs[0]
def pixel_nodes(nt):
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='Paint UV';sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0]);return mathn(nt,'MULTIPLY',sep.outputs[0],1672),mathn(nt,'MULTIPLY',mathn(nt,'SUBTRACT',1,sep.outputs[1]),941)
arc=[(936.5+41.5*math.cos(math.pi-i*math.pi/16),449-13*math.sin(math.pi-i*math.pi/16)) for i in range(17)]
hole=arc+[(978,631),(895,631)]
def polygon_mask(nt,x,y,poly):
 mask=1.
 for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
  dx=bx-ax;dy=by-ay;a=mathn(nt,'MULTIPLY',x,-dy);b=mathn(nt,'MULTIPLY',y,dx);z=mathn(nt,'ADD',mathn(nt,'ADD',a,b),dy*ax-dx*ay);edge=mathn(nt,'GREATER_THAN',z,-.15*math.hypot(dx,dy));mask=mathn(nt,'MULTIPLY',mask,edge)
 return mask
boundary=[(0,1375),(300,1375),(314,1400),(368,1408),(400,1420),(440,1425),(470,1415),(530,1416),(570,1408),(630,1412),(690,1400),(750,1415),(941,1415)]
def right_mask(nt,x,y):
 b=1375.
 for (y0,x0),(y1,x1) in zip(boundary,boundary[1:]):
  if x1==x0:continue
  n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.inputs['From Min'].default_value=y0;n.inputs['From Max'].default_value=y1;n.inputs['To Min'].default_value=0;n.inputs['To Max'].default_value=x1-x0;nt.links.new(y,n.inputs[0]);b=mathn(nt,'ADD',b,n.outputs[0])
 return mathn(nt,'GREATER_THAN',mathn(nt,'SUBTRACT',x,b),0)
def shader_mask(m,which):
 nt=m.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');old=out.inputs['Surface'].links[0].from_socket;x,y=pixel_nodes(nt);rm=right_mask(nt,x,y)
 mask=mathn(nt,'MAXIMUM',rm,polygon_mask(nt,x,y,hole)) if which=='front' else mathn(nt,'SUBTRACT',1,rm)
 tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mask,mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(tr.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);return m
front=original_mat.copy();front.name='v049 | school front | physical aperture and rear foliage split';shader_mask(front,'front');school.data.materials[0]=front
# Reproject only the separated rear card to preserve its registration at frame1225.
S.frame_set(reference);bpy.context.view_layer.update();cam=S.camera;backVerts=[]
for v in school.data.vertices:
 p=school.matrix_world@v.co;d0=p.y-cam.matrix_world.translation.y;d1=d0+.65;ray=p-cam.matrix_world.translation;backVerts.append(cam.matrix_world.translation+ray*(d1/d0))
me=school.data.copy();me.name='v049 right foliage | projected source mesh'
for v,p in zip(me.vertices,backVerts):v.co=p
back=bpy.data.objects.new('v049 | right-side original foliage | rear depth layer',me);C.objects.link(back);rear=original_mat.copy();rear.name='v049 | source foliage only |65cm behind front';shader_mask(rear,'rear');me.materials.clear();me.materials.append(rear);back['world_fixed']=True;created.append(back.name)
registration_error=max((Vector((world_to_camera_view(S,cam,school.matrix_world@a.co).x,world_to_camera_view(S,cam,school.matrix_world@a.co).y))-Vector((world_to_camera_view(S,cam,b.co).x,world_to_camera_view(S,cam,b.co).y))).length*3840 for a,b in zip(school.data.vertices,me.vertices));assert registration_error<.005
# Native reveal: existing front opening to a genuinely recessed, inset back opening.
n=len(hole);inner=[(936.5+(x-936.5)*.94,537+(y-537)*.97) for x,y in hole];pix=hole+inner;faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];reveal=make('window masonry reveal |35cm recess',pix,[9.995]*n+[10.35]*n,faces,[stoneShadow,stone],[0 if i<17 or i==n-1 else 1 for i in range(n)])
make('window deep room backing',inner,10.62,[tuple(range(n))],[room])
# Thick arch sash; the geometry is confined to its source-painted frame.
outer=[(936.5+(x-936.5)*1.13,537+(y-537)*1.025) for x,y in hole];pix=outer+hole+outer+hole;ys=[9.91]*(2*n)+[10.025]*(2*n);faces=[];inds=[]
for i in range(n):
 j=(i+1)%n;faces.extend([(i,j,j+n,i+n),(i+n,j+n,j+3*n,i+3*n),(i,j,j+2*n,i+2*n)]);inds.extend([0,1,1])
make('arch sash front and wood returns',pix,ys,faces,[frontPaint,woodSide],inds)
def extrude(name,poly,front_y,back_y,frontmat,sidemat):
 n=len(poly);pix=poly+poly;faces=[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return make(name,pix,[front_y]*n+[back_y]*n,faces,[frontmat,sidemat],[0,1]+[1]*n)
for i,(a,b,wi) in enumerate([((936.5,439),(936.5,631),6.4),((895,486.5),(978,486.5),6.0),((895,551),(978,551),5.0),((895,597),(978,597),4.0),((921.4,438),(921.4,482),2.1),((951.3,439),(951.3,482),2.1)]):
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length*wi/2;ny=dx/length*wi/2;poly=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)];extrude('thick timber mullion '+str(i),poly,9.895,10.04,frontPaint,woodSide)
shards=json.loads((O/'original_glass_geometry.json').read_text())['polygons']
for i,poly in enumerate(shards):extrude('registered glass fragment '+str(i),poly,9.975,9.986,frontPaint,glassEdge)
# Original-painted stone fronts with actual proud edges and return geometry.
for side,x0,x1 in [('left',865,881),('right',984,1001)]:
 for k in range(7):
  y0=449+k*26;y1=min(633,y0+25.2);j=random.uniform(-.6,.6);poly=[(x0+j,y0+.3),(x1-.3,y0),(x1-.1,y1),(x0-.4,y1+.3)];extrude(side+' source-painted jamb block '+str(k),poly,9.96-random.uniform(0,.006),10.08,frontPaint,stoneShadow)
for i in range(9):
 a=math.pi-i*math.pi/9-.008;b=math.pi-(i+1)*math.pi/9+.008
 poly=[(932.5+67*math.cos(a),450-29*math.sin(a)),(932.5+67*math.cos(b),450-29*math.sin(b)),(932.5+53*math.cos(b),450-15*math.sin(b)),(932.5+53*math.cos(a),450-15*math.sin(a))];extrude('source-painted arch voussoir '+str(i),poly,9.95-random.uniform(0,.006),10.07,frontPaint,stone)
extrude('deep stone sill',[(862,634),(1004,634),(1006,644),(862,646)],9.89,10.18,frontPaint,stoneShadow)
# Irregular outer broken-wall returns, coherent with the split rear foliage.
edge=[(x,y) for y,x in boundary if 300<=y<=750];n=len(edge);pix=edge+edge;ys=[9.997]*n+[10.43]*n;faces=[(i,i+1,i+1+n,i+n) for i in range(n-1)];make('ruined wall broken outer cross-section |43cm',pix,ys,faces,[stoneShadow,stone,chalk],[i%3 for i in range(n-1)])
# Chipped cap facets are attached to the return, not loose drafting lines.
for k in range(8):
 x,y=edge[min(k,len(edge)-1)];extrude('attached wall fracture flake '+str(k),[(x-3,y),(x+1,y-2),(x+3,y+4),(x-2,y+6)],9.991,10.03,frontPaint,stoneShadow)
# Three small painted rubble solids share the school footing, behind the path.
for i,(x,y,w,h) in enumerate([(1265,730,14,10),(1340,733,18,11),(1401,729,12,10)]):
 poly=[(x-w,y),(x-w*.7,y-h*.65),(x+w*.4,y-h),(x+w,y-h*.3),(x+w*.8,y)];extrude('grounded rubble block '+str(i),poly,9.80,10.11,frontPaint,stoneShadow)
light=bpy.data.lights.new('v049 | broad overcast key for native returns','AREA');light.energy=900;light.shape='DISK';light.size=8;lo=bpy.data.objects.new('v049 | stationary overcast opening key',light);C.objects.link(lo);lo.location=(64,-1,9);lo.rotation_euler=(P(935,540)-lo.location).to_track_quat('-Z','Y').to_euler();created.append(lo.name)
# Keep spatial masks fixed, but fit their whole support into valid source pixels.
# EXTEND previously repeated the last image column outside0..1 at adjacent views.
fixed=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for t in list(m.node_tree.nodes):
  if t.type!='TEX_IMAGE' or not t.image or t.image.name!='Foreground_Bank_Paintover_v047.png' or not t.inputs[0].is_linked:continue
  nt=m.node_tree;old=t.inputs[0].links[0].from_socket;sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(old,sep.inputs[0]);x=nt.nodes.new('ShaderNodeMath');x.operation='MULTIPLY_ADD';x.inputs[1].default_value=.99/1.48;x.inputs[2].default_value=.005+.24*.99/1.48;nt.links.new(sep.outputs[0],x.inputs[0]);vec=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(x.outputs[0],vec.inputs[0]);nt.links.new(sep.outputs[1],vec.inputs[1]);nt.links.new(sep.outputs[2],vec.inputs[2]);nt.links.new(vec.outputs[0],t.inputs[0]);fixed.append({'material':m.name,'node':t.name})

assert all(not o.animation_data for o in C.objects)
S.name='WTSC_REGISTERED_SCHOOL_DEPTH_v049c_OPEN_DIAGNOSTIC';S['v049_scope']='Registered school aperture, actual recessed reveals, source-painted stone fronts, wood/glass thickness and rear foliage parallax. Original v048d children/color/title/actions retained. No color-test variant integrated.';S.render.resolution_percentage=100;S.eevee.taa_render_samples=32;S.frame_set(reference);bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'after_preview_c').mkdir(exist_ok=True);S.render.resolution_percentage=25;S.eevee.taa_render_samples=16
for f in [1201,1225,1249]:
 S.frame_set(f);S.render.filepath=str(O/'after_preview_c'/f'After_{f}_960.png');bpy.ops.render.render(write_still=True,scene=S.name);print('ARCHITECTURE_PREVIEW',f,flush=True)
report={'native':str(OUT),'native_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'reference_frame':reference,'adjacent_frames':[1201,1249],'source_image':'School_v001.png','source_dimensions':[1672,941],'front_card_affine':{'x_center':65,'width':22,'z_center':3.29222369194,'height':12.3815793991,'front_y':10},'window_hole_pixel_polygon':hole,'window_recess_m':.35,'room_back_m':.62,'ruin_return_depth_m':.43,'rear_foliage_depth_m':.65,'rear_registration_error_4K_pixels':registration_error,'glass_contours_from_source':len(shards),'bank_valid_sample_remaps':fixed,'created_objects':len(created),'all_new_world_fixed_without_actions':True,'new_color_progression_applied':False,'glass_boundary_method':'Source-painted surviving fragments traced to native extruded polygons; no generated texture or upscale claimed.','status':'TECHNICAL PREVIEW; visual acceptance pending','limitations':['Front plaster/stone painting remains original sub4K source; registered source-painted glass/wood with physical edges supply resolution-independent boundary detail, not a newly painted full4K facade.','One selected broken window and right wall/foliage separation only.','Static broad key lights only new diffuse geometry; inherited FX and child materials unchanged.']};(O/'ARCHITECTURE_BUILD_v049c.json').write_text(json.dumps(report,indent=2));print('REGISTERED_SCHOOL_BUILT',len(created),registration_error,flush=True)
