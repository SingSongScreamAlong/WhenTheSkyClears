import bpy, json, math, runpy, hashlib, sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1]
runpy.run_path(str(P/'scripts/build_locomotion.py'),run_name='__build__')

# Real Append into an empty file, including the dormant native Actions.
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='LOCO | Appendix import and retime test'
with bpy.data.libraries.load(str(P/'native/WTSC_Locomotion_Library_v001.blend'),link=False) as (src,dst):
    dst.collections=['WTSC_LOCO_PAIR_v001']
s.collection.children.link(dst.collections[0])
helper=runpy.run_path(str(P/'scripts/configure_clip.py'));configure=helper['configure']
root=next(o for o in s.objects if o.get('loco_pack'));rigs=[o for o in s.objects if o.type=='ARMATURE']
assert len(rigs)==2
clips=json.loads((P/'evidence/asset_manifest.json').read_text())['clips']
report={'blender':bpy.app.version_string,'append':'factory empty, bpy.data.libraries.load(link=False), collection WTSC_LOCO_PAIR_v001',
 'rigs':[o.name for o in rigs],'native_actions':[a.name for a in bpy.data.actions],'packed_images':[i.name for i in bpy.data.images if i.packed_file],
 'meshes':len([o for o in s.objects if o.type=='MESH']),'geometry':'All visible child meshes planar at rest; native armature deformation, original packed paint','tests':[]}
assert len(bpy.data.actions)==8
assert len(report['packed_images'])>=1
for clip in clips:
    config=configure(clip['id'],repeat=1,root_motion=True)
    records={};scales=[];centres=[];heights=[];scale_details=[]
    for f in range(1,clip['frames']+2):
        s.frame_set(f);bpy.context.view_layer.update()
        for rig in rigs:
            for side,offset in [('near',0),('far',.5)]:
                pb=rig.pose.bones['foot_'+side];p=rig.matrix_world@pb.head
                contact=clip['kind']!='loop' or (((f-1)/clip['frames']+offset)%1)<clip['stance']
                key=(rig.get('character'),side)
                records.setdefault(key,[]).append({'f':f,'p':list(p),'contact':contact})
            scales.extend(float(v) for b in rig.pose.bones for v in b.scale)
            scale_details.extend({'rig':rig.name,'bone':b.name,'frame':f,'scale':list(b.scale)} for b in rig.pose.bones if max(b.scale)>1.025)
        centres.append(sum((rig.matrix_world.translation.x for rig in rigs))/2-root.matrix_world.translation.x)
    drift=[]
    for key,rows in records.items():
        previous=None
        for row in rows:
            if row['contact'] and previous and previous['contact']:
                # A new stance begins after cycle wrap only after airborne samples.
                drift.append(abs(row['p'][0]-previous['p'][0]))
            previous=row
    r={'clip':clip['id'],'config':config,'max_planted_ankle_drift_per_frame_m':max(drift,default=0),'bone_scale_range':[min(scales),max(scales)],
       'pair_average_tracks_travel_error_m':max(abs(c-root['ground_speed_mps']*i/24) for i,c in enumerate(centres)), 'stretched_bones':scale_details[:10]}
    report['tests'].append(r)
    if clip['kind']=='loop':assert r['max_planted_ankle_drift_per_frame_m']<.00002,r
    assert r['bone_scale_range'][1]<1.011,r

# Slower NLA timing must halve root speed and preserve planted contact.
configure('WALK',repeat=1,time_scale=2,root_motion=True)
xs=[]
for f in range(2,19):
    s.frame_set(f);bpy.context.view_layer.update();rig=rigs[0];xs.append((rig.matrix_world@rig.pose.bones['foot_near'].head).x)
report['retime_test']={'NLA_time_scale':2,'speed_mps':root['ground_speed_mps'],'planted_drift_m':max(xs)-min(xs)}
assert report['retime_test']['planted_drift_m']<.00002
# Root controls independent import; shift, scale, then root-motion readback.
root.location=(4,2,.7);root.scale=(1.5,1.5,1.5);configure('WALK',repeat=2,root_motion=False)
s.frame_set(5);bpy.context.view_layer.update()
report['placement_test']={'root_location':list(root.location),'root_scale':list(root.scale),'pair_midpoint':list((rigs[0].matrix_world.translation+rigs[1].matrix_world.translation)/2)}
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.fps=24
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Locomotion_Append_Test_v001.blend'),compress=True)
(P/'evidence/append_validation.json').write_text(json.dumps(report,indent=2))
print('APPEND_CONTACT_RETIME_PASS',json.dumps(report),flush=True)

