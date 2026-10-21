import bpy,math,json,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import model_spec as M
SRC=ROOT/'locomotion/weight_loading_v048/native/WTSC_Connected_Weight_Loading_v048.blend';source_sha=hashlib.sha256(SRC.read_bytes()).hexdigest();assert source_sha=='eeefa9ea2059a613d796277d6dfebfabe84a89b1c31470b585e5475fcb35001b';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V048 | CONNECTED WEIGHT LOADING | ordinary walk'];bpy.context.window.scene=S;S.name='V049 | MODEL FIT AND GROUPED HANDS | v048 motion';master=bpy.data.collections['V048 | AGE10 PAIR | connected weight loading'];master.name='V049 | AGE10 PAIR | connected model fit';C=bpy.data.collections['V046 | restored original painted wardrobe'];ART=bpy.data.collections['V044 | age10 editable profile anatomy'];RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]).encode()).hexdigest()
protected={w:{'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in r.data.bones},'action_hash':ah(r.animation_data.action)} for w,r in RIGS.items()};head_hashes={o.name:hashlib.sha256(repr([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() for o in ART.objects if o.get('proportion_role')=='head'};root=bpy.data.objects['V048 | shared travel | steady .73125mps'];root_hash=ah(root.animation_data.action);camera_hash=ah(S.camera.animation_data.action);changes=[];hand_checks={}
atlas=next(i for i in bpy.data.images if 'Parts_Atlas_v040' in i.name and i.size[0]==1254);pixels=np.empty(1254*1254*4,dtype=np.float32);atlas.pixels.foreach_get(pixels);alpha=pixels.reshape(1254,1254,4)[::-1,:,3]
for who,r in RIGS.items():
 body=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='body');deltas=[]
 for i,v in enumerate(body.data.vertices):row,col=divmod(i,17);delta=M.torso_delta(who,row/64,col/16);v.co.x+=delta;deltas.append(delta)
 body.data.update();changes.append({'object':body.name,'max_silhouette_x_change_m':max(abs(x) for x in deltas),'scope':'Only garment outline, neck and hem end rows unchanged; no joint or stature edits.'})
 for side in ['near','far']:
  fore=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='skin' and o.name.endswith(side))
  hand=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='hand' and o.name.endswith(side));hs=hand['painted_vertical_hand_span_m']/(hand['actual_painted_fingertip_source_row']-950);wristz=r.data.bones['hand_'+side].head_local.z
  for i,v in enumerate(fore.data.vertices):
   row,col=divmod(i,9);t=row/32;s=col/8;x=(s*2-1)*M.forearm_radius(t)
   if t>.90:
    py=950+(wristz-v.co.z)/hs;good=np.flatnonzero(alpha[min(1253,max(0,int(round(py)))),140:330]>.75)+140;assert len(good)
    lo=float(good.min())+.6;hi=float(good.max())-.6;a=M.hand_x((lo-220)*hs,lo,py);b=M.hand_x((hi-220)*hs,hi,py);w=M.smooth((t-.90)/.10);x=x*(1-w)+(a+(b-a)*s)*w
   v.co.x=x
  fore.data.update();before=[v.co.copy() for v in hand.data.vertices];uv={lp.vertex_index:hand.data.uv_layers[0].data[lp.index].uv.copy() for lp in hand.data.loops}
  for i,v in enumerate(hand.data.vertices):u=uv[i];v.co.x=M.hand_x(v.co.x,u.x*1254,(1-u.y)*1254)
  hand.data.update();zerr=max(abs(v.co.z-p.z) for v,p in zip(hand.data.vertices,before));assert zerr==0
  mingap=min(hand.data.vertices[row*17+j+1].co.x-hand.data.vertices[row*17+j].co.x for row in range(49) for j in range(16));assert mingap>0
  hand['V049_scope']='Original painted fingers grouped horizontally, thumb brought closer and wrist tapered. Original vertical coordinates and measured extended-hand target retained; no finger animation system.';hand_checks[hand.name]={'all_original_z_coordinates_preserved':True,'vertical_coordinate_error_m':zerr,'minimum_row_x_order_gap_m':mingap,'extended_hand_target_m':hand['painted_vertical_hand_span_m'],'maximum_local_x_deformation_m':max(abs(v.co.x-p.x) for v,p in zip(hand.data.vertices,before))}
# Only sleeves change: preserve every leg drawing and the gait exactly.
CACHE={w:{} for w in RIGS}
for i in range(129):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for who,r in RIGS.items():e=r.evaluated_get(dg);CACHE[who][f]={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()}
for who,r in RIGS.items():
 for side in ['near','far']:
  o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')=='sleeve' and o.name.endswith(side));poses={f:M.limb_vertices(r,p,side,'sleeve') for f,p in CACHE[who].items()};o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in poses[1.] for c in p]);o.shape_key_add(name='Basis | softened sleeve F1')
  for i in range(1,128):
   f=1+i/4;k=o.shape_key_add(name='V049 sleeve fit F%05.2f'%f);k.data.foreach_set('co',[c for p in poses[f] for c in p])
   for at in [1.,max(1.,f-.25),f,min(33.,f+.25),33.]:k.value=float(at==f);k.keyframe_insert('value',frame=at)
  for l in o.data.shape_keys.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
      cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
for who,r in RIGS.items():
 assert ah(r.animation_data.action)==protected[who]['action_hash']
 for b in r.data.bones:assert list(b.head_local)==protected[who]['bones'][b.name]['head'] and list(b.tail_local)==protected[who]['bones'][b.name]['tail']
for name,h in head_hashes.items():assert hashlib.sha256(repr([tuple(v.co) for v in bpy.data.objects[name].data.vertices]).encode()).hexdigest()==h
assert ah(root.animation_data.action)==root_hash and ah(S.camera.animation_data.action)==camera_hash;assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_sha
S['V049_scope']='Static model-fit candidate following independent visual findings. Softer connected garment ribcage/waist/pelvis, shaped sleeve crowns/cuffs, fuller tapered forearms, grouped original fingers. v048 bones, gait, root, head/hair and image pixels preserved.';S['V049_limit']='Hand vertical dimensions unchanged; local horizontal finger/wrist deformation only. Girl charcoal face/white eye remains a separate finish mismatch. Static proof is not model or animation acceptance.';S.frame_set(1);bpy.context.view_layer.update();report={'source':str(SRC),'source_sha256':source_sha,'source_unchanged':True,'protected_rigs':protected,'root_action_hash':root_hash,'camera_action_hash':camera_hash,'gait_and_rest_bones_preserved':True,'head_hair_geometry_hashes':head_hashes,'face_hair_geometry_preserved':True,'source_images_and_uvs_edited':False,'garment_changes':changes,'hand_checks':hand_checks,'sleeve_changes':'Softer narrower crown, quieter flare,4mm shaped cuff-edge overlap; no shoulder joint movement. All sleeve caches regenerated to SAME v048 poses.','forearm_changes':'Slightly fuller proximal forearm; nominal21mm wrist radius blends into the actual painted hand alpha contour over the final10percent.','artistic_limit':S['V049_limit']};(P/'evidence/MODEL_FIT_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Connected_Model_Fit_v049.blend'),compress=True);print('V049_TARGETED_MODEL_FIT_NATIVE_SAVED_V048_GAIT_PRESERVED',flush=True)
