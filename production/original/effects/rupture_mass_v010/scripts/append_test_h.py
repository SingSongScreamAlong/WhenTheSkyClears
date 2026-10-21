import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s;c=bpy.data.collections['FXv010 | JOINED EARTH RUPTURE and DUST'];r=bpy.data.objects['FXv010 | fixed impact anchor and timing']
source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest();asset=P/'native/WTSC_Earth_Rupture_Append_v010h.blend';bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
def sample(scene,col,root,frame):
    root.update_tag(refresh={'OBJECT'});scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out={}
    for o in col.all_objects:
        if o.type!='MESH':continue
        ev=o.evaluated_get(dg);out[o.name]=[float(v) for p in ev.data.vertices for v in (ev.matrix_world@p.co-root.location)]
    volume=next(o for o in col.all_objects if o.type=='VOLUME').evaluated_get(dg);volume.data.grids.load();return out,volume.data.grids.frame_filepath
base,basefile=sample(s,c,r,20)
bpy.ops.wm.read_factory_settings(use_empty=True);test=bpy.context.scene;test.name='FXv010 | independent APPEND TEST';test.render.fps=24
with bpy.data.libraries.load(str(asset),link=False) as (a,b):b.collections=['FXv010 | JOINED EARTH RUPTURE and DUST']
c=b.collections[0];test.collection.children.link(c);r=next(o for o in c.all_objects if 'fixed impact anchor' in o.name)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Earth_Rupture_Append_Test_v010h.blend'),compress=True)
now,nowfile=sample(test,c,r,20);err=max(abs(x-y) for n in base for x,y in zip(base[n],now[n]));assert err<1e-4,err;assert nowfile.endswith('fluid_data_0020.vdb'),nowfile
r['start_frame']=107.;shift,shiftfile=sample(test,c,r,120);shift_err=max(abs(x-y) for n in base for x,y in zip(base[n],shift[n]));assert shift_err<1e-4,shift_err;assert shiftfile.endswith('fluid_data_0020.vdb'),shiftfile
r['size']=1.7;scaled,scaledfile=sample(test,c,r,120);scaleerr=max(abs(y-1.7*x) for n in base for x,y in zip(base[n],scaled[n]));assert scaleerr<1e-4,scaleerr
r['size']=1.;r['start_frame']=7.;sample(test,c,r,20);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Earth_Rupture_Append_Test_v010h.blend'),compress=True)
assert not any(o.type in {'CAMERA','LIGHT'} for o in c.all_objects);assert not any(m.type=='FLUID' for o in c.all_objects for m in o.modifiers)
images=list(bpy.data.images);assert all(im.packed_file for im in images)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report={'objects':len(c.all_objects),'images':len(images),'all_images_packed':True,'camera_light_count':0,'fluid_simulation_modifiers':0,'append_geometry_error':err,'offset100_geometry_error':shift_err,'offset100_loaded_vdb':shiftfile,'scale1p7_geometry_error':scaleerr,'native_asset_bytes':asset.stat().st_size,'native_asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'cache_dependency':'../cache/dust64_flat/data/fluid_data_0001.vdb ...0120.vdb','proof_source_sha256_unchanged':before,'artistic_status':'Unaccepted prototype; native test does not establish visual force or tutorial match.'}
(P/'evidence/append_test_h.json').write_text(json.dumps(report,indent=2));print('EARTH_APPEND_TEST_DONE',json.dumps(report),flush=True)
