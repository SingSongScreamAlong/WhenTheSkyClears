"""Build a separate editable v056 animation candidate after six-key visual review."""
import bpy,hashlib,json,math,runpy
from pathlib import Path

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';N=P/'native';N.mkdir(exist_ok=True)
study=runpy.run_path(str(P/'scripts'/'key_proof.py'))
S=study['S'];rig=study['rig'];yoke=study['obj'];mesh=yoke.data;base=study['base'];kinds=list(study['frames'].values())
wardrobe=bpy.data.collections['V046 | restored original painted wardrobe']
body=next(o for o in wardrobe.objects if o.parent==rig and o.get('wardrobe_role')=='body')
original=[v.co.copy() for v in body.data.vertices]
assert len(original)==1105 and not body.data.shape_keys

def yoke_shape(kind):
    rear_x,front_x,lower_z,front_z=study['shape'](kind)
    result=[]
    for index,p in enumerate(base):
        row,col=divmod(index,study['NCOL']);t=row/(study['NROW']-1);s=col/(study['NCOL']-1)
        q=p.copy();q.x+=t*t*(rear_x*(1-s)+front_x*s);q.z+=t*t*lower_z+math.sin(math.pi*t)*s*front_z;result.append(q)
    return result

param={
 'loading_near':(.014,-.008,-.005,.010,-.015,.006),
 'loading_far':(.013,-.009,-.006,.009,-.014,.006),
 'passing_near':(-.004,.004,.002,-.004,.005,-.002),
 'passing_far':(-.003,.004,.002,-.004,.004,-.002),
 'push_near':(-.007,.006,.003,-.005,.005,-.002),
 'push_far':(-.006,.005,.002,-.004,.005,-.002),
}
def bump(t,a,b):return math.sin(math.pi*(t-a)/(b-a))**2 if a<t<b else 0.
def body_shape(kind):
    p=param[kind];out=[]
    for i,v in enumerate(original):
        row,col=divmod(i,17);t=row/64;s=col/16
        sh=bump(t,.02,.37) if row>2 else 0.
        wa=bump(t,.25,.66) if row<43 else 0.
        q=v.copy();q.x+=sh*(p[0]*(1-s)+p[1]*s)+wa*(p[3]*(1-s)+p[4]*s)
        q.z+=sh*p[2]+wa*p[5];out.append(q)
    return out

anchors=[(1,{'loading_near':.1}),(4,{'loading_near':1.}),(7,{}),
 (9,{'passing_near':1.}),(11,{}),(13,{'push_near':1.}),(16,{}),
 (17,{'loading_far':.1}),(20,{'loading_far':1.}),(23,{}),
 (25,{'passing_far':1.}),(27,{}),(29,{'push_far':1.}),(32,{}),
 (33,{'loading_near':.1})]

def install(obj,geometry,label):
    assert not obj.data.shape_keys
    obj.shape_key_add(name='Basis | original fitted painting')
    keys={}
    for kind in kinds:
        key=obj.shape_key_add(name=f'V056 | {kind} | {label}')
        points=geometry(kind)
        key.data.foreach_set('co',[c for p in points for c in p])
        keys[kind]=key
    for frame,values in anchors:
        for kind,key in keys.items():
            key.value=values.get(kind,0.)
            key.keyframe_insert(data_path='value',frame=frame)
    action=obj.data.shape_keys.animation_data.action
    action.name=f'V056 | {label} authored 32-frame cloth cycle'
    curve_count=0
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    curve_count+=1
                    for point in fc.keyframe_points:
                        point.interpolation='BEZIER';point.handle_left_type='AUTO_CLAMPED';point.handle_right_type='AUTO_CLAMPED'
                    cycle=fc.modifiers.new('CYCLES');cycle.mode_before=cycle.mode_after='REPEAT'
    assert curve_count==len(kinds)
    for key in keys.values():key.value=0
    return {'object':obj.name,'keys':len(keys),'curves':curve_count,'action':action.name}

installed=[install(yoke,yoke_shape,'original-paint yoke'),install(body,body_shape,'girl fitted torso')]
S.name='V056 | ORIGINAL-PAINT SHOULDER DRAPE | v053 grounded walk'
S['V056_status']='Independent editable visual candidate; six phase-specific yoke and bodice key shapes. Not production-approved.'
S['V056_source']='Frozen v053 painted age10 walk, with exact original travel/root/camera and unchanged feet.'
S['V056_visual_caveat']='Original-paint yoke reads at shot size, but movement and costume quality require normal-speed review.'
S.frame_set(1);bpy.context.view_layer.update()
native=N/'WTSC_Girl_Original_Paint_Yoke_v056.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
src=study['SRC'];pair=study['PAIR']
assert hashlib.sha256(src.read_bytes()).hexdigest()==study['SHA']
assert hashlib.sha256(pair.read_bytes()).hexdigest()==study['psha']
info={'source':str(src),'source_sha256':study['SHA'],'original_pair_paint':str(pair),'original_pair_sha256':study['psha'],
 'native':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'source_unchanged':True,
 'source_root_camera_and_all_existing_rig_actions_untouched':True,'new_yoke_grid':[study['NROW'],study['NCOL']],
 'dress_original_uv_material_pixels_unchanged':True,'shape_actions':installed,'shape_clock_frames':32,
 'phase_anchors':anchors,'scene_frame_end':S.frame_end,'render_range_for_review':[1,65]}
(E/'NATIVE_BUILD.json').write_text(json.dumps(info,indent=2))
print('V056_NATIVE_SAVED',native,info['native_sha256'],flush=True)
