import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend'),load_ui=False)
report={'blender':bpy.app.version_string,'active_scene':bpy.context.scene.name,'scenes':[]}
for s in bpy.data.scenes:
    roots=[o for o in s.objects if o.get('loco_pack')]
    entry={'scene':s.name,'engine':s.render.engine,'frames':[s.frame_start,s.frame_end],'fps':s.render.fps,'resolution':[s.render.resolution_x,s.render.resolution_y],'objects':len(s.objects),'root_names':[o.name for o in roots]}
    if roots:
        bpy.context.window.scene=s;entry['samples']=[]
        for f in [1801,1837,1850,1858,1881,1910]:
            s.frame_set(f);bpy.context.view_layer.update();cam=s.camera
            row={'frame':f,'camera':{'name':cam.name,'location':list(cam.matrix_world.translation),'rotation':list(cam.rotation_euler),'type':cam.data.type,'ortho_scale':cam.data.ortho_scale,'lens':cam.data.lens},'roots':[]}
            for root in roots:
                rr={'name':root.name,'location':list(root.location),'matrix_world':[list(v) for v in root.matrix_world],'properties':{k:str(v) for k,v in root.items()},'rigs':[]}
                for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
                    rr['rigs'].append({'name':rig.name,'who':rig.get('character'),'world':list(rig.matrix_world.translation),'scale':list(rig.scale),'foot_heads':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ['foot_near','foot_far']},'children':[{'name':o.name,'skin':o.get('skin_region'),'verts':len(o.data.vertices) if o.type=='MESH' else None} for o in rig.children]})
                row['roots'].append(rr)
            entry['samples'].append(row)
    report['scenes'].append(entry)
(P/'evidence/v043_native_audit.json').write_text(json.dumps(report,indent=2));print('V043_READ_ONLY_AUDIT_COMPLETE',flush=True)
