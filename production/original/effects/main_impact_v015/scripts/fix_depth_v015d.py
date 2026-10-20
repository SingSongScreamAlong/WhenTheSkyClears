"""Minimal transparent-depth/zero-alpha entry fix, preserving c diagnostic."""
import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];cinfo=json.loads((P/'evidence/build_main_impact_v015c.json').read_text())
source=Path(bpy.data.filepath);assert source.resolve()==Path(cinfo['native_context']).resolve()
sha=hashlib.sha256(source.read_bytes()).hexdigest()
s=bpy.data.scenes[cinfo['scene']];bpy.context.window.scene=s
c=bpy.data.collections[cinfo['collection']];r=bpy.data.objects[cinfo['root']]
c.name='FXv015d | PAINTED SOIL RUPTURE | separated native planes'
r.name='FXv015d | fixed origin and evolving mass controls'
s.name='WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v015d'
depths={'Ignition':.045,'RisingTear':.015,'MainFan':-.020,'Collapse':-.055}
changed=[]
for row in cinfo['drawings']:
    name=row['stage'];lo,hi=row['age_exposure'];y=depths[name]
    for obname in row['objects']:
        ob=bpy.data.objects[obname]
        for v in ob.data.vertices:v.co.y=y
        if ob.data.shape_keys:
            for key in ob.data.shape_keys.key_blocks:
                for pt in key.data:pt.co.y=y
        for curve in ob.animation_data.drivers:
            if curve.data_path in{'hide_render','hide_viewport'} and name!='Ignition':
                curve.driver.expression=f'not ({lo}<t<{hi})'
        changed.append({'object':ob.name,'native_y':y,'zero_opacity_entry_hidden':name!='Ignition'})
    row['native_y']=y
s.frame_set(1829);bpy.context.view_layer.update()
native=P/'native/WTSC_Painted_Main_Impact_Context_v015d.blend';asset=P/'native/WTSC_Painted_Main_Impact_Append_v015d.blend'
assert not native.exists() and not asset.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
report=dict(cinfo);report.update({'native_context':str(native),'native_append':str(asset),'scene':s.name,'collection':c.name,'root':r.name,
 'parent_v015c':str(source),'parent_v015c_sha256':sha,'parent_v015c_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==sha,
 'native_render_fix':'Stage planes separated inY; zero-alpha entry frame not drawn; same original RGBA, mass deformation, opacity curves, values, light, debris and scar.',
 'depth_fix_objects':changed,'drawings':cinfo['drawings'],'rendered':False,'artistic_acceptance':False})
(P/'evidence/build_main_impact_v015d.json').write_text(json.dumps(report,indent=2))
print('PAINTED_IMPACT_V015D_DEPTH_FIXED',json.dumps({'native':str(native),'source_c_unchanged':report['parent_v015c_unchanged']}),flush=True)
