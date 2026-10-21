"""Revise native scar tracing boundary only; original image pixels unchanged."""
from pathlib import Path
import json,ast,numpy as np
from PIL import Image
P=Path(__file__).resolve().parents[1]
source=P/'scripts/trace_painted_assets.py'
parsed=ast.parse(source.read_text());parsed.body=[n for n in parsed.body if isinstance(n,ast.FunctionDef)]
exec(compile(parsed,str(source),'exec'),globals())
info=json.loads((P/'assets/painted_contours.json').read_text())
a=np.asarray(Image.open(info['source']).getchannel('A'));H,W=a.shape
mask=np.zeros_like(a,dtype=bool)
for left,right,values in [(1485,1665,[670,675,664,677,669,681,671,678]),(1700,1888,[679,671,676,666,675,668,681,673,679]),(1935,2110,[676,664,674,669,679,671,681])]:
    xs=np.arange(left,right);top=np.interp(xs,np.linspace(left,right-1,len(values)),values)
    for x,y in zip(xs,top):mask[int(y):,x]=a[int(y):,x]>22
info['scar']['islands']=contours(mask,35)
info['scar']['native_vector_boundary_revision']='Three separated irregular short earth patches traced from untouched painted loweredge. No straight full-width UVband uppercut.'
info['scar']['native_UV_band_only']=[1485,664,2110,689]
(P/'assets/painted_contours_v015b.json').write_text(json.dumps(info,indent=2))
text=(P/'scripts/build_painted_impact.py').read_text()
text=text.replace("'assets/painted_contours.json'","'assets/painted_contours_v015b.json'")
text=text.replace("s.name = 'WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v015'","s.name = 'WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v015b'")
text=text.replace('WTSC_Painted_Main_Impact_Context_v015.blend','WTSC_Painted_Main_Impact_Context_v015b.blend')
text=text.replace('WTSC_Painted_Main_Impact_Append_v015.blend','WTSC_Painted_Main_Impact_Append_v015b.blend')
text=text.replace("P/'evidence/build_main_impact.json'","P/'evidence/build_main_impact_v015b.json'")
text=text.replace("'rendered':False,'artistic_acceptance':False", "'rendered':False,'scar_revision':'Three native irregular painted patches; original stage geometry and RGBA unchanged.','artistic_acceptance':False")
(P/'scripts/build_painted_impact_v015b.py').write_text(text)
for filename in ['render_keys.py','render_consecutive_native4Kcrop.py','verify_native.py']:
    text=(P/'scripts'/filename).read_text().replace("'evidence/build_main_impact.json'","'evidence/build_main_impact_v015b.json'")
    text=text.replace("'previews/native4K_keys'","'previews/native4K_keys_v015b'")
    text=text.replace("'evidence/render_keys.json'","'evidence/render_keys_v015b.json'")
    text=text.replace("'evidence/cold_verification.json'","'evidence/cold_verification_v015b.json'")
    (P/'scripts'/(Path(filename).stem+'_v015b.py')).write_text(text)
print('IRREGULAR_SCAR_VECTORS_V015B_READY',len(info['scar']['islands']))
