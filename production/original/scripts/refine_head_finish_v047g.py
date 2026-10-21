"""Continue the new turn into a matching painted profile, rather than popping to old hair."""
import bpy,json,hashlib,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';prior=json.loads((N/'build_v047f.json').read_text())
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v047g.blend';assert not out.exists()
s=bpy.data.scenes[prior['world_scene']];m=bpy.data.scenes[prior['master_scene']];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');rig=next(o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')=='GIRL')
old=next(o for o in rig.children if 'original-painted look toward boy' in o.name);old.animation_data_clear();old.hide_render=True;old.hide_viewport=True
original=next(o for o in rig.children if 'original head and attached braid' in o.name)
name='Girl_Left_Profile_v047.png';path=R/'characters/head_turn_v047'/name
info=json.loads((R/'characters/head_turn_v047/contours.json').read_text())[name];outline=info['contour'];W,H=info['size']
ax,ay,scale=595,1000,.000434;rest=rig.data.bones['head'].matrix_local.copy()
points=[(rest.translation.x+(x-ax)*scale,-.047,rest.translation.z+(ay-y)*scale) for x,y in outline]
me=bpy.data.meshes.new('v047g | matching painted profile editable contour');me.from_pydata(points,[],[tuple(range(len(points)))]);me.update()
ob=bpy.data.objects.new('v047g | matching original-girl left profile',me);s.collection.objects.link(ob);ob.parent=rig
uv=me.uv_layers.new(name='Original generated matching profile registered to contour')
for loop in me.loops:
 x,y=outline[loop.vertex_index];uv.data[loop.index].uv=(x/W,1-y/H)
im=bpy.data.images.load(str(path),check_existing=True);im.pack();mat=original.data.materials[0].copy();mat.name='v047g | matching profile with original event light'
images=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==1;images[0].image=im;me.materials.append(mat)
group=ob.vertex_groups.new(name='head');group.add(list(range(len(points))),1,'REPLACE');modifier=ob.modifiers.new('Unchanged native head pose','ARMATURE');modifier.object=rig
defs=ast.parse((R/'scripts/build_improvement_v047a.py').read_text());defs.body=[n for n in defs.body if isinstance(n,ast.FunctionDef) and n.name=='exposure'];exec(compile(defs,'reused_exposure_clock.py','exec'),globals());exposure(ob,1848,1920)
ob['v047_role']='painted_head_exposure';ob['source_image']=str(path)
ob.shape_key_add(name='Basis');sway=ob.shape_key_add(name='Braid settling after turn');sway.slider_min=-1
for i,(x,y) in enumerate(outline):
 weight=max(0,min(1,(y-780)/430))**2*max(0,min(1,(x-680)/220))
 sway.data[i].co.x+=.010*weight
driver=sway.driver_add('value').driver;driver.expression='0.5*sin((frame-1848)/10)*exp(-max(frame-1848,0)/30)'
gp=bpy.data.grease_pencils.new('v047g | GP matching left profile contour');gpo=bpy.data.objects.new(gp.name,gp);s.collection.objects.link(gpo);gpo.parent=rig
layer=gp.layers.new('Matching painted profile outline',set_active=True);drawing=layer.frames.new(1).drawing;drawing.add_strokes([len(points)]);stroke=drawing.strokes[0];stroke.cyclic=True
for p,co in zip(stroke.points,points):p.position=rest.inverted()@Vector(co);p.radius=.0004;p.opacity=1
ink=bpy.data.materials.new('v047g | contour editing ink');bpy.data.materials.create_gpencil_data(ink);ink.grease_pencil.color=(.012,.012,.012,1);gp.materials.append(ink)
c=gpo.constraints.new('COPY_TRANSFORMS');c.target=rig;c.subtarget='head';gpo.hide_render=True;gpo.hide_viewport=True
row={'object':ob.name,'image':str(path),'exposure':[1848,1920],'neck_pixel_anchor':[ax,ay],'metres_per_pixel':scale,'contour_vertices':len(points),'GP_guide':gpo.name,'braid_motion':'Native damped shape-key follow-through, root area fixed.'}
report=dict(prior);report['head_drawings']=prior['head_drawings']+[row]
allheads=[original,old]+[s.objects[x['object']] for x in report['head_drawings']]
exposures=[]
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();visible=[h.name for h in allheads if not h.hide_render];assert len(visible)==1,(f,visible);exposures.append({'frame':f,'head':visible[0]})
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047g';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v047g'
report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,'head_exposures_all120':exposures,
 'GP_contour_objects':4,'previous_movie':str(R/'renders/refinement_v047f/WTSC_Refinement_v047f_75_80_4K.mp4'),
 'review_correction':'v047f 4K chronology revealed a hair-shape/texture pop at1848 when returning to the older reflected profile. Matching generated true-left-profile painting continues the new turn style, with a small damped braid settle.',
 'unchanged_prefix_frames':[1801,1847],'changed_tail_frames':[1848,1920],
 'artistic_acceptance':False,'full_trailer_propagated':False})
text=bpy.data.texts.new('CURRENT v047g | Matching profile review correction');text.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1901);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v047g.json').write_text(json.dumps(report,indent=2))
print('V047G_NATIVE_BUILT',json.dumps({'native':str(out),'sha256':report['sha256'],'contour':len(points)}),flush=True)
