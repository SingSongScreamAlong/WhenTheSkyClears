"""Analysis crops only; original raster art and native sources are untouched."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

R=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
frames=[1801,1834,1840,1846,1881,1901,1918]
select='+'.join(f'eq(n\\,{f-1801})' for f in frames)
args=[F,'-hide_banner','-nostdin','-v','error','-i',str(R/'renders/refinement_v047g/WTSC_Refinement_v047g_75_80_4K.mp4'),'-vf','select='+select,'-fps_mode','vfr','-frames:v',str(len(frames)),'-threads','2','-n',str(D/'v047g_baseline_%02d.png')]
if not (D/'v047g_baseline_07.png').exists():
    run=subprocess.run(args,capture_output=True,text=True)
    assert run.returncode==0,run.stderr
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',22)
for j,f in enumerate(frames):
    old=Image.open(D/f'v047g_baseline_{j+1:02d}.png').convert('RGB')
    new=Image.open(R/f'renders/refinement_v048a/Full_{f}_4K.png').convert('RGB')
    assert old.size==new.size==(3840,2160)
    # 1440x1200 native-pixel crop, displayed at exactly one pixel per source pixel.
    box=(1400,480,2840,1680)
    sheet=Image.new('RGB',(2890,1240),(18,18,18));draw=ImageDraw.Draw(sheet)
    draw.text((4,6),f'v047g before | {f} | decoded actual4K, native pixel crop',fill='white',font=font)
    draw.text((1450,6),f'v048a after | {f} | native4K render, native pixel crop',fill='white',font=font)
    sheet.paste(old.crop(box),(0,40));sheet.paste(new.crop(box),(1450,40))
    sheet.save(D/f'Actor_Before_After_{f}_NativePixels.jpg',quality=97)
    # Restrict to head/shoulder for a compact exact-pixel comparison.
    box=(1670,690,2450,1240)
    head=Image.new('RGB',(1570,590),(18,18,18));draw=ImageDraw.Draw(head)
    draw.text((4,6),f'v047g before | {f} | native pixels',fill='white',font=font)
    draw.text((790,6),f'v048a after | {f} | native pixels',fill='white',font=font)
    head.paste(old.crop(box),(0,40));head.paste(new.crop(box),(790,40))
    head.save(D/f'Head_Shoulder_Before_After_{f}_NativePixels.jpg',quality=97)
print('V048A_COMPARISONS_READY',D)
