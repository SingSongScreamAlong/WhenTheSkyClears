import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv011 | compact brief impact low dust'];bpy.context.window.scene=s;c=bpy.data.collections['FXv011 | COMPACT IMPACT | brief flash small debris low dust'];r=bpy.data.objects['FXv011 | fixed impact anchor and controls'];asset=P/'native/WTSC_Compact_Impact_Append_v011.blend'
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
def sample(scene,col,root,fr):
    root.update_tag(refresh={'OBJECT'});scene.frame_set(fr);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts={}
    for o in col.all_objects:
        if o.type=='MESH':ev=o.evaluated_get(dg);pts[o.name]=[float(v) for p in ev.data.vertices for v in (ev.matrix_world@p.co-root.location)]
    v=next(o for o in col.all_objects if o.type=='VOLUME').evaluated_get(dg);v.data.grids.load();return pts,v.data.grids.frame_filepath
a,af=sample(s,c,r,20);bpy.ops.wm.read_factory_settings(use_empty=True);test=bpy.context.scene;test.name='FXv011 | independent APPEND test';test.render.fps=24
with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.collections=['FXv011 | COMPACT IMPACT | brief flash small debris low dust']
c=dst.collections[0];test.collection.children.link(c);r=next(o for o in c.all_objects if 'fixed impact anchor' in o.name);out=P/'native/WTSC_Compact_Impact_Append_Test_v011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
b,bf=sample(test,c,r,20);err=max(abs(x-y) for n in a for x,y in zip(a[n],b[n]));assert err<1e-4 and bf.endswith('fluid_data_0020.vdb'),(err,bf)
r['start_frame']=107.;b,bf=sample(test,c,r,120);offseterr=max(abs(x-y) for n in a for x,y in zip(a[n],b[n]));assert offseterr<1e-4 and bf.endswith('fluid_data_0020.vdb'),(offseterr,bf)
r['start_frame']=7.;sample(test,c,r,20);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert not any(o.type in {'CAMERA','LIGHT'} for o in c.all_objects);assert not any(m.type=='FLUID' for o in c.all_objects for m in o.modifiers);assert all(im.packed_file for im in bpy.data.images)
report={'objects':len(c.all_objects),'images':len(bpy.data.images),'all_images_packed':True,'camera_light_count':0,'fluid_modifiers':0,'append_geometry_error':err,'offset100_geometry_error':offseterr,'offset100_loaded_vdb':bf,'native_asset_bytes':asset.stat().st_size,'native_asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'cache_frames':30,'artistic_acceptance':'Pending user review of the single compact test; these are native dependency/control checks only.'}
(P/'evidence/append_test.json').write_text(json.dumps(report,indent=2));print('COMPACT_APPEND_TESTED',json.dumps(report),flush=True)
