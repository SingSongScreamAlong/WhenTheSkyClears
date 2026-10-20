"""Cold read-only validation of the owned current-v046 continuation.

Run serially with Blender --background --python this_file.py after v047b exists.
This script opens only the two owned files, never saves a .blend or renders,
and writes only current_v046_continuation/evidence/COLD_NATIVE_VALIDATION.json.
"""
import bpy
import hashlib
import json
import math
import re
import traceback
from pathlib import Path
import numpy as np

OWNED = Path(__file__).resolve().parents[1]/'current_v046_continuation'
SOURCE = OWNED/'reference/PRESERVED_FINAL_v046_INPUT.blend'
TARGET = OWNED/'native/WTSC_Age10_Paired_Reach_v047b.blend'
REPORT = OWNED/'evidence/COLD_NATIVE_VALIDATION.json'
SOURCE_SHA = 'e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d'
SOURCE_SCENE = 'V046 | AGE10 BONES | restored painted clothing'
TARGET_SCENE = 'V047b | AGE TEN | reach and contact'
ARM = {'upper_arm_near','forearm_near','hand_near'}
BODIES = {'BOY':'V046 BOY | tailored coat',
          'GIRL':'V046 GIRL | tailored knee-length dress'}
NEW_PAIRS = {('V047 '+w+' | reach sleeve near'):
             ('V046 '+w+' | painted continuous rolled sleeve near')
             for w in BODIES}
NEW_PAIRS.update({('V047 '+w+' | retained paint hand fold near'):
                 ('V046 '+w+' | original painted hand near')
                 for w in BODIES})
HIDE_ALLOWED = set(NEW_PAIRS.values())
PINNED = 493
GEOMETRY_TOL = 0.000020
UPPER_TOL = 0.000002
FRAMES = [1+i/4 for i in range(373)]


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
        allow_nan=False).encode()).hexdigest()


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simple(value):
    if isinstance(value,(str,int,float,bool)) or value is None:
        return value
    try:
        return [simple(x) for x in value]
    except TypeError:
        return str(value)


def rna_values(value):
    result={}
    for prop in value.bl_rna.properties:
        name=prop.identifier
        if name in {'rna_type','users','session_uid','tag','is_updated',
                    'is_updated_data','is_evaluated','is_runtime_data',
                    'is_embedded_data','is_missing'} or prop.type in {'POINTER','COLLECTION'}:
            continue
        try:
            result[name]=simple(getattr(value,name))
        except (AttributeError,TypeError,ValueError):
            pass
    return result


def channel_selected(path):
    return any(path.startswith('pose.bones["'+n+'"].') for n in ARM)


def action_signature(action, omit_selected=False):
    if not action:
        return None
    rows=[]
    for li,layer in enumerate(action.layers):
        for si,strip in enumerate(layer.strips):
            for bi,bag in enumerate(strip.channelbags):
                for fc in bag.fcurves:
                    if omit_selected and channel_selected(fc.data_path):
                        continue
                    rows.append({'path':fc.data_path,'index':fc.array_index,
                        'group':fc.group.name if fc.group else None,
                        'extrapolation':fc.extrapolation,'mute':fc.mute,
                        'keys':[(list(k.co),list(k.handle_left),list(k.handle_right),
                                 k.interpolation,k.handle_left_type,k.handle_right_type,
                                 k.easing,k.amplitude,k.back,k.period)
                                for k in fc.keyframe_points],
                        'modifiers':[rna_values(m) for m in fc.modifiers]})
    return digest(sorted(rows,key=lambda q:(q['path'],q['index'])))


def active_action(ob):
    return ob.animation_data.action if ob.animation_data else None


def array_hash(data, field, width=1, kind=np.float32):
    arr=np.empty(len(data)*width,dtype=kind)
    data.foreach_get(field,arr)
    return hashlib.sha256(arr.tobytes()).hexdigest()


