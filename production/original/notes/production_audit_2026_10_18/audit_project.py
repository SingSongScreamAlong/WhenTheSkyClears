"""Read-only project census; writes only into this audit directory."""
import ast
import collections
import csv
import hashlib
import json
import re
import subprocess
import wave
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
SKIP = {'.git', '__pycache__'}

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

files = sorted(p for p in ROOT.rglob('*') if p.is_file()
               and not (set(p.relative_to(ROOT).parts) & SKIP)
               and not p.is_relative_to(OUT))
rows = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
         'extension': p.suffix.lower(),
         'modified_utc': datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()}
        for p in files]
with (OUT / 'file_inventory.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
folders = collections.defaultdict(lambda: {'files': 0, 'bytes': 0})
extensions = collections.Counter()
invalid_json, syntax_errors, hardcoded_scripts, scripts = [], [], [], []
docs = []
for p, row in zip(files, rows):
    bucket = folders[row['path'].split('/')[0]]
    bucket['files'] += 1
    bucket['bytes'] += row['bytes']
    extensions[row['extension']] += 1
    if p.suffix == '.json':
        try:
            json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as exc:
            invalid_json.append({'path': row['path'], 'error': str(exc)})
    if p.suffix == '.py':
        source = p.read_text(encoding='utf-8-sig', errors='replace')
        scripts.append(row['path'])
        try:
            ast.parse(source, filename=row['path'])
        except SyntaxError as exc:
            syntax_errors.append({'path': row['path'], 'line': exc.lineno, 'error': exc.msg})
        if re.search(r'[A-Za-z]:[\\/]', source):
            hardcoded_scripts.append(row['path'])
    if p.suffix.lower() in {'.txt', '.md'}:
        content = p.read_text(encoding='utf-8-sig', errors='replace')
        terms = sorted(set(re.findall(r'(?i)\b(?:unapproved|unfinished|deferred|withdrawn|rejected|remaining|not built|held|not integrated|not conformed)\b', content)))
        if terms:
            docs.append({'path': row['path'], 'status_terms': terms})

# Hash native checkpoints, archives and user/art sources, excluding render caches.
hash_candidates = [p for p in files if p.suffix.lower() in {'.blend', '.blend1', '.zip', '.wav', '.fbx', '.docx'}
                   or (p.suffix.lower() in {'.png', '.jpg'} and p.relative_to(ROOT).parts[0] in {'source', 'sets', 'characters'})]
hash_rows = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in hash_candidates]
(OUT / 'source_hashes.json').write_text(json.dumps(hash_rows, indent=2), encoding='utf-8')
groups = collections.defaultdict(list)
for row in hash_rows:
    groups[row['sha256']].append(row)
duplicate_groups = [group for group in groups.values() if len(group) > 1]
(OUT / 'exact_duplicate_sources.json').write_text(json.dumps(duplicate_groups, indent=2), encoding='utf-8')

with wave.open(str(ROOT / 'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'), 'rb') as sound:
    audio = {'frames': sound.getnframes(), 'sample_rate': sound.getframerate(),
             'channels': sound.getnchannels(), 'sample_width': sound.getsampwidth(),
             'seconds': sound.getnframes() / sound.getframerate()}

git = lambda *args: subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
count = git('rev-list', '--all', '--count')
tracked = git('ls-files')
summary = {
    'captured_utc': datetime.now(timezone.utc).isoformat(), 'root': str(ROOT),
    'scope': 'All regular project files except .git, __pycache__, and this audit output. Native and media checks are separate bounded samples.',
    'files': len(files), 'bytes': sum(row['bytes'] for row in rows),
    'folders': dict(folders), 'extensions': dict(extensions),
    'json_files': extensions['.json'], 'json_parse_errors': invalid_json,
    'python_files': len(scripts), 'python_syntax_errors': syntax_errors,
    'scripts_with_absolute_windows_paths': len(hardcoded_scripts),
    'absolute_path_scripts': hardcoded_scripts,
    'hashes_computed': len(hash_rows), 'hash_bytes': sum(row['bytes'] for row in hash_rows),
    'exact_duplicate_source_groups': len(duplicate_groups),
    'duplicate_bytes_beyond_one_copy': sum(sum(r['bytes'] for r in g[1:]) for g in duplicate_groups),
    'git_commit_count': count.stdout.strip(), 'git_commit_error': count.stderr.strip(),
    'git_tracked_files': len(tracked.stdout.splitlines()),
    'gitignore_exists': (ROOT / '.gitignore').exists(),
    'audio': audio, 'status_document_index': docs,
    'live_source_mutations': False,
}
(OUT / 'census.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k not in {'absolute_path_scripts', 'status_document_index', 'folders'}}, indent=2))
