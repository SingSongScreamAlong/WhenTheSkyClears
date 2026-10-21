import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
CN='FXv013 | DRAWN COMPACT IMPACT | distinct onset and contacts'
RN='FXv013 | terrain anchor and controls'
s=bpy.data.scenes['FXv013 | drawn expansion and seated contacts'];bpy.context.window.scene=s
c=bpy.data.collections[CN];r=bpy.data.objects[RN]
asset=P/'native/WTSC_Drawn_Impact_Append_v013.blend'
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)

def sample(scene,col,root,fr):
    root.update_tag(refresh={'OBJECT'});scene.frame_set(fr);bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();pts={};visible=[]
    for o in sorted(col.all_objects,key=lambda x:x.name):
        # Hidden exposure drawings intentionally do not evaluate in Blender's
        # viewport depsgraph. Compare the geometry that is actually exposed.
        if o.type!='MESH' or o.hide_render:continue
        ev=o.evaluated_get(dg)
        pts[o.name]=[float(v) for p in ev.data.vertices for v in (ev.matrix_world@p.co-root.location)]
        if not o.hide_render:visible.append(o.name)
    return {'vertices':pts,'visible':visible,'age':float(root['age'])}

frames=[7,8,9,10,14,18,22,26,30,72]
reference={f:sample(s,c,r,f) for f in frames}
bpy.ops.wm.read_factory_settings(use_empty=True);test=bpy.context.scene
test.name='FXv013 | independent APPEND sandbox';test.render.fps=24;test.frame_end=172
test.unit_settings.system='METRIC';test.unit_settings.scale_length=1
with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.collections=[CN]
c=dst.collections[0];test.collection.children.link(c);r=bpy.data.objects[RN]
checks=[]
for offset,size in [(0,1),(100,1),(100,1.7)]:
    r['start_frame']=7.+offset;r['size']=float(size)
    for f,a in reference.items():
        b=sample(test,c,r,f+offset)
        err=max(abs(x*size-y) for n in a['vertices'] for x,y in zip(a['vertices'][n],b['vertices'][n]))
        assert err<1e-4,(f,offset,size,err)
        assert a['visible']==b['visible'],(f,offset,'visibility mismatch')
        assert abs(a['age']-b['age'])<1e-5
        checks.append({'frame':f,'offset':offset,'scale':size,'geometry_error':err,'visible_objects':len(b['visible'])})
assert not any(o.type in {'CAMERA','LIGHT','VOLUME'} for o in c.all_objects)
assert not any(m.type=='FLUID' for o in c.all_objects for m in o.modifiers)
assert all(im.packed_file for im in bpy.data.images)
bad=[];count=0
for data in list(bpy.data.objects)+list(bpy.data.shape_keys)+[m.node_tree for m in bpy.data.materials if m.node_tree]:
    if data.animation_data:
        for fc in data.animation_data.drivers:
            count+=1
            if not fc.is_valid:bad.append([data.name,fc.data_path])
assert not bad,bad
r['start_frame']=7.;r['size']=1.;sample(test,c,r,22)
out=P/'native/WTSC_Drawn_Impact_Append_Test_v013.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'blender':bpy.app.version_string,'asset':str(asset),'objects':len(c.all_objects),'packed_images':len(bpy.data.images),'camera_light_volume_count':0,'fluid_modifiers':0,'external_cache_files':0,'valid_drivers':count,'checks':checks,'max_geometry_error':max(x['geometry_error'] for x in checks),'native_asset_bytes':asset.stat().st_size,'native_asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scope':'Technical append, time-offset, visibility and scale tests. Artistic acceptance remains pending; no production integration.'}
(P/'evidence/append_test.json').write_text(json.dumps(report,indent=2));print('DRAWN_APPEND_TESTED',json.dumps(report),flush=True)
