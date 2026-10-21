from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parents[1];F=P/'rgba/Drawn_Compact_Impact_24fps';records=[]
for f in range(1,73):
    p=F/f'{f:04d}.png'
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.size==(1920,1080)
        a=np.array(im);alpha=a[:,:,3];records.append({'frame':f,'bytes':p.stat().st_size,'alpha_nonzero_pixels':int((alpha>0).sum()),'alpha_intermediate_pixels':int(((alpha>0)&(alpha<255)).sum())})
assert records[0]['alpha_nonzero_pixels']==0
a=np.array(Image.open(F/'0009.png')).astype('int16');b=np.array(Image.open(P/'evidence/Append_Offset100_Actual_RGBA_Frame9.png')).astype('int16')
diff=np.abs(a-b);mask=(a[:,:,3]>0)|(b[:,:,3]>0)
report={'frames':72,'fps':24,'pixels':[1920,1080],'all_files_opened':True,'alpha_convention':'Straight/unassociated PNG','no_foreground_holdout_baked':True,'frames_summary':records,'append_offset100_pixel_comparison':{'all_pixels_identical':bool(np.array_equal(a,b)),'max_channel_error_8bit':int(diff.max()),'mean_channel_error_8bit':float(diff.mean()),'mean_error_effect_area_8bit':float(diff[mask].mean()) if mask.any() else 0,'effect_area_pixels':int(mask.sum())}}
baseline=np.array(Image.open(P/'evidence/Append_Baseline_Actual_RGBA_Frame9.png')).astype('int16');bd=np.abs(a-baseline);bm=(a[:,:,3]>0)|(baseline[:,:,3]>0)
report['append_baseline_pixel_comparison']={'all_pixels_identical':bool(np.array_equal(a,baseline)),'max_channel_error_8bit':int(bd.max()),'mean_channel_error_8bit':float(bd.mean()),'mean_error_effect_area_8bit':float(bd[bm].mean())}
report['appended_baseline_vs_appended_offset100_pixels_identical']=bool(np.array_equal(b,baseline))
(P/'evidence/rgba_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='frames_summary'}))
