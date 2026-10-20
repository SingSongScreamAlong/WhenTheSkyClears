import bpy,json,runpy,re
from pathlib import Path
P=Path(__file__).resolve().parents[1];V9=P.parent/'recovery_walk_refinement_v009'
bpy.ops.wm.open_mainfile(filepath=str(V9/'native/WTSC_v009_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene
old=next(o for o in s.objects if o.get('motion_revision')=='v009_recovery_walk');anchor=old.matrix_world.copy();oldcol=old.users_collection[0];stem=lambda name:re.sub(r'\.\d{3}$','',name)
cameras={};frozen=[]
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();cameras[f]=s.camera.matrix_world.copy()
for f in range(1921,1969):
 cameras[f]=cameras[1920].copy();cameras[f].translation.x+=.012*(f-1920)
paint={stem(o.name):list(o.data.materials) for o in old.children_recursive if o.type=='MESH'}
with bpy.data.libraries.load(str(P/'native/WTSC_Stumble_Polish_Continuation_v010.blend'),link=False) as (av,loaded):loaded.collections=['WTSC_STUMBLE_POLISH_CONTINUATION_v010']
newcol=loaded.collections[0];s.collection.children.link(newcol);root=next(o for o in newcol.all_objects if o.get('motion_revision')=='v010_polish_continuation');root.matrix_world=anchor
cfg=runpy.run_path(str(P/'scripts/configure_v010.py'))['configure_v010'];cfg(start=1801,root_motion=True,root=root)
for o in root.children_recursive:
 if o.type=='MESH' and stem(o.name) in paint:
  o.data.materials.clear()
  for mat in paint[stem(o.name)]:o.data.materials.append(mat)
oldcol.hide_render=True;oldcol.hide_viewport=True;rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};contactrows=[]
for plane in [o for o in s.objects if o.name.startswith('v041 sole contact |')]:
 s.frame_set(1801);bpy.context.view_layer.update();slope=(3-(plane.location.z+.002))/(plane.location.y+16);who='BOY' if 'BOY' in plane.name else 'GIRL';side='near' if 'near' in plane.name else 'far';boot=next(o for o in rigs[who].children if o.get('v007_role')=='support_boot' and stem(o.name).endswith(side));plane.animation_data_clear();nt=plane.data.materials[0].node_tree;nt.animation_data_clear();weight=next(n for n in nt.nodes if n.type=='MATH' and n.operation=='MULTIPLY')
 for f in range(1801,1969):
  s.frame_set(f);bpy.context.view_layer.update();ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();low=min(v.z for v in pts);bottom=[v for v in pts if v.z<=low+.004];x=sum(v.x for v in bottom)/len(bottom);y=sum(v.y for v in bottom)/len(bottom);height=low-(3-slope*(y+16));yy=y+.018;plane.location=(x,yy,3-slope*(yy+16)-.002);plane.scale=(max(.08,(max(v.x for v in pts)-min(v.x for v in pts))*1.05),1,.035+.025*max(0,min(1,height/.15)));weight.inputs[1].default_value=max(0,min(1,1-max(0,height)/.13))**2;plane.keyframe_insert('location',frame=f);plane.keyframe_insert('scale',frame=f);weight.inputs[1].keyframe_insert('default_value',frame=f);contactrows.append({'frame':f,'who':who,'side':side,'contact_x':x,'height':height,'opacity':weight.inputs[1].default_value})
 for id in [plane,nt]:
  for layer in id.animation_data.action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for key in fc.keyframe_points:key.interpolation='LINEAR'
 plane['v010_new_boot_reference']=boot.name
camera=bpy.data.objects.new('V010 | v009 camera retained plus separate constant extension',s.camera.data.copy());s.collection.objects.link(camera);camera.rotation_mode='QUATERNION'
for f,M in cameras.items():
 camera.matrix_world=M
 for field in ['location','rotation_quaternion','scale']:camera.keyframe_insert(field,frame=f)
for layer in camera.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
s.camera=camera;s.name='V010 | matched polish and separate continuation review';s.frame_start=1801;s.frame_end=1968;s.render.use_sequencer=False;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=16;s.frame_set(1801)
(P/'evidence/matched_contact_samples.json').write_text(json.dumps(contactrows,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_v010_Matched_Review_Copy.blend'),compress=True)
(P/'evidence/matched_copy.json').write_text(json.dumps({'source':'Retained isolated v009 matched world; read-only','camera':'First120 evaluated matrices retained exactly;1921..1968 add.012m/frame to1920cameraX. Same other camera channels.','art':'Retained v045c art and actual source material/light response. Existing FX clock allowed to continue; no new FX work.','contacts':'Four soft marks rebaked from actual v010 soles through1968.','timing':'1801..1920 original five-second contract;1921..1968 separate2s extension. No full trailer edit.'},indent=2));print('V010_MATCHED_COPY_BUILT',flush=True)
