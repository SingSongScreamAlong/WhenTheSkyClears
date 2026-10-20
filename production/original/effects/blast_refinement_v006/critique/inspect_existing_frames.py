"""Read-only render audit: arrange already-rendered pixels; do not run Blender."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];O=P/'critique';O.mkdir(exist_ok=True)
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
def board(name,frames,folder,crop,tile,columns):
    rows=(len(frames)+columns-1)//columns;w,h=tile
    sheet=Image.new('RGB',(columns*w,rows*(h+30)),(24,28,31));draw=ImageDraw.Draw(sheet)
    for i,frame in enumerate(frames):
        file=folder/f'{frame:04d}.png';im=Image.open(file).convert('RGBA')
        if crop:im=im.crop(crop)
        im=im.resize(tile,Image.Resampling.LANCZOS)
        plate=Image.new('RGBA',tile,(49,54,56,255));plate.alpha_composite(im)
        x=(i%columns)*w;y=(i//columns)*(h+30);sheet.paste(plate.convert('RGB'),(x,y+30));draw.text((x+7,y+4),f'frame {frame}',font=font,fill=(229,226,213))
    sheet.save(O/name)
board('Dense_Onset_1823-1840.png',list(range(1823,1841)),P/'previews/motion_frames',(1280,530,1800,780),(520,250),3)
board('Expansion_and_Debris_1840-1870.png',list(range(1840,1871,2)),P/'previews/motion_frames',(1120,220,1920,780),(520,364),4)
board('MID_Only_Existing_RGBA_Lifetime.png',[1,5,9,13,17,21,25,29,37,49,61,73,85,97,109,120],P/'sequences/MID_unbloomed_960_RGBA',None,(480,270),4)
files=[P/'native/WTSC_Painted_Blast_Assets_v006.blend',P/'native/WTSC_Painted_Blast_Proof_v006.blend',P.parents[1]/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend']
(O/'inspection_manifest.json').write_text(json.dumps({'new_Blender_renders':0,'source_mutations':0,'sources':[{'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'onset_frames':list(range(1823,1841)),'expansion_frames':list(range(1840,1871,2)),'late_solo_sequence':'Existing960px unbloomed MID render isolates late smoke from later NEAR/FAR events; no new render.'},indent=2))
print('EXISTING_FRAMES_ARRANGED')
