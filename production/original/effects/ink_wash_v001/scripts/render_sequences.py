import bpy,json,sys,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
manifest=json.loads((P/'evidence/asset_manifest.json').read_text());records=[]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(P/'native/WTSC_Ink_Wash_FX_Library_v001.blend'),link=False) as (src,dst):dst.collections=[n for n in src.collections if n.startswith('FX0')]
collections={c.name:c for c in dst.collections}
for spec in manifest['assets']:
    name=spec['collection'];c=collections[name];s=bpy.data.scenes.new('RGBA | '+name);bpy.context.window.scene=s;s.collection.children.link(c)
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.cycles.max_bounces=1;s.cycles.transparent_max_bounces=32;s.render.threads_mode='FIXED';s.render.threads=2
    s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.fps=24
    s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=25
    s.view_settings.view_transform='Standard';s.view_settings.look='None';s.world=bpy.data.worlds.new(name+' | world');s.world.color=(0,0,0)
    d=bpy.data.cameras.new(name+' | RGBA camera');d.type='ORTHO';d.ortho_scale=8 if name.startswith(('FX04','FX05')) else 6
    centerz=1.5;cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=(0,-20,centerz);cam.rotation_euler=(math.pi/2,0,0);s.camera=cam
    sample=[32,32,32,6,6,16,48,48,48][manifest['assets'].index(spec)]
    snapshot=P/'previews/native_assets';snapshot.mkdir(exist_ok=True)
    s.frame_set(sample);s.render.filepath=str(snapshot/f'{name}.png');bpy.ops.render.render(write_still=True)
    # Three complete low-cost working sequences. The other effects remain native,
    # with transparent stills and this script available for later exports.
    if name not in ['FX01_Explosion_Tall_Charcoal','FX06_Impact_Dry_Dust','FX09_Burning_Debris_Loop']:continue
    folder=P/'sequences'/name;folder.mkdir(exist_ok=True)
    s.render.resolution_x=256;s.render.resolution_y=256;s.cycles.samples=8
    s.frame_start=1;s.frame_end=spec['frames'];s.render.filepath=str(folder)+'/'
    rec={'collection':name,'folder':str(folder.relative_to(P)),'fps':24,'frame_range':[1,s.frame_end],'pixels':[256,256],'alpha':'straight/unassociated PNG RGBA','view_transform':'Standard, display-referred sRGB','pixel_anchor_xy_top_left':[128,round(256*(.5+centerz/d.ortho_scale),3)],'world_width_and_height_m':d.ortho_scale,'camera_center_x_z':[0,centerz],'loop':spec['loop'],'reason_for_subset':'Production four-worker4K render active; only three complete modest CPU working sequences exported. All nine native collections and individual transparent512px stills included.'}
    records.append(rec);(P/'evidence/sequence_manifest.json').write_text(json.dumps(records,indent=2))
    print('FX_SEQUENCE_START',name,s.frame_end,flush=True);bpy.ops.render.render(animation=True);print('FX_SEQUENCE_DONE',name,flush=True)
print('FX_ALL_RGBA_SEQUENCES_COMPLETE',flush=True)
