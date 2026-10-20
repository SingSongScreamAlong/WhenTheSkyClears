from pathlib import Path
import json,numpy as np
from PIL import Image
O=Path(__file__).resolve().parents[1];Q=O/'evidence/native_edit_pixels';render=json.loads((O/'evidence/NATIVE_EDIT_RENDER.json').read_text());build=json.loads((O/'evidence/BUILD.json').read_text());assert render['native_sha256']==build['native_sha256']
rows=[]
for g in [937,1056]:
 a=np.asarray(Image.open(Q/f'direct_{g:04d}.png').convert('RGB')).astype(np.int16);b=np.asarray(Image.open(Q/f'master_{g:04d}.png').convert('RGB')).astype(np.int16);d=np.abs(a-b)
 rows.append({'frame':g,'max_RGB_error':int(d.max()),'mean_RGB_error':float(d.mean())})
report={'native_sha256':render['native_sha256'],'resolution':[1280,720],'rows':rows,'all_within_one_RGB_code_value':all(r['max_RGB_error']<=1 for r in rows)}
(O/'evidence/NATIVE_EDIT_PIXEL_AGREEMENT.json').write_text(json.dumps(report,indent=2));assert report['all_within_one_RGB_code_value'];print('NATIVE_EDIT_PIXEL_AGREEMENT_PASSED',json.dumps(rows))
