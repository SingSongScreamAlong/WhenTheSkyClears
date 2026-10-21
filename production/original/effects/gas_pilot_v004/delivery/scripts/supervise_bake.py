"""Hard caps apply only to the child process this script creates."""
import subprocess,os,time,json,ctypes,sys
from ctypes import wintypes
from pathlib import Path
P=Path(__file__).resolve().parents[1]
B=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
fixture=P.parent/'benchmark_v003/native/WTSC_Evolution_Proof_v003.blend'
proof='--proof' in sys.argv
cache=P/('cache/proof_48r_120f' if proof else 'cache/pilot_40r_72f')
prefix='proof_' if proof else ''
assert not cache.exists(),'Pilot cache already exists: reconcile before any new bake.'
class PMC(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
mem=ctypes.WinDLL('psapi').GetProcessMemoryInfo;mem.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD];mem.restype=wintypes.BOOL
env=os.environ.copy();env['OMP_NUM_THREADS']='2';env['OPENBLAS_NUM_THREADS']='2'
start=time.perf_counter();peak=0;peak_private=0;cache_peak=0;reason=None;samples=[]
with (P/('evidence/'+prefix+'bake_log.txt')).open('w') as log:
    command=[str(B),'--background',str(fixture),'--threads','2','--python',str(P/'scripts/bake_gas_pilot.py')]+(['--','--proof'] if proof else [])
    process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    (P/('evidence/'+prefix+'owned_bake_process.json')).write_text(json.dumps({'pid':process.pid,'script':'bake_gas_pilot.py','owned_by':'supervise_bake.py','limits':{'seconds':120,'cache_bytes':128*1024**2,'rss_bytes':2048*1024**2}},indent=2))
    while process.poll() is None:
        elapsed=time.perf_counter()-start;pc=PMC();pc.cb=ctypes.sizeof(pc)
        if mem(wintypes.HANDLE(int(process._handle)),ctypes.byref(pc),ctypes.sizeof(pc)):
            peak=max(peak,pc.WorkingSetSize,pc.PeakWorkingSetSize);peak_private=max(peak_private,pc.PrivateUsage)
        used=sum(f.stat().st_size for f in cache.rglob('*') if f.is_file()) if cache.exists() else 0;cache_peak=max(cache_peak,used)
        if not samples or elapsed-samples[-1]['seconds']>=2:samples.append({'seconds':round(elapsed,2),'rss_bytes':pc.WorkingSetSize,'private_bytes':pc.PrivateUsage,'cache_bytes':used})
        if elapsed>120:reason='120-second wall cap'
        elif used>128*1024**2:reason='128MiB cache cap'
        elif peak>2048*1024**2:reason='2GiB resident memory cap'
        if reason:process.terminate();break
        time.sleep(.25)
    process.wait(timeout=15)
report={'owned_pid':process.pid,'exit_code':process.returncode,'terminated_for_limit':reason,'wall_seconds':time.perf_counter()-start,'peak_rss_bytes':peak,'peak_private_bytes':peak_private,'peak_cache_bytes':cache_peak,'cpu_threads_requested':2,'priority':'BELOW_NORMAL','samples':samples,'bake_result_exists':(P/('evidence/'+prefix+'bake_result.json')).exists()}
(P/('evidence/'+prefix+'bake_resources.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if process.returncode!=0 or reason or not report['bake_result_exists']:raise SystemExit(2)