# Reopen own saved library; render a bounded reel in a single two-thread CPU job.
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Locomotion_Library_v001.blend'),load_ui=False)
s=bpy.context.scene;root=next(o for o in s.objects if o.get('loco_pack'))
configure=runpy.run_path(str(P/'scripts/configure_clip.py'))['configure']
shoe=[]
for clip in clips:
    configure(clip['id'],repeat=1,root_motion=False)
    # Actual deformed mesh support samples, filtered against original paint alpha.
    image=next(i for i in bpy.data.images if i.name.startswith('Pair_Painterly_Near_Age'))
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels);alpha=pixels.reshape(image.size[1],image.size[0],4)[:,:,3]
    candidates=[]
    for ob in s.objects:
        if ob.type!='MESH' or not str(ob.get('skin_region','')).startswith('leg_'):continue
        uv=ob.data.uv_layers[0];d={l.vertex_index:uv.data[l.index].uv.copy() for l in ob.data.loops}
        ids=[]
        for idx,u in d.items():
            px=min(image.size[0]-1,max(0,int(u.x*image.size[0])));py=min(image.size[1]-1,max(0,int(u.y*image.size[1])))
            if py<image.size[1]-860 and alpha[py,px]>.6:ids.append(idx)
        candidates.append((ob,ids))
    support=[]
    for f in range(1,clip['frames']+1):
        s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get()
        for ob,ids in candidates:
            side=ob['skin_region'].split('_')[1];offset=0 if side=='near' else .5
            contact=clip['kind']!='loop' or (((f-1)/clip['frames']+offset)%1)<clip['stance']
            if contact and ids:
                ev=ob.evaluated_get(dg);support.append({'frame':f,'object':ob.name,'min_visible_sample_z':min((ev.matrix_world@ev.data.vertices[i].co).z for i in ids)})
    shoe.append({'clip':clip['id'],'planted_visible_sample_z_range_m':[min(x['min_visible_sample_z'] for x in support),max(x['min_visible_sample_z'] for x in support)]})
(P/'evidence/visible_support_samples.json').write_text(json.dumps(shoe,indent=2))
print('VISIBLE_SHOE_SUPPORT',json.dumps(shoe),flush=True)

previews=[];outidx=1
for clip,count in [('WALK',96),('TRUDGE',88),('CAUTION_CROUCH',48),('CARE_REACH',64)]:
    spec=next(c for c in clips if c['id']==clip);configure(clip,repeat=3,root_motion=False)
    s.frame_end=count;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100
    s.cycles.device='CPU';s.cycles.samples=1;s.render.threads=2
    s.objects['LOCO | clip label'].data.body=f'{clip.replace("_"," ")} / 24fps / {spec["speed"]:.2f}m per sec / {spec["frames"]}fr'
    folder=P/'previews'/clip.lower();folder.mkdir(exist_ok=True)
    for f in range(1,count+1):
        s.frame_set(f);s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
    previews.append({'clip':clip,'frames':count,'fps':24,'pixels':[960,540],'folder':str(folder.relative_to(P)),'source':'Actual Blender 5.2.2 Cycles CPU, native saved library reopened'})
    if clip=='WALK':
        s.frame_set(1);s.render.filepath=str(P/'previews/walk/frame_');s.frame_end=96
        bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Neutral_Walk_Proof_v001.blend'),compress=True)
(P/'evidence/preview_manifest.json').write_text(json.dumps(previews,indent=2))
# Actual native production lettering, copied only for a short readability test.
# No world render, compositor, production data save, or GPU use is involved.
ms=bpy.data.scenes.new('LOCO | native knockout lettering test');bpy.context.window.scene=ms
ms.render.engine='CYCLES';ms.cycles.device='CPU';ms.cycles.samples=1;ms.cycles.use_denoising=False
ms.render.threads_mode='FIXED';ms.render.threads=2;ms.render.fps=24;ms.render.resolution_x=960;ms.render.resolution_y=540;ms.render.resolution_percentage=100
ms.render.film_transparent=True;ms.render.image_settings.file_format='PNG';ms.render.image_settings.color_mode='RGBA'
ms.view_settings.view_transform='Standard';ms.view_settings.look='None'
with bpy.data.libraries.load(str(R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend'),link=False) as (src,dst):
    dst.objects=['v037 | Entire film | WHEN THE SKY CLEARS']
line=dst.objects[0];ms.collection.objects.link(line);line.animation_data_clear();line.parent=None;line.hide_render=False
line.data=line.data.copy();line.data.materials.clear()
m=bpy.data.materials.new('LOCO | temporary native glyph white');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);line.data.materials.append(m)
line.rotation_euler=(0,0,0);line.scale=(1,1,1);line.location=(0,0,0);bpy.context.view_layer.update()
ev=line.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[v.co.copy() for v in me.vertices];ev.to_mesh_clear()
xmin=min(v.x for v in vs);ymin=min(v.y for v in vs);ymax=max(v.y for v in vs);sc=2.025*.995/(ymax-ymin);line.scale=(sc,sc,sc)
cd=bpy.data.cameras.new('LOCO | mask XY camera');cd.type='ORTHO';cd.ortho_scale=3.6;cam=bpy.data.objects.new(cd.name,cd);ms.collection.objects.link(cam);cam.location=(0,0,10);ms.camera=cam
folder=P/'previews/native_mask';folder.mkdir(exist_ok=True)
for f in range(1,97):
    ms.frame_set(f);line.location=(1.8-xmin*sc-(f-1)*6.5/95,-1.007-ymin*sc,0);ms.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/knockout_test.json').write_text(json.dumps({'source_text_object':'v037 | Entire film | WHEN THE SKY CLEARS','source_file':'v038 read-only append','native_mask_frames':96,'fps':24,'pixels':[960,540],'glyph_height_fraction':.995,'scope':'Accelerated 4-second production-lettering fragment over the neutral walk, separate readability study. Not the 100-second production composite. No fonts redistributed in delivery archive.'},indent=2))
audit=json.loads((P/'evidence/native_audit.json').read_text());preserved={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in audit['protected_hashes'].items()}
assert all(preserved.values()),preserved
(P/'evidence/source_preservation.json').write_text(json.dumps(preserved,indent=2))
print('LOCOMOTION_PREVIEW_COMPLETE',flush=True)
