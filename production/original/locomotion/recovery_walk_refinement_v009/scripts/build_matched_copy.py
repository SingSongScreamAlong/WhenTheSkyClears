import bpy,json,runpy,re
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'),load_ui=False)
s=bpy.data.scenes['WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046'];bpy.context.window.scene=s
old=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');anchor=old.matrix_world.copy();oldcol=old.users_collection[0]
cameras={}
for f in range(1801,1921):s.frame_set(f);bpy.context.view_layer.update();cameras[f]=s.camera.matrix_world.copy()
def stem(name):return re.sub(r'\.\d{3}$','',name)
paint={stem(o.name):list(o.data.materials) for o in old.children_recursive if o.type=='MESH'}
with bpy.data.libraries.load(str(P/'native/WTSC_Recovery_Walk_v009.blend'),link=False) as (av,loaded):loaded.collections=['WTSC_RECOVERY_WALK_PAIR_v009']
newcol=loaded.collections[0];s.collection.children.link(newcol);root=next(o for o in newcol.all_objects if o.get('motion_revision')=='v009_recovery_walk');root.matrix_world=anchor
cfg=runpy.run_path(str(P/'scripts/configure_v009.py'))['configure_v009'];cfg(start=1801,root_motion=True,root=root)
rows=[]
for o in root.children_recursive:
 if o.type=='MESH' and stem(o.name) in paint:
  o.data.materials.clear()
  for mat in paint[stem(o.name)]:o.data.materials.append(mat)
  rows.append(o.name)
oldcol.hide_render=True;oldcol.hide_viewport=True
# Re-bake the existing four soft contact planes from the actual new boots.
# Their old v046 curves were valid only for the previous protected foot route.
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};contactrows=[]
for plane in [o for o in s.objects if o.name.startswith('v041 sole contact |')]:
 s.frame_set(1801);bpy.context.view_layer.update();slope=(3-(plane.location.z+.002))/(plane.location.y+16)
 who='BOY' if 'BOY' in plane.name else 'GIRL';side='near' if 'near' in plane.name else 'far';boot=next(o for o in rigs[who].children if o.get('v007_role')=='support_boot' and stem(o.name).endswith(side))
 plane.animation_data_clear();nt=plane.data.materials[0].node_tree;nt.animation_data_clear();weight=next(n for n in nt.nodes if n.type=='MATH' and n.operation=='MULTIPLY')
 for f in range(1801,1921):
  s.frame_set(f);bpy.context.view_layer.update();ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();low=min(v.z for v in pts);bottom=[v for v in pts if v.z<=low+.004];x=sum(v.x for v in bottom)/len(bottom);y=sum(v.y for v in bottom)/len(bottom);height=low-(3-slope*(y+16));yy=y+.018;plane.location=(x,yy,3-slope*(yy+16)-.002);plane.scale=(max(.08,(max(v.x for v in pts)-min(v.x for v in pts))*1.05),1,.035+.025*max(0,min(1,height/.15)));weight.inputs[1].default_value=max(0,min(1,1-max(0,height)/.13))**2
  plane.keyframe_insert('location',frame=f);plane.keyframe_insert('scale',frame=f);weight.inputs[1].keyframe_insert('default_value',frame=f)
  contactrows.append({'frame':f,'who':who,'side':side,'boot_min_z':low,'height_above_projected_floor':height,'contact_x':x,'opacity':weight.inputs[1].default_value})
 for id in [plane,nt]:
  for layer in id.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='LINEAR'
 plane['v009_new_boot_reference']=boot.name;plane['binding_method']='V009 actual evaluated boot sole,120 samples; source soft contact material and floor projection retained.'
(P/'evidence/matched_contact_rebind.json').write_text(json.dumps(contactrows,indent=2))
camera=bpy.data.objects.new('V009 | matched camera with travel compensation',s.camera.data.copy());s.collection.objects.link(camera)
curve=list(__import__('csv').DictReader((P/'evidence/travel_curve_v009.csv').open()))
for f in range(1801,1921):
 M=cameras[f].copy();M.translation.x+=float(curve[f-1801]['delta_vs_v046_m']);camera.matrix_world=M;camera.rotation_mode='QUATERNION'
 for field in ['location','rotation_quaternion','scale']:camera.keyframe_insert(field,frame=f)
for layer in camera.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
s.camera=camera;s.name='V009 | matched v045c world review only';s.frame_start=1801;s.frame_end=1920;s.render.use_sequencer=False
for scene in list(bpy.data.scenes):
 if scene!=s:bpy.data.scenes.remove(scene)
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=16
s.render.filepath=str(P/'previews/matched/');s.frame_set(1801)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v009_Matched_Review_Copy.blend'),compress=True)
(P/'evidence/matched_copy.json').write_text(json.dumps({'source_world':'v046 on retained v045c art, opened read-only','anchor':[list(v) for v in anchor],'old_collection_hidden':oldcol.name,'source_material_response_reused_objects':rows,'camera':'Original evaluated v046 world matrices + X delta D009-D007; same lens/framing and fixed world/FX clocks. New per-frame camera keys only in isolated review copy.','render':'EEVEE960x540,16samples,two CPU threads; small review quality. No full master/audio/title edit.'},indent=2))
print('MATCHED_COPY_BUILT',flush=True)
