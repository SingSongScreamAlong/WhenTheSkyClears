import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];R=P.parents[1]
library=P/'native/WTSC_Performance_Library_v003.blend'
helper=runpy.run_path(str(P/'scripts/configure_performance.py'));configure=helper['configure']
manifest=json.loads((P/'evidence/build_manifest.json').read_text());src=json.loads((P/'art/native_overlap_sources.json').read_text())
samples=json.loads((P/'evidence/performance_samples.json').read_text());sample={(r['clip'],r['who'],r['frame']):r for r in samples}
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='LOCO v003 | Fresh append test'
with bpy.data.libraries.load(str(library),link=False) as (a,b):b.collections=['WTSC_PERFORMANCE_PAIR_v003']
s.collection.children.link(b.collections[0]);root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v003');rigs={o['character']:o for o in s.objects if o.type=='ARMATURE'}
report={'blender':bpy.app.version_string,'append':'factory-empty Append of WTSC_PERFORMANCE_PAIR_v003','actions':[a.name for a in bpy.data.actions],'packed_images':[i.name for i in bpy.data.images if i.packed_file],'tests':[]}
assert len(rigs)==2 and len(bpy.data.actions)==5
for clip in manifest['clips']:
    configure(clip['id'],repeat=1,root_motion=True);scales=[];groups={};pose1=None
    for f in range(1,clip['frames']+2 if clip['loop'] else clip['frames']+1):
        s.frame_set(f);bpy.context.view_layer.update()
        for who,rig in rigs.items():
            r=sample[clip['id'],who,f]
            for pb in rig.pose.bones:scales.extend(float(v) for v in pb.scale)
            for side in ['near','far']:
                footrow=r['feet'][side];bn=rig.data.bones['foot_'+side];pb=rig.pose.bones[bn.name];data=src['feet'][who+'_'+side];kind='toe' if footrow['pitch']>=0 else 'heel';px,pz=data[kind];point=rig.matrix_world@(pb.matrix@bn.matrix_local.inverted())@Vector((px,0,pz))
                if footrow['contact']:groups.setdefault((who,side,footrow['phase'],kind),[]).append((f,list(point)))
            expected=r['root_distance_m'];actual=rig.matrix_world.translation.x-root.matrix_world.translation.x-(-.5 if who=='BOY' else .5)*root['pair_gap_m']
            assert abs(actual-expected)<.00001,(clip['id'],f,actual,expected)
        if f==1:pose1={who:{p.name:p.matrix.copy() for p in rig.pose.bones} for who,rig in rigs.items()}
    errors=[];support=[]
    for key,rs in groups.items():
        for (f,a),(g,b) in zip(rs,rs[1:]):
            if g==f+1:errors.append(abs(b[0]-a[0]))
        support.extend(abs(p[2]) for _,p in rs)
    maxscale=max(scales);assert maxscale<1.002,(clip['id'],maxscale)
    e=max(errors,default=0);assert e<.00001,(clip['id'],e)
    row={'clip':clip['id'],'max_contact_pivot_dx_m':e,'max_contact_pivot_above_floor_m':max(support,default=0),'bone_scale_range':[min(scales),maxscale]}
    if clip['loop']:
        seam=max(abs(rig.pose.bones[n].matrix[i][j]-m[i][j]) for who,rig in rigs.items() for n,m in pose1[who].items() for i in range(4) for j in range(4));row['pose_loop_seam_max_matrix_error']=seam;assert seam<.00001,seam
    report['tests'].append(row)
configure('WEARY_STUMBLE_RECOVER',time_scale=2,root_motion=True)
travel=next(o for o in root.children if 'TRAVEL' in o.name)
s.frame_set(69);bpy.context.view_layer.update();report['retime']={'time_scale':2,'frame':69,'expected_distance_m':sample['WEARY_STUMBLE_RECOVER','BOY',35]['root_distance_m'],'actual_distance_m':travel.location.x};assert abs(report['retime']['expected_distance_m']-travel.location.x)<.00001
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.fps=24
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Performance_Append_Test_v003.blend'),compress=True)
(P/'evidence/native_validation.json').write_text(json.dumps(report,indent=2));print('V003_NATIVE_APPEND_CONTACT_PASS',json.dumps(report),flush=True)

bpy.ops.wm.open_mainfile(filepath=str(library),load_ui=False);s=bpy.context.scene;root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v003');rigs={o['character']:o for o in s.objects if o.type=='ARMATURE'}
previews=[];projection=[]
for clip in manifest['clips']:
    configure(clip['id'],repeat=3 if clip['loop'] else 1,root_motion=False);folder=P/'previews'/clip['id'].lower();folder.mkdir(exist_ok=True)
    s.objects['LOCO | clip label'].data.body=('PLAYFUL SKIP / step-hop / 0.60m per sec' if clip['loop'] else 'WEARY STUMBLE / toe catch, rescue step, settle / variable speed')+' / v003 STUDY'
    count=clip['reel_frames'];s.frame_start=1;s.frame_end=count;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.device='CPU';s.cycles.samples=2
    for f in range(1,count+1):
        s.frame_set(f);bpy.context.view_layer.update();line={'clip':clip['id'],'frame':f,'feet':[]}
        for who,rig in rigs.items():
            sf=(f-1)%40+1 if clip['loop'] else f;r=sample[clip['id'],who,sf]
            for side in ['near','far']:
                ft=r['feet'][side];data=src['feet'][who+'_'+side];bn=rig.data.bones['foot_'+side];pb=rig.pose.bones[bn.name];deform=rig.matrix_world@pb.matrix@bn.matrix_local.inverted();points=[deform@Vector((x,0,z)) for x,z in data['lower_hull']]
                coords=[world_to_camera_view(s,s.camera,p) for p in points]
                line['feet'].append({'who':who,'side':side,'contact':ft['contact'],'pitch':ft['pitch'],'phase':ft['phase'],'bounds_pixels':[min(p.x for p in coords)*960,min(1-p.y for p in coords)*540,max(p.x for p in coords)*960,max(1-p.y for p in coords)*540]})
        line['ground_row_pixels']=(1-world_to_camera_view(s,s.camera,Vector((0,0,-.025))).y)*540;line['floor_row_pixels']=(1-world_to_camera_view(s,s.camera,Vector((0,0,0))).y)*540
        line['ground_translation_m']=s.objects['LOCO | traveling ground preview'].location.x;projection.append(line)
        s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
    previews.append({'clip':clip['id'],'frames':count,'fps':24,'pixels':[960,540],'folder':str(folder.relative_to(P))})
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native'/('WTSC_'+clip['id']+'_Proof_v003.blend')),compress=True)
(P/'evidence/projection_samples.json').write_text(json.dumps(projection,indent=2));(P/'evidence/preview_manifest.json').write_text(json.dumps(previews,indent=2))
assert hashlib.sha256(Path(manifest['source_library']).read_bytes()).hexdigest()==manifest['source_sha256']
print('V003_ACTUAL_PREVIEWS_COMPLETE',flush=True)

