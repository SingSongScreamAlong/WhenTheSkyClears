"""Cold compare frozen v053 and isolated v056 contacts, rig curves and import."""
import bpy,hashlib,json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';build=json.loads((E/'NATIVE_BUILD.json').read_text())
source=Path(build['source']);native=Path(build['native'])
assert hashlib.sha256(source.read_bytes()).hexdigest()==build['source_sha256']
assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
def curves(action):
    return {(fc.data_path,fc.array_index):hashlib.sha256(repr(([(tuple(p.co),p.interpolation) for p in fc.keyframe_points],[(m.type,m.mode_before,m.mode_after) for m in fc.modifiers if m.type=='CYCLES'])).encode()).hexdigest()
            for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves}
def snapshot():
    rigs={who:bpy.data.objects[f'V044 {who} | estimated joint centres'] for who in ('BOY','GIRL')}
    return {'root':curves(bpy.data.objects['V048 | shared travel | steady .73125mps'].animation_data.action),
            'camera':curves(bpy.context.scene.camera.animation_data.action),
            'rigs':{who:curves(obj.animation_data.action) for who,obj in rigs.items()},
            'bones':{who:{b.name:(tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in obj.data.bones} for who,obj in rigs.items()},
            'body_base':hashlib.sha256(repr([tuple(v.co) for v in bpy.data.objects['V046 GIRL | tailored knee-length dress'].data.vertices]).encode()).hexdigest()}
def boots():
    dg=bpy.context.evaluated_depsgraph_get();rigs=[bpy.data.objects[f'V044 {who} | estimated joint centres'] for who in ('BOY','GIRL')]
    objects=[o for o in bpy.context.scene.objects if o.parent in rigs and o.get('proportion_role')=='boot']
    return np.array([list(e.matrix_world@v.co) for o in objects for e in [o.evaluated_get(dg)] for v in e.data.vertices])
ref=[];max_boot=0.;snapshots=[]
for tag,path,scene in [('v053',source,'V053 | AUTHORED WALK BEATS | v051 grounded feet'),('v056',native,'V056 | ORIGINAL-PAINT SHOULDER DRAPE | v053 grounded walk')]:
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S
    snapshots.append(snapshot())
    if tag=='v056':
        collection=bpy.data.collections['V053 | AGE10 PAIR | authored walk beats']
        yoke=bpy.data.objects['V056 GIRL | pose-specific original painted shoulder yoke']
        assert yoke.name in collection.all_objects
        assert len(yoke.data.shape_keys.key_blocks)==7
        assert yoke.data.materials[0].node_tree
        original_paint=next(n.image for n in yoke.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')
        assert original_paint.packed_file and tuple(original_paint.size)==(1672,941)
        assert S.frame_end==257
    for i in range(129):
        f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();positions=boots()
        if tag=='v053':ref.append(positions)
        else:max_boot=max(max_boot,float(np.max(np.linalg.norm(positions-ref[i],axis=1))))
a,b=snapshots
assert a==b,'One or more preserved curve/bone/base mesh snapshots changed'
assert max_boot<5e-5,max_boot
assert hashlib.sha256(source.read_bytes()).hexdigest()==build['source_sha256']
assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
production=ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'
production_sha=hashlib.sha256(production.read_bytes()).hexdigest()
assert production_sha=='f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'
result={'cold_reopen_both':True,'root_camera_rig_curves_rest_bones_and_body_base_exact':True,
 'review_samples':129,'maximum_boot_world_difference_m':max_boot,'append_collection':'V053 | AGE10 PAIR | authored walk beats',
 'new_yoke_is_inside_append_collection':True,'source_sha256':build['source_sha256'],'native_sha256':build['native_sha256'],
 'original_yoke_paint_packed_in_native':True,
 'production_sha256':production_sha,'no_scene_duration_change':True,
 'scope':'Technical contact/import check only; does not establish visual acceptance.'}
(E/'COLD_TECHNICAL_VALIDATION.json').write_text(json.dumps(result,indent=2))
print('V056_COLD_TECHNICAL_VALIDATION_PASS',max_boot,flush=True)
