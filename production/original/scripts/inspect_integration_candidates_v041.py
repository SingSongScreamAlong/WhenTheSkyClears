"""Read-only production geometry and unsealed performance schema inspection."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest();s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];bpy.context.window.scene=s;pair=next(o for o in s.objects if o.type=='GREASEPENCIL');frames=[]
for f in [1801,1813,1825,1849,1897,1920]:
    s.frame_set(f);bpy.context.view_layer.update();points=[pair.matrix_world@p.vector for p in pair.data.layers[0].frames[0].drawing.attributes['position'].data];p=[world_to_camera_view(s,s.camera,q) for q in points]
    frames.append({'frame':f,'seconds':(f-1)/24,'camera':list(s.camera.matrix_world.translation),'pair_root':list(pair.matrix_world.translation),'world_bounds':[min(q.x for q in points),max(q.x for q in points),min(q.z for q in points),max(q.z for q in points)],'screen_bounds':[min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p)]})
objects=[]
for ob in s.objects:
    if any(word in ob.name for word in ['continuous blended paint','Battlefield | broken','Ruins | distant','near rooted','near bank','painted fill','High crown foreground']):
        objects.append({'name':ob.name,'type':ob.type,'location':list(ob.location),'bounds':[list(ob.matrix_world@Vector(p)) for p in ob.bound_box] if ob.type=='MESH' else None,'materials':[m.name for m in ob.data.materials] if hasattr(ob.data,'materials') else []})
report={'production_source':str(source),'production_sha256':before,'shot_frames':[1801,1920],'camera_lens':s.camera.data.lens,'camera_shift':[s.camera.data.shift_x,s.camera.data.shift_y],'samples':frames,'live_geometry':objects,'candidate_imported':False}
p=R/'locomotion/performance_v003/native/WTSC_Performance_Library_v003.blend';motion_before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));root=next(o for o in bpy.data.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v003');actions=[]
for a in bpy.data.actions:
    channels=[f for layer in a.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves];row={'name':a.name,'range':list(a.frame_range),'channels':len(channels)}
    if 'ROOT__WEARY' in a.name:
        row['distance_curve']=[{'path':f.data_path,'index':f.array_index,'samples':[[i,f.evaluate(i)] for i in [1,13,18,24,29,33,41,49,64,80,96]]} for f in channels]
    actions.append(row)
report['unsealed_motion_read_only']={'path':str(p),'sha256_at_inspection':motion_before,'root':root.name,'root_properties':{k:v for k,v in root.items() if isinstance(v,(str,int,float,bool))},'children':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None} for o in root.children_recursive],'actions':actions,'sealed_handoff_received':False,'use_in_integration':False}
assert hashlib.sha256(source.read_bytes()).hexdigest()==before and hashlib.sha256(p.read_bytes()).hexdigest()==motion_before
(R/'notes/world_v016/integration_read_only_v041.json').write_text(json.dumps(report,indent=2));print('INTEGRATION_CANDIDATES_READ_ONLY',json.dumps({'production_unchanged':True,'motion_sha256_at_inspection':motion_before,'imported':False}),flush=True)
