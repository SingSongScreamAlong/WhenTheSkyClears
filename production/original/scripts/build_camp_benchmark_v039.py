"""Bounded camp look/grounding study. No v001 FX pack imports. No render by default."""
import bpy,json,math,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');out=R/'shots/world/WTSC_Camp_Light_Ground_Benchmark_v039.blend';assert not out.exists()
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v038'];bpy.context.window.scene=w;w.frame_set(1609)
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');fire=w.objects['v036 | Camp hearth | fixed emitter'];light=next(o for o in w.objects if o.parent==fire and o.type=='LIGHT')
fire['receiver_radius']=2.8;fire['receiver_strength']=.075;fire['character_response']=.10;fire['light_power']=420.;fire['flame_power']=1.8;fire['fire_beat']=.8
beat='(.82+.12*sin(frame*.77+2.13)+.065*sin(frame*1.93+3.13)+.045*sin(frame*.313+4.13))'
fire.driver_add('["fire_beat"]').driver.expression=beat
def driven(owner,path,expr,props,index=None):
 f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED';f.driver.expression=expr
 for name,prop in props:
  v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=fire;v.targets[0].data_path='["'+prop+'"]'
 return f
light.data.driver_remove('energy');driven(light.data,'energy','P*F',[('P','light_power'),('F','fire_beat')])
def mathn(nt,op,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,(int,float)):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs[0]
def mapr(nt,src,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP';n.inputs['From Min'].default_value=a;n.inputs['From Max'].default_value=b;n.inputs['To Min'].default_value=c;n.inputs['To Max'].default_value=d;nt.links.new(src,n.inputs[0]);return n.outputs[0]
def mix(nt,a,b,f,mode='MIX',name='v039 paint response'):
 n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type=mode;n.name=name
 for socket,x in [(n.inputs[6],a),(n.inputs[7],b),(n.inputs[0],f)]:
  if isinstance(x,(int,float,tuple)):socket.default_value=x
  else:nt.links.new(x,socket)
 return n.outputs[2]
def vecop(nt,op,a,b=None):
 n=nt.nodes.new('ShaderNodeVectorMath');n.operation=op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,tuple):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs['Value'] if op in ['LENGTH','DOT_PRODUCT','DISTANCE'] else n.outputs['Vector']
def scalar_control(nt,name,prop):
 n=nt.nodes.new('ShaderNodeValue');n.name=name;driven(n.outputs[0],'default_value','v',[('v',prop)]);return n.outputs[0]
def light_vector(nt,position):
 n=nt.nodes.new('ShaderNodeCombineXYZ');n.name='v039 actual firelight world position'
 for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
  f=n.inputs[i].driver_add('default_value');f.driver.expression='p';v=f.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=light;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
 delta=vecop(nt,'SUBTRACT',n.outputs[0],position);return vecop(nt,'NORMALIZE',delta),vecop(nt,'LENGTH',delta),delta
def strip_old_wash(nt,em):
 src=em.inputs[0].links[0].from_socket;removed=[]
 while src.node.bl_idname=='ShaderNodeMix' and src.node.blend_type=='ADD' and tuple(round(v,3) for v in src.node.inputs[7].default_value[:3])==(.8,.2,.025):
  n=src.node;removed.append(n.name);src=n.inputs[6].links[0].from_socket
 return src,removed
