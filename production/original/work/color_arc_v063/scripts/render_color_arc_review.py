import bpy,json,hashlib,math
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\color_arc_v063');N=O/'native/WTSC_Shared_Color_To_Charcoal_v063.blend';h=hashlib.sha256(N.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(N),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063'];bpy.context.window.scene=s
ctrl=bpy.data.objects['V063 | shared color to charcoal | both children']
fcs=[f for l in ctrl.animation_data.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves];assert len(fcs)==1;fc=fcs[0]
mats=[m for m in bpy.data.materials if m.get('V063_color_arc')]
nodes=[n for m in mats for n in m.node_tree.nodes if n.name.startswith('V063 | shared color to charcoal /')]
assert nodes and len(mats)==35
root=bpy.data.objects['V047 | shared travel | steady .73125mps']
def active_nodes():
 active={sl.material for ob in root.children_recursive if ob.type=='MESH' and not ob.hide_render for sl in ob.material_slots if sl.material and sl.material.get('V063_color_arc')}
 return [n for m in active for n in m.node_tree.nodes if n.name.startswith('V063 | shared color to charcoal /')]
for m in mats:
 for driver in m.node_tree.animation_data.drivers:
  if 'shared color to charcoal /' in driver.data_path:
   v=driver.driver.variables[0];assert v.targets[0].id==ctrl and v.targets[0].data_path=='["charcoal_progress"]'
samples=[]
for sec in [0,18,35,39,44,50,67,80,90,96,100]:
 g=1+24*sec;s.frame_set(g);bpy.context.view_layer.update();p=float(ctrl['charcoal_progress'])
 live_nodes=active_nodes();errors=[abs(n.inputs[0].default_value-p) for n in live_nodes];assert max(errors)<1e-6,(sec,p,max(errors))
 samples.append({'seconds':sec,'frame':g,'progress':p,'all_material_driver_max_error':max(errors)})
review_values=[(i*100/59,float(fc.evaluate(1+24*i*100/59))) for i in range(60)]
endpoints={t:float(fc.evaluate(1+24*t)) for t in [0,50,96]}
s.frame_set(981);bpy.context.view_layer.update();nodes=active_nodes();fc.mute=True
P=O/'previews/arc_frames';P.mkdir(exist_ok=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s,'eevee'):s.eevee.taa_render_samples=64
rows=[]
for i in range(60):
 t,p=review_values[i];ctrl['charcoal_progress']=p;ctrl.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
 assert max(abs(n.inputs[0].default_value-p) for n in nodes)<1e-6
 s.render.filepath=str(P/('%04d.png'%(i+1)));bpy.ops.render.render(write_still=True,scene=s.name)
 rows.append({'review_frame':i+1,'represented_trailer_seconds':t,'progress':p,'scene_pose_frame':981,'sha256':hashlib.sha256((P/('%04d.png'%(i+1))).read_bytes()).hexdigest()})
for label,t in [('Full_Color',0),('Midpoint',50),('Charcoal',96)]:
 p=endpoints[t];ctrl['charcoal_progress']=p;ctrl.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
 s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.filepath=str(O/('previews/'+label+'_v063.png'));bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(N.read_bytes()).hexdigest()==h
(O/'evidence/COLOR_ARC_RENDER.json').write_text(json.dumps({'native_sha256':h,'native_unchanged':True,'cold_driver_samples':samples,'actor_material_count':len(mats),'emission_driver_nodes':len(nodes),'review':'Color-only study: pose/camera/background held at G981; full0-100s palette progression compressed to5s at12fps; no story motion or soundtrack timing claim','native_scene_interval_seconds':[39,44],'rows':rows},indent=2))
print('V063_COLOR_ARC_REVIEW_RENDER_COMPLETE',flush=True)
