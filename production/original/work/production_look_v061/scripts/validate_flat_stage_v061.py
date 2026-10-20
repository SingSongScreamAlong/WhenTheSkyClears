"""Cold, material-preserving validation of the flat v061 actor stage.

snapshot(scene) returns JSON-compatible invariants at production frame937.
apply(scene, reference_path) reads reference_path.with_suffix('.invariants.json')
and validates the CURRENT scene; it never opens or saves a native and never renders.
The optional command-line entry point cold-opens reference once, records it,
cold-opens the requested target, validates, and writes only JSON evidence.
"""
import bpy
import numpy as np
import math, json, hashlib, argparse
from pathlib import Path

ROOT_NAME='V047 | shared travel | steady .73125mps'
G0,G1=937,1056
FRAMES=tuple(G0+i*.25 for i in range(477))
SCHEMA='WTSC_FLAT_STAGE_INVARIANTS_v061_2'

def _hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _filehash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def _simple(value):
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    try:return [_simple(x) for x in value]
    except TypeError:return str(value)

def _frame(scene,f):
    i=math.floor(f);scene.frame_set(i,subframe=f-i)
    bpy.context.view_layer.update()

def _array(items,field,width=1,dtype=np.float32):
    a=np.empty(len(items)*width,dtype=dtype);items.foreach_get(field,a)
    return hashlib.sha256(a.tobytes()).hexdigest()

def _rna(value):
    out={}
    skip={'rna_type','name','name_full','users','session_uid','tag','is_updated',
          'is_updated_data','is_evaluated','is_runtime_data','is_embedded_data',
          'is_missing','is_library_indirect','is_editable','execution_time'}
    for p in value.bl_rna.properties:
        if p.identifier in skip or p.type in {'POINTER','COLLECTION'}:continue
        try:out[p.identifier]=_simple(getattr(value,p.identifier))
        except (AttributeError,TypeError,ValueError):pass
    return out

def _action_rows(idblock):
    ad=getattr(idblock,'animation_data',None);a=ad.action if ad else None
    if a is None:return None
    rows=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for f in bag.fcurves:
                    rows.append({'path':f.data_path,'index':f.array_index,
                        'extrapolation':f.extrapolation,'mute':f.mute,
                        'keys':[(list(k.co),list(k.handle_left),list(k.handle_right),
                            k.interpolation,k.handle_left_type,k.handle_right_type,
                            k.easing,k.amplitude,k.back,k.period) for k in f.keyframe_points],
                        'modifiers':[_rna(m) for m in f.modifiers]})
    return sorted(rows,key=lambda r:(r['path'],r['index']))

def _action(idblock):
    rows=_action_rows(idblock)
    return None if rows is None else _hash(rows)

def _drivers(idblock):
    ad=getattr(idblock,'animation_data',None)
    if not ad:return None
    rows=[]
    for fc in ad.drivers:
        d=fc.driver
        rows.append({'path':fc.data_path,'index':fc.array_index,'type':d.type,
            'expression':d.expression,'use_self':d.use_self,
            'variables':[(v.name,v.type,[(t.id.name if t.id else None,
                t.data_path,getattr(t,'bone_target',''),getattr(t,'transform_type',''),
                getattr(t,'transform_space','')) for t in v.targets]) for v in d.variables]})
    return _hash(rows)

def _material(mat):
    if mat is None:return None
    out={'settings':_rna(mat),'nodes':[],'links':[]}
    if mat.node_tree:
        for n in mat.node_tree.nodes:
            row={'name':n.name,'type':n.bl_idname,'settings':_rna(n),
                'inputs':[(s.identifier,_simple(s.default_value) if hasattr(s,'default_value') else None) for s in n.inputs],
                'image':n.image.name if hasattr(n,'image') and n.image else None}
            if hasattr(n,'color_ramp'):
                row['ramp']={'settings':_rna(n.color_ramp),'elements':[(e.position,list(e.color)) for e in n.color_ramp.elements]}
            out['nodes'].append(row)
        out['links']=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in mat.node_tree.links)
        out['action']=_action(mat.node_tree);out['drivers']=_drivers(mat.node_tree)
    return _hash(out)