def attributes(mesh):
    out={}
    for attribute in mesh.attributes:
        data=attribute.data
        row={'domain':attribute.domain,'type':attribute.data_type,'count':len(data)}
        if len(data):
            item=data[0]
            field=next((n for n in ('value','vector','color') if hasattr(item,n)),None)
            if field is None:
                row['data']=digest([str(v) for v in data])
            else:
                val=getattr(item,field)
                width=len(val) if hasattr(val,'__len__') else 1
                kind=np.int32 if attribute.data_type.startswith(('INT','BOOLEAN')) else np.float32
                row['data']=array_hash(data,field,width,kind)
        out[attribute.name]=row
    return out


def mesh_signature(ob, include_shapes=True, include_coordinates=True):
    mesh=ob.data
    out={'vertices':len(mesh.vertices),'edges':len(mesh.edges),
         'polygons':len(mesh.polygons),'loops':len(mesh.loops),
         'faces':digest([list(p.vertices) for p in mesh.polygons]),
         'edge_indices':array_hash(mesh.edges,'vertices',2,np.int32),
         'polygon_materials':array_hash(mesh.polygons,'material_index',1,np.int32),
         'uv_layers':[(u.name,array_hash(u.data,'uv',2)) for u in mesh.uv_layers],
         'materials':[m.name if m else None for m in mesh.materials]}
    if include_coordinates:
        out['coordinates']=array_hash(mesh.vertices,'co',3)
        out['attributes']=attributes(mesh)
    if include_shapes:
        keys=mesh.shape_keys
        out['shape_keys']=None
        if keys:
            out['shape_keys']={'relative':keys.use_relative,
                'keys':[(k.name,array_hash(k.data,'co',3),
                         k.relative_key.name if k.relative_key else None,
                         k.interpolation,k.slider_min,k.slider_max)
                        for k in keys.key_blocks],
                'action':action_signature(active_action(keys))}
    return out


def socket_value(socket):
    if hasattr(socket,'default_value'):
        return simple(socket.default_value)
    return None


def material_signature(mat):
    if not mat:
        return None
    out={'name':mat.name,'settings':rna_values(mat)}
    if mat.node_tree:
        tree=mat.node_tree
        out['nodes']=[]
        for n in tree.nodes:
            row={'name':n.name,'type':n.bl_idname,'settings':rna_values(n),
                 'inputs':[(s.identifier,socket_value(s)) for s in n.inputs],
                 'image':n.image.name if hasattr(n,'image') and n.image else None}
            if hasattr(n,'color_ramp'):
                ramp=n.color_ramp
                row['ramp']={'settings':rna_values(ramp),
                    'elements':[(e.position,list(e.color)) for e in ramp.elements]}
            out['nodes'].append(row)
        out['links']=sorted((l.from_node.name,l.from_socket.identifier,
                            l.to_node.name,l.to_socket.identifier) for l in tree.links)
        out['action']=action_signature(active_action(tree))
    return digest(out)


def transform_signature(ob):
    names=('location','rotation_mode','rotation_euler','rotation_quaternion',
           'rotation_axis_angle','scale','delta_location','delta_rotation_euler',
           'delta_rotation_quaternion','delta_scale','matrix_parent_inverse')
    return {'parent':ob.parent.name if ob.parent else None,'parent_type':ob.parent_type,
            'parent_bone':ob.parent_bone,
            **{n:simple(getattr(ob,n)) for n in names}}


def rig_rest(rig):
    return {b.name:{'head':list(b.head_local),'tail':list(b.tail_local),
        'matrix':[list(r) for r in b.matrix_local],
        'parent':b.parent.name if b.parent else None,
        'connected':b.use_connect,'inherit_scale':b.inherit_scale}
        for b in rig.data.bones}


