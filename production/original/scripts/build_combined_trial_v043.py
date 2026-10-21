"""Verified snapshots, live depth/light, local corrections; bounded5s copy only."""
import bpy,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');fx_receipt=json.loads((R/'notes/world_v016/fx_snapshot_v043.json').read_text());snapshot=Path(fx_receipt['snapshot']);assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==fx_receipt['snapshot_sha256'];out=R/'shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(snapshot));source_coll=bpy.data.collections[fx_receipt['collection']];assert len(source_coll.all_objects)==55 and not any(o.type=='LIGHT' for o in source_coll.all_objects)
base=R/'shots/world/WTSC_Open_Battlefield_Motion_Trial_v042.blend';base_sha=hashlib.sha256(base.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_MOTION_TRIAL_v042'];bpy.context.window.scene=s;s.frame_set(1825);root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');travel=next(o for o in root.children if 'TRAVEL' in o.name);held=next(o for o in s.objects if o.type=='GREASEPENCIL');points=[held.matrix_world@p.vector for p in held.data.layers[0].frames[0].drawing.attributes['position'].data];sole=min(points,key=lambda p:p.z);slope=(3-sole.z)/(sole.y+16);old_z=root.location.z;root.location.z=3-slope*16
view=s.camera.data.view_frame(scene=s);depth=travel.matrix_world.translation.y+16;center_x=(min(p.x for p in view)+max(p.x for p in view))*.5*depth/abs(view[0].z);curve=next(f for f in s.camera.animation_data.drivers if f.data_path=='location' and f.array_index==0);curve.driver.expression='x-('+repr(center_x)+')'
for ob in list(s.objects):
    if ob.name.startswith('v041 sole contact |'):bpy.data.objects.remove(ob,do_unlink=True)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
correction=module('local_correction',R/'scripts/local_pose_corrections_v043.py');pose_report=correction.correct_upper_body(root);own=bpy.data.collections.new('v043 OWNED | Local contours and physical light');s.collection.children.link(own);overlaps=correction.add_contour_overlaps(root,own)
with bpy.data.libraries.load(str(snapshot),link=False) as (available,loaded):loaded.collections=[fx_receipt['collection']]
fx_coll=loaded.collections[0];s.collection.children.link(fx_coll);fx_root=next(o for o in fx_coll.all_objects if o.name=='FXv003 | fixed ground origin and controls');assert len(fx_coll.all_objects)==55 and not any(o.type=='LIGHT' for o in fx_coll.all_objects);fx_root.location=(109.1,10,3-slope*26)
for key,value in {'start_frame':1824.,'speed':1.,'size':1.,'intensity':.94,'smoke_density':.88,'wind':.18,'hot_frames':14.}.items():fx_root[key]=value
fx_root['smoke_color']=[.72,.77,.83]
hidden=[]
for ob in s.objects:
    if (ob.name.startswith('v036 | Battlefield burn |') and 'charred hearth stone' not in ob.name) or ob.name.startswith(('v016 | Battlefield smoke |','v016 | Far battlefield smoke |','v016 | Distant light bloom ')):ob.hide_render=True;hidden.append(ob.name)
old_fire=s.objects['v036 | Battlefield burn | fixed emitter'];old_fire['light_power']=0.;old_fire['flame_power']=0.
data=bpy.data.lights.new('v043 OWNED | Brief eruption light','POINT');data.color=(1,.37,.11);data.shadow_soft_size=.65;light=bpy.data.objects.new(data.name,data);own.objects.link(light);light.parent=fx_root;light.location=(0,-.55,.85);d=data.driver_add('energy');d.driver.expression='1800*H*I'
for name,prop in [('H','hot_envelope'),('I','intensity')]:v=d.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=fx_root;v.targets[0].data_path='["'+prop+'"]'
bindings=module('live_binding',R/'scripts/integration_live_bindings_v041.py');event=bindings.bind_event_to_native_fx(s,fx_root,light);event['reference_watts']=1800.;event['receiver_gain']=.10
# New character-material response uses the same actual pulse, not a second clock.
materials={m for ob in root.children_recursive if hasattr(ob.data,'materials') for m in ob.data.materials if m and m.node_tree};material_rows=[]
for mat in materials:
    nt=mat.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
    if not em or not em.inputs[0].is_linked:continue
    base_color=em.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry');pos=nt.nodes.new('ShaderNodeCombineXYZ')
    for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
        f=pos.inputs[i].driver_add('default_value');f.driver.expression='p';v=f.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=light;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
    def mathn(op,a,b):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op
        for i,x in enumerate([a,b]):
            if isinstance(x,(int,float)):n.inputs[i].default_value=x
            else:nt.links.new(x,n.inputs[i])
        return n.outputs[0]
    def remap(x,a,b,c,d):
        n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
        for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
        nt.links.new(x,n.inputs[0]);return n.outputs[0]
    distance=nt.nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE';nt.links.new(geo.outputs['Position'],distance.inputs[0]);nt.links.new(pos.outputs[0],distance.inputs[1]);fall=remap(distance.outputs['Value'],2,16,1,0);power=nt.nodes.new('ShaderNodeValue');f=power.outputs[0].driver_add('default_value');f.driver.expression='p/1800';v=f.driver.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id_type='LIGHT';v.targets[0].id=light.data;v.targets[0].data_path='energy';luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base_color,luma.inputs[0]);eye=remap(luma.outputs[0],.18,.65,1,0);protect=remap(luma.outputs[0],.01,.16,.2,1);fac=mathn('MULTIPLY',fall,fall);fac=mathn('MULTIPLY',fac,power.outputs[0]);fac=mathn('MULTIPLY',fac,mathn('MULTIPLY',eye,protect));fac=mathn('MULTIPLY',fac,.025);mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='ADD';mix.name='v043 | Brief physically sourced reflected light';mix.inputs[7].default_value=(.85,.31,.065,1);nt.links.new(base_color,mix.inputs[6]);nt.links.new(fac,mix.inputs[0]);nt.links.new(mix.outputs[2],em.inputs[0]);material_rows.append(mat.name)
