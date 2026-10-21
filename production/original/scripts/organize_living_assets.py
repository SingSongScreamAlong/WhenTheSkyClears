"""Separate authored set pieces for local editing without changing world positions.
The movie continues to render immutable v010. This writes a new delivery source.
"""
import bpy,json,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
assert bpy.data.filepath.endswith('WTSC_Living_World_v010.blend')
recipe=json.loads((ROOT/'work/living_world_meshes/v008/assembly.json').read_text())
root=bpy.data.collections['20 | LIVING WORLD dimensional sets']
hidden=bpy.data.collections.new('LW | Hidden combined source meshes');root.children.link(hidden);hidden.hide_render=True;hidden.hide_viewport=True
assets={};origins={};asset_regions={};split_report=[]

def asset(key,region=None,origin=None):
    if key in assets:return assets[key]
    if '|' in key:
        kind,region,x,y=key.split('|');origin=(float(x),float(y),0)
        label=f'{kind} | {region} | {float(x):.2f}'
        if kind=='House' and float(x)==2.0:label='Bakery | Village'
    else:label=key
    obj=bpy.data.objects.new('ASSET | '+label,None);obj.empty_display_type='PLAIN_AXES';obj.empty_display_size=.65;obj.location=origin
    bpy.data.collections['LW | '+region].objects.link(obj)
    obj['use']='Move, rotate or scale this root to edit the complete set piece.'
    assets[key]=obj;origins[key]=Vector(origin);asset_regions[key]=region
    bpy.context.view_layer.update()
    return obj

def hide_source(obj):
    obj.hide_render=True;obj.hide_viewport=True
    for col in list(obj.users_collection):col.objects.unlink(obj)
    hidden.objects.link(obj)
    obj['status']='Preserved combined source; replaced by individual asset parts'

def copy_drivers(old_data,new_data):
    if not old_data.animation_data:return
    for fc in old_data.animation_data.drivers:
        newfc=new_data.driver_add(fc.data_path,fc.array_index) if fc.array_index else new_data.driver_add(fc.data_path)
        newfc.driver.type=fc.driver.type;newfc.driver.expression=fc.driver.expression
        assert not fc.driver.variables,'Unexpected dependency needs explicit mapping'

for entry in recipe['entries']:
    obj=bpy.data.objects[entry['name']]
    owners=entry.get('face_assets',[])
    if obj.hide_render or not any(owners):continue
    mesh=obj.data;assert len(owners)==len(mesh.polygons),(obj.name,len(owners),len(mesh.polygons))
    expected=json.loads(Path(entry['payload']).read_text())
    assert len(expected['vertices'])==len(mesh.vertices)
    delta=max((mesh.vertices[i].co-Vector(p)).length for i,p in enumerate(expected['vertices']))
    assert delta<.00002,(obj.name,delta)
    faces_by_owner=defaultdict(list)
    for face,owner in zip(mesh.polygons,owners):faces_by_owner[owner].append(face.index)
    for owner,indices in faces_by_owner.items():
        if owner:
            parent=asset(owner);origin=origins[owner]
        else:parent=None;origin=Vector((0,0,0))
        vertex_ids=sorted({vi for fi in indices for vi in mesh.polygons[fi].vertices});remap={old:i for i,old in enumerate(vertex_ids)}
        verts=[tuple(mesh.vertices[i].co-origin) for i in vertex_ids]
        faces=[tuple(remap[i] for i in mesh.polygons[fi].vertices) for fi in indices]
        data=bpy.data.meshes.new(obj.name+' asset part');data.from_pydata(verts,[],faces);data.update()
        for mat in mesh.materials:data.materials.append(mat)
        new=obj.copy();new.data=data;new.name=(parent.name[8:] if parent else entry['region']+' general')+' | '+entry['material']
        new.hide_render=False;new.hide_viewport=False;new.parent=parent;new.location=(0,0,0)
        bpy.data.collections['LW | '+entry['region']].objects.link(new)
        for newface,fi in zip(data.polygons,indices):
            newface.use_smooth=mesh.polygons[fi].use_smooth;newface.material_index=mesh.polygons[fi].material_index
        for layer in mesh.uv_layers:
            uv=data.uv_layers.new(name=layer.name)
            for nf,fi in zip(data.polygons,indices):
                for nl,ol in zip(nf.loop_indices,mesh.polygons[fi].loop_indices):uv.data[nl].uv=layer.data[ol].uv
        for oldattr in mesh.color_attributes:
            assert oldattr.domain=='CORNER'
            attr=data.color_attributes.new(name=oldattr.name,type=oldattr.data_type,domain='CORNER')
            for nf,fi in zip(data.polygons,indices):
                for nl,ol in zip(nf.loop_indices,mesh.polygons[fi].loop_indices):attr.data[nl].color=oldattr.data[ol].color
        if mesh.shape_keys:
            oldkeys=mesh.shape_keys
            for oldkey in oldkeys.key_blocks:
                key=new.shape_key_add(name=oldkey.name)
                for newpoint,vi in zip(key.data,vertex_ids):newpoint.co=oldkey.data[vi].co-origin
                key.value=oldkey.value;key.slider_min=oldkey.slider_min;key.slider_max=oldkey.slider_max
            copy_drivers(oldkeys,data.shape_keys)
        new['asset_root']=parent.name if parent else 'General regional dressing'
        # World-space data must remain the same after the new local transform.
        for ni,vi in enumerate(vertex_ids):
            assert (data.vertices[ni].co+origin-mesh.vertices[vi].co).length<.00002
    split_report.append({'source':obj.name,'parts':len(faces_by_owner),'max_input_delta':delta})
    hide_source(obj)

