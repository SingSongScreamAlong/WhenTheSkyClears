"""Bounded contour and value refinement; existing acting and staging are unchanged."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048';N.mkdir(exist_ok=True)
prior=json.loads((R/'notes/improvement_v047/build_v047g.json').read_text())
source=Path(bpy.data.filepath);assert hashlib.sha256(source.read_bytes()).hexdigest()==prior['sha256']
out=R/'shots/world/WTSC_Open_Battlefield_Refinement_v048a.blend';assert not out.exists()
s=bpy.data.scenes[prior['world_scene']];m=bpy.data.scenes[prior['master_scene']];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rigs=[o for o in root.children_recursive if o.type=='ARMATURE']
before={}
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update()
 before[f]={'camera':s.camera.matrix_world.copy(),'root':root.matrix_world.copy(),'bones':{o.name:{p.name:p.matrix.copy() for p in o.pose.bones} for o in rigs}}
changes=[]
for rig in rigs:
 for side in ['near','far']:
  ob=s.objects[f'V007_{rig["character"]} | drawn sleeve {side}']
  maxdelta=0.
  for key in ob.data.shape_keys.key_blocks:
   old=[p.co.copy() for p in key.data];centers=[(old[i]+old[i+1])*.5 for i in range(0,len(old),2)]
   axis=(centers[3]-centers[0]).normalized();normal=(old[1]-old[0]).normalized();A=centers[0]
   # The sleeve itself has a rounded shoulder crown; no separate joint disc.
   for i,(along,width) in enumerate([(-.018,.008),(-.005,.028),(.017,.040)]):
    c=A+axis*along
    for j,sign in enumerate([-1,1]):key.data[2*i+j].co=c+normal*width*sign
   # Small cloth turn at the cuff mouth instead of projecting rectangular corners.
   for i,factor in [(16,.98),(17,.94),(18,.86)]:
    c=centers[i]
    for j in [0,1]:key.data[2*i+j].co=c+(old[2*i+j]-c)*factor
   maxdelta=max(maxdelta,max((p.co-o).length for p,o in zip(key.data,old)))
  for v,p in zip(ob.data.vertices,ob.data.shape_keys.key_blocks['Basis'].data):v.co=p.co
  changes.append({'object':ob.name,'native_pose_drawings':120,'max_vertex_change_m':maxdelta,'method':'Continuous sleeve shoulder crown and softened cuff contours. Existing 38-vertex editable drawing topology, UV, action, anchors and materials retained.'})
 # Match the native cuff overlay to the new mouth contour, otherwise it masks the correction.
 for side in ['near','far']:
  sleeve=s.objects[f'V007_{rig["character"]} | drawn sleeve {side}'];cuff=s.objects[f'V007_{rig["character"]} | drawn source gray cuff {side}']
  for key in cuff.data.shape_keys.key_blocks:
   sk=sleeve.data.shape_keys.key_blocks[key.name]
   for v,p in zip(key.data,list(sk.data)[-8:]):v.co=p.co;v.co.y-=.001
  for v,p in zip(cuff.data.vertices,cuff.data.shape_keys.key_blocks['Basis'].data):v.co=p.co
heads=[]
for row in prior['head_drawings']:
 ob=s.objects[row['object']];old=ob.data.materials[0];mat=old.copy();mat.name='v048a | restrained charcoal | '+ob.name;ob.data.materials[0]=mat;nt=mat.node_tree
 tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');targets=[l.to_socket for l in tex.outputs['Color'].links]
 bw=nt.nodes.new('ShaderNodeRGBToBW');bw.name='v048 | Source pigment luminance';nt.links.new(tex.outputs['Color'],bw.inputs[0])
 mask=nt.nodes.new('ShaderNodeMapRange');mask.name='v048 | Preserve small white eye marks';mask.clamp=True;mask.interpolation_type='SMOOTHERSTEP'
 for k,v in [('From Min',.12),('From Max',.65),('To Min',.40),('To Max',1.)]:mask.inputs[k].default_value=v
 nt.links.new(bw.outputs[0],mask.inputs[0]);mul=nt.nodes.new('ShaderNodeMixRGB');mul.name='v048 | Painterly charcoal compression';mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1.
 nt.links.new(tex.outputs['Color'],mul.inputs[1]);nt.links.new(mask.outputs[0],mul.inputs[2])
 for t in targets:nt.links.new(mul.outputs[0],t)
 heads.append({'object':ob.name,'old_material':old.name,'new_material':mat.name,'dark_pigment_linear_gain':.4,'white_eye_linear_gain':1.,'texture_alpha_and_source_pixels_unchanged':True,'original_reflected_light_downstream':True})
errors={'camera':0.,'root':0.,'all_pose_bones':0.}
for f,row in before.items():
 s.frame_set(f);bpy.context.view_layer.update()
 for k,mat in [('camera',s.camera.matrix_world),('root',root.matrix_world)]:errors[k]=max(errors[k],max(abs(mat[i][j]-row[k][i][j]) for i in range(4) for j in range(4)))
 for rig in rigs:
  for p in rig.pose.bones:errors['all_pose_bones']=max(errors['all_pose_bones'],max(abs(p.matrix[i][j]-row['bones'][rig.name][p.name][i][j]) for i in range(4) for j in range(4)))
assert max(errors.values())==0,errors
s.name='WTSC_OPEN_BATTLEFIELD_REFINEMENT_v048a';m.name='WTSC_OPEN_5S_REFINEMENT_MASTER_v048a'
report=dict(prior);report.update({'native':str(out),'world_scene':s.name,'master_scene':m.name,'parent_native':str(source),'parent_sha256':prior['sha256'],'contour_changes':changes,'head_value_changes':heads,'all120_staging_errors':errors,'scope':'Refine painted contours and material values only. Existing character choreography/camera/root/world/light/FX retained. No new gait.','artistic_acceptance':False,'full_trailer_propagated':False})
t=bpy.data.texts.new('CURRENT v048a | Contour and charcoal review candidate');t.write(json.dumps(report,indent=2))
bpy.context.window.scene=m;m.frame_set(1901);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();(N/'build_v048a.json').write_text(json.dumps(report,indent=2));print('V048A_NATIVE_BUILT',json.dumps({'native':str(out),'sha256':report['sha256'],'errors':errors}),flush=True)
