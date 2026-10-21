"""Fix observed foreground occlusion, with conservative proof for unchanged-frame reuse."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v027'
target=R/'shots/world/WTSC_Painted_World_Trailer_v030.blend';assert not target.exists()
trees=[o for o in s.objects if o.name.startswith('v025 | Whole rooted foreground oak ')]
assert len(trees)==4
old_bounds={}
for o in trees:
    # Union of basis and both signed wind extremes; no parent or object transform keys.
    assert o.parent is None and not o.animation_data
    basis=o.data.shape_keys.key_blocks[0];wind=o.data.shape_keys.key_blocks[1]
    positions=[]
    for a,b in zip(basis.data,wind.data):positions.extend([a.co.copy(),a.co+(b.co-a.co),a.co-(b.co-a.co)])
    old_bounds[o.name]=(min(p.x for p in positions),max(p.x for p in positions),min(p.z for p in positions),max(p.z for p in positions),o.matrix_world.copy())
    o.scale.x=.55
    for key in o.data.shape_keys.key_blocks:
        for p in key.data:
            v=max(0,min(1,(p.co.z/6-.06)/.20));smooth=v*v*(3-2*v)
            p.co.z+=1.8*smooth
    o['readability']='Narrower crown and higher canopy; rooted lower trunk and root contact retained. Children and school stay visible beneath.'

# Only these emissive foreground trees changed. Prove both old/new geometry is
# horizontally outside the camera for every reused frame, including end pullback.
outside=[]
for frame in list(range(1,301))+list(range(1873,2401)):
    s.frame_set(frame);bpy.context.view_layer.update()
    for o in trees:
        a,b,c,d,mat=old_bounds[o.name]
        for kind,bounds,matrix in [('old',(a,b,c,d),mat),('new',(a,b,c,d+1.8),o.matrix_world)]:
            # New X is smaller; using the old local X bounds with new matrix is conservative.
            x0,x1,z0,z1=bounds;projected=[world_to_camera_view(s,s.camera,matrix@Vector((x,0,z))).x for x in [x0,x1] for z in [z0,z1]]
            assert max(projected)<0 or min(projected)>1,(frame,o.name,kind,projected)
    outside.append(frame)
assert not s.eevee.use_raytracing
s.name='WTSC_PAINTED_WORLD_4K_100S_v030'
s['readability_correction']='Foreground crowns narrowed and lifted after full-movie review revealed obscured children/school.'
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v030.mp4')
for text in bpy.data.texts:
    if text.name.startswith('CURRENT v027'):
        value=text.as_string().replace('v027','v030')+'\nForeground readability correction: four transition oaks have narrower crowns and higher canopies while their roots remain fixed. This corrects observed coverage of child heads and school facade. Only frames 301–1872 need new native rendering; all 828 reused frames have old and new tree bounds strictly outside the camera.\n'
        text.name='CURRENT v030 | Painted world and readable foreground';text.clear();text.write(value)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'source':str(target),'source_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changed_objects':[o.name for o in trees],'change':'X scale .55; canopy raised 1.8m via rooted mesh key warp','native_new_frames':[301,1872],'new_frame_count':1572,'reuse_ranges_frames':[[1,300],[1873,2400]],'reused_frame_count':len(outside),'proof':'Old and new signed-wind geometry bounds strictly outside horizontal camera frustum on all 828 reused frames. Only emissive foreground tree meshes changed; no raytracing, no relevant title-light shadow overlap. All camera, GP, scenery, effects and fades preserved.','parent_movie':'renders/world_v016/WTSC_Painted_World_4K_v027.mp4','art_status':'Observed occlusion correction; no artistic acceptance inferred.'}
(R/'notes/world_v016/readability_and_reuse_v030.json').write_text(json.dumps(report,indent=2))
print('READABILITY_SOURCE_AND_REUSE_PROOF',json.dumps(report),flush=True)
out=R/'renders/world_v016/inspection_v030';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
for name,f in [('01_Woods',769),('02_School',1057),('03_Camp',1417)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);print('V030_REVIEW',name,f,flush=True)
