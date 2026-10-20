import bpy,math,json
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];master=bpy.data.scenes['WTSC_MASTER_4K_100S'];bpy.context.window.scene=world
assert bpy.data.filepath.endswith('WTSC_Living_World_v009.blend')
def ground_z(x,y):
    wall=.27*max(0,min(1,(x-13)/.7,(20-x)/.7)) if 13<x<20 else 0
    crater=-.62*math.sin((x-44)/5*math.pi)**2 if 44<x<49 else 0
    title=.1*max(0,math.sin((x-67)*1.8)) if 67<x<94 else 0
    return wall+crater+title+(.16*math.sin(x*.43+y*.37)+.1*math.cos(x*.21-y*.6))*min(1,abs(y)/3)
fixes=[]
for obj in bpy.data.collections['20 | LIVING WORLD dimensional sets'].all_objects:
    if obj.type!='MESH':continue
    if '_Plaster_' in obj.name:
        for mod in list(obj.modifiers):
            if mod.type=='BEVEL':obj.modifiers.remove(mod)
        attr=obj.data.color_attributes.get('PaintVariation')
        tone=.53 if 'Battlefield' in obj.name else 1.
        if attr:attr.data.foreach_set('color',[tone,tone,tone,1.]*len(attr.data))
    if obj.data.shape_keys and ('Washing' in obj.name or 'HangingCanvas' in obj.name):
        basis,wind=obj.data.shape_keys.key_blocks[:2]
        bottom=min(p.co.z for p in basis.data);top=max(p.co.z for p in basis.data)
        for base,point in zip(basis.data,wind.data):
            point.co=base.co.copy();p=point.co;weight=max(0,min(1,(top-p.z)/max(.01,top-bottom)))**1.5
            p.y+=.27*weight*math.sin(p.x*3+p.z*2.8);p.x+=.045*weight*math.sin(p.z*3)
        fixes.append({'object':obj.name,'change':'Washing top edge anchored to rope; free lower edge moves'})
    if obj.data.shape_keys and '_Grass_' in obj.name:
        basis,wind=obj.data.shape_keys.key_blocks[:2]
        for base,point in zip(basis.data,wind.data):
            point.co=base.co.copy();p=point.co;weight=max(0,min(.35,p.z-ground_z(p.x,p.y)))
            p.x+=weight*.21*math.sin(p.x*.8+p.y*1.4);p.y+=weight*.13
    if obj.data.shape_keys and '_TentCanvas_' in obj.name:
        basis,wind=obj.data.shape_keys.key_blocks[:2]
        tents=[(50.8,7.4,3.6,3.3),(55.4,10.7,3.8,3.6),(57.4,5.7,3.2,3.3)]
        for base,point in zip(basis.data,wind.data):
            point.co=base.co.copy();p=point.co;x,y,w,d=min(tents,key=lambda t:(p.x-t[0])**2+(p.y-t[1])**2)
            u=max(0,min(1,(p.y-y)/d+.5));v=max(0,min(1,abs(p.x-x)/(w/2)))
            weight=math.sin(math.pi*u)*math.sin(math.pi*v)
            if u<.002 or u>.998:weight=max(0,1-abs(abs(p.x-x)-w*.125)/(w*.375))*max(0,1-(p.z-ground_z(x,y))/2.55)
            p.y+=.15*weight*math.sin(p.x*3+p.z*2);p.z+=.035*weight*math.sin(p.y*5)
        fixes.append({'object':obj.name,'change':'Tent ridge and guyed boundaries anchored; fabric and free flap edges move'})
world['technical_scope']='4K dimensional environment pass. Character performance remains a held GP pair; this is not a completed character-animation trailer.'
world['quality_status']='Environment production iteration v010, with original native models and animated ambience. Needs artistic review; not final quality approval.'
world.render.resolution_percentage=100;master.render.resolution_percentage=100
world.render.filepath='//../../renders/living_world/still_'
master.render.filepath='//../../renders/living_world/WTSC_Living_World_4K_v010.mp4'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.region_3d.view_perspective='CAMERA';space.shading.type='MATERIAL';space.overlay.show_overlays=False
world.frame_set(1);master.frame_set(1);bpy.context.window.scene=world
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_Living_World_v010.blend'))
(ROOT/'notes/living_world/source_final_fixes_v010.json').write_text(json.dumps(fixes,indent=2))
print(json.dumps({'saved':bpy.data.filepath,'cloth_fixes':len(fixes),'settings':[3840,2160,24,2400]}))
