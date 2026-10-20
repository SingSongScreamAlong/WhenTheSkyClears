"""Create a separate corrected art recipe; preserve the failed v045 evidence."""
from pathlib import Path
R=Path(__file__).resolve().parents[1];original=(R/'scripts/build_art_study_v045.py').read_text();text=original.replace('v045','v045a')
old="for name,strength,fog in [('v016 | Battlefield | broken village line',.42,(.23,.265,.29,1)),('v026 | Countryside panorama | stationary at true depth',.20,(.34,.38,.41,1))]:"
new="for name,strength,fog in [('v016 | Battlefield | broken village line',.30,(.22,.25,.275,1)),('v026 | Countryside panorama | stationary at true depth',.12,(.34,.38,.41,1))]:"
assert old in text;text=text.replace(old,new)
old="graded=mix(nt,base,fog,strength,'v045a | Broad fixed atmospheric depth and shadow separation');nt.links.new(graded,target)"
new="""if 'Battlefield' in name:
  geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
  # Static ash-street atmosphere over a broad existing geographic corridor.
  # Darker side framing retained; no actor/camera/animated input or outline.
  left=remap(nt,xyz.outputs['X'],101.5,104.,0,1);right=remap(nt,xyz.outputs['X'],109.,112.,1,0)
  corridor=mathn(nt,'MULTIPLY',left,right);strength_input=mathn(nt,'ADD',.075,mathn(nt,'MULTIPLY',corridor,.225))
 else:strength_input=strength
 graded=mix(nt,base,fog,strength_input,'v045a | Restrained static ash-street depth with darker side masses');nt.links.new(graded,target)"""
assert old in text;text=text.replace(old,new)
old="quietuv=nt.nodes.new('ShaderNodeCombineXYZ');quietuv.name='v045a | Quieter soil passage from original paint';nt.links.new(uv.outputs['X'],quietuv.inputs[0]);nt.links.new(mathn(nt,'ADD',.54,mathn(nt,'MULTIPLY',uv.outputs['Y'],.10)),quietuv.inputs[1]);quiet=nt.nodes.new('ShaderNodeTexImage');quiet.name='v045a | Same packed road paint - quiet soil sample';quiet.image=tex.image;quiet.extension=tex.extension;quiet.interpolation='Cubic';nt.links.new(quietuv.outputs[0],quiet.inputs[0])"
new="""quietuv=nt.nodes.new('ShaderNodeCombineXYZ');quietuv.name='v045a | Uniform world-scale soil texels - no strip sampling'
#1536x1024 painting:1536*.42 ==1024*.63 ==645.12source pixels/metre.
for index,axis,scale,offset in [(0,'X',.42,.37),(1,'Z',.63,.21)]:
 nt.links.new(mathn(nt,'PINGPONG',mathn(nt,'ADD',mathn(nt,'MULTIPLY',sep.outputs[axis],scale),offset),1),quietuv.inputs[index])
groundtex=next(n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image and 'Ground_Painted' in n.image.name)
quiet=nt.nodes.new('ShaderNodeTexImage');quiet.name='v045a | Existing full painted soil at uniform density';quiet.image=groundtex.image;quiet.extension='REPEAT';quiet.interpolation='Cubic';nt.links.new(quietuv.outputs[0],quiet.inputs[0])
bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(quiet.outputs['Color'],bw.inputs[0]);palette=nt.nodes.new('ShaderNodeValToRGB');palette.name='v045a | Dust-road soil palette with preserved painted grain';palette.color_ramp.elements[0].position=.02;palette.color_ramp.elements[0].color=(.43,.40,.34,1);palette.color_ramp.elements[1].position=.25;palette.color_ramp.elements[1].color=(.78,.74,.65,1);palette.color_ramp.interpolation='EASE';nt.links.new(bw.outputs[0],palette.inputs[0])"""
assert old in text;text=text.replace(old,new)
text=text.replace("mix(nt,tex.outputs['Color'],quiet.outputs['Color'],quietweight", "mix(nt,tex.outputs['Color'],palette.outputs[0],quietweight")
text=text.replace("'method':'World-fixed sparse original plant sites; quieter soil sampled from same original packed road painting between sites. No alpha or geometry deletion.'", "'method':'World-fixed sparse original plant sites; original full soil underpainting sampled at uniform645.12sourcepixels/metre with palette adaptation. No UVstrip compression/clamping or alpha/geometry deletion.','source_pixel_density_per_metre':[645.12,645.12]")
anchor="for name,sha in preserved.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha,name"
insertion="""failed=R/'shots/world/WTSC_Open_Battlefield_Art_Study_v045.blend';assert hashlib.sha256(failed.read_bytes()).hexdigest()=='cbc66bea6d14d2baaea7ffe73488e5db233964593964a5014335c322ac93288b'
preserved[str(failed)]='cbc66bea6d14d2baaea7ffe73488e5db233964593964a5014335c322ac93288b'
for image in (R/'renders/world_v016/art_v045').glob('Art_v045_*_4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()
"""+anchor
assert text.count(anchor)==2;text=text.replace(anchor,insertion,1)
text=text.replace("'pending':'Actual six representative frames", "'rejected_predecessor':'v045actualsource/PNGs retained: UVstrip sampling failed visualreview; broadgrade over-fogged. This separatev045a uses uniform-density underpaint and restrained world-fixed corridor grade.','pending':'Actual six representative frames")
out=R/'scripts/build_art_study_v045a.py';assert not out.exists();compile(text,str(out),'exec');out.write_text(text);print('SEPARATE_V045A_RECIPE_CREATED',str(out))
