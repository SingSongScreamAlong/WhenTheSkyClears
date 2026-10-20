import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Readability_Working_View_v034.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;fore=S.view_layers['V025 | original foreground'];cfg=json.loads((P/'evidence/WORKING_VIEW_BUILD.json').read_text());hands={s:bpy.data.objects['V007_BOY | articulated drawn hand '+s] for s in ['near','far']};guide=bpy.data.collections['V034 | DIAGNOSTIC joint and cloth guides'];xray=bpy.data.collections['V034 | DIAGNOSTIC hand xray overlay'];visibility={o.name:o.hide_render for o in S.objects if o.type in ['MESH','GREASEPENCIL','CURVE']};frames=[1,11,20,27];S.render.threads_mode='FIXED';S.render.threads=2;start=time.time();records=[]
def matte(name,c):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*c,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
ids={'near':matte('V034 hand ID near',(.90,.015,.30)),'far':matte('V034 hand ID far',(.015,.45,.80))}
def restore():
    for n,v in visibility.items():bpy.data.objects[n].hide_render=v
    guide.hide_render=True;xray.hide_render=True
    for side,ob in hands.items():ob.material_slots[0].material=bpy.data.materials[cfg['working_hand_materials'][side]]
def render(mode,f):
    folder=P/'previews'/mode;folder.mkdir(exist_ok=True);S.render.filepath=str(folder/f'{f:04d}.png');bpy.ops.render.render(write_still=True);records.append({'mode':mode,'frame':f,'size':[S.render.resolution_x,S.render.resolution_y]})
for view,camera,size in [('CLOSE','V024 | CLOSE portrait',(480,720)),('SHOT','V020 | CHILD | SHOT',(1280,720))]:
    S.camera=bpy.data.objects[camera];S.render.resolution_x,S.render.resolution_y=size;S.render.resolution_percentage=100
    for f in frames:
        S.frame_set(f);bpy.context.view_layer.update();fore.update();restore();render('WORK_'+view,f);guide.hide_render=False;xray.hide_render=False;render('GUIDE_'+view,f);restore()
        for side,ob in hands.items():ob.material_slots[0].material=ids[side]
        render('ID_FULL_'+view,f)
        for side,ob in hands.items():
            for n in visibility:bpy.data.objects[n].hide_render=True
            ob.hide_render=False;render('ID_ISO_'+side.upper()+'_'+view,f)
        restore()
camdata=bpy.data.cameras.new('V034 isolated hand detail camera');camdata.type='ORTHO';camdata.sensor_fit='HORIZONTAL';camera=bpy.data.objects.new(camdata.name,camdata);S.collection.objects.link(camera);camera.rotation_euler=(math.pi/2,0,0);S.camera=camera;S.render.resolution_x=S.render.resolution_y=384
for f in frames:
    S.frame_set(f);bpy.context.view_layer.update();fore.update()
    for side,ob in hands.items():
        restore()
        for n in visibility:bpy.data.objects[n].hide_render=True
        ob.hide_render=False;vl=fore if side=='near' else bpy.context.view_layer;vl.update();e=ob.evaluated_get(vl.depsgraph);V=[e.matrix_world@v.co for v in e.data.vertices];xmin,xmax=min(v.x for v in V),max(v.x for v in V);zmin,zmax=min(v.z for v in V),max(v.z for v in V);camera.location=((xmin+xmax)/2,-7,(zmin+zmax)/2);camdata.ortho_scale=max(xmax-xmin,zmax-zmin)*1.6;render('DETAIL_'+side.upper(),f)
(P/'evidence/STILL_RENDER_RECORD.json').write_text(json.dumps({'actual_stills':records,'actual_render_count':len(records),'frames':frames,'threads':2,'elapsed_seconds':time.time()-start,'modes':'Working actual-depth values; guided with explicit exact-shape hand xray; full/isolated hand ID masks; enlarged actual hand-mesh views. No long animation rendered.','saved_native_unchanged':True},indent=2));print('V034_DIAGNOSTIC_STILLS_COMPLETE',len(records),time.time()-start,flush=True)
