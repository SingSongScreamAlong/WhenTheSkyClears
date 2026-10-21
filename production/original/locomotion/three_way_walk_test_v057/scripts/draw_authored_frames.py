"""Author editable 2D vector drawings per frame from independently posed beats.

This is algorithmic drawing by the agent, not human hand-drawn cels and not
Blender puppet renders. Each SVG stores newly computed visible contours.
"""
import argparse,hashlib,json,math,random
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance

P=Path(__file__).resolve().parents[1];V=P/'previews';E=P/'evidence';SV=P/'native'/'B_svg_frames';PN=V/'frames_B_drawn'
SV.mkdir(parents=True,exist_ok=True);PN.mkdir(parents=True,exist_ok=True);E.mkdir(parents=True,exist_ok=True)
W,H=660,720;AA=2
INK='#251f1b';SKIN='#bd8762';SKIN_SHADE='#a67051';HAIR='#433124';HAIR_LIGHT='#76533b'
COAT='#35484a';COAT_SHADE='#27383b';COAT_LIGHT='#63716c';PANTS='#5e5b40';PANTS_DARK='#484732';BOOT='#50372a';BOOT_LIGHT='#7e5a40'
ATLAS=P.parent/'character_design_finish_v040'/'textures'/'WTSC_Boy_Painted_Parts_Atlas_v040.png'
SWATCHES=P/'native'/'B_pigment_swatches';SWATCHES.mkdir(parents=True,exist_ok=True)
swatch_boxes={'coat':(650,170,715,310),'pants':(595,730,645,930),'skin':(192,735,245,925),
              'hair':(150,115,240,220),'boot':(900,900,990,1010)}
source_atlas=Image.open(ATLAS).convert('RGB')
pigment={}
for name,box in swatch_boxes.items():
    patch=source_atlas.crop(box).resize((64,64),Image.Resampling.BICUBIC)
    path=SWATCHES/f'{name}.png';patch.save(path)
    pigment[name]=patch
pigment['coat_dark']=ImageEnhance.Brightness(pigment['coat']).enhance(.70)
pigment['pants_dark']=ImageEnhance.Brightness(pigment['pants']).enhance(.78)
pigment['skin_dark']=ImageEnhance.Brightness(pigment['skin']).enhance(.80)
pigment['boot_dark']=ImageEnhance.Brightness(pigment['boot']).enhance(.79)
for name in ('coat_dark','pants_dark','skin_dark','boot_dark'):
    pigment[name].save(SWATCHES/f'{name}.png')
color_to_pigment={COAT:'coat',COAT_SHADE:'coat_dark',PANTS:'pants',PANTS_DARK:'pants_dark',SKIN:'skin',SKIN_SHADE:'skin_dark',HAIR:'hair',BOOT:'boot', '#44332b':'boot_dark'}

def mix(a,b,t):return a+(b-a)*t
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def beat(t,values):
    t=t%32
    for i in range(len(values)-1):
        if values[i][0]<=t<=values[i+1][0]:
            a,v=values[i];b,w=values[i+1];return mix(v,w,smooth((t-a)/(b-a)))
    return values[0][1]
def ik(hip,ankle,l1=113,l2=127):
    dx=ankle[0]-hip[0];dy=ankle[1]-hip[1];d=max(1,math.hypot(dx,dy));d=min(d,l1+l2-.2)
    along=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-along*along))
    ux,uy=dx/d,dy/d;return (hip[0]+along*ux+h*uy,hip[1]+along*uy-h*ux)
def foot(u):
    # The two halves have explicit planted and swing windows. Stationary
    # world contact is interpreted in the body-following camera coordinates.
    if u<.60:return (490+62-124*u/.60,630,0.,'planted')
    v=(u-.60)/.40
    return (490-62+124*smooth(v),630-43*math.sin(math.pi*v),-8*math.sin(math.pi*v),'swing')
