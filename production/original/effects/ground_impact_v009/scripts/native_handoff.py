"""Native dependency export and independent empty-scene append/retime test."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
source=Path(bpy.data.filepath);before=hashlib.sha256(source.read_bytes()).hexdigest()
s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s
c=bpy.data.collections['FXv009 | GROUND IMPACT | baked Bullet and crater'];root=bpy.data.objects['FXv009 | impact anchor and controls']
asset=P/'native/WTSC_Ground_Debris_Append_v009d.blend'
if 'dust' in root:del root['dust']
root['status']='Ground-first motion prototype. See review; not an accepted finished explosion.'
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
def sample(scene,root,frame):
    root.update_tag(refresh={'OBJECT'});scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();result={}
    for o in c.all_objects:
        if o.type!='MESH':continue
        ev=o.evaluated_get(dg);result[o.name]={'location':[v for p in ev.data.vertices for v in (ev.matrix_world@p.co-root.location)],'scale':list(ev.scale)}
    return result
base=sample(s,root,20)
bpy.ops.wm.read_factory_settings(use_empty=True);test=bpy.context.scene;test.name='FXv009 | independent APPEND TEST';test.render.fps=24
with bpy.data.libraries.load(str(asset),link=False) as (a,b):b.collections=['FXv009 | GROUND IMPACT | baked Bullet and crater']
c=b.collections[0];test.collection.children.link(c);root=next(o for o in c.all_objects if 'impact anchor and controls' in o.name)
def evaluate(fr):
    root.update_tag(refresh={'OBJECT'});test.frame_set(int(fr),subframe=fr-int(fr));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();return {o.name:[v for p in o.evaluated_get(dg).data.vertices for v in (o.evaluated_get(dg).matrix_world@p.co-root.location)] for o in c.all_objects if o.type=='MESH'}
now=evaluate(20);err=max(abs(a-b) for n in now for a,b in zip(now[n],base[n]['location']));assert err<1e-4,err
root['start_frame']=107.;retimed=evaluate(120);retimeerr=max(abs(a-b) for n in now for a,b in zip(now[n],retimed[n]));assert retimeerr<1e-4,retimeerr
root['size']=1.7;scaled=evaluate(120);scaleerr=max(abs(b-1.7*a) for n in now for a,b in zip(now[n],scaled[n]));assert scaleerr<1e-4,scaleerr
root['size']=1.;root['start_frame']=7.;root['speed']=2.;fast=evaluate(13.5);speederr=max(abs(a-b) for n in now for a,b in zip(now[n],fast[n]));assert speederr<1e-4,speederr
root['speed']=1.;evaluate(20)
invalid=[];external=[]
owners=set(c.all_objects)
for ob in c.all_objects:
    if ob.type=='MESH':
        if ob.data.shape_keys:owners.add(ob.data.shape_keys)
        for m in ob.data.materials:
            if m and m.node_tree:owners.add(m.node_tree)
for owner in owners:
    ad=owner.animation_data
    if not ad:continue
    for f in ad.drivers:
        if not f.driver.is_valid:invalid.append([owner.name,f.data_path])
        for v in f.driver.variables:
            for target in v.targets:
                if target.id and target.id not in owners:external.append([owner.name,target.id.name])
assert not invalid,invalid
assert not external,external
assert not any(o.type in {'CAMERA','LIGHT'} for o in c.all_objects)
assert len(bpy.data.images)==0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Ground_Debris_Append_Test_v009d.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report={'append_file':asset.name,'append_file_bytes':asset.stat().st_size,'append_file_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'objects':len(c.all_objects),'images':len(bpy.data.images),'camera_light_count':0,'external_driver_ids':external,'invalid_drivers':invalid,'append_position_error':err,'start_frame_offset_test':{'old_start':7,'new_start':107,'old_frame':20,'new_frame':120,'max_error':retimeerr},'scale_test':{'factor':1.7,'max_error':scaleerr},'speed_test':{'factor':2,'old_frame':20,'new_frame':13.5,'max_error':speederr},'source_hash_unchanged':before,'artistic_acceptance':'Not established by native tests. See actual visual assessment.'}
(P/'evidence/append_test_v009d.json').write_text(json.dumps(report,indent=2));print('GROUND_APPEND_TESTED',json.dumps(report),flush=True)