contacts=bindings.bake_boot_contacts(s,root,1801,1920,floor_slope=slope);s.name='WTSC_OPEN_BATTLEFIELD_COMBINED_TRIAL_v043';s.frame_start=1801;s.frame_end=1920;s.render.filepath='//../../renders/world_v016/integration_v043/WTSC_Combined_Open_75_80_v043.mp4';s['integration_status']='Bounded combined artistic trial. Sealed motionv005+FXv003; local native contours/timing/settle. No v001/v002a, no held plates. Full040 preserved.'
samples=[]
for frame in [1801,1823,1824,1825,1830,1838,1843,1852,1881,1920]:
    s.frame_set(frame);bpy.context.view_layer.update();samples.append({'frame':frame,'camera':list(s.camera.matrix_world.translation),'travel':list(travel.matrix_world.translation),'fx_age':fx_root['age'],'hot_envelope':fx_root['hot_envelope'],'physical_watts':data.energy,'receiver_watts':event['power_watts'],'fx_origin':list(fx_root.matrix_world.translation)})
    assert abs(event['power_watts']-data.energy)<.01
    if frame>=1838:assert abs(data.energy)<1e-6
report={'source':str(out),'base_motion_trial':str(base),'base_sha256':base_sha,'scene':s.name,'motion_snapshot':json.loads((R/'notes/world_v016/motion_snapshot_v042.json').read_text()),'fx_snapshot':fx_receipt,'native_fx_snapshot_reopened_before_append':True,'fx_import_objects':len(fx_coll.all_objects),'fx_import_lights':0,'owned_physical_lights':1,'frame_range':[1801,1920],'global_seconds':[75,80],'resolution':[3840,2160],'fps':24,'floor_correction':{'original_held_floor_point':list(sole),'slope':slope,'previous_motion_origin_z':old_z,'correct_motion_origin_z':root.location.z,'cameraX_optical_offset':-center_x,'cameraY':-16,'cameraZ':3},'local_pose_corrections':pose_report,'local_contour_overlaps':overlaps,'source_connected_actor_materials':material_rows,'replaced_old_fx_hidden':hidden,'live_samples':samples,'occlusion':'All real geometry, characters, FX and owned light evaluated in one live scene; no cached image/receiver/holdout compositor nodes.','comparison_limit':'Original040camera covers10.76m in75–80. This localproof follows0.561667m performance, starting near oldglobal76spatialposition. Before/afterwilllabeldifferent localcamera/route, not perfectly matchedA/B.','artist_review':'Must review actual frames then dense moving sequence. Localcaps/asymmetry/settle are trials, not acceptedcorrectiveart. Cutoutstiffness mayremainweakestissue.'}
note=bpy.data.texts.new('CURRENT v043 | Combined local trial provenance and limits');note.write(json.dumps(report,indent=2));(R/'notes/world_v016/boot_contact_geometry_v043.json').write_text(json.dumps(contacts,indent=2));s.frame_set(1830);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['source_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==fx_receipt['snapshot_sha256'] and hashlib.sha256(Path(fx_receipt['sealed_source']).read_bytes()).hexdigest()==fx_receipt['source_sha256'];assert hashlib.sha256(base.read_bytes()).hexdigest()==base_sha;(R/'notes/world_v016/combined_trial_build_v043.json').write_text(json.dumps(report,indent=2));print('COMBINED_TRIAL_V043_SAVED',json.dumps({'source':str(out),'sha256':report['source_sha256'],'floor':root.location.z,'hot_phase_zero_after1838':True}),flush=True)
