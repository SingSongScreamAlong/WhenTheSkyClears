import bpy,math,json,hashlib,time,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];B=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text())
JOIN=json.loads((P/'evidence/ORIGINAL_CUFF_TO_SHOE_RELATION.json').read_text())['1'];JN=Vector(JOIN['near']['relative_to_flat_shoe_ankle']);JF=Vector(JOIN['far']['relative_to_flat_shoe_ankle']);JN.y=JF.y=0
AUDIT=json.loads((P/'evidence/ACTUAL_V028_FOOTWEAR_AUDIT.json').read_text());OLDV={s:[Vector(v) for v in AUDIT['frames']['1'][s]['normalized_vertices']] for s in ['near','far']}
def load(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);return bpy.context.scene
def points(o,view):
    view.update();e=o.evaluated_get(view.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
def action_hash(a):
    rows=[]
    for l in a.layers:
        for st in l.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:rows.append((fc.data_path,fc.array_index,fc.extrapolation,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in fc.keyframe_points],[(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None)) for m in fc.modifiers]))
    return hashlib.sha256(repr(rows).encode()).hexdigest()
def coat_hash():
    ob=bpy.data.objects['V025 | COAT drawings | editable GP'];return hashlib.sha256(repr([(f.frame_number,[[(tuple(p.position),p.radius,p.opacity,tuple(p.vertex_color)) for p in s.points] for s in f.drawing.strokes]) for f in ob.data.layers[0].frames]).encode()).hexdigest()
S=load(P/'reference/PREFERRED_MOVEMENT_v028.blend');rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];fg=bpy.data.collections['V025 | retained foreground identity'];fg_names={o.name for o in fg.all_objects};names=[o.name for o in S.objects if o.type=='MESH' and not o.hide_render and ('BOY' in o.name or o.name=='V024 continuous near trouser drawing') and o.name not in [v['object'] for v in B.values()]];actions={a.name:action_hash(a) for a in bpy.data.actions};coat=coat_hash();old={}
for f in range(1,33):
    S.frame_set(f);bpy.context.view_layer.update();fore.update();old[f]={'root':T.matrix_world.copy(),'bones':{b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones},'meshes':{n:points(bpy.data.objects[n],fore if n in fg_names else bpy.context.view_layer) for n in names},'far_pants':points(bpy.data.objects['V024 continuous far trouser drawing'],bpy.context.view_layer),'near_shoe':points(bpy.data.objects[B['near']['object']],bpy.context.view_layer)}
S=load(P/'native/WTSC_Preferred_Walk_Consistent_Shoes_v033.blend');rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;fore=S.view_layers['V025 | original foreground'];maxbone=0.;maxroot=0.;maxmesh=0.;maxnear=0.;maxupper=0.;maxcuff=0.
def original_sole_z(s):
    F=rig.matrix_world@rig.pose.bones['foot_'+s].matrix;R=F.to_3x3()@Matrix(B[s]['flat_bone']).to_3x3().inverted();a=math.atan2(R[0][2],R[0][0]);return F.translation.z+min(-math.sin(a)*v.x+math.cos(a)*v.z for v in OLDV[s])
for f in range(1,33):
    S.frame_set(f);bpy.context.view_layer.update();fore.update();r=old[f];maxroot=max(maxroot,max(abs(T.matrix_world[i][j]-r['root'][i][j]) for i in range(4) for j in range(4)))
    for b in rig.pose.bones:
        W=rig.matrix_world@b.matrix;maxbone=max(maxbone,max(abs(W[i][j]-r['bones'][b.name][i][j]) for i in range(4) for j in range(4)))
    for n,V in r['meshes'].items():maxmesh=max(maxmesh,max((v-w).length for v,w in zip(V,points(bpy.data.objects[n],fore if n in fg_names else bpy.context.view_layer))))
    maxnear=max(maxnear,max((v-w).length for v,w in zip(r['near_shoe'],points(bpy.data.objects['V033 | near | canonical painted shoe'],bpy.context.view_layer))))
    pant=points(bpy.data.objects['V024 continuous far trouser drawing'],bpy.context.view_layer);maxupper=max(maxupper,max((v-w).length for v,w in zip(pant[:490],r['far_pants'][:490])));E=sum(pant[-7:],Vector())/7;E0=sum(r['far_pants'][-7:],Vector())/7;A=(rig.matrix_world@rig.pose.bones['foot_far'].matrix).translation;shoe=bpy.data.objects['V033 | far | canonical painted shoe'];N=shoe.matrix_world.translation;correction=Matrix.Rotation(shoe.rotation_euler.y,4,'Y')@(JN*.97-JF);maxcuff=max(maxcuff,math.hypot(E.x-E0.x-(N.x-A.x)-correction.x,E.z-E0.z-(N.z-A.z)-correction.z))
