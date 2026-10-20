import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v025';s.name='WTSC_PAINTED_WORLD_4K_100S_v026'
target=R/'shots/world/WTSC_Painted_World_Trailer_v026.blend';assert not target.exists()
for o in list(s.objects):
    if o.name.startswith(('v023 | Distant countryside','v023 | Distant landscape continuation','v023 | Sky |')):bpy.data.objects.remove(o,do_unlink=True)
path=R/'sets/world_v026/Countryside_Continuous_Panorama.png';im=bpy.data.images.load(str(path),check_existing=True);im.pack()
m=bpy.data.materials.new('v026 | Continuous countryside paint | fixed land, cloud wind only');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear()
uv=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
skyweight=nt.nodes.new('ShaderNodeMapRange');skyweight.clamp=True;skyweight.interpolation_type='SMOOTHERSTEP';skyweight.inputs['From Min'].default_value=.67;skyweight.inputs['From Max'].default_value=.88;nt.links.new(sep.outputs['Y'],skyweight.inputs[0])
drift=nt.nodes.new('ShaderNodeValue');drift.name='Cloud drift only';f=drift.outputs[0].driver_add('default_value');f.driver.expression='frame*.000002'
mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(skyweight.outputs[0],mul.inputs[0]);nt.links.new(drift.outputs[0],mul.inputs[1]);vec=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(mul.outputs[0],vec.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';nt.links.new(uv.outputs['UV'],add.inputs[0]);nt.links.new(vec.outputs[0],add.inputs[1])
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';nt.links.new(add.outputs[0],tex.inputs[0]);hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(tex.outputs['Color'],hsv.inputs['Color'])
cool=nt.nodes.new('ShaderNodeMixRGB');cool.blend_type='MULTIPLY';cool.inputs[2].default_value=(.65,.81,1,1);nt.links.new(hsv.outputs[0],cool.inputs[1])
for t,sat,cold in [(0,1,0),(18,.90,.08),(42,.72,.38),(67,.52,.85),(80,.36,1),(100,.34,1)]:
    frame=min(2400,t*24+1);hsv.inputs['Saturation'].default_value=sat;hsv.inputs['Saturation'].keyframe_insert('default_value',frame=frame);cool.inputs[0].default_value=cold;cool.inputs[0].keyframe_insert('default_value',frame=frame)
em=nt.nodes.new('ShaderNodeEmission');nt.links.new(cool.outputs[0],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0])
width=280;height=width*im.size[1]/im.size[0]
d=bpy.data.meshes.new('v026 | One continuous panoramic painting');d.from_pydata([(-width/2,0,-height/2),(width/2,0,-height/2),(width/2,0,height/2),(-width/2,0,height/2)],[],[(0,1,2,3)]);d.materials.append(m);d.update();uvlayer=d.uv_layers.new(name='Panorama UV')
for loop,co in zip(uvlayer.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
o=bpy.data.objects.new('v026 | Countryside panorama | stationary at true depth',d);s.collection.objects.link(o);o.location=(50,180,3)
o['motion']='World-space stationary land. Only UV sky area above .67 has gentle cloud drift.'
o['source_pixels']=list(im.size);o['coverage']='One new GPT-painted panorama; no mirrored copies, stretched edge rows or camera-follow keys.'
for text in bpy.data.texts:
    if text.name.startswith('START HERE'):
        text.clear();text.write('Superseded checkpoint notes. Read CURRENT v026.\n')
note=bpy.data.texts.new('CURRENT v026 | Painted world trailer and motion corrections')
note.write('WHEN THE SKY CLEARS\n100-second animated painted world pass, UHD 3840x2160, 24 fps, frames 1–2400.\n\nCurrent user direction: preserve the painterly direction; near-age dark painted children with boy slightly taller; hold their pose during this world pass. Native GP boundary with a matching vector-clipped painted fill. Translation only, no gait/acting.\n\nMotion coherence corrections after review of v019: the opening oak, its roots, fence and painted path share one surface at Y=2. Registered repaint UVs stay on that same mesh. The landscape is stationary in world space at Y=180; a new continuous wide GPT painting covers the whole route without mirrored seams or stretched edges. Cloud drift is masked to sky only. Far woods now project smaller than nearby woods. Foreground transitions use whole isolated tree paintings. Chimney smoke origins sit at physical emitters; canopy/cloth motion is rooted/pinned. Architecture is kept rigid. Continuous painted ground replaces the opaque narrow strip edge.\n\nDepth remains real: near bank -4.99, foreground trees -4/-3, children around 0, path 2, woods 6/18, village/school/camp 10/12, distant ruins 28, countryside 180. Camera motion supplies the lateral parallax. The scenes are primarily 2.5D paintings, with an editable extruded 3D title.\n\nAll art created through GPT imagegen, with files and prompts retained in sets/ and notes/. Most base source paintings are about 1672x941. The new panorama size is recorded in the manifest. UHD output does not imply native UHD source painting.\n\nMusic is the supplied WAV, with final 10-second fade; picture fades over the last 2 seconds. Original sources remain preserved. The exact older approved ink-and-wash reference remains unavailable. Current direction is liked, but no final artistic/motion approval or Arcane-level finish is inferred.\n')
s['motion_coherence']='One opening oak/path surface; stationary continuous world panorama; smaller distant woods; emitter-anchored smoke; surface-locked repaints.'
s['scope']='100-second painted world animation development pass. Held pair per user; performance deferred.'
s['source_paint_limit']='Most base images 1672x941; panorama '+str(tuple(im.size))+'; smoke 1024x1536. Composite native 3840x2160.'
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v026.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/current_source_v026.json').write_text(json.dumps({'source':str(target),'scene':s.name,'panorama':str(path),'panorama_pixels':list(im.size),'resolution':[3840,2160],'fps':24,'frames':2400,'children':'Held near-age painted pair, native editable GP boundary; object translation only','motion_corrections':['Whole opening oak/roots/fence/path share one physical plane','Stationary real-depth continuous panorama, sky-only cloud drift','Far woods smaller than nearby woods; whole foreground tree art','Emitter-anchored smoke; architecture rigid','Continuous irregularly blended ground; no opaque lower strip'],'reference_status':'Exact old approved image missing; current direction liked; no final motion/art approval inferred'},indent=2))
out=R/'renders/world_v016/inspection_v026';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V026_REVIEW',name,f,flush=True)
