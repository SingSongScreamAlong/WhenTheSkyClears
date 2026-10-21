import bpy,bmesh,math,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s
ground=bpy.data.objects['FXv009 | persistent excavated bowl and raised rim'];me=ground.data
# Correct the actual top-surface winding, then feather only the external apron.
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
attr=me.attributes.new('ground_coverage','FLOAT','POINT')
for i,v in enumerate(me.vertices):
    ring=i//48;coverage=[1,1,1,1,1,0][ring];attr.data[i].value=coverage
    # 2.5D art direction: open the rear wall toward the horizontal story camera.
    v.co.z+=.17*v.co.y
for i,mat in enumerate(list(me.materials)):
    mat=mat.copy();mat.name+=' | crater apron coverage';me.materials[i]=mat;mat.surface_render_method='BLENDED';nt=mat.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');surface=out.inputs['Surface'].links[0].from_socket
    a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='ground_coverage';tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a.outputs['Fac'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(surface,mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
s.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Ground_Debris_Proof_v009c.blend'),compress=True)
(P/'evidence/crater_correction.json').write_text(json.dumps({'actual_review_problem':'Ground read as a polygon plate.','correction':['reversed downward top normals','feathered external apron while leaving the broken rim opaque','opened rear cavity wall toward horizontal 2.5D camera'],'smoke':False,'status':'Pending actual shot-size visual evaluation'},indent=2));print('CRATER_C_CORRECTED')
