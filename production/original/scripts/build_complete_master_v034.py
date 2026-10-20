"""Versioned bounded assembly: cached reframed0–70 + clean native70–82 + v033 ending."""
import bpy,json,hashlib
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
out=R/'shots/world/WTSC_Complete_Trailer_Editable_v034.blend';assert not out.exists()
w=bpy.data.scenes['WTSC_WORLD_CENTERED_v033'];e=bpy.data.scenes['WTSC_KNOCKOUT_ENDING_v033'];master=bpy.data.scenes['WTSC_MASTER_4K_103S_v033']
pair=next(o for o in w.objects if o.type=='GREASEPENCIL');pos=pair.data.layers[0].frames[0].drawing.attributes['position'].data
camera=w.camera
# Match exactly the original v030 camera ray projection followed by v033's2x
# finishing crop. Off-axis lens shift preserves all depth/parallax relationships;
# physically moving the camera sideways would cause a discontinuity at70.
camera.animation_data_clear();camera.location=(0,-16,3);camera.data.lens=100;camera.data.shift_x=0;camera.data.shift_y=0
driver=camera.driver_add('location',0).driver;driver.type='SCRIPTED'
v=driver.variables.new();v.name='pair_world_x';v.type='TRANSFORMS';v.targets[0].id=pair;v.targets[0].transform_type='LOC_X';v.targets[0].transform_space='WORLD_SPACE';driver.expression='pair_world_x+1.6891200542449951'
def center():
 bpy.context.view_layer.update();p=[world_to_camera_view(w,camera,pair.matrix_world@p.vector) for p in pos]
 return ((min(p.x for p in p)+max(p.x for p in p))/2,(min(p.y for p in p)+max(p.y for p in p))/2)
bpy.context.window.scene=w;w.frame_set(1249)
c0=center();camera.data.shift_x=1;c1=center();camera.data.shift_x=(.5-c0[0])/(c1[0]-c0[0])
camera.data.shift_y=1;c2=center();camera.data.shift_y=(.5-c0[1])/(c2[1]-c0[1])
samples=[]
for f in [1,1249,1681,1921,1968]:
 w.frame_set(f);c=center();assert abs(c[0]-.5)<1e-5 and abs(c[1]-.5)<1e-5,(f,c)
 samples.append({'frame':f,'pair_center':list(c),'camera':list(camera.location)})
for s in [w,e,master]:s.name=s.name.replace('v033','v034')
w['v034_camera_scope']='Native off-axis100mm lens matches v0332x finishing crop: original physical camera ray position, constantY-16/Z3 until knockout; shared root driver follows route. No original80s pullback, preventing size jump into ending.'
master.render.filepath='//../../renders/world_v016/WTSC_Complete_Trailer_Native_4K_v034.mp4'
master['v034_export_scope']='Actual movie assembly: cached corrected v0300–70 with2x crop; native clean70–82; v033 ending82–103. Master remains fully native editable world0–82+native ending82–103+one packed originalWAV. Cached crop effective1080 detail in UHD output.'
report={'source':str(out),'world_scene':w.name,'ending_scene':e.name,'native_master':master.name,'output':[3840,2160,24],'frames':2472,'seconds':103,'native_world_camera':{'lens_mm':camera.data.lens,'shift_x':camera.data.shift_x,'shift_y':camera.data.shift_y,'constant_y_z':[-16,3],'root_driver':driver.expression},'center_samples':samples,'actual_picture_sections':[{'global':[0,70],'source':'v030 cached world0–70','method':'Uniform2x centered finishing crop; no retime/interpolation','effective_pixels':[1920,1080]},{'global':[70,82],'source':'new native v034 world camera','method':'Native4K off-axis projection matching cached crop; legacy terrain title disabled','effective_pixels':[3840,2160]},{'global':[82,103],'source':'v033 rendered knockout ending','method':'Native4K text alpha. Clean cached world52–70 at2x crop fills82–100; final card100–103','effective_world_fill_pixels':[1920,1080]}],'boundary82_scope':'Exact pair size/center matches. Intentional cut to black as first glyph enters at82; world setting inside letters reuses52–70, not continuous landscape geography.','audio':'One suppliedWAV from0, single90–100fade, silent100–103; do not copy preview audio','last_S_clear':100,'silent_card':[100,103],'held_pair':True,'legacy_title_hidden':bpy.data.collections['v016 | 07 Monumental title terrain'].hide_render}
note=bpy.data.texts.new('CURRENT v034 | Complete103s trailer master');note.write(json.dumps(report,indent=2))
bpy.context.window.scene=master;master.frame_set(1);w.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'notes/world_v016/complete_build_v034.json').write_text(json.dumps(report,indent=2))
# Full-resolution readback before launching the limited world render.
bpy.context.window.scene=w;w.render.resolution_percentage=100;w.render.image_settings.media_type='IMAGE';w.render.image_settings.file_format='PNG'
for f in [1681,1968]:
 w.frame_set(f);w.render.filepath=str(R/f'renders/world_v016/complete_checks_v034/{f}.png');bpy.ops.render.render(write_still=True,scene=w.name)
print('COMPLETE_MASTER_SAVED',str(out),flush=True)
