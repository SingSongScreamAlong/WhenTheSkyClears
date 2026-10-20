from pathlib import Path
import re,json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
rx=re.compile(r'\b(?:aged?|ages|years?\s*old|height|heights|stature|metres?|meters?)\b|(?:near|same)[_ -]age|(?:boy|girl|child).{0,35}(?:scale|tall)|(?:scale|tall).{0,35}(?:boy|girl|child)',re.I)
files=[]
for folder in ['notes','reference','source','characters','scripts']:
 files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in ['.py','.txt','.md','.json','.csv'] and p.stat().st_size<4000000)
files+=list(ROOT.glob('*.txt'))
hits=[]
for p in files:
 try:lines=p.read_text(encoding='utf-8-sig').splitlines()
 except (UnicodeError,OSError):continue
 for n,line in enumerate(lines,1):
  if rx.search(line):hits.append({'file':str(p.relative_to(ROOT)),'line':n,'text':line[:900]})
out={'searched_files':len(files),'search_patterns':rx.pattern,'hits':hits}
(P/'evidence/CANON_SEARCH.json').write_text(json.dumps(out,indent=2))
print('SEARCHED_FILES',len(files),'HITS',len(hits))
for h in hits:
 if re.search(r'age|years?\s*old|stature|child.{0,15}height|boy.{0,15}height|girl.{0,15}height|near.?equal',h['text'],re.I) and not re.search('(?:image|pixel|resolution|size|render|layer|plane|mask)_?height',h['text'],re.I):print(json.dumps(h))
print('REFERENCE_SOURCE_NONRASTER_FILES')
for folder in ['reference','source','characters']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and p.suffix.lower() not in ['.png','.jpg','.jpeg','.blend','.blend1','.mp4','.wav','.mp3']:
   print(str(p.relative_to(ROOT)),p.stat().st_size)
