import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
bpy.ops.wm.open_mainfile(filepath=str(R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060']
n=m.compositing_node_group.nodes.new('CompositorNodeCryptomatteV2')
report={'rna':[{'id':p.identifier,'type':p.type,'readonly':p.is_readonly} for p in n.bl_rna.properties],
 'values':{k:str(getattr(n,k,None)) for k in ['source','scene','layer_name','matte_id']},
 'inputs':[x.name for x in n.inputs], 'outputs':[x.name for x in n.outputs],
 'view_layer':w.view_layers[0].name,
 'pass_properties':[p.identifier for p in w.view_layers[0].bl_rna.properties if 'crypto' in p.identifier]}
a=m.compositing_node_group.nodes.new('CompositorNodeAlphaOver')
report['alpha_over_inputs']=[{'name':x.name,'identifier':x.identifier,'type':x.type,'value':str(getattr(x,'default_value',None))} for x in a.inputs]
report['alpha_over_outputs']=[x.name for x in a.outputs]
cam=next(o for o in w.objects if o.type=='CAMERA' and o.name.startswith('v032 | Camera follows shared pair center'))
report['old_camera_drivers']=[{'expression':f.driver.expression,'vars':[{'name':v.name,'id':v.targets[0].id.name if v.targets[0].id else None,'type':v.type,'space':v.targets[0].transform_space} for v in f.driver.variables]} for f in cam.animation_data.drivers]
(O/'evidence/MATTE_API_PROBE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
