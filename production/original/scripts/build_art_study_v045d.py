"""Art-only native material study; exact v044 performance/stage/EEVEE/FX preserved."""
import bpy,json,hashlib,struct,math
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');p=Path(bpy.data.filepath);out=R/'shots/world/WTSC_Open_Battlefield_Art_Study_v045d.blend';assert not out.exists()
prior=json.loads((R/'notes/world_v016/integration_checkpoint_v044.json').read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()==prior['source']['sha256']
preserved={prior[k]['path']:prior[k]['sha256'] for k in ['source','master','view','matched_comparison']};preserved.update({str(R/k):v for k,v in prior['preserved_inputs'].items()})
failed=R/'shots/world/WTSC_Open_Battlefield_Art_Study_v045.blend';assert hashlib.sha256(failed.read_bytes()).hexdigest()=='cbc66bea6d14d2baaea7ffe73488e5db233964593964a5014335c322ac93288b'
preserved[str(failed)]='cbc66bea6d14d2baaea7ffe73488e5db233964593964a5014335c322ac93288b'
for image in (R/'renders/world_v016/art_v045').glob('Art_v045_*_4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()
for version,sha in [('v045a','7dc52ab80047ab3b7d7ae3f8ca61414b4763a04ecf6784b23afb34219b2630fa'),('v045b','b1de051977efd68c7871de638df55f9dd7505dc1c04bdc8124a79ee6ba430f64'),('v045c','5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4')]:
 failed_copy=R/f'shots/world/WTSC_Open_Battlefield_Art_Study_{version}.blend';assert hashlib.sha256(failed_copy.read_bytes()).hexdigest()==sha;preserved[str(failed_copy)]=sha
 for image in (R/f'renders/world_v016/art_{version}').glob('*4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()
for name,sha in preserved.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name
s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_DRAWN_TRIAL_v044'];m=bpy.data.scenes['WTSC_OPEN_5S_MASTER_v044'];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v006_drawn_pose_corrections');fx=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];travel=next(o for o in root.children if 'TRAVEL' in o.name)
protected=set([root,*root.children_recursive,fx,*fx.children_recursive,s.camera,*[o for o in s.objects if o.type=='LIGHT'],*[o for o in s.objects if o.name.startswith('v041 sole contact |')]])
def stable(value):
 if isinstance(value,(str,int,float,bool)) or value is None:return value
 try:return list(value)
 except:return str(value)
def props(obj):
 result={}
 for item in obj.bl_rna.properties:
  if item.identifier=='rna_type' or item.type in {'POINTER','COLLECTION'}:continue
  try:result[item.identifier]=stable(getattr(obj,item.identifier))
  except:pass
 return result
def render_settings():return {'render':props(s.render),'eevee':props(s.eevee),'view':props(s.view_settings),'camera':props(s.camera.data),'world':s.world.name}
def curves(action):return [f for l in action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]
def action_data(id):
 a=getattr(id,'animation_data',None)
 if not a:return None
 actions=set(([a.action] if a.action else [])+[st.action for t in a.nla_tracks for st in t.strips if st.action])
 return {'actions':{ac.name:[[f.data_path,f.array_index,[[*k.co,k.interpolation] for k in f.keyframe_points]] for f in curves(ac)] for ac in actions},'nla':[[t.name,t.mute,[[st.name,st.action.name if st.action else None,st.frame_start,st.frame_end,st.scale,st.extrapolation] for st in t.strips]] for t in a.nla_tracks],'drivers':[[f.data_path,f.array_index,f.driver.expression,[[v.name,v.type,[[t.id.name if t.id else None,t.data_path,t.transform_type,t.transform_space] for t in v.targets]] for v in f.driver.variables]] for f in a.drivers]}
def protected_fingerprint():
 s.frame_set(1801);bpy.context.view_layer.update();h=hashlib.sha256();actions={};materials=set();meshes={}
 for o in sorted(protected,key=lambda o:o.name):
  actions[o.name]={'type':o.type,'matrix':[list(r) for r in o.matrix_world],'hide_render':o.hide_render,'animation':action_data(o),'data':o.data.name if o.data else None,'materials':[ma.name if ma else None for ma in o.data.materials] if hasattr(o.data,'materials') else None}
  if o.type=='MESH':
   h.update(o.name.encode());h.update(b''.join(struct.pack('fff',*v.co) for v in o.data.vertices))
   if o.data.shape_keys:
    keys=o.data.shape_keys;actions[keys.name]=action_data(keys)
    for key in keys.key_blocks:h.update(key.name.encode());h.update(b''.join(struct.pack('fff',*v.co) for v in key.data))
  if hasattr(o.data,'materials'):materials.update(ma for ma in o.data.materials if ma and ma.node_tree)
 for mat in sorted(materials,key=lambda ma:ma.name):
  nt=mat.node_tree;actions['material '+mat.name]={'animation':action_data(nt),'nodes':[[n.name,n.bl_idname,[(i.identifier,stable(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],getattr(n,'operation',None)] for n in nt.nodes],'links':[[l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier] for l in nt.links]}
 h.update(json.dumps(actions,sort_keys=True).encode());return h.hexdigest()
settings=render_settings();assert s.render.engine=='BLENDER_EEVEE';protected_before=protected_fingerprint();baseline=[]
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();baseline.append({'frame':f,'camera':[list(r) for r in s.camera.matrix_world],'travel':list(travel.matrix_world.translation),'root':[list(r) for r in root.matrix_world],'fx':[list(r) for r in fx.matrix_world],'age':fx['age'],'hot':fx['hot_envelope'],'watts':light.data.energy})
def mathn(nt,op,a,b=None,name=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.name=name or 'v045d | '+op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,(int,float)):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs[0]
def remap(nt,x,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.name='v045d | Static broad spacing transition';n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
 for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
 nt.links.new(x,n.inputs[0]);return n.outputs[0]
def mix(nt,a,b,f,name):
 n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type='MIX';n.name=name
 for socket,x in [(n.inputs[6],a),(n.inputs[7],b),(n.inputs[0],f)]:
  if isinstance(x,(int,float,tuple)):socket.default_value=x
  else:nt.links.new(x,socket)
 return n.outputs[2]
changed=[]
def own_material(object_name):
 ob=s.objects[object_name];old=ob.data.materials[0];new=old.copy();new.name='v045d ART ONLY | '+object_name;ob.data.materials[0]=new;changed.append({'object':ob.name,'original_material':old.name,'art_material':new.name});return ob,new.node_tree
# Whole painted masses enter the same cooler atmospheric value family. The
# actual fixed eruption response remains downstream, with original source/clock.
for name,strength,fog in [('v016 | Battlefield | broken village line',.30,(.22,.25,.275,1)),('v026 | Countryside panorama | stationary at true depth',.12,(.34,.38,.41,1))]:
 ob,nt=own_material(name);em=next(n for n in nt.nodes if n.type=='EMISSION');receiver=next((n for n in nt.nodes if n.name=='v041 DORMANT | source-bound local warmth'),None);target=receiver.inputs[6] if receiver else em.inputs[0];base=target.links[0].from_socket
 # Contrast compression on the entire card, independent of characters/camera/time.
 if 'Battlefield' in name:
  geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
  # Static ash-street atmosphere over a broad existing geographic corridor.
  # Darker side framing retained; no actor/camera/animated input or outline.
  left=remap(nt,xyz.outputs['X'],101.5,104.,0,1);right=remap(nt,xyz.outputs['X'],109.,112.,1,0)
  corridor=mathn(nt,'MULTIPLY',left,right);strength_input=mathn(nt,'ADD',.075,mathn(nt,'MULTIPLY',corridor,.225))
 else:strength_input=strength
 graded=mix(nt,base,fog,strength_input,'v045d | Restrained static ash-street depth with darker side masses');nt.links.new(graded,target)
 changed[-1].update({'fog_mix':strength,'fog_linear_color':fog,'alpha_changed':False,'character_following_inputs':False,'local_fire_receiver_stays_downstream':bool(receiver)})
# One tight organic retouch of one repeated clump; rest of v044path untouched.
path,nt=own_material('v020 | Walking path | continuous blended paint');tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and 'Path_Detail' in n.image.name);destinations=[l.to_socket for l in tex.outputs['Color'].links]
uv=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tex.inputs[0].links[0].from_socket,uv.inputs[0]);geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
coords=nt.nodes.new('ShaderNodeCombineXYZ');coords.name='v045d | Adjacent source soil - same V and texel density';nt.links.new(mathn(nt,'PINGPONG',mathn(nt,'ADD',uv.outputs['X'],.64),1),coords.inputs[0]);nt.links.new(uv.outputs['Y'],coords.inputs[1])
sample=nt.nodes.new('ShaderNodeTexImage');sample.name='v045d | Same packed painting, adjacent soil at SAME depth';sample.image=tex.image;sample.extension='REPEAT';sample.interpolation=tex.interpolation;nt.links.new(coords.outputs[0],sample.inputs[0])
dx=mathn(nt,'DIVIDE',mathn(nt,'SUBTRACT',xyz.outputs['X'],107.35),.25);dz=mathn(nt,'DIVIDE',mathn(nt,'SUBTRACT',xyz.outputs['Z'],.35),.16);radius=mathn(nt,'SQRT',mathn(nt,'ADD',mathn(nt,'MULTIPLY',dx,dx),mathn(nt,'MULTIPLY',dz,dz)))
noise=nt.nodes.new('ShaderNodeTexNoise');noise.name='v045d | Small irregular static retouch boundary';noise.inputs['Scale'].default_value=12.;noise.inputs['Detail'].default_value=2.;nt.links.new(geo.outputs['Position'],noise.inputs[0]);radius=mathn(nt,'ADD',radius,mathn(nt,'MULTIPLY',mathn(nt,'SUBTRACT',noise.outputs['Fac'],.5),.18));patch=remap(nt,radius,.55,1,1,0)
bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],bw.inputs[0]);dark=remap(nt,bw.outputs[0],.015,.20,1,0);weight=mathn(nt,'MULTIPLY',patch,dark);color=mix(nt,tex.outputs['Color'],sample.outputs['Color'],weight,'v045d | One irregular dark-leaf retouch only')
for socket in destinations:nt.links.new(color,socket)
changed[-1].update({'method':'One tight irregular world-fixed clump patch atX107.35,Z.35, radii.25/.16metres; only original dark leaf pixels receive adjacent soil from the same packed painting at SAME V, unchanged texture density. Original path/bank elsewhere retained.','patch_world_center_xz':[107.35,.35],'patch_radii_xz':[.25,.16],'source_U_offset':.64,'source_V_changed':False,'camera_character_or_time_inputs':False,'alpha_or_geometry_changed':False})
# Verify ALL protected scene/performance/FX bytes and evaluated stage channels.
protected_after=protected_fingerprint();assert protected_before==protected_after
errors={'camera':0.,'travel':0.,'root':0.,'fx':0.,'age':0.,'hot':0.,'watts':0.}
for row in baseline:
 s.frame_set(row['frame']);bpy.context.view_layer.update()
 for key,mat in [('camera',s.camera.matrix_world),('root',root.matrix_world),('fx',fx.matrix_world)]:errors[key]=max(errors[key],max(abs(mat[i][j]-row[key][i][j]) for i in range(4) for j in range(4)))
 errors['travel']=max(errors['travel'],max(abs(travel.matrix_world.translation[i]-row['travel'][i]) for i in range(3)))
 for key,value in [('age',fx['age']),('hot',fx['hot_envelope']),('watts',light.data.energy)]:errors[key]=max(errors[key],abs(value-row[key]))
