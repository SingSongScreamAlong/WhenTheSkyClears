"""Read selected animation sources in Blender; never save a production scene."""
import bpy, hashlib, json, math, sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCES = {
    'full_v064': 'work/procedural_cut_v064/native/WTSC_Procedural_Full_Trailer_v064.blend',
    'walk_v053': 'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend',
    'danger_v065f': 'work/first_danger_conform_v065/native/WTSC_First_Danger_Conformed_v065f.blend',
}

def curves(o):
    ad = getattr(o, 'animation_data', None)
    if not ad or not ad.action: return []
    return [f for l in ad.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]

def span(xs): return [min(xs), max(xs), max(xs)-min(xs)]

report = json.loads((OUT/'native_readback.json').read_text()) if '--walk-only' in sys.argv else {}
for label, rel in SOURCES.items():
    if '--walk-only' in sys.argv and label != 'walk_v053': continue
    path = ROOT / rel
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    entry = {'source': rel, 'sha256_before': before, 'blender': bpy.app.version_string,
             'scenes': [], 'grease_pencil_actors': [], 'rigs': []}
    for s in bpy.data.scenes:
        entry['scenes'].append({'name': s.name, 'range': [s.frame_start,s.frame_end],
            'fps':s.render.fps/s.render.fps_base, 'types':dict(Counter(o.type for o in s.objects)),
            'color_view':s.view_settings.view_transform})
        for o in s.objects:
            if o.type == 'GREASEPENCIL' and any(t in o.name.upper() for t in ['CHILD','PAIR']):
                entry['grease_pencil_actors'].append({'scene':s.name,'name':o.name,'hide_render':o.hide_render,
                    'layers':[{'name':l.name,'frames':[f.frame_number for f in l.frames]} for l in o.data.layers],
                    'modifiers':[m.type for m in o.modifiers],
                    'animation_channels':[f.data_path for f in curves(o)]})
    if label == 'walk_v053':
        s = next(s for s in bpy.data.scenes if s.name.startswith('V053 |'))
        bpy.context.window.scene = s
        rigs = [o for o in s.objects if o.type=='ARMATURE' and o.name.startswith('V044 ')]
        for r in rigs:
            values={n:[] for n in ['pelvis','chest','head','upper_arm_near','upper_arm_far'] if n in r.pose.bones}
            heights=[]
            for i in range(129):
                t=1+i/4; s.frame_set(math.floor(t),subframe=t-math.floor(t)); bpy.context.view_layer.update()
                e=r.evaluated_get(bpy.context.evaluated_depsgraph_get())
                for n in values:
                    b=e.pose.bones[n]; v=b.tail-b.head
                    angle=math.degrees(math.atan2(v.x,v.z))
                    if values[n]:
                        angle += 360*round((values[n][-1]-angle)/360)
                    values[n].append(angle)
                heights.append(e.pose.bones['pelvis'].head.z)
            entry['rigs'].append({'name':r.name,'bone_count':len(r.pose.bones),
                'sagittal_angle_min_max_span_degrees':{n:span(v) for n,v in values.items()},
                'pelvis_height_min_max_span_metres':span(heights),
                'unique_key_times':len(set(round(k.co.x,5) for f in curves(r) for k in f.keyframe_points)),
                'actions':r.animation_data.action.name})
    entry['sha256_after']=hashlib.sha256(path.read_bytes()).hexdigest()
    entry['production_source_unchanged']=entry['sha256_after']==before
    report[label]=entry
    (OUT/'native_readback.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(label, 'UNCHANGED', entry['production_source_unchanged'], flush=True)
print('ANIMATION_NATIVE_AUDIT_COMPLETE',flush=True)