def pose(k):
    p=k/25.6;t=(k*1.25)%32
    bob=beat(t,[(0,0),(3,7),(8,-7),(12,-2),(16,0),(19,6),(24,-8),(28,-2),(32,0)])
    chest=beat(t,[(0,3),(3,14),(8,-7),(12,4),(16,3),(19,12),(24,-6),(28,5),(32,3)])
    hip=(490+1.4*math.sin(.37*k),401+bob)
    shoulder=(489+chest,225+.39*bob+beat(t,[(0,0),(3,4),(8,-2),(16,0),(19,4),(24,-2),(32,0)]))
    neck=(shoulder[0]+6,shoulder[1]-15);head=(neck[0]+5,neck[1]-48)
    legs={};arms={}
    for side,phase in [('near',(p+.5)%1),('far',p%1)]:
        fx,fy,pitch,state=foot(phase)
        h=(hip[0]+(-6 if side=='near' else 7),hip[1]+2)
        a=(fx+(1 if side=='near' else -1),fy)
        legs[side]={'hip':h,'knee':ik(h,a),'ankle':a,'pitch':pitch,'state':state,'phase':phase}
        sh=(shoulder[0]+(-27 if side=='near' else 23),shoulder[1]+12)
        swing=32*math.cos(2*math.pi*phase)
        el=(sh[0]+.42*swing,sh[1]+91+1.8*math.sin(.31*k))
        wr=(sh[0]+swing,sh[1]+177+2.3*math.sin(.31*k+1.4))
        arms[side]={'shoulder':sh,'elbow':el,'wrist':wr,'hand':(wr[0]+6,wr[1]+25)}
    return {'hip':hip,'shoulder':shoulder,'neck':neck,'head':head,'legs':legs,'arms':arms,'phase_source':t,'bob_px':bob,'chest_px':chest,'frame':k+1}

def ribbon(points,widths):
    # A fresh contour is built from the three landmarks each frame, with a
    # knee/elbow relief rather than transforming one rigid limb cutout.
    center=[];radii=[]
    for seg in range(len(points)-1):
        a=points[seg];b=points[seg+1]
        for j in range(10):
            t=j/10;tt=smooth(t)
            center.append((mix(a[0],b[0],tt),mix(a[1],b[1],tt)))
            radii.append(mix(widths[seg],widths[seg+1],tt))
    center.append(points[-1]);radii.append(widths[-1])
    left=[];right=[]
    for i,(x,y) in enumerate(center):
        prev=center[max(0,i-1)];nxt=center[min(len(center)-1,i+1)]
        dx=nxt[0]-prev[0];dy=nxt[1]-prev[1];length=max(1,math.hypot(dx,dy));nx=-dy/length;ny=dx/length
        left.append((x+nx*radii[i],y+ny*radii[i]));right.append((x-nx*radii[i],y-ny*radii[i]))
    return left+right[::-1]

