import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv009 | ground debris proof'];bpy.context.window.scene=s;r=bpy.data.objects['FXv009 | impact anchor and controls'];o=bpy.data.objects['FXv009 | coherent tumbling clod 00'];rows=[]
for start,frame in [(7,20),(107,120),(7,20),(107,120)]:
    r['start_frame']=start;r.update_tag(refresh={'OBJECT'});o.update_tag(refresh={'OBJECT'});s.frame_set(frame);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());rows.append({'start':start,'frame':frame,'age':r['age'],'strip_time':o.animation_data.nla_tracks[0].strips[0].strip_time,'evaluated_strip':ev.animation_data.nla_tracks[0].strips[0].strip_time,'location':list(ev.matrix_world.translation-r.location),'drivers':[(f.data_path,f.driver.expression,f.driver.is_valid) for f in o.animation_data.drivers]})
(P/'evidence/retime_probe.json').write_text(json.dumps(rows,indent=2));print('RETIME_PROBE',json.dumps(rows))
