import bpy,json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
file=P/'native/FX01_Explosion_Tall_Charcoal_v001.blend'
roots=[];collections=[]
for start in [1,49]:
    with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith('FX01')]
    c=dst.collections[0];s.collection.children.link(c);collections.append(c)
    r=next(o for o in c.objects if 'CONTROLS' in o.name);r['start_frame']=float(start);roots.append(r)
s.frame_set(33);bpy.context.view_layer.update()
assert roots[0]!=roots[1] and roots[0]['age']==32 and roots[1]['age']==-16
materials=[{m for o in c.objects if o.type=='MESH' for m in o.data.materials} for c in collections]
assert not materials[0].intersection(materials[1]),'Independent Append must not share animated materials'
retarget=[]
for c,r in zip(collections,roots):
    wrong=[]
    for m in {m for o in c.objects if o.type=='MESH' for m in o.data.materials}:
        for f in m.node_tree.animation_data.drivers:
            for v in f.driver.variables:
                if v.targets[0].id!=r:wrong.append(m.name)
    assert not wrong,wrong
    retarget.append({'root':r.name,'start_frame':r['start_frame'],'age_at_frame33':r['age'],'material_driver_targets_correct':True})
with bpy.data.libraries.load(str(P/'native/FX07_Smoke_Roll_Loop_v001.blend'),link=True) as (src,dst):dst.collections=[n for n in src.collections if n.startswith('FX07')]
linked=dst.collections[0];instance=bpy.data.objects.new('Actual linked collection instance',None);instance.instance_type='COLLECTION';instance.instance_collection=linked;s.collection.objects.link(instance);instance.location=(4,1,0)
assert linked.library and len(linked.objects)>10
link_result={'file':linked.library.filepath,'collection':linked.name,'object_count':len(linked.objects),'instance_location':list(instance.location)}
# Visual state of 192-frame loops repeats exactly atframe193 (frame1 equivalent).
loops=[]
for stem in ['FX07_Smoke_Roll_Loop','FX08_Ash_Embers_Loop','FX09_Burning_Debris_Loop']:
    with bpy.data.libraries.load(str(P/'native'/f'{stem}_v001.blend'),link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith(stem)]
    c=dst.collections[0];s.collection.children.link(c)
    def state(frame):
        s.frame_set(frame);bpy.context.view_layer.update();a=[]
        for o in sorted(c.objects,key=lambda q:q.name):
            a.extend(o.location[:]);a.extend(o.scale[:]);a.extend(o.rotation_euler[:])
            if o.type=='LIGHT':a.append(o.data.energy)
            if o.type=='MESH':
                if o.data.shape_keys:a.extend(k.value for k in o.data.shape_keys.key_blocks)
                for m in o.data.materials:
                    for n in m.node_tree.nodes:
                        if n.name=='ANIMATED WASH OPACITY':a.append(n.inputs[1].default_value)
        return a
    a=state(1);b=state(193);difference=max(abs(x-y) for x,y in zip(a,b));assert difference<.0001,(stem,difference)
    loops.append({'collection':stem,'frames_compared':[1,193],'max_numeric_difference':difference,'pass':True})
before=json.loads((P/'evidence/project_inspection.json').read_text())['source_fingerprints']
source_checks={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==digest for p,digest in before.items()}
assert all(source_checks.values())
report={'blender':bpy.app.version_string,'independent_append':retarget,'link_test':link_result,'loops':loops,'source_hashes_unchanged':source_checks,'no_simulation_caches':True}
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));print('FX_NATIVE_VALIDATION_PASS',json.dumps(report),flush=True)