class Cel:
    def __init__(self):
        self.im=Image.new('RGBA',(W*AA,H*AA),(0,0,0,0));self.draw=ImageDraw.Draw(self.im)
        self.svg=['<svg xmlns="http://www.w3.org/2000/svg" width="660" height="720" viewBox="0 0 660 720">']
        self.pigment_counter=0
    def polygon(self,points,fill,stroke=INK,sw=1.15):
        pt=[(int(x*AA),int(y*AA)) for x,y in points]
        pigment_name=color_to_pigment.get(fill)
        if pigment_name:
            mask=Image.new('L',self.im.size);ImageDraw.Draw(mask).polygon(pt,fill=255)
            x0=max(0,min(x for x,y in pt));y0=max(0,min(y for x,y in pt));x1=min(W*AA,max(x for x,y in pt)+1);y1=min(H*AA,max(y for x,y in pt)+1)
            if x1>x0 and y1>y0:
                patch=pigment[pigment_name].resize((x1-x0,y1-y0),Image.Resampling.BICUBIC).convert('RGBA')
                layer=Image.new('RGBA',self.im.size);layer.paste(patch,(x0,y0))
                self.im.paste(layer,(0,0),mask)
            ident=f'paint_{self.pigment_counter}';self.pigment_counter+=1
            px=x0/AA;py=y0/AA;pw=max(1,(x1-x0)/AA);ph=max(1,(y1-y0)/AA)
            self.svg.append(f'<defs><pattern id="{ident}" patternUnits="userSpaceOnUse" x="{px:.2f}" y="{py:.2f}" width="{pw:.2f}" height="{ph:.2f}"><image x="{px:.2f}" y="{py:.2f}" width="{pw:.2f}" height="{ph:.2f}" preserveAspectRatio="none" href="../B_pigment_swatches/{pigment_name}.png"/></pattern></defs>')
            svgfill=f'url(#{ident})'
        else:
            self.draw.polygon(pt,fill=fill);svgfill=fill
        if stroke:self.draw.line(pt+[pt[0]],fill=stroke,width=max(1,int(sw*AA)),joint='curve')
        d='M '+' L '.join(f'{x:.2f} {y:.2f}' for x,y in points)+' Z'
        self.svg.append(f'<path d="{d}" fill="{svgfill}" stroke="{stroke if stroke else "none"}" stroke-width="{sw:.2f}" stroke-linejoin="round"/>')
    def line(self,points,color,width=1.1,opacity=1):
        self.draw.line([(int(x*AA),int(y*AA)) for x,y in points],fill=color,width=max(1,int(width*AA)),joint='curve')
        d='M '+' L '.join(f'{x:.2f} {y:.2f}' for x,y in points)
        self.svg.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{opacity:.3f}" stroke-width="{width:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')
    def ellipse(self,box,fill,stroke=None,sw=1):
        self.draw.ellipse(tuple(int(x*AA) for x in box),fill=fill,outline=stroke,width=max(1,int(sw*AA)))
        x0,y0,x1,y1=box;self.svg.append(f'<ellipse cx="{(x0+x1)/2:.2f}" cy="{(y0+y1)/2:.2f}" rx="{(x1-x0)/2:.2f}" ry="{(y1-y0)/2:.2f}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw:.2f}"/>')
    def finish(self,png,svg,bg):
        self.svg.append('</svg>');svg.write_text('\n'.join(self.svg),encoding='utf-8')
        art=self.im.resize((W,H),Image.Resampling.LANCZOS)
        image=bg.copy().convert('RGBA');image.alpha_composite(art);image.convert('RGB').save(png)

def boot(c,leg,front=True):
    x,y=leg['ankle'];p=leg['pitch'];shade=BOOT if front else '#44332b'
    heel=(x-17,y+35+p*.25);toe=(x+48,y+34+p);top=(x+8,y+7)
    c.polygon([(x-16,y-6),(x+10,y-7),top,(x+14,y+18),(x+39,y+22+p*.8),toe,(x+49,y+42+p),
               (x+12,y+43+p*.3),heel,(x-18,y+24)],shade)
    c.line([(x-14,y+34+p*.2),(x+13,y+40+p*.3),(x+48,y+38+p)],'#251b18',2.4)
    c.line([(x+1,y+11),(x+12,y+12),(x+25,y+20)],BOOT_LIGHT,1.6)
    for i in range(3):c.line([(x+5+i*5,y+15+i*2),(x+11+i*5,y+12+i*2)],'#261d18',1.2)

def draw_cel(data):
    c=Cel();hip=data['hip'];sh=data['shoulder'];hd=data['head'];f=data['frame'];rng=random.Random(5750+f)
    # Far side first; pant curves are redrawn from hip/knee/ankle.
    leg=data['legs']['far'];c.polygon(ribbon([leg['hip'],leg['knee'],leg['ankle']],[18,16,12]),PANTS_DARK);boot(c,leg,False)
    arm=data['arms']['far'];c.polygon(ribbon([arm['shoulder'],arm['elbow']],[23,16]),COAT_SHADE)
    c.polygon(ribbon([arm['elbow'],arm['wrist']],[12,9]),SKIN_SHADE);c.ellipse((arm['wrist'][0]-8,arm['wrist'][1]-2,arm['wrist'][0]+7,arm['wrist'][1]+31),SKIN_SHADE)
    # Near trousers, fold direction and ankle collars change with the pose.
    leg=data['legs']['near'];c.polygon(ribbon([leg['hip'],leg['knee'],leg['ankle']],[20,18,12]),PANTS)
    knee=leg['knee'];c.line([(knee[0]-8,knee[1]-5),(knee[0]+3,knee[1]+3),(knee[0]+11,knee[1]+11)],'#827b54',2.)
    c.line([(leg['ankle'][0]-10,leg['ankle'][1]-14),(leg['ankle'][0]+8,leg['ankle'][1]-12)],'#958e69',3)
    boot(c,leg,True)
    # Distinct chest and pelvis controls define a deforming coat silhouette.
    sx,sy=sh;hx,hy=hip;back=(sx-34,sy+6);front=(sx+35,sy+5)
    hem_shift=3*math.sin(f*.34)+2*math.sin(f*.13+1)
    coat=[back,(sx-45,sy+48),(hx-43,hy-25),(hx-50,hy+16+hem_shift),(hx-12,hy+18+hem_shift),
          (hx+32,hy+17-hem_shift*.6),(hx+33,hy-12),(front[0]-2,front[1]+82),front,(sx+8,sy-7)]
    c.polygon(coat,COAT)
    c.polygon([(sx+9,sy-7),(front[0],front[1]),(front[0]-2,front[1]+82),(hx+25,hy+11),(hx+3,hy+18),(sx+1,sy+45)],COAT_SHADE,None)
    c.line([(sx+4,sy+5),(sx+11,sy+71),(hx+6,hy+8)],COAT_LIGHT,1.55)
    c.line([(back[0]+6,back[1]+24),(hx-43,hy-33),(hx-36,hy+7)],'#6b7771',1.35)
    c.polygon([(sx-9,sy-7),(sx+17,sy-8),(sx+12,sy+15),(sx+3,sy+26),(sx-4,sy+14)],'#8b978a')
    for i in range(3):
        by=sy+57+i*44+1.2*math.sin(f*.21+i)
        c.ellipse((sx+24,by,sx+29,by+5),'#a18459','#3b362c',.6)
    pocket=(hx-12,hy-35);c.polygon([(pocket[0]-7,pocket[1]-4),(pocket[0]+14,pocket[1]-3),(pocket[0]+11,pocket[1]+15),(pocket[0]-9,pocket[1]+11)],COAT_SHADE)
    c.line([(pocket[0]-6,pocket[1]-2),(pocket[0]+14,pocket[1]-1)],'#88948a',1.2)
    for i in range(8):
        y=sy+37+i*21;x=mix(sx-31,hx-38,i/8)+2*math.sin(i*4.1+f*.19)
        c.line([(x,y),(x+5+rng.random()*4,y+9+rng.random()*7)],'#52615d',.8)
    # Neck/profile are fresh vector outlines, with no edge-on head card.
    nx,ny=data['neck'];c.polygon([(nx-14,ny-1),(nx+10,ny-4),(nx+9,ny+23),(nx-12,ny+25)],SKIN_SHADE)
    x,y=hd
    face=[(x-36,y-23),(x-27,y-39),(x+6,y-41),(x+29,y-26),(x+39,y-11),(x+43,y+3),
          (x+49,y+11),(x+39,y+16),(x+41,y+27),(x+31,y+35),(x+7,y+40),(x-21,y+28),(x-34,y+8)]
    c.polygon(face,SKIN)
    c.ellipse((x-23,y-6,x-3,y+17),SKIN_SHADE,'#604437',1.)
    c.line([(x+22,y-8),(x+34,y-10)],'#422e26',1.9)
    c.ellipse((x+30,y-9,x+34,y-5),'#262522')
    c.line([(x+36,y+23),(x+41,y+24)],'#85503f',1.1)
    # Hair masses and little ink tufts use temporally coherent fresh paths.
    breeze=2.2*math.sin(f*.17)+.8*math.sin(f*.41)
    hair=[(x-39,y+13),(x-45,y-17),(x-41,y-35),(x-34,y-46),(x-24,y-55),(x-10,y-54),
          (x-4,y-62+breeze),(x+8,y-55),(x+20,y-58+breeze),(x+28,y-49),(x+35,y-41),
          (x+42,y-43+breeze),(x+34,y-31),(x+26,y-20),(x+20,y-29),(x+6,y-32),
          (x-8,y-25),(x-21,y-14),(x-28,y+5),(x-30,y+20)]
    c.polygon(hair,HAIR)
    for i in range(10):
        xx=x-34+i*6.1;yy=y-44+5*math.sin(i*.91+f*.073)
        c.line([(xx,yy),(xx+5,yy-7+1.5*math.sin(f*.11+i)),(xx+13,yy-8)],HAIR_LIGHT,1.0 if i%3 else 1.5)
    # Near arm overlaps coat at the true drawn shoulder insertion.
    arm=data['arms']['near'];a=arm['shoulder'];e=arm['elbow'];w=arm['wrist']
    c.polygon(ribbon([a,(mix(a[0],e[0],.48)-3,mix(a[1],e[1],.48)),e],[22,20,16]),COAT)
    c.line([(a[0]-7,a[1]+8),(e[0]-9,e[1]-19)],'#53625e',1.7)
    c.polygon(ribbon([e,w],[12,9]),SKIN)
    c.polygon([(e[0]-15,e[1]-8),(e[0]+17,e[1]-8),(e[0]+14,e[1]+5),(e[0]-12,e[1]+5)],'#aaa489')
    c.ellipse((w[0]-10,w[1]-4,w[0]+9,w[1]+29),SKIN)
    for i in range(3):
        xx=w[0]-3+i*4;c.line([(xx,w[1]+18),(xx+2,w[1]+31)],'#8b5b43',.75)
    return c

def background():
    path=V/'WTSC_Comparison_Studio_Background.png'
    if path.exists():return Image.open(path).convert('RGB')
    source=P.parent/'authored_walk_beats_v053'/'previews'/'frames_V053'/'FRAME_0001.png'
    raw=Image.open(source).convert('RGB');bg=Image.new('RGB',(W,H))
    d=ImageDraw.Draw(bg)
    for y in range(H):
        color=raw.getpixel((200,y));d.line((0,y,W,y),fill=color,width=1)
    # The original studio's fine field ticks are retained in every lane.
    for x in (9,167,325,482,639):
        d.line((x,664,x,686),fill='#a9aaa3',width=1)
    d.line((0,674,W,674),fill='#999d96',width=1)
    bg.save(path);return bg

def main(pilot):
    bg=background();indices=[0,4,8,12,16,20,24,28] if pilot else list(range(120));rows=[]
    for k in indices:
        p=pose(k);cel=draw_cel(p)
        png=PN/f'FRAME_{k+1:04d}.png';svg=SV/f'FRAME_{k+1:04d}.svg';cel.finish(png,svg,bg)
        rows.append({'frame':k+1,'time_s':k/24,'svg':str(svg),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),
                     'png':str(png),'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),
                     'pose':p})
    name='B_PILOT_DRAWINGS.json' if pilot else 'B_ALL_DRAWINGS.json'
    (E/name).write_text(json.dumps({'method':'Agent-authored algorithmic per-frame SVG contours, not human drawn, no puppet renders',
                                   'fps':24,'total_intended_frames':120,'completed':len(rows),'no_literal_frame_reuse':len({r['svg_sha256'] for r in rows})==len(rows),
                                   'design':'Original boy profile, age-ten scale, coat/pants/boots/skin/hair palette approximated by vector drawing',
                                   'records':rows},indent=2))
    print('V057_B_DRAWINGS',name,len(rows),'all_svg_unique',len({r['svg_sha256'] for r in rows})==len(rows))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args();main(args.pilot)
