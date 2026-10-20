"""Two small actual native shoe-design stills. Temporary flat review layout; native unchanged."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Preferred_Walk_Consistent_Shoes_v033.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update();rig=bpy.data.objects['LOCO_BOY | RIG'];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());newmesh=bpy.data.objects['V033 | near | canonical painted shoe'].data;old={}
for s in ['near','far']:
    e=bpy.data.objects[B[s]['object']].evaluated_get(bpy.context.evaluated_depsgraph_get());tmp=e.to_mesh(preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());mesh=tmp.copy();W=e.matrix_world.copy();e.to_mesh_clear();F=rig.matrix_world@rig.pose.bones['foot_'+s].matrix;R=F.to_3x3()@Matrix(B[s]['flat_bone']).to_3x3().inverted();a=math.atan2(R[0][2],R[0][0]);iv=Matrix.Rotation(-a,4,'Y');V=[iv@(W@v.co-F.translation) for v in mesh.vertices];mesh.vertices.foreach_set('co',[x for v in V for x in v]);mesh.update();old[s]=mesh
for o in S.objects:
    if o.type in ['MESH','GREASEPENCIL','CURVE']:o.hide_render=True
col=bpy.data.collections.new('V033 | temporary flat footwear inspection');S.collection.children.link(col);S.view_layers['V025 | original foreground'].layer_collection.children[col.name].exclude=True
sets={}
for tag in ['OLD','SHARED']:
    pair=[]
    for s,x in [('near',-.18),('far',.18)]:
        data=old[s] if tag=='OLD' else newmesh;ob=bpy.data.objects.new('Flat review '+tag+' '+s,data);col.objects.link(ob);sc=.97 if tag=='SHARED' and s=='far' else 1.;ob.scale=(sc,)*3;ob.location=(x,0,-min(v.co.z for v in data.vertices)*sc);ob.hide_render=True;pair.append(ob)
    sets[tag]=pair
mesh=bpy.data.meshes.new('review sole plane line');mesh.from_pydata([(-.5,.1,-.001),(.5,.1,-.001),(.5,.1,.001),(-.5,.1,.001)],[],[(0,1,2,3)]);line=bpy.data.objects.new('review sole plane line',mesh);col.objects.link(line);ma=bpy.data.materials.new('review line gray');ma.use_nodes=True;n=ma.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.35,.36,.33,1);ma.node_tree.links.new(em.outputs[0],out.inputs[0]);mesh.materials.append(ma)
camdata=bpy.data.cameras.new('flat footwear review camera');camdata.type='ORTHO';camdata.ortho_scale=.85;camdata.sensor_fit='HORIZONTAL';cam=bpy.data.objects.new(camdata.name,camdata);col.objects.link(cam);cam.location=(0,-5,.085);cam.rotation_euler=(math.pi/2,0,0);S.camera=cam;S.render.resolution_x=1280;S.render.resolution_y=400;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2
for tag,pair in sets.items():
    for ob in pair:ob.hide_render=False
    S.render.filepath=str(P/f'previews/FLAT_{tag}_PAIR.png');bpy.ops.render.render(write_still=True)
    for ob in pair:ob.hide_render=True
(P/'evidence/FLAT_DESIGN_RENDER_RECORD.json').write_text(json.dumps({'actual_native_stills':2,'dimensions':[1280,400],'old':'Original two V028 shoes normalized to flat without replacing their geometry/UVs','shared':'One native shoe mesh/UV/material instance for both feet; far uniformly97%','temporary_scene_only_native_unchanged':True},indent=2));print('V033_FLAT_SHOE_DESIGN_REVIEW_RENDERED',flush=True)
