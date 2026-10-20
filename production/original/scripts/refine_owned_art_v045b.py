"""Refine unrendered owned dark-soil candidate; archive its exact first native bytes."""
import bpy,json,hashlib,shutil
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');N=R/'notes/world_v016';report=json.loads((N/'art_study_build_v045b.json').read_text());p=Path(bpy.data.filepath);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==report['source_sha256'];assert p==R/'shots/world/WTSC_Open_Battlefield_Art_Study_v045b.blend'
archive=R/'shots/integration/v045b/Initial_Unrendered_Dark_Palette_v045b.blend';archive.parent.mkdir(parents=True,exist_ok=True);assert not archive.exists();shutil.copyfile(p,archive);assert hashlib.sha256(archive.read_bytes()).hexdigest()==sha
shutil.copyfile(N/'art_study_build_v045b.json',N/'art_study_build_v045b_unrendered_initial.json')
s=bpy.data.scenes[report['world_scene']];m=bpy.data.scenes[report['master_scene']];bpy.context.window.scene=s;path=s.objects['v020 | Walking path | continuous blended paint'];nt=path.data.materials[0].node_tree
def mathn(op,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.name='v045b | Organic static patch '+op;n.operation=op
 for i,x in enumerate([a,b]):
  if x is None:continue
  if isinstance(x,(int,float)):n.inputs[i].default_value=x
  else:nt.links.new(x,n.inputs[i])
 return n.outputs[0]
def remap(x,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.name='v045b | Organic feather, no moving input';n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
 for name,value in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=value
 nt.links.new(x,n.inputs[0]);return n.outputs[0]
geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0]);coords=nt.nodes['v045b | Uniform world-scale soil texels - no strip sampling']
# Uniform source density matches the apparent grain of the original near bank:
# bank mean~243px/metre at11.01m; path148.224px/metre at18.06m.
for index,axis,scale,offset in [(0,'X',.0965,.37),(1,'Z',.14475,.21)]:nt.links.new(mathn('PINGPONG',mathn('ADD',mathn('MULTIPLY',xyz.outputs[axis],scale),offset),1),coords.inputs[index])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.name='v045b | Fixed soil/plant feather breakup';noise.inputs['Scale'].default_value=3.1;noise.inputs['Detail'].default_value=2;nt.links.new(geo.outputs['Position'],noise.inputs[0]);edgeoffset=mathn('MULTIPLY',mathn('SUBTRACT',noise.outputs['Fac'],.5),.10)
uv=nt.nodes['v045b | Existing path paint coordinates'];v=mathn('ADD',uv.outputs['Y'],edgeoffset);lower=remap(v,.36,.64,1,0)
sites=[];spec=[(104.85,.38),(107.35,.12),(109.25,.18),(110.65,.50),(113.8,.28)]
for center,radius in spec:
 distance=mathn('ABSOLUTE',mathn('ADD',mathn('SUBTRACT',xyz.outputs['X'],center),mathn('MULTIPLY',edgeoffset,.35)));sites.append(remap(distance,radius*.36,radius,1,0))
site=sites[0]
for value in sites[1:]:site=mathn('MAXIMUM',site,value)
weight=mathn('MULTIPLY',lower,mathn('SUBTRACT',1,site));target=nt.nodes['v045b | Sparse fixed plant sites and soil negative space'];nt.links.new(weight,target.inputs[0])
row=report['changed_materials'][-1];row.update({'method':'Original v044road below sparse plant sites; quiet areas use original ground underpainting with original near-bank dark earth multiplier(.13,.17,.16). Uniform world-scaled source density148.224px/metre, calibrated to the apparent near-bank texture scale. Fixed3Dnoise makes feather boundaries organic; no clamped/stretched source strips, pale road frontage, character/camera/time inputs.','source_pixel_density_per_metre':[148.224,148.224],'plant_sites_x_m':spec,'noise_scale':3.1,'noise_uv_edge_amplitude':.10})
report['unrendered_first_owned_native_archived']={'path':str(archive),'sha256':sha};report['first_test_gate']=[1849,1901];report['pending']='First two actual4KPNGs1849/1901 must read continuously before rendering fullsix. Movie remains prohibited pending coordinated review.'
note=bpy.data.texts['CURRENT v045b | Art-only frame-first provenance'];note.clear();note.write(json.dumps(report,indent=2));bpy.context.window.scene=m;m.frame_set(1849);bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);report['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();(N/'art_study_build_v045b.json').write_text(json.dumps(report,indent=2));print('V045B_ORGANIC_DARK_SOIL_NATIVE_SAVED',report['source_sha256'],flush=True)
