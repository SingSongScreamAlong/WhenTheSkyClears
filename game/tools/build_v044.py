"""Isolated v0.4.4 Windows export, native QA and delivery packaging.

Examples, from the repository root:
  python game/tools/build_v044.py export
  python game/tools/build_v044.py test all
  python game/tools/build_v044.py test capture
  python game/tools/build_v044.py verify
  python game/tools/build_v044.py package

Artifacts stay under build/v0.4.4 and evidence/v044. Existing runtime flags and
report version labels are retained; wrapper metadata identifies this delivery as
0.4.4 without rewriting runtime source. Animation QA runs as a separately bound
native source fixture. Existing v0.4.0 through v0.4.3 artifacts remain untouched.
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

VERSION = "0.4.4"
P = Path(__file__).resolve().parents[1]
DOCS = P / "docs" if (P / "docs").is_dir() else P.parent / "docs"
E = P / "evidence/v044"
B = P / "build/v0.4.4"
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
    "trolley-checks": "trolley_checks.json", "performance-checks": "performance_checks.json",
    "physical-v044-checks": "physical_puzzles_v044.json",
    "garden-v044-checks": "garden_puzzle_v044.json",
    "character-v044-checks": "character_checks_v044.json",
    "traverse": "continuous_traversal.json", "animation-checks": "movement_checks.json",
}
PLAYTHROUGHS = {
    "mill-playthrough": dict(flag="mill-checks", record="--record-mill", report="mill_checks.json", frames="motion_frames"),
    "sluice-playthrough": dict(flag="sluice-checks", record="--record-sluice", report="sluice_checks.json", frames="sluice_motion_frames"),
    "craft-playthrough": dict(flag="craft-checks", record="--record-craft", report="craft_checks.json", frames="craft_motion_frames"),
    "trolley-playthrough": dict(flag="trolley-checks", record="--record-trolley", report="trolley_checks.json", frames="trolley_motion_frames"),
    "performance-playthrough": dict(flag="performance-checks", record="--record-performance", report="performance_checks.json", frames="performance_motion_frames"),
    "physical-playthrough": dict(flag="physical-v044-checks", record="--record-physical-v044", report="physical_puzzles_v044.json", frames="physical_v044_motion_frames"),
    "garden-playthrough": dict(flag="garden-v044-checks", record="--record-garden-v044", report="garden_puzzle_v044.json", frames="garden_v044_motion_frames"),
    "character-playthrough": dict(flag="character-v044-checks", record="--record-character-v044", report="character_checks_v044.json", frames="character_v044_motion_frames"),
}
REVIEW_MOVIES = {
    "physical": dict(kind="physical-playthrough", filename="WTSC_Physical_Puzzles_Review_v044.mp4",
                     label="PHYSICAL PUZZLES / BOUNDED NATIVE INPUT FIXTURES / 30 FPS / 0.4.4"),
    "garden": dict(kind="garden-playthrough", filename="WTSC_Garden_Puzzle_Review_v044.mp4",
                   label="GARDEN / BOUNDED NATIVE INPUT FIXTURE / 30 FPS / 0.4.4"),
    "character": dict(kind="character-playthrough", filename="WTSC_Character_Review_v044.mp4",
                      label="CHARACTERS / STAGED NATIVE PERFORMANCE / 30 FPS / 0.4.4"),
}
EXTRAS = ["capture", "motion", "crossing-capture", *PLAYTHROUGHS]
CAPTURE_NAMES = [
    "01_mill_gardens.png", "02_canal_lower_route.png", "03_canal_upper_route.png",
    "04_signal_yard.png", "05_school_gallery.png", "06_living_terraces.png",
    "07_character_close_study.png", "08_interactive_mill_bridge.png",
    "09_interactive_wheel_approach.png", "10_canal_pump_work.png",
    "11_canal_sluice_drained.png", "12_supplies_close_study.png",
    "13_counterweight_wait.png", "14_counterweight_crossing.png",
    "15_counterweight_reunion.png",
    "16_logging_counterweight.png",
    "17_trolley_cover.png", "18_trolley_dock.png", "19_trolley_reunion.png",
    "20_orchard_weighted_mechanism.png", "21_orchard_open_route.png",
    "22_freight_lift_wait.png", "23_freight_lift_reunion.png",
    "24_garden_ferry_board.png", "25_garden_ferry_crossing.png", "26_garden_ferry_moored.png",
    "27_character_attention_study.png",
]
SLUICE_CAPTURE_NAMES = CAPTURE_NAMES[12:15]
TROLLEY_CAPTURE_NAMES = CAPTURE_NAMES[16:19]
PHYSICAL_CAPTURE_NAMES = CAPTURE_NAMES[19:23]
GARDEN_CAPTURE_NAMES = CAPTURE_NAMES[23:26]
CAPTURE_SEQUENCES = {
    "sluice": ("sluice_capture.json", SLUICE_CAPTURE_NAMES),
    "trolley": ("trolley_capture.json", TROLLEY_CAPTURE_NAMES),
    "physical_v044": ("physical_v044_capture.json", PHYSICAL_CAPTURE_NAMES),
    "garden_v044": ("garden_v044_capture.json", GARDEN_CAPTURE_NAMES),
}
CAPTURE_REPORT_NAMES = [filename for filename, _ in CAPTURE_SEQUENCES.values()]
FRAME_DIRS = {"motion": "motion_frames", **{kind: spec["frames"] for kind, spec in PLAYTHROUGHS.items()}}


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
        require(capture_count == len(CAPTURE_NAMES), "Capture count must match the complete authored v0.4.4 capture list.")
        expected = CAPTURE_NAMES + CAPTURE_REPORT_NAMES
        cleanup = CAPTURE_NAMES + CAPTURE_REPORT_NAMES
    else:
        filename = REPORTS.get(kind, {"motion": "motion_review.json", "crossing-capture": "capture_report.json",
                                     **{key: spec["report"] for key, spec in PLAYTHROUGHS.items()}}.get(kind))
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
    reports = {}
    for label, (filename, names) in CAPTURE_SEQUENCES.items():
        report = load(folder / filename)
        require(report.get("all_states_reached") is True and report.get("screenshots") == names,
                f"{label.title()} capture did not reach its required authored sequence states.")
        reports[label] = report
    return reports


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
    require(identity.get("build") == VERSION, "Missing v0.4.4 export identity; run export after freezing the source.")
    require(EXE.is_file() and identity.get("sha256") == sha(EXE)
            and identity.get("bytes") == EXE.stat().st_size, "v0.4.4 executable changed after export.")
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
        "application/product_version": '"0.4.4.0"', "application/file_version": '"0.4.4.0"',
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
        scope="v0.4.4 delivery wrapper; runtime report labels and save behavior are not rewritten by this tool.")
    atomic_write(IDENTITY, json_bytes(identity))
    print("V044_EXPORTED", identity["bytes"], identity["sha256"])


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
        fps = 30 if kind == "motion" or kind in PLAYTHROUGHS else 60
        flag = args.capture_flag if kind == "capture" else PLAYTHROUGHS.get(kind, {}).get("flag", kind)
        require(re.fullmatch(r"[A-Za-z0-9_-]+", flag), "Capture flag must be a simple Godot user flag.")
        command += ["--fixed-fps", str(fps), "--log-file", str(folder / "engine.log"),
                    "--", "--evidence-dir", str(folder), "--" + flag]
        if kind in PLAYTHROUGHS:
            command += [PLAYTHROUGHS[kind]["record"]]
        metadata = dict(scope="Native source fixture" if source_fixture else "Standalone v0.4.4 executable")
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
        print("V044_TEST", kind, record["exit_code"], record["elapsed_seconds"])


def verify(expected_captures):
    require(expected_captures == len(CAPTURE_NAMES), "Verification requires the complete authored v0.4.4 capture list.")
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
    require({path.name for path in captures} == set(CAPTURE_NAMES), "Native capture filenames differ from the authored v0.4.4 list.")
    capture_inventory = verify_outputs(final / "capture", capture_call,
                                       [path.name for path in captures] + CAPTURE_REPORT_NAMES)
    capture_sequences = validate_capture(final / "capture")
    selected.extend(final / "capture" / name for name in CAPTURE_REPORT_NAMES)
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
        sluice_capture=capture_sequences["sluice"], trolley_capture=capture_sequences["trolley"],
        physical_v044_capture=capture_sequences["physical_v044"], garden_v044_capture=capture_sequences["garden_v044"],
        captures=[dict(file=path.relative_to(P).as_posix(), sha256=sha(path), size=[3840, 2160],
                       scope="Staged close view" if "close" in path.stem else "Native rendered scene") for path in captures],
        evidence={path.relative_to(P).as_posix(): sha(path) for path in selected},
        runtime_report_labels={kind: report.get("build", report.get("version")) for kind, report in reports.items()},
        notes=["v0.4.4 identifies this wrapper/export snapshot; runtime report labels are preserved as recorded.",
               "The source animation fixture overlaps baseline checks and is excluded from the native functional total.",
               "Campaign traversal, targeted fixtures and rendered studies have different scopes.",
               "No movie, terrain audit or artistic approval is claimed by this manifest unless separately supplied.",
               "v0.4.0 through v0.4.3 artifacts and evidence are preserved; AAA finish remains a production target."])
    frozen()
    return manifest, selected


def source_export_config():
    """Archive-only portable preset: installed templates and this version's path."""
    text = normalized_export((P / "export_presets.cfg").read_bytes()).decode("utf-8")
    fields = {"export_path": '"build/v0.4.4/When the Sky Clears.exe"',
              "application/product_version": '"0.4.4.0"', "application/file_version": '"0.4.4.0"'}
    for key, value in fields.items():
        text, count = re.subn(r"^" + re.escape(key) + r"=[^\r\n]*", key + "=" + value,
                              text, flags=re.MULTILINE)
        require(count == 1, f"Expected one source export preset field: {key}")
    return text.encode("utf-8")


