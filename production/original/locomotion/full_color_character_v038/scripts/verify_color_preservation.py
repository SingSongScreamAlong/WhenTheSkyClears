import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];F=[1,4,11,20,27]
def ah(a):return hashlib.sha256(repr([(fc.data_path,fc.array_index,fc.extrapolation,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points],[(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None)) for m in fc.modifiers]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
def mesh_hash(m):return hashlib.sha256(repr(([tuple(v.co) for v in m.vertices],[[tuple(p.co) for p in k.data] for k in m.shape_keys.key_blocks] if m.shape_keys else [],[tuple(v.uv) for v in m.uv_layers.active.data] if m.uv_layers.active else [])).encode()).hexdigest()
def setup(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;return S,bpy.data.objects['LOCO_BOY | RIG'],S.view_layers['V025 | original foreground']
def frame(S,f):S.frame_set(f);bpy.context.view_layer.update()
def pts(o,vl):vl.update();e=o.evaluated_get(vl.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
def me(A,B):return max(abs(A[a][b]-B[a][b]) for a in range(4) for b in range(4))
S,rig,fore=setup(P/'reference/PRESERVED_GARMENT_v037.blend');actions={a.name:ah(a) for a in bpy.data.actions};meshdata={m.name:mesh_hash(m) for m in bpy.data.meshes};images={i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file};fg={o.name for o in bpy.data.collections['V025 | retained foreground identity'].all_objects};names=[o.name for o in S.objects if o.type=='MESH' and not o.hide_render and any(tag in o.name for tag in ['BOY','V024 continuous','V033 |','V037 | coherent'])];motion={};cache={}
headmat=bpy.data.objects['PERF_BOY | original head'].material_slots[0].material
def alpha_links(m):return sorted((n.name,i,link.from_node.name,link.from_socket.name) for n in m.node_tree.nodes if n.type=='MIX_SHADER' for i,sock in enumerate(n.inputs) if i==0 for link in sock.links)
oldalpha=alpha_links(headmat)
for f in range(1,95):
 frame(S,f);motion[f]={'root':rig.parent.matrix_world.copy(),'bones':{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones},'wrists':{s:bpy.data.objects['BOY | WRIST_'+s].matrix_world.copy() for s in ['near','far']}}
 if f in F:
  fore.update();cache[f]={'meshes':{n:pts(bpy.data.objects[n],fore if n in fg else bpy.context.view_layer) for n in names},'cameras':{n:bpy.data.objects[n].matrix_world.copy() for n in ['V024 | CLOSE portrait','V020 | CHILD | SHOT']}}
S,rig,fore=setup(P/'native/WTSC_Boy_Full_Color_Readability_v038.blend');errors={k:0. for k in ['root_matrix','all_bone_world_matrices','wrist_world_matrices','head_hand_coat_sleeve_shoe_mesh_vertices_m','lower70percent_trouser_vertices_m','trouser_centerline_m','camera_world_matrices']};rootmoves=[]
for f in range(1,95):
 frame(S,f);src=motion[f];errors['root_matrix']=max(errors['root_matrix'],me(rig.parent.matrix_world,src['root']))
 for b in rig.pose.bones:errors['all_bone_world_matrices']=max(errors['all_bone_world_matrices'],me(rig.matrix_world@b.matrix,src['bones'][b.name]))
 for s in ['near','far']:errors['wrist_world_matrices']=max(errors['wrist_world_matrices'],me(bpy.data.objects['BOY | WRIST_'+s].matrix_world,src['wrists'][s]))
 if f in F:
  fore.update();src=cache[f]
  for n,V in src['meshes'].items():
   new=pts(bpy.data.objects[n],fore if n in fg else bpy.context.view_layer)
   if 'V024 continuous' in n:
    errors['lower70percent_trouser_vertices_m']=max(errors['lower70percent_trouser_vertices_m'],max((a-b).length for i,(a,b) in enumerate(zip(new,V)) if (i//7)/96>=.30));rootmoves.append({'frame':f,'object':n,'max_upper_root_contour_change_m':max((a-b).length for a,b in zip(new,V))})
    for row in range(97):errors['trouser_centerline_m']=max(errors['trouser_centerline_m'],(((new[row*7]+new[row*7+6])*.5)-((V[row*7]+V[row*7+6])*.5)).length)
   else:errors['head_hand_coat_sleeve_shoe_mesh_vertices_m']=max(errors['head_hand_coat_sleeve_shoe_mesh_vertices_m'],max((a-b).length for a,b in zip(new,V)))
  for n,M in src['cameras'].items():errors['camera_world_matrices']=max(errors['camera_world_matrices'],me(bpy.data.objects[n].matrix_world,M))
changedactions=[n for n,h in actions.items() if ah(bpy.data.actions[n])!=h];changedmeshes=[n for n,h in meshdata.items() if mesh_hash(bpy.data.meshes[n])!=h];changedimages=[n for n,h in images.items() if hashlib.sha256(bytes(bpy.data.images[n].packed_file.data)).hexdigest()!=h];near=bpy.data.objects['V033 | near | canonical painted shoe'];far=bpy.data.objects['V033 | far | canonical painted shoe'];newalpha=alpha_links(bpy.data.objects['PERF_BOY | original head'].material_slots[0].material)
report={'scope':'Cold full-color/root-art technical preservation; artistic acceptance remains separate','original_actions_changed':changedactions,'original_mesh_vertex_shape_UV_data_changed':changedmeshes,'original_packed_image_bytes_changed':changedimages,'intentional_geometry_field_change':'Only V036_width_scale point attribute on two trouser meshes is multiplied by a rounded/tucked root factor, ending before30percent down the drawing. Original rest coordinates, pose keys, joints, centerlines and lower70percent stay unchanged.','root_contour_changes':rootmoves,'all_original_bone_root_wrist_frame_range':[1,94],'visible_geometry_and_camera_frames':F,'errors':errors,'shoe_mesh_shared':near.data==far.data,'shoe_color_material_shared':near.material_slots[0].material==far.material_slots[0].material,'head_original_alpha_factor_wiring_unchanged':oldalpha==newalpha,'images_packed':all(bool(i.packed_file) for i in bpy.data.images if i.type=='IMAGE'),'head_color_exception':'Native UV mask supplies natural skin/hair colors. Original profile mesh, UV, alpha and packed image bytes stay fixed. A tiny static iris is shaded inside the unchanged original eye opening.','garment_scope':'Five inherited static coat poses only; no new cloth inbetweens or animation cycle.','blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode()};(P/'evidence/COLD_COLOR_AND_ROOT_PRESERVATION.json').write_text(json.dumps(report,indent=2));assert not(changedactions or changedmeshes or changedimages) and max(errors.values())<2e-5 and report['shoe_mesh_shared'] and report['shoe_color_material_shared'] and report['head_original_alpha_factor_wiring_unchanged'];print('V038_PRESERVATION_PASS',json.dumps({'errors':errors,'original_actions_changed':changedactions,'original_paint_changed':changedimages}),flush=True)
