"""Isolated face-paint registration and static relaxed-hand model; gait read-only."""
import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];SRC=ROOT/'locomotion/connected_model_fit_v049/native/WTSC_Connected_Model_Fit_v049.blend'
H='2f78c5cd86b96d437d97a165b8b61473bcd6c9d1ab284015c229bfb11c6f9a94';assert hashlib.sha256(SRC.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V049 | MODEL FIT AND GROUPED HANDS | v048 motion'];bpy.context.window.scene=S;S.name='V050 | FACE FINISH AND RELAXED HANDS | v049 gait';bpy.data.collections['V049 | AGE10 PAIR | connected model fit'].name='V050 | AGE10 PAIR | face and hand finish'
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]).encode()).hexdigest()
protected_actions={a.name:ah(a) for a in bpy.data.actions};rigs={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};bones={w:{b.name:[tuple(b.head_local),tuple(b.tail_local)] for b in r.data.bones} for w,r in rigs.items()};art=bpy.data.collections['V044 | age10 editable profile anatomy'];C=bpy.data.collections['V046 | restored original painted wardrobe'];heads={o.name:hashlib.sha256(repr([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() for o in art.objects if o.get('proportion_role')=='head'}
gen=bpy.data.images.load(str(P/'textures/WTSC_Girl_Face_Finish_Study_v050.png'),check_existing=True);gen.pack();W,Hg=gen.size
raw=np.empty(W*Hg*4,dtype=np.float32);gen.pixels.foreach_get(raw);gp=raw.reshape(Hg,W,4)[::-1];warm=(gp[:,:,0]-gp[:,:,1]>.015)&(gp[:,:,3]>.65)&(gp[:,:,0]>.08)
pair=next(i for i in bpy.data.images if 'Pair_Painterly_Near_Age_v015' in i.name and i.size[0]==1672);raw=np.empty(1672*941*4,dtype=np.float32);pair.pixels.foreach_get(raw);op=raw.reshape(941,1672,4)[::-1]
edge_shift=[]
for py in range(194,316,2):
 gy=665+(py-229)*4.2;row=max(0,min(Hg-1,round(gy)));gx=np.flatnonzero(warm[row]);ox=np.flatnonzero(op[py,1000:1110,3]>.65)+1000
 if not len(ox):ox=np.flatnonzero(op[py,950:1110,3]>.65)+950
 if len(gx) and len(ox):edge_shift.append((py,float(gx[-1]-4.2*ox[-1])))
assert len(edge_shift)>45
raw_edge_shift=list(edge_shift)
# The original jaw becomes a neck one source row before the generated jaw.
# Reject isolated alpha-edge correspondence outliers rather than introducing
# a UV jump/black stripe across the neck. Genuine broad profile changes remain.
edge_shift=[(py,float(np.median([v for _,v in raw_edge_shift[max(0,i-3):i+4]])) if abs(value-float(np.median([v for _,v in raw_edge_shift[max(0,i-3):i+4]])))>25 else value) for i,(py,value) in enumerate(raw_edge_shift)]
girlhead=next(o for o in art.objects if o.parent==rigs['GIRL'] and o.get('proportion_role')=='head');oldmat=girlhead.data.materials[0];m=oldmat.copy();m.name='V050 GIRL | registered face paint, original hair braid and alpha';girlhead.data.materials[0]=m;ns=m.node_tree.nodes;lk=m.node_tree.links
def mn(op,a,b=None):
 n=ns.new('ShaderNodeMath');n.operation=op
 for value,i in [(a,0),(b,1)]:
  if value is None:continue
  if isinstance(value,(int,float)):n.inputs[i].default_value=value
  else:lk.new(value,n.inputs[i])
 return n.outputs[0]
def clamp(a):return mn('MINIMUM',1,mn('MAXIMUM',0,a))
def curve(x,keys):
 value=keys[0][1]
 for (a,b),(c,d) in zip(keys,keys[1:]):value=mn('ADD',value,mn('MULTIPLY',d-b,clamp(mn('DIVIDE',mn('SUBTRACT',x,a),c-a))))
 return value
uv=ns.new('ShaderNodeUVMap');uv.uv_map=girlhead.data.uv_layers[0].name;sep=ns.new('ShaderNodeSeparateXYZ');lk.new(uv.outputs[0],sep.inputs[0]);px=mn('MULTIPLY',sep.outputs['X'],1672);py=mn('MULTIPLY',mn('SUBTRACT',1,sep.outputs['Y']),941)
gx=mn('ADD',mn('MULTIPLY',px,4.2),curve(py,edge_shift));gy=mn('ADD',665,mn('MULTIPLY',mn('SUBTRACT',py,229),4.2));v=ns.new('ShaderNodeCombineXYZ');lk.new(mn('DIVIDE',gx,W),v.inputs['X']);lk.new(mn('SUBTRACT',1,mn('DIVIDE',gy,Hg)),v.inputs['Y']);tx=ns.new('ShaderNodeTexImage');tx.name='V050 registered generated face painting only';tx.image=gen;tx.extension='CLIP';lk.new(v.outputs[0],tx.inputs[0]);rgb=ns.new('ShaderNodeSeparateColor');rgb.mode='RGB';lk.new(tx.outputs['Color'],rgb.inputs[0]);skin=clamp(mn('DIVIDE',mn('SUBTRACT',mn('SUBTRACT',rgb.outputs['Red'],rgb.outputs['Green']),.012),.018))
# Original-space left boundary protects the hair/fringe and braid from any new
# skin paint. Only the exposed face/ear/neck region is eligible. Original shader
# alpha and all original mesh coordinates remain the sole outer silhouette.
left=[(194,1071),(200,1055),(210,1040),(220,1024),(230,992),(240,990),(250,1000),(258,1005),(268,986),(278,979),(290,972),(305,980),(315,997)]
region=clamp(mn('DIVIDE',mn('SUBTRACT',px,curve(py,left)),1.5));region=mn('MULTIPLY',region,mn('MULTIPLY',clamp(mn('SUBTRACT',py,193)),clamp(mn('SUBTRACT',315,py))));factor=mn('MULTIPLY',skin,region)
em=next(n for n in ns if n.type=='EMISSION');original=em.inputs[0].links[0].from_socket;mix=ns.new('ShaderNodeMixRGB');mix.name='V050 face only; original hair braid and outer alpha retained';lk.new(factor,mix.inputs[0]);lk.new(original,mix.inputs[1]);lk.new(tx.outputs['Color'],mix.inputs[2]);lk.new(mix.outputs[0],em.inputs[0]);girlhead['V050_scope']='New registered face/ear/neck paint only, source-space hair protection, original mesh and original alpha. No turnaround.'
# Match exposed girl forearms/hands to the face; retain the exact atlas, UVs,
# painting and garment materials. Remove only the former charcoal conversion.
for role in ['skin','hand']:
 source=next(o.data.materials[0] for o in C.objects if o.parent==rigs['BOY'] and o.get('wardrobe_role')==role)
 mat=source.copy();mat.name='V050 GIRL | original painted '+role+' in matching skin finish'
 for o in C.objects:
  if o.parent==rigs['GIRL'] and o.get('wardrobe_role')==role:o.data.materials[0]=mat
hands=[]
def sm(t):t=max(0,min(1,t));return t*t*(3-2*t)
for who,r in rigs.items():
 for side in ['near','far']:
  o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='hand' and o.name.endswith(side));wrist=r.data.bones['hand_'+side].head_local.z;L=o['painted_vertical_hand_span_m'];a=.057;angle=math.radians((23 if side=='near' else 19) if who=='BOY' else (21 if side=='near' else 17));k=angle/(L-a);old=[v.co.copy() for v in o.data.vertices];uvs={lp.vertex_index:o.data.uv_layers[0].data[lp.index].uv.copy() for lp in o.data.loops}
  for i,v in enumerate(o.data.vertices):
   d=wrist-v.co.z
   if d<=a:continue
   theta=k*(d-a);cx=(1-math.cos(theta))/k;dz=a+math.sin(theta)/k;u=uvs[i];pxh=u.x*1254;pyh=(1-u.y)*1254
   group=1-.09*sm((d-a)/.035);x=v.co.x*group
   x-=.002*sm((pxh-267)/35)*sm((pyh-1005)/40)*(1-sm((pyh-1110)/55))
   v.co.x=cx+x*math.cos(theta);v.co.z=wrist-dz+x*math.sin(theta)
  o.data.update();o['V050_hand_finish']='Static relaxed continuous MCP/finger arc and tucked thumb; source painting and original hand Action preserved. Developed centreline length retained; projected span is shorter under curl.'
  samples=[a+j*(L-a)/1000 for j in range(1001)];points=[((1-math.cos(k*(d-a)))/k,a+math.sin(k*(d-a))/k) for d in samples];arc=a+sum(math.hypot(q[0]-p[0],q[1]-p[1]) for p,q in zip(points,points[1:]));assert abs(arc-L)<1e-8
  wrist_error=max((v.co-p).length for v,p in zip(o.data.vertices,old) if wrist-p.z<=a);assert wrist_error==0
  hands.append({'object':o.name,'developed_wrist_to_tip_target_m':L,'measured_developed_centreline_m':arc,'curl_degrees':math.degrees(angle),'projected_centreline_m':a+math.sin(angle)/k,'wrist_and_proximal_palm_error_m':wrist_error,'source_paint_and_uvs_preserved':True})
assert protected_actions=={a.name:ah(a) for a in bpy.data.actions}
for who,r in rigs.items():assert bones[who]=={b.name:[tuple(b.head_local),tuple(b.tail_local)] for b in r.data.bones}
for name,h in heads.items():assert hashlib.sha256(repr([tuple(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest()==h
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='2f78c5cd86b96d437d97a165b8b61473bcd6c9d1ab284015c229bfb11c6f9a94'
S['V050_scope']='Face rendering and static relaxed-hand construction only; all v049 bones, gait, root/camera and clothing Actions preserved.';S['V050_limit']='One fixed profile, no 3D head turn or articulated fingers. Static/walk-pose proof required before normal-speed preview. Technical checks are not artistic approval.';S.frame_set(1);bpy.context.view_layer.update()
(P/'evidence/FINISH_BUILD.json').write_text(json.dumps({'source':str(SRC),'source_sha256':'2f78c5cd86b96d437d97a165b8b61473bcd6c9d1ab284015c229bfb11c6f9a94','all_existing_actions_preserved':protected_actions,'bones':bones,'head_geometry_hashes':heads,'head_geometry_unchanged':True,'head_outer_alpha':'Original pair texture alpha connection unchanged. New generated alpha does not own silhouette.','face_registration':{'gen_image_size':[W,Hg],'gen_y':'665+(original_py-229)*4.2','gen_x':'4.2*original_px+piecewise edge shift','edge_shift':edge_shift,'original_hair_protection_left_boundary':left,'mask':'Generated warm skin only, within original-space face/ear/neck eligibility.'},'hand_changes':hands,'source_unchanged':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Face_Hand_Finish_v050.blend'),compress=True);print('V050_FACE_AND_RELAXED_HAND_CANDIDATE_SAVED_GAIT_UNCHANGED')
