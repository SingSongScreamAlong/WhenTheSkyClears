"""Cold validation for the owned v060 affine-staged 24fps trailer shot.

Run serially after WORLD_BUILD.json and the owned native exist. Never renders or
saves a .blend. Writes only evidence/WORLD_NATIVE_VALIDATION.json.
"""
import bpy
import numpy as np
import json, math, hashlib, traceback
from pathlib import Path

O=Path(__file__).resolve().parents[1]
SOURCE=O/'reference/PRESERVED_STEADY_PAIR_v047.blend'
WORLD=O/'reference/PRESERVED_WORLD_v058.blend'
TARGET=O/'native/WTSC_First_Danger_Trailer_Development_v060.blend'
REPORT=O/'evidence/WORLD_NATIVE_VALIDATION.json'
SOURCE_SHA='29a4d9f794187602af43f7349f2b01c1019f39cba9f1d1278b966b78d1770103'
WORLD_SHA='13c2aee075315131eac6f85d9d726b766051a84edffa961f4ec38ecf7029a890'
ARM={'upper_arm_near','forearm_near','hand_near','head'}
BODIES={'BOY':'V046 BOY | tailored coat','GIRL':'V046 GIRL | tailored knee-length dress'}
ROOT_NAME='V047 | shared travel | steady .73125mps'
COLLECTION='V047 | AGE10 PAIR | steady ordinary walk'
G0,G1=937,1056
GS=[G0+i*.25 for i in range(477)]
TOL=.000030

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



def curves(action, omit_selected=False, world_time=False):
    if action is None:return {}
    result={}
    def clock(f):return 1+(f-G0)*1.25 if world_time else f
    for l in action.layers:
        for st in l.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    if omit_selected and channel_selected(fc.data_path):continue
                    result[fc.data_path+'|'+str(fc.array_index)]={
                        'keys':[(clock(float(k.co.x)),float(k.co.y),k.interpolation) for k in fc.keyframe_points],
                        'extrapolation':fc.extrapolation,
                        'cycles':[(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None)) for m in fc.modifiers]}
    return result


def compare_curves(a,b):
    if a.keys()!=b.keys():return False,0.,0.
    tx=vy=0.
    for name,x in a.items():
        y=b[name]
        if x['extrapolation']!=y['extrapolation'] or x['cycles']!=y['cycles'] or len(x['keys'])!=len(y['keys']):return False,tx,vy
        for p,q in zip(x['keys'],y['keys']):
            if p[2]!=q[2]:return False,tx,vy
            tx=max(tx,abs(p[0]-q[0]));vy=max(vy,abs(p[1]-q[1]))
    return tx<=.0001 and vy<=.0000002,tx,vy


def mesh_rest(ob):
    out=mesh_signature(ob,True,True)
    if out.get('shape_keys'):out['shape_keys'].pop('action',None)
    return out


def actor_snapshot(scene,world_time=False):
    collection=bpy.data.collections[COLLECTION]
    data={'meshes':{},'bones':{},'materials':{},'images':image_pixels(),'actions':{},'transforms':{}}
    for ob in collection.all_objects:
        if ob.name!=ROOT_NAME:data['transforms'][ob.name]=transform_signature(ob)
        data['actions'][ob.name+' | OBJECT']=curves(active_action(ob),ob.type=='ARMATURE',world_time)
        if ob.type=='MESH':
            data['meshes'][ob.name]=mesh_rest(ob)
            if ob.data.shape_keys:
                data['actions'][ob.name+' | KEYS']=curves(active_action(ob.data.shape_keys),False,world_time)
            for mat in ob.data.materials:
                if mat:data['materials'][mat.name]=material_signature(mat)
        if ob.type=='ARMATURE' and ob.get('age_years')==10:
            data['bones'][ob.name]=rig_rest(ob)
    assert len(data['bones'])==2
    return data


