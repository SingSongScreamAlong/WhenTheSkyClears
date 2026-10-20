import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work'/'production_review_v059'
M=R/'shots/world/WTSC_Open_Battlefield_Refinement_v048a.blend';W=R/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend'
bpy.ops.wm.open_mainfile(filepath=str(M),load_ui=False,use_scripts=False)
src=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v048a'];bpy.context.window.scene=src
root=next(o for o in src.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
cams=[];feet=[];props={}
for f in range(1801,1921):
 src.frame_set(f);bpy.context.view_layer.update()
 cams.append({'f':f,'matrix':[list(v) for v in src.camera.matrix_world]})
 if f in [1801,1834,1844,1861,1881,1901,1918,1920]:
  deps=bpy.context.evaluated_depsgraph_get()
  row={'f':f,'root':list(root.matrix_world.translation),'objects':[]}
  for ob in root.children_recursive:
   if ob.type=='MESH' and any(q in ob.name.lower() for q in ['boot','shoe','foot','hand','skin','cuff']):
    e=ob.evaluated_get(deps);pts=[e.matrix_world@v.co for v in e.data.vertices]
    row['objects'].append({'name':ob.name,'parent':ob.parent.name if ob.parent else None,'count':len(pts),'bbox':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'shapes':list(ob.data.shape_keys.key_blocks.keys())[:5] if ob.data.shape_keys else [],'modifiers':[(m.name,m.type) for m in ob.modifiers]})
  feet.append(row)
props['source_collections']=[{'name':c.name,'objects':len(c.all_objects)} for c in src.collection.children]
props['v043_objects']=[ob.name for ob in bpy.data.collections['v043 OWNED | Local contours and physical light'].objects]
with bpy.data.libraries.load(str(W),link=False) as (a,b):
 b.scenes=['WTSC_WORLD_FOREGROUND_v058d','WTSC_FULL_FILM_KNOCKOUT_v040']
s=b.scenes[0];mask=b.scenes[1];s.name='WTSC_PAIRED_RECOVERY_WORLD_v059a'
for cn in ['WTSC_BATTLEFIELD_DRAWN_PAIR_v007','v047 | Painterly turn drawings and connected wrists','v043 OWNED | Local contours and physical light']:
 c=bpy.data.collections[cn];s.collection.children.link(c)
fx=src.objects.get('FXv003 | fixed ground origin and controls')
if fx:
 for ob in [fx]+list(fx.children_recursive):
  if ob.name not in s.objects:s.collection.objects.link(ob)
held=next(o for o in s.objects if o.name.startswith('v016 | CHILDREN | held painterly'))
for ob in [held]+list(held.children_recursive):ob.hide_render=True;ob.hide_viewport=True
cam=bpy.data.objects.new('v059 | Independent camera | baked from reviewed recovery',src.camera.data.copy());s.collection.objects.link(cam);s.camera=cam
for row in cams:
 cam.matrix_world=Matrix(row['matrix']);cam.keyframe_insert('location',frame=row['f']);cam.keyframe_insert('rotation_euler',frame=row['f']);cam.keyframe_insert('scale',frame=row['f'])
for l in cam.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_start=1801;s.frame_end=1920;s.render.use_sequencer=False
bpy.context.window.scene=s;s.frame_set(1901);bpy.context.view_layer.update()
props['mask_nodes']=[{'name':n.name,'type':n.bl_idname,'scene':n.scene.name if hasattr(n,'scene') and n.scene else None,'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mask.compositing_node_group.links if l.from_node==n]} for n in mask.compositing_node_group.nodes]
props['camera_samples']=cams;props['foot_hand_snapshots']=feet
props['sources']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [M,W]}
props['output_scene']=s.name;props['mask_scene']=mask.name
(O/'integration_inspection.json').write_text(json.dumps(props,indent=2))
s.render.filepath='//preview_v059/'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'WTSC_Paired_Recovery_Integration_v059a.blend'),compress=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [1801,1844,1881,1901,1918]:
 s.frame_set(f);s.render.filepath=str(O/f'integrated_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name)
 print('INTEGRATED_KEY',f,flush=True)
print('INTEGRATION_READY',s.name,flush=True)
