import bpy,json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Control_Asset_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;pack=bpy.data.collections['WTSC_PAINTED_RIG_CAPABILITY_v016'];rigs={o['character']:o for o in pack.all_objects if o.type=='ARMATURE'}
mapping={'scope':'Source-independent control contract only. No imported FBX, motion adapter or retargeting compatibility claim.','collection':pack.name,'axis':'metres; +X travel, +Z up, camera from-Y; in-plane rotation about worldY','travel':'V016 | WORLD_TRAVEL | diagnostic zero','characters':{},'controls':[]}
for w,r in rigs.items():
 head=next(o for o in r.children if o.type=='MESH' and 'original head' in o.name);uv=[head.data.uv_layers.active.data[l.index].uv for l in head.data.loops];scale=1.45/851;cx=636 if w=='BOY' else 1010
 d={'rig':r.name,'bones':{b.name:{'length_m':b.length,'rest_head':list(b.head_local),'rest_tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in r.data.bones},'head_view':'Original right profile; no approved yaw or turnaround','head_source_uv_bbox_px':[min(v.x for v in uv)*1672,min(1-v.y for v in uv)*941,max(v.x for v in uv)*1672,max(1-v.y for v in uv)*941],'neck_registration_source_px':[cx+r.data.bones['head'].head_local.x/scale,907-r.data.bones['head'].head_local.z/scale]}
 if w=='GIRL':d['braid_root_source_px']=[cx+r.data.bones['braid'].head_local.x/scale,907-r.data.bones['braid'].head_local.z/scale]
 mapping['characters'][w]=d
for o in pack.all_objects:
 if o.get('v016_control'):mapping['controls'].append({'object':o.name,'role':o['v016_control'],'parent':o.parent.name if o.parent else None,'properties':{k:o[k] for k in ['Reach','Brace','BraceFollow','TorsoFollow'] if k in o}})
(P/'NATIVE_CONTROL_MAP_v016.json').write_text(json.dumps(mapping,indent=2))
tests=[]
for r in rigs.values():
 for side in ['near','far']:
  w=bpy.data.objects[r['character']+' | WRIST_'+side];w['Reach']=1.;w['Brace']=1.;w.update_tag();bpy.context.view_layer.update()
  hand=next(o for o in r.children if o.get('v007_role')=='drawn_hand' and o.name.endswith(side));keys=hand.data.shape_keys.key_blocks
  tests.append({'who':r['character'],'side':side,'requested':[1,1],'effective':[keys['Reach'].value,keys['Brace'].value],'normalized':abs(keys['Reach'].value-.5)<1e-6 and abs(keys['Brace'].value-.5)<1e-6})
(P/'evidence/hand_shape_safety.json').write_text(json.dumps(tests,indent=2))
known={
 'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend':'77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de',
 'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend':'f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661',
 'shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend':'5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4'}
guards=[]
for name,expected in known.items():
 actual=hashlib.sha256((R/name).read_bytes()).hexdigest();guards.append({'file':name,'expected':expected,'actual':actual,'unchanged':actual==expected})
(P/'evidence/source_integrity.json').write_text(json.dumps(guards,indent=2))
print('FINAL_EVIDENCE',all(t['normalized'] for t in tests),all(g['unchanged'] for g in guards))
