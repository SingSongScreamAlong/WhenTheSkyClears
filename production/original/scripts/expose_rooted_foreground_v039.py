import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];bpy.context.window.scene=w
bank=w.objects['v020 | Foreground bank | continuous blended paint'];nt=bank.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and 'Foreground_Ground' in n.image.name)
bank_color=next(l.to_node for l in nt.links if l.from_node==tex and l.to_node.type=='MIX_RGB' and l.to_node.blend_type=='MULTIPLY');blend=next(l.to_node for l in nt.links if l.from_node==bank_color and l.to_node.type=='MIX_RGB' and l.to_socket==l.to_node.inputs[2])
for link in list(blend.inputs[0].links):nt.links.remove(link)
blend.inputs[0].default_value=0
changed=[]
for ob in w.objects:
 if not ob.name.startswith('v016 | Rooted grass ') or not 78<=ob.location.x<=100:continue
 old=list(ob.location);depth=ob.location.y+16;width=.36*depth;height=width*2160/3840
 ob.location.z=3+(.17-.5)*height+w.camera.data.shift_y*width
 ob['v039_grounding']='Root below foreground-bank edge on actual camera floor ray; upper pinned blades emerge through static feather. Fixed world position, original wind retained.'
 changed.append({'object':ob.name,'old':old,'new':list(ob.location)})
w.frame_set(1609);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
p=R/'notes/world_v016/camp_paint_language_v039.json';r=json.loads(p.read_text());r['sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();r['foreground']='Repeated bank photograph contribution removed; continuous painted earth retained. Existing native rooted grass in camp78–100 now rises from bank ray instead of being buried below it. Source wind kept; no new prototype art.';r['native_grass_contacts']=changed;p.write_text(json.dumps(r,indent=2));print('ROOTED_FOREGROUND_EXPOSED',json.dumps({'count':len(changed),'source':bpy.data.filepath}),flush=True)
