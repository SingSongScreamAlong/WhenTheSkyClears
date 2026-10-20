import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
source=P/'native/WTSC_Evolving_Eruption_Collection_v003.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.name='FX_APPEND_TEST_v003 | independent source with no scene lighting'
with bpy.data.libraries.load(str(source),link=False) as (a,b):
    b.collections=['FXv003 | Evolving anchored eruption | NO PRODUCTION LIGHTS']
c=b.collections[0];s.collection.children.link(c)
root=bpy.data.objects['FXv003 | fixed ground origin and controls']
root.location=(0,0,0);root['size']=1.1;root['start_frame']=24.0;root.update_tag();s.render.fps=24
states=[];driver_count=0;bad=[];external=[]
for age in [1,6,14,18,36,66,95]:
    s.frame_set(24+age);bpy.context.view_layer.update()
    live=[]
    for ob in c.all_objects:
        if 'rolling smoke ' in ob.name:
            m=ob.data.materials[0];alpha=m.node_tree.nodes['Birth rise and independent dissipating lifetime'].inputs[1].default_value
            if alpha>0:live.append({'object':ob.name,'opacity_envelope':alpha,'centre':list(ob.location),'roll_radians':ob.rotation_euler.y,'scale_xz':[ob.scale.x,ob.scale.z]})
    hot=bpy.data.materials['FXv003 | detailed soot internal light and cooling'].node_tree.nodes['Shot age opacity'].inputs[1].default_value
    states.append({'age':age,'root':list(root.matrix_world.translation),'size':list(root.scale),'hot_envelope':root['hot_envelope'],'hot_paint_alpha':hot,'active_billows':live})
    assert max(abs(v-1.1) for v in root.scale)<1e-5
    assert root.matrix_world.translation.length<1e-6
    if age>=14:assert hot==0 and root['hot_envelope']==0
ids=list(c.all_objects)+list(bpy.data.shape_keys)+[m.node_tree for m in bpy.data.materials if m.node_tree]
for owner in ids:
    if owner.animation_data:
        for f in owner.animation_data.drivers:
            driver_count+=1
            if not f.driver.is_valid:bad.append({'id':owner.name,'path':f.data_path})
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id is not None and t.id != root:external.append({'id':owner.name,'target':t.id.name})
assert not bad and not external,(bad,external)
assert not any(ob.type=='LIGHT' for ob in c.all_objects)
images=[{'name':im.name,'packed':bool(im.packed_file),'pixels':list(im.size),'alpha':im.alpha_mode} for im in bpy.data.images if im.type!='RENDER_RESULT']
assert len(images)==3 and all(im['packed'] for im in images)
assert all(ob.parent==root for ob in c.all_objects if ob!=root)
s.frame_start=0;s.frame_end=119;s.frame_set(60)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Append_Test_v003.blend'),compress=True)
production=json.loads((P.parent/'benchmark_v002/evidence/benchmark_build.json').read_text())
unchanged=hashlib.sha256(Path(production['source']).read_bytes()).hexdigest()==production['source_sha256'];assert unchanged
report={'objects':len(c.all_objects),'driver_count':driver_count,'invalid_drivers':bad,'driver_ids_outside_root':external,'native_lights':0,'packed_images':images,'states':states,'anchor_move_test':'origin0, timing24, size1.1, all children parented','production_source_unchanged':unchanged,'collection_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'artistic_status':'Technical validation only; review five-second comparison for motion quality.'}
(P/'evidence/append_validation_v003.json').write_text(json.dumps(report,indent=2));print('FX_APPEND_VALIDATED',json.dumps({k:v for k,v in report.items() if k!='states'}),flush=True)
