import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv012 | drawn expansion and seated contacts'];bpy.context.window.scene=s;c=bpy.data.collections['FXv012 | DRAWN COMPACT IMPACT | distinct onset and contacts'];r=bpy.data.objects['FXv012 | terrain anchor and controls']
def signature():
    h=hashlib.sha256()
    for o in sorted(c.all_objects,key=lambda x:x.name):
        if o.type!='MESH':continue
        h.update(o.name.encode())
        for v in o.data.vertices:h.update(struct.pack('<fff',*v.co))
        if o.data.shape_keys:
            for k in o.data.shape_keys.key_blocks:
                for v in k.data:h.update(struct.pack('<fff',*v.co))
    return h.hexdigest()
before=signature();r['painted']=1.;r.update_tag(refresh={'OBJECT'});s.frame_set(9);bpy.context.view_layer.update();after=signature();assert before==after
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Drawn_Impact_Painted_v012.blend'),compress=True);(P/'evidence/paint_finish.json').write_text(json.dumps({'geometry_before':before,'geometry_after':after,'geometry_unchanged':True,'finish':'Original pigment changes color only. Cel contours, exposures, motion and contacts unchanged.','full_mature_painting_as_pose':False},indent=2));print('DRAWN_PAINT_FINISH_READY',before,flush=True)