assert max(errors.values())==0,errors
s.frame_set(1801);assert render_settings()==settings
s.name='WTSC_OPEN_BATTLEFIELD_ART_STUDY_v045d';m.name='WTSC_OPEN_5S_ART_MASTER_v045d';s['art_only_status']='FRAME-FIRST candidate. No movie authorized. v044 motion/camera/route/EEVEE/FX fixed.'
for scene in [s,m]:scene.render.filepath='//../../renders/world_v016/art_v045d/FRAME_FIRST_ONLY_NO_MOVIE'
report={'source':str(out),'base_source':str(p),'base_sha256':prior['source']['sha256'],'world_scene':s.name,'master_scene':m.name,'scope':'Isolated art-only frame-first candidate; no new motion/FX import, no movie render.','changed_materials':changed,'unchanged_protected_fingerprint':protected_before,'protected_ids':sorted(o.name for o in protected),'protected_definition':'All new-pair geometry, all120shape drawings, object/NLA/action/driver channels, character and FX material nodes, all FX geometry, lights, camera, sole contact geometry/actions.','evaluated_120frame_errors':errors,'unchanged_render_settings':settings,'baseline_staging':baseline,'preserved_inputs':preserved,'frame_first':[1842,1849,1856,1881,1901,1920],'new_nodes_have_no_animation_drivers':True,'source_image_pixels_unchanged':True,'layer_alpha_and_geometry_unchanged':True,'no_character_outline_or_following_halo':True,'light_direction_and_existing_local_fire_influence':'No light data/material response changed. New background color grade is upstream of the unchanged source-bound eruption receiver.','reuse':{'contract':'dcc-mcp-production-reuse/v1','guide_checked':'notes/dcc_agent_workflows.md','native_reuse':'Original packed paintings and native shader interfaces; no replacement plugin/asset needed for this controlled art comparison. Existing provider/marketplace investigation retained in notes/production_reuse_evidence.json; no new provider-call claim.','transport':'Established owned background bpy fallback; no live DCC-MCP validation claimed.','asset_rights':'Same local original GPT project paintings; no new third-party content or publication.'},'artistic_acceptance':False,'movie_render_started':False,'full_trailer_propagation':False,'rejected_predecessor':'v045dctualsource/PNGs retained: UVstrip sampling failed visualreview; broadgrade over-fogged. This separatev045d uses uniform-density underpaint and restrained world-fixed corridor grade.','foreground_status':'Single localized retouch test only. Background-onlyv045c preserved as honestfallback; foregroundcleanup incomplete until actualframe review.','first_test_gate':[1901],'pending':'One actual1901frame before any further work; then six representative frames, matched normal/grayscale/thumbnail review and painted-card continuity checks.'}
note=bpy.data.texts.new('CURRENT v045d | Art-only frame-first provenance');note.write(json.dumps(report,indent=2));bpy.context.window.scene=m;m.frame_set(1849);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['source_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
for name,sha in preserved.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name
(R/'notes/world_v016/art_study_build_v045d.json').write_text(json.dumps(report,indent=2));print('V045_ART_ONLY_NATIVE_SAVED',json.dumps({'source':str(out),'sha256':report['source_sha256'],'protected_fingerprint':protected_before,'stage_errors':errors}),flush=True)
