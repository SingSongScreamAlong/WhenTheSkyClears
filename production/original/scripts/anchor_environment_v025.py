import bpy,math,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene;assert s.name=='WTSC_PAINTED_WORLD_4K_100S_v024';s.name='WTSC_PAINTED_WORLD_4K_100S_v025'
target=R/'shots/world/WTSC_Painted_World_Trailer_v025.blend';assert not target.exists()
far=s.objects['v016 | Woods | far silver canopy']
baseline=3+(.5-.825)*(18+16)*.405
height=38*941/1672
far.scale=(.64,1,.64);far.location.z=baseline+height*.64*(.835-.5)
far['depth_design']='Far row projects at 67% of the near-row width, rather than the old 107%.'
for side,x in [('left',12),('right',46)]:
    o=far.copy();o.name='v025 | Far woods continuation '+side;s.collection.objects.link(o);o.location.x=x;o.location.y=18.015

# Replace cropped strips of the same woods painting with whole isolated foreground trees.
im=bpy.data.images.load(str(R/'sets/painted_layers/Foreground_Tree_v001.png'),check_existing=True);im.pack()
m=bpy.data.materials.new('v025 | Whole foreground oak paint');m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
t=nt.nodes.new('ShaderNodeTexImage');t.image=im;t.extension='CLIP';hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.52;hsv.inputs['Value'].default_value=.30;nt.links.new(t.outputs['Color'],hsv.inputs['Color']);clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.inputs['From Min'].default_value=.045;clean.inputs['From Max'].default_value=.96;nt.links.new(t.outputs['Alpha'],clean.inputs[0])
em=nt.nodes.new('ShaderNodeEmission');nt.links.new(hsv.outputs[0],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(clean.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
for i,o in enumerate([o for o in s.objects if o.name.startswith('v016 | Foreground oak transition ')]):
    x,y=o.location.x,o.location.y;w=9;h=6
    d=bpy.data.meshes.new('v025 | Whole rooted oak grid');nx,nz=40,32
    d.from_pydata([((u/nx-.5)*w,0,v/nz*h) for v in range(nz+1) for u in range(nx+1)],[],[(v*(nx+1)+u,v*(nx+1)+u+1,(v+1)*(nx+1)+u+1,(v+1)*(nx+1)+u) for v in range(nz) for u in range(nx)]);d.update();uv=d.uv_layers.new(name='Whole oak UV')
    for loop in d.loops:j=loop.vertex_index;uv.data[loop.index].uv=(j%(nx+1)/nx,j//(nx+1)/nz)
    d.materials.append(m);o.data=d;o.name='v025 | Whole rooted foreground oak '+str(i);o.location=(x,y,.30)
    o.shape_key_add(name='Basis');key=o.shape_key_add(name='Wind | base pinned');key.slider_min=-1
    for p in key.data:p.co.x+=.08*max(0,(p.co.z/h-.10)/.9)**1.7
    f=key.driver_add('value');f.driver.expression=f'.65*sin(frame/47+{i})+.25*sin(frame/21+{i})+.1*sin(frame/117)'

# Origin at emitter: scale/billow develops upward while the column base stays on the chimney/fire.
specs={'Bakery chimney':(4.44,11.995,5.27,4.2),'Far chimney':(11.5,11.995,4.5,3.1),'Camp smoke':(51,9.995,1.8,5.5),'Battlefield smoke':(62,14,1.2,9),'Far battlefield smoke':(72,24,1,11)}
for o in list(s.objects):
    label=next((k for k in specs if o.name.startswith('v016 | '+k+' | wisp ')),None)
    if not label:continue
    x,y,z,h=specs[label]
    for axis in [0,2]:
        try:o.driver_remove('location',axis)
        except (TypeError,RuntimeError):pass
    for p in o.data.vertices:p.co.z+=h/2
    if o.data.shape_keys:
        for key in o.data.shape_keys.key_blocks:
            for p in key.data:p.co.z+=h/2
    o.location=(x,y,z);o['attachment']='Object origin at physical emitter; scale and pinned wind extend upward, never translate the base.'
# Remove unregistered curtain/lantern overlays; registered window flicker remains inside facade UVs.
for name in ['v016 | School torn curtain | upper edge pinned','v016 | Warm painted light pool 1']:
    if name in s.objects:bpy.data.objects.remove(s.objects[name],do_unlink=True)
for text in bpy.data.texts:
    if text.name.startswith('START HERE v024'):
        value=text.as_string().replace('v024','v025')+'\nAdditional motion coherence: smaller distant woods; whole isolated foreground oaks replace cropped duplicate strips; smoke object origins sit on their emitters; unregistered curtain and lantern overlays removed.\n'
        text.name='START HERE v025 | Painted world trailer';text.clear();text.write(value)
s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v025.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report={'source':str(target),'verified_additional_findings':[{'finding':'Identical woods paintings at two depths projected at nearly the same size','old_far_over_near_ratio':(38/(34*.72))/(23/(22*.72)),'new_ratio':(38*.64/(34*.72))/(23/(22*.72)),'correction':'Far row physically smaller; foreground transitions now use a separate whole-tree painting.'},{'finding':'Whole smoke cards had independent root translation drivers','correction':'Origins relocated to emitters; object location drivers removed, with upward billow/scale retained.'}],'source_panorama':'New wide painting generating; v025 not the final background checkpoint.'}
(R/'notes/world_v016/attachment_corrections_v025.json').write_text(json.dumps(report,indent=2))
s.frame_set(721);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'renders/world_v016/woods_attachment_v025.png');bpy.ops.render.render(write_still=True)
