"""Run in isolated UE5.8 commandlet. Import actual room mesh/surfaces and save native map."""
import unreal, pathlib, json, datetime
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
exec((ROOT/'Scripts/author_content.py').read_text().split('\ntry:')[0])
SOURCE=ROOT/'SourceAssets/AuthoredWestRoom'
recipe=json.loads((SOURCE/'WestRoom_Recipe.json').read_text())
dest='/Game/WTSC/ArtStudy'
textures={}
for p in sorted(SOURCE.glob('*.png')):
    imported=import_file(p,dest+'/Surfaces')
    textures[p.stem]=next(a for a in imported if isinstance(a,unreal.Texture2D))
objects=import_file(SOURCE/'WestRoom_Assembly.gltf',dest+'/Architecture')
meshes=[x for x in objects if isinstance(x,unreal.StaticMesh)]
if not meshes:
    meshes=[unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets(dest+'/Architecture',recursive=True,include_folder=False) if isinstance(unreal.load_asset(p),unreal.StaticMesh)]
assert len(meshes)==1, 'Expected one multi-material authored room assembly'
mesh=meshes[0]

def newmat(name):
    m=unreal.load_asset(dest+'/Materials/'+name)
    if not m:m=tools.create_asset(name,dest+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m)
    m.set_editor_property('two_sided',True)
    return m
def constant(m,value,x=-300,y=250):
    c=lib.create_material_expression(m,unreal.MaterialExpressionConstant,x,y);c.set_editor_property('r',value);return c
def vector(m,value,x=-300,y=0):
    c=lib.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,x,y);c.set_editor_property('constant',unreal.LinearColor(*value,1));return c
def checked_connect(a,out,b,pin):
    ok=lib.connect_material_expressions(a,out,b,pin)
    if not ok:raise RuntimeError('Material pin connection failed: '+b.get_class().get_name()+' input '+repr(pin))
    return ok
def finish(m,base):
    # A restrained paint-preserving ambient term avoids pure-black albedo in this no-GI prototype.
    # It is a stylized surface choice, not an emissive light source or baked beauty image.
    ambient=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,100,250)
    checked_connect(base,'RGB' if isinstance(base,unreal.MaterialExpressionTextureSample) else '',ambient,'A')
    checked_connect(constant(m,.065,-100,400),'',ambient,'B')
    lib.connect_material_property(ambient,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    lib.connect_material_property(constant(m,.94),'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.connect_material_property(constant(m,.075,-300,350),'',unreal.MaterialProperty.MP_SPECULAR)
    lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);receipt['materials'].append(m.get_path_name());return m

surface_map={'LimePlaster':'WestRoom_Plaster','Timber':'WestRoom_Timber','TimberEdge':'WestRoom_Timber','EndGrain':'WestRoom_Timber','FloorOak':'WestRoom_Timber','FloorEdge':'WestRoom_Timber','Cloth':'WestRoom_Cloth','Rug':'WestRoom_Rug','Paper':'WestRoom_Note'}
materials={}
for key,color in recipe['palette'].items():
    m=newmat('M_WestRoom_'+key)
    if key in surface_map:
        sample=lib.create_material_expression(m,unreal.MaterialExpressionTextureSample,-600,0);sample.set_editor_property('texture',textures[surface_map[key]])
        if key in ['EndGrain','TimberEdge','FloorEdge']:
            gain=1.16 if key!='EndGrain' else .78
            mult=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-200,0);checked_connect(sample,'RGB',mult,'A');checked_connect(constant(m,gain,-500,200),'',mult,'B');out=mult
        else:out=sample
        lib.connect_material_property(out,'RGB' if out==sample else '',unreal.MaterialProperty.MP_BASE_COLOR)
    else:
        out=vector(m,color[:3]);lib.connect_material_property(out,'',unreal.MaterialProperty.MP_BASE_COLOR)
    materials[key]=finish(m,out)
slots=mesh.get_editor_property('static_materials')
for index,slot in enumerate(slots):
    key=str(slot.material_slot_name).removeprefix('AR_')
    assert key in materials, (index,str(slot.material_slot_name))
    mesh.set_material(index,materials[key])
