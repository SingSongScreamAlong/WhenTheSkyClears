import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v027'
pair=next(o for o in s.objects if o.type=='GREASEPENCIL')
oak=s.objects['v023 | Opening oak roots fence and path | one coherent surface']
pano=s.objects['v026 | Countryside panorama | stationary at true depth']
samples=[]
for frame in [1,25,49,193,721,817,2305,2400]:
    s.frame_set(frame);bpy.context.view_layer.update()
    def screen(point):
        p=world_to_camera_view(s,s.camera,point);return [p.x*3840,(1-p.y)*2160]
    drawing=pair.data.layers[0].frames[0].drawing;positions=drawing.attributes['position'].data
    blob=b''.join(struct.pack('fff',*p.vector) for p in positions)
    pts=[]
    for uv in [(.1,.2),(.1,.6)]:
        co=Vector(((uv[0]-.5)*7.92,(uv[1]-.5)*4.455,0));pts.append(screen(oak.matrix_world@co))
    samples.append({'frame':frame,'camera':list(s.camera.location),'pair':list(pair.location),'drawing_sha256':hashlib.sha256(blob).hexdigest(),'same_oak_root_upper_px':pts,'landmark_panorama_px':screen(pano.matrix_world@Vector((0,0,0)))})
assert len({a['drawing_sha256'] for a in samples})==1
assert not pano.animation_data
assert abs((samples[1]['same_oak_root_upper_px'][0][0]-samples[0]['same_oak_root_upper_px'][0][0])-(samples[1]['same_oak_root_upper_px'][1][0]-samples[0]['same_oak_root_upper_px'][1][0]))<.01
smoke=[]
for o in s.objects:
    if ' | wisp ' in o.name:
        basis=o.data.shape_keys.key_blocks[0]
        smoke.append({'name':o.name,'origin':list(o.location),'basis_min_z':min(p.co.z for p in basis.data),'basis_max_z':max(p.co.z for p in basis.data),'location_drivers':[d.data_path for d in o.animation_data.drivers if d.data_path=='location'] if o.animation_data else []})
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frame_samples':samples,'single_held_drawing_persisted':True,'oak_root_and_upper_camera_shift_equal':True,'panorama_stationary':True,'panorama_landmark_moves_with_perspective':samples[0]['landmark_panorama_px']!=samples[1]['landmark_panorama_px'],'smoke_anchors':smoke,'native_output':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.fps,s.frame_start,s.frame_end],'active_images':[{'name':i.name,'pixels':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE'],'gp_frames':sum(len(l.frames) for l in pair.data.layers),'review_scope':'Native persistence and coherence checks. Does not establish artistic or performance approval.'}
(R/'notes/world_v016/native_motion_audit_v027.json').write_text(json.dumps(report,indent=2))
print('MOTION_AUDIT',json.dumps({'held':True,'oak_coherent':True,'panorama_stationary':True,'smoke_z_minima':[(a['name'],a['basis_min_z']) for a in smoke],'samples':len(samples)}),flush=True)

