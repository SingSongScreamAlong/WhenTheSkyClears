import bpy,json,csv,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];F=P/'native/WTSC_GP_Coat_Transition_v025.blend'
bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];T=rig.parent;body=bpy.data.objects['LOCO_BOY | PAINT body'];coat=bpy.data.objects['V025 | COAT drawings | editable GP']
C=bpy.data.collections['V025 | separate authored GP coat transition'];gp=bpy.data.grease_pencils.new('V025 | bare torso diagnostic');diag=bpy.data.objects.new('V025 | bare torso diagnostic | optional',gp);C.objects.link(diag);diag.parent=T;layer=gp.layers.new('Pelvis ribcage sternum | no coat',set_active=True);layer.use_lights=False
m=bpy.data.materials.new('V025 diagnostic warm ink');bpy.data.materials.create_gpencil_data(m);m.grease_pencil.show_fill=False;m.grease_pencil.show_stroke=True;m.grease_pencil.color=(.14,.065,.035,1);gp.materials.append(m)
def line(d,V,cyclic=False):
    d.add_strokes([len(V)]);s=d.strokes[-1];s.cyclic=cyclic
    for p,v in zip(s.points,V):p.position=(v.x,-.05,v.z);p.radius=.002;p.opacity=1
for f in range(17,33):
    S.frame_set(f);bpy.context.view_layer.update();d=layer.frames.new(f).drawing;H=rig.pose.bones['pelvis'].head;ch=rig.pose.bones['chest'].tail
    line(d,[H,H.lerp(ch,.5),ch]);line(d,[rig.pose.bones['upper_arm_near'].head,rig.pose.bones['upper_arm_far'].head]);line(d,[H+Vector((-.05,0,0)),H+Vector((.05,0,0))])
    for centre,rx,rz in [(H,.055,.04),(H.lerp(ch,.72),.085,.125)]:line(d,[centre+Vector((rx*math.cos(a*2*math.pi/32),0,rz*math.sin(a*2*math.pi/32))) for a in range(32)],True)
diag.hide_render=True;diag.hide_set(True)
S.frame_set(20);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True)
boots=json.loads((P.parent/'loading_walk_refinement_v024/reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());rows=[]
for i in range(61):
    f=17+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();row={'frame':f,'seconds':(f-17)/30}
    for name,position in [('pelvis',rig.matrix_world@rig.pose.bones['pelvis'].head),('sternum',rig.matrix_world@rig.pose.bones['chest'].tail),('knee_near',rig.matrix_world@rig.pose.bones['shin_near'].head),('knee_far',rig.matrix_world@rig.pose.bones['shin_far'].head)]:
        row[name+'_x']=position.x-T.location.x;row[name+'_z']=position.z
    for side in ['near','far']:
        o=bpy.data.objects[boots[side]['object']];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());V=[e.matrix_world@v.co for v in e.data.vertices]
        # Track fixed source-sole endpoint vertices, not an ankle proxy.
        rest=boots[side]['vertices'];heel=min(range(len(rest)),key=lambda k:rest[k][0]);toe=max(range(len(rest)),key=lambda k:rest[k][0])
        for n,k in [('heel',heel),('toe',toe)]:row[side+'_'+n+'_x']=V[k].x-T.location.x;row[side+'_'+n+'_z']=V[k].z
    rows.append(row)
with (P/'evidence/BARE_BODY_AND_FOOT_ARCS.csv').open('w',newline='') as fp:w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for mode in ['BARE','GP_CLOSE','GP_SHOT']:
    diag.hide_render=mode!='BARE';coat.hide_render=mode=='BARE';body.hide_render=mode=='BARE'
    S.camera=bpy.data.objects['V020 | CHILD | SHOT' if mode=='GP_SHOT' else 'V024 | CLOSE portrait'];S.render.resolution_x,S.render.resolution_y=(960,540) if mode=='GP_SHOT' else (400,600);S.render.resolution_percentage=100
    for f in [19,21,25,28]:S.frame_set(f);S.render.filepath=str(P/f'previews/{mode}_{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V025_FIRST_CHECK_COMPLETE')