unreal.EditorAssetLibrary.save_loaded_asset(mesh)

level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);assert level.load_level('/Game/Maps/ShelterDawn')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();stage=next(a for a in actors if a.get_class().get_name()=='WTSCStage')
props=dict(stage.get_editor_property('prop_meshes'));assert len(props)==7 or 'WestRoomAssembly' in [str(k) for k in props]
old_keys=[str(k) for k in props if str(k)!='WestRoomAssembly'];assert len(old_keys)==7
stage_mats=dict(stage.get_editor_property('materials'))
graded=[]
for key in old_keys:
    all_assets=[unreal.load_asset(p) for p in unreal.EditorAssetLibrary.list_assets('/Game/WTSC/Props/'+key,recursive=True,include_folder=False)]
    diffuse=next(x for x in all_assets if isinstance(x,unreal.Texture2D) and '_diff' in x.get_name().lower())
    normal=next((x for x in all_assets if isinstance(x,unreal.Texture2D) and '_nor' in x.get_name().lower()),None)
    m=newmat('M_RoomProp_'+key)
    tex=lib.create_material_expression(m,unreal.MaterialExpressionTextureSample,-800,0);tex.set_editor_property('texture',diffuse)
    desat=lib.create_material_expression(m,unreal.MaterialExpressionDesaturation,-550,0);checked_connect(tex,'RGB',desat,'');checked_connect(constant(m,.30,-800,200),'',desat,'Fraction')
    tint=vector(m,(.82,.88,.84),-550,220)
    mul=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-300,0);checked_connect(desat,'',mul,'A');checked_connect(tint,'',mul,'B')
    lift=lib.create_material_expression(m,unreal.MaterialExpressionAdd,-100,0);checked_connect(mul,'',lift,'A');checked_connect(vector(m,(.018,.024,.022),-300,300),'',lift,'B');lib.connect_material_property(lift,'',unreal.MaterialProperty.MP_BASE_COLOR)
    if normal:
        n=lib.create_material_expression(m,unreal.MaterialExpressionTextureSample,-800,500);n.set_editor_property('texture',normal);n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        strength=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-500,500);checked_connect(n,'RGB',strength,'A');checked_connect(vector(m,(.45,.45,1),-750,700),'',strength,'B')
        norm=lib.create_material_expression(m,unreal.MaterialExpressionNormalize,-250,500);checked_connect(strength,'',norm,'');lib.connect_material_property(norm,'',unreal.MaterialProperty.MP_NORMAL)
    stage_mats['RoomProp_'+key]=finish(m,lift)
    graded.append({'prop':key,'diffuse':diffuse.get_path_name(),'normal':normal.get_path_name() if normal else None,'source_texture_pixels_unchanged':True,'material':m.get_path_name(),'scope':'Room placements only; shop/storage originals retain their publisher materials'})
props['WestRoomAssembly']=mesh;stage.set_editor_property('prop_meshes',props);stage.set_editor_property('materials',stage_mats);stage.rebuild_stage();assert level.save_current_level()
unreal.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False,recursive=True)
b=mesh.get_bounding_box()
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':unreal.SystemLibrary.get_engine_version(),'level_saved':True,'room_mesh':mesh.get_path_name(),'room_material_slots':len(slots),'room_bounds_min':[b.min.x,b.min.y,b.min.z],'room_bounds_max':[b.max.x,b.max.y,b.max.z],'source_geometry_stats':recipe['geometry_stats'],'original_prop_keys':old_keys,'prop_references':{str(k):v.get_path_name() for k,v in props.items()},'room_prop_materials':graded,'surface_provenance':recipe['surface_provenance'],'failures':receipt['failures'],'imports':receipt['imports'],'materials':receipt['materials']}
(ROOT/'Evidence/WestRoomNativeImport.json').write_text(json.dumps(record,indent=2),encoding='utf8')
assert not receipt['failures']
unreal.log('WTSC_WEST_ROOM_NATIVE '+json.dumps({'mesh':record['room_mesh'],'materials':len(slots),'original_props':len(old_keys),'bounds_min':record['room_bounds_min'],'bounds_max':record['room_bounds_max']}))