def image_pixels():
    out={}
    for im in bpy.data.images:
        if im.type=='RENDER_RESULT' or not im.packed_file:
            continue
        values=np.empty(len(im.pixels),dtype=np.float32)
        im.pixels.foreach_get(values)
        out[im.name]={'size':list(im.size),'channels':im.channels,
            'alpha_mode':im.alpha_mode,'colorspace':im.colorspace_settings.name,
            'pixel_sha256':hashlib.sha256(values.tobytes()).hexdigest()}
    return out


def set_frame(scene,frame):
    f=math.floor(frame)
    scene.frame_set(f,subframe=frame-f)
    bpy.context.view_layer.update()


def world_vertices(ob,dg):
    ev=ob.evaluated_get(dg)
    mesh=ev.to_mesh()
    try:
        values=np.empty(len(mesh.vertices)*3,dtype=np.float64)
        mesh.vertices.foreach_get('co',values)
        values=values.reshape(-1,3)
        matrix=np.array(ev.matrix_world,dtype=np.float64)
        return values@matrix[:3,:3].T+matrix[:3,3]
    finally:
        ev.to_mesh_clear()


def static_snapshot(scene):
    set_frame(scene,1)
    rigs={w:scene.objects['V044 '+w+' | estimated joint centres'] for w in BODIES}
    objects={}
    for ob in scene.objects:
        row={'type':ob.type,'transform':transform_signature(ob),
             'hide_render':ob.hide_render,'hide_viewport':ob.hide_viewport,
             'action':action_signature(active_action(ob),ob in rigs.values())}
        if ob.type=='MESH':
            row['mesh']=mesh_signature(ob,ob.name not in BODIES.values())
        objects[ob.name]=row
    materials={m.name:material_signature(m) for m in bpy.data.materials}
    return {'objects':objects,'images':image_pixels(),'materials':materials,
        'rig_rest':{w:rig_rest(r) for w,r in rigs.items()},
        'nonselected_actions':{w:action_signature(active_action(r),True) for w,r in rigs.items()},
        'camera_data':rna_values(scene.camera.data),
        'fps':scene.render.fps,'range':[scene.frame_start,scene.frame_end]}


def dynamic_snapshot(scene, frames, boot_names=None, compare=None):
    rigs={w:scene.objects['V044 '+w+' | estimated joint centres'] for w in BODIES}
    if boot_names is None:
        boot_names=sorted(o.name for o in scene.objects if o.type=='MESH'
            and o.parent in rigs.values() and o.get('proportion_role')=='boot'
            and not o.hide_render)
        assert len(boot_names)==4,boot_names
    travel=scene.objects['V045 | shared travel | new stride90percent']
    records=[]
    maxima={'body_upper_world_m':0.0,'body_lower_world_change_m':0.0,
        'boots_world_m':0.0,'root_matrix_max_abs':0.0,
        'camera_matrix_max_abs':0.0,'rig_matrix_max_abs':0.0,
        'nonselected_bone_matrix_max_abs':0.0}
    per_body={w:{'upper_m':0.0,'lower_m':0.0} for w in BODIES}
    for index,frame in enumerate(frames):
        set_frame(scene,frame)
        dg=bpy.context.evaluated_depsgraph_get()
        record={'frame':frame,'root':np.array(travel.matrix_world),
            'camera':np.array(scene.camera.matrix_world),'rigs':{},'boots':{},
            'bodies':{}}
        for who,rig in rigs.items():
            e=rig.evaluated_get(dg)
            record['rigs'][who]={'world':np.array(e.matrix_world),
                'bones':{b.name:np.array(e.matrix_world@b.matrix)
                         for b in e.pose.bones if b.name not in ARM}}
            record['bodies'][who]=world_vertices(scene.objects[BODIES[who]],dg)
        record['boots']={n:world_vertices(scene.objects[n],dg) for n in boot_names}
        if compare is None:
            records.append(record)
            continue
        before=compare[index]
        maxima['root_matrix_max_abs']=max(maxima['root_matrix_max_abs'],
            float(np.max(np.abs(record['root']-before['root']))))
        maxima['camera_matrix_max_abs']=max(maxima['camera_matrix_max_abs'],
            float(np.max(np.abs(record['camera']-before['camera']))))
        for who in rigs:
            aa,bb=record['rigs'][who],before['rigs'][who]
            maxima['rig_matrix_max_abs']=max(maxima['rig_matrix_max_abs'],
                float(np.max(np.abs(aa['world']-bb['world']))))
            assert aa['bones'].keys()==bb['bones'].keys()
            for n in aa['bones']:
                maxima['nonselected_bone_matrix_max_abs']=max(
                    maxima['nonselected_bone_matrix_max_abs'],
                    float(np.max(np.abs(aa['bones'][n]-bb['bones'][n]))))
            delta=np.linalg.norm(record['bodies'][who]-before['bodies'][who],axis=1)
            upper,lower=float(np.max(delta[:PINNED])),float(np.max(delta[PINNED:]))
            per_body[who]['upper_m']=max(per_body[who]['upper_m'],upper)
            per_body[who]['lower_m']=max(per_body[who]['lower_m'],lower)
            maxima['body_upper_world_m']=max(maxima['body_upper_world_m'],upper)
            maxima['body_lower_world_change_m']=max(maxima['body_lower_world_change_m'],lower)
        for n in boot_names:
            maxima['boots_world_m']=max(maxima['boots_world_m'],
                float(np.max(np.linalg.norm(record['boots'][n]-before['boots'][n],axis=1))))
    return {'records':records,'boot_names':boot_names,'maxima':maxima,'body_changes':per_body}


