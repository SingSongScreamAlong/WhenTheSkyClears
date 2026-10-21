import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v039'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v039'];bpy.context.window.scene=w;fire=w.objects['v036 | Camp hearth | fixed emitter']
flames=[]
for ob in w.objects:
 if ob.parent!=fire or 'painted flame' not in ob.name:continue
 for mat in ob.data.materials:
  nt=mat.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],bw.inputs[0]);r=nt.nodes.new('ShaderNodeValToRGB');r.name='v039 restrained ochre / gold paint palette';r.color_ramp.elements[0].position=.015;r.color_ramp.elements[0].color=(.12,.065,.028,1);r.color_ramp.elements[1].position=.72;r.color_ramp.elements[1].color=(1.25,.94,.57,1)
  for p,col in [(.10,(.31,.16,.055,1)),(.28,(.66,.39,.12,1)),(.48,(.99,.72,.32,1))]:x=r.color_ramp.elements.new(p);x.color=col
  r.color_ramp.interpolation='EASE';nt.links.new(bw.outputs[0],r.inputs[0]);mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='MIX';mix.inputs[0].default_value=.14;nt.links.new(r.outputs[0],mix.inputs[6]);nt.links.new(tex.outputs['Color'],mix.inputs[7]);nt.links.new(mix.outputs[2],em.inputs[0]);flames.append(ob.name)
light=next(o for o in w.objects if o.parent==fire and o.type=='LIGHT');light.data.color=(1,.40,.12)
bank=w.objects['v020 | Foreground bank | continuous blended paint'];nt=bank.data.materials[0].node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and 'Foreground_Ground' in n.image.name)
bank_color=next(l.to_node for l in nt.links if l.from_node==tex and l.to_node.type=='MIX_RGB' and l.to_node.blend_type=='MULTIPLY')
blend=next(l.to_node for l in nt.links if l.from_node==bank_color and l.to_node.type=='MIX_RGB' and l.to_socket==l.to_node.inputs[2])
old=blend.inputs[0].links[0].from_socket;noise=next(n for n in nt.nodes if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-.42)<.001);mapn=nt.nodes.new('ShaderNodeMapRange');mapn.clamp=True;mapn.inputs['From Min'].default_value=.2;mapn.inputs['From Max'].default_value=.8;mapn.inputs['To Min'].default_value=.32;mapn.inputs['To Max'].default_value=.64;nt.links.new(noise.outputs['Fac'],mapn.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(mapn.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],blend.inputs[0])
glare=next(n for n in e.compositing_node_group.nodes if n.bl_idname=='CompositorNodeGlare');glare.inputs['Quality'].default_value='Medium'
w.frame_set(1609);e.frame_set(1609);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
report={'source':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'existing_flames_refined':flames,'palette':'Restrained charcoal-ochre/gold ramp retaining14%originalpaint grain/color; originalAlpha and native motion unchanged.','foreground':'World-stable patch variation reduces repeating bank photograph contribution to32–64%, revealing coherent underpainting; no alpha/geometry gaps.','glow':'Softer medium-quality fog kernel on hot cores, output remains4K; no full-frame scenery blur.','v001_assets_imported':False,'render_status':'Working benchmark; no substantive moving render yet.'}
(R/'notes/world_v016/camp_paint_language_v039.json').write_text(json.dumps(report,indent=2));print('PAINT_LANGUAGE_REFINED',json.dumps(report),flush=True)