def receive(nt,base,normal=None):
 geo=nt.nodes.new('ShaderNodeNewGeometry');direction,distance,delta=light_vector(nt,geo.outputs['Position']);radius=scalar_control(nt,'v039 local receiver radius','receiver_radius');fall=nt.nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.interpolation_type='SMOOTHERSTEP';fall.inputs['From Min'].default_value=.15;fall.inputs['To Min'].default_value=1;fall.inputs['To Max'].default_value=0;nt.links.new(radius,fall.inputs['From Max']);nt.links.new(distance,fall.inputs[0]);weight=mathn(nt,'MULTIPLY',fall.outputs[0],fall.outputs[0])
 if normal is not None:
  lambert=mathn(nt,'MAXIMUM',vecop(nt,'DOT_PRODUCT',normal,direction),.08);weight=mathn(nt,'MULTIPLY',weight,lambert)
 luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,luma.inputs[0]);ink=mapr(nt,luma.outputs[0],.012,.20,.18,1);weight=mathn(nt,'MULTIPLY',weight,ink)
 fac=mathn(nt,'MULTIPLY',scalar_control(nt,'v039 receiver strength','receiver_strength'),scalar_control(nt,'v039 coherent fire beat','fire_beat'));fac=mathn(nt,'MULTIPLY',fac,weight)
 return mix(nt,base,(1,.34,.075,1),fac,'ADD','v039 restrained local firelight | preserved ink')
camp=w.objects['v016 | Camp | pinned canvas and ropes'];mat=camp.data.materials[0].copy();mat.name='v039 | Camp paint | shaped cool key and localized warm source';camp.data.materials[0]=mat;nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base,removed=strip_old_wash(nt,em)
tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');geo=nt.nodes.new('ShaderNodeNewGeometry');bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.035;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(geo.outputs['Normal'],bump.inputs['Normal'])
key=vecop(nt,'NORMALIZE',(.35,-.70,.72));lambert=mathn(nt,'MAXIMUM',vecop(nt,'DOT_PRODUCT',bump.outputs['Normal'],key),0)
tonal=mix(nt,(.79,.84,.93,1),(1.05,1.055,1.065,1),lambert,name='v039 coherent cool key / sky fill');base=mix(nt,base,tonal,1,'MULTIPLY','v039 original painted fabric form retained');nt.links.new(receive(nt,base,bump.outputs['Normal']),em.inputs[0])
# Reduce repeated strip cues with stable, small world-space paint variation.
ground_changes=[]
for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
 ob=w.objects[name];mat=ob.data.materials[0].copy();mat.name='v039 | '+name.split(' | ')[1]+' | stable paint variation';ob.data.materials[0]=mat;nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base,_=strip_old_wash(nt,em);geo=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.42;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
 affected=[]
 for t in list(nt.nodes):
  if t.type!='TEX_IMAGE' or not t.image or not any(k in t.image.name for k in ['Path_Detail','Foreground_Ground']):continue
  if not t.inputs[0].is_linked:continue
  old=t.inputs[0].links[0].from_socket;sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(old,sep.inputs[0]);offset=mathn(nt,'MULTIPLY',mathn(nt,'SUBTRACT',noise.outputs['Fac'],.5),.16);u=mathn(nt,'PINGPONG',mathn(nt,'ADD',sep.outputs['X'],offset),1);comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(u,comb.inputs[0]);nt.links.new(sep.outputs['Y'],comb.inputs[1]);nt.links.new(comb.outputs[0],t.inputs[0]);affected.append(t.image.name)
 dim=mapr(nt,noise.outputs['Fac'],.2,.8,.82,1.02);base=mix(nt,base,(.86,.89,.92,1),.22,'MULTIPLY','v039 restrained foreground value');nt.links.new(receive(nt,base),em.inputs[0]);ground_changes.append({'object':name,'stable_uv_variation_images':affected})
# Keep exactly the established drawing/topology/root/pose; add only receiving paint.
fill=next(o for o in w.objects if o.parent==pair and 'Near-black painted fill' in o.name);mat=fill.data.materials[0].copy();mat.name='v039 | Charcoal pair | restrained source-connected rim';fill.data.materials[0]=mat;nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.interpolation='Cubic';uv=nt.nodes.new('ShaderNodeTexCoord');alpha=tex.outputs['Alpha']
def edge(dx,dy):
 add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(dx,dy,0);nt.links.new(uv.outputs['UV'],add.inputs[0]);t=nt.nodes.new('ShaderNodeTexImage');t.image=tex.image;t.extension='CLIP';t.interpolation='Cubic';nt.links.new(add.outputs[0],t.inputs[0]);return mathn(nt,'MAXIMUM',mathn(nt,'SUBTRACT',alpha,t.outputs['Alpha']),0)
