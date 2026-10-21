"""Keep the animated world as the render owner; reference only static glyph geometry."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text())
S=Path(build['native']);N=O/'native/WTSC_First_Danger_Conformed_v065c.blend';assert not N.exists()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];ctrl=bpy.data.objects['V065 | both children | global full-cut color time']
w.compositing_node_group=m.compositing_node_group.copy();w.compositing_node_group.name='V065 | world-owned title and visible drawing composite'
for n in w.compositing_node_group.nodes:
 if n.type=='R_LAYERS' and n.scene==w:n.scene=None
m.render.use_compositing=False
for n in m.compositing_node_group.nodes:
 if n.type=='OUTPUT_FILE':n.mute=True
for name in ['WTSC_FIRST_DANGER_TITLE_v065','WTSC_FIRST_DANGER_UNMASKED_EDIT_v065','WTSC_FIRST_DANGER_REVIEW_MASTER_v065']:
 s=bpy.data.scenes[name]
 if ctrl.name in s.collection.objects:s.collection.objects.unlink(ctrl)
 if s.sequence_editor:
  for st in s.sequence_editor.strips:
   if st.type=='SCENE':st.scene=w
w.render.use_compositing=True
w['V065_render_owner']='Render this world scene directly: editable world, live global color, visible-object matte and native title composite evaluate on one dependency graph. Disable Compositing for a raw world render; the compositor also exports an unmasked branch.'
bpy.context.window.scene=w;w.frame_set(981);m.frame_set(981);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True)
build['previous_clock_draft']=str(S);build['native']=str(N);build['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest();build['render_owner']=w.name;build['title_geometry_scene']=m.name
build['render_graph_correction']='Animated world owns the compositor; only the static glyph geometry is cross-scene. This avoids the observed cross-scene render dependency freeze. Unmasked branch is an editable native File Output.'
build['unmasked_edit_note']='Old source edit retained as a reference Scene strip. For an unmasked render, use world with Compositing disabled, or the live unmasked File Output.'
(O/'evidence/BUILD.json').write_text(json.dumps(build,indent=2));print('V065C_WORLD_OWNED_COMPOSITOR_SAVED',flush=True)
