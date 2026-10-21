import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;SRC=O/'WTSC_World_Foreground_Development_v058d.blend';OUT=O/'WTSC_World_Development_v058_Packed.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
def graph():
 return {m.name:hashlib.sha256(repr(([(n.name,n.bl_idname) for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])).encode()).hexdigest() for m in bpy.data.materials if m.node_tree}
before=graph()
paths={}
for s in bpy.data.scenes:
 s.render.filepath='//renders_v058/'+s.name+'/frame_';paths[s.name]=s.render.filepath
s=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];bpy.context.window.scene=s;s.frame_set(1537)
text=bpy.data.texts.new('READ ME | v058 world development')
text.write('Foreground refinement checkpoint. Open scene WTSC_WORLD_FOREGROUND_v058d for the unmasked world review. Full inherited title/master scenes remain available. Render outputs now go to a new relative renders_v058 folder. All file images are packed.\nThis file does not contain new v027 character performance. Full-film children still hold the old pose. Whole-film minimum remains unmet: paired drawn acting/story beats, integrated contacts/occlusion, broader native architecture and full artistic review are outstanding. Original production and v057 are preserved.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
assert graph()==before
(O/'PACKAGED_NATIVE_MANIFEST.json').write_text(json.dumps({'native':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'rendered_content_source':str(SRC),'rendered_content_source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'packaging_only_changes':['Unique relative renders_v058 export paths in every scene','Native READ ME text block'],'material_node_graphs_identical':graph()==before,'all_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.type!='RENDER_RESULT'),'scenes':[{'name':sc.name,'range':[sc.frame_start,sc.frame_end],'fps':sc.render.fps,'resolution':[sc.render.resolution_x,sc.render.resolution_y]} for sc in bpy.data.scenes],'relative_output_paths':paths},indent=2))
print('NATIVE_PACKAGED',flush=True)
