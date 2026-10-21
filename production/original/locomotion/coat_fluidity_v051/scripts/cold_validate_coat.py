import bpy,json,hashlib,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];old=ROOT/'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend';new=P/'native/WTSC_Controlled_Fluid_Coat_v051.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]}
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves]).encode()).hexdigest()
def snapshot():
 rigs={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};parts={o.name:o for o in bpy.context.scene.objects if o.type=='MESH' and o.parent in rigs.values()};allowed=[n for n,o in parts.items() if o.parent==rigs['BOY'] and o.get('wardrobe_role') in ['body','sleeve']]
 return {'actions':{a.name:ah(a) for a in bpy.data.actions},'bones':{w:{b.name:[tuple(b.head_local),tuple(b.tail_local)] for b in r.data.bones} for w,r in rigs.items()},'geometry_except_boy_coat_sleeves':{n:hashlib.sha256(repr([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() for n,o in parts.items() if n not in allowed},'all_original_uvs_material_slots_and_weights':{n:hashlib.sha256(repr({'uvs':{u.name:[tuple(x.uv) for x in u.data] for u in o.data.uv_layers},'materials':[m.name for m in o.data.materials],'weights':[(v.index,[(g.group,g.weight) for g in v.groups]) for v in o.data.vertices]}).encode()).hexdigest() for n,o in parts.items()},'images':{i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}}
def sample():
 dg=bpy.context.evaluated_depsgraph_get();rigs=[bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']];bones=np.array([list(v) for r in rigs for b in r.evaluated_get(dg).pose.bones for v in [b.head,b.tail]])
 boots=[o for o in bpy.context.scene.objects if o.parent in rigs and o.get('proportion_role')=='boot'];bootpoints=np.array([list(e.matrix_world@v.co) for o in boots for e in [o.evaluated_get(dg)] for v in e.data.vertices])
 C=bpy.data.collections['V046 | restored original painted wardrobe'];coat=next(o for o in C.objects if o.parent==rigs[0] and o.get('wardrobe_role')=='body');e=coat.evaluated_get(dg);verts=np.array([list(e.matrix_world@v.co) for v in e.data.vertices]);areas=[]
 for i in range(64):
  for j in range(16):a,b,c=verts[i*17+j,[0,2]],verts[i*17+j+1,[0,2]],verts[(i+1)*17+j,[0,2]];areas.append(float(np.cross(b-a,c-a)))
 cuff=[]
 for side in ['near','far']:
  o=next(o for o in C.objects if o.parent==rigs[0] and o.get('wardrobe_role')=='sleeve' and o.name.endswith(side));e=o.evaluated_get(dg);cuff.extend([list(e.matrix_world@v.co) for i,v in enumerate(e.data.vertices) if i//9<=3 or i//9>=46])
 return {'bones':bones,'boots':bootpoints,'coat_anchor':verts[:8*17],'sleeve_anchors':np.array(cuff),'areas':np.array(areas)}
reference=[];maxima={k:0. for k in ['bones','boots','coat_anchor','sleeve_anchors']};min_area=float('inf')
for tag,path,scene in [('OLD',old,'V050 | FACE FINISH AND RELAXED HANDS | v049 gait'),('NEW',new,'V051 | BOY COAT FLUIDITY | exact v050 gait')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S
 if tag=='OLD':before=snapshot()
 else:
  after=snapshot();extra=set(after['actions'])-set(before['actions']);assert len(extra)==1
  for k in before:
   if k=='actions':
    for n,h in before[k].items():assert after[k][n]==h,n
   else:assert before[k]==after[k],k
 for i in range(129):
  f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();s=sample()
  if tag=='OLD':reference.append(s)
  else:
   for k in maxima:maxima[k]=max(maxima[k],float(np.max(np.linalg.norm(s[k]-reference[i][k],axis=1))))
   assert np.all(s['areas']*reference[i]['areas']>0),'coat cell inversion';min_area=min(min_area,float(np.min(abs(s['areas']))))
assert max(maxima[k] for k in ['bones','boots','coat_anchor'])<1e-7,maxima
assert maxima['sleeve_anchors']<.0005,maxima
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
assert json.loads((P/'evidence/STATIC_COAT_PROOF.json').read_text())['source_hashes']==hashes
(P/'evidence/COLD_COAT_VALIDATION.json').write_text(json.dumps({'source_hashes':hashes,'sources_unchanged':True,'all_existing_actions_bones_and_non_coat_geometry_exactly_preserved':True,'face_hand_improvements_preserved':True,'all_original_uvs_materials_vertex_weights_packed_payloads_preserved':True,'new_actions':list(extra),'quarter_frame_samples':129,'maximum_baseline_differences_m':maxima,'minimum_coat_cell_area_m2':min_area,'coat_cell_inversions':0,'contact_scope':'Every sampled actual boot vertex matches v050. No new contact error introduced; underlying support motion and its earlier numerical validation are unchanged.','artistic_scope':'Fabric/control integrity only. Robotic body rhythm is intentionally unchanged and needs separate performance work after this cloth-only A/B.'},indent=2));print('V051_COLD_CLOTH_ONLY_CONTACT_AND_ANCHOR_PASS',maxima)
