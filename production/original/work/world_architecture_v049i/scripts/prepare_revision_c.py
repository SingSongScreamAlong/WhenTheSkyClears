from pathlib import Path
O=Path(__file__).parent
s=(O/'build_registered_school.py').read_text()
s=s.replace("WTSC_Registered_School_Depth_v049.blend","WTSC_Registered_School_Depth_v049c.blend")
start=s.index("(O/'before_preview').mkdir")
end=s.index("C=bpy.data.collections",start)
s=s[:start]+s[end:]
def change(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
change('932.5+50.5*math.cos','936.5+41.5*math.cos')
change('hole=arc+[(983,632),(882,632)]','hole=arc+[(978,631),(895,631)]')
change('inner=[(932.5+(x-932.5)*.94','inner=[(936.5+(x-936.5)*.94')
change('outer=[(932.5+(x-932.5)*1.055','outer=[(936.5+(x-936.5)*1.13')
change('faces,[woodV,woodSide],inds)','faces,[frontPaint,woodSide],inds)')
a=s.index('for i,(a,b,wi) in enumerate(')
b=s.index('\n dx=b[0]',a)
s=s[:a]+"for i,(a,b,wi) in enumerate([((936.5,439),(936.5,631),6.4),((895,486.5),(978,486.5),6.0),((895,551),(978,551),5.0),((895,597),(978,597),4.0),((921.4,438),(921.4,482),2.1),((951.3,439),(951.3,482),2.1)]):"+s[b:]
change('10.04,woodV if abs(dy)>abs(dx) else woodH,woodSide)','10.04,frontPaint,woodSide)')
a=s.index('shards=[')
b=s.index('\n# Original-painted stone',a)
s=s[:a]+"shards=json.loads((O/'original_glass_geometry.json').read_text())['polygons']\nfor i,poly in enumerate(shards):extrude('registered glass fragment '+str(i),poly,9.975,9.986,frontPaint,glassEdge)"+s[b:]
refine=(O/'refine_registered_school.py').read_text()
a=refine.index('# Keep spatial masks fixed')
b=refine.index("s.name='WTSC_",a)
bank=refine[a:b]
s=s.replace('assert all(not o.animation_data for o in C.objects)',bank+"\nassert all(not o.animation_data for o in C.objects)")
s=s.replace('WTSC_REGISTERED_SCHOOL_DEPTH_v049_OPEN_DIAGNOSTIC','WTSC_REGISTERED_SCHOOL_DEPTH_v049c_OPEN_DIAGNOSTIC')
s=s.replace("O/'after_preview'","O/'after_preview_c'")
s=s.replace("O/'ARCHITECTURE_BUILD_v049.json'","O/'ARCHITECTURE_BUILD_v049c.json'")
s=s.replace("'created_objects':len(created)","'glass_contours_from_source':len(shards),'bank_valid_sample_remaps':fixed,'created_objects':len(created)")
s=s.replace('native glass/wood and physical edges supply new resolution-independent detail','registered source-painted glass/wood with physical edges supply resolution-independent boundary detail')
s=s.replace("'new_color_progression_applied':False","'new_color_progression_applied':False,'glass_boundary_method':'Source-painted surviving fragments traced to native extruded polygons; no generated texture or upscale claimed.'")
compile(s,'build_registered_school_c.py','exec')
(O/'build_registered_school_c.py').write_text(s)
print('Prepared source-registered revision c')
