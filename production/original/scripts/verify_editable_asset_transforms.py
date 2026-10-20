import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector,kdtree
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
assert bpy.data.filepath.endswith('WTSC_Living_World_Editable_v011.blend')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world;world.frame_set(1);bpy.context.view_layer.update()
root=bpy.data.collections['20 | LIVING WORLD dimensional sets']
# Original unsplit dressing uses world-coordinate vertices. Resolve its parent
# transform after the new roots have evaluated, keeping the original placement.
reconciled=[]
for obj in root.all_objects:
    if obj.parent and obj.name.startswith(('LW_School','LW_VillageProps')) and not obj.hide_render:
        obj.matrix_world=Matrix.Identity(4);reconciled.append(obj.name)
bpy.context.view_layer.update()
trees={};checks=[]
for obj in root.all_objects:
    if obj.type!='MESH' or obj.hide_render or ' asset part' not in obj.data.name:continue
    source_name=obj.data.name.split(' asset part')[0];source=bpy.data.objects[source_name]
    obj['combined_source']=source_name
    if source_name not in trees:
        tree=kdtree.KDTree(len(source.data.vertices))
        for i,v in enumerate(source.data.vertices):tree.insert(source.matrix_world@v.co,i)
        tree.balance();trees[source_name]=tree
    distances=[trees[source_name].find(obj.matrix_world@p.co)[2] for p in obj.data.vertices]
    error=max(distances,default=0);assert error<.0001,(obj.name,error)
    checks.append({'object':obj.name,'source':source_name,'max_world_distance_m':error})
for obj in root.all_objects:
    if obj.parent and obj.name.startswith(('LW_School','LW_VillageProps')) and not obj.hide_render:
        assert obj.matrix_world.translation.length<.0001,(obj.name,list(obj.matrix_world.translation))
curve_checks=[]
for obj in root.all_objects:
    if obj.type!='CURVE' or obj.hide_render or 'continuous branches' not in obj.name:continue
    region=obj.name.split('|')[1].strip();source=bpy.data.objects['LWC_'+region+'_OrganicTrees']
    key='curve '+region
    if key not in trees:
        points=[Vector(p.co[:3]) for s in source.data.splines for p in s.points];tree=kdtree.KDTree(len(points))
        for i,p in enumerate(points):tree.insert(source.matrix_world@p,i)
        tree.balance();trees[key]=tree
    error=max(trees[key].find(obj.matrix_world@Vector(p.co[:3]))[2] for s in obj.data.splines for p in s.points)
    assert error<.0001,(obj.name,error);curve_checks.append({'object':obj.name,'max_world_distance_m':error})
functional=[]
for name in ['ASSET | Bakery | Village','ASSET | School building','ASSET | Tree | Village | -9.00']:
    parent=bpy.data.objects[name];child=next(c for c in parent.children if c.type in ['MESH','CURVE'])
    local=child.data.vertices[0].co if child.type=='MESH' else Vector(child.data.splines[0].points[0].co[:3])
    original=parent.location.copy();before=child.matrix_world@local
    parent.location.x+=.25;bpy.context.view_layer.update();after=child.matrix_world@local
    parent.location=original;bpy.context.view_layer.update()
    assert abs((after-before).x-.25)<.0001,(name,list(after-before))
    assert ((child.matrix_world@local)-before).length<.0001
    functional.append({'asset':name,'tested_translation_m':.25,'child_translation_m':list(after-before),'restored':True})
world.frame_set(1)
world['asset_transform_verification']='Native world-space nearest-point comparison within 0.1 mm; root movement checked on bakery, school and tree, then restored.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_Living_World_Editable_v011.blend'))
report={'file':bpy.data.filepath,'mesh_parts_checked':len(checks),'curve_assets_checked':len(curve_checks),'tolerance_m':.0001,'mesh_checks':checks,'curve_checks':curve_checks,'functional_checks':functional,'world_coordinate_dressing_reconciled':reconciled}
(ROOT/'notes/living_world/asset_transform_verification_v011.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['mesh_checks','curve_checks','world_coordinate_dressing_reconciled']}))
