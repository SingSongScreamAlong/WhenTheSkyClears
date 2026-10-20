"""One native mass/value fix using preserved original paint, scar and debris."""
import bpy,json,math,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parents[1]
b=json.loads((P/'evidence/build_main_impact_v015b.json').read_text())
assert Path(bpy.data.filepath).resolve()==Path(b['native_context']).resolve()
source=Path(bpy.data.filepath);before_sha=hashlib.sha256(source.read_bytes()).hexdigest()
s=bpy.data.scenes[b['scene']];bpy.context.window.scene=s
c=bpy.data.collections[b['collection']];r=bpy.data.objects[b['root']]
c.name='FXv015c | PAINTED SOIL RUPTURE | evolving anchored mass'
r.name='FXv015c | fixed origin and evolving mass controls'
s.name='WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v015c'
info=json.loads((P/'assets/painted_contours_v015b.json').read_text())
H=info['size'][1]
def drive(owner,path,expr):
    f=owner.driver_add(path);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for name,key in [('t','age'),('I','intensity')]:
        if not re.search(r'\b'+name+r'\b',expr):continue
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["'+key+'"]'
    f.driver.expression=expr
def smooth(lo,hi):
    x=f'min(1,max(0,(t-({lo}))/({hi-lo})))'
    return f'({x}*{x}*(3-2*{x}))'
def rising(a,b,lo,hi):return f'({a}+({b-a})*{smooth(lo,hi)})'
specs={
 'Ignition':{'exposure':[0,5],'opacity':f'I*(1-{smooth(3,5)})','height':'.43','side':'0'},
 'RisingTear':{'exposure':[1,10],'opacity':f'I*{smooth(1,3)}*(1-{smooth(6,10)})','height':rising(.43,1.05,1,4),'side':'.035*sin(min(1,max(0,(t-1)/9))*pi)'},
 'MainFan':{'exposure':[5,22],'opacity':f'I*{smooth(5,8)}*(1-{smooth(14,22)})','height':f'{rising(.95,1.75,5,9)}-.4*{smooth(9,18)}','side':'.08*sin(min(1,max(0,(t-5)/17))*pi)'},
 'Collapse':{'exposure':[14,48],'opacity':f'I*{smooth(14,20)}*(1-{smooth(31,48)})','height':f'1.35-.27*{smooth(14,24)}-.38*{smooth(24,42)}','side':'.10*sin(min(1,max(0,(t-14)/34))*pi/2)'},
}
changed=[]
for stage,row in zip(info['stages'],b['drawings']):
    name=stage['name'];spec=specs[name];lo,hi=spec['exposure']
    first=bpy.data.objects[row['objects'][0]]
    oldmat=first.data.materials[0];mat=oldmat.copy();mat.name=f'FXv015c | {name} own paint/value/opacity envelope'
    nt=mat.node_tree
    hs=next(n for n in nt.nodes if n.type=='HUE_SAT');hs.inputs['Value'].default_value=.60;hs.inputs['Saturation'].default_value=.20
    alpha=next(n for n in nt.nodes if n.type=='MATH' and n.operation=='MULTIPLY')
    alpha.inputs[1].driver_remove('default_value');drive(alpha.inputs[1],'default_value',spec['opacity'])
    ay=stage['anchor'][1];scale=stage['metres_per_pixel'];height=stage['height_m']
    for obname in row['objects']:
        ob=bpy.data.objects[obname];ob.data.materials[0]=mat
        if ob.data.shape_keys:ob.shape_key_clear()
        ob.driver_remove('hide_render');ob.driver_remove('hide_viewport')
        expression=f'not ({lo}<=t<{hi})';drive(ob,'hide_render',expression);drive(ob,'hide_viewport',expression)
        # Recover exact original ground anchor from native original-pixel UVs.
        loop=ob.data.loops[0];v0=ob.data.vertices[loop.vertex_index]
        uv=ob.data.uv_layers.active.data[loop.index].uv;py=(1-uv.y)*H
        floor=float(v0.co.z-(ay-py)*scale)
        ob.shape_key_add(name='Original painted drawing; fixed world base')
        vertical=ob.shape_key_add(name='Anchored changing upper earth mass')
        side=ob.shape_key_add(name='Upper soil directional follow through')
        for d,e,v in zip(vertical.data,side.data,ob.data.vertices):
            u=max(0,min(1,(v.co.z-floor)/height));w=u*u*(3-2*u)
            d.co.z+=w
            e.co.x+=w
        vertical.slider_min=-2;vertical.slider_max=2;side.slider_min=-1;side.slider_max=1
        drive(vertical,'value',f'({spec["height"]})-{height}')
        drive(side,'value',spec['side'])
        ob['native_mass_revision']='v015c fixed-base nonuniform per-vertex upper mass compression/expansion and directional motion; own stage opacity envelope'
        changed.append(ob.name)
    row['age_exposure']=[lo,hi];row['opacity_expression']=spec['opacity'];row['upper_height_expression']=spec['height']

r['construction']='Four original painted stages with separate own-material opacity envelopes and overlapping decay; nonuniform anchored upper-mass native mesh motion carries painted clods. Same physical event light, world origin, native eight chip arcs and irregular painted ground disturbance.'
r['artistic_acceptance']=False
s.frame_set(1837);bpy.context.view_layer.update()
native=P/'native/WTSC_Painted_Main_Impact_Context_v015c.blend';asset=P/'native/WTSC_Painted_Main_Impact_Append_v015c.blend'
assert not native.exists() and not asset.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
report=dict(b);report.update({'native_context':str(native),'native_append':str(asset),'scene':s.name,'collection':c.name,'root':r.name,
 'parent_v015b':str(source),'parent_v015b_sha256':before_sha,'native_mass_changed_objects':changed,'drawings':b['drawings'],
 'native_motion_revision':'v015c overlapping own-stage opacity envelopes; nonuniform fixed-base upper mass; charcoal values0.60 instead0.78',
 'parent_v015b_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before_sha,
 'source_unchanged':hashlib.sha256(Path(b['source']).read_bytes()).hexdigest()==b['source_sha256'],
 'rendered':False,'artistic_acceptance':False,
 'limits':['Four source paintings remain; overlapping native deformation must be judged in actual consecutive frames.',
 'Painted depth, not simulated volumetric smoke or excavated physical ground.',
 'Native fragment support follows approximate prior painted terrain mask.',
 'No new light/camera/body changes and no full-trailer propagation.']})
(P/'evidence/build_main_impact_v015c.json').write_text(json.dumps(report,indent=2))
print('PAINTED_MAIN_IMPACT_V015C_BUILT',json.dumps({k:report[k]for k in('native_context','native_append','parent_v015b_unchanged','source_unchanged')}),flush=True)