changed_actions=[n for n,h in actions.items() if action_hash(bpy.data.actions[n])!=h];assert not changed_actions and coat_hash()==coat
maxsole=0.;maxclear=0.;sole_by_side={'near':0.,'far':0.};source_sole={'near':0.,'far':0.};near=bpy.data.objects['V033 | near | canonical painted shoe'];far=bpy.data.objects['V033 | far | canonical painted shoe']
for i in range(993):
    q=i/32;S.frame_set(int(q+1),subframe=q+1-int(q+1));bpy.context.view_layer.update()
    for s,ob in [('near',near),('far',far)]:
        vv=[ob.matrix_world@v.co for v in ob.data.vertices];z=min(v.z for v in vv);t=(q-(0 if s=='near' else 16))%31;toe=18.5 if s=='near' else 19.25
        if t<=toe+1e-9:
            maxsole=max(maxsole,abs(z));sole_by_side[s]=max(sole_by_side[s],abs(z));source_sole[s]=max(source_sole[s],abs(original_sole_z(s)))
        else:maxclear=max(maxclear,abs(z-original_sole_z(s)))
report={'scope':'Cold native preservation/contact safeguards, not artistic acceptance','preferred_source':'v028','source_original_action_count':len(actions),'original_actions_changed':changed_actions,'original_GP_coat_drawing_hash_unchanged':coat_hash()==coat,'preserved_visible_mesh_names':names,'max_all_bone_world_matrix_change':maxbone,'max_root_world_matrix_change':maxroot,'max_preserved_visible_mesh_change_m':maxmesh,'max_near_shoe_vertex_change_m':maxnear,'max_far_upper72percent_trouser_change_m':maxupper,'max_far_cuff_endpoint_fit_error_m':maxcuff,'contact_samples':993,'sample_interval_frames':1/32,'max_support_sole_height_error_m':maxsole,'max_swing_sole_clearance_change_m':maxclear,'one_shared_shoe_mesh':near.data==far.data,'same_UVs_and_material':near.data==far.data,'perspective_scales':[near.scale.x,far.scale.x],'observation_limit':'Continuous playback not observed; matched source/candidate frames and actual movie will be reviewed.'}
report['support_sole_error_by_side_m']=sole_by_side;report['preferred_v028_support_sole_error_by_side_m']=source_sole;report['contact_criterion']='Retained near shoe may preserve baseline subframe sole error, with at most20micrometre increase; corrected far shoe must remain below0.4mm. No unexplained threshold broadening.'
(P/'evidence/COLD_PREFERRED_MOTION_AND_SHOE_CHECK.json').write_text(json.dumps(report,indent=2));assert max(maxbone,maxroot,maxmesh,maxnear,maxupper,maxcuff)<.00002 and sole_by_side['near']<=source_sole['near']+.00002 and sole_by_side['far']<.0004 and maxclear<.0004 and near.data==far.data
if '--verify-only' in sys.argv:
    print('V033_FINAL_COLD_PRESERVATION_PASS',json.dumps(report),flush=True);sys.exit(0)
S.render.threads_mode='FIXED';S.render.threads=2;start=time.time();frames=list(range(1,33))
for mode,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    folder=P/'previews'/('PROOF_'+mode);folder.mkdir(exist_ok=True);S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in (frames if mode=='CLOSE' else [1,4,8,11,13,17,20,24,27,29,32]):S.frame_set(f);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/PROOF_RENDER_RECORD.json').write_text(json.dumps({'actual_frames':frames,'views':{'CLOSE':[480,720],'SHOT':[1280,720]},'threads':2,'elapsed_seconds':time.time()-start},indent=2));print('V033_COLD_CHECK_AND_PROOF_COMPLETE',json.dumps(report),flush=True)
