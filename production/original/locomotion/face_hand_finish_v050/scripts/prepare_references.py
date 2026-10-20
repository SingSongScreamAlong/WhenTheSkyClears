"""Extract existing asset regions for the face-paint reference; no artwork edit."""
from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
for n in ['reference','textures','native','evidence','previews']:(P/n).mkdir(exist_ok=True)
girl=ROOT/'characters/Pair_Painterly_Near_Age_v015.png';boy=ROOT/'locomotion/character_design_finish_v040/textures/WTSC_Boy_Painted_Parts_Atlas_v040.png'
Image.open(girl).crop((850,90,1110,390)).resize((1040,1200),Image.Resampling.LANCZOS).save(P/'reference/GIRL_ORIGINAL_HEAD_IDENTITY.png')
Image.open(boy).crop((0,0,440,490)).save(P/'reference/BOY_PAINT_LANGUAGE_REFERENCE.png')
(P/'evidence/REFERENCE_SOURCES.json').write_text(json.dumps({'girl_source':str(girl),'girl_sha256':hashlib.sha256(girl.read_bytes()).hexdigest(),'girl_crop_bounds':[850,90,1110,390],'girl_reference_scale':4,'boy_source':str(boy),'boy_sha256':hashlib.sha256(boy.read_bytes()).hexdigest(),'scope':'Existing raster region extraction for the painting study only; source files read-only.'},indent=2))
