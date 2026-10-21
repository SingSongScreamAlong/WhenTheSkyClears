import unreal, pathlib, json, datetime
root=pathlib.Path(unreal.Paths.project_dir()).resolve()
assert (root/'WTSC_Survival.uproject').is_file()
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Maps/ShelterDawn')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
stage=next(a for a in actors if a.get_class().get_name()=='WTSCStage')
stage.rebuild_stage()
backdrop=unreal.load_asset('/Game/WTSC/Materials/M_Backdrop')
ml=unreal.MaterialEditingLibrary;ml.delete_all_material_expressions(backdrop)
tex=ml.create_material_expression(backdrop,unreal.MaterialExpressionTextureSample,-500,0)
tex.set_editor_property('texture',unreal.load_asset('/Game/WTSC/EstablishedArt/Village_Empty_v001'))
tint=ml.create_material_expression(backdrop,unreal.MaterialExpressionVectorParameter,-500,200)
tint.set_editor_property('parameter_name','DistantTint');tint.set_editor_property('default_value',unreal.LinearColor(.035,.07,.085,1))
mul=ml.create_material_expression(backdrop,unreal.MaterialExpressionMultiply,-200,0)
ml.connect_material_expressions(tex,'RGB',mul,'A');ml.connect_material_expressions(tint,'',mul,'B')
ml.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);ml.connect_material_property(tex,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
ml.recompile_material(backdrop);unreal.EditorAssetLibrary.save_loaded_asset(backdrop)
assert level.save_current_level()
meshes=stage.get_editor_property('prop_meshes');assert len(meshes)==7
assets=[]
for path in unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False):
    obj=unreal.load_asset(path)
    if obj:assets.append({'path':obj.get_path_name(),'class':obj.get_class().get_name()})
scale=stage.get_actor_scale3d()
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':unreal.SystemLibrary.get_engine_version(),'level':'/Game/Maps/ShelterDawn','stage_scale':[scale.x,scale.y,scale.z],'map_reopened_and_saved':True,'stage_components':len(stage.get_components_by_class(unreal.ActorComponent)),'prop_meshes':{str(k):v.get_path_name() for k,v in meshes.items()},'assets':assets}
(root/'Evidence/NativeSceneReadback.json').write_text(json.dumps(record,indent=2),encoding='utf8')
unreal.log('WTSC_NATIVE_READBACK '+str(len(assets))+' assets; seven prop references; map reopened and saved')