def wpoints(ob,dg):
    ev=ob.evaluated_get(dg);mesh=ev.to_mesh()
    try:
        p=np.empty(len(mesh.vertices)*3,dtype=np.float64);mesh.vertices.foreach_get('co',p);p=p.reshape(-1,3)
        m=np.array(ev.matrix_world,dtype=np.float64)
        return p@m[:3,:3].T+m[:3,3]
    finally:ev.to_mesh_clear()


def sample(scene,frame,boot_names):
    set_frame(scene,frame);dg=bpy.context.evaluated_depsgraph_get()
    rigs={w:scene.objects['V044 '+w+' | estimated joint centres'].evaluated_get(dg) for w in BODIES}
    return {'root':np.array(scene.objects[ROOT_NAME].evaluated_get(dg).matrix_world),
        'rigs':{w:np.array(r.matrix_world) for w,r in rigs.items()},
        'heads':{w:np.array(r.pose.bones['head'].matrix) for w,r in rigs.items()},
        'bones':{w:{b.name:np.array(r.matrix_world@b.matrix) for b in r.pose.bones if b.name not in ARM} for w,r in rigs.items()},
        'boots':{name:wpoints(scene.objects[name],dg) for name in boot_names}}


def transform_points(points,M):
    return points@M[:3,:3].T+M[:3,3]


def glyphs(scene):
    result={}
    for ob in scene.objects:
        if ob.type!='FONT':continue
        c=ob.data
        names=('body','size','space_character','space_word','space_line','align_x','align_y',
               'offset_x','offset_y','offset','extrude','bevel_depth','bevel_resolution',
               'resolution_u','render_resolution_u','shear','fill_mode')
        result[ob.name]={'data':{n:simple(getattr(c,n)) for n in names if hasattr(c,n)},
            'font':{'filepath':c.font.filepath,
                    'packed_sha256':hashlib.sha256(c.font.packed_file.data).hexdigest() if c.font.packed_file else None} if c.font else None,
            'characters':[(f.use_bold,f.use_italic,f.use_underline,getattr(f,'use_small_caps',False)) for f in c.body_format],
            'action':action_signature(active_action(ob)),
            'data_action':action_signature(active_action(c))}
    return result


