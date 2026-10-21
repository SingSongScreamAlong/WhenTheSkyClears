import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv011 | compact brief impact low dust'];bpy.context.window.scene=s;o=bpy.data.objects['FXv011 | faint low residual dust only'];v=o.data;old=v.filepath
v.filepath='//../cache/data/fluid_data_0001.vdb';v.is_sequence=True;v.frame_start=1;v.frame_duration=100000
root=bpy.data.objects['FXv011 | fixed impact anchor and controls']
for prop in ['hide_render','hide_viewport']:
    f=o.driver_add(prop);f.driver.type='SCRIPTED';f.driver.expression='t<0 or t>22';var=f.driver.variables.new();var.name='t';var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["age"]'
v.grids.unload();s.frame_set(19);s.frame_set(20);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());ev.data.grids.load();loaded=ev.data.grids.frame_filepath;assert loaded.endswith('fluid_data_0020.vdb') and Path(loaded).is_file(),(old,loaded,ev.data.grids.error_message)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Compact_Impact_Proof_v011.blend'),compress=True)
(P/'evidence/cache_path_repair.json').write_text(json.dumps({'old_path':old,'correct_path':v.filepath,'actual_loaded_frame20':loaded,'playback_window':100000,'actual_cache_files':30,'visibility_age_range':[0,22],'reason':'Correct the new-folder relative path, and keep a long playback window so native frame_offset works after the original30-frame global interval. Visibility and density still end at age22.','artistic_parameters_changed':False},indent=2));print('COMPACT_CACHE_PATH_VERIFIED',loaded,flush=True)
