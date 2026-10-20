import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE')
P=R/'effects/ink_wash_v001'
rows=[]
for s in bpy.data.scenes:
    s.frame_set(1801)
    cam=s.camera
    row={'scene':s.name,'fps':s.render.fps,'fps_base':s.render.fps_base,'frames':[s.frame_start,s.frame_end],
         'resolution':[s.render.resolution_x,s.render.resolution_y], 'unit_system':s.unit_settings.system,
         'scale_length':s.unit_settings.scale_length,'engine':s.render.engine,'view_transform':s.view_settings.view_transform}
    if cam:
        row['camera']={'name':cam.name,'location':list(cam.matrix_world.translation),'rotation_euler':list(cam.rotation_euler),
            'forward':list(cam.matrix_world.to_quaternion()@Vector((0,0,-1))),'up':list(cam.matrix_world.to_quaternion()@Vector((0,1,0))),
            'lens':cam.data.lens,'type':cam.data.type,'ortho_scale':cam.data.ortho_scale,'shifts':[cam.data.shift_x,cam.data.shift_y]}
    row['reference_objects']=[]
    for o in s.objects:
        if o.type=='GREASEPENCIL' or 'fixed emitter' in o.name or 'Walking path' in o.name:
            ob={'name':o.name,'type':o.type,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions)}
            if o.type=='GREASEPENCIL':
                pts=[o.matrix_world@v.vector for l in o.data.layers for f in l.frames for v in f.drawing.attributes['position'].data]
                if pts: ob['actual_drawing_bounds']=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
            row['reference_objects'].append(ob)
    rows.append(row)
sources=[R/'shots/world/WTSC_World_Atmosphere_v036.blend',R/'scripts/build_spatial_atmosphere_v036.py',R/'sets/fx/Painted_Smoke_Wisp_v016.png',R/'sets/fx/v036/Painterly_Flame.png']
report={'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'inspected_file':bpy.data.filepath,'scenes':rows,
        'source_fingerprints':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'observed_active_processes':'DCC bootstrap PID39896; production v037 background build PID5696. Neither touched.',
        'reuse_gate':{'contract':'dcc-mcp-production-reuse/v1','canonical_source_checked':'https://raw.githubusercontent.com/dcc-mcp/dcc-mcp-core/main/crates/dcc-mcp-gateway/src/gateway/native_resources/agent_workflows.md',
          'date':'2026-10-17','guide_checker_passed':True,'providers':'No directly surfaced DCC tools; CLI absent from selected PATH. Existing skill examined; no installation authorized.',
          'marketplace_search':'DCC marketplace URL not found; official Blender smoke extension query unavailable in web reader. No external compatible asset with verified redistribution rights found.',
          'selected':'Reuse two existing project-owned GPT imagegen paint textures, packed into Blender. New native 2.5D meshes and node materials for the missing explosion/streak controls. No third-party assets or add-ons.'}}
(P/'evidence/project_inspection.json').write_text(json.dumps(report,indent=2))
print('FX_READ_ONLY_INSPECTION_COMPLETE',json.dumps(report),flush=True)