def validated_review_files(manifest):
    """Admit only review artifacts tied to this exact export and native run."""
    admitted = {}
    specs = {"review_board_validation.json": ("V044_PLAYABLE_REVIEW.jpg", "capture", None),
             **{name + "_movie_validation.json": (spec["filename"], spec["kind"], PLAYTHROUGHS[spec["kind"]]["report"])
                for name, spec in REVIEW_MOVIES.items()}}
    for validation_name, (filename, scenario, report_name) in specs.items():
        path, artifact = E / validation_name, E / filename
        if not path.exists() and not artifact.exists():
            continue
        require(path.is_file() and artifact.is_file() and not path.is_symlink() and not artifact.is_symlink(),
                f"Review artifact/validation pair incomplete or indirect: {filename}")
        record = load(path)
        require(record.get("build") == VERSION and record.get("file") == filename
                and record.get("source_exe_sha256") == manifest["executable"]["sha256"]
                and record.get("export_identity_sha256") == sha(IDENTITY), f"Stale review identity: {validation_name}")
        require(record.get("bytes") == artifact.stat().st_size and record.get("sha256") == sha(artifact),
                f"Changed review artifact: {filename}")
        folder = E / "release_final" / scenario
        call = invocation(folder, manifest["executable"]["sha256"])
        require(record.get("native_invocation_sha256") == sha(folder / "invocation.json"),
                f"Stale native review invocation: {validation_name}")
        if report_name:
            verify_outputs(folder, call, [report_name])
            report = load(folder / report_name)
            require(record.get("native_report_sha256") == sha(folder / report_name)
                    and report.get("all_passed") is True and report.get("checks")
                    and all(c.get("passed") is True for c in report["checks"])
                    and isinstance(record.get("frames"), int) and record["frames"] > 0 and record.get("fps") == 30
                    and record.get("frames") == record.get("decoded_frames") == report.get("recorded_frames")
                    and record.get("native_frame_inventory_sha256") == hashlib.sha256(json_bytes(call["generated_frame_sequences"][PLAYTHROUGHS[scenario]["frames"]])).hexdigest()
                    and all(record.get(key) is True for key in ["decode_passed", "full_decode_passed", "frame_count_passed"]),
                    f"Unverified native review movie: {validation_name}")
        else:
            captures = {item["file"]: item["sha256"] for item in manifest["captures"]}
            selected = record.get("captures", [])
            require(len(selected) == 9 and len({item.get("file") for item in selected}) == 9
                    and all(item.get("file") in captures and captures[item["file"]] == item.get("sha256") for item in selected),
                    "Review board is not bound to the verified native capture set.")
        admitted[artifact.relative_to(P).as_posix()] = artifact
        admitted[path.relative_to(P).as_posix()] = path
    return admitted


