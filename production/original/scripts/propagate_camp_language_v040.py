"""Propagate the reviewed camp treatment; run after moving comparison QA."""
import bpy, math, json, hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
assert json.loads((R/'notes/world_v016/camp_comparison_visual_review_v039.json').read_text())['technical_comparison_reviewed']
out=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend';assert not out.exists()
w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v039'];bpy.context.window.scene=w
def driver(owner,path,root,expression,props):
    f=owner.driver_add(path);f.driver.type='SCRIPTED';f.driver.expression=expression
    for name,prop in props:
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+prop+'"]'
    return f
def mathn(nt,op,a,b=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,x in enumerate([a,b]):
        if x is None:continue
        if isinstance(x,(int,float)):n.inputs[i].default_value=x
        else:nt.links.new(x,n.inputs[i])
    return n.outputs[0]
def vec(nt,op,a,b=None):
    n=nt.nodes.new('ShaderNodeVectorMath');n.operation=op
    for i,x in enumerate([a,b]):
        if x is None:continue
        if isinstance(x,tuple):n.inputs[i].default_value=x
        else:nt.links.new(x,n.inputs[i])
    return n.outputs['Value'] if op in ['LENGTH','DOT_PRODUCT','DISTANCE'] else n.outputs['Vector']
def mapr(nt,src,a,b,c,d):
    n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
    for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
    nt.links.new(src,n.inputs[0]);return n.outputs[0]
def mix(nt,a,b,f,mode='MIX',name='v040 paint response'):
    n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type=mode;n.name=name
    for socket,x in [(n.inputs[6],a),(n.inputs[7],b),(n.inputs[0],f)]:
        if isinstance(x,(int,float,tuple)):socket.default_value=x
        else:nt.links.new(x,socket)
    return n.outputs[2]
def value(nt,root,prop,power=False):
    n=nt.nodes.new('ShaderNodeValue');n.name='v040 '+root.name+' '+prop
    driver(n.outputs[0],'default_value',root,'v*P/N' if power else 'v',[('v',prop),('P','light_power'),('N','reference_power')] if power else [('v',prop)])
    return n.outputs[0]
def lightvector(nt,root,position):
    light=next(o for o in w.objects if o.parent==root and o.type=='LIGHT');n=nt.nodes.new('ShaderNodeCombineXYZ');n.name='v040 actual physical source position'
    for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
        f=n.inputs[i].driver_add('default_value');f.driver.expression='p';v=f.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=light;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
    delta=vec(nt,'SUBTRACT',n.outputs[0],position);return vec(nt,'NORMALIZE',delta),vec(nt,'LENGTH',delta),delta
def strip_old_wash(nt,em):
    src=em.inputs[0].links[0].from_socket;removed=[]
    while src.node.bl_idname=='ShaderNodeMix' and src.node.blend_type=='ADD' and tuple(round(v,3) for v in src.node.inputs[7].default_value[:3])==(.8,.2,.025):
        n=src.node;removed.append(n.name);src=n.inputs[6].links[0].from_socket
    return src,removed
def receive(nt,base,root,normal=None):
    geo=nt.nodes.new('ShaderNodeNewGeometry');direction,distance,delta=lightvector(nt,root,geo.outputs['Position']);fall=nt.nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.interpolation_type='SMOOTHERSTEP';fall.inputs['From Min'].default_value=.15;fall.inputs['To Min'].default_value=1;fall.inputs['To Max'].default_value=0;nt.links.new(value(nt,root,'receiver_radius'),fall.inputs['From Max']);nt.links.new(distance,fall.inputs[0]);weight=mathn(nt,'MULTIPLY',fall.outputs[0],fall.outputs[0])
    if normal is not None:weight=mathn(nt,'MULTIPLY',weight,mathn(nt,'MAXIMUM',vec(nt,'DOT_PRODUCT',normal,direction),.08))
    luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,luma.inputs[0]);weight=mathn(nt,'MULTIPLY',weight,mapr(nt,luma.outputs[0],.012,.20,.18,1));strength=mathn(nt,'MULTIPLY',value(nt,root,'receiver_strength'),value(nt,root,'fire_beat',True));strength=mathn(nt,'MULTIPLY',strength,weight)
    return mix(nt,base,(1,.34,.075,1),strength,'ADD','v040 localized source-connected warmth')
