"""V030 volumes retained, rounded chest contour and partial oblique waist seam.
Native rough GP drawings, not final ink/paint.
"""
import bpy,math
from mathutils import Vector
gp=None
def initialize(data):
    global gp,COAT,WASH,SHADOW,NEAR,FAR,LEGPLANE,CUFF,SKIN,FARSKIN,INK
    gp=data
    COAT=mat('charcoal coat',(.014,.015,.014,1));WASH=mat('coat volume wash',(.032,.034,.031,.48));SHADOW=mat('fold ink',(.004,.005,.005,.72));NEAR=mat('near trouser charcoal',(.019,.021,.019,1));FAR=mat('far trouser wash',(.036,.039,.035,1));LEGPLANE=mat('trouser plane',(.027,.029,.026,.55));CUFF=mat('restrained gray cuff',(.057,.060,.054,1));SKIN=mat('foreground charcoal skin plane',(.026,.028,.026,1));FARSKIN=mat('far charcoal skin',(.028,.031,.027,1));INK=mat('drawn seam',(.006,.008,.006,.75),False,True)
def mat(name,color,fill=True,stroke=False):
    m=bpy.data.materials.new('V032 | '+name);bpy.data.materials.create_gpencil_data(m);g=m.grease_pencil;g.show_fill=fill;g.show_stroke=stroke;g.fill_color=color;g.color=color;gp.materials.append(m);return len(gp.materials)-1
def v(xz,y=0):return Vector((xz[0],y,xz[1]))
def unit(a,b):return (b-a).normalized()
def normal(u):return Vector((-u.z,0,u.x))
def quadratic(A,B,C,steps=7):return [(1-t)*(1-t)*A+2*(1-t)*t*B+t*t*C for t in [i/(steps-1) for i in range(steps)]]
def catmull(V,steps=3,closed=True):
    n=len(V);out=[]
    for i in range(n if closed else n-1):
        a=V[(i-1)%n] if closed or i else V[0];b=V[i];c=V[(i+1)%n];d=V[(i+2)%n] if closed or i+2<n else V[-1]
        for j in range(steps):
            t=j/steps;out.append((b*2+(-a+c)*t+(a*2-b*5+c*4-d)*t*t+(-a+b*3-c*3+d)*t*t*t)*.5)
    if not closed:out.append(V[-1])
    return out
def draw(d,points,mi,y,closed=True,steps=3,radius=.0008):
    V=[v(p,y) if not isinstance(p,Vector) else Vector((p.x,y,p.z)) for p in points];V=catmull(V,steps,closed);d.add_strokes([len(V)]);s=d.strokes[-1];s.cyclic=closed;s.material_index=mi;s.fill_id=len(d.strokes) if closed else 0;s.fill_opacity=1.;s.fill_color=(0,0,0,0);s.softness=.25
    for point,co in zip(s.points,V):point.position=co;point.radius=radius;point.opacity=1
def leg(d,p,r,side):
    L=r['legs'][side];H=v(L['hip']);K=v(L['knee']);A=v(L['ankle']);u=unit(H,K);w=unit(K,A);Nu=normal(u);Nv=normal(w);Nm=(Nu+Nv).normalized();width=1 if side=='near' else .92;y=-.018 if side=='near' else .012
    # Separate thigh mass, front patella, calf and tapered shin. No shared S-curve ribbon.
    # Rounded front knee cap and soft rear fold, between separate thigh/shin masses.
    front=quadratic(K-u*.055+Nu*.034*width,K+Nm*.043*width,K+w*.060+Nv*.034*width)
    back=quadratic(K+w*.075-Nv*.039*width,K-Nm*.022*width,K-u*.070-Nu*.038*width)
    V=[H+Nu*.052*width,H.lerp(K,.52)+Nu*.048*width,*front,K.lerp(A,.64)+Nv*.030*width,A-w*.004+Nv*.024*width,A-w*.004-Nv*.024*width,K.lerp(A,.47)-Nv*.034*width,*back,H.lerp(K,.70)-Nu*.039*width,H-Nu*.052*width]
    draw(d,V,NEAR if side=='near' else FAR,y,steps=4)
    draw(d,[H+Nu*.013,H.lerp(K,.60)+Nu*.020,K-u*.029+Nu*.012,K-u*.008-Nm*.004,H.lerp(K,.45)-Nu*.015],LEGPLANE,y-.0005)
    draw(d,[K+w*.052+Nv*.008,K.lerp(A,.75)+Nv*.012,A-w*.021-Nv*.006,K+w*.065-Nv*.009],LEGPLANE,y-.0007)
    # Narrow integrated cuff, not a large rectangular gray boot-collar block.
    C=A-w*.013;draw(d,[C-w*.018+Nv*.028*width,C-w*.018-Nv*.028*width,C+w*.007-Nv*.027*width,C+w*.007+Nv*.027*width],CUFF,y-.001,steps=3)
    draw(d,[K-Nm*.018-u*.008,K-Nm*.011+w*.014,K+w*.026-Nv*.020],INK,y-.0015,closed=False,steps=2,radius=.0011)
