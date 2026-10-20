import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];FILE=P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.threads_mode='FIXED';S.render.threads=2;S.render.dither_intensity=0
ART=bpy.data.collections['V044 | age10 editable profile anatomy'];C=bpy.data.collections['V046 | restored original painted wardrobe'];BEFORE=bpy.data.collections['V044 | before F1 source painting snapshots'];RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};visible={o.name:o.hide_render for c in [ART,C] for o in c.objects};G=bpy.data.collections.new('V046 | actual skeleton review only');S.collection.children.link(G)
mat=bpy.data.materials.new('V046 review | actual-bone amber');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();em=ns.new('ShaderNodeEmission');em.inputs[0].default_value=(.55,.19,.045,1);out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs[0]);S.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();bones={}
for who,r in RIGS.items():
 e=r.evaluated_get(dg);bones[who]={}
 for n,b in e.pose.bones.items():
  a=e.matrix_world@b.head;c=e.matrix_world@b.tail;a.y=c.y=-.13;d=(c-a).normalized();side=Vector((-d.z,0,d.x))*.003;me=bpy.data.meshes.new('actual '+n);me.from_pydata([a-side,c-side,c+side,a+side],[],[(0,1,2,3)]);me.materials.append(mat);o=bpy.data.objects.new('ACTUAL '+who+' '+n,me);G.objects.link(o);o.hide_render=True;bones[who][n]={'rest_length_m':r.data.bones[n].length,'evaluated_head_world':list(a),'evaluated_tail_world':list(c)}
def render(name):S.render.filepath=str(P/'previews'/name);bpy.context.view_layer.update();bpy.ops.render.render(write_still=True,scene=S.name)
render('RESTORED_DRESSED_F1.png')
for c in [ART,C]:
 for o in c.objects:
  if o.type=='MESH':o.hide_render=True
for o in G.objects:o.hide_render=False
render('ACTUAL_CORRECTED_BONES_F1.png')
for o in G.objects:o.hide_render=True
for o in BEFORE.objects:o.hide_render=False;o.location.x=-.4 if o.name.startswith('BEFORE BOY') else .4
render('OLD_POLISHED_REFERENCE_F1.png')
for o in BEFORE.objects:o.hide_render=True
for c in [ART,C]:
 for o in c.objects:o.hide_render=visible[o.name]
for o in G.objects:o.hide_render=False
render('RESTORED_WITH_ACTUAL_BONES_F1.png')
for o in G.objects:o.hide_render=True
for f in [9,17,25]:S.frame_set(f);render('RESTORED_DRESSED_F%02d.png'%f)
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==before;(P/'evidence/ACTUAL_BONE_RENDER_PROOF.json').write_text(json.dumps({'native_sha256':before,'native_unchanged':True,'actual_evaluated_bones':bones,'common_camera_resolution':[1280,720],'common_camera_ortho_width_m':3.25,'old_reference_caveat':'Old polished sourceF1 snapshots shown at identical metres/camera; those have older anatomy. Corrected bone panels are actual evaluated native rigs, not independent drawn anatomy guides.'},indent=2));print('V046_OUTFIT_COMPARISON_RENDER_COMPLETE',flush=True)
