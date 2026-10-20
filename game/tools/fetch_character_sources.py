"""Download free Standard asset archives from their publisher's normal public flow.
No login, payment, registration, or personal data is supplied.
"""
from pathlib import Path
import urllib.request, urllib.parse, http.cookiejar, re, json, hashlib, zipfile
P=Path(__file__).resolve().parents[1]/'character_sources';P.mkdir(exist_ok=True)
jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
records=[]
for slug in ['universal-animation-library','universal-base-characters']:
    base='https://quaternius.itch.io/'+slug
    page=opener.open(base).read().decode()
    csrf=re.search(r'name="csrf_token" value="([^"]+)"',page).group(1)
    request=urllib.request.Request(base+'/download_url',data=urllib.parse.urlencode({'csrf_token':csrf}).encode(),headers={'Referer':base,'X-Requested-With':'XMLHttpRequest'})
    response=json.load(opener.open(request)); link=response.get('url')
    assert link and link.startswith(base+'/download/'),response
    downloads=opener.open(link).read().decode()
    (P/(slug+'_download_page.html')).write_text(downloads,encoding='utf8')
    # The returned authorized free-download page exposes the available upload IDs.
    uploads=re.findall(r'<div[^>]*class="[^"]*upload[^"]*"[^>]*data-upload_id="(\d+)"[\s\S]*?(?=<div[^>]*class="[^"]*upload[^"]*"[^>]*data-upload_id=|$)',downloads)
    matches=list(re.finditer(r'data-upload_id="(\d+)"',downloads))
    selected=None
    for j,m in enumerate(matches):
        block=downloads[m.start():matches[j+1].start() if j+1<len(matches) else len(downloads)]
        if '[Standard]' in block: selected=m.group(1);break
    if selected is None:
        print('UPLOAD_DISCOVERY',slug,[(m.group(1),downloads[m.start():m.start()+500]) for m in matches],flush=True)
        raise RuntimeError('No free Standard upload identified')
    request=urllib.request.Request(base+'/file/'+selected+'?source=game_download&as_props=1',data=urllib.parse.urlencode({'csrf_token':csrf}).encode(),headers={'Referer':link,'X-Requested-With':'XMLHttpRequest'})
    file_info=json.load(opener.open(request)); source=file_info['url']
    dest=P/(slug+'_standard.zip')
    with opener.open(source) as src,dest.open('wb') as out:
        while True:
            block=src.read(1024*1024)
            if not block:break
            out.write(block)
    folder=P/slug;folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest) as archive:
        for info in archive.infolist():
            target=(folder/info.filename).resolve();assert target.is_relative_to(folder.resolve())
        archive.extractall(folder)
        files=archive.namelist()
    records.append({'publisher':'Quaternius','page':base,'edition':'Free Standard','upload_id':selected,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'files':files,'use':'Local character modeling and animation source. Preserve archive license; do not redistribute standalone sources if current QAL applies.'})
    print('DOWNLOADED',slug,len(files),dest.stat().st_size,flush=True)
(P/'SOURCE_RECEIPTS.json').write_text(json.dumps(records,indent=2),encoding='utf8')