# Split each continuous tree curve into its own tree asset with attached foliage.
for region in ['Village','Departure','Woods','Battlefield']:
    old=bpy.data.objects['LWC_'+region+'_OrganicTrees'];curve=old.data
    assert len(curve.splines)%29==0
    offset=0
    for ti in range(len(curve.splines)//29):
        group=list(curve.splines)[ti*29:(ti+1)*29]
        first=group[0].points[0].co
        candidates=[key for key in assets if key.startswith('Tree|'+region+'|')]
        if candidates:key=min(candidates,key=lambda k:(origins[k].x-first.x)**2+(origins[k].y-first.y)**2)
        else:key=f'Tree|{region}|{first.x}|{first.y}'
        if key in assets and (origins[key]-Vector((first.x,first.y,0))).length>.01:key=f'Tree|{region}|{first.x}|{first.y}'
        parent=asset(key);origin=origins[key]
        data=bpy.data.curves.new(parent.name+' branches','CURVE');data.dimensions='3D';data.bevel_depth=curve.bevel_depth;data.bevel_resolution=curve.bevel_resolution;data.resolution_u=curve.resolution_u;data.use_fill_caps=curve.use_fill_caps;data.twist_mode=curve.twist_mode
        for mat in curve.materials:data.materials.append(mat)
        count=0
        for old_spline in group:
            spline=data.splines.new('POLY');spline.points.add(len(old_spline.points)-1)
            for p,q in zip(spline.points,old_spline.points):p.co=(*tuple(Vector(q.co[:3])-origin),q.co.w);p.radius=q.radius;p.tilt=q.tilt
            spline.use_cyclic_u=old_spline.use_cyclic_u;count+=len(old_spline.points)
        obj=bpy.data.objects.new(parent.name[8:]+' | continuous branches',data);bpy.data.collections['LW | '+region].objects.link(obj);obj.parent=parent
        for oldkey in curve.shape_keys.key_blocks:
            keyblock=obj.shape_key_add(name=oldkey.name)
            assert len(keyblock.data)==count
            for newpoint,oldpoint in zip(keyblock.data,oldkey.data[offset:offset+count]):newpoint.co=oldpoint.co-origin
            keyblock.value=oldkey.value
        copy_drivers(curve.shape_keys,data.shape_keys)
        offset+=count
    assert offset==len(curve.shape_keys.key_blocks[0].data)
    hide_source(old)

# The school was authored as one distinct location; parent its original pieces.
school=asset('School building','School',(42,8.8,0))
for obj in list(bpy.data.collections['LW | School'].objects):
    if obj==school or obj.parent or obj.hide_render:continue
    matrix=obj.matrix_world.copy();obj.parent=school;obj.matrix_world=matrix

# Details that belong to one tent move with that tent; village cart/barrels group
# remains separately editable rather than being joined to house walls.
for entry in json.loads((ROOT/'work/living_world_details/details_recipe.json').read_text())['mesh_entries']:
    obj=bpy.data.objects[entry['name']]
    if entry['region']=='VillageProps':
        parent=asset('Village cart and barrels','Village',(-4.75,5.8,0));matrix=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=matrix

world['asset_editing']='Individual building, tree, tent and ruin roots. Select an ASSET root to move the complete piece; child materials, native geometry and wind keys remain editable.'
world['delivery_source_note']='v011 reorganizes native v010 geometry into asset roots, preserving world coordinates, materials and animation expressions. The complete review movie renders immutable v010; v010 remains available as its exact source.'
world.frame_set(1);bpy.context.view_layer.update()
target=ROOT/'shots/world/WTSC_Living_World_Editable_v011.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(target))
report={'source':str(target),'movie_render_source':'shots/world/WTSC_Living_World_v010.blend','asset_roots':len(assets),'roots':[o.name for o in assets.values()],'split_mesh_groups':split_report,'geometry_tolerance_m':.00002,'note':'World geometry, UVs, colors and shape key coordinates preserved. Per-object foliage sorting can differ after regrouping; final artist review remains pending.'}
(ROOT/'notes/living_world/editable_assets_v011.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'saved':str(target),'asset_roots':len(assets),'split_mesh_groups':len(split_report)}))