def validate():
    assert SOURCE.exists() and TARGET.exists(), 'Both owned native files must exist before validation.'
    assert filehash(SOURCE)==SOURCE_SHA,'Owned input does not match the final v046 snapshot.'
    target_sha=filehash(TARGET)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    source_scene=bpy.data.scenes[SOURCE_SCENE]
    bpy.context.window.scene=source_scene
    source=static_snapshot(source_scene)
    baseline=dynamic_snapshot(source_scene,FRAMES)
    print('COLD_SOURCE_SAMPLED',len(FRAMES),flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(TARGET),load_ui=False,use_scripts=False)
    target_scene=bpy.data.scenes[TARGET_SCENE]
    bpy.context.window.scene=target_scene
    target=static_snapshot(target_scene)
    checks={}
    missing=sorted(set(source['objects'])-set(target['objects']))
    checks['all_original_scene_objects_retained']=not missing
    unexpected=sorted(set(target['objects'])-set(source['objects'])-set(NEW_PAIRS))
    checks['only_expected_new_near_arm_objects']=not unexpected
    changed={'transforms':[],'raw_mesh_data':[],'visibility':[],
             'object_actions':[],'source_materials':[]}
    for name,old in source['objects'].items():
        if name not in target['objects']:
            continue
        new=target['objects'][name]
        if old['transform']!=new['transform']:
            changed['transforms'].append(name)
        if old.get('mesh')!=new.get('mesh'):
            changed['raw_mesh_data'].append(name)
        if name not in HIDE_ALLOWED and (old['hide_render'],old['hide_viewport'])!=(new['hide_render'],new['hide_viewport']):
            changed['visibility'].append(name)
        if old['action']!=new['action']:
            changed['object_actions'].append(name)
    for name,value in source['materials'].items():
        if target['materials'].get(name)!=value:
            changed['source_materials'].append(name)
    checks.update({'original_object_transforms_exact':not changed['transforms'],
        'original_mesh_topology_rest_UV_attributes_materials_and_nonbody_shapes_exact':not changed['raw_mesh_data'],
        'only_original_selected_sleeve_hand_visibility_may_change':not changed['visibility'],
        'original_object_actions_except_selected_arm_channels_exact':not changed['object_actions'],
        'original_material_graphs_and_properties_exact':not changed['source_materials'],
        'all_packed_image_pixels_and_settings_exact':source['images']==target['images'] and len(source['images'])>=3,
        'age10_rest_bones_exact':source['rig_rest']==target['rig_rest'],
        'nonselected_rig_action_curves_exact':source['nonselected_actions']==target['nonselected_actions'],
        'camera_projection_data_exact':source['camera_data']==target['camera_data'],
        'source_clock_range_exact':source['fps']==target['fps']==30 and source['range']==target['range']==[1,94]})
    new_drawing={}
    for name,original in NEW_PAIRS.items():
        ob=target_scene.objects.get(name)
        old=source['objects'][original]['mesh']
        if ob:
            signature=mesh_signature(ob,False,False)
            original_signature={k:v for k,v in old.items() if k not in {'coordinates','attributes','shape_keys'}}
            new_drawing[name]=signature==original_signature
        else:
            new_drawing[name]=False
    checks['new_selected_drawings_retain_original_topology_UV_materials']=all(new_drawing.values())
    sampled=dynamic_snapshot(target_scene,FRAMES,baseline['boot_names'],baseline['records'])
    maxima=sampled['maxima']
    checks['upper_493_body_vertices_unchanged_within_2um']=maxima['body_upper_world_m']<=UPPER_TOL
    for metric in ('boots_world_m','root_matrix_max_abs','camera_matrix_max_abs',
                   'rig_matrix_max_abs','nonselected_bone_matrix_max_abs'):
        checks[metric+'_within_20um_or_matrix_tolerance']=maxima[metric]<=GEOMETRY_TOL
    checks['both_lower_garments_have_measured_changes']=all(
        value['lower_m']>0.0001 for value in sampled['body_changes'].values())
    checks['native_files_unchanged_by_validation']=filehash(SOURCE)==SOURCE_SHA and filehash(TARGET)==target_sha
    return {'source':str(SOURCE),'source_sha256':SOURCE_SHA,'candidate':str(TARGET),
        'candidate_sha256':target_sha,'read_only_native_open':True,
        'no_native_save_or_render':True,'frames':[1,94],'quarter_frame_samples':len(FRAMES),
        'checks':checks,'all_checks_pass':all(checks.values()),
        'maxima':maxima,'per_body_world_changes':sampled['body_changes'],
        'tolerances_m':{'upper_body':UPPER_TOL,'boots_roots_camera_nonselected':GEOMETRY_TOL},
        'missing_original_objects':missing,'unexpected_new_objects':unexpected,
        'changed_protected_data':changed,'new_drawing_topology_UV_material_checks':new_drawing,
        'body_material_signatures':{name:source['objects'][name]['mesh'] for name in BODIES.values()},
        'packed_image_pixel_signatures':source['images'],
        'nonselected_action_curve_hashes':{'source':source['nonselected_actions'],'candidate':target['nonselected_actions']},
        'allowed_changes':['Two lower-garment native shape-key actions; upper 493 vertices pinned.',
            'Only upper_arm_near, forearm_near and hand_near pose channels on each child.',
            'New selected sleeve drawing cache and native hand-fold copies.',
            'Original selected hand/sleeve objects may be hidden, while their source geometry remains intact.'],
        'quality_limit':'Cold geometry and data preservation checks do not approve hand anatomy, perceived weight, cloth appeal or final artistic quality.'}


def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=validate()
    except Exception as exc:
        REPORT.write_text(json.dumps({'all_checks_pass':False,'exception':repr(exc),
            'traceback':traceback.format_exc(),'source':str(SOURCE),'candidate':str(TARGET),
            'no_native_save_or_render':True},indent=2))
        raise
    REPORT.write_text(json.dumps(result,indent=2))
    print('COLD_NATIVE_VALIDATION',json.dumps({'all_checks_pass':result['all_checks_pass'],
        'maxima':result['maxima'],'failed':[k for k,v in result['checks'].items() if not v]}),flush=True)
    assert result['all_checks_pass'],[k for k,v in result['checks'].items() if not v]


if __name__=='__main__':
    main()