left=edge(-2/1672,0);right=edge(2/1672,0);top=edge(0,2/941);geo=nt.nodes.new('ShaderNodeNewGeometry');direction,distance,delta=light_vector(nt,geo.outputs['Position']);sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(delta,sep.inputs[0]);fromleft=mathn(nt,'LESS_THAN',sep.outputs['X'],0);side=mathn(nt,'ADD',mathn(nt,'MULTIPLY',left,fromleft),mathn(nt,'MULTIPLY',right,mathn(nt,'SUBTRACT',1,fromleft)))
inv=mathn(nt,'DIVIDE',1,mathn(nt,'ADD',1,mathn(nt,'POWER',mathn(nt,'DIVIDE',distance,4),2)));reach=mapr(nt,distance,7,14,1,0);warm=mathn(nt,'MULTIPLY',mathn(nt,'MULTIPLY',inv,reach),scalar_control(nt,'v039 actor response','character_response'));warm=mathn(nt,'MULTIPLY',warm,scalar_control(nt,'v039 source-connected actor beat','fire_beat'));warm=mathn(nt,'MULTIPLY',warm,mathn(nt,'ADD',mathn(nt,'MULTIPLY',side,.7),mathn(nt,'MULTIPLY',top,.12)))
luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,luma.inputs[0]);preserve_eyes=mapr(nt,luma.outputs[0],.16,.65,1,0);warm=mathn(nt,'MULTIPLY',warm,preserve_eyes);color=mix(nt,base,(.9,.31,.065,1),warm,'ADD','v039 subtle warm rim | dark read retained');cool=mathn(nt,'MULTIPLY',mathn(nt,'MULTIPLY',top,.0055),preserve_eyes);color=mix(nt,color,(.42,.57,.74,1),cool,'ADD','v039 soft sky edge on existing paint');nt.links.new(color,em.inputs[0])
# Existing contacts were extremely narrow. Add a soft occlusion core/penumbra,
# behind each measured sole; no pose/topology or rig transforms are edited.
for ob in w.objects:
 if 'Ground contact |' in ob.name:ob.hide_render=True
contact_col=bpy.data.collections.new('v039 | Measured shoe contact and occlusion');w.collection.children.link(contact_col)
def contactmat(name,opacity):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear();uv=nt.nodes.new('ShaderNodeTexCoord');d=nt.nodes.new('ShaderNodeVectorMath');d.operation='DISTANCE';d.inputs[1].default_value=(.5,.5,0);nt.links.new(uv.outputs['UV'],d.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.clamp=True;r.interpolation_type='SMOOTHERSTEP';r.inputs['From Min'].default_value=.08;r.inputs['From Max'].default_value=.5;r.inputs['To Min'].default_value=opacity;r.inputs['To Max'].default_value=0;nt.links.new(d.outputs['Value'],r.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=31;noise.inputs['Detail'].default_value=2;nt.links.new(uv.outputs['UV'],noise.inputs[0]);grain=mathn(nt,'ADD',mathn(nt,'MULTIPLY',noise.outputs['Fac'],.16),.84);a=mathn(nt,'MULTIPLY',r.outputs[0],grain);em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.015,.012,.009,1);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mixn=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a,mixn.inputs[0]);nt.links.new(tr.outputs[0],mixn.inputs[1]);nt.links.new(em.outputs[0],mixn.inputs[2]);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mixn.outputs[0],o.inputs[0]);return m
core=contactmat('v039 | Shoe contact core',.57);soft=contactmat('v039 | Shoe soft occlusion penumbra',.21);soles=json.loads((R/'characters/Pair_Painterly_Near_Age_Vector_v015.json').read_text())['soles'];contact=[]
for i,p in enumerate(soles):
 for label,mat,factor,h in [('core',core,1.08,.021),('penumbra',soft,1.55,.065)]:
  width=p['width']*factor;d=bpy.data.meshes.new(f'v039 shoe{i} {label}');d.from_pydata([(-width/2,0,-h/2),(width/2,0,-h/2),(width/2,0,h/2),(-width/2,0,h/2)],[],[(0,1,2,3)]);d.materials.append(mat);uv=d.uv_layers.new(name='soft contact UV')
  for l,xy in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=xy
  ob=bpy.data.objects.new(d.name,d);contact_col.objects.link(ob);ob.parent=pair;ob.location=(p['x']+(.01 if label=='penumbra' else 0),-.33,p['z']-.007);contact.append({'shoe':i,'kind':label,'width':width,'location_relative_to_pair':list(ob.location)})
