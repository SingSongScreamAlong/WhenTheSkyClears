import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_MOTION_TRIAL_v042'];bpy.context.window.scene=s;root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');rows=[]
for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
    rows.append({'rig':rig.name,'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones],'meshes':[{'name':o.name,'verts':len(o.data.vertices),'groups':[v.name for v in o.vertex_groups],'materials':[m.name for m in o.data.materials]} for o in rig.children_recursive if o.type=='MESH'],'action_paths':sorted({f.data_path for t in rig.animation_data.nla_tracks for st in t.strips for l in st.action.layers for strip in l.strips for bag in strip.channelbags for f in bag.fcurves})})
(R/'notes/world_v016/trial_rig_schema_v042.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{'rig':r['rig'],'bones':[b['name'] for b in r['bones']],'meshes':[m['name'] for m in r['meshes']]} for r in rows]),flush=True)
