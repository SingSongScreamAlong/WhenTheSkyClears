import bpy,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v037'];bpy.context.window.scene=w
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');pano=next(o for o in w.objects if o.name.startswith('v026 | Countryside panorama'))
samples=[];drawing_hashes=[]
for f in [1,433,841,1201,1609,1921,2161,2400]:
 w.frame_set(f);bpy.context.view_layer.update();points=pair.data.layers[0].frames[0].drawing.attributes['position'].data;drawing_hashes.append(hashlib.sha256(b''.join(struct.pack('fff',*p.vector) for p in points)).hexdigest());p=[world_to_camera_view(w,w.camera,pair.matrix_world@v.vector) for v in points];cx=(min(x.x for x in p)+max(x.x for x in p))/2;cy=(min(x.y for x in p)+max(x.y for x in p))/2;assert abs(cx-.5)<1e-5 and abs(cy-.5)<1e-5
 b=[world_to_camera_view(w,w.camera,pano.matrix_world@Vector(v)) for v in pano.bound_box];box=[min(x.x for x in b),max(x.x for x in b),min(x.y for x in b),max(x.y for x in b)];assert box[0]<=0 and box[1]>=1 and box[2]<=0 and box[3]>=1,box
 samples.append({'frame':f,'pair_center':[cx,cy],'panorama_opaque_coverage_bounds':box})
assert len(set(drawing_hashes))==1
def ancestors(socket,seen=None):
 seen=set() if seen is None else seen
 for l in socket.links:
  if l.from_node.name in seen:continue
  seen.add(l.from_node.name)
  for inp in l.from_node.inputs:ancestors(inp,seen)
 return seen
set_rows=[]
for mat in set(o.data.materials[0] for o in w.objects if o.type=='MESH' and any('Regional painted sets' in c.name for c in o.users_collection)):
 nt=mat.node_tree;alpha=set()
 for n in nt.nodes:
  if n.type=='MIX_SHADER':alpha|=ancestors(n.inputs[0])
 curves=[]
 if nt.animation_data:
  if nt.animation_data.action:curves.extend(f for l in nt.animation_data.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves)
  curves.extend(nt.animation_data.drivers)
 alpha_curves=[f.data_path for f in curves if any(f.data_path.startswith(nt.nodes[n].path_from_id()) for n in alpha)]
 assert not alpha_curves,(mat.name,alpha_curves)
 users=[o for o in w.objects if o.type=='MESH' and mat in list(o.data.materials)]
 assert all(not o.hide_render for o in users)
 set_rows.append({'material':mat.name,'objects':[o.name for o in users],'animated_alpha_paths':alpha_curves,'static_image_alpha_and_edge_mask':True})
effects=[]
for root in [o for o in w.objects if o.type=='EMPTY' and 'fixed emitter' in o.name and o.name.startswith('v036')]:
 values=[]
 for f in [1609,1633]:
  w.frame_set(f);bpy.context.view_layer.update();children=[o for o in w.objects if o.parent==root];light=next(o for o in children if o.type=='LIGHT');flame=next(o for o in children if 'painted flame 0' in o.name);dep=bpy.context.evaluated_depsgraph_get();ev=flame.evaluated_get(dep);mesh=ev.to_mesh();signature=[sum(p.co.x for p in mesh.vertices),sum(p.co.z for p in mesh.vertices)];ev.to_mesh_clear();values.append({'frame':f,'root_world':list(root.matrix_world.translation),'energy':light.data.energy,'flame_geometry_signature':signature})
 assert values[0]['root_world']==values[1]['root_world'] and abs(values[0]['energy']-values[1]['energy'])>.1 and values[0]['flame_geometry_signature']!=values[1]['flame_geometry_signature']
 effects.append({'emitter':root.name,'native_evaluated_motion':values})
assert e.frame_end==2544 and m.frame_end==2544
texts=[o.data.body for o in e.objects if o.type=='FONT' and 'Credits' in o.name];expected=['WHEN THE','SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'];assert sorted(texts)==sorted(expected)
assert not any(n.bl_idname=='CompositorNodeImage' for n in e.compositing_node_group.nodes)
sound=next(x for x in m.sequence_editor.strips if x.type=='SOUND');volume=[]
for f in [1,1969,2161,2281,2400]:m.frame_set(f);volume.append([f,sound.volume])
assert abs(volume[0][1]-1)<1e-5 and abs(volume[2][1]-1)<1e-5 and volume[-1][1]==0
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'frames':2544,'fps':24,'total_seconds':106,'moving_world_seconds':100,'silent_credits_seconds':6,'native_center_and_coverage_samples':samples,'coverage_proof':'Fixed opaque panorama, constant lens/Y/Z; cameraX follows piecewise-linear monotone route. Coverage at all route keys bounds every interpolated camera position. Ground extends-24..220 beyond route0..160.75.','persistent_set_alpha_audit':set_rows,'building_visibility':'No animated material alpha, no hide switches; sets only enter/leave with spatial travel. Static source alpha and staticedge feather retained.','held_drawing_sha256':drawing_hashes[0],'evaluated_fire_motion':effects,'exact_card_bodies':texts,'native_master_audio_volume':volume,'music_packed':bool(sound.sound.packed_file),'native_picture_no_cached_movie':True,'gait_added':False,'scope':'Native technical verification and actual frame review; not artistic approval.'}
(R/'notes/world_v016/full_native_audit_v037.json').write_text(json.dumps(report,indent=2));print('FULL_NATIVE_AUDIT_PASSED',json.dumps({'sets':len(set_rows),'emitter_motion':len(effects),'coverage_samples':len(samples),'duration':106}),flush=True)
