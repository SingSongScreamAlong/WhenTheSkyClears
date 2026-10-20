"""Verify the frozen v0.4.0 delivery, then package Windows and editable source.

Run only after the final export, release_final QA, captures, terrain audit and
mill movie are complete. --verify-only reads and decodes evidence without
writing a manifest or archive. The default evidence root is evidence/v040.

Movie validation: mill_movie_validation.json, or the MP4's same-stem JSON, must
record file, bytes, sha256, size, fps, decoded_frames, duration_seconds,
source_exe_sha256 and source_invocation_sha256. The last two bind the encoded
movie to release_final/mill-playthrough/invocation.json. This tool also fully
decodes the MP4 using --ffmpeg, ffmpeg on PATH, or imageio_ffmpeg.

Runtime source hashes must be present in EXPORT_IDENTITY.json, including all
current assets/story files, scripts, JSON levels, native scenes/resources,
project.godot and export_presets.cfg. All other recorded hashes are verified too.
No download, Godot invocation, Git action or publication is performed here.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib


VERSION = "0.4.0"
P = Path(__file__).resolve().parents[1]
REPO = P.parent
REPORT_FILES = {
    "smoke": "runtime_smoke.json",
    "survival": "survival_consequences.json",
    "encounters": "encounter_checks.json",
    "journey-checks": "journey_checks.json",
    "side-routes": "side_route_checks.json",
    "development-checks": "development_checks.json",
    "movement-checks": "movement_checks.json",
    "mill-checks": "mill_checks.json",
    "story-checks": "story_checks.json",
    "crossing-checks": "crossing_checks.json",
    "animation-checks": "movement_checks.json",
    "traverse": "continuous_traversal.json",
    "mill-playthrough": "mill_checks.json",
}
MOVIE_NAME = "WTSC_Mill_Playthrough_v040.mp4"
MANIFEST_NAME = "DELIVERY_MANIFEST_v040.json"
BAD_LOG = re.compile(r"(?:SCRIPT ERROR|ERROR:)")


class DeliveryError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise DeliveryError(message)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path):
    require(path.is_file(), f"Required evidence is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        require(isinstance(value, dict), f"Expected a JSON object in {path}")
        return value
    except (ValueError, UnicodeError) as error:
        raise DeliveryError(f"Invalid JSON in {path}: {error}") from error


def project_path(name: str) -> Path:
    require(isinstance(name, str), "Export identity contains a non-string path.")
    rel = PurePosixPath(name.replace("\\", "/"))
    require(not rel.is_absolute() and ".." not in rel.parts and ":" not in str(rel),
            f"Export identity contains an unsafe path: {name}")
    path = P.joinpath(*rel.parts)
    require(path.resolve().is_relative_to(P.resolve()), f"Path escapes project: {name}")
    return path


def runtime_files() -> set[Path]:
    paths = {P / "project.godot", P / "export_presets.cfg"}
    for folder in ["assets", "story"]:
        paths.update(path for path in (P / folder).rglob("*") if path.is_file())
    suffixes = {
        "scripts": {".gd", ".gdshader", ".gdshaderinc"},
        "levels": {".json"},
        "scenes": {".tscn", ".tres", ".scn", ".res"},
    }
    for folder, extensions in suffixes.items():
        paths.update(path for path in (P / folder).rglob("*")
                     if path.is_file() and path.suffix in extensions)
    return paths


def verify_source(identity):
    recorded = identity.get("source")
    require(isinstance(recorded, dict) and recorded, "Export identity has no source hashes.")
    paths = {project_path(name): expected for name, expected in recorded.items()}
    missing = sorted(path.relative_to(P).as_posix() for path in runtime_files() - paths.keys())
    require(not missing, "Runtime files were not hashed by the exporter: " + ", ".join(missing))
    for path, expected in paths.items():
        require(isinstance(expected, str) and re.fullmatch(r"[a-fA-F0-9]{64}", expected),
                f"Invalid SHA-256 in export identity: {path}")
        require(path.is_file(), f"Recorded source is missing: {path}")
        require(sha(path) == expected.lower(),
                f"Source changed after export: {path.relative_to(P)}. Re-export and re-run exact-build QA.")
    return {path.relative_to(P).as_posix(): expected.lower() for path, expected in paths.items()}


def invocation(folder: Path, executable_sha: str):
    item = load(folder / "invocation.json")
    require(item.get("exe_sha256") == executable_sha, f"Stale executable in {folder}/invocation.json")
    require(item.get("exit_code") == 0 and item.get("native_exit_code") == 0,
            f"Invocation did not exit successfully: {folder}")
    require(item.get("engine_errors") == [], f"Recorded engine errors: {folder}")
    command = item.get("command", [])
    require(isinstance(command, list) and command and "--path" not in command,
            f"Expected a packaged executable invocation, not source editor QA: {folder}")
    for name in ["engine.log", "stdout.log", "stderr.log"]:
        path = folder / name
        require(path.is_file(), f"Required QA log is missing: {path}")
        log = path.read_text(encoding="utf-8-sig", errors="replace")
        require(not BAD_LOG.search(log), f"Engine/script error in {path}")
    return item


def verify_report(folder: Path, filename: str, executable_sha: str):
    call = invocation(folder, executable_sha)
    report = load(folder / filename)
    # The unchanged side-route harness retains its v0.3 label. The invocation,
    # embedded source and native executable hash bind its newly run results.
    allowed_versions = [VERSION, "0.3.0"] if folder.name == "side-routes" else [VERSION]
    require(report.get("build", VERSION) in allowed_versions, f"Wrong report version in {folder}")
    if folder.name == "traverse":
        require(report.get("completed") is True and not report.get("failure"),
                "Continuous final journey did not complete.")
        require(sorted(set(report.get("chapters_reached", []))) == [1, 2, 3, 4, 5],
                "Continuous journey did not reach all five chapters.")
        require(float(report.get("simulated_seconds", 0)) > 0,
                "Continuous journey has no positive recorded duration.")
    else:
        checks = report.get("checks")
        require(report.get("all_passed") is True and isinstance(checks, list) and checks,
                f"No passing check set in {folder / filename}")
        require(all(isinstance(check, dict) and check.get("passed") is True for check in checks),
                f"A check failed or lacks an explicit pass in {folder / filename}")
    return report, call


def verify_animation(folder: Path, executable_sha: str, source, identity_path: Path):
    """Prefer packaged --script QA; permit an explicitly source-bound editor run."""
    call = load(folder / "invocation.json")
    command = call.get("command", [])
    require("--script" in command and "res://scripts/animation_movement_checks.gd" in command,
            "Animation fixture must invoke its actual native --script resource.")
    if call.get("exe_sha256") == executable_sha:
        return verify_report(folder, "movement_checks.json", executable_sha)
    require(call.get("exit_code") == 0 and call.get("native_exit_code") == 0
            and call.get("engine_errors") == [], "Source animation fixture did not pass cleanly.")
    require(call.get("export_identity_sha256") == sha(identity_path),
            "Editor fallback animation fixture must bind export_identity_sha256 to this export identity.")
    require(call.get("source") == source,
            "Editor fallback animation fixture must record the full matching export source hash map.")
    engine = Path(command[0])
    require(engine.is_file() and call.get("exe_sha256") == sha(engine),
            "Animation fixture's editor binary differs from its invocation hash.")
    for name in ["engine.log", "stdout.log", "stderr.log"]:
        path = folder / name
        require(path.is_file() and not BAD_LOG.search(path.read_text(encoding="utf-8-sig", errors="replace")),
                f"Missing or failing source animation log: {path}")
    report = load(folder / "movement_checks.json")
    checks = report.get("checks")
    require(report.get("all_passed") is True and isinstance(checks, list) and checks
            and all(isinstance(check, dict) and check.get("passed") is True for check in checks),
            "Source animation fixture has a missing or failed check.")
    return report, call


def png_size(path: Path):
    """Check chunk CRCs and decompress an 8-bit RGB(A) screenshot completely."""
    require(path.is_file(), f"Missing native capture: {path}")
    compressed = bytearray()
    header = None
    ended = False
    with path.open("rb") as stream:
        require(stream.read(8) == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature: {path}")
        while not ended:
            length_bytes = stream.read(4)
            require(len(length_bytes) == 4, f"Truncated PNG: {path}")
            length = struct.unpack(">I", length_bytes)[0]
            require(length <= 128 * 1024 * 1024, f"Unexpected PNG chunk size: {path}")
            kind = stream.read(4)
            data = stream.read(length)
            crc_bytes = stream.read(4)
            require(len(data) == length and len(crc_bytes) == 4, f"Truncated PNG chunk: {path}")
            require(zlib.crc32(kind + data) & 0xFFFFFFFF == struct.unpack(">I", crc_bytes)[0],
                    f"PNG chunk checksum failed: {path}")
            if kind == b"IHDR":
                require(header is None and length == 13, f"Invalid PNG header: {path}")
                header = struct.unpack(">IIBBBBB", data)
            elif kind == b"IDAT":
                compressed.extend(data)
            elif kind == b"IEND":
                ended = True
        require(not stream.read(1), f"Unexpected bytes after PNG end: {path}")
    require(header is not None, f"PNG lacks a header: {path}")
    width, height, depth, color, compression, filtering, interlace = header
    require(depth == 8 and color in [2, 6] and compression == filtering == interlace == 0,
            f"Expected an 8-bit non-interlaced RGB/RGBA native screenshot: {path}")
    channels = 3 if color == 2 else 4
    stride = 1 + width * channels
    decoded = zlib.decompress(compressed)
    require(len(decoded) == stride * height, f"Incorrect decoded PNG size: {path}")
    require(all(decoded[row * stride] <= 4 for row in range(height)), f"Invalid PNG row filter: {path}")
    return [width, height]


def find_ffmpeg(explicit: str | None):
    if explicit:
        require(Path(explicit).is_file(), f"FFmpeg does not exist: {explicit}")
        return explicit
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError) as error:
        raise DeliveryError("Full movie decoding requires ffmpeg on PATH, --ffmpeg PATH, or imageio-ffmpeg.") from error


def verify_movie(evidence: Path, final: Path, executable_sha: str, report, ffmpeg: str | None):
    movie = evidence / MOVIE_NAME
    require(movie.is_file(), f"Final mill movie is missing: {movie}")
    alternatives = [evidence / "mill_movie_validation.json", movie.with_suffix(".json")]
    record_path = next((path for path in alternatives if path.is_file()), alternatives[0])
    video = load(record_path)
    recording = report.get("recording", {})
    require(recording.get("enabled") is True, "Final mill playthrough did not enable recording.")
    expected_frames = recording.get("frames", 0)
    fps = recording.get("fps", 0)
    require(isinstance(expected_frames, int) and expected_frames > 0 and fps > 0,
            "Final mill recording has invalid frame count or FPS.")
    require(video.get("file", "").replace("\\", "/").split("/")[-1] == MOVIE_NAME,
            f"Validation references a different movie: {record_path}")
    require(video.get("sha256") == sha(movie) and video.get("bytes") == movie.stat().st_size,
            "Mill movie hash/length differs from its validation record.")
    require(video.get("source_exe_sha256", video.get("exe_sha256")) == executable_sha,
            "Movie validation must bind source_exe_sha256 to the final executable.")
    require(video.get("source_invocation_sha256") == sha(final / "mill-playthrough/invocation.json"),
            "Movie validation must bind source_invocation_sha256 to the final mill recording invocation.")
    require(video.get("decoded_frames") == expected_frames and video.get("fps") == fps,
            "Movie validation frame count/FPS differs from native recording.")
    size = video.get("size")
    require(isinstance(size, list) and len(size) == 2 and all(isinstance(n, int) and n > 0 for n in size),
            "Movie validation must include a positive [width,height] size.")
    duration = video.get("duration_seconds", 0)
    require(isinstance(duration, (int, float)) and math.isclose(duration, expected_frames / fps, abs_tol=1 / fps),
            "Movie duration differs from its recorded frame count/FPS.")
    command = [find_ffmpeg(ffmpeg), "-v", "error", "-xerror", "-i", str(movie),
               "-map", "0:v:0", "-an", "-f", "null", "-", "-progress", "pipe:1", "-nostats"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=300, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    frames = [int(line.split("=", 1)[1]) for line in result.stdout.splitlines()
              if re.fullmatch(r"frame=\d+", line)]
    require(result.returncode == 0 and not result.stderr.strip() and frames and max(frames) == expected_frames,
            "Full mill movie decode failed or produced a different frame count: " + result.stderr[-1200:])
    return video, record_path


def verify_terrain(evidence: Path):
    path = evidence / "terrain_polygon_audit_current.json"
    audit = load(path)
    require(audit.get("all_passed") is True and audit.get("mode") == "current"
            and audit.get("failed_polygons") == 0 and audit.get("checks", 0) > 0,
            "Current terrain polygon audit is not passing.")
    chapters = audit.get("chapters", [])
    require(sorted(row.get("chapter", 0) for row in chapters) == [1, 2, 3, 4, 5]
            and all(row.get("failed_polygons") == 0 for row in chapters),
            "Terrain audit must cover all five chapters without failed polygons.")
    dependencies = [P / "scripts/world.gd", *sorted((P / "levels").glob("*.json")),
                    P / "tools/audit_terrain_v040.gd"]
    binding_path = path.with_suffix(".identity.json")
    binding = load(binding_path) if binding_path.exists() else audit
    if isinstance(binding.get("source"), dict):
        require(binding.get("report_sha256", sha(path)) == sha(path), "Terrain audit identity binds an old report.")
        for dependency in dependencies:
            require(binding["source"].get(dependency.relative_to(P).as_posix()) == sha(dependency),
                    f"Terrain audit source identity is stale: {dependency}")
    else:
        require(all(path.stat().st_mtime >= dependency.stat().st_mtime for dependency in dependencies),
                "Terrain audit predates world/level/audit-tool edits. Re-run audit_terrain_v040.gd after freeze "
                "or supply terrain_polygon_audit_current.identity.json with matching source/report hashes.")
    return audit, [path] + ([binding_path] if binding_path.exists() else [])


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def normalized_export(data: bytes):
    text = data.decode("utf-8-sig")
    for kind in ["debug", "release"]:
        text, count = re.subn(r'^custom_template/' + kind + r'=.*$',
                              'custom_template/' + kind + '=""', text, flags=re.MULTILINE)
        require(count == 1, f"Expected exactly one custom_template/{kind} setting.")
    return text.encode("utf-8")


def source_entries(evidence: Path, selected_reports: list[Path], manifest_data: bytes):
    entries: dict[str, Path | bytes] = {}
    for folder in ["assets", "scripts", "scenes", "levels", "story", "previous"]:
        for path in (P / folder).rglob("*"):
            if path.is_file() and not any(part in [".godot", "__pycache__", "motion_frames", "build"] for part in path.parts):
                require(not path.is_symlink(), f"Source archive cannot include a symlink: {path}")
                require(path.suffix.lower() not in [".exe", ".zip", ".tpz", ".pyc", ".tmp"],
                        f"Unexpected generated binary/archive in source folder: {path}")
                entries[path.relative_to(P).as_posix()] = path
    for path in P.iterdir():
        if path.is_file() and (path.suffix.lower() in [".txt", ".cmd"] or path.name in ["project.godot", "export_presets.cfg", ".gitignore"]):
            entries[path.name] = path
    for path in (P / "tools").rglob("*"):
        if path.is_file() and not any(part in ["godot", "__pycache__"] for part in path.relative_to(P / "tools").parts):
            if path.suffix in [".py", ".gd", ".uid"] or path.name in [".gdignore", "ENGINE_PROVENANCE.json", "SHA512-SUMS.txt"] or path.name.startswith("requirements"):
                entries[path.relative_to(P).as_posix()] = path
    for path in (REPO / "docs").rglob("*"):
        if path.is_file() and path.suffix.lower() in [".md", ".txt", ".json", ".docx"]:
            entries[path.relative_to(REPO).as_posix()] = path
    for relative in ["character_sources/.gdignore", "character_sources/SOURCE_RECEIPTS.json",
                     "character_sources/QUATERNIUS_CURRENT_LICENSE.html", "evidence/.gdignore",
                     "character_sources/kenney-impact-sounds/RECEIPT.json"]:
        path = P / relative
        if path.is_file():
            entries[relative] = path
    entries["export_presets.cfg"] = normalized_export((P / "export_presets.cfg").read_bytes())
    for path in selected_reports:
        entries[path.relative_to(P).as_posix()] = path
    entries[(evidence / MANIFEST_NAME).relative_to(P).as_posix()] = manifest_data
    entries["README_SOURCE.txt"] = (
        "WHEN THE SKY CLEARS - EDITABLE SOURCE 0.4.0\n\n"
        "Import project.godot at this archive's root with Godot 4.6 Standard.\n"
        "This source ZIP flattens the repository's game/ folder. Paths beginning\n"
        "game/ in repository-reference documentation therefore refer to this root.\n"
        "Use matching standard Godot export templates; custom template paths are cleared.\n"
        "Python helpers have their own dependencies; the game needs no Python.\n"
        "Engine binaries, import caches, raw vendor packs, diagnostic captures and\n"
        "intermediate movie frames are excluded. The repository retains review media.\n"
        "The delivery manifest identifies the tested executable and original source.\n"
        "https://github.com/SingSongScreamAlong/WhenTheSkyClears\n"
    ).encode("utf-8")
    return entries


def make_archive(target: Path, entries: dict[str, Path | bytes]):
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    os.close(handle)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, item in sorted(entries.items()):
                require(not name.startswith("/") and ".." not in PurePosixPath(name).parts,
                        f"Unsafe archive member: {name}")
                if isinstance(item, bytes):
                    archive.writestr(name, item)
                else:
                    archive.write(item, name)
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            require(bad is None, f"ZIP CRC failed: {target.name}: {bad}")
            require(len(archive.namelist()) == len(set(archive.namelist())), "Duplicate ZIP members.")
        return temporary
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write(path: Path, data: bytes):
    handle, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="read/check/decode only; write nothing")
    parser.add_argument("--evidence-root", type=Path, default=P / "evidence/v040")
    parser.add_argument("--output-dir", type=Path, default=P)
    parser.add_argument("--ffmpeg", help="explicit existing ffmpeg executable")
    args = parser.parse_args()
    evidence = args.evidence_root.resolve()
    require(evidence.is_relative_to(P.resolve()), "Evidence root must be inside this game project.")
    final = evidence / "release_final"
    executable = P / "build/v0.4.0/When the Sky Clears.exe"
    identity_path = evidence / "EXPORT_IDENTITY.json"
    identity = load(identity_path)
    require(identity.get("build") == VERSION and executable.is_file(), "Final v0.4.0 executable/export identity is missing.")
    require(project_path(identity.get("executable", "")) == executable, "Export identity references a different executable path.")
    executable_sha = sha(executable)
    require(identity.get("sha256") == executable_sha and identity.get("bytes") == executable.stat().st_size,
            "Final executable differs from export identity.")
    source = verify_source(identity)
    reports, invocations, selected = {}, {}, [identity_path]
    for scenario, filename in REPORT_FILES.items():
        if scenario == "animation-checks":
            report, call = verify_animation(final / scenario, executable_sha, source, identity_path)
        else:
            report, call = verify_report(final / scenario, filename, executable_sha)
        reports[scenario], invocations[scenario] = report, call
        selected += [final / scenario / filename, final / scenario / "invocation.json"]
    capture_call = invocation(final / "capture-v040", executable_sha)
    selected.append(final / "capture-v040/invocation.json")
    captures = sorted((final / "capture-v040").glob("*.png"))
    require(len(captures) == 9, f"Expected exactly nine final native PNG captures, found {len(captures)}.")
    graphics = []
    for path in captures:
        size = png_size(path)
        require(size == [3840, 2160], f"Final native capture is not 3840x2160: {path}")
        graphics.append(dict(file=path.relative_to(P).as_posix(), size=size, sha256=sha(path),
                             scope="Staged character close view" if "close" in path.stem else "Native rendered scene capture"))
    movie, validation_path = verify_movie(evidence, final, executable_sha, reports["mill-playthrough"], args.ffmpeg)
    selected.append(validation_path)
    terrain, terrain_paths = verify_terrain(evidence)
    selected += terrain_paths
    levels = [load(P / f"levels/{number:02}.json") for number in range(1, 6)]
    check_counts = {name: len(report["checks"]) for name, report in reports.items()
                    if "checks" in report and name not in ["mill-playthrough", "animation-checks"]}
    manifest = dict(build=VERSION, created_at_utc=datetime.now(timezone.utc).isoformat(),
        executable=dict(file=executable.relative_to(P).as_posix(), bytes=executable.stat().st_size, sha256=executable_sha),
        source=source, checks=check_counts, total_functional_checks=sum(check_counts.values()),
        animation_fixture=dict(checks=len(reports["animation-checks"]["checks"]),
            all_passed=True, excluded_from_functional_total=True,
            overlaps_baseline_movement_checks=True,
            invocation_scope="Final packaged executable" if invocations["animation-checks"]["exe_sha256"] == executable_sha
                else "Native editor fixture bound to the full final export source map"),
        journey=reports["traverse"],
        journey_design=dict(route_units=sum(level["width"] for level in levels), previous_route_units=56000,
            physical_forks=sum(len(level.get("branch_routes", [])) for level in levels),
            timed_hazard_lanes=sum(len(level.get("hazard_lanes", [])) for level in levels),
            held_relay_clear_brace_actions=sum(item.get("kind") in ["relay", "clear", "brace"]
                for level in levels for item in level.get("interact", []))),
        invocations={name: dict(file=(final / name / "invocation.json").relative_to(P).as_posix(),
            sha256=sha(final / name / "invocation.json"), **call) for name, call in invocations.items()},
        graphics=dict(captures=graphics, invocation=capture_call), mill_movie=movie,
        terrain_geometry_audit=terrain,
        evidence_files={path.relative_to(P).as_posix(): sha(path) for path in selected},
        source_archive_transform=dict(file="export_presets.cfg", operation="Clear debug/release custom templates for installed Godot 4.6 templates.",
            original_sha256=sha(P / "export_presets.cfg"),
            archive_sha256=hashlib.sha256(normalized_export((P / "export_presets.cfg").read_bytes())).hexdigest()),
        notes=["Full journey, targeted fixtures and rendered scene studies have separate scopes.",
            "Mill movie uses native input and physics after explicit initial fixture setup; it is not the full campaign.",
            "The mill recording repeats checks for media verification; its checks are not added twice to the functional total.",
            "Packaged gameplay invocations identify the same final executable SHA-256; any editor fallback animation fixture separately binds the complete source identity.",
            "The expanded animation fixture includes baseline movement checks and is reported separately without inflating the functional total.",
            "Source ZIP keeps project.godot at archive root; repository game/ paths are flattened.",
            "Source export-template normalization is the declared archive-only configuration change.",
            "Route length is measured authored data; human playtime and artistic approval are not established.",
            "Expanded development build; AAA quality remains a production target."])
    verify_source(identity)
    require(sha(executable) == executable_sha, "Executable changed during verification.")
    summary = dict(build=VERSION, executable_sha256=executable_sha, checks=check_counts,
                   total_functional_checks=sum(check_counts.values()), traversal_completed=True,
                   captures=len(captures), movie_decoded_frames=movie["decoded_frames"])
    if args.verify_only:
        print("V040_VERIFIED " + json.dumps(summary))
        return 0
    manifest_data = json_bytes(manifest)
    native_entries: dict[str, Path | bytes] = {
        executable.name: executable,
        "BUILD_MANIFEST.json": manifest_data,
        "READ_ME.txt": ("WHEN THE SKY CLEARS - WINDOWS DEVELOPMENT 0.4.0\n"
            "Extract the whole ZIP, then run When the Sky Clears.exe.\n"
            "Godot and Python are not needed to play.\n"
            "MILL_PLAYTEST.cmd opens an isolated, unsaved mill preview.\n"
            "FREIGHT_CROSSING.cmd opens a rehearsal with a separate save.\n"
            "Development-note asset/tool paths refer to the editable source.\n\n" +
            (P / "DEVELOPMENT_v0.4.0.txt").read_text(encoding="utf-8-sig")).encode("utf-8"),
        "JOURNEY_DESIGN.txt": P / "JOURNEY_v0.4.0.txt",
        "MILL_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --mill-preview\r\n',
        "FREIGHT_CROSSING.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --freight-crossing\r\n',
    }
    licenses = list((REPO / "docs/licenses").glob("*.txt"))
    require(licenses and (REPO / "docs/licenses/GODOT-LICENSE.txt").is_file(), "Distribution license notices are missing.")
    native_entries.update({"licenses/" + path.name: path for path in licenses})
    editable_entries = source_entries(evidence, selected, manifest_data)
    outputs = [
        (args.output_dir / f"When_The_Sky_Clears_Windows_v{VERSION}.zip", native_entries),
        (args.output_dir / f"When_The_Sky_Clears_Editable_Source_v{VERSION}.zip", editable_entries),
    ]
    prepared = []
    try:
        for target, entries in outputs:
            prepared.append((target, make_archive(target, entries)))
        verify_source(identity)
        require(sha(executable) == executable_sha, "Executable changed while packaging.")
        for target, temporary in prepared:
            os.replace(temporary, target)
        atomic_write(evidence / MANIFEST_NAME, manifest_data)
        artifacts = [dict(file=target.name, bytes=target.stat().st_size, sha256=sha(target)) for target, _ in outputs]
        atomic_write(evidence / "RELEASE_ARTIFACTS_v040.json", json_bytes(artifacts))
    finally:
        for _, temporary in prepared:
            temporary.unlink(missing_ok=True)
    print("V040_DELIVERY_READY " + json.dumps(dict(**summary, artifacts=artifacts)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeliveryError, OSError, ValueError, zlib.error, subprocess.TimeoutExpired, zipfile.BadZipFile) as error:
        print(f"v0.4.0 delivery verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
