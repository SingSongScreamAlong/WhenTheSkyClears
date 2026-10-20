from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
source=R/'locomotion/battlefield_corrections_v006/scripts/build_drawn_corrections.py';s=source.read_text()
s=s.replace('v006','v007').replace('V006','V007')
s=s.replace("from mathutils import Vector,Matrix","from mathutils import Vector,Matrix\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent))\nimport acting_v007")
a=s.index('for who,rig in rigs.items():\n    for t in list(rig.animation_data.nla_tracks)');b=s.index('for t in list(distance.animation_data.nla_tracks)',a)
s=s[:a]+"acting_v007.author(globals())\n"+s[b:]
a=s.index('for who,rig in rigs.items():\n    cx=636',s.index('src=json.loads'));b=s.index('N=32;faces=',a)
s=s[:a]+"boot_report,boot_openings=acting_v007.boots(globals())\n\n"+s[b:]
s=s.replace("for name in ['pelvis','thigh_near','thigh_far','shin_near','shin_far','foot_near','foot_far']:","for name in ['foot_near','foot_far']:")
s=s.replace("'protected_lower_body_matrix_max_error'","'protected_foot_matrix_max_error'")
s=s.replace("S.frame_set(1);out=P/'native/WTSC_Battlefield_Drawn_Corrections_v007.blend'", "glance_report=acting_v007.glance(globals())\n(P/'evidence/glance_method.json').write_text(json.dumps(glance_report,indent=2))\nS.render.engine='BLENDER_EEVEE'\nS.frame_set(1);out=P/'native/WTSC_Supported_Recovery_v007.blend'")
s=s.replace("env=smooth(76,87,f);breathe.value", "env=smooth(110,120,f);breathe.value")
# Pose-specific compression, retaining rest widths outside the catch/recovery.
s=s.replace("crease=max(0,min(1,(angle-.65)/1.7))", "width*=1-(.20 if who=='BOY' and side=='near' else .10)*smooth(28,36,f)*(1-smooth(64,72,f))\n                crease=max(0,min(1,(angle-.65)/1.7))")
s=s.replace("t=f-(2 if side=='far' else 0)-(1 if who=='GIRL' else 0);opening=", "t=f-(2 if side=='far' else 0)-(1 if who=='GIRL' else 0);opening=")
needle="            points,hf=hand_drawing(curl,opening,f/11);byframe[f]=[BM@p for p in points]"
replacement="""            if who=='BOY' and side=='near':
                brace=smooth(38,49,f)*(1-smooth(101,115,f));curl=curl*(1-brace)+.12*brace;opening=max(opening,.55*brace)
            if (who=='BOY' and side=='far') or (who=='GIRL' and side=='near'):
                help=smooth(79 if who=='BOY' else 51,101 if who=='BOY' else 78,f);curl=curl*(1-help)+.35*help;opening=opening*(1-help)+.18*help
            points,hf=hand_drawing(curl,opening,f/11);byframe[f]=[BM@p for p in points]"""
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("'DRAWN BENDS + ARTICULATED HANDS + LIVING SETTLE /75-80s /24FPS'", "'STAGGERED SUPPORT / GIRL CHECKS BOY / SUPPORTED RISE /75-80s /24FPS'")
s=s.replace("S.name='V007 | authored bend hands living recovery'", "S.name='V007 | supported recovery and distinct acting'")
(P/'scripts/build_supported_recovery.py').write_text(s)
cfg=(R/'locomotion/battlefield_corrections_v006/scripts/configure_v006.py').read_text().replace('v006','v007').replace('V006','V007')
(P/'scripts/configure_v007.py').write_text(cfg)
print('V007_DERIVED_NATIVE_BUILDER_READY')
