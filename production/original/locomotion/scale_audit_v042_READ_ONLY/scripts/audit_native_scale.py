"""Read sources, inspect and render diagnostic cutouts in RAM. NEVER save a blend."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];L=P.parent;CASES={
'v028':L/'upper_body_pose_refinement_v028/native/WTSC_Upper_Body_Pose_Refinement_v028.blend',
'v036':L/'rigid_limb_continuity_v036/native/WTSC_Limb_Volume_and_Hand_Readability_v036.blend',
'v039':L/'full_color_coat_continuity_v039/native/WTSC_Full_Color_Coat_Continuity_Rough_v039.blend',
'v040':L/'character_design_finish_v040/native/WTSC_Painted_Character_Look_STUDY_v040.blend',
'v041':L/'neck_collar_connection_v041/native/WTSC_Neck_Collar_Connection_Candidate_v041.blend'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def box(V):return [[min(v[i] for v in V),max(v[i] for v in V)] for i in range(len(V[0]))]
def projected(S,c,V,size):
 S.render.resolution_x,S.render.resolution_y=size;Q=[world_to_camera_view(S,c,v) for v in V];return box([Vector((v.x*size[0],(1-v.y)*size[1])) for v in Q])
report={};hashes={}
for version,path in CASES.items():
 before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;R=bpy.data.objects['LOCO_BOY | RIG'];fore=S.view_layers['V025 | original foreground'];fg={o.name for o in bpy.data.collections['V025 | retained foreground identity'].all_objects};head=bpy.data.objects.get('V040 | painted boy profile and neck');head=head if head and not head.hide_render else bpy.data.objects['PERF_BOY | original head'];keep={o.name for o in S.objects if o.type in ['MESH','GREASEPENCIL'] and not o.hide_render and (o==head or any(tag in o.name for tag in ['BOY','V024 continuous','canonical painted shoe','shoe','V037 | coherent','V025 | COAT','V041 | folded']))};cams={n:bpy.data.objects[n] for n in ['V024 | CLOSE portrait','V020 | CHILD | SHOT']};scene_record={'source':str(path),'source_sha256':before,'saved_camera':S.camera.name if S.camera else None,'saved_render':[S.render.resolution_x,S.render.resolution_y,S.render.resolution_percentage],'pixel_aspect':[S.render.pixel_aspect_x,S.render.pixel_aspect_y],'fps':S.render.fps,'unit_system':S.unit_settings.system,'unit_scale_length':S.unit_settings.scale_length,'rig_scale':list(R.scale),'root_scale':list(R.parent.scale),'rig_world_scale':list(R.matrix_world.to_scale()),'head_object':head.name,'camera_data':{},'bones':{},'frames':{},'diagnostic_visible_objects':sorted(keep)}
 for name,c in cams.items():scene_record['camera_data'][name]={k:getattr(c.data,k) for k in ['type','lens','ortho_scale','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']}
 for b in R.data.bones:
  if any(t in b.name for t in ['pelvis','chest','neck','head','upper_arm','forearm','hand','thigh','shin','foot']):scene_record['bones'][b.name]={'rest_length':b.length,'head':list(b.head_local),'tail':list(b.tail_local)}
 for f in [1,20]:
  S.frame_set(f);bpy.context.view_layer.update();fore.update();row={'root_world':[list(x) for x in R.parent.matrix_world],'camera_world':{n:[list(r) for r in c.matrix_world] for n,c in cams.items()},'parts':{}}
  for name in sorted(keep):
   o=bpy.data.objects[name]
   if o.type!='MESH':continue
   vl=fore if (name in fg or name.startswith('V041 |')) else bpy.context.view_layer;vl.update();e=o.evaluated_get(vl.depsgraph);V=[e.matrix_world@v.co for v in e.data.vertices]
   if not V:continue
   r={'world_geometry_bbox_including_transparent_canvas':box(V),'vertices':len(V),'close_projected_geometry_pixels':projected(S,cams['V024 | CLOSE portrait'],V,(480,720)),'shot_projected_geometry_pixels':projected(S,cams['V020 | CHILD | SHOT'],V,(1280,720))}
   if 'articulated drawn hand' in name:
    side='near' if name.endswith('near') else 'far';B=R.matrix_world@R.pose.bones['hand_'+side].matrix;axes=[B.to_3x3().col[j].normalized() for j in range(3)];local=[Vector(tuple((v-B.translation).dot(ax) for ax in axes)) for v in V];r['hand_bone_aligned_bbox']=box(local)
   if 'shoe' in name.lower():r['shoe_rest_bbox']=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]
   row['parts'][name]=r
  scene_record['frames'][str(f)]=row
 # Cutouts are diagnostic renders of actual source geometry/material alpha.
 # Stage/floor and paper compositor are hidden only in memory, not saved.
 for o in S.objects:
  if o.type in ['MESH','GREASEPENCIL','CURVE','FONT'] and o.name not in keep:o.hide_render=True
 S.render.film_transparent=True;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.image_settings.color_depth='8';g=bpy.data.node_groups.new('SCALE AUDIT ONLY | transparent character layers','CompositorNodeTree');g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');S.compositing_node_group=g;n=g.nodes;lk=g.links;a=n.new('CompositorNodeRLayers');a.layer=S.view_layers[0].name;b=n.new('CompositorNodeRLayers');b.layer='V025 | original foreground';over=n.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;lk.new(a.outputs['Image'],over.inputs['Background']);lk.new(b.outputs['Image'],over.inputs['Foreground']);out=n.new('NodeGroupOutput');lk.new(over.outputs['Image'],out.inputs['Image']);S.frame_set(1)
 for view,cam,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
  S.camera=cams[cam];S.render.resolution_x,S.render.resolution_y=size;S.render.filepath=str(P/f'images/{version}_FULL_{view}_F1.png');bpy.ops.render.render(write_still=True)
 for name in keep:
  if name!=head.name:bpy.data.objects[name].hide_render=True
 S.camera=cams['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.filepath=str(P/f'images/{version}_HEAD_CLOSE_F1.png');bpy.ops.render.render(write_still=True);after=sha(path);assert before==after;hashes[version]={'source':str(path),'before':before,'after':after,'unchanged':True};report[version]=scene_record;print('SCALE_AUDIT',version,'READ_ONLY_COMPLETE',flush=True)
(P/'evidence/NATIVE_SCALE_AUDIT.json').write_text(json.dumps(report,indent=2));(P/'evidence/SOURCE_HASHES_BEFORE_AFTER.json').write_text(json.dumps(hashes,indent=2));print('ALL_SCALE_AUDITS_COMPLETE',flush=True)
