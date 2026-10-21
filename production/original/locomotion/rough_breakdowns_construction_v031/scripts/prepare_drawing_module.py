from pathlib import Path
P=Path(__file__).resolve().parents[1]
src=(P.parent/'four_pose_volume_revision_v030/scripts/build_four_poses.py').read_text()
func=src[src.index('def mat('):src.index('for p,r in zip(D.POSES,anatomy):',src.index('def mat('))]
a=func.index('COAT=mat(');b=func.index('def v(',a)
materials=func[a:b].replace("'V030 | '","'V031 | '").replace(".031,.65)",".031,.48)")
func=func[:a]+func[b:]
func=func.replace("'V030 | '","'V031 | '")
start=func.index('    contour=');end=func.index('    draw(d,contour',start)
func=func[:start]+'''    # Round shoulder/chest transitions in the silhouette itself.
    front=quadratic(N+Vector((.031,0,.012)),N+Vector((.135,0,-.055)),R+Vector((.125,0,.020)),8)
    back=quadratic(R+Vector((-.106,0,-.048)),N+Vector((-.160,0,-.065)),N+Vector((-.035,0,.010)),8)
    contour=[N+Vector((-.035,0,.010)),*front,R+Vector((.103,0,-.055)),W+Vector((.078,0,.004)),F,H+Vector((.025,0,.043)),H+Vector((-.028,0,-.006)),B,W+Vector((-.087,0,-.021)),*back]
'''+func[end:]
old="draw(d,[W+Vector((-.050,0,.013)),W+Vector((-.009,0,-.012)),W+Vector((.044,0,-.003)),W+Vector((.012,0,.002)),W+Vector((-.025,0,.022))],SHADOW,-.029,steps=2)"
new="draw(d,[W+Vector((-.043,0,.012)),W+Vector((-.018,0,-.005)),W+Vector((.005,0,-.008))],INK,-.029,closed=False,steps=4,radius=.0011)"
assert old in func;func=func.replace(old,new)
head='''"""V030 volumes retained, rounded chest contour and partial oblique waist seam.
Native rough GP drawings, not final ink/paint.
"""
import bpy,math
from mathutils import Vector
gp=None
def initialize(data):
    global gp,COAT,WASH,SHADOW,NEAR,FAR,LEGPLANE,CUFF,SKIN,FARSKIN,INK
    gp=data
'''
head+=''.join('    '+line+'\n' for line in materials.strip().splitlines())
(P/'scripts/draw_construction.py').write_text(head+func)
print('DRAWING_MODULE_PREPARED')
