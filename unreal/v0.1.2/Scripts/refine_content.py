import unreal, pathlib, json
ROOT=pathlib.Path(unreal.Paths.project_dir()).resolve()
exec((ROOT/'Scripts/author_content.py').read_text().split('\ntry:')[0])
palette={'Sky':(.025,.055,.065,1),'Stone':(.23,.25,.23,1),'Road':(.13,.16,.16,1),'Plaster':(.40,.39,.34,1),'WarmPlaster':(.42,.39,.31,1),'FadedBlue':(.19,.27,.28,1),'Wood':(.29,.23,.16,1),'OldWood':(.29,.29,.24,1),'DarkWood':(.13,.12,.10,1),'Brick':(.29,.21,.16,1),'Metal':(.08,.10,.10,1),'Lamp':(1,.63,.2,1),'Cloth':(.30,.31,.28,1),'Dark':(.018,.035,.037,1),'ShopPlaster':(.29,.33,.32,1),'Ochre':(.63,.48,.24,1),'Stain':(.27,.29,.25,1),'GirlDress':(.23,.29,.32,1),'Bundle':(.45,.36,.22,1)}
mats={k:material('M_'+k,c,k not in ('Sky','Lamp','Dark')) for k,c in palette.items()}
mats['Backdrop']=unreal.load_asset('/Game/WTSC/Materials/M_Backdrop')
atlas=unreal.load_asset('/Game/WTSC/EstablishedArt/boy_atlas')
for name,box in {'Thigh':(500,595,325,355),'Shin':(500,915,325,355),'Sleeve':(875,0,330,550),'Forearm':(120,615,155,375),'Hand':(155,965,175,230)}.items():
    card_material('M_Boy'+name,atlas,tuple(x/1280 for x in box))
girl=unreal.load_asset('/Game/WTSC/EstablishedArt/girl_profile')
card_material('M_GirlBlouse',girl,(.35,.68,.47,.32),(.78,.86,.92,1))
card_material('M_GirlSleeve',atlas,(875/1280,0,330/1280,550/1280),(.62,.69,.76,1))
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert level.load_level('/Game/Maps/ShelterDawn')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
stage=next(a for a in actors if a.get_class().get_name()=='WTSCStage')
stage.set_editor_property('materials',mats);stage.rebuild_stage()
assert level.save_current_level()
unreal.EditorAssetLibrary.save_directory('/Game/WTSC',only_if_is_dirty=False,recursive=True)
receipt['level_saved']=True;receipt['operation']='v0.1.1 native material and stage refinement; retained all seven imported meshes'
(ROOT/'Evidence/NativeRefinementReceipt.json').write_text(json.dumps(receipt,indent=2))
exec((ROOT/'Scripts/check_native_scene.py').read_text())
