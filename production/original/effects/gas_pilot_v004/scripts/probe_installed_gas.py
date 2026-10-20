import bpy,json,sys,os
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add();ob=bpy.context.object;mod=ob.modifiers.new('Probe installed native fluid','FLUID');mod.fluid_type='DOMAIN';bpy.context.view_layer.update();d=mod.domain_settings;d.domain_type='GAS'
def describe(settings):
    values={}
    for prop in settings.bl_rna.properties:
        if prop.identifier=='rna_type':continue
        info={'type':prop.type,'readonly':prop.is_readonly}
        if prop.type=='ENUM':info['enum']=[item.identifier for item in prop.enum_items]
        if prop.type in ['INT','FLOAT']:info.update({'min':prop.hard_min,'max':prop.hard_max,'default':str(prop.default)})
        try:
            value=getattr(settings,prop.identifier)
            if prop.type in ['BOOLEAN','INT','FLOAT','STRING','ENUM']:info['current']=list(value) if prop.is_array else value
        except Exception:pass
        values[prop.identifier]=info
    return values
domain=describe(d)
bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4);flow=bpy.context.object;fm=flow.modifiers.new('Probe flow','FLUID');fm.fluid_type='FLOW';bpy.context.view_layer.update();fs=fm.flow_settings
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'build_options':{k:getattr(bpy.app.build_options,k) for k in dir(bpy.app.build_options) if not k.startswith('_') and isinstance(getattr(bpy.app.build_options,k),(str,bool,int,float))},'fluid_ops':[v for v in dir(bpy.ops.fluid) if not v.startswith('_')],'domain':domain,'flow':describe(fs),'python':sys.version,'note':'Constructed actual native GAS domain/flow modifiers. No bake performed by this probe; installed solver execution still requires pilot.'}
(P/'evidence/installed_gas_probe.json').write_text(json.dumps(report,indent=2));print('GAS_SUPPORT_PROBED',json.dumps({'blender':report['blender'],'build_options':report['build_options'],'operators':report['fluid_ops'],'domain_properties':len(domain),'flow_properties':len(report['flow'])}),flush=True)
