import json,re,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
session=Path(r'WTSC_LOCAL_USER\.codex\sessions\2026\10\16\rollout-2026-10-16T11-16-00-01a14548-c7ee-7af3-88fe-234af9b17275.jsonl')
prompts=[]
for line in session.open(encoding='utf-8'):
    try:record=json.loads(line)
    except json.JSONDecodeError:continue
    p=record.get('payload',{})
    if p.get('type')!='custom_tool_call':continue
    source=p.get('input','')
    if 'tools.image_gen__imagegen' not in source:continue
    key=re.search(r'store\("(world_[^"]+)"',source)
    prompt=re.search(r'prompt:("(?:[^"\\]|\\.)*")',source)
    if not key or not prompt:continue
    refs=re.search(r'referenced_image_paths:(\[[^\]]*\])',source)
    prompts.append({'key':key.group(1),'tool':'built-in image_gen.imagegen',
      'prompt':json.loads(prompt.group(1)),
      'transparent_background':'transparent_background:true' in source,
      'references':json.loads(refs.group(1)) if refs else []})
(ROOT/'notes/imagegen_world_prompts.json').write_text(json.dumps(prompts,indent=2),encoding='utf-8')
assets=[]
for p in sorted((ROOT/'sets/painted_layers').glob('*.png'))+[ROOT/'characters/Pair_Static_Imagegen_v001.png',ROOT/'characters/Pair_Static_Vector_Contours_v001.json']:
    d={'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'status':'provisional original project art'}
    if p.suffix=='.png':
        im=Image.open(p);d.update({'size':list(im.size),'mode':im.mode,'alpha_extrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None})
    assets.append(d)
manifest={'project':'When the Sky Clears','scope':'worlds and sets first; translation-only held pair',
  'master_resolution':[3840,2160],'fps':24,'duration_seconds':100,'frames':2400,
  'native_project':'shots/world/WTSC_World_First_v004.blend',
  'source_scene':'WTSC_WORLD_FIRST_4K','master_scene':'WTSC_MASTER_4K_100S',
  'areas':['village intact/abandoned','woods','school','camp','battlefield/crater','ruins/ash','monumental title terrain'],
  'asset_generation':'built-in GPT imagegen; exact prompt set in imagegen_world_prompts.json',
  'source_raster_note':'Generated rasters are approximately 1672x941 or 1536x1024. Native output is rendered at UHD; no claim of native 4K input paintings.',
  'music':'user-supplied exact 100.000-second WAV; no public release permission established',
  'character_animation':'None. One held native GP drawing and object translation only.',
  'future_animation_direction':'Use actual rigged 3D motion aligned behind manipulable 2D vector outlines. The prior procedural mannequin gait is rejected.',
  'assets':assets}
(ROOT/'notes/world_asset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Recorded',len(prompts),'exact imagegen world prompts and',len(assets),'source assets')
