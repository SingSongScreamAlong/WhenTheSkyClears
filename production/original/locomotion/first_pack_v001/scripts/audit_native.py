import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

P=Path(__file__).resolve().parents[1]
R=P.parents[1]
files=[R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend',R/'shots/WTSC_Girl_Walk_Proof_v002.blend']
report={'blender':bpy.app.version_string,'binary':bpy.app.binary_path,'sources':[]}
for path in files:
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    entry={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scenes':[],'characters':[]}
    for s in bpy.data.scenes:
        cam=s.camera
        entry['scenes'].append({'name':s.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'frames':[s.frame_start,s.frame_end],
            'units':s.unit_settings.system,'metres_per_unit':s.unit_settings.scale_length,
            'camera':{'name':cam.name,'location':list(cam.location),'rotation':list(cam.rotation_euler),'forward':list(cam.matrix_world.to_quaternion()@Vector((0,0,-1))),'up':list(cam.matrix_world.to_quaternion()@Vector((0,1,0)))} if cam else None})
    for o in bpy.data.objects:
        if o.type in ['ARMATURE','GREASEPENCIL'] or ('painted fill' in o.name.lower()):
            row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'scale':list(o.scale),'modifiers':[(m.name,m.type) for m in o.modifiers],'properties':{k:str(v) for k,v in o.items()}}
            if o.type=='ARMATURE':row['bones']=[b.name for b in o.data.bones]
            if o.type=='GREASEPENCIL':
                row['layers']=[{'name':l.name,'frames':len(l.frames)} for l in o.data.layers]
                pts=[o.matrix_world@p.vector for l in o.data.layers for f in l.frames for p in f.drawing.attributes['position'].data]
                if pts:row['bounds']=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
            entry['characters'].append(row)
    report['sources'].append(entry)
report['protected_hashes']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*files,R/'characters/Pair_Painterly_Near_Age_v015.png',R/'characters/Pair_Painterly_Near_Age_Vector_v015.json',R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v037.blend']}
(P/'evidence/native_audit.json').write_text(json.dumps(report,indent=2))
print('LOCOMOTION_READ_ONLY_AUDIT_COMPLETE',bpy.app.version_string,flush=True)
