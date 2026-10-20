"""Draw three quiet ink-and-wash bodice treatments in the existing charcoal palette.

The drawings register to a new UV layer on the v053 dress. They do not modify
the original pair image or its pigment UVs. A full cycle is only attempted if
these distinct loading/passing/push-off drawings read in actual Blender keys.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

P = Path(__file__).resolve().parents[1]
O = P / 'textures'
O.mkdir(parents=True, exist_ok=True)
N = 768
rng = np.random.default_rng(55019)
noise = rng.normal(0, 1, (N,N)).astype(np.float32)
noise_img = Image.fromarray(np.uint8(np.clip(128+31*noise,0,255)), 'L').filter(ImageFilter.GaussianBlur(1.1))
grain = (np.asarray(noise_img, dtype=np.float32)-128)/32

def curve(p0,p1,p2,p3,count=80):
    u=np.linspace(0,1,count)
    return [((1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3))*N for t in u]

def paint_stroke(canvas, control, color, width, alpha, blur, seed):
    points=curve(*control)
    mask=Image.new('L',(N,N));d=ImageDraw.Draw(mask)
    local=np.random.default_rng(seed)
    jitter=local.normal(0, .8, (len(points),2))
    line=[tuple(map(float,p+j)) for p,j in zip(points,jitter)]
    d.line(line, fill=255, width=width, joint='curve')
    for end in (line[0],line[-1]):d.ellipse((end[0]-width/2,end[1]-width/2,end[0]+width/2,end[1]+width/2),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(mask,dtype=np.float32)/255
    # Uneven graphite pigment, but broad enough to survive the shot-size reduction.
    a=np.clip(a*(alpha/255)*(1+.24*grain),0,1)
    shade=np.empty((N,N,4),dtype=np.uint8)
    shade[:,:,:3]=color
    shade[:,:,3]=(255*a).astype(np.uint8)
    canvas.alpha_composite(Image.fromarray(shade,'RGBA'))

# Coordinates are s=rear-to-front and t=collar-to-hem, copied from the dress
# mesh grid. Each phase changes fabric *direction*, not just brightness.
designs={
 'loading':[
  (((.40,.105),(.50,.12),(.59,.19),(.67,.225)),(6,7,8),41,82,12),
  (((.47,.10),(.55,.13),(.61,.20),(.70,.245)),(92,88,79),17,111,5),
  (((.42,.30),(.52,.34),(.56,.415),(.66,.455)),(6,7,8),46,79,13),
  (((.40,.29),(.47,.34),(.52,.39),(.60,.43)),(96,91,81),15,93,6),
  (((.57,.17),(.62,.23),(.63,.29),(.69,.33)),(75,72,65),8,70,4),
 ],
 'passing':[
  (((.32,.12),(.45,.105),(.60,.125),(.73,.17)),(86,83,75),17,104,7),
  (((.38,.15),(.51,.16),(.63,.21),(.72,.255)),(5,7,9),37,61,13),
  (((.53,.25),(.56,.31),(.58,.38),(.59,.445)),(79,76,68),15,76,7),
  (((.60,.29),(.65,.35),(.70,.39),(.73,.43)),(8,9,10),31,55,11),
 ],
 'push':[
  (((.30,.13),(.41,.11),(.54,.115),(.67,.16)),(91,87,79),19,104,7),
  (((.42,.16),(.52,.19),(.62,.22),(.72,.28)),(5,7,9),39,71,13),
  (((.39,.27),(.48,.32),(.55,.36),(.67,.44)),(84,80,72),18,80,6),
  (((.47,.33),(.57,.37),(.65,.41),(.75,.45)),(7,8,9),31,52,12),
 ],
}
records=[]
for phase,strokes in designs.items():
    canvas=Image.new('RGBA',(N,N))
    for index,(control,color,width,alpha,blur) in enumerate(strokes):
        # The body is only about 40 pixels wide in the actual 720p shot.
        # These marks need a several-pixel wash, not subpixel pinstripes.
        paint_stroke(canvas,control,color,round(width*1.8),min(220,round(alpha*1.5)),blur*1.25,5500+index)
    path=O/f'WTSC_Girl_Bodice_{phase}_v055.png'
    canvas.save(path)
    records.append({'phase':phase,'path':str(path),'size':path.stat().st_size})
(P/'evidence').mkdir(exist_ok=True)
(P/'evidence'/'PAINT_DESIGN.json').write_text(json.dumps({'source':'Existing original charcoal textile palette; new controlled gesture marks','uv':'s rear-to-front, t collar-to-hem','image_size':[N,N],'records':records},indent=2))
print('V055_PAINT_IMAGES_CREATED',records)
