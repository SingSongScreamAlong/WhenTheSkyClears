"""Isolated v0.4.2 Windows export, native QA and delivery packaging.

Examples, from the repository root:
  python game/tools/build_v042.py export
  python game/tools/build_v042.py test all
  python game/tools/build_v042.py test capture
  python game/tools/build_v042.py verify
  python game/tools/build_v042.py package

Artifacts stay under build/v0.4.2 and evidence/v042. Existing runtime flags and
report version labels are retained; wrapper metadata identifies this delivery as
0.4.2 without rewriting runtime source. Animation QA runs as a separately bound
native source fixture. Existing v0.4.0 and v0.4.1 artifacts remain untouched.
Each test removes only its recognized direct output files and records a fresh
per-run hash inventory. Verification rejects missing or subsequently changed outputs.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

# Reuse only version-independent validators/ZIP primitives; never call the
# frozen v0.4.0 tool's main(), version checks, media paths or archive selector.
from package_v040 import (DeliveryError, atomic_write, invocation, json_bytes,
                          load, make_archive, normalized_export, png_size,
                          require, runtime_files, sha)

VERSION = "0.4.2"
P = Path(__file__).resolve().parents[1]
DOCS = P / "docs" if (P / "docs").is_dir() else P.parent / "docs"
E = P / "evidence/v042"
B = P / "build/v0.4.2"
EXE = B / "When the Sky Clears.exe"
IDENTITY = E / "EXPORT_IDENTITY.json"
REPORTS = {
    "smoke": "runtime_smoke.json", "survival": "survival_consequences.json",
    "encounters": "encounter_checks.json", "journey-checks": "journey_checks.json",
    "side-routes": "side_route_checks.json", "development-checks": "development_checks.json",
    "movement-checks": "movement_checks.json", "mill-checks": "mill_checks.json",
    "story-checks": "story_checks.json", "crossing-checks": "crossing_checks.json",
    "refinement-checks": "refinement_checks.json",
    "sluice-checks": "sluice_checks.json", "craft-checks": "craft_checks.json",
    "world-craft-checks": "world_craft_checks.json",
    "traverse": "continuous_traversal.json", "animation-checks": "movement_checks.json",
}
EXTRAS = ["capture", "motion", "mill-playthrough", "sluice-playthrough", "craft-playthrough", "crossing-capture"]
CAPTURE_NAMES = [
    "01_mill_gardens.png", "02_canal_lower_route.png", "03_canal_upper_route.png",
    "04_signal_yard.png", "05_school_gallery.png", "06_living_terraces.png",
    "07_character_close_study.png", "08_interactive_mill_bridge.png",
    "09_interactive_wheel_approach.png", "10_canal_pump_work.png",
    "11_canal_sluice_drained.png", "12_supplies_close_study.png",
    "13_counterweight_wait.png", "14_counterweight_crossing.png",
    "15_counterweight_reunion.png",
    "16_logging_counterweight.png",
]
SLUICE_CAPTURE_NAMES = CAPTURE_NAMES[12:15]
FRAME_DIRS = {"motion": "motion_frames", "mill-playthrough": "motion_frames",
              "sluice-playthrough": "sluice_motion_frames", "craft-playthrough": "craft_motion_frames"}


def snapshot():
    files = runtime_files()
    # Resource UID sidecars belong to the same frozen source snapshot, including
    # newly imported scripts/scenes. Assets and story are already recursive.
    for folder in ["scripts", "scenes", "levels"]:
        files.update(path for path in (P / folder).rglob("*.uid") if path.is_file())
    return {path.relative_to(P).as_posix(): sha(path) for path in sorted(files)}


def prepare_outputs(folder, kind, capture_count):
    """Remove only direct, recognized outputs from this one scenario directory."""
    require(folder.resolve().is_relative_to(E.resolve()) and folder.name == kind,
            f"Refusing output cleanup outside the intended scenario directory: {folder}")
    if kind == "capture":
        require(0 < capture_count <= len(CAPTURE_NAMES), "Capture count exceeds the known native capture list.")
        expected = CAPTURE_NAMES[:capture_count] + ["sluice_capture.json"]
        cleanup = CAPTURE_NAMES + ["sluice_capture.json"]
    else:
        filename = REPORTS.get(kind, {"motion": "motion_review.json", "mill-playthrough": "mill_checks.json",
                                     "sluice-playthrough": "sluice_checks.json",
                                     "craft-playthrough": "craft_checks.json",
                                     "crossing-capture": "capture_report.json"}.get(kind))
        require(filename is not None, f"Unknown scenario output set: {kind}")
        expected = [filename]
        cleanup = [filename]
    folder.mkdir(parents=True, exist_ok=True)
    paths = [folder / name for name in cleanup + ["invocation.json", "timeout.json"]]
    if kind == "crossing-capture":
        paths += [path for path in folder.glob("*.png") if path.name == "crossing_arrival.png"
                  or re.fullmatch(r"\d{2}_[A-Za-z0-9_-]+\.png", path.name)]
    for path in paths:
        require(path.parent.resolve() == folder.resolve() and not path.is_symlink(),
                f"Refusing to remove an indirect scenario output: {path}")
        if path.exists():
            require(path.is_file(), f"Expected an output file, found another object: {path}")
            path.unlink()
    if kind in FRAME_DIRS:
        sequence = folder / FRAME_DIRS[kind]
        require(not sequence.is_symlink() and sequence.resolve().parent == folder.resolve(),
                f"Refusing an indirect native frame directory: {sequence}")
        if sequence.exists():
            require(sequence.is_dir(), f"Expected a native frame directory: {sequence}")
            for path in sequence.glob("*.jpg"):
                if re.fullmatch(r"\d{4,5}\.jpg", path.name):
                    require(path.is_file() and not path.is_symlink(), f"Refusing indirect frame cleanup: {path}")
                    path.unlink()
    return [folder / name for name in expected]


def verify_outputs(folder, call, required_names):
    inventory = call.get("generated_outputs")
    require(isinstance(inventory, dict) and re.fullmatch(r"[a-f0-9]{32}", call.get("run_id", "")),
            f"Invocation lacks a fresh per-run output inventory: {folder}")
    for name in required_names:
        require(name in inventory, f"Invocation did not generate its required output: {folder / name}")
    for name, recorded in inventory.items():
        require(Path(name).name == name and "/" not in name and "\\" not in name,
                f"Invalid generated output name in {folder}")
        path = folder / name
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == recorded.get("bytes")
                and sha(path) == recorded.get("sha256"), f"Scenario output changed after its invocation: {path}")
    return inventory


def validate_capture(folder):
    report = load(folder / "sluice_capture.json")
    require(report.get("all_states_reached") is True
            and report.get("screenshots") == SLUICE_CAPTURE_NAMES,
            "Sluice capture did not reach the authored wait, crossing and reunion states.")
    return report


def verify_frame_sequence(folder, call, directory, frames, digits=5):
    require(directory in FRAME_DIRS.values() and isinstance(frames, int) and frames > 0,
            "Invalid native frame sequence description.")
    sequence = folder / directory
    require(sequence.is_dir() and not sequence.is_symlink() and sequence.resolve().parent == folder.resolve(),
            f"Missing or indirect native frame directory: {sequence}")
    inventory = call.get("generated_frame_sequences", {}).get(directory)
    names = [f"{index:0{digits}d}.jpg" for index in range(frames)]
    require(isinstance(inventory, dict) and set(inventory) == set(names),
            f"Native frame inventory does not match the recorded range: {sequence}")
    require({path.name for path in sequence.glob("*.jpg")} == set(names),
            f"Native frame directory contains missing or stale JPGs: {sequence}")
    for name in names:
        path, recorded = sequence / name, inventory[name]
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == recorded.get("bytes")
                and sha(path) == recorded.get("sha256"), f"Native frame changed after its invocation: {path}")
    return [sequence / name for name in names]


def run(command, folder, timeout, metadata=None, output_paths=None):
    folder.mkdir(parents=True, exist_ok=True)
    binary_sha = sha(Path(command[0]))
    started = time.monotonic()
    try:
        result = subprocess.run(command, cwd=P, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        stdout, stderr, native_code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode("utf-8", "replace") if isinstance(value, bytes) else value or ""
        stdout, stderr, native_code = text(error.stdout), text(error.stderr), 124
    errors = [line for line in (stdout + "\n" + stderr).splitlines()
              if "ERROR:" in line or "SCRIPT ERROR" in line]
    if sha(Path(command[0])) != binary_sha:
        errors.append("ERROR: executable changed while the process was running")
    inventory = {}
    generated = list(output_paths or [])
    if folder.name == "crossing-capture":
        generated += [path for path in folder.glob("*.png") if path.name == "crossing_arrival.png"
                      or re.fullmatch(r"\d{2}_[A-Za-z0-9_-]+\.png", path.name)]
    for path in generated:
        require(path.parent.resolve() == folder.resolve(), "Generated output must be a direct scenario file.")
        if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
            errors.append("ERROR: expected fresh scenario output is missing: " + path.name)
        else:
            inventory[path.name] = dict(bytes=path.stat().st_size, sha256=sha(path))
    sequences = {}
    if folder.name in FRAME_DIRS:
        directory = FRAME_DIRS[folder.name]
        sequence = folder / directory
        recorded = {}
        if sequence.is_dir() and not sequence.is_symlink():
            for path in sequence.glob("*.jpg"):
                if not re.fullmatch(r"\d{4,5}\.jpg", path.name) or path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
                    errors.append("ERROR: invalid native frame output: " + path.name)
                else:
                    recorded[path.name] = dict(bytes=path.stat().st_size, sha256=sha(path))
        if not recorded:
            errors.append("ERROR: expected fresh native frame sequence is missing: " + directory)
        sequences[directory] = recorded
    record = dict(build=VERSION, command=command, exe_sha256=binary_sha,
        run_id=uuid.uuid4().hex, generated_outputs=inventory,
        generated_frame_sequences=sequences,
        exit_code=native_code or (1 if errors else 0), native_exit_code=native_code,
        elapsed_seconds=round(time.monotonic() - started, 2), engine_errors=errors,
        **(metadata or {}))
    atomic_write(folder / "stdout.log", stdout.encode("utf-8"))
    atomic_write(folder / "stderr.log", stderr.encode("utf-8"))
    atomic_write(folder / "invocation.json", json_bytes(record))
    require(record["exit_code"] == 0, f"Native operation failed: {folder}\n"
            + "\n".join(errors[-4:]) + "\n" + stderr[-1800:])
    return record


def frozen():
    identity = load(IDENTITY)
    require(identity.get("build") == VERSION, "Missing v0.4.2 export identity; run export after freezing the source.")
    require(EXE.is_file() and identity.get("sha256") == sha(EXE)
            and identity.get("bytes") == EXE.stat().st_size, "v0.4.2 executable changed after export.")
    require(identity.get("source") == snapshot(), "Runtime source changed after export. Re-export and repeat final QA.")
    return identity


def export(engine, timeout):
    require(engine.is_file(), "Missing portable Godot engine; run setup_godot.py first.")
    for name in ["windows_debug_x86_64.exe", "windows_release_x86_64.exe"]:
        require((P / "tools" / name).is_file(), f"Missing portable template: {name}")
    B.mkdir(parents=True, exist_ok=True)
    E.mkdir(parents=True, exist_ok=True)
    preset = P / "export_presets.cfg"
    original = preset.read_bytes()
    run([str(engine), "--headless", "--path", str(P), "--editor", "--import", "--quit",
         "--log-file", str(E / "export/import/engine.log")], E / "export/import", timeout)
    require(preset.read_bytes() == original, "Preset changed during import; export cancelled.")
    before = snapshot()
    text = original.decode("utf-8-sig")
    overrides = {
        "custom_template/debug": '"res://tools/windows_debug_x86_64.exe"',
        "custom_template/release": '"res://tools/windows_release_x86_64.exe"',
        "application/product_version": '"0.4.2.0"', "application/file_version": '"0.4.2.0"',
    }
    for key, value in overrides.items():
        text, count = re.subn(r"^" + re.escape(key) + r"=[^\r\n]*", key + "=" + value,
                              text, flags=re.MULTILINE)
        require(count == 1, f"Expected one export preset field: {key}")
    temporary_exe = B / "When the Sky Clears.building.exe"
    try:
        preset.write_bytes(text.encode("utf-8"))
        run([str(engine), "--headless", "--path", str(P), "--export-release", "Windows Desktop",
             str(temporary_exe), "--log-file", str(E / "export/windows/engine.log")],
            E / "export/windows", timeout)
    finally:
        preset.write_bytes(original)
    require(snapshot() == before, "Source changed during export; final executable was not published.")
    require(temporary_exe.is_file() and temporary_exe.stat().st_size > 0, "Godot produced no standalone executable.")
    os.replace(temporary_exe, EXE)
    identity = dict(build=VERSION, created_at_utc=datetime.now(timezone.utc).isoformat(),
        executable=EXE.relative_to(P).as_posix(), bytes=EXE.stat().st_size, sha256=sha(EXE), source=before,
        export_overrides=overrides, preset_restored_byte_for_byte=True,
        scope="v0.4.2 delivery wrapper; runtime report labels and save behavior are not rewritten by this tool.")
    atomic_write(IDENTITY, json_bytes(identity))
    print("V042_EXPORTED", identity["bytes"], identity["sha256"])


def test(args):
    kinds = list(REPORTS) if args.kinds == ["all"] else args.kinds
    require("all" not in kinds, "Use all alone, or name individual test kinds.")
    identity = None if args.source else frozen()
    for kind in kinds:
        require(kind in REPORTS or kind in EXTRAS, f"Unknown test kind: {kind}")
        before = snapshot()
        if identity:
            require(before == identity["source"], "Source changed before QA.")
        source_fixture = args.source or kind == "animation-checks"
        binary = args.engine if source_fixture else EXE
        require(binary.is_file(), f"Missing executable: {binary}")
        tag = args.tag or ("source" if args.source else "release_final")
        require(re.fullmatch(r"[A-Za-z0-9_-]+", tag), "Evidence tag must be one simple directory name.")
        folder = E / tag / kind
        command = [str(binary)] + (["--path", str(P)] if source_fixture else [])
        visual = kind in EXTRAS
        command += ["--position", "-20000,-20000"] if visual else ["--headless"]
        if kind == "motion":
            require((P / "scenes/animation_review.tscn").is_file(), "Missing dedicated character review scene.")
            command += ["res://scenes/animation_review.tscn"]
        if kind == "animation-checks":
            command += ["--script", "res://scripts/animation_movement_checks.gd"]
        fps = 30 if kind in ["motion", "mill-playthrough", "sluice-playthrough", "craft-playthrough"] else 60
        flag = args.capture_flag if kind == "capture" else (
            kind.replace("-playthrough", "-checks") if kind in ["mill-playthrough", "sluice-playthrough", "craft-playthrough"] else kind)
        require(re.fullmatch(r"[A-Za-z0-9_-]+", flag), "Capture flag must be a simple Godot user flag.")
        command += ["--fixed-fps", str(fps), "--log-file", str(folder / "engine.log"),
                    "--", "--evidence-dir", str(folder), "--" + flag]
        if kind == "mill-playthrough":
            command += ["--record-mill"]
        if kind == "sluice-playthrough":
            command += ["--record-sluice"]
        if kind == "craft-playthrough":
            command += ["--record-craft"]
        metadata = dict(scope="Native source fixture" if source_fixture else "Standalone v0.4.2 executable")
        if kind == "motion":
            metadata["review_scene"] = "res://scenes/animation_review.tscn"
        if source_fixture:
            metadata["source"] = before
            if identity:
                metadata["export_identity_sha256"] = sha(IDENTITY)
        outputs = prepare_outputs(folder, kind, args.expected_captures)
        record = run(command, folder, args.timeout, metadata, outputs)
        if kind == "capture":
            try:
                validate_capture(folder)
            except DeliveryError as error:
                record["exit_code"] = 1
                record["semantic_errors"] = [str(error)]
                atomic_write(folder / "invocation.json", json_bytes(record))
                raise
        require(snapshot() == before, f"Runtime source changed during {kind}; discard this QA result.")
        print("V042_TEST", kind, record["exit_code"], record["elapsed_seconds"])


def verify(expected_captures):
    identity = frozen()
    final = E / "release_final"
    reports, selected, counts = {}, [IDENTITY], {}
    for kind, filename in REPORTS.items():
        folder = final / kind
        report = load(folder / filename)
        if kind == "animation-checks":
            call = load(folder / "invocation.json")
            require(call.get("source") == identity["source"]
                    and call.get("export_identity_sha256") == sha(IDENTITY), "Animation source binding is stale.")
            require(call.get("exit_code") == call.get("native_exit_code") == 0
                    and call.get("engine_errors") == [], "Animation source fixture did not exit cleanly.")
            require(sha(Path(call["command"][0])) == call.get("exe_sha256"), "Animation engine hash changed.")
            for log in ["engine.log", "stdout.log", "stderr.log"]:
                text = (folder / log).read_text(encoding="utf-8", errors="replace")
                require("ERROR:" not in text and "SCRIPT ERROR" not in text, f"Error in {folder / log}")
        else:
            call = invocation(folder, identity["sha256"])
        verify_outputs(folder, call, [filename])
        if kind == "traverse":
            require(report.get("completed") is True and not report.get("failure")
                    and sorted(set(report.get("chapters_reached", []))) == [1, 2, 3, 4, 5], "Journey did not complete all five chapters.")
        else:
            checks = report.get("checks", [])
            require(report.get("all_passed") is True and isinstance(checks, list) and checks
                    and all(check.get("passed") is True for check in checks), f"Unpassed {kind} report.")
            if kind != "animation-checks":
                counts[kind] = len(checks)
        reports[kind] = report
        selected += [folder / filename, folder / "invocation.json"]
    capture_call = invocation(final / "capture", identity["sha256"])
    selected.append(final / "capture/invocation.json")
    captures = sorted((final / "capture").glob("*.png"))
    require(len(captures) == expected_captures, f"Expected {expected_captures} native captures, found {len(captures)}.")
    capture_inventory = verify_outputs(final / "capture", capture_call,
                                       [path.name for path in captures] + ["sluice_capture.json"])
    sluice_capture = validate_capture(final / "capture")
    selected.append(final / "capture/sluice_capture.json")
    require({name for name in capture_inventory if name.endswith(".png")} == {path.name for path in captures},
            "Capture directory contains PNGs not generated by its current invocation.")
    for path in captures:
        require(png_size(path) == [3840, 2160], f"Capture is not native 4K: {path}")
    manifest = dict(build=VERSION, created_at_utc=datetime.now(timezone.utc).isoformat(),
        executable={key: identity[key] for key in ["executable", "bytes", "sha256"]}, source=identity["source"],
        export_overrides=identity["export_overrides"], checks=counts, total_functional_checks=sum(counts.values()),
        animation_fixture=dict(checks=len(reports["animation-checks"]["checks"]), excluded_from_functional_total=True,
                               scope="Native source fixture bound to the full export source identity; includes baseline movement checks."),
        journey=reports["traverse"],
        sluice_capture=sluice_capture,
        captures=[dict(file=path.relative_to(P).as_posix(), sha256=sha(path), size=[3840, 2160],
                       scope="Staged close view" if "close" in path.stem else "Native rendered scene") for path in captures],
        evidence={path.relative_to(P).as_posix(): sha(path) for path in selected},
        runtime_report_labels={kind: report.get("build", report.get("version")) for kind, report in reports.items()},
        notes=["v0.4.2 identifies this wrapper/export snapshot; runtime report labels are preserved as recorded.",
               "The source animation fixture overlaps baseline checks and is excluded from the native functional total.",
               "Campaign traversal, targeted fixtures and rendered studies have different scopes.",
               "No movie, terrain audit or artistic approval is claimed by this manifest unless separately supplied.",
               "v0.4.0 and v0.4.1 artifacts and evidence are preserved; AAA finish remains a production target."])
    frozen()
    return manifest, selected


def source_export_config():
    """Archive-only portable preset: installed templates and this version's path."""
    text = normalized_export((P / "export_presets.cfg").read_bytes()).decode("utf-8")
    fields = {"export_path": '"build/v0.4.2/When the Sky Clears.exe"',
              "application/product_version": '"0.4.2.0"', "application/file_version": '"0.4.2.0"'}
    for key, value in fields.items():
        text, count = re.subn(r"^" + re.escape(key) + r"=[^\r\n]*", key + "=" + value,
                              text, flags=re.MULTILINE)
        require(count == 1, f"Expected one source export preset field: {key}")
    return text.encode("utf-8")


