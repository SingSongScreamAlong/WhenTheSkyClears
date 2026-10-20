"""Focused art changes following independent review. No motion/action edits."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Live_Limb_Continuity_v036.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];report={'scope':'Focused native art correction; no animation curves edited','sleeves':{},'hands':{},'cuffs':{}}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
for side in ['near','far']:
 for part in ['drawn sleeve','drawn source gray cuff']:
  o=bpy.data.objects['V007_BOY | '+part+' '+side];a=o.data.attributes['V017_width'];old=[x.value for x in a.data];count=len(old)//2;ts=[(15+i//2)/18 if 'cuff' in part else (i//2)/(count-1) for i in range(len(old))];new=[w*(1-.24*smooth((t-.42)/.58)) for w,t in zip(old,ts)];a.data.foreach_set('value',new);report['sleeves'][o.name]={'original_halfwidth_last_m':max(abs(x) for x in old[-2:]),'candidate_halfwidth_last_m':max(abs(x) for x in new[-2:]),'shoulder_width_retained':True,'UV_material_retained':True}
  o['V036_art']='Restrained24percent distal sleeve/cuff width taper; shoulder widths, elbow/wrist paths and original pigment UV retained. The fabric edge meets the existing forearm without a broad blunt wedge.'
 # Keep existing palm/fingers. Only give the relaxed original thumb a little clearance.
 o=bpy.data.objects['V007_BOY | articulated drawn hand '+side];B=rig.data.bones['hand_'+side].matrix_local;inv=B.inverted();mx=0
 for kb in o.data.shape_keys.key_blocks:
  for i,p in enumerate(kb.data):
   if i<80:continue
   t=(i-80)//2/8;d=Vector((-.0035*t*t,-.001*t*t,0));p.co+=B.to_3x3()@d;mx=max(mx,d.length)
 # Mesh coordinates mirror Basis for correct editable rest artwork.
 o.data.vertices.foreach_set('co',[c for p in o.data.shape_keys.key_blocks[0].data for c in p.co]);o.data.update();report['hands'][side]={'thumb_local_adjustment_max_m':mx,'palm_finger_vertices_unchanged':80,'global_hand_scale_unchanged':True,'no_hand_path_or_bone_orientation_edit':True}
 for part,delta in [('articulated drawn hand',.020),('drawn skin',.013)]:
  ob=bpy.data.objects['V007_BOY | '+part+' '+side];m=ob.material_slots[0].material;n=m.node_tree.nodes.get('V035 modest local charcoal lift');assert n;n.inputs[2].default_value=(delta,delta,delta,1);m.name='V036 | restrained charcoal separation | '+part+' '+side
 # Narrow the rolled-cuff cross-sections around the unchanged center and ankle join.
 o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];maxmove=0
 for kb in o.data.shape_keys.key_blocks:
  V=[p.co.copy() for p in kb.data]
  for row in range(97):
   t=row/96;w=.085*smooth((t-.78)/.07);C=(V[row*7]+V[row*7+6])*.5;N=(V[row*7+6]-V[row*7]).normalized()
   for col in range(7):
    i=row*7+col;new=V[i]-N*(V[i]-C).dot(N)*w;maxmove=max(maxmove,(new-V[i]).length);kb.data[i].co=new
 o.data.vertices.foreach_set('co',[c for p in o.data.shape_keys.key_blocks[0].data for c in p.co]);a=o.data.attributes['V036_width_scale'];ts=[(i//7)/96 for i in range(len(a.data))];a.data.foreach_set('value',[(1-.085*math.exp(-((t-.58)/.12)**2)-.025*math.exp(-((t-.28)/.24)**2))*(1-.065*math.exp(-((t-.70)/.075)**2)) for t in ts]);report['cuffs'][side]={'cross_section_width_reduction_fraction':.085,'max_vertex_change_m':maxmove,'center_and_shoe_paths_unchanged':True,'calf_local_width_reduction_fraction':.065}
# Both children-facing shoe instances retain one shared mesh and all sole geometry.
near=bpy.data.objects['V033 | near | canonical painted shoe'];far=bpy.data.objects['V033 | far | canonical painted shoe'];assert near.data==far.data;old=[v.co.copy() for v in near.data.vertices];protected=set()
for i in range(3401):
 a=math.radians(-85+i*.05);z=[-math.sin(a)*v.x+math.cos(a)*v.z for v in old];mn=min(z)
 for j,value in enumerate(z):
  if value<=mn+1e-6:protected.add(j)
changed=[]
for j,v in enumerate(near.data.vertices):
 if j in protected or v.co.z<=-.02:continue
 w=smooth((v.co.z+.02)/.062);v.co.x*=1-.06*w;v.co.z-=.0015*w*w;changed.append(j)
near.data.update();report['shoe_upper_contour']={'shared_mesh':True,'changed_upper_vertices':changed,'all_support_vertices_unchanged':all((near.data.vertices[j].co-old[j]).length==0 for j in protected),'support_vertex_count':len(protected),'tested_pitch_degrees':[-85,85],'max_upper_vertex_change_m':max((v.co-w).length for v,w in zip(near.data.vertices,old)),'foot_and_shoe_object_paths_edited':False}
assert report['shoe_upper_contour']['all_support_vertices_unchanged']
S['V036_status']='Focused limb art/motion candidate after independent review. Live thigh/shin drawing axes; slimmer knees/calves/cuffs and upper shoe opening; tapered sleeve ends; modest local hand values and thumb clearance. Preferred control timing preserved. ART REVIEW OPEN.';S.frame_set(11);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Limb_Volume_and_Hand_Readability_v036.blend'),compress=True);(P/'evidence/FOCUSED_ART_CORRECTIONS.json').write_text(json.dumps(report,indent=2));print('V036_FOCUSED_ART_BUILT',json.dumps(report),flush=True)
