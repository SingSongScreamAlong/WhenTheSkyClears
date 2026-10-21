import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];L=P.parent/'performance_v003';R=P.parents[1]
source=L/'native/WTSC_Performance_Library_v003.blend';source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v003');root['loco_pack']='WTSC_BATTLEFIELD_WEARY_v005';root.name='BATTLEFIELD_WEARY | CONTROLS'
pair=root.users_collection[0];pair.name='WTSC_BATTLEFIELD_WEARY_PAIR_v005';pair.asset_data.description='Five-second cleaned weary stumble/recovery, both original painted children.120frames/24fps.0.561667m native distance curve. Review before production.'
for obj in [root,*root.children_recursive]:
    if obj.animation_data:
        obj.animation_data.action=None
        for track in list(obj.animation_data.nla_tracks):
            if 'PLAYFUL_SKIP' in track.name:obj.animation_data.nla_tracks.remove(track)
for a in list(bpy.data.actions):
    if 'PLAYFUL_SKIP' in a.name:a.use_fake_user=False;bpy.data.actions.remove(a)
configure=runpy.run_path(str(P/'scripts/configure_battlefield.py'))['configure_battlefield'];rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
src=json.loads((L/'art/native_overlap_sources.json').read_text());rows=json.loads((L/'evidence/performance_samples.json').read_text());samples={(r['who'],r['frame']):r for r in rows if r['clip']=='WEARY_STUMBLE_RECOVER'}
def source_row(who,f):
    q=min(96.,max(1.,1+(f-1-3)/(116/95)));i=int(math.floor(q));j=min(96,i+1);w=q-i;a=samples[who,i];b=samples[who,j]
    return a,b,w
def expected_distance(f):
    a,b,w=source_row('BOY',f);return a['root_distance_m']*(1-w)+b['root_distance_m']*w
configure(start=1801,time_scale=116/95,lead_in_frames=3,root_motion=True)
tr=next(o for o in root.children if 'TRAVEL' in o.name);groups={};scales=[];distance_errors=[]
for f in range(1,121):
    s.frame_set(1800+f);bpy.context.view_layer.update();distance_errors.append(abs(tr.location.x-expected_distance(f)))
    for who,rig in rigs.items():
        a,b,w=source_row(who,f)
        for pb in rig.pose.bones:scales.extend(float(x) for x in pb.scale)
        for side in ['near','far']:
            fa=a['feet'][side];fb=b['feet'][side]
            if not(fa['contact'] and fb['contact'] and fa['phase']==fb['phase']):continue
            pitch=fa['pitch']*(1-w)+fb['pitch']*w;kind='toe' if pitch>=0 else 'heel';px,pz=src['feet'][who+'_'+side][kind];bn=rig.data.bones['foot_'+side];pb=rig.pose.bones[bn.name]
            pt=rig.matrix_world@pb.matrix@bn.matrix_local.inverted()@Vector((px,0,pz));groups.setdefault((who,side,fa['phase'],kind),[]).append((f,list(pt)))
dx=[]
for points in groups.values():
    for (f,a),(g,b) in zip(points,points[1:]):
        if g==f+1:dx.append(abs(a[0]-b[0]))
test={'fps':24,'frames':120,'seconds':5.,'source_clip_frames':96,'time_scale':116/95,'lead_in_frames':3,'action_start_global_frame':1804,'tested_global_range':[1801,1920],'boundary_frame':1921,'native_actions':[a.name for a in bpy.data.actions],'root_distance_error_m':max(distance_errors),'max_planted_pivot_dx_m':max(dx),'bone_scale_range':[min(scales),max(scales)],'total_distance_m':expected_distance(120),'source_library':str(source),'source_library_sha256':source_hash,'source_library_preserved':hashlib.sha256(source.read_bytes()).hexdigest()==source_hash}
assert len(bpy.data.actions)==3 and max(distance_errors)<.00001 and max(dx)<.0006 and max(scales)<1.002,test
configure(start=1,time_scale=116/95,lead_in_frames=3,root_motion=False);s.name='BATTLEFIELD75-80s | weary recovery |120frames';s.frame_start=1;s.frame_end=120
s.objects['LOCO | title'].data.body='WHEN THE SKY CLEARS / BATTLEFIELD75-80s / MOTION PROOF'
s.objects['LOCO | clip label'].data.body='WEARY STUMBLE + RECOVERY / BOTH CHILDREN /120FRAMES /24FPS /5SECONDS'
s.objects['LOCO | provisional'].data.body='NATIVE PAINTED2D / REVIEW BEFORE INTEGRATION / VARIABLE DISTANCE0.5617m'
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
t=bpy.data.texts.new('configure_battlefield.py');t.write((P/'scripts/configure_battlefield.py').read_text())
t=bpy.data.texts.new('BATTLEFIELD_HANDOFF.txt');t.write((P/'BATTLEFIELD_HANDOFF.txt').read_text())
s.frame_set(1);path=P/'native/WTSC_Battlefield_Weary_Stumble_5s_v005.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
report=[];folder=P/'previews/frames';folder.mkdir(exist_ok=True)
for f in range(1,121):
    s.frame_set(f);bpy.context.view_layer.update();line={'clip':'BATTLEFIELD_WEARY_STUMBLE','frame':f,'feet':[],'ground_translation_m':s.objects['LOCO | traveling ground preview'].location.x}
    for who,rig in rigs.items():
        a,b,w=source_row(who,f)
        for side in ['near','far']:
            aa=a['feet'][side];bb=b['feet'][side];data=src['feet'][who+'_'+side];bn=rig.data.bones['foot_'+side];pb=rig.pose.bones[bn.name];deform=rig.matrix_world@pb.matrix@bn.matrix_local.inverted()
            coords=[world_to_camera_view(s,s.camera,deform@Vector((x,0,z))) for x,z in data['lower_hull']]
            line['feet'].append({'who':who,'side':side,'contact':aa['contact'] and bb['contact'],'pitch':aa['pitch']*(1-w)+bb['pitch']*w,'phase':aa['phase'],'bounds_pixels':[min(p.x for p in coords)*960,min(1-p.y for p in coords)*540,max(p.x for p in coords)*960,max(1-p.y for p in coords)*540]})
    line['ground_row_pixels']=(1-world_to_camera_view(s,s.camera,Vector((0,0,-.025))).y)*540;line['floor_row_pixels']=(1-world_to_camera_view(s,s.camera,Vector((0,0,0))).y)*540;report.append(line)
    s.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/projection_samples.json').write_text(json.dumps(report,indent=2));(P/'evidence/preview_manifest.json').write_text(json.dumps([{'clip':'BATTLEFIELD_WEARY_STUMBLE','frames':120,'fps':24,'pixels':[960,540],'folder':'previews/frames'}],indent=2))
test['native_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(P/'evidence/native_validation.json').write_text(json.dumps(test,indent=2));print('BATTLEFIELD_5S_NATIVE_PROOF_PASS',json.dumps(test),flush=True)

