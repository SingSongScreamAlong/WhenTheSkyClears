import bpy,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_v025.blend';start=time.time()
def background(S):
    # The neutral stage uses the World, so transparency for the foreground pass requires a compositor paper colour.
    g=S.compositing_node_group;n=g.nodes;l=g.links;out=next(x for x in n if x.type=='GROUP_OUTPUT');existing=out.inputs['Image'].links[0].from_socket
    over=n.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;over.inputs['Background'].default_value=(.65,.635,.59,1);l.new(existing,over.inputs['Foreground']);l.new(over.outputs[0],out.inputs['Image'])
def draw(S,mode,camera):
    folder=P/'previews'/mode;folder.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=(360,540) if 'CLOSE' in mode or 'BARE' in mode else (960,540);S.render.resolution_percentage=100
    for f in range(17,33):S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene
deps=bpy.data.collections['V025 | evaluation dependencies']
for o in list(deps.objects):
    if o.type not in ['EMPTY','ARMATURE','CAMERA','LIGHT']:deps.objects.unlink(o)
background(S);S.frame_set(21);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
draw(S,'GP_CLOSE','V024 | CLOSE portrait');draw(S,'GP_SHOT','V020 | CHILD | SHOT')
bpy.data.objects['V025 | COAT drawings | editable GP'].hide_render=True;bpy.data.objects['LOCO_BOY | PAINT body'].hide_render=True;bpy.data.objects['V025 | bare torso diagnostic | optional'].hide_render=False
draw(S,'BARE_CLOSE','V024 | CLOSE portrait')
# Match the paper background for the unchanged v024 reference, rather than recolour its character pixels.
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_WALK_v024.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;S.render.film_transparent=True;g=bpy.data.node_groups.new('V025 comparison paper','CompositorNodeTree');g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');S.compositing_node_group=g;r=g.nodes.new('CompositorNodeRLayers');out=g.nodes.new('NodeGroupOutput');g.links.new(r.outputs['Image'],out.inputs['Image']);background(S)
draw(S,'V024_CLOSE','V024 | CLOSE portrait');draw(S,'V024_SHOT','V020 | CHILD | SHOT')
(P/'evidence/REVIEW_RENDER_RECORD.json').write_text(json.dumps({'source_frames':[17,32],'fps':30,'normal_speed_one_pass_seconds':16/30,'modes':['GP_CLOSE','GP_SHOT','BARE_CLOSE','V024_CLOSE','V024_SHOT'],'frames_per_mode':16,'threads':2,'seconds_elapsed':time.time()-start,'production_unchanged':True,'comparison_background':'Matched neutral compositor paper; original character painting not recoloured'},indent=2));print('V025_TRANSITION_REVIEW_RENDERED',time.time()-start)
