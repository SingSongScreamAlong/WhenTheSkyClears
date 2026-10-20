"""Enable existing paint only AFTER the silhouette proof has been inspected."""
import bpy,json,hashlib,struct,ast,re
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FXv008 | coherent silhouette validation'];bpy.context.window.scene=s
root=bpy.data.objects['FXv008 | fixed world impact and controls'];asset=bpy.data.collections['FXv008 | ONE COHERENT NATIVE BLAST']
source=json.loads((P/'evidence/build_coherent.json').read_text());validation=json.loads((P/'evidence/silhouette_review.json').read_text())
assert validation['continuous_structure_passed'] and validation['proceed_to_existing_paint']
tree=ast.parse((P/'scripts/build_coherent.py').read_text());tree.body=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='geometry_hash'];exec(compile(tree,'owned_geometry_fingerprint','exec'),globals())
before=geometry_hash();assert before==source['geometry_sha256']
anchor=list(root.location);camera=[list(row) for row in s.camera.matrix_world]
owners=[root,s.compositing_node_group]
for ob in asset.all_objects:
    owners.append(ob)
    if ob.type=='MESH':
        if ob.data.shape_keys:owners.append(ob.data.shape_keys)
        owners.extend(m.node_tree for m in ob.data.materials if m and m.node_tree)
pruned=0
for owner in set(owners):
    if owner.animation_data:
        for f in owner.animation_data.drivers:
            for variable in list(f.driver.variables):
                if not re.search(r'\b'+variable.name+r'\b',f.driver.expression):f.driver.variables.remove(variable);pruned+=1
# A redundant self-target on the light envelope generated a depsgraph warning;
# deleting unused variables leaves every expression and vertex key unchanged.
s.frame_set(1827);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Coherent_Silhouette_Clean_v008.blend'),compress=True)
root['painted']=1.;s.name='FXv008 | coherent painted proof';s.frame_set(1827);bpy.context.view_layer.update()
assert geometry_hash()==before and list(root.location)==anchor and [list(row) for row in s.camera.matrix_world]==camera
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Coherent_Painted_v008.blend'),compress=True)
helper=bpy.data.node_groups['FXv008 | FX-only restrained bloom over']
bpy.data.libraries.write(str(P/'native/WTSC_Coherent_Append_v008.blend'),{asset,helper},fake_user=True,compress=True)
report={'silhouette_validated':True,'paint_source':source['reused_paint_image'],'geometry_before':before,'geometry_after':geometry_hash(),'same_vertex_keys_and_topology':True,'same_world_anchor':anchor,'same_camera':camera,'unused_driver_variables_pruned':pruned,'no_new_artwork':True,'no_shape_changes_when_paint_enabled':True,'paint_method':'Existing packed v003 paint/palette fills advected UVs inside native evolving outlines. Source image alpha affects pigment color only.','local_light_and_bloom':'Only compact flash/local receiver changes lighting, driven from the same impulse; no camera shake or audio.'}
(P/'evidence/paint_application.json').write_text(json.dumps(report,indent=2));print('EXISTING_PAINT_APPLIED_TO_IDENTICAL_GEOMETRY',json.dumps(report),flush=True)
