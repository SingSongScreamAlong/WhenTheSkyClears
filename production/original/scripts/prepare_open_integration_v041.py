"""Bounded open-frame groundwork only; no unapproved specialist imports."""
import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');source=Path(bpy.data.filepath);source_sha=hashlib.sha256(source.read_bytes()).hexdigest();assert source_sha=='c3ed3c15055ae5cd242a68964d6980bb8bda3ff6f7f4882d69fa4198e937819f'
out=R/'shots/world/WTSC_Open_Frame_Integration_Groundwork_v041.blend';assert not out.exists()
s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'];bpy.context.window.scene=s
glow_source=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare');settings={i.name:i.default_value for i in glow_source.inputs if i.name!='Image' and hasattr(i,'default_value')}
for scene in list(bpy.data.scenes):
    if scene!=s:bpy.data.scenes.remove(scene)
s.name='WTSC_OPEN_INTEGRATION_GROUNDWORK_v041';s.frame_start=1801;s.frame_end=1920;s.use_preview_range=True;s.frame_preview_start=1801;s.frame_preview_end=1920;s.render.fps=24;s.render.use_sequencer=False;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.dither_intensity=0
nt=bpy.data.node_groups.new('v041 | Live world only | no cached plates or masks','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=s;g=nt.nodes.new('CompositorNodeGlare')
for name,value in settings.items():
    try:g.inputs[name].default_value=value
    except (TypeError,ValueError):pass
o=nt.nodes.new('NodeGroupOutput');nt.links.new(rl.outputs['Image'],g.inputs['Image']);nt.links.new(g.outputs['Image'],o.inputs[0]);s.compositing_node_group=nt;s.render.use_compositing=True
col=bpy.data.collections.new('v041 | Integration controls | no imported candidates');s.collection.children.link(col);event=bpy.data.objects.new('v041 | Live event binding | awaiting verified FX',None);col.objects.link(event);event.location=(109.1,10,-.7048803);event.empty_display_type='CIRCLE';event.empty_display_size=.25
for k,v in {'power_watts':0.,'reference_watts':2800.,'receiver_gain':.10,'ground_radius':2.2,'wall_radius':6.,'bound_to_verified_fx':0.}.items():event[k]=v
event['status']='DORMANT. No FX or motion candidate imported. Bind to verified replacement native light only after parent handoff.'
def scalar(nt,op,a,b=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,x in enumerate([a,b]):
        if x is None:continue
        if isinstance(x,(int,float)):n.inputs[i].default_value=x
        else:nt.links.new(x,n.inputs[i])
    return n.outputs[0]
def control(nt,prop):
    n=nt.nodes.new('ShaderNodeValue');n.name='v041 EVENT | '+prop;f=n.outputs[0].driver_add('default_value');f.driver.expression='v';var=f.driver.variables.new();var.name='v';var.type='SINGLE_PROP';var.targets[0].id=event;var.targets[0].data_path='["'+prop+'"]';return n.outputs[0]
def transform(nt,ob):
    n=nt.nodes.new('ShaderNodeCombineXYZ');n.name='v041 live transform | '+ob.name
    for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
        f=n.inputs[i].driver_add('default_value');f.driver.expression='v';var=f.driver.variables.new();var.name='v';var.type='TRANSFORMS';var.targets[0].id=ob;var.targets[0].transform_type=axis;var.targets[0].transform_space='WORLD_SPACE'
    sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(n.outputs[0],sep.inputs[0]);return n.outputs[0],sep
def remap(nt,x,a,b,c,d):
    n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
    for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
    nt.links.new(x,n.inputs[0]);return n.outputs[0]
receivers=[]
for name,ground,gain in [('v016 | Battlefield | broken village line',False,1.),('v016 | Ruins | distant ash street',False,.6),('v020 | Walking path | continuous blended paint',True,.8),('v020 | Foreground bank | continuous blended paint',True,.35)]:
    ob=s.objects[name];mat=ob.data.materials[0].copy();mat.name='v041 OWNED | live event receiver | '+name;ob.data.materials[0]=mat;nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry');ev,es=transform(nt,event);radius=control(nt,'ground_radius' if ground else 'wall_radius');target=ev
    if ground:
        cv,cs=transform(nt,s.camera);ov,os=transform(nt,ob);ratio=scalar(nt,'DIVIDE',scalar(nt,'SUBTRACT',os.outputs['Y'],cs.outputs['Y']),scalar(nt,'SUBTRACT',es.outputs['Y'],cs.outputs['Y']));hit=nt.nodes.new('ShaderNodeCombineXYZ')
        for i,axis in enumerate(['X','Y','Z']):nt.links.new(scalar(nt,'ADD',cs.outputs[axis],scalar(nt,'MULTIPLY',scalar(nt,'SUBTRACT',es.outputs[axis],cs.outputs[axis]),ratio)),hit.inputs[i])
        target=hit.outputs[0];radius=scalar(nt,'MULTIPLY',radius,scalar(nt,'ABSOLUTE',ratio))
    dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';nt.links.new(geo.outputs['Position'],dist.inputs[0]);nt.links.new(target,dist.inputs[1]);fall=nt.nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.interpolation_type='SMOOTHERSTEP';fall.inputs['From Min'].default_value=.04;fall.inputs['To Min'].default_value=1;fall.inputs['To Max'].default_value=0;nt.links.new(radius,fall.inputs['From Max']);nt.links.new(dist.outputs['Value'],fall.inputs[0]);fac=scalar(nt,'MULTIPLY',fall.outputs[0],fall.outputs[0]);luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,luma.inputs[0]);fac=scalar(nt,'MULTIPLY',fac,remap(nt,luma.outputs[0],.012,.22,.14,1));strength=scalar(nt,'DIVIDE',control(nt,'power_watts'),control(nt,'reference_watts'));strength=scalar(nt,'MULTIPLY',strength,control(nt,'receiver_gain'));fac=scalar(nt,'MULTIPLY',fac,scalar(nt,'MULTIPLY',strength,gain));mix=nt.nodes.new('ShaderNodeMix');mix.name='v041 DORMANT | source-bound local warmth';mix.data_type='RGBA';mix.blend_type='ADD';mix.inputs[7].default_value=(.85,.31,.065,1);nt.links.new(base,mix.inputs[6]);nt.links.new(fac,mix.inputs[0]);nt.links.new(mix.outputs[2],em.inputs[0]);receivers.append({'object':name,'material':mat.name,'ground_projection_updates_with_live_camera':ground})
# Replace the repeating bright path-plant fence with a higher, irregular live
# near-bank edge. Keep a clear margin below the measured shoe sole atscreen.271.
bank=s.objects['v020 | Foreground bank | continuous blended paint'];nt=bank.data.materials[0].node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.6;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs[0]);edge=scalar(nt,'ADD',1.34,scalar(nt,'MULTIPLY',scalar(nt,'SUBTRACT',noise.outputs['Fac'],.5),.09));delta=scalar(nt,'SUBTRACT',sep.outputs['Z'],edge);alpha=remap(nt,delta,-.10,.02,1,0);mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');nt.links.new(alpha,mix.inputs[0])
for v in bank.data.vertices:
    if v.co.z>1.2:v.co.z=1.47
bank['v041_change']='Static world-space irregular bank edge covers repeated lower path plants; no time input, camera-locked plate, raster repaint or building fade.'
s['integration_status']='GROUNDWORK ONLY. FXv002a failed artistic review; v001 excluded. Motion currently unsealed. No specialist collection appended.';s['chosen_shot']='Battlefield global75–80,1801–1920 inclusive. Event hero1825 motivates stumble; local camera/root phase must be matched to sealed distance curve.';s.render.filepath='//../../renders/world_v016/integration_v041/WTSC_Groundwork_Only_75_80_v041.mp4';s.frame_set(1825)
report={'native_source':str(out),'base_source':str(source),'base_sha256':source_sha,'scene':s.name,'global_seconds':[75,80],'frames':[1801,1920],'total_frames':120,'resolution':[3840,2160],'fps':24,'status':'GROUNDWORK ONLY. Waiting for verified replacement FX and verified current motion snapshot. No integrated proof rendered.','shot_rationale':'Eruption hero76seconds can motivate toe-catch/lurch, rescue step and weary settle in one open shot. Camp lacks that causal beat.','receivers':receivers,'occlusion':'Actual original live world geometry in same scene with later appended FX. No held plates, holdout maps or receiver images.','event_binding':'Dormant native transform/power control, default0W. Bind to sealed FX root and actual native point-light energy before use.','foreground':'Local near-bank edge height/feather modified; original paint unchanged, staticworldspace/noTime alpha. Requires actualframe review.','character_state':'Original held pair preserved until verified motion snapshot. No motion imports.','camera_plan':'Original route retained in groundwork. Original75–80covers10.76m; stumble0.562m requires local route/camera adjustment after sealed handoff. Full v040 title/timeline untouched.','excluded':['effects/ink_wash_v001','FXv002a rejected smoke/core motion','unsealed motion collections'],'artistic_acceptance':False}
note=bpy.data.texts.new('CURRENT v041 | Groundwork, integration hold and binding');note.write(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();assert hashlib.sha256(source.read_bytes()).hexdigest()==source_sha;(R/'notes/world_v016/integration_groundwork_v041.json').write_text(json.dumps(report,indent=2));print('OPEN_GROUNDWORK_SAVED_NO_CANDIDATES_IMPORTED',json.dumps({'source':str(out),'sha256':report['sha256']}),flush=True)
