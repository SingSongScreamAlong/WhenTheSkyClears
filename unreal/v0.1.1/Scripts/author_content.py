"""Run inside this project's Unreal 5.8 Editor only after resource release.

Creates native imports, editable material resources, and the cutaway level.
Writes exact native asset paths and failures. No silent replacement of failed imports.
"""
import unreal, json, pathlib, hashlib, datetime

ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
assert (ROOT/'WTSC_Survival.uproject').is_file(), 'Wrong project: refuse to author another production'
EVIDENCE=ROOT/'Evidence';EVIDENCE.mkdir(exist_ok=True)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':unreal.SystemLibrary.get_engine_version(),'project':str(ROOT),'imports':[],'failures':[],'materials':[],'level_saved':False}
tools=unreal.AssetToolsHelpers.get_asset_tools()
lib=unreal.MaterialEditingLibrary

def import_file(src,destination):
    task=unreal.AssetImportTask()
    for key,val in {'filename':str(src),'destination_path':destination,'automated':True,'save':True,'replace_existing':True,'async_':False}.items():task.set_editor_property(key,val)
    tools.import_asset_tasks([task])
    paths=list(task.get_editor_property('imported_object_paths'))
    receipt['imports'].append({'source':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'native_paths':paths})
    if not paths:receipt['failures'].append({'source':str(src),'reason':'Import returned no native paths'})
    return [unreal.load_asset(p) for p in paths if unreal.load_asset(p)]