def _attributes(mesh):
    out={}
    for a in mesh.attributes:
        row={'type':a.data_type,'domain':a.domain,'count':len(a.data)}
        if a.data:
            item=a.data[0];field=next((k for k in ('value','vector','color') if hasattr(item,k)),None)
            if field is None:row['value']=_hash([str(v) for v in a.data])
            else:
                v=getattr(item,field)
                if isinstance(v,str):row['value']=_hash([getattr(x,field) for x in a.data])
                else:
                    width=len(v) if hasattr(v,'__len__') else 1
                    row['value']=_array(a.data,field,width,np.int32 if a.data_type.startswith(('INT','BOOLEAN')) else np.float32)
        out[a.name]=row
    return out

def _mesh(ob):
    m=ob.data
    out={'count':[len(m.vertices),len(m.edges),len(m.polygons),len(m.loops)],
        'co':_array(m.vertices,'co',3),'edges':_array(m.edges,'vertices',2,np.int32),
        'faces':_hash([list(p.vertices) for p in m.polygons]),
        'polygon_material_index':_array(m.polygons,'material_index',1,np.int32),
        'uv':[(u.name,_array(u.data,'uv',2)) for u in m.uv_layers],
        'attributes':_attributes(m),'data_material_slots':[x.name if x else None for x in m.materials],
        'vertex_groups':_hash([(g.name,g.lock_weight) for g in ob.vertex_groups]),
        'weights':_hash([[(g.group,g.weight) for g in v.groups] for v in m.vertices])}
    k=m.shape_keys
    out['shapes']=None if not k else {'relative':k.use_relative,
        'keys':[(b.name,_array(b.data,'co',3),b.relative_key.name if b.relative_key else None,
                 b.interpolation,b.slider_min,b.slider_max) for b in k.key_blocks],
        'action':_action(k),'drivers':_drivers(k)}
    return out

def _transforms(ob):
    fields=('location','rotation_mode','rotation_euler','rotation_quaternion',
        'rotation_axis_angle','scale','delta_location','delta_rotation_euler',
        'delta_rotation_quaternion','delta_scale')
    result={'parent':ob.parent.name if ob.parent else None,'parent_type':ob.parent_type,
        'parent_bone':ob.parent_bone,**{k:_simple(getattr(ob,k)) for k in fields}}
    if ob.name!=ROOT_NAME:result['matrix_parent_inverse']=_simple(ob.matrix_parent_inverse)
    return result

def _descends(ob,root):
    p=ob
    while p:
        if p==root:return True
        p=p.parent
    return False

def _rest(rig):
    return {b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length,
        'matrix':_simple(b.matrix_local),'parent':b.parent.name if b.parent else None,
        'connected':b.use_connect,'inherit_scale':b.inherit_scale} for b in rig.data.bones}