roots=[o for o in w.objects if o.type=='EMPTY' and o.name.startswith('v036') and 'fixed emitter' in o.name];camp=next(o for o in roots if 'Camp hearth' in o.name);other=[o for o in roots if o!=camp];fire_changes=[]
for root in roots:
    if root==camp:root['reference_power']=420.;continue
    idx=0 if 'School' in root.name else 2 if 'Battlefield' in root.name else 3
    root['light_power']=[248,420,660,720][idx];root['reference_power']=root['light_power'];root['receiver_radius']=[2.8,2.8,3.6,5][idx];root['receiver_strength']=[.065,.075,.075,.08][idx];root['character_response']=.10;root['flame_power']=1.8;root['fire_beat']=.82
    root.driver_add('["fire_beat"]').driver.expression=f'(.82+.12*sin(frame*.77+{idx*2.13})+.065*sin(frame*1.93+{idx*2.13+1})+.045*sin(frame*.313+{idx*2.13+2}))'
    light=next(o for o in w.objects if o.parent==root and o.type=='LIGHT');light.data.driver_remove('energy');light.data.color=(1,.40,.12);driver(light.data,'energy',root,'P*F',[('P','light_power'),('F','fire_beat')])
    for ob in [o for o in w.objects if o.parent==root and 'painted flame' in o.name]:
        j=int(ob.name.rsplit(' ',1)[-1]);template=w.objects['v036 | Camp hearth | painted flame '+str(j)].data.materials[0];mat=template.copy();mat.name='v040 | '+root.name+' | restrained flame '+str(j);ob.data.materials[0]=mat
        for f in mat.node_tree.animation_data.drivers if mat.node_tree.animation_data else []:
            for variable in f.driver.variables:
                for target in variable.targets:
                    if target.id==camp:target.id=root
    for ob in [o for o in w.objects if o.parent==root and 'rooted smoke' in o.name]:
        nt=ob.data.materials[0].node_tree
        for f in nt.animation_data.drivers if nt.animation_data else []:
            if 'sin(pi*' in f.driver.expression:
                expr=f.driver.expression;expr=expr[expr.index('sin(pi*'):];expr=expr[:-1] if expr.endswith('**2)') else expr;f.driver.expression='.16*'+expr
    fire_changes.append({'root':root.name,'power_watts':root['light_power'],'radius':root['receiver_radius'],'smoke_reset_opacity':0})
paint_changes=[]
for name in ['v016 | School | broken windows and plaster','v016 | Battlefield | broken village line','v016 | Ruins | distant ash street']:
    ob=w.objects[name];mat=ob.data.materials[0].copy();mat.name='v040 | '+name+' | shaped paint and bounded source';ob.data.materials[0]=mat;nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base,removed=strip_old_wash(nt,em);tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');geo=nt.nodes.new('ShaderNodeNewGeometry');bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.035;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(geo.outputs['Normal'],bump.inputs['Normal']);lambert=mathn(nt,'MAXIMUM',vec(nt,'DOT_PRODUCT',bump.outputs['Normal'],vec(nt,'NORMALIZE',(-.35,-.70,.72))),0);tone=mix(nt,(.82,.87,.95,1),(1.05,1.055,1.065,1),lambert);base=mix(nt,base,tone,1,'MULTIPLY','v040 preserved painted form with coherent cool key')
    for root in roots:
        if abs(ob.location.x-root.location.x)<40:base=receive(nt,base,root,bump.outputs['Normal'])
    nt.links.new(base,em.inputs[0]);paint_changes.append({'object':name,'old_broad_washes_bypassed':removed})
for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
    nt=w.objects[name].data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket
    for root in other:base=receive(nt,base,root)
    nt.links.new(base,em.inputs[0])
