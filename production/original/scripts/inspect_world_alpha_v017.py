import bpy,json
s=bpy.context.scene
for f in [1,241,481,721]:
 s.frame_set(f)
 m=bpy.data.materials['v016 | Village continues | abandoned paint']
 print('ALPHA_INSPECT',f,[(n.name,n.type,[i.default_value for i in n.inputs if hasattr(i,'default_value') and i.type=='VALUE']) for n in m.node_tree.nodes if n.type in ['MATH','MIX_SHADER']],flush=True)
print('EEVEE_PROPERTIES',[p.identifier for p in s.eevee.bl_rna.properties],flush=True)