def _images():
    result={}
    for im in bpy.data.images:
        if im.type=='RENDER_RESULT' or not im.packed_file:continue
        a=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(a)
        result[im.name]={'size':list(im.size),'channels':im.channels,'alpha_mode':im.alpha_mode,
            'colorspace':im.colorspace_settings.name,'pixel_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
    return result

def _camera(ob):
    c=ob.data
    fields=('type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end','ortho_scale')
    dof_fields=('use_dof','focus_distance','aperture_fstop','aperture_blades','aperture_rotation','aperture_ratio')
    return {'data':{k:_simple(getattr(c,k)) for k in fields},
        'dof':{**{k:_simple(getattr(c.dof,k)) for k in dof_fields},
            'focus_object':c.dof.focus_object.name if c.dof.focus_object else None},
        'transform':_transforms(ob),'action':_action(ob),'action_rows':_action_rows(ob),
        'data_action':_action(c),'drivers':_drivers(ob),'data_drivers':_drivers(c)}

def _compare_camera(source,actual):
    """Authorize only Z-1.30m, corresponding shift_y, and f/6.3 -> f/5.6."""
    dz=1.30
    expected_z=source['transform']['location'][2]-dz
    expected_shift=source['data']['shift_y']+dz*source['data']['lens']/(source['data']['sensor_width']*15.64)
    result={};checks={}
    checks['camera_source_matches_planned_3m_f6_3_basis']=abs(source['transform']['location'][2]-3.)<1e-6 and abs(source['dof']['aperture_fstop']-6.3)<1e-6
    checks['camera_lowered_exactly_1_3m']=abs(actual['transform']['location'][2]-expected_z)<2e-7
    checks['camera_shift_y_matches_15_64m_compensation']=abs(actual['data']['shift_y']-expected_shift)<2e-7
    checks['camera_aperture_is_planned_f5_6']=abs(actual['dof']['aperture_fstop']-5.6)<2e-7
    normalized=json.loads(json.dumps(actual['transform']))
    normalized['location'][2]=source['transform']['location'][2]
    checks['camera_all_other_transform_fields_exact']=normalized==source['transform']
    normalized=json.loads(json.dumps(actual['data']))
    normalized['shift_y']=source['data']['shift_y']
    checks['camera_lens_projection_Xshift_sensor_clipping_exact']=normalized==source['data']
    normalized=json.loads(json.dumps(actual['dof']))
    normalized['aperture_fstop']=source['dof']['aperture_fstop']
    checks['camera_all_other_focus_and_dof_fields_exact']=normalized==source['dof']
    checks['camera_data_action_and_drivers_exact']=all(actual.get(k)==source.get(k) for k in ('data_action','drivers','data_drivers'))
    before=source['action_rows'];after=actual['action_rows']
    action_ok=(before is None)==(after is None);shift_error=0.;changed_curves=0
    if before is not None and after is not None:
        normalized=json.loads(json.dumps(after))
        if len(before)!=len(normalized):action_ok=False
        else:
            for src,dst in zip(before,normalized):
                if src['path']=='location' and src['index']==2:
                    changed_curves+=1
                    if len(src['keys'])!=len(dst['keys']):action_ok=False;continue
                    for sk,ak in zip(src['keys'],dst['keys']):
                        for coordinate in (0,1,2):  # key, left handle, right handle
                            if sk[coordinate][0]!=ak[coordinate][0]:action_ok=False
                            err=abs(ak[coordinate][1]-(sk[coordinate][1]-dz))
                            shift_error=max(shift_error,err)
                            if err>2e-7:action_ok=False
                            ak[coordinate][1]=sk[coordinate][1]
            action_ok=action_ok and normalized==before
    checks['camera_actions_exact_except_Z_key_and_handle_values_minus_1_3m']=action_ok
    result={'plan':{'height_delta_m':-dz,'focus_plane_depth_m':15.64,'aperture_fstop':5.6,
                   'unchanged':'X/Y, rotations, lens, sensor, focus target/distance, frame times, interpolation, non-Z keys and handles, all drivers'},
        'source_height_m':source['transform']['location'][2],
        'expected_height_m':expected_z,'actual_height_m':actual['transform']['location'][2],
        'source_shift_y':source['data']['shift_y'],'expected_shift_y':expected_shift,'actual_shift_y':actual['data']['shift_y'],
        'source_aperture_fstop':source['dof']['aperture_fstop'],'actual_aperture_fstop':actual['dof']['aperture_fstop'],
        'Z_action_curves_changed':changed_curves,'maximum_Z_key_or_handle_shift_error_m':shift_error}
    return checks,result

def snapshot(scene):
    """Data-only source record; changes frame temporarily and restores it."""
    original=scene.frame_current+scene.frame_subframe
    try:
        _frame(scene,G0)
        root=scene.objects.get(ROOT_NAME)
        if not root or not root.parent:raise RuntimeError('Missing shared root/stage')
        actors=sorted((o for o in scene.objects if _descends(o,root)),key=lambda o:o.name)
        out={'schema':SCHEMA,'snapshot_frame':G0,'root':ROOT_NAME,
            'stage_world_matrix':_simple(root.parent.matrix_world),
            'meshes':{},'rig_rest':{},'transforms':{},'actions':{},'drivers':{},
            'modifiers':{},'materials':{},'images':_images(),'boots':[],
            'camera':_camera(scene.camera)}
        for ob in actors:
            out['transforms'][ob.name]=_transforms(ob)
            out['actions'][ob.name]=_action(ob);out['drivers'][ob.name]=_drivers(ob)
            out['modifiers'][ob.name]=[{'type':m.type,'name':m.name,'settings':_rna(m),
                'object':m.object.name if hasattr(m,'object') and m.object else None} for m in ob.modifiers]
            if ob.type=='ARMATURE':
                out['rig_rest'][ob.name]=_rest(ob)
            if ob.type=='MESH':
                out['meshes'][ob.name]=_mesh(ob)
                for mat in ob.data.materials:
                    if mat:out['materials'][mat.name]=_material(mat)
                if ob.get('proportion_role')=='boot' and not ob.hide_render:out['boots'].append(ob.name)
        if len(out['rig_rest'])!=2 or len(out['boots'])!=4:
            raise RuntimeError('Expected two source rigs and four visible boot meshes')
        # Sidecars are JSON: canonicalize containers, preserving every scalar/hash.
        # This removes tuple/list representation differences without dropping fields.
        return json.loads(json.dumps(out,allow_nan=False))
    finally:_frame(scene,original)

def _points(ob,dg):
    e=ob.evaluated_get(dg);m=e.to_mesh()
    try:
        p=np.empty(len(m.vertices)*3,dtype=np.float64);m.vertices.foreach_get('co',p);p=p.reshape(-1,3)
        w=np.array(e.matrix_world,dtype=np.float64);return p@w[:3,:3].T+w[:3,3]
    finally:e.to_mesh_clear()

def _phase(name,ob,f):
    # Metadata and actual source vertex-group assignment, never a guessed gait oscillator.
    names=set(g.name for g in ob.vertex_groups)
    side=next((s for s in ('near','far') if s in name.lower()),None)
    if side is None:
        candidates=[s for s in ('near','far') if 'foot_'+s in names]
        side=candidates[0] if len(candidates)==1 else None
    who=next((w for w in ('BOY','GIRL') if w in name or (ob.parent and w in ob.parent.name)),None)
    if side is None or who is None:return None
    return (f+(2 if who=='GIRL' else 0)-1-(16 if side=='far' else 0))%32

def apply(scene,reference_path):
    """Validate an already-open flat-stage scene. No native open/save/render."""
    ref=Path(reference_path).resolve();sidecar=ref.with_suffix('.invariants.json')
    source=json.loads(sidecar.read_text());expected_sha=source.get('reference_sha256')
    if source.get('schema')!=SCHEMA or not expected_sha or _filehash(ref)!=expected_sha:
        raise RuntimeError('Source invariants schema/hash mismatch')
    before_frame=scene.frame_current+scene.frame_subframe
    try:
        actual=snapshot(scene);checks={};differences={}
        for name in ('meshes','rig_rest','transforms','actions','drivers','modifiers','materials'):
            differences[name]=[n for n,v in source[name].items() if actual[name].get(n)!=v]
            checks[name+'_source_exact']=not differences[name]
        differences['images']=[n for n,v in source['images'].items() if actual['images'].get(n)!=v]
        checks['all_source_packed_image_pixels_and_registration_exact']=not differences['images']
        checks['all_target_FILE_images_packed']=all(i.packed_file for i in bpy.data.images if i.source=='FILE' and i.type!='RENDER_RESULT')
        camera_checks,camera_plan=_compare_camera(source['camera'],actual['camera']);checks.update(camera_checks)
        checks['scene_24fps_937_1056']=abs(scene.render.fps/scene.render.fps_base-24)<1e-9 and (scene.frame_start,scene.frame_end)==(G0,G1)
        root=scene.objects[ROOT_NAME];anchor=np.array(source['stage_world_matrix'],dtype=np.float64)
        stage=np.array(root.parent.matrix_world,dtype=np.float64)
        inverse=np.array(root.matrix_parent_inverse,dtype=np.float64)
        checks['root_parent_inverse_identity_no_floor_shear']=float(np.max(np.abs(inverse-np.eye(4))))<1e-8
        checks['stage_is_source_translation_only']=float(np.max(np.abs(stage-anchor)))<1e-7 and float(np.max(np.abs(stage[:3,:3]-np.eye(3))))<1e-8
        floor_z=float(stage[2,3]);boots=source['boots']
        rows={n:{'minimum_clearance_m':float('inf'),'maximum_clearance_m':-float('inf'),
            'stance_maximum_abs_clearance_m':0.,'stance_samples':0,'below_floor_samples':0,'near_floor_samples':0} for n in boots}
        offsets=[];floor_support=None;floor_errors=[]
        floor=scene.objects.get('V061 | physical path and bank | actual shadow receiver')
        if floor and floor.type=='MESH':
            v=np.array([floor.matrix_world@p.co for p in floor.data.vertices],dtype=np.float64)
            corridor=v[(v[:,1]>=-.9)&(v[:,1]<=2.)]
            if len(corridor):floor_support={'corridor_vertices':len(corridor),
                'maximum_flat_corridor_height_error_m':float(np.max(np.abs(corridor[:,2]-floor_z)))}
        checks['physical_corridor_matches_flat_actor_floor']=bool(floor_support) and floor_support['maximum_flat_corridor_height_error_m']<1e-6
        root_rotation_error=0.;stage_error=0.;endpoints=[]
        for i,g in enumerate(FRAMES):
            _frame(scene,g);dg=bpy.context.evaluated_depsgraph_get()
            rw=np.array(root.evaluated_get(dg).matrix_world,dtype=np.float64)
            root_rotation_error=max(root_rotation_error,float(np.max(np.abs(rw[:3,:3]-np.eye(3)))))
            stage_error=max(stage_error,float(np.max(np.abs(np.array(root.parent.matrix_world)-anchor))))
            offsets.append(float(scene.camera.matrix_world.translation.x-rw[0,3]))
            f=1+(g-G0)*1.25
            for name in boots:
                ob=scene.objects[name];p=_points(ob,dg);clearance=float(np.min(p[:,2])-floor_z);r=rows[name]
                r['minimum_clearance_m']=min(r['minimum_clearance_m'],clearance)
                r['maximum_clearance_m']=max(r['maximum_clearance_m'],clearance)
                r['below_floor_samples']+=int(clearance<-.00005);r['near_floor_samples']+=int(abs(clearance)<=.0003)
                phase=_phase(name,ob,f)
                if phase is not None and phase<=18.8+1e-8:
                    r['stance_samples']+=1;r['stance_maximum_abs_clearance_m']=max(r['stance_maximum_abs_clearance_m'],abs(clearance))
            if i in (0,len(FRAMES)-1):endpoints.append({'frame':g,'root_world':rw.tolist(),'camera_root_x_offset_m':offsets[-1]})
        checks['evaluated_root_has_no_shear_or_rotation']=root_rotation_error<1e-7
        checks['stage_static_across_shot']=stage_error<1e-7
        checks['four_boots_no_penetration_beyond_50um']=all(r['below_floor_samples']==0 for r in rows.values())
        checks['known_stance_support_within_0_3mm']=all(r['stance_samples']>0 and r['stance_maximum_abs_clearance_m']<=.0003 for r in rows.values())
        camera_range=max(offsets)-min(offsets)
        checks['camera_root_x_offset_constant_within_30um']=camera_range<=.00003
        return {'all_checks_pass':all(checks.values()),'checks':checks,'differences':differences,
            'source':str(ref),'source_sha256':expected_sha,'scene':scene.name,
            'samples':len(FRAMES),'production_frames':[G0,G1],
            'source_clock':'F=1+(G-937)*1.25;32frames/.78m/.73125mps;girl+2alreadybaked.',
            'expected_flat_stage_world_matrix':anchor.tolist(),'root_parent_inverse':inverse.tolist(),
            'floor_z_m':floor_z,'physical_floor':floor_support,'boot_clearances':rows,
            'camera_root_x_offset_range_m':camera_range,'camera_permitted_change_validation':camera_plan,'maximum_root_basis_error':root_rotation_error,
            'endpoint_samples':endpoints,'object_material_overrides_allowed':True,
            'source_data_material_slots_protected':True,'native_open_save_render_in_apply':False,
            'limits':'Raw geometry/UV/attributes/shapes/actions/materials and images compare to the exact frozen v060. Current boot mesh minima are measured; transparent paint silhouettes and artistic weight/contact/lighting are not approved by this report.'}
    finally:_frame(scene,before_frame)

def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--target',required=True)
    p.add_argument('--scene',default='WTSC_INK_WASH_DEPTH_v061');p.add_argument('--report',required=True)
    import sys
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    ref=Path(args.reference).resolve()
    bpy.ops.wm.open_mainfile(filepath=str(ref),load_ui=False,use_scripts=False)
    original=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];bpy.context.window.scene=original
    invariants=snapshot(original);invariants['reference_sha256']=_filehash(ref)
    ref.with_suffix('.invariants.json').write_text(json.dumps(invariants,indent=2))
    target=Path(args.target).resolve();target_sha=_filehash(target)
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes[args.scene];bpy.context.window.scene=scene
    report=apply(scene,ref);report['native']=str(target);report['native_sha256']=target_sha
    report['native_file_unchanged']=_filehash(target)==target_sha
    report['all_checks_pass']=report['all_checks_pass'] and report['native_file_unchanged']
    Path(args.report).write_text(json.dumps(report,indent=2))
    print('V061_FLAT_STAGE_VALIDATION',json.dumps({'pass':report['all_checks_pass'],
        'failed':[k for k,v in report['checks'].items() if not v]}),flush=True)
    assert report['all_checks_pass'],report['differences']

if __name__=='__main__':main()
