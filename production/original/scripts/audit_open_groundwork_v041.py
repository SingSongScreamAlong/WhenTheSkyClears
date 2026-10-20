"""Native reopen/dependency audit; no GPU render or candidate integration."""
import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');p=Path(bpy.data.filepath);before=hashlib.sha256(p.read_bytes()).hexdigest();s=bpy.data.scenes['WTSC_OPEN_INTEGRATION_GROUNDWORK_v041'];bpy.context.window.scene=s
assert len(bpy.data.scenes)==1 and s.frame_start==1801 and s.frame_end==1920 and s.render.fps==24
assert not any(n.bl_idname=='CompositorNodeImage' for n in s.compositing_node_group.nodes)
assert not any('ink_wash_v001' in im.filepath.lower() or 'benchmark_v002' in im.filepath.lower() or 'benchmark_v003' in im.filepath.lower() for im in bpy.data.images)
assert not any(o.name.startswith(('FXv002','FXv003','LOCO_PAIR')) for o in s.objects)
event=s.objects['v041 | Live event binding | awaiting verified FX'];assert event['power_watts']==0 and event['bound_to_verified_fx']==0
pair=next(o for o in s.objects if o.type=='GREASEPENCIL');samples=[]
for f in [1801,1825,1861,1920]:
    s.frame_set(f);bpy.context.view_layer.update();C=s.camera.matrix_world.translation;E=event.matrix_world.translation;values=[]
    for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
        ob=s.objects[name];k=(ob.matrix_world.translation.y-C.y)/(E.y-C.y);hit=C+(E-C)*k;point=world_to_camera_view(s,s.camera,hit);origin=world_to_camera_view(s,s.camera,E);assert abs(point.x-origin.x)<1e-5 and abs(point.y-origin.y)<1e-5;values.append({'receiver':name,'live_projected_world_hit':list(hit),'screen_error':[point.x-origin.x,point.y-origin.y]})
    samples.append({'frame':f,'camera':list(C),'receivers':values,'event_power':event['power_watts']})
bad=[]
for mat in bpy.data.materials:
    if mat.name.startswith('v041') and mat.node_tree.animation_data:
        bad += [[mat.name,d.data_path,d.driver.expression] for d in mat.node_tree.animation_data.drivers if not d.is_valid]
assert not bad,bad
sha040=hashlib.sha256((R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend').read_bytes()).hexdigest();assert sha040=='c3ed3c15055ae5cd242a68964d6980bb8bda3ff6f7f4882d69fa4198e937819f'
report={'source':str(p),'source_sha256':before,'native_reopen_pass':True,'frames':[1801,1920],'duration_seconds':5,'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'compositor_uses_live_renderlayers_only':True,'held_plates_or_masks':False,'specialist_collections_imported':False,'invalid_receiver_drivers':bad,'live_camera_projection_samples':samples,'production_v040_preserved_sha256':sha040,'current_blockers':['Replacement FX must pass smoke-evolution/hot-phase review and sealed handoff','Motion library requires coordinating-parent sealed current snapshot','Actual foreground frames await free GPU; FX v003 worker currently owns GPU render'],'scope':'Groundwork structural checks only; not an integrated artistic proof.'}
assert hashlib.sha256(p.read_bytes()).hexdigest()==before;(R/'notes/world_v016/integration_groundwork_reopen_v041.json').write_text(json.dumps(report,indent=2));print('OPEN_GROUNDWORK_REOPEN_VERIFIED',json.dumps({'live_projection_samples':len(samples),'invalid_drivers':bad,'candidates_imported':False}),flush=True)
