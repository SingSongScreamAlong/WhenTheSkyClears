"""Copy the original imagegen outputs; inspect alpha without altering artwork."""
import hashlib, json, shutil
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parents[1]
dest=R/'characters/head_turn_v047'
dest.mkdir(exist_ok=True)
generation=Path(r'WTSC_LOCAL_USER\.codex\generated_images\01a14548-c7ee-7af3-88fe-234af9b17275')
sources={
    'Girl_Three_Quarter_Right_v047.png':generation/'exec-b80ae632-744c-4ebe-a81b-cf885d671043.png',
    'Girl_Three_Quarter_Left_v047.png':generation/'exec-6525c5a9-8450-459a-928e-88127487684c.png',
    'Girl_Front_v047.png':generation/'exec-3ce97624-0b7f-4c19-b5c1-2dedc2d25e99.png',
    'Girl_Left_Profile_v047.png':generation/'exec-0f5ed71b-f82e-410f-bed4-da9996927825.png',
}
rows=[]
for name,source in sources.items():
    target=dest/name
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()
    else:shutil.copy2(source,target)
    im=Image.open(target)
    assert im.mode=='RGBA'
    alpha=im.getchannel('A')
    assert alpha.getextrema()==(0,255)
    rows.append({'path':str(target),'generation_source':str(source),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                 'size':list(im.size),'mode':im.mode,'alpha_bounds':list(alpha.getbbox()),
                 'opaque_bounds':list(alpha.point(lambda x:255 if x>230 else 0).getbbox())})
guide={
 'provider':'Built-in GPT imagegen; original outputs copied byte-for-byte, no external art or image editing.',
 'reference':str(R/'characters/Pair_Painterly_Near_Age_v015.png'),
 'purpose':'Two matching three-quarter views and one frontal drawing for a six-frame native head turn.',
 'prompt_right':'Identity-preserve: GIRL on right of reference, complete isolated head, little neck, full naturally attached braid and small fabric bow. Nose points image RIGHT about35 degrees off frontal. Exact age/skull/cheek/jaw proportions, swept wavy fringe, subtle charcoal black/grayscale paint, tiny warm-white flat eye marks, transparent margins; no boy, torso, text, halo, cropped-cap hair or 3D rendering.',
 'prompt_left':'Identity-preserve: use original pair and generated first drawing as references. Corresponding second quarter view, nose image LEFT toward boy about35 degrees off frontal, naturally attached braid behind skull on RIGHT. Same girl and paint/fringe/skull/age; small flat warm-white triangular eye marks, no iris detail/glow, no torso/text/halo/cropped cap; full head/braid on transparent alpha.',
 'prompt_front':'Identity-preserve: same original charcoal girl and matching generated quarter views, front-on midway through turn. Complete swept fringe, small neck and single naturally attached braid with bow on image right. Nearly black charcoal face and subtle fine grayscale hair strokes, small flat eye marks, genuine transparency, no torso, text, cap or 3D rendering.',
 'assets':rows,
 'review_limit':'Generated quarter views still require native shot registration and visual review. Eye/pupil rendering differs subtly from the original simple profile mark; no artistic acceptance implied.'
}
(dest/'provenance.json').write_text(json.dumps(guide,indent=2))
print(json.dumps(rows,indent=2))
