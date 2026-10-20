"""Fetch official Godot 4.6 portable tools and verify the release hashes."""
from pathlib import Path
import urllib.request, hashlib, zipfile, json, io, struct, time
P = Path(__file__).resolve().parent
BASE = 'https://github.com/godotengine/godot-builds/releases/download/4.6-stable/'
checks = {}
for line in (P/'SHA512-SUMS.txt').read_text().splitlines():
    parts = line.split()
    if len(parts) == 2: checks[parts[1].lstrip('*')] = parts[0]
name = 'Godot_v4.6-stable_win64.exe.zip'
dest = P/name
if not dest.exists(): urllib.request.urlretrieve(BASE+name, dest)
assert hashlib.sha512(dest.read_bytes()).hexdigest() == checks[name], 'Engine checksum mismatch'
with zipfile.ZipFile(dest) as z: z.extractall(P/'godot')
print('GODOT_ENGINE_VERIFIED', flush=True)
# Fetch the official template archive once. Keep only Windows/Linux/Web templates
# needed by this game; do not install any global settings or system packages.
name = 'Godot_v4.6-stable_export_templates.tpz'
dest = P/name
if not dest.exists(): urllib.request.urlretrieve(BASE+name, dest)
assert hashlib.sha512(dest.read_bytes()).hexdigest() == checks[name], 'Template checksum mismatch'
with zipfile.ZipFile(dest) as z:
    for entry in z.infolist():
        if entry.filename.split('/')[-1] in ['windows_release_x86_64.exe','windows_debug_x86_64.exe']:
            (P/entry.filename.split('/')[-1]).write_bytes(z.read(entry))
print('WINDOWS_TEMPLATES_VERIFIED', flush=True)
(P/'ENGINE_PROVENANCE.json').write_text(json.dumps({'version':'4.6.stable','source':BASE,'sha512':checks,'verified':True},indent=2))