def material(name,color,painted=True):
    m=unreal.load_asset('/Game/WTSC/Materials/'+name)
    if not m:m=tools.create_asset(name,'/Game/WTSC/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m)
    tint=lib.create_material_expression(m,unreal.MaterialExpressionVectorParameter,-500,0)
    tint.set_editor_property('parameter_name','Tint');tint.set_editor_property('default_value',unreal.LinearColor(*color))
    if painted:
        pos=lib.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-900,220)
        noise=lib.create_material_expression(m,unreal.MaterialExpressionNoise,-650,220)
        noise.set_editor_property('scale',.018);noise.set_editor_property('levels',2)
        noise.set_editor_property('output_min',.82);noise.set_editor_property('output_max',1.02)
        lib.connect_material_expressions(pos,'',noise,'Position')
        multiply=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-250,0)
        lib.connect_material_expressions(tint,'',multiply,'A');lib.connect_material_expressions(noise,'',multiply,'B')
        lib.connect_material_property(multiply,'',unreal.MaterialProperty.MP_BASE_COLOR)
    elif name in ('M_Sky','M_Lamp'):
        m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
        lib.connect_material_property(tint,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:lib.connect_material_property(tint,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-200,200);rough.set_editor_property('r',.9)
    lib.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    receipt['materials'].append(m.get_path_name());return m

def card_material(name,texture,rect=(0,0,1,1),tint=(.85,.9,.91,1)):
    m=unreal.load_asset('/Game/WTSC/Materials/'+name)
    if not m:m=tools.create_asset(name,'/Game/WTSC/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(m)
    m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property('two_sided',True)
    m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
    sample=lib.create_material_expression(m,unreal.MaterialExpressionTextureSample,-200,0);sample.set_editor_property('texture',texture)
    uv=lib.create_material_expression(m,unreal.MaterialExpressionTextureCoordinate,-850,0)
    scale=lib.create_material_expression(m,unreal.MaterialExpressionConstant2Vector,-850,180);scale.set_editor_property('r',rect[2]);scale.set_editor_property('g',rect[3])
    mul=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,-650,0)
    lib.connect_material_expressions(uv,'',mul,'A');lib.connect_material_expressions(scale,'',mul,'B')
    offset=lib.create_material_expression(m,unreal.MaterialExpressionConstant2Vector,-650,180);offset.set_editor_property('r',rect[0]);offset.set_editor_property('g',rect[1])
    add=lib.create_material_expression(m,unreal.MaterialExpressionAdd,-450,0)
    lib.connect_material_expressions(mul,'',add,'A');lib.connect_material_expressions(offset,'',add,'B');lib.connect_material_expressions(add,'',sample,'UVs')
    color=lib.create_material_expression(m,unreal.MaterialExpressionConstant4Vector,-200,220);color.set_editor_property('constant',unreal.LinearColor(*tint))
    colored=lib.create_material_expression(m,unreal.MaterialExpressionMultiply,0,0);lib.connect_material_expressions(sample,'RGB',colored,'A');lib.connect_material_expressions(color,'RGB',colored,'B')
    lib.connect_material_property(colored,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);lib.connect_material_property(sample,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
    lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);receipt['materials'].append(m.get_path_name());return m

try:
    props={}
    for folder in sorted((ROOT/'SourceAssets/DerivedStaticModels').iterdir()):
        src=next(folder.glob('*.gltf'))
        imported=import_file(src,'/Game/WTSC/Props/'+folder.name)
        meshes=[a for a in imported if isinstance(a,unreal.StaticMesh)]
        if not meshes:
            assets=unreal.EditorAssetLibrary.list_assets('/Game/WTSC/Props/'+folder.name,recursive=True,include_folder=False)
            meshes=[unreal.load_asset(p) for p in assets if isinstance(unreal.load_asset(p),unreal.StaticMesh)]
        if len(meshes)==1:props[folder.name]=meshes[0]
        elif len(meshes)>1:receipt['failures'].append({'source':str(src),'reason':'Expected one complete baked mesh; multiple native meshes require review before placement'})
        else:receipt['failures'].append({'source':str(src),'reason':'No StaticMesh found after import'})
    textures={}
    for src in sorted((ROOT/'SourceAssets/EstablishedWTSC').glob('*.png')):
        textures[src.stem]=next(a for a in import_file(src,'/Game/WTSC/EstablishedArt') if isinstance(a,unreal.Texture2D))
    palette={'Sky':(.025,.055,.065,1),'Stone':(.18,.20,.19,1),'Road':(.10,.13,.14,1),'Plaster':(.40,.39,.32,1),'WarmPlaster':(.42,.37,.27,1),'FadedBlue':(.13,.23,.25,1),'Wood':(.24,.16,.09,1),'OldWood':(.24,.23,.17,1),'DarkWood':(.065,.055,.04,1),'Brick':(.26,.17,.12,1),'Metal':(.065,.085,.09,1),'Lamp':(1,.63,.2,1),'Cloth':(.26,.25,.20,1),'Dark':(.018,.035,.037,1),'ShopPlaster':(.24,.32,.32,1)}
    mats={k:material('M_'+k,c,k not in ('Sky','Lamp','Dark')) for k,c in palette.items()}
    mats['Backdrop']=card_material('M_Backdrop',textures['Village_Empty_v001'],tint=(.035,.07,.085,1))
    atlas=textures['boy_atlas']
    for name,box in {'Head':(0,0,470,530),'Coat':(490,0,365,605),'Arm':(105,615,240,610),'Leg':(500,595,325,675),'Boot':(820,835,455,395)}.items():
        card_material('M_Boy'+name,atlas,tuple(x/1280 for x in box))
    card_material('M_GirlProfile',textures['girl_profile'])
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level.new_level('/Game/Maps/ShelterDawn'), 'Could not create separate map'
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cls=unreal.load_class(None,'/Script/WTSCSurvival.WTSCStage');assert cls
    stage=actors.spawn_actor_from_class(cls,unreal.Vector(0,0,0))
    stage.set_actor_label('WTSC_Editable_CutawayShelter_And_Shop')
    stage.set_editor_property('prop_meshes',props);stage.set_editor_property('materials',mats);stage.rebuild_stage()
    start=actors.spawn_actor_from_class(unreal.PlayerStart,unreal.Vector(100,0,70));start.set_actor_label('WTSC_StartInsideShelter')
    assert level.save_current_level(), 'Map save failed'
    unreal.EditorAssetLibrary.save_directory('/Game/WTSC',only_if_is_dirty=False,recursive=True)
    receipt['prop_meshes']={k:v.get_path_name() for k,v in props.items()};receipt['level_saved']=True
except Exception as e:
    receipt['failures'].append({'stage':'author_content','reason':repr(e)});raise
finally:
    (EVIDENCE/'NativeImportReceipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