# Add the same material-only contour response at the other fixed sources.
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');fill=next(o for o in w.objects if o.parent==pair and 'Near-black painted fill' in o.name);nt=fill.data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');uv=nt.nodes.new('ShaderNodeTexCoord')
def edge(dx,dy):
    add=vec(nt,'ADD',uv.outputs['UV'],(dx,dy,0));t=nt.nodes.new('ShaderNodeTexImage');t.image=tex.image;t.extension='CLIP';t.interpolation='Cubic';nt.links.new(add,t.inputs[0]);return mathn(nt,'MAXIMUM',mathn(nt,'SUBTRACT',tex.outputs['Alpha'],t.outputs['Alpha']),0)
left=edge(-2/1672,0);right=edge(2/1672,0);top=edge(0,2/941);geo=nt.nodes.new('ShaderNodeNewGeometry');luma=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,luma.inputs[0]);eye=mapr(nt,luma.outputs[0],.16,.65,1,0)
for root in other:
    direction,distance,delta=lightvector(nt,root,geo.outputs['Position']);sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(delta,sep.inputs[0]);fromleft=mathn(nt,'LESS_THAN',sep.outputs['X'],0);side=mathn(nt,'ADD',mathn(nt,'MULTIPLY',left,fromleft),mathn(nt,'MULTIPLY',right,mathn(nt,'SUBTRACT',1,fromleft)));inv=mathn(nt,'DIVIDE',1,mathn(nt,'ADD',1,mathn(nt,'POWER',mathn(nt,'DIVIDE',distance,4),2)));warm=mathn(nt,'MULTIPLY',mathn(nt,'MULTIPLY',inv,mapr(nt,distance,7,14,1,0)),value(nt,root,'character_response'));warm=mathn(nt,'MULTIPLY',warm,value(nt,root,'fire_beat',True));warm=mathn(nt,'MULTIPLY',warm,mathn(nt,'ADD',mathn(nt,'MULTIPLY',side,.7),mathn(nt,'MULTIPLY',top,.12)));warm=mathn(nt,'MULTIPLY',warm,eye);base=mix(nt,base,(.9,.31,.065,1),warm,'ADD','v040 source-connected charcoal contour')
nt.links.new(base,em.inputs[0]);grass=[]
for ob in w.objects:
    if not ob.name.startswith('v016 | Rooted grass ') or not 78<=ob.location.x<=100:continue
    depth=ob.location.y+16;width=.36*depth;height=width*2160/3840;ob.location.z=3+(.17-.5)*height+w.camera.data.shift_y*width;grass.append(ob.name)
w.name='WTSC_WORLD_CORRECTED_v040';e.name='WTSC_FULL_FILM_KNOCKOUT_v040';m.name='WTSC_MASTER_4K_106S_v040'
for scene,path in [(w,'WTSC_Corrected_World_Native_v040.mp4'),(e,'WTSC_Full_Knockout_Picture_Native_v040.mp4'),(m,'WTSC_Full_Knockout_Native_Edit_v040.mp4')]:scene.use_preview_range=False;scene.render.filepath='//../../renders/world_v016/'+path
report={'source':str(out),'benchmark':'v039 actual64–69s moving comparison reviewed before propagation','changes':{'regional_paint':paint_changes,'fire_assemblies':fire_changes,'measured_contacts':'Same8soft core/penumbra contacts introduced in039, now travel throughout100s','grass_roots_placed_at_bank_edge':len(grass),'character_material':'Same charcoal design/topology/UV/root/pose. Added bounded physically sourced contours for other3fires only.','foreground':'Same039stable paint/UV treatment throughout route; no repeated bank photograph contribution.','glow':'Same039 restrained medium FogGlow throughout.','mask_credits_audio_timing':'Unchanged106s/24fps/4K, originalsingleWAV0–100,fading90–100,silent6scredits.'},'excluded':'All rejected effects/ink_wash_v001 assets and all untested new character motion.','scope':'Native2.5Dpaint refinement, not artistic acceptance or Arcane-level finish.'}
note=bpy.data.texts.new('CURRENT v040 | Propagated paint light and grounded world');note.write(json.dumps(report,indent=2));bpy.context.window.scene=m;m.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report['source_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(R/'notes/world_v016/full_build_v040.json').write_text(json.dumps(report,indent=2));print('FULL_V040_SOURCE_SAVED',json.dumps({'source':str(out),'sha256':report['source_sha256']}),flush=True)
