"""Owned v064 tail coordinator. Not imported by Blender; run manually after review.
Only stops the pinned original 1201..1800 worker. Native/worker files are read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import subprocess
import time
import traceback

O = Path(__file__).resolve().parents[1]
E = O / 'evidence'
FRAMES = O / 'previews/world_frames'
WORKER = O / 'scripts/render_world_worker.py'
BLENDER = Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
TARGET_PID = 35596
TARGET_CREATED_MS = 1792370738557  # Read-only CIM observation of this exact owned process.
CANONICAL = ((1, 600), (601, 1200), (1201, 1800), (1801, 2400))
THIRD = (1201, 1800)
ATTEMPT = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
ARCHIVE = E / 'parallel_tail_proofs' / ATTEMPT
LOGS = E / 'parallel_tail_logs' / ATTEMPT
REPORT = E / 'PARALLEL_TAIL_COORDINATOR.json'
PS = str(Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe')
state = {'attempt_utc': ATTEMPT, 'target_pid': TARGET_PID, 'target_created_unix_ms': TARGET_CREATED_MS,
         'native_or_worker_modified': False, 'started_workers': [], 'archived_proofs': []}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def save(phase):
    state['phase'] = phase
    REPORT.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    print('V064_TAIL_COORDINATOR', phase, flush=True)


def proof_path(a, b):
    return E / ('world_worker_%04d_%04d.json' % (a, b))


def read_proof(a, b):
    try:
        d = json.loads(proof_path(a, b).read_text(encoding='utf-8-sig'))
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None  # Worker writes its final JSON non-atomically.
    assert d['native_sha256'] == state['native_sha256']
    assert d['native_unchanged'] is True and d['resolution'] == [1280, 720]
    assert d['source_world_frames_fresh'] is True and d['all_shared_material_driver_checks_pass'] is True
    assert [r['frame'] for r in d['frames']] == list(range(a, b + 1))
    return d


def guard():
    assert sha(state['native']) == state['native_sha256'], 'Native changed'
    assert sha(E / 'FULL_CUT_BUILD.json') == state['build_sha256'], 'Build changed'
    assert sha(WORKER) == state['worker_sha256'], 'Worker script changed'


def process_info(pid):
    cmd = ("$p=Get-CimInstance Win32_Process -Filter 'ProcessId = %d'; "
           "if($null -ne $p){[pscustomobject]@{ProcessId=$p.ProcessId;Name=$p.Name;"
           "ExecutablePath=$p.ExecutablePath;CommandLine=$p.CommandLine;"
           "CreationUnixMs=([DateTimeOffset]$p.CreationDate).ToUnixTimeMilliseconds()}"
           "|ConvertTo-Json -Compress}") % pid
    r = subprocess.run([PS, '-NoProfile', '-NonInteractive', '-Command', cmd],
                       check=True, capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None


def command_argv(command):
    shell32 = ctypes.WinDLL('shell32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    shell32.CommandLineToArgvW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    shell32.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL
    count = ctypes.c_int()
    ptr = shell32.CommandLineToArgvW(command, ctypes.byref(count))
    if not ptr:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return [ptr[i] for i in range(count.value)]
    finally:
        kernel32.LocalFree(ctypes.cast(ptr, wintypes.HLOCAL))


def validate_target(info):
    assert info and info['ProcessId'] == TARGET_PID, 'Pinned worker no longer running'
    assert info['CreationUnixMs'] == TARGET_CREATED_MS, 'PID reused; refusing termination'
    assert Path(info['ExecutablePath']).resolve() == BLENDER.resolve()
    argv = command_argv(info['CommandLine'])
    expected = [str(BLENDER), '--background', '--factory-startup', '--disable-autoexec',
                '--threads', '3', '--python', str(WORKER), '--', '1201', '1800']
    assert argv == expected, ('Unexpected command; refusing termination', argv)
    return info


def stop_pinned_target():
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    k.GetProcessTimes.restype = wintypes.BOOL
    k.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k.TerminateProcess.restype = wintypes.BOOL
    k.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k.WaitForSingleObject.restype = wintypes.DWORD
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k.OpenProcess(0x1000 | 0x0001 | 0x00100000, False, TARGET_PID)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        creation, exit_time, kernel, user = (wintypes.FILETIME() for _ in range(4))
        assert k.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time),
                                 ctypes.byref(kernel), ctypes.byref(user))
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        assert (ticks - 116444736000000000) // 10000 == TARGET_CREATED_MS
        state['stopped_process'] = validate_target(process_info(TARGET_PID))
        # This handle pins the verified process; no recursive/task-tree termination.
        assert k.TerminateProcess(handle, 1), 'Could not terminate owned worker'
        assert k.WaitForSingleObject(handle, 30000) == 0, 'Owned worker did not exit'
    finally:
        k.CloseHandle(handle)
    assert process_info(TARGET_PID) is None, 'PID still active/reused; stop here'


def verify_pngs(quarantine=False):
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    rows, failures = [], []
    for f in range(1201, 1801):
        path = FRAMES / ('%04d.png' % f)
        if not path.exists():
            continue
        try:
            before = path.stat()
            with Image.open(path) as im:
                assert im.format == 'PNG' and im.size == (1280, 720) and im.mode == 'RGB'
                im.verify()  # PNG chunk CRC/integrity.
            with Image.open(path) as im:
                im.load()  # Full pixel decompression, not merely header inspection.
            after = path.stat()
            assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            rows.append({'frame': f, 'sha256': sha(path), 'bytes': after.st_size})
        except Exception as exc:
            item = {'frame': f, 'error': repr(exc)}
            if quarantine:
                dest = E / 'parallel_tail_quarantine' / ATTEMPT / path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                path.rename(dest)
                item['quarantined_to'] = str(dest)
            failures.append(item)
    return rows, failures


def missing():
    return [f for f in range(1201, 1801) if not (FRAMES / ('%04d.png' % f)).is_file()]


def start_worker(a, b, label):
    guard()
    log = LOGS / ('%s_%04d_%04d.log' % (label, a, b))
    log.parent.mkdir(parents=True, exist_ok=True)
    out = log.open('wb')
    argv = [str(BLENDER), '--background', '--factory-startup', '--disable-autoexec',
            '--threads', '3', '--python', str(WORKER), '--', str(a), str(b), '--resume']
    try:
        p = subprocess.Popen(argv, stdout=out, stderr=subprocess.STDOUT)
    finally:
        out.close()
    state['started_workers'].append({'pid': p.pid, 'range': [a, b], 'log': str(log), 'argv': argv})
    save('workers running')
    return p


def main():
    from PIL import Image  # Dependency check before any process termination.
    assert os.name == 'nt' and BLENDER.is_file() and WORKER.is_file()
    build = json.loads((E / 'FULL_CUT_BUILD.json').read_text(encoding='utf-8-sig'))
    state.update(native=build['native'], native_sha256=build['native_sha256'],
                 build_sha256=sha(E / 'FULL_CUT_BUILD.json'), worker_sha256=sha(WORKER))
    guard()
    save('waiting for other three canonical proofs')
    while not all(read_proof(*r) is not None for r in CANONICAL if r != THIRD):
        time.sleep(3)
    guard()
    absent = missing()
    state['missing_before_decision'] = len(absent)
    if read_proof(*THIRD) is not None or len(absent) <= 120:
        save('leaving original worker to finish; split threshold not met')
        while read_proof(*THIRD) is None:
            time.sleep(3)
        guard()
        rows, bad = verify_pngs(False)
        assert not bad and len(rows) == 600, ('Original completed PNG integrity', bad)
        state['decision'] = 'original worker retained'
        save('complete')
        return

    validate_target(process_info(TARGET_PID))
    # Fail rather than touching any old canonical proof or an unexpected completed job.
    assert read_proof(*THIRD) is None, 'Original just completed; rerun coordinator'
    guard()
    stop_pinned_target()
    save('owned original worker stopped')
    rows, bad = verify_pngs(True)
    state['retained_before_split'] = rows
    state['bad_interrupted_PNGs'] = bad
    guard()
    absent = missing()
    count = len(absent)
    groups = [absent[i * count // 3:(i + 1) * count // 3] for i in range(3)]
    ranges = [(group[0], group[-1]) for group in groups if group]
    assert all(ranges[i][1] < ranges[i + 1][0] for i in range(len(ranges) - 1))
    assert all(any(a <= f <= b for a, b in ranges) for f in absent)
    state['split_ranges'] = [list(r) for r in ranges]
    assert all(not proof_path(a, b).exists() for a, b in ranges), 'Prior subrange proof would be overwritten'
    processes = [(r, start_worker(*r, label='split')) for r in ranges]
    exit_codes = [(r, p.wait()) for r, p in processes]
    state['split_exit_codes'] = [[list(r), code] for r, code in exit_codes]
    assert all(code == 0 for _, code in exit_codes), exit_codes
    guard()
    rows, bad = verify_pngs(False)
    assert not bad and len(rows) == 600, ('Precanonical full PNG decode', bad, len(rows))
    hashes = {r['frame']: r['sha256'] for r in rows}
    for a, b in ranges:
        proof = read_proof(a, b)
        assert proof is not None
        assert all(hashes[r['frame']] == r['sha256'] for r in proof['frames'])
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for a, b in ranges:
        path = proof_path(a, b)
        dest = ARCHIVE / path.name
        state['archived_proofs'].append({'path': str(dest), 'sha256': sha(path)})
        path.rename(dest)
    state['precanonical_png_integrity'] = {'checked': len(rows), 'bad': 0, 'checks': 'PIL verify+load and stable size/mtime'}
    assert not proof_path(*THIRD).exists(), 'Unexpected canonical proof; refusing overwrite'
    save('collecting canonical 1201..1800 replay proof')
    p = start_worker(*THIRD, label='canonical')
    assert p.wait() == 0, 'Canonical replay failed'
    guard()
    proof = read_proof(*THIRD)
    assert proof is not None and proof['resumed_existing_frames'] == list(range(1201, 1801))
    assert all(r['rendered_in_session'] is False and r['sha256'] == hashes[r['frame']]
               for r in proof['frames'])
    expected = {proof_path(*r).name for r in CANONICAL}
    assert {p.name for p in E.glob('world_worker_*.json')} == expected
    state['canonical_proof'] = {'path': str(proof_path(*THIRD)), 'sha256': sha(proof_path(*THIRD)),
                                '600_resumed_hashes_match_full_decoded_PNGs': True}
    state['decision'] = 'three disjoint owned tail workers; canonical proof restored'
    save('complete')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        state['exception'] = repr(exc)
        state['traceback'] = traceback.format_exc()
        save('failed; inspect logs and retained evidence')
        raise