def arm(d,p,side):
    N=v(p['neck']);S0=N+Vector((p[side+'_shoulder_x'],0,-.078));aa,bb,hh=[math.radians(a) for a in p[side+'_arm']];u=Vector((math.sin(aa),0,-math.cos(aa)));w=Vector((math.sin(bb),0,-math.cos(bb)));h=Vector((math.sin(hh),0,-math.cos(hh)));E=S0+u*.198;W=E+w*.178;C=E.lerp(W,.30);Nu=normal(u);Nw=normal(w);Nh=normal(h);y=-.045 if side=='near' else .026
    draw(d,[C+Nw*.016,W+Nw*.011,W-Nw*.011,C-Nw*.016],SKIN if side=='near' else FARSKIN,y-.001)
    draw(d,[S0+Nu*.043,S0.lerp(E,.60)+Nu*.038,E+Nu*.030,C+Nw*.023,C-Nw*.023,E-Nu*.029,S0.lerp(E,.4)-Nu*.038,S0-Nu*.043],COAT,y,steps=4)
    draw(d,[C-w*.014+Nw*.024,C-w*.014-Nw*.024,C+w*.004-Nw*.023,C+w*.004+Nw*.023],CUFF,y-.002,steps=2)
    hand=[W-Nh*.011,W+h*.024-Nh*.017,W+h*.050-Nh*.015,W+h*.062-Nh*.007,W+h*.060+Nh*.001,W+h*.053+Nh*.004,W+h*.058+Nh*.009,W+h*.051+Nh*.014,W+h*.032+Nh*.014,W+h*.025+Nh*.025,W+h*.014+Nh*.024,W+h*.020+Nh*.009,W+Nh*.011]
    draw(d,hand,SKIN if side=='near' else FARSKIN,y-.003,steps=2)
    draw(d,[S0+Nu*.014,E+Nu*.010,C+Nw*.009,C-Nw*.006,E-Nu*.011,S0-Nu*.008],WASH,y-.0007)
def torso(d,p):
    H=v(p['hip']);N=v(p['neck']);W=v(p['waist']);R=v(p['rib']);F=v(p['hem_front']);B=v(p['hem_back'])
    draw(d,[H+Vector((-.077,0,.068)),H+Vector((.069,0,.077)),H+Vector((.083,0,.027)),H+Vector((.070,0,-.022)),H+Vector((.022,0,-.057)),H+Vector((-.070,0,-.026))],NEAR,-.023,steps=5)
    # Round shoulder/chest transitions in the silhouette itself.
    front=quadratic(N+Vector((.031,0,.012)),N+Vector((.135,0,-.055)),R+Vector((.125,0,.020)),8)
    back=quadratic(R+Vector((-.106,0,-.048)),N+Vector((-.160,0,-.065)),N+Vector((-.035,0,.010)),8)
    contour=[N+Vector((-.035,0,.010)),*front,R+Vector((.103,0,-.055)),W+Vector((.078,0,.004)),F,H+Vector((.025,0,.043)),H+Vector((-.028,0,-.006)),B,W+Vector((-.087,0,-.021)),*back]
    draw(d,contour,COAT,-.026,steps=4)
    draw(d,[N+Vector((-.085,0,-.075)),R+Vector((-.055,0,.055)),W+Vector((-.045,0,.009)),H+Vector((-.038,0,.023)),B,W+Vector((-.080,0,-.015)),R+Vector((-.093,0,-.047))],SHADOW,-.027)
    draw(d,[N+Vector((.055,0,-.075)),R+Vector((.091,0,.055)),R+Vector((.071,0,-.049)),W+Vector((.047,0,-.002)),F+Vector((-.018,0,.012)),H+Vector((.038,0,.059)),W+Vector((.018,0,.018)),R+Vector((.039,0,.015))],WASH,-.028)
    # Visible trouser/pelvis bridge in the front hem opening.
    draw(d,[H+Vector((.026,0,.043)),H+Vector((.078,0,.038)),H+Vector((.068,0,-.012)),H+Vector((.025,0,-.032))],LEGPLANE,-.024,steps=4)
    # Waist fold follows each whole-pose bend, rather than ornamenting a fixed panel.
    draw(d,[W+Vector((-.043,0,.012)),W+Vector((-.018,0,-.005)),W+Vector((.005,0,-.008))],INK,-.029,closed=False,steps=4,radius=.0011)
    draw(d,[N+Vector((.027,0,-.082)),R+Vector((.034,0,.039)),W+Vector((.024,0,.015)),F+Vector((-.027,0,.009))],INK,-.030,closed=False,steps=3,radius=.0012)