def package(expected_captures):
    manifest, selected = verify(expected_captures)
    source_preset = source_export_config()
    manifest["source_archive_transform"] = dict(file="export_presets.cfg",
        operation="Clear custom templates; set portable v0.4.4 output path and product/file versions in source ZIP only.",
        original_sha256=sha(P / "export_presets.cfg"),
        archive_sha256=hashlib.sha256(source_preset).hexdigest())
    review_entries = validated_review_files(manifest)
    review_digests = {name: sha(path) for name, path in review_entries.items()}
    manifest["evidence"].update(review_digests)
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
    manifest_name = "DELIVERY_MANIFEST_v044.json"
    entries[(E / manifest_name).relative_to(P).as_posix()] = data
    entries["evidence/.gdignore"] = b""
    entries.update(review_entries)
    entries["README_SOURCE.txt"] = b"Import project.godot in Godot 4.6 Standard. This ZIP flattens the repository game/ folder. Editor play needs no export templates. See docs/releases/v0.4.4.md for this snapshot's scope.\n"
    native = {EXE.name: EXE, "BUILD_MANIFEST.json": data,
        "READ_ME.txt": b"WHEN THE SKY CLEARS - DEVELOPMENT 0.4.4\nExtract this ZIP and run When the Sky Clears.exe. Godot and Python are not needed.\nA/D move; Space jump; Shift run; S crouch; hold E work; Q wait/call; H medicine; Tab pack; Esc pause.\nSee the build manifest for verified scope. Artistic acceptance is separate.\n",
        "MILL_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --mill-preview\r\n',
        "CANAL_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --canal-preview\r\n',
        "SLUICE_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --sluice-preview\r\n',
        "TROLLEY_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --trolley-preview\r\n',
        "ORCHARD_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --orchard-preview\r\n',
        "FREIGHT_LIFT_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --freight-lift-preview\r\n',
        "GARDEN_FERRY_PLAYTEST.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --garden-preview\r\n',
        "FREIGHT_CROSSING.cmd": b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "When the Sky Clears.exe" -- --freight-crossing\r\n'}
    for path in (DOCS / "licenses").glob("*.txt"):
        native["licenses/" + path.name] = path
    native["DEVELOPMENT_v0.4.4.txt"] = P / "DEVELOPMENT_v0.4.4.txt"
    require("licenses/GODOT-LICENSE.txt" in native, "Missing Godot distribution notice.")
    outputs = [(P / f"When_The_Sky_Clears_Windows_v{VERSION}.zip", native),
               (P / f"When_The_Sky_Clears_Editable_Source_v{VERSION}.zip", entries)]
    prepared = []
    try:
        for target, members in outputs:
            prepared.append((target, make_archive(target, members)))
        frozen()
        require(all(sha(path) == manifest["evidence"][path.relative_to(P).as_posix()] for path in selected),
                "Required delivery evidence changed during packaging.")
        final_reviews = validated_review_files(manifest)
        require({name: sha(path) for name, path in final_reviews.items()} == review_digests,
                "Review artifacts changed during packaging.")
        for target, temporary in prepared:
            os.replace(temporary, target)
        atomic_write(E / manifest_name, data)
        artifacts = [dict(file=target.name, bytes=target.stat().st_size, sha256=sha(target)) for target, _ in outputs]
        atomic_write(E / "RELEASE_ARTIFACTS_v044.json", json_bytes(artifacts))
        print("V044_PACKAGED", json.dumps(artifacts))
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
    parser.add_argument("--capture-flag", default="capture-v044", help="runtime user flag used by test capture")
    parser.add_argument("--expected-captures", type=int, default=len(CAPTURE_NAMES))
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
        print("V044_VERIFIED", manifest["total_functional_checks"], "native checks; source animation separate")
    else:
        package(args.expected_captures)


if __name__ == "__main__":
    try:
        main()
    except (DeliveryError, OSError, ValueError, KeyError) as error:
        print(f"v0.4.4 operation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
