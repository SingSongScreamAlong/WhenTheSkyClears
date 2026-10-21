import subprocess,os,time,json,ctypes
from ctypes import wintypes
from pathlib import Path
P=Path(__file__).resolve().parents[1]
B=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
class PMC(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
memory=ctypes.WinDLL('psapi').GetProcessMemoryInfo;memory.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD];memory.restype=wintypes.BOOL
def gpu_used():
    try:
        r=subprocess.run([r'C:\Windows\system32\nvidia-smi.exe','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=3,creationflags=subprocess.CREATE_NO_WINDOW)
        return int(r.stdout.strip().splitlines()[0]) if r.returncode==0 else None
    except Exception:return None
baseline=gpu_used();peak_gpu=baseline or 0;peak_rss=0;reason=None;samples=[];started=time.perf_counter();env=os.environ.copy();env['OMP_NUM_THREADS']='2'
with (P/'evidence/render_motion.log').open('w') as log:
    p=subprocess.Popen([str(B),'--background',str(P/'native/WTSC_Gas_Particles_Proof_48r_120f_v004.blend'),'--threads','2','--python',str(P/'scripts/render_gas_proof.py'),'--','motion'],stdout=log,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    (P/'evidence/owned_gpu_render.json').write_text(json.dumps({'pid':p.pid,'script':'render_gas_proof.py -- motion','wall_cap':180,'rss_cap_MiB':2048},indent=2))
    while p.poll() is None:
        pc=PMC();pc.cb=ctypes.sizeof(pc)
        if memory(wintypes.HANDLE(int(p._handle)),ctypes.byref(pc),ctypes.sizeof(pc)):peak_rss=max(peak_rss,pc.PeakWorkingSetSize,pc.WorkingSetSize)
        now=time.perf_counter()-started
        if not samples or now-samples[-1]['seconds']>=2:
            used=gpu_used();peak_gpu=max(peak_gpu,used or 0);samples.append({'seconds':round(now,2),'rss_bytes':pc.WorkingSetSize,'gpu_total_used_MiB':used})
        if now>180:reason='180second render cap'
        elif peak_rss>2048*1024**2:reason='2GiB render RSS cap'
        if reason:p.terminate();break
        time.sleep(.25)
    p.wait(timeout=15)
report={'pid':p.pid,'exit_code':p.returncode,'terminated_for_limit':reason,'wall_seconds':time.perf_counter()-started,'peak_rss_bytes':peak_rss,'gpu_baseline_total_used_MiB':baseline,'gpu_peak_total_used_MiB':peak_gpu,'gpu_note':'Device total usage, not exclusive per-process attribution. Production was absent at preflight.','samples':samples,'all_frames_report_exists':(P/'evidence/render_motion.json').exists()}
(P/'evidence/render_resources.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='samples'}),flush=True)
if p.returncode!=0 or reason or not report['all_frames_report_exists']:raise SystemExit(2)
