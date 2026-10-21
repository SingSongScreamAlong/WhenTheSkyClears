"""Read-only final benchmark audit, including unchanged native character data."""
import bpy, json, hashlib, struct
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
source=Path(bpy.data.filepath); source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039']; e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039']; m=bpy.data.scenes['WTSC_MASTER_4K_106S_v039']; bpy.context.window.scene=w
def geometry(scene):
    pair=next(o for o in scene.objects if o.type=='GREASEPENCIL')
    fill=next(o for o in scene.objects if o.parent==pair and 'Near-black painted fill' in o.name)
    data={'drawing':[[list(p.vector) for p in f.drawing.attributes['position'].data] for layer in pair.data.layers for f in layer.frames], 'vertices':[list(v.co) for v in fill.data.vertices], 'polygons':[list(p.vertices) for p in fill.data.polygons], 'uv':[[list(v.uv) for v in layer.data] for layer in fill.data.uv_layers], 'pair_scale':list(pair.scale), 'fill_transform':[list(fill.location),list(fill.rotation_euler),list(fill.scale)]}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
signature=geometry(w); pair=next(o for o in w.objects if o.type=='GREASEPENCIL'); samples=[]
for f in [1537,1609,1656]:
    w.frame_set(f); bpy.context.view_layer.update()
    p=[world_to_camera_view(w,w.camera,pair.matrix_world@v.vector) for v in pair.data.layers[0].frames[0].drawing.attributes['position'].data]
    center=[(min(v.x for v in p)+max(v.x for v in p))/2,(min(v.y for v in p)+max(v.y for v in p))/2]
    assert all(abs(x-.5)<1e-5 for x in center)
    samples.append({'frame':f,'pair_center':center,'pair_root':list(pair.matrix_world.translation)})
bad=[]
for mat in bpy.data.materials:
    nt=mat.node_tree
    if nt and nt.animation_data:
        for f in nt.animation_data.drivers:
            if not f.is_valid:bad.append([mat.name,f.data_path,f.driver.expression])
assert not bad,bad
root=w.objects['v036 | Camp hearth | fixed emitter']; light=next(o for o in w.objects if o.parent==root and o.type=='LIGHT'); values=[]
for f in [1537,1561,1609,1656]:
    w.frame_set(f); bpy.context.view_layer.update(); values.append({'frame':f,'beat':root['fire_beat'],'light_energy':light.data.energy,'root':list(root.matrix_world.translation)})
    assert abs(light.data.energy-root['light_power']*root['fire_beat'])<.01
assert len({v['light_energy'] for v in values})==4 and all(v['root']==values[0]['root'] for v in values)
contacts=[o.name for o in w.objects if o.name.startswith('v039 shoe')]; assert len(contacts)==8
assert not any('ink_wash_v001' in i.filepath.lower() for i in bpy.data.images)
assert not any('FX001' in o.name for o in w.objects)
assert e.frame_end==m.frame_end==2544 and w.render.resolution_x==3840 and w.render.resolution_y==2160 and w.render.fps==24
sound=next(s for s in m.sequence_editor.strips if s.type=='SOUND'); bpy.context.window.scene=m; m.frame_set(1); m.frame_set(2401); assert sound.volume==0, sound.volume
study={'source':str(source),'source_sha256':source_sha,'benchmark_frames':[1537,1656],'benchmark_seconds':[64,69],'samples':samples,'geometry_and_uv_sha256':signature,'invalid_material_drivers':bad,'coherent_fire_values':values,'contact_objects':contacts,'v001_pack_imported':False,'frame_count':2544,'music_fade_ends_at_100s':True,'scope':'Native structural audit; artistic comparison still requires decoded moving review.'}
bpy.ops.wm.open_mainfile(filepath=str(R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend'))
baseline=geometry(bpy.data.scenes['WTSC_WORLD_CORRECTED_v037']); assert signature==baseline,(signature,baseline)
study['unchanged_character_geometry_topology_uv_and_local_transforms']=True
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha
(R/'notes/world_v016/camp_final_native_audit_v039.json').write_text(json.dumps(study,indent=2))
print('CAMP_FINAL_NATIVE_AUDIT_PASSED',json.dumps({'source_sha256':source_sha,'unchanged_character_geometry':True,'v001_pack_imported':False}),flush=True)
