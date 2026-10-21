import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v019'
names=['v015 | Rear countryside','v015 | Walking path','v015 | Oak frame and near bank','v015 | Painted village']
rows=[]
for f in [1,25,49,193,721,817]:
    s.frame_set(f);bpy.context.view_layer.update();row={'frame':f,'camera':list(s.camera.location),'objects':{}}
    for name in names:
        o=s.objects[name];lo=[v.co for v in o.data.vertices]
        uv=(.14,.23) if 'path' in name.lower() or 'Oak' in name else (.5,.5)
        point=Vector((min(v.x for v in lo)+(max(v.x for v in lo)-min(v.x for v in lo))*uv[0],min(v.y for v in lo)+(max(v.y for v in lo)-min(v.y for v in lo))*uv[1],0))
        p=world_to_camera_view(s,s.camera,o.matrix_world@point)
        row['objects'][name]={'location':list(o.location),'screen_px':[p.x*3840,(1-p.y)*2160],'same_source_uv':uv,'images':[n.image.name for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE']}
    rows.append(row)
findings=[
 {'cause':'One painted oak was split between two depths','evidence':'Walking path and oak frame share Foreground_Ground.png. The near card masks out UV .075-.25; the walking-path card supplies that image region at Y=2 while the upper trunk/canopy uses Y=-5. Identical image features align only in the first camera view, then separate at different perspective speeds.','fix':'Keep the whole oak, including its roots, on the near tree surface; replace the old path crop with the continuous dedicated path surface.'},
 {'cause':'Rear countryside was screen locked','evidence':'The full rear countryside object X was keyed identically to camera X. It contains fields/trees/river as well as distant sky; these did not participate in lateral scene perspective. A UV offset also drifted the entire landscape, not only clouds.','fix':'Stationary world-space distant landscape with a real farther depth and extended paint coverage; cloud drift on sky alone.'},
 {'cause':'Opaque foreground strip had a rectangular edge','evidence':'The v019 bank was an opaque narrow quad. Its upper edge projected near the bottom 7% of the first camera view.','fix':'v022 continuous earth surfaces with irregular feathered blending; no narrow opaque strip.'},
 {'checked':'Bakery/path repaints remain registered to their surfaces','evidence':'They are texture nodes inside the original material, sharing the same mesh UVs; there are no independently moving repaint-overlay objects.'},
 {'checked':'Children remain held','evidence':'One GP object and vector-clipped paint, translation only. Their static feet sliding over a scrolling path is intentional for the user-requested held-pose world pass; gait remains deferred.'}
]
report={'source_preview':'renders/world_v016/WTSC_Motion_Excerpts_1080p_v019.mp4','exact_scene_source':bpy.data.filepath,'sampled_native_projections':rows,'findings':findings,'visual_evidence':'Six decoded preview samples inspected, together with saved native 4K source frames. Findings concern coherence, not a rejection of depth-dependent parallax.'}
(R/'notes/world_v016/layer_motion_diagnosis_v019.json').write_text(json.dumps(report,indent=2))
print('LAYER_MOTION_DIAGNOSIS_SAVED',json.dumps(findings),flush=True)
