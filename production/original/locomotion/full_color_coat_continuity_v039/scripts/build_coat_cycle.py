import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import coat_cycle_model as M
SRC=P/'reference/PRESERVED_COLOR_v038.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];coat=bpy.data.objects['V037 | coherent charcoal coat | five pose study'];ctrl=bpy.data.objects['V037 | garment review values | static pose selector'];old=bpy.data.objects['V025 | COAT drawings | editable GP']
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();fore.update()
def ah(a):return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
oldactions={a.name:ah(a) for a in bpy.data.actions};oldUV=hashlib.sha256(repr([tuple(v.uv) for v in coat.data.uv_layers.active.data]).encode()).hexdigest();mat=coat.material_slots[0].material;oldramps={n.name:[(e.position,tuple(e.color)) for e in n.color_ramp.elements] for n in mat.node_tree.nodes if n.type=='VALTORGB'};bounds=[]
for f in range(1,32):
 fr=next(fr for fr in old.data.layers[0].frames if fr.frame_number==f);V=[old.matrix_local@p.position for p in fr.drawing.strokes[0].points];bounds.append([min(v.z for v in V),max(v.z for v in V)])
cache={};angles=[]
for i in range(125):
 f=1+i/4;frame(f);inv=T.matrix_world.inverted();h=inv@(rig.matrix_world@rig.pose.bones['pelvis'].head);n=inv@(rig.matrix_world@rig.pose.bones['chest'].tail);cache[f]={'h':h.copy(),'n':n.copy()}
 if i<124:angles.append(math.atan2((n-h).x,(n-h).z))
lag,lagreport=M.settled_lag(angles);hipref=cache[1.]['h'].z;coords={};compression={};records=[]
for i in range(125):
 f=1+i/4;q=f-1;h=cache[f]['h'];n=cache[f]['n'];c=M.smooth((hipref-h.z)/.015);zmin=M.periodic([r[0] for r in bounds],q);zmax=M.periodic([r[1] for r in bounds],q);delta=lag[(i*2)%248];V=M.points(h,n,zmin,zmax,c,delta);coords[f]=V;compression[f]=c;records.append({'frame':f,'hip':list(h),'neck':list(n),'compression':c,'hem_lag_degrees':math.degrees(delta),'vertical_extent_m':[min(v.z for v in V),max(v.z for v in V)],'source_extent_m':[zmin,zmax]})
# Closing sample is an exact local-space bookend, independently of tiny source
# floating-point differences after one unwrapped root stride.
coords[32.]=[v.copy() for v in coords[1.]];compression[32.]=compression[1.]
for id in [coat.data.shape_keys,ctrl]:
 if id.animation_data and id.animation_data.action:id.animation_data.action.use_fake_user=True
coat.shape_key_clear();ctrl.animation_data_clear();coat.data.vertices.foreach_set('co',[c for p in coords[1.] for c in p]);coat.shape_key_add(name='Basis | F1 cycle contact');F=list(coords)
for f in F[1:-1]:
 key=coat.shape_key_add(name='V039 coat breakdown F%05.2f'%f);key.data.foreach_set('co',[c for p in coords[f] for c in p])
 # Compact hat weights: quarter-frame breakdowns interpolate continuously and
 # repeat exactly over1..32. Every channel includes the bookend for period31.
 for t in [1.,max(1.,f-.25),f,min(32.,f+.25),32.]:
  key.value=float(t==f);key.keyframe_insert('value',frame=t)
for f,c in compression.items():ctrl['compression']=c;ctrl.keyframe_insert('["compression"]',frame=f)
for id,name in [(coat.data.shape_keys,'V039 | one cycle coat breakdowns | quarter-frame'),(ctrl,'V039 | existing loading to coat compression')]:
 a=id.animation_data.action;a.name=name
 for l in a.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cyc=fc.modifiers.new('CYCLES');cyc.mode_before=cyc.mode_after='REPEAT'
ctrl['painted']=1.;ctrl['V039_scope']='Continuous compression from existing hip drop; one31-frame cycle with closing key. Original color palette retained.';coat['V039_scope']='Rough continuous coat test.124quarter-frame shape samples+exactclosingbookend. Reviewed construction/palette retained; small settled hem lag only. Body motion unchanged. No broad garment redesign or artistic acceptance.'
coat.data.update();S.frame_start=1;S.frame_end=94;S.render.fps=30
for marker in list(S.timeline_markers):S.timeline_markers.remove(marker)
for f,label in [(1,'CONTACT / CYCLE START'),(4,'LOADED DOWN'),(11,'PASSING / ARM CROSS'),(17,'FAR CONTACT'),(20,'LOADED DOWN / FAR HAND BEHIND LEG'),(27,'HAND HEM CHECK'),(32,'EXACT LOCAL COAT BOOKEND'),(63,'SECOND CYCLE BOOKEND'),(94,'THIRD CYCLE BOOKEND')]:S.timeline_markers.new(label,frame=f)
S['V039_status']='ROUGH FULL-COLOR COAT CONTINUITY TEST. One31-frame cycle+closingbookend, rendered as repeated native cycles for review. Preferred body/foot motion and v038 palette retained. Not accepted final animation.';S['V039_legacy_labels']='Some object/attribute labels retain V037 names for dependency stability; the coat now has continuous V039 breakdowns, not five held poses.'
t=bpy.data.texts.new('READ_FIRST_v039');t.write('Current rough coat continuity test. Native frames1..32 author one31-frame cycle; repeats over the unchanged body/root clock. V038 full-color materials, root repair, identity and preferred body motion preserved.124quarter-frame samples plus exact closing bookend; no frozen pose swapping. Small damped hem follower derives from actual trunk direction. Track fitted/flat coat volume, conspicuous pattern and passing-foot congestion candidly. No production integration or acceptance.');frame(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
unchanged=[n for n,h in oldactions.items() if ah(bpy.data.actions[n])!=h];newUV=hashlib.sha256(repr([tuple(v.uv) for v in coat.data.uv_layers.active.data]).encode()).hexdigest();newramps={n.name:[(e.position,tuple(e.color)) for e in n.color_ramp.elements] for n in mat.node_tree.nodes if n.type=='VALTORGB'};assert not unchanged and oldUV==newUV and oldramps==newramps
report={'scope':'Technical build record, not artistic acceptance','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'Blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'authored_source_frame_range':[1,32],'period_frames':31,'fps':30,'native_breakdown_sample_interval':.25,'local_pose_samples':125,'quarter_pose_shape_keys_plus_basis':len(coat.data.shape_keys.key_blocks),'exact_local_closing_bookend':True,'original_action_datablocks_mutated':unchanged,'active_garment_actions_replaced':['coat shape-key Action','garment compression custom-property Action'],'all_other_original_active_actions_untouched':True,'UV_hash_unchanged':oldUV==newUV,'coat_color_ramp_stops_unchanged':oldramps==newramps,'hem_follower':lagreport,'compression':'Smoothstep of the same existing hip-drop range; no body motion changes.','source_extent_interpolation':'Periodic Catmull interpolation through original coat min/max Z; integer-frame extents retained.','samples':records};(P/'evidence/COAT_CYCLE_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Full_Color_Coat_Continuity_Rough_v039.blend'),compress=True);print('V039_COAT_CYCLE_BUILT',json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
