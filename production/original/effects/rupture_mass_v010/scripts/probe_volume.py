import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'volume_properties':{p.identifier:p.description for p in bpy.types.Volume.bl_rna.properties},'domain_cache_properties':{p.identifier:p.description for p in bpy.types.FluidDomainSettings.bl_rna.properties if 'cache' in p.identifier or 'gravity' in p.identifier or 'dissolve' in p.identifier},'flow_properties':{p.identifier:p.description for p in bpy.types.FluidFlowSettings.bl_rna.properties if 'velocity' in p.identifier or 'density' in p.identifier},'source':'Installed native RNA introspection; no production scene read or mutated.'}
(P/'evidence/installed_volume_api.json').write_text(json.dumps(report,indent=2));print(json.dumps({'blender':report['blender'],'volume_fields':list(report['volume_properties']),'cache_fields':list(report['domain_cache_properties'])}),flush=True)
