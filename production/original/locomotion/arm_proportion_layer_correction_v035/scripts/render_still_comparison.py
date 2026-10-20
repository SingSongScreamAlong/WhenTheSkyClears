import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];start=time.time();records=[];projected={};FRAMES=[11,20,27]
def draw_guides(S,rig):
 fore=S.view_layers['V025 | original foreground'];col=bpy.data.collections.new('V035 | measured joint guides | review only');bpy.data.collections['V025 | retained foreground identity'].children.link(col);gp=bpy.data.grease_pencils.new('V035 actual straight bone axes');ob=bpy.data.objects.new(gp.name,gp);col.objects.link(ob);ob.parent=rig.parent;layer=gp.layers.new('Actual source bones on ones',set_active=True);layer.use_lights=False;mi={}
 for side,c in [('near',(.9,.16,.035)),('far',(.015,.32,.85))]:
  m=bpy.data.materials.new('V035 guide '+side);bpy.data.materials.create_gpencil_data(m);m.grease_pencil.show_fill=True;m.grease_pencil.show_stroke=False;m.grease_pencil.fill_color=(*c,1);gp.materials.append(m);mi[side]=len(gp.materials)-1
 def poly(d,V,side):
  d.add_strokes([len(V)]);st=d.strokes[-1];st.cyclic=True;st.material_index=mi[side];st.fill_id=len(d.strokes);st.fill_opacity=1;st.fill_color=(0,0,0,0)
  for p,v in zip(st.points,V):p.position=(v.x,-.30,v.z);p.radius=.001;p.opacity=1
 for f in range(1,32):
  S.frame_set(f);bpy.context.view_layer.update();fore.update();inv=rig.parent.matrix_world.inverted();d=layer.frames.new(f).drawing
  for side in ['far','near']:
   b=rig.pose.bones;sets=[[(inv@(rig.matrix_world@p)) for p in [b['thigh_'+side].head,b['shin_'+side].head,b['shin_'+side].tail]],[(inv@(rig.matrix_world@p)) for p in [b['upper_arm_'+side].head,b['forearm_'+side].head,b['hand_'+side].head]]]
   for V in sets:
    for a,z in zip(V,V[1:]):n=Vector((-(z-a).z,0,(z-a).x)).normalized()*.0015;poly(d,[a+n,z+n,z-n,a-n],side)
    for p in V:poly(d,[p+Vector((.006*math.cos(i*math.tau/16),0,.006*math.sin(i*math.tau/16))) for i in range(16)],side)
  d.tag_positions_changed()
 return col
def light(S):
 for o in list(S.objects):
  if o.type!='MESH' or o.hide_render:continue
  side='near' if 'near' in o.name else 'far';c=None
  if 'articulated drawn hand' in o.name:c=(.69,.53,.38) if side=='near' else (.57,.52,.44)
  elif 'drawn skin' in o.name:c=(.56,.45,.34) if side=='near' else (.48,.46,.40)
  elif 'drawn sleeve' in o.name:c=(.37,.44,.47) if side=='near' else (.29,.36,.39)
  elif 'source gray cuff' in o.name:c=(.76,.72,.59)
  elif 'V024 continuous' in o.name:c=(.25,.31,.35) if side=='near' else (.43,.47,.49)
  elif o.name=='LOCO_BOY | PAINT body':c=(.55,.59,.56)
  if c is None:continue
  for slot in o.material_slots:
   if not slot.material:continue
   m=slot.material.copy();m.name='V035 TEMP WORK | '+o.name;slot.link='OBJECT';slot.material=m
   for n in m.node_tree.nodes:
    if n.type=='EMISSION':
     for link in list(n.inputs['Color'].links):m.node_tree.links.remove(link)
     n.inputs['Color'].default_value=(*c,1)
 coat=bpy.data.objects['V025 | COAT drawings | editable GP'];colors=[(.37,.41,.42,1),(.17,.22,.24,.60),(.65,.69,.67,.72),(.62,.66,.62,.7),(.08,.13,.15,.75),(.20,.24,.25,.14),(.8,.8,.8,.75)]
 for i,old in enumerate(list(coat.data.materials)):
  m=old.copy();m.name='V035 TEMP WORK coat '+str(i);m.grease_pencil.fill_color=colors[i];m.grease_pencil.color=colors[i];coat.data.materials[i]=m
def render(S,mode,f):
 folder=P/'previews'/mode;folder.mkdir(exist_ok=True);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'mode':mode,'frame':f,'size':[S.render.resolution_x,S.render.resolution_y]})
for variant,path in [('ARMS',P/'native/WTSC_Arm_Proportion_Correction_v035.blend'),('ALL',P/'native/WTSC_Arm_and_Leg_Structure_v035.blend'),('SOURCE',P/'reference/PREFERRED_v033.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];fore=S.view_layers['V025 | original foreground'];S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100
 if variant!='SOURCE':
  for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
   S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size
   for f in FRAMES:S.frame_set(f);render(S,variant+'_'+view,f)
 if variant=='ARMS':continue
 light(S);guides=draw_guides(S,rig);projected[variant]={}
 for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
  S.camera=bpy.data.objects[cam];S.render.resolution_x,S.render.resolution_y=size;projected[variant][view]={}
  for f in FRAMES:
   S.frame_set(f);bpy.context.view_layer.update();fore.update();guides.hide_render=True
   if view=='CLOSE':render(S,variant+'_LIGHT_'+view,f)
   guides.hide_render=False;render(S,variant+'_GUIDES_'+view,f);r={}
   for side in ['near','far']:
    b=rig.pose.bones;r[side]={}
    for name,pos in [('Hip',b['thigh_'+side].head),('Knee',b['shin_'+side].head),('Ankle',b['shin_'+side].tail),('Shoulder',b['upper_arm_'+side].head),('Elbow',b['forearm_'+side].head),('Wrist',b['hand_'+side].head)]:
     v=world_to_camera_view(S,S.camera,rig.matrix_world@pos);r[side][name]=[v.x*size[0],(1-v.y)*size[1]]
   projected[variant][view][f]=r
 if variant=='ALL':
  S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.frame_set(20);S['V035_working_review']='Temporary light materials; actual rigid bone guides. No hand x-ray. Candidate final-charcoal native is separate.';bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Light_Structure_Review_v035.blend'),compress=True)
(P/'evidence/STILL_RENDER_RECORD.json').write_text(json.dumps({'records':records,'render_count':len(records),'frames':FRAMES,'elapsed_seconds':time.time()-start,'no_cycle_render':True,'guides':'Measured actual native hip-knee-ankle and shoulder-elbow-wrist segments; projected in front only for labelled structure review. No hand mesh x-ray.','temporary_light_materials':'Diagnostic color separation only, no lighting changes. Dark candidate saved separately.','joint_projections':projected},indent=2));print('V035_STILLS_COMPLETE',len(records),time.time()-start,flush=True)
