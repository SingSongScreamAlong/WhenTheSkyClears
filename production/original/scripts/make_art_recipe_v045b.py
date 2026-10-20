"""Separate bounded palette correction; preserve both earlier failed frame sets."""
from pathlib import Path
R=Path(__file__).resolve().parents[1];text=(R/'scripts/build_art_study_v045a.py').read_text().replace('v045a','v045b')
old="bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(quiet.outputs['Color'],bw.inputs[0]);palette=nt.nodes.new('ShaderNodeValToRGB');palette.name='v045b | Dust-road soil palette with preserved painted grain';palette.color_ramp.elements[0].position=.02;palette.color_ramp.elements[0].color=(.43,.40,.34,1);palette.color_ramp.elements[1].position=.25;palette.color_ramp.elements[1].color=(.78,.74,.65,1);palette.color_ramp.interpolation='EASE';nt.links.new(bw.outputs[0],palette.inputs[0])"
new="mult=nt.nodes.new('ShaderNodeMixRGB');mult.name='v045b | Same dark earth palette as continuous near bank';mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1.;mult.inputs[2].default_value=(.13,.17,.16,1);nt.links.new(quiet.outputs['Color'],mult.inputs[1]);quietcolor=mult.outputs[0]"
assert old in text;text=text.replace(old,new);text=text.replace("palette.outputs[0],quietweight", "quietcolor,quietweight")
anchor="for image in (R/'renders/world_v016/art_v045').glob('Art_v045_*_4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()"
extra=anchor+"\nfailed_a=R/'shots/world/WTSC_Open_Battlefield_Art_Study_v045a.blend';assert hashlib.sha256(failed_a.read_bytes()).hexdigest()=='7dc52ab80047ab3b7d7ae3f8ca61414b4763a04ecf6784b23afb34219b2630fa';preserved[str(failed_a)]='7dc52ab80047ab3b7d7ae3f8ca61414b4763a04ecf6784b23afb34219b2630fa'\nfor image in (R/'renders/world_v016/art_v045a').glob('Art_v045a_*_4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()"
assert anchor in text;text=text.replace(anchor,extra)
text=text.replace('uniform645.12sourcepixels/metre with palette adaptation','uniform645.12sourcepixels/metre using the same native dark-earth palette as the near bank')
text=text.replace('This separatev045b uses uniform-density underpaint and restrained world-fixed corridor grade.','v045a uniformdensity passed but brightpalette failed. This separatev045b uses the matching darkbank palette, uniform-density underpaint and restrained world-fixed corridor grade.')
out=R/'scripts/build_art_study_v045b.py';assert not out.exists();compile(text,str(out),'exec');out.write_text(text)
renderer=R/'scripts/render_art_frames_v045b.py';assert not renderer.exists();renderer.write_text((R/'scripts/render_art_frames_v045a.py').read_text().replace('v045a','v045b'));print('V045B_SEPARATE_RECIPES_WRITTEN')