def package(expected_captures):
    manifest, selected = verify(expected_captures)
    source_preset = source_export_config()
    manifest["source_archive_transform"] = dict(file="export_presets.cfg",
        operation="Clear custom templates; set portable v0.4.2 output path and product/file versions in source ZIP only.",
        original_sha256=sha(P / "export_presets.cfg"),
        archive_sha256=hashlib.sha256(source_preset).hexdigest())
    data = json_bytes(manifest)
    entries = {}
    for folder in ["assets", "scripts", "scenes", "levels", "story", "previous"]:
        for path in (P / folder).rglob("*"):
            if path.is_file() and not any(part in [".godot", "__pycache__", "build", "motion_frames"] for part in path.parts):
                require(path.suffix.lower() not in [".exe", ".zip", ".tpz", ".pyc"], f"Unexpected source binary: {path}")
                entries[path.relative_to(P).as_posix()] = path
    for path in P.iterdir():
        if path.is_file() and (path.suffix in [".txt", ".cmd"] or path.name in ["project.godot", ".gitignore"]):
            entries[path.name] = path
    for path in (P / "tools").glob("*"):
        if path.is_file() and (path.suffix in [".py", ".gd", ".uid"] or path.name in [".gdignore", "ENGINE_PROVENANCE.json", "SHA512-SUMS.txt"]):
            entries[path.relative_to(P).as_posix()] = path
    for path in DOCS.rglob("*"):
        if path.is_file() and path.suffix in [".md", ".txt", ".json", ".docx"]:
            entries["docs/" + path.relative_to(DOCS).as_posix()] = path
    entries["export_presets.cfg"] = source_preset
    for name in ["character_sources/.gdignore", "character_sources/SOURCE_RECEIPTS.json",
                 "character_sources/QUATERNIUS_CURRENT_LICENSE.html",
                 "character_sources/kenney-impact-sounds/RECEIPT.json"]:
        path = P / name
        if path.is_file():
            entries[name] = path
    for path in selected:
        entries[path.relative_to(P).as_posix()] = path
    name = "DELIVERY_MANIFEST_v042.json"
    entries[(E / name).relative_to(P).as_posix()] = data
    entries["evidence/.gdignore"] = b""
    review = E / "V042_PLAYABLE_REVIEW.jpg"
    if review.is_file():
        entries[review.relative_to(P).as_posix()] = review
    movie_validation = E / "mill_movie_validation.json"
    if movie_validation.is_file():
        entries[movie_validation.relative_to(P).as_posix()] = movie_validation
    sluice_validation = E / "sluice_movie_validation.json"
    if sluice_validation.is_file():
        entries[sluice_validation.relative_to(P).as_posix()] = sluice_validation
    craft_validation = E / "craft_movie_validation.json"
    if craft_validation.is_file():
        entries[craft_validation.relative_to(P).as_posix()] = craft_validation
    entries["README_SOURCE.txt"] = b"Import project.godot in Godot 4.6 Standard. This ZIP flattens the repository game/ folder. Editor play needs no export templates. See docs/releases/v0.4.2.md for this snapshot's scope.\n"
    native = {EXE.name: EXE, "BUILD_MANIFEST.json": data,
        "READ_ME.txt": b"WHEN THE SKY CLEARS - DEVELOPMENT 0.4.2\nExtract this ZIP and run When the Sky Clears.exe. Godot and Python are not needed.\nA/D move; Space jump; Shift run; S crouch; hold E work; Q wait/call; H medicine; Tab pack; Esc pause.\nSee the build manifest for verified scope. Artistic acceptance is separate.\n",
        "MILL_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --mill-preview\r\n',
        "CANAL_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --canal-preview\r\n',
        "SLUICE_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --sluice-preview\r\n',
        "FREIGHT_CROSSING.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --freight-crossing\r\n'}
    for path in (DOCS / "licenses").glob("*.txt"):
        native["licenses/" + path.name] = path
    native["DEVELOPMENT_v0.4.2.txt"] = P / "DEVELOPMENT_v0.4.2.txt"
    require("licenses/GODOT-LICENSE.txt" in native, "Missing Godot distribution notice.")
    outputs = [(P / f"When_The_Sky_Clears_Windows_v{VERSION}.zip", native),
               (P / f"When_The_Sky_Clears_Editable_Source_v{VERSION}.zip", entries)]
    prepared = []
    try:
        for target, members in outputs:
            prepared.append((target, make_archive(target, members)))
        frozen()
        for target, temporary in prepared:
            os.replace(temporary, target)
        atomic_write(E / name, data)
        artifacts = [dict(file=target.name, bytes=target.stat().st_size, sha256=sha(target)) for target, _ in outputs]
        atomic_write(E / "RELEASE_ARTIFACTS_v042.json", json_bytes(artifacts))
        print("V042_PACKAGED", json.dumps(artifacts))
    finally:
        for _, temporary in prepared:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["export", "test", "verify", "package"])
    parser.add_argument("kinds", nargs="*", help="test kinds, or all for functional suites + traversal + source animation")
    parser.add_argument("--engine", type=Path, default=P / "tools/godot/Godot_v4.6-stable_win64_console.exe")
    parser.add_argument("--source", action="store_true", help="test unfrozen source into its own evidence tag")
    parser.add_argument("--tag", help="one evidence subdirectory; defaults to source or release_final")
    parser.add_argument("--capture-flag", default="capture-v042", help="runtime user flag used by test capture")
    parser.add_argument("--expected-captures", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    args.engine = args.engine.resolve()
    require(args.timeout > 0 and args.expected_captures > 0, "Timeout and capture count must be positive.")
    require(args.operation == "test" or not args.kinds, "Test kinds are valid only with the test operation.")
    if args.operation == "export":
        export(args.engine.resolve(), args.timeout)
    elif args.operation == "test":
        require(args.kinds, "Specify test kinds or all.")
        test(args)
    elif args.operation == "verify":
        manifest, _ = verify(args.expected_captures)
        print("V042_VERIFIED", manifest["total_functional_checks"], "native checks; source animation separate")
    else:
        package(args.expected_captures)


if __name__ == "__main__":
    try:
        main()
    except (DeliveryError, OSError, ValueError, KeyError) as error:
        print(f"v0.4.2 operation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
