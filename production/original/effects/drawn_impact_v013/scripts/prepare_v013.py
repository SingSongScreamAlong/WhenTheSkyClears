from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];prior=P.parent/'drawn_impact_v012'
for f in ['scripts','native','previews','evidence']:(P/f).mkdir(parents=True,exist_ok=True)
(P/'evidence/visible_terrain_profile.json').write_bytes((prior/'evidence/visible_terrain_profile.json').read_bytes())
for name in ['build_drawn.py','finish_paint.py','render_drawn.py','key_sheet.py','finish_media.py','append_test.py','append_render.py','render_rgba.py','verify_rgba.py']:
    t=(prior/'scripts'/name).read_text().replace('v012','v013')
    if name=='build_drawn.py':
        old="pts=[(x,z+(ground_z(x) if terrain else 0)) for x,z in points];cx=sum(x for x,z in pts)/len(pts);cz=sum(z for x,z in pts)/len(pts);inner=[(cx+(x-cx)*.965,cz+(z-cz)*.965) for x,z in pts];"
        new="""soft=name.startswith('A') or name.startswith('landing')
    if soft:
        # Two corner-cut passes round the authored contours; every exposure
        # still has its own distinct mesh and outward shape change.
        for _ in range(2):
            smooth=[]
            for j,p in enumerate(points):
                q=points[(j+1)%len(points)]
                smooth += [(.78*p[0]+.22*q[0],.78*p[1]+.22*q[1]),(.22*p[0]+.78*q[0],.22*p[1]+.78*q[1])]
            points=smooth
    feather=.86 if name.startswith('landing') else (.90 if soft else .965)
    pts=[(x,z+(ground_z(x) if terrain else 0)) for x,z in points];cx=sum(x for x,z in pts)/len(pts);cz=sum(z for x,z in pts)/len(pts);inner=[(cx+(x-cx)*feather,cz+(z-cz)*feather) for x,z in pts];"""
        assert old in t;t=t.replace(old,new)
        old="o=poly(f'varied coherent chip{i:02d}',shape,M['chip']"
        new="""shape=[(.125*shape[(j-1)%n][0]+.75*p[0]+.125*shape[(j+1)%n][0],.125*shape[(j-1)%n][1]+.75*p[1]+.125*shape[(j+1)%n][1]) for j,p in enumerate(shape)]
    o=poly(f'varied coherent chip{i:02d}',shape,M['chip']"""
        assert old in t;t=t.replace(old,new)
        changes={"(.68,.29,.065),.95,.45":"(.48,.26,.08),.95,.35","(.94,.73,.33),1,.28":"(.72,.55,.27),1,.25","(.15,.15,.13),.34,.7":"(.27,.25,.20),.60,.30","(.14,.145,.13),.15,.7":"(.18,.17,.14),.23,.40"}
        for a,b in changes.items():assert a in t;t=t.replace(a,b)
        # Pigment grain changes opacity as well as color, without making the
        # packed mature painting define any temporal silhouette.
        old="tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix="
        new="""noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=105;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.7;nt.links.new(uv.outputs['UV'],noise.inputs['Vector']);rng=nt.nodes.new('ShaderNodeMapRange');rng.clamp=True;rng.inputs['From Min'].default_value=.27;rng.inputs['From Max'].default_value=.72;rng.inputs['To Min'].default_value=.50;rng.inputs['To Max'].default_value=1;nt.links.new(noise.outputs['Fac'],rng.inputs['Value']);grainmode=nt.nodes.new('ShaderNodeMixRGB');grainmode.inputs[1].default_value=(1,1,1,1);drive(grainmode.inputs[0],'default_value','P');nt.links.new(rng.outputs[0],grainmode.inputs[2]);pigmentalpha=nt.nodes.new('ShaderNodeMath');pigmentalpha.operation='MULTIPLY';nt.links.new(alpha.outputs[0],pigmentalpha.inputs[0]);nt.links.new(grainmode.outputs[0],pigmentalpha.inputs[1]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix="""
        assert old in t;t=t.replace(old,new)
        old="nt.links.new(alpha.outputs[0],mix.inputs[0])";assert old in t;t=t.replace(old,"nt.links.new(pigmentalpha.outputs[0],mix.inputs[0])")
        t=t.replace("'status':'Plain keys require", "'refinement':'Rounded distinct contours, softened pigment edges, less saturated initial heat, higher contrast brief landing cues; no additional smoke volume.','status':'Plain keys require")
    if name=='build_drawn.py':
        t=t.replace("def puffs(name,points,mat,lo,hi):poly(name,[(lx+x,floor+z) for x,z in points],mat,lo,hi,y=-.16)", "def puffs(name,points,mat,lo,hi):\n            if 'B split' in name or 'C torn' in name:points=[(x*1.15,z*1.65) for x,z in points]\n            poly(name,[(lx+x,floor+z) for x,z in points],mat,lo,hi,y=-.16)")
        t=t.replace('M[\'contact\'],land_age+1,land_age+3)', 'M[\'contact\'],land_age+1,land_age+4)')
        t=t.replace('M[\'contactlate\'],land_age+3,land_age+5)', 'M[\'contactlate\'],land_age+4,land_age+6)')
        t=t.replace('(.27,.25,.20),.60,.30','(.27,.25,.20),.68,.30').replace('(.18,.17,.14),.23,.40','(.18,.17,.14),.25,.40')
    t=t.replace("rng.inputs['To Min'].default_value=.50", "rng.inputs['To Min'].default_value=1 if any(term in name for term in ['chips','soil nicks','contact shadow']) else .50")
    t=t.replace("if f.exists() and f.read_bytes()", "if '--force' not in __import__('sys').argv and f.exists() and f.read_bytes()")
    if name=='render_drawn.py':
        t=t.replace("mode='motion' if '--motion' in sys.argv else 'keys'", "mode='contact' if '--contact' in sys.argv else ('motion' if '--motion' in sys.argv else 'keys')")
        t=t.replace("frames=list(range(1,73)) if mode=='motion' else list(range(6,16))+[18,22,26,30,36,72]", "frames=[16,17,18,19,20,21,22,23,24,25,26,27,31,32,33,34] if mode=='contact' else (list(range(1,73)) if mode=='motion' else list(range(6,16))+[18,22,26,30,36,72])")
    if name=='render_rgba.py':t=t.replace('s.compositing_node_group=None;s.render.film_transparent=True','s.compositing_node_group=None;s.render.film_transparent=True;s.render.dither_intensity=0')
    if name=='append_render.py':t=t.replace('dither=source.render.dither_intensity','dither=0 # Same export setting as the reusable RGBA plate.')
    t=t.replace('Original pigment is color-only finishing.','Pigment finish modulates color and local opacity grain; separate native contours define the silhouettes.')
    t=t.replace('Original pigment changes color only.','Original pigment changes color and local opacity grain only.')
    (P/'scripts'/name).write_text(t)
(P/'evidence/construction_decision.txt').write_text('Same isolated compact impact refinement following v012. Reuse: installed verified Blender5.2.2, original project-owned v003 packed pigment, held camera/plate/masks, measured alpha terrain and v012 native construction. No third-party asset or installation. Rights and native compatibility already established in preceding checkpoint. Remaining gap is visual: angular onset and faint contact cues. Two contour rounding passes, wider feather and local pigment opacity grain; brief contact contrast adjusted. Timing, seven debris specifications and low smoke scope retained. All writes under effects/drawn_impact_v013. No production integration, source modification or shared UI control. Tutorial motion remains unverified.\n')
print('V013_SCRIPTS_PREPARED')
