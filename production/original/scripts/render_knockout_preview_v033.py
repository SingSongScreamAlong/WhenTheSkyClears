import subprocess,time,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
B=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
source=R/'shots/world/WTSC_Knockout_Ending_Editable_v033.blend';partdir=R/'renders/world_v016/ending_parts_v033';partdir.mkdir(exist_ok=True)
jobs=[];flags=subprocess.CREATE_NO_WINDOW
for i,(a,b) in enumerate([(1969,2094),(2095,2220),(2221,2346),(2347,2472)]):
 out=partdir/f'part_{i+1}.mp4';assert not out.exists()
 log=open(partdir/f'part_{i+1}.log','w',encoding='utf8')
 p=subprocess.Popen([str(B),'--background','--factory-startup',str(source),'--threads','3','--python',str(R/'scripts/render_knockout_part_v033.py'),'--',str(a),str(b),str(out)],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
 jobs.append((p,log,out,a,b));print('START',p.pid,a,b,flush=True)
while any(p.poll() is None for p,_,_,_,_ in jobs):
 print('RENDER_PROGRESS',[(a,b,'running' if p.poll() is None else p.returncode) for p,_,_,a,b in jobs],flush=True);time.sleep(25)
for p,log,out,a,b in jobs:
 log.close();assert p.returncode==0 and out.exists(),str(out)
 assert 'ENDING_PART_COMPLETED' in out.with_suffix('.log').read_text(encoding='utf8',errors='replace'),str(out)
 result=subprocess.run([str(F),'-hide_banner','-i',str(out),'-an','-f','null','-'],capture_output=True,text=True)
 assert result.returncode==0,result.stderr[-2000:]
 print('PART_DECODED',out.name,result.stderr[-450:],flush=True)
concat=partdir/'concat.txt';concat.write_text('\n'.join("file '"+p.name+"'" for _,_,p,_,_ in jobs),encoding='utf8')
output=R/'renders/world_v016/WTSC_Knockout_Ending_4K_v033.mp4';assert not output.exists()
cmd=[str(F),'-hide_banner','-nostdin','-f','concat','-safe','0','-i',str(concat),'-ss','82','-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','afade=t=out:st=8:d=10,apad=pad_dur=3','-c:a','aac','-b:a','320k','-ar','48000','-t','21','-movflags','+faststart',str(output)]
result=subprocess.run(cmd,capture_output=True,text=True);(R/'notes/world_v016/ending_mux_v033.log').write_text(result.stderr);assert result.returncode==0,result.stderr[-2500:]
decoded=subprocess.run([str(F),'-hide_banner','-i',str(output),'-f','null','-'],capture_output=True,text=True);assert decoded.returncode==0
(R/'notes/world_v016/ending_full_decode_v033.log').write_text(decoded.stderr)
report={'preview':str(output),'size':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'frames':504,'seconds':21,'resolution':[3840,2160],'fps':24,'global_range':[82,103],'native_picture_parts':[[a,b] for _,_,_,a,b in jobs],'clean_cached_picture_range':[52,70],'music_source_range':[82,100],'music_fade_global':[90,100],'silent_card_global':[100,103],'full_decode_pass':True}
(R/'notes/world_v016/ending_completed_v033.json').write_text(json.dumps(report,indent=2));print('ENDING_PREVIEW_COMPLETE',json.dumps(report),flush=True)
