import bpy,json,sys,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
base=ROOT/'locomotion/leaves_child_pose_correction_v021/native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend'
bpy.ops.wm.open_mainfile(filepath=str(base),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY'];out={'blender':bpy.app.version_string,'build':bpy.app.build_hash.decode(),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'meshes':[],'poses':[]}
for o in rig.children:
 if o.type!='MESH':continue
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
 row={'name':o.name,'role':o.get('v007_role'),'region':o.get('skin_region'),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'modifiers':[{'name':m.name,'type':m.type,'nodes':m.node_group.name if m.type=='NODES' and m.node_group else None} for m in o.modifiers],'materials':[],'uv':[[list(x.uv) for x in l.data] for l in o.data.uv_layers]}
 if o.data.shape_keys:row['shape_keys']=[{'name':k.name,'value':k.value} for k in o.data.shape_keys.key_blocks]
 for m in o.data.materials:
  row['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'attribute':n.attribute_name if n.type=='ATTRIBUTE' else None} for n in m.node_tree.nodes] if m.use_nodes else []})
 out['meshes'].append(row)
for phase,f in [('R_LOADING',3.25),('R_PASSING',9.0),('L_LOADING',17.25),('L_PASSING',25.25)]:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();row={'phase':phase,'frame':f,'bones':{b.name:{'head':list(rig.matrix_world@b.head),'tail':list(rig.matrix_world@b.tail)} for b in rig.pose.bones},'meshes':{}}
 for o in rig.children:
  if o.type!='MESH':continue
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());row['meshes'][o.name]={'vertices':[list(e.matrix_world@v.co) for v in e.data.vertices],'base_vertices':[list(v.co) for v in o.data.vertices],'triangles':[[i for i in p.vertices] for p in e.data.polygons],'loop_vertices':[l.vertex_index for l in e.data.loops],'uv':[[list(x.uv) for x in l.data] for l in e.data.uv_layers]}
 out['poses'].append(row)
(P/'evidence/native_structure_and_four_poses.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'blender':out['blender'],'base_sha256':out['base_sha256'],'meshes':[{'name':m['name'],'vertices':m['vertices'],'modifiers':m['modifiers'],'shape_keys':m.get('shape_keys'),'materials':[n['name'] for n in m['materials']]} for m in out['meshes']]}))