def validate():
    assert SOURCE.exists() and WORLD.exists() and TARGET.exists()
    assert filehash(SOURCE)==SOURCE_SHA and filehash(WORLD)==WORLD_SHA
    target_sha=filehash(TARGET)
    build=json.loads((O/'evidence/WORLD_BUILD.json').read_text())
    M=np.array(build['world_registration_matrix'],dtype=np.float64)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    src=bpy.data.scenes['V047 | STEADY ORDINARY WALK | no stumble baseline'];bpy.context.window.scene=src
    set_frame(src,1);base=actor_snapshot(src)
    source_objects=bpy.data.collections[COLLECTION].all_objects
    boot_names=sorted(o.name for o in source_objects if o.type=='MESH' and o.get('proportion_role')=='boot' and not o.hide_render)
    assert len(boot_names)==4
    source_samples=[sample(src,1+(g-G0)*1.25,boot_names) for g in GS]
    print('WORLD_VALIDATOR_SOURCE_SAMPLED',len(source_samples),flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(WORLD),load_ui=False,use_scripts=False)
    old_glyph=glyphs(bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'])
    bpy.ops.wm.open_mainfile(filepath=str(TARGET),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];bpy.context.window.scene=scene;set_frame(scene,G0)
    target=actor_snapshot(scene,True);checks={};differences={'meshes':[],'materials':[],'action_keys':[]}
    for name,state in base['meshes'].items():
        if target['meshes'].get(name)!=state:differences['meshes'].append(name)
    for name,state in base['materials'].items():
        if target['materials'].get(name)!=state:differences['materials'].append(name)
    time_error=value_error=0.
    for name,state in base['actions'].items():
        ok,tx,vy=compare_curves(state,target['actions'].get(name,{}))
        time_error=max(time_error,tx);value_error=max(value_error,vy)
        if not ok:differences['action_keys'].append(name)
    checks['original_actor_rest_topology_UV_point_attributes_shape_coordinates_material_slots_exact']=not differences['meshes']
    checks['original_material_datablocks_exact_object_material_overrides_allowed']=not differences['materials']
    checks['original_actor_actions_retime_exact_except_selected_near_arm_and_head']=not differences['action_keys']
    checks['age10_rest_bones_exact']=base['bones']==target['bones']
    checks['original_actor_local_transforms_and_moved_depth_origins_preserved']=all(target['transforms'].get(n)==v for n,v in base['transforms'].items())
    image_matches={}
    target_hashes={v['pixel_sha256'] for v in target['images'].values()}
    for name,state in base['images'].items():
        image_matches[name]=state['pixel_sha256'] in target_hashes
    checks['all_original_actor_packed_image_pixels_present_unchanged']=all(image_matches.values()) and len(image_matches)>=3
    checks['all_target_FILE_images_packed']=all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.type!='RENDER_RESULT')
    checks['scene_clock_and_range']=scene.render.fps==24 and [scene.frame_start,scene.frame_end]==[G0,G1]
    root=scene.objects[ROOT_NAME]
    checks['root_parent_registration_matches_recorded_affine']=bool(root.parent) and float(np.max(np.abs(np.array(root.parent.matrix_world@root.matrix_parent_inverse)-M)))<=1e-7
    errors={k:0. for k in ('boot_world_vertex_m','root_world_matrix','rig_world_matrix','nonselected_bone_world_matrix')}
    camera_offsets=[];endpoint_rows=[]
    head_response={w:{'maximum_rotation_difference_degrees':0.,'maximum_local_pivot_change_m':0.} for w in BODIES}
    for i,g in enumerate(GS):
        actual=sample(scene,g,boot_names);before=source_samples[i]
        errors['root_world_matrix']=max(errors['root_world_matrix'],float(np.max(np.abs(actual['root']-M@before['root']))))
        for w in BODIES:
            aa,bb=actual['heads'][w],before['heads'][w]
            relative=aa[:3,:3]@np.linalg.inv(bb[:3,:3])
            u,sv,vh=np.linalg.svd(relative);rotation=u@vh
            angle=math.degrees(math.acos(max(-1.,min(1.,(float(np.trace(rotation))-1.)*.5))))
            head_response[w]['maximum_rotation_difference_degrees']=max(head_response[w]['maximum_rotation_difference_degrees'],angle)
            head_response[w]['maximum_local_pivot_change_m']=max(head_response[w]['maximum_local_pivot_change_m'],float(np.linalg.norm(aa[:3,3]-bb[:3,3])))
            errors['rig_world_matrix']=max(errors['rig_world_matrix'],float(np.max(np.abs(actual['rigs'][w]-M@before['rigs'][w]))))
            assert actual['bones'][w].keys()==before['bones'][w].keys()
            for name,m in before['bones'][w].items():
                errors['nonselected_bone_world_matrix']=max(errors['nonselected_bone_world_matrix'],
                    float(np.max(np.abs(actual['bones'][w][name]-M@m))))
        for name in boot_names:
            expected=transform_points(before['boots'][name],M)
            errors['boot_world_vertex_m']=max(errors['boot_world_vertex_m'],
                float(np.max(np.linalg.norm(actual['boots'][name]-expected,axis=1))))
        camera_offsets.append(scene.camera.matrix_world.translation.x-float(actual['root'][0,3]))
        if i in (0,len(GS)-1):
            endpoint_rows.append({'world_frame':g,'source_frame':1+(g-G0)*1.25,
                'root_world':actual['root'].tolist(),'camera_root_x_offset':camera_offsets[-1]})
    for name,error in errors.items():checks[name+'_within_30um_numeric']=error<=TOL
    checks['head_response_remains_small']=all(r['maximum_rotation_difference_degrees']<=4.0 for r in head_response.values())
    offset_range=max(camera_offsets)-min(camera_offsets)
    checks['camera_follows_root_without_second_travel']=offset_range<=TOL
    event=scene.objects['V060 | one offscreen distant flash | painted response']
    pulse_keys=[(937,0),(955,0),(956,.15),(957,1),(958,.8),(960,.23),(965,0),(1056,0)]
    settle_keys=[(937,0),(968,0),(1000,1),(1056,1)]
    pulse_rows=[];pulse_error=settle_error=0.
    for frame,value in pulse_keys:
        set_frame(scene,frame);actual=float(event['pulse']);pulse_error=max(pulse_error,abs(actual-value))
        pulse_rows.append({'frame':frame,'pulse':actual,'expected':value})
    for frame,value in settle_keys:
        set_frame(scene,frame);settle_error=max(settle_error,abs(float(event['settle'])-value))
    checks['event_pulse_actual_957_clock']=pulse_error<1e-6
    checks['event_settle_keys']=settle_error<1e-6
    new_glyph=glyphs(bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060'])
    checks['original_font_glyph_geometry_and_actions_preserved']=bool(old_glyph) and old_glyph==new_glyph
    sound_rows=[{'name':s.name,'packed':bool(s.packed_file),'filepath':s.filepath} for s in bpy.data.sounds]
    music=[r for r in sound_rows if 'When_The_Sky_Clears_Trailer_Music_100s' in r['name'] or 'When_The_Sky_Clears_Trailer_Music_100s' in r['filepath']]
    checks['original_supplied_music_packed']=bool(music) and all(r['packed'] for r in music)
    edit=bpy.data.scenes.get('WTSC_FIRST_DANGER_EDIT_v060')
    strips=list(edit.sequence_editor.strips) if edit and edit.sequence_editor else []
    sounds=[st for st in strips if st.type=='SOUND']
    checks['shot_music_uses_original_global_start']=bool(sounds) and all(st.frame_start==1 for st in sounds)
    checks['owned_natives_unchanged']=filehash(SOURCE)==SOURCE_SHA and filehash(WORLD)==WORLD_SHA and filehash(TARGET)==target_sha
    return {'all_checks_pass':all(checks.values()),'checks':checks,'source':str(SOURCE),'source_sha256':SOURCE_SHA,
        'world_source':str(WORLD),'world_source_sha256':WORLD_SHA,'native':str(TARGET),'native_sha256':target_sha,
        'world_frames':[G0,G1],'source_frames':[1,149.75],'quarter_production_samples':len(GS),
        'source_mapping':'F=1+(G-937)*1.25; source30fps -> world24fps.',
        'expected_affine':M.tolist(),'errors':errors,'numeric_tolerance':TOL,
        'camera_root_x_offset_range_m':offset_range,'allowed_head_response':head_response,
        'normalized_action_time_max_error_source_frames':time_error,'action_value_max_error':value_error,
        'protected_data_differences':differences,'original_actor_image_matches':image_matches,
        'pulse_samples':pulse_rows,'event_pulse_max_error':pulse_error,'event_settle_max_error':settle_error,
        'source_glyph_objects':list(old_glyph),'target_glyph_objects':list(new_glyph),
        'packed_music':music,'endpoint_samples':endpoint_rows,
        'no_native_save_or_render':True,
        'limits':'Read-only data and fractional-time staging validation. It does not approve hand anatomy, perceived weight, painted contacts, lighting or title readability.'}


def main():
    REPORT.parent.mkdir(exist_ok=True)
    try:result=validate()
    except Exception as exc:
        REPORT.write_text(json.dumps({'all_checks_pass':False,'exception':repr(exc),
            'traceback':traceback.format_exc(),'no_native_save_or_render':True},indent=2))
        raise
    REPORT.write_text(json.dumps(result,indent=2))
    print('WORLD_NATIVE_VALIDATION',json.dumps({'pass':result['all_checks_pass'],
        'errors':result['errors'],'failed':[k for k,v in result['checks'].items() if not v]}),flush=True)
    assert result['all_checks_pass'],[k for k,v in result['checks'].items() if not v]


if __name__=='__main__':main()
