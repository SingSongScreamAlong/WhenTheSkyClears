"""Sealed v005 motion-only trial in own live battlefield copy; FX still held."""
import bpy,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');receipt=json.loads((R/'notes/world_v016/motion_snapshot_v042.json').read_text());snapshot=Path(receipt['snapshot']);expected=receipt['snapshot_sha256'];assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==expected
out=R/'shots/world/WTSC_Open_Battlefield_Motion_Trial_v042.blend';assert not out.exists()
# Reopen the sealed LOCAL snapshot before appending; no specialist source save.
bpy.ops.wm.open_mainfile(filepath=str(snapshot));assert len([a for a in bpy.data.actions if 'WEARY_STUMBLE_RECOVER' in a.name])==3;assert 'configure_battlefield.py' in bpy.data.texts;config_code=bpy.data.texts['configure_battlefield.py'].as_string();assert any(o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005' for o in bpy.data.objects)
base=R/'shots/world/WTSC_Open_Frame_Integration_Groundwork_v041.blend';base_sha=hashlib.sha256(base.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.data.scenes['WTSC_OPEN_INTEGRATION_GROUNDWORK_v041'];bpy.context.window.scene=s;s.frame_set(1825);held=next(o for o in s.objects if o.type=='GREASEPENCIL');start_x=held.matrix_world.translation.x;floor_z=.7713720202445984
with bpy.data.libraries.load(str(snapshot),link=False) as (available,loaded):
    assert 'WTSC_BATTLEFIELD_WEARY_PAIR_v005' in available.collections;loaded.collections=['WTSC_BATTLEFIELD_WEARY_PAIR_v005'];loaded.texts=['configure_battlefield.py']
collection=loaded.collections[0];s.collection.children.link(collection);root=next(o for o in collection.all_objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');root.location=(start_x,0,floor_z);root.scale=(1,1,1)
namespace={};exec(compile(config_code,'sealed_snapshot/configure_battlefield.py','exec'),namespace);config=namespace['configure_battlefield'](start=1801,time_scale=116/95,lead_in_frames=3,root_motion=True,root=root);travel=next(o for o in root.children if 'TRAVEL' in o.name)
hidden=[]
for ob in [held,*held.children_recursive]:ob.hide_render=True;hidden.append(ob.name)
camera=s.camera;camera.animation_data_clear();camera.location.y=-16;camera.location.z=3;curve=camera.driver_add('location',0);curve.driver.expression='x+1.6891200542449951';variable=curve.driver.variables.new();variable.name='x';variable.type='TRANSFORMS';variable.targets[0].id=travel;variable.targets[0].transform_type='LOC_X';variable.targets[0].transform_space='WORLD_SPACE'
def mathn(nt,op,a,b):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,x in enumerate([a,b]):
        if isinstance(x,(int,float)):n.inputs[i].default_value=x
        else:nt.links.new(x,n.inputs[i])
    return n.outputs[0]
def remap(nt,x,a,b,c,d):
    n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
    for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
    nt.links.new(x,n.inputs[0]);return n.outputs[0]
def mix(nt,a,b,f,mode):
    n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type=mode
    for socket,value in [(n.inputs[6],a),(n.inputs[7],b),(n.inputs[0],f)]:
        if isinstance(value,(tuple,int,float)):socket.default_value=value
        else:nt.links.new(value,socket)
    return n.outputs[2]
fire=s.objects['v036 | Battlefield burn | physical firelight'];owned={};material_rows=[]
for ob in root.children_recursive:
    if not hasattr(ob.data,'materials'):continue
    for index,original in enumerate(list(ob.data.materials)):
        if not original or not original.node_tree:continue
        if original.name not in owned:
            mat=original.copy();mat.name='v042 OWNED | restrained charcoal response | '+original.name;owned[original.name]=mat;nt=mat.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
            if em and em.inputs[0].is_linked:
                base_color=em.inputs[0].links[0].from_socket;luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base_color,luma.inputs[0]);eye=remap(nt,luma.outputs[0],.18,.65,1,0);cool=mix(nt,base_color,(.96,1.01,1.075,1),mathn(nt,'MULTIPLY',eye,.18),'MULTIPLY');geo=nt.nodes.new('ShaderNodeNewGeometry');position=nt.nodes.new('ShaderNodeCombineXYZ')
                for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
                    d=position.inputs[i].driver_add('default_value');d.driver.expression='p';v=d.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=fire;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
                distance=nt.nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE';nt.links.new(geo.outputs['Position'],distance.inputs[0]);nt.links.new(position.outputs[0],distance.inputs[1]);fall=remap(nt,distance.outputs['Value'],2,16,1,0);power=nt.nodes.new('ShaderNodeValue');d=power.outputs[0].driver_add('default_value');d.driver.expression='p/660';v=d.driver.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id_type='LIGHT';v.targets[0].id=fire.data;v.targets[0].data_path='energy';fac=mathn(nt,'MULTIPLY',fall,fall);fac=mathn(nt,'MULTIPLY',fac,power.outputs[0]);fac=mathn(nt,'MULTIPLY',fac,remap(nt,luma.outputs[0],.012,.16,.2,1));fac=mathn(nt,'MULTIPLY',fac,mathn(nt,'MULTIPLY',eye,.045));nt.links.new(mix(nt,cool,(.85,.31,.065,1),fac,'ADD'),em.inputs[0])
                material_rows.append({'source':original.name,'owned':mat.name,'response':'Subtle cool overcast fill and same actual existing battlefield light energy/position; eye/ink protected. Replacement FX remains0W/unbound.'})
        ob.data.materials[index]=owned[original.name]
spec=importlib.util.spec_from_file_location('owned_integration_bindings',R/'scripts/integration_live_bindings_v041.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers);contacts=helpers.bake_boot_contacts(s,root,1801,1920)
s.name='WTSC_OPEN_BATTLEFIELD_MOTION_TRIAL_v042';s.frame_start=1801;s.frame_end=1920;s.render.filepath='//../../renders/world_v016/integration_v042/WTSC_Motion_Trial_75_80_v042.mp4';s['integration_status']='MOTION-ONLY TRIAL. Sealed v005 snapshot; corrected FX pending. No v001/v002a. Not cinematic acceptance.'
samples=[]
for frame in [1801,1804,1825,1837,1849,1861,1881,1920]:
    s.frame_set(frame);bpy.context.view_layer.update();samples.append({'frame':frame,'root_world':list(root.matrix_world.translation),'travel_world':list(travel.matrix_world.translation),'camera_world':list(camera.matrix_world.translation)})
distance=samples[-1]['travel_world'][0]-samples[0]['travel_world'][0];assert abs(distance-.561666667)<1e-5,distance
report={'source':str(out),'world_base':str(base),'world_base_sha256':base_sha,'motion_snapshot':receipt,'native_snapshot_reopened_before_append':True,'import_collection':collection.name,'configure':config,'scene':s.name,'global_range':[75,80],'frames':[1801,1920],'character_start_floor_origin':[start_x,0,floor_z],'source_heights_preserved':[1.45,1.3699],'uniform_scale':1,'local_travel_m':distance,'old_held_pair_hidden_in_copy':hidden,'camera':'Follows TRAVEL worldX +original optical offset1.68912; original10.76m route removed from proof camera, no double travel. Original full040 not touched.','materials':material_rows,'contact_method':'4native soft planes baked from actual evaluated boot-sole geometry each globalframe, floor at source depth. Not parented to old held route.','samples':samples,'new_fx_imported':False,'fx_status':'Corrected replacement pending parent handoff. FailedFXv002a andv001 excluded. Existing040environment retained.','artistic_status':'Unreviewed actual-shot motion test. Must densely inspect seams, angular knee/boot silhouettes, rigid hands, weight/skating and held finalsettle.'}
note=bpy.data.texts.new('CURRENT v042 | Sealed motion-only shot trial and pendingFX');note.write(json.dumps(report,indent=2));(R/'notes/world_v016/boot_contact_geometry_v042.json').write_text(json.dumps(contacts,indent=2));s.frame_set(1825);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['source_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==expected and hashlib.sha256(Path(receipt['sealed_source']).read_bytes()).hexdigest()==expected and hashlib.sha256(base.read_bytes()).hexdigest()==base_sha;(R/'notes/world_v016/motion_trial_build_v042.json').write_text(json.dumps(report,indent=2));print('MOTION_ONLY_V042_SAVED',json.dumps({'source':str(out),'travel_m':distance,'contact_boots':len(contacts),'fx_imported':False}),flush=True)
