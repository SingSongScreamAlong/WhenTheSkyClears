import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;r=next(o for o in S.objects if o.type=='ARMATURE' and o['character']=='GIRL');head=next(o for o in r.children if o.type=='MESH' and 'original head' in o.name);body=next(o for o in r.children if o.get('skin_region')=='dress')
def pts(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [v.co.copy() for v in e.data.vertices]
basehead=pts(head);basebody=pts(body);grp=head.vertex_groups['braid'].index
fixed=[v.index for v in head.data.vertices if all(g.group!=grp or g.weight<1e-8 for g in v.groups)]
def area(vs,p):
 a,b,c=(vs[i] for i in p.vertices[:3]);return (b.x-a.x)*(c.z-a.z)-(b.z-a.z)*(c.x-a.x)
beforearea=[area(basebody,p) for p in body.data.polygons];results=[]
for kind,deg in [('braid',-5),('braid',5),('skirt',-5),('skirt',5)]:
 for n in ['braid','skirt_front','skirt_back']:r.pose.bones[n].rotation_mode='XYZ';r.pose.bones[n].rotation_euler=(0,0,0)
 if kind=='braid':r.pose.bones['braid'].rotation_euler.z=math.radians(deg)
 else:
  r.pose.bones['skirt_front'].rotation_euler.z=math.radians(deg);r.pose.bones['skirt_back'].rotation_euler.z=-math.radians(deg)
 afterhead=pts(head);afterbody=pts(body);afterarea=[area(afterbody,p) for p in body.data.polygons]
 results.append({'control':kind,'delta_degrees':deg,'max_head_displacement_m':max((a-b).length for a,b in zip(basehead,afterhead)),'head_vertices_without_braid_weight_max_drift_m':max((basehead[i]-afterhead[i]).length for i in fixed),'max_dress_displacement_m':max((a-b).length for a,b in zip(basebody,afterbody)),'dress_triangle_orientation_flips':sum(a*b<0 for a,b in zip(beforearea,afterarea)),'art_acceptance':'OPEN; bounded secondary control test only, not approved hair/cloth motion.'})
 S.render.filepath=str(P/f'previews/SECONDARY_{kind}_{deg:+d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/secondary_control_tests.json').write_text(json.dumps(results,indent=2));print('SECONDARY_TESTS',json.dumps(results))
