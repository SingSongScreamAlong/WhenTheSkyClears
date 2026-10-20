import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import walk_common as W
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(P/'native/WTSC_Boy_Travelling_Walk_v018.blend'),link=False) as (src,dst):dst.collections=['WTSC_BOY_TRAVELLING_WALK_v018']
pack=dst.collections[0];bpy.context.scene.collection.children.link(pack);r,c=W.api.initialize_from_scene();rig=r['BOY'];S=bpy.context.scene;recipes=json.loads((P/'evidence/actual_sole_pivots.json').read_text());rows=[]
for f in [1,10.375,13.875,15.125,19,25,39.125,49]:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();rows.append(W.validate(f,rig,recipes))
S.frame_set(19);bpy.context.view_layer.update();base={o.name:W.evaluated_points(o) for o in rig.children if o.type=='MESH'};placement=bpy.data.objects['V018 | EXERCISE_PLACEMENT | move whole study'];offset=Vector((1.1,0,.3));placement.location=offset;bpy.context.view_layer.update();err=max((a+offset-b).length for o in rig.children if o.type=='MESH' for a,b in zip(base[o.name],W.evaluated_points(o)))
refs=[{'owner':o.name,'constraint':ct.name,'target':ct.target.name,'target_in_scene':ct.target.name in S.objects} for o in S.objects for ct in o.constraints if hasattr(ct,'target') and ct.target]
linked=[{'type':typ,'name':v.name,'library':v.library.filepath} for typ in ['objects','meshes','armatures','materials','images','node_groups','actions','collections','cameras','curves'] for v in getattr(bpy.data,typ) if v.library]
out={'linked_datablocks':linked,'appended_collection':pack.name,'rigs':len(r),'bones':len(rig.data.bones),'IK_chains':sum(ct.type=='IK' for b in rig.pose.bones for ct in b.constraints),'objects':len(pack.all_objects),'all_constraint_targets_linked':all(x['target_in_scene'] for x in refs),'constraint_targets':refs,'external_libraries':[l.filepath for l in bpy.data.libraries],'frame_handlers':len(bpy.app.handlers.frame_change_pre)+len(bpy.app.handlers.frame_change_post),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'samples':rows,'whole_study_placement_translation_m':list(offset),'whole_study_placement_max_mesh_error_m':err,'status':'PASS' if err<.0001 and all(x['reachable'] for row in rows for x in row['reach']) and all(x['target_in_scene'] for x in refs) and not linked else 'FAIL'}
(P/'evidence/fresh_append_validation.json').write_text(json.dumps(out,indent=2));print('V018_APPEND',out['status'],'placement_error',err,'targets',out['all_constraint_targets_linked'])
if out['status']!='PASS':raise RuntimeError('Fresh append failed')
