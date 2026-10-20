"""Bounded CPU check of the same authored point functions, no Blender render."""
import ast,math,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
tree=ast.parse((P/'scripts/build_coherent.py').read_text());names={'curve','wrap','mass_state','mass_fn','topology'};constants={'TIMES','LEFT','RIGHT','CORE','N','RINGS'}
nodes=[node for node in tree.body if (isinstance(node,ast.FunctionDef) and node.name in names) or (isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in constants for t in node.targets))]
scope={'math':math};exec(compile(ast.Module(body=nodes,type_ignores=[]),'owned_motion_functions','exec'),scope)
report={}
for name,spec,side,seed in [('LEFT',scope['LEFT'],1,.4),('RIGHT',scope['RIGHT'],-1,2.1),('CORE',scope['CORE'],1,4.)]:
    fn=scope['mass_fn'](spec,side,seed);samples=[];negative=0
    previous=None;early=[];late=[]
    for age in range(133):
        points=fn(age,64,5);cx,cz=points[0];ring=points[-64:]
        for i,(x,z) in enumerate(ring):
            xx,zz=ring[(i+1)%64];area=(x-cx)*(zz-cz)-(xx-cx)*(z-cz)
            negative+=area<-.000001
        if previous:
            speed=math.dist(points[0],previous[0]);(early if age<=5 else late if 24<=age<=60 else []).append(speed)
        if age in [0,1,2,3,5,8,12,18,24,32,44,60,84,114]:samples.append({'age':age,'centroid':points[0],'top':max(p[1] for p in points),'floor':min(p[1] for p in points)})
        previous=points
    report[name]={'samples':samples,'negative_outer_fan_sectors':negative,'early_max_centroid_m_per_frame':max(early),'late_max_centroid_m_per_frame':max(late),'points_per_frame':len(points)}
(P/'evidence/geometry_motion_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({n:{k:v for k,v in r.items() if k!='samples'} for n,r in report.items()},indent=2))