# Tone existing production flame edges and keep smoke resets invisible. No FXv001.
for ob in w.objects:
 if ob.parent==fire and 'painted flame' in ob.name:
  for mat in ob.data.materials:
   nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');em.inputs[1].driver_remove('default_value');driven(em.inputs[1],'default_value','P*F',[('P','flame_power'),('F','fire_beat')]);tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');tex.interpolation='Cubic'
   mult=next(n for n in nt.nodes if n.bl_idname=='ShaderNodeMix' and n.blend_type=='MULTIPLY');mult.inputs[7].default_value=(.88,.78,.66,1)
 if ob.parent==fire and 'rooted smoke' in ob.name:
  nt=ob.data.materials[0].node_tree
  for f in nt.animation_data.drivers if nt.animation_data else []:
   if 'sin(pi*' in f.driver.expression:
    expr=f.driver.expression;start=expr.index('sin(pi*');f.driver.expression='.11*'+expr[start:];f.driver.expression=f.driver.expression.replace('**2)', '**2',1)
glare=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare');glare.inputs['Strength'].default_value=.16;glare.inputs['Size'].default_value=.12
w.name='WTSC_WORLD_CORRECTED_v039';e.name='WTSC_FULL_FILM_KNOCKOUT_v039';m.name='WTSC_MASTER_4K_106S_v039';m.render.filepath='//../../renders/world_v016/WTSC_Study_Full_Film_Native_v039.mp4'
for s in [w,e,m]:s.use_preview_range=True;s.frame_preview_start=1537;s.frame_preview_end=1656
report={'source':str(out),'matched_baseline':'v037 immutable native world','benchmark_seconds':[64,69],'benchmark_frames':[1537,1656],'benchmark_frame_count':120,'production_render_preserved':True,'v001_effects_pack_used':False,'external_effects_imported':False,'unchanged':'Held GP drawing, fill topology, root/pose/spacing, camera/route, static architecture visibility, full-film typography and exact106s credits/audio','changes':{'camp_broad_additive_wash_bypassed':removed,'fire_radius_metres':2.8,'receiver_strength':.075,'physical_firelight_watts':420,'source_connected_fire_beat':beat,'canvas_form':'Preserved original texture; modest bump-derived directional cool key/sky fill and bounded warm Lambert response','actor_rim':'Subtle source-connected warm contour and cool top edge, eye/ink preservation; no new character artwork','shoe_contacts':contact,'ground_repetition_variation':ground_changes,'flame':'Existing production asset, cooler muted outer paint and coherent beat; no v001 art','smoke':'Existing production wisps only; reset opacity goes tozero; no v001 art'},'resource_plan':'Scene edits/CPU readback and at most tiny low-cost stills while037runs. Substantive120frame4Kworld benchmark rendering waits for037production tocomplete.','comparison_plan':'Same64–69range unmasked andknockout against matched037baseline, native4Ksources; comparison deliveredFIRST, then propagate appropriate changes and full106s updatedfilm afterQA.','artistic_scope':'2.5D paint relighting/contact study; no Arcane-level approval inferred.'}
note=bpy.data.texts.new('CURRENT v039 | Five-second camp visual benchmark');note.write(json.dumps(report,indent=2));bpy.context.window.scene=w;w.frame_set(1609);e.frame_set(1609);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(R/'notes/world_v016/camp_benchmark_build_v039.json').write_text(json.dumps(report,indent=2));print('CAMP_BENCHMARK_PREPARED',str(out),flush=True)
