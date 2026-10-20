"""Read-only v040 freeze audit and exact glyph/character comparison to v038."""
import bpy,json,struct,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v040']
def curves(id):
    if not id.animation_data or not id.animation_data.action:return []
    return [f for layer in id.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
def action(id):
    return [{'path':f.data_path,'index':f.array_index,'extrapolation':f.extrapolation,'keys':[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]} for f in curves(id)]
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
def geometry(scene):
    pair=next(o for o in scene.objects if o.type=='GREASEPENCIL');fill=next(o for o in scene.objects if o.parent==pair and 'Near-black painted fill' in o.name)
    return digest({'drawing':[[list(p.vector) for p in frame.drawing.attributes['position'].data] for layer in pair.data.layers for frame in layer.frames],'vertices':[list(v.co) for v in fill.data.vertices],'polygons':[list(p.vertices) for p in fill.data.polygons],'uv':[[list(v.uv) for v in layer.data] for layer in fill.data.uv_layers],'pair_scale':list(pair.scale),'pair_action':action(pair),'fill_transform':[list(fill.location),list(fill.rotation_euler),list(fill.scale)]})
def glyphs(scene):
    bpy.context.window.scene=scene;scene.frame_set(1);rows=[]
    for ob in sorted(scene.objects,key=lambda o:o.name):
        row={'name':ob.name,'type':ob.type,'local_matrix':[list(r) for r in ob.matrix_local],'hide_render':ob.hide_render,'animation':action(ob)}
        if ob.type=='FONT':
            d=ob.data;row['font']={a:getattr(d,a) for a in ['body','size','align_x','align_y','space_character','space_word','space_line','offset','extrude','bevel_depth','resolution_u','fill_mode','shear']};row['font']['packed_sha256']=hashlib.sha256(d.font.packed_file.data).hexdigest();row['data_animation']=action(d)
        if ob.type=='CAMERA':row['camera']={a:getattr(ob.data,a) for a in ['type','ortho_scale','lens','shift_x','shift_y','clip_start','clip_end']}
        rows.append(row)
    return digest({'objects':rows,'resolution':[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps],'film_transparent':scene.render.film_transparent,'range':[scene.frame_start,scene.frame_end]})
character_signature=geometry(w);glyph_signature=glyphs(e);bpy.context.window.scene=w;pair=next(o for o in w.objects if o.type=='GREASEPENCIL');pano=next(o for o in w.objects if o.name.startswith('v026 | Countryside panorama'));samples=[]
for f in [1,433,841,1201,1609,1921,2161,2400]:
    w.frame_set(f);bpy.context.view_layer.update();points=pair.data.layers[0].frames[0].drawing.attributes['position'].data;p=[world_to_camera_view(w,w.camera,pair.matrix_world@v.vector) for v in points];center=[(min(v.x for v in p)+max(v.x for v in p))/2,(min(v.y for v in p)+max(v.y for v in p))/2];assert all(abs(v-.5)<1e-5 for v in center)
    q=[world_to_camera_view(w,w.camera,pano.matrix_world@Vector(v)) for v in pano.bound_box];box=[min(v.x for v in q),max(v.x for v in q),min(v.y for v in q),max(v.y for v in q)];assert box[0]<=0 and box[1]>=1 and box[2]<=0 and box[3]>=1
    samples.append({'frame':f,'pair_center':center,'coverage_bounds':box})
def ancestors(socket,seen=None):
    seen=set() if seen is None else seen
    for link in socket.links:
        if link.from_node.name in seen:continue
        seen.add(link.from_node.name)
        for inp in link.from_node.inputs:ancestors(inp,seen)
    return seen
sets=[]
for mat in set(o.data.materials[0] for o in w.objects if o.type=='MESH' and any('Regional painted sets' in c.name for c in o.users_collection)):
    nt=mat.node_tree;alpha=set()
    for node in nt.nodes:
        if node.type=='MIX_SHADER':alpha|=ancestors(node.inputs[0])
    fc=curves(nt)+(list(nt.animation_data.drivers) if nt.animation_data else []);paths=[f.data_path for f in fc if any(f.data_path.startswith(nt.nodes[n].path_from_id()) for n in alpha)];assert not paths,(mat.name,paths);sets.append({'material':mat.name,'animated_alpha_paths':paths})
bad=[]
for mat in bpy.data.materials:
    if mat.node_tree and mat.node_tree.animation_data:
        for f in mat.node_tree.animation_data.drivers:
            if not f.is_valid:bad.append([mat.name,f.data_path,f.driver.expression])
assert not bad,bad
fires=[]
for root in [o for o in w.objects if o.type=='EMPTY' and 'fixed emitter' in o.name and o.name.startswith('v036')]:
    values=[]
    for f in [1609,1633]:
        w.frame_set(f);bpy.context.view_layer.update();children=[o for o in w.objects if o.parent==root];light=next(o for o in children if o.type=='LIGHT');flame=next(o for o in children if 'painted flame 0' in o.name);ev=flame.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();sig=[sum(p.co.x for p in mesh.vertices),sum(p.co.z for p in mesh.vertices)];ev.to_mesh_clear();assert abs(light.data.energy-root['light_power']*root['fire_beat'])<.01;values.append({'frame':f,'root':list(root.matrix_world.translation),'energy':light.data.energy,'flame_geometry_signature':sig})
    assert values[0]['root']==values[1]['root'] and values[0]['energy']!=values[1]['energy'] and values[0]['flame_geometry_signature']!=values[1]['flame_geometry_signature'];fires.append({'root':root.name,'evaluated_motion':values})
assert len([o for o in w.objects if o.name.startswith('v039 shoe')])==8
assert not any('ink_wash_v001' in image.filepath.lower() for image in bpy.data.images)
assert not any(n.bl_idname=='CompositorNodeImage' for n in e.compositing_node_group.nodes)
texts=[o.data.body for o in e.objects if o.type=='FONT' and 'Credits' in o.name];expected=['WHEN THE','SKY CLEARS.','The Animated Series.','2027.','A Two Truck Productions project.'];assert sorted(texts)==sorted(expected)
bpy.context.window.scene=m;sound=next(s for s in m.sequence_editor.strips if s.type=='SOUND');volumes=[]
for f in [1,2161,2281,2400,2401]:m.frame_set(f);volumes.append([f,sound.volume])
assert abs(volumes[2][1]-.5)<1e-5 and 0<volumes[3][1]<.005 and volumes[-1][1]==0
assert m.frame_end==e.frame_end==2544 and (m.render.resolution_x,m.render.resolution_y,m.render.fps)==(3840,2160,24)
picture=next(s for s in m.sequence_editor.strips if s.type=='SCENE');assert picture.scene==e and picture.frame_final_duration==2544
images={}
def collect(nt):
    if not nt:return
    for node in nt.nodes:
        if node.type=='TEX_IMAGE' and node.image and node.image.source=='FILE':images[node.image.name]=node.image
        if node.type=='GROUP':collect(node.node_tree)
for ob in w.objects:
    if hasattr(ob.data,'materials'):
        for mat in ob.data.materials:
            if mat:collect(mat.node_tree)
assert all(image.packed_file for image in images.values()) and sound.sound.packed_file
report={'source':str(source),'source_sha256':source_sha,'frames':2544,'fps':24,'total_seconds':106,'native_center_and_coverage_samples':samples,'persistent_set_alpha_audit':sets,'invalid_material_drivers':bad,'evaluated_fire_motion':fires,'exact_card_bodies':texts,'native_master_audio_volume':volumes,'music_packed':bool(sound.sound.packed_file),'native_picture_no_cached_movie':True,'v001_pack_used':False,'gait_added':False,'character_geometry_signature':character_signature,'mask_and_credits_signature':glyph_signature,'scope':'Native technical verification; artistic acceptance not inferred.'}
report['used_images_packed']=[{'name':image.name,'pixels':list(image.size)} for image in images.values()];report['master_scene']=m.name;report['world_scene']=w.name;report['picture_scene']=e.name
bpy.ops.wm.open_mainfile(filepath=str(R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend'))
assert geometry(bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'])==character_signature
assert glyphs(bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v037'])==glyph_signature
report['unchanged_character_geometry_topology_uv']=True;report['unchanged_mask_and_credits_signature']=True
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
(R/'notes/world_v016/full_native_audit_v040.json').write_text(json.dumps(report,indent=2));print('FULL_V040_NATIVE_AUDIT_PASSED',json.dumps({'source_sha256':source_sha,'frames':2544,'regional_alpha_curves':0,'unchanged_mask_and_character':True}),flush=True)
