"""Compose the v0.4.4 review board and validate labelled native recordings.

Run after the final build/capture/recording invocations:
  python game/tools/make_review_v044.py board
  python game/tools/make_review_v044.py physical
  python game/tools/make_review_v044.py garden
  python game/tools/make_review_v044.py character
  python game/tools/make_review_v044.py all

Movies retain the exact recorded frame range at 30 fps with an explicit staged
review label. They are bounded fixtures, not continuous campaign playthroughs.
Every source frame must match the hash inventory of the native invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

import build_v044 as delivery

P, E = delivery.P, delivery.E
F = E / "release_final"
SHOTS = [
    ("20_orchard_weighted_mechanism.png", "Orchard / weighted physical mechanism"),
    ("21_orchard_open_route.png", "Orchard / opened route"),
    ("22_freight_lift_wait.png", "Freight / lift and waiting child"),
    ("23_freight_lift_reunion.png", "Freight / reunion beyond the lift"),
    ("24_garden_ferry_board.png", "Garden / both children board"),
    ("25_garden_ferry_crossing.png", "Garden / rope ferry crossing"),
    ("26_garden_ferry_moored.png", "Garden / ferry moored at the dock"),
    ("27_character_attention_study.png", "Characters / staged attention study"),
    ("01_mill_gardens.png", "Village / mill gardens"),
]
MOVIES = {name: dict(spec, report=delivery.PLAYTHROUGHS[spec["kind"]]["report"],
                    directory=delivery.PLAYTHROUGHS[spec["kind"]]["frames"],
                    flag="--" + delivery.PLAYTHROUGHS[spec["kind"]]["flag"],
                    record=delivery.PLAYTHROUGHS[spec["kind"]]["record"])
          for name, spec in delivery.REVIEW_MOVIES.items()}


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    delivery.require(result.returncode == 0, "Media operation failed:\n" + result.stderr[-3000:])
    return result


def font(size):
    return ImageFont.truetype(str(P / "assets/fonts/interface.ttf"), size)


def native_call(folder, identity, required):
    call = delivery.invocation(folder, identity["sha256"])
    delivery.require(call.get("build") == delivery.VERSION, "Media invocation has the wrong delivery version.")
    delivery.verify_outputs(folder, call, required)
    return call


def board():
    identity = delivery.frozen()
    folder = F / "capture"
    call = native_call(folder, identity, delivery.CAPTURE_NAMES + delivery.CAPTURE_REPORT_NAMES)
    delivery.validate_capture(folder)
    invocation_hash = delivery.sha(folder / "invocation.json")
    delivery.require({path.name for path in folder.glob("*.png")} == set(delivery.CAPTURE_NAMES),
                     "Native capture directory contains missing or unexpected PNGs.")
    for name in delivery.CAPTURE_NAMES:
        delivery.require(delivery.png_size(folder / name) == [3840, 2160], "Expected a native 4K capture: " + name)
    sheet = Image.new("RGB", (1980, 1320), "#14201e")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), "WHEN THE SKY CLEARS / PHYSICAL PUZZLES AND PERFORMANCE / 0.4.4",
              fill="#e4dfcb", font=font(26))
    draw.text((24, 60), "Native 3840 x 2160 captures. Staged views and bounded authored sequence; artistic acceptance pending.",
              fill="#bbc5ba", font=font(18))
    selected = []
    for index, (name, label) in enumerate(SHOTS):
        source = folder / name
        with Image.open(source) as image:
            tile = image.convert("RGB").resize((640, 360), Image.Resampling.LANCZOS)
        x, y = 20 + index % 3 * 660, 110 + index // 3 * 400
        sheet.paste(tile, (x, y))
        draw.text((x + 3, y + 369), label, fill="#ced3c6", font=font(18))
        selected.append(dict(file=source.relative_to(P).as_posix(), sha256=delivery.sha(source), label=label))
    output = E / "V044_PLAYABLE_REVIEW.jpg"
    temporary = output.with_name(output.stem + ".building.jpg")
    try:
        sheet.save(temporary, quality=93)
        with Image.open(temporary) as image:
            image.verify()
        delivery.frozen()
        delivery.require(delivery.sha(folder / "invocation.json") == invocation_hash,
                         "Capture invocation changed while composing the board.")
        delivery.verify_outputs(folder, call, delivery.CAPTURE_NAMES + delivery.CAPTURE_REPORT_NAMES)
        os.replace(temporary, output)
        validation = dict(build=delivery.VERSION, file=output.name, bytes=output.stat().st_size,
                          sha256=delivery.sha(output), size=[1980, 1320],
                          source_exe_sha256=identity["sha256"], export_identity_sha256=delivery.sha(delivery.IDENTITY),
                          native_invocation_sha256=invocation_hash, captures=selected,
                          scope="Nine labelled panels from the exact native capture invocation. Staged close views and a bounded authored sequence; separate from artistic acceptance and campaign traversal.")
        delivery.atomic_write(E / "review_board_validation.json", delivery.json_bytes(validation))
        print("V044_REVIEW_BOARD", output)
        return validation
    finally:
        temporary.unlink(missing_ok=True)


def movie(name):
    identity = delivery.frozen()
    spec = MOVIES[name]
    folder = F / spec["kind"]
    call = native_call(folder, identity, [spec["report"]])
    command = call["command"]
    delivery.require("--fixed-fps" in command and command[command.index("--fixed-fps") + 1] == "30",
                     "Native recording was not run at fixed 30 fps.")
    delivery.require("--" in command and spec["flag"] in command[command.index("--") + 1:]
                     and spec["record"] in command[command.index("--") + 1:],
                     "Invocation did not request the expected native recording.")
    report = delivery.load(folder / spec["report"])
    checks = report.get("checks", [])
    delivery.require(report.get("all_passed") is True and checks
                     and all(check.get("passed") is True for check in checks), "Native recording checks did not pass.")
    frames = report.get("recorded_frames")
    delivery.require(isinstance(frames, int) and frames > 0, "Native report has no recorded frames.")
    recording = report.get("recording", {})
    delivery.require(recording.get("enabled") is True and recording.get("frames") == frames
                     and recording.get("fps") == 30 and report.get("fps", 30) == 30,
                     name.title() + " report has inconsistent recording metadata.")
    sources = delivery.verify_frame_sequence(folder, call, spec["directory"], frames)
    size = None
    for source in sources:
        with Image.open(source) as image:
            image.load()
            if size is None:
                size = image.size
            delivery.require(image.size == size, "Native movie frame dimensions changed: " + source.name)
    delivery.require(size and all(value > 0 and value % 2 == 0 for value in size),
                     "Movie frame size must be positive and even for YUV420.")
    invocation_hash = delivery.sha(folder / "invocation.json")
    report_hash = delivery.sha(folder / spec["report"])
    inventory_hash = hashlib.sha256(delivery.json_bytes(call["generated_frame_sequences"][spec["directory"]])).hexdigest()
    output = E / spec["filename"]
    temporary = output.with_name(output.stem + ".building.mp4")
    overlay = E / ("." + name + "_review_label.png")
    strip = Image.new("RGBA", (size[0], max(32, round(size[1] * .049))), (12, 20, 19, 232))
    ImageDraw.Draw(strip).text((12, 6), spec["label"], fill=(237, 233, 217, 255),
                              font=font(max(15, round(size[1] * .022))))
    strip.save(overlay)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    try:
        run([ffmpeg, "-y", "-framerate", "30", "-start_number", "0", "-i",
             str(sources[0].parent / "%05d.jpg"), "-loop", "1", "-i", str(overlay),
             "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]",
             "-frames:v", str(frames), "-r", "30", "-c:v", "libx264", "-preset", "medium",
             "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(temporary)])
        decoded = run([ffmpeg, "-v", "error", "-xerror", "-i", str(temporary), "-progress", "pipe:1",
                       "-nostats", "-f", "null", "-"])
        delivery.require(not decoded.stderr.strip() and "progress=end" in decoded.stdout,
                         "FFmpeg did not decode the complete native review movie.")
        decoded_counts = [int(line.partition("=")[2]) for line in decoded.stdout.splitlines() if line.startswith("frame=")]
        delivery.require(decoded_counts and max(decoded_counts) == frames, "Full decode frame count differs from the recorded range.")
        counted, seconds = imageio_ffmpeg.count_frames_and_secs(str(temporary))
        delivery.require(counted == frames and abs(seconds - frames / 30) <= 1 / 30 + .001,
                         "Encoded movie frame count or duration differs from native 30 fps footage.")
        delivery.frozen()
        delivery.require(delivery.sha(folder / "invocation.json") == invocation_hash
                         and delivery.sha(folder / spec["report"]) == report_hash,
                         "Native recording evidence changed while encoding.")
        delivery.verify_frame_sequence(folder, call, spec["directory"], frames)
        os.replace(temporary, output)
        validation = dict(build=delivery.VERSION, file=output.name, bytes=output.stat().st_size,
                          sha256=delivery.sha(output), frames=frames, decoded_frames=max(decoded_counts),
                          seconds=seconds, duration_seconds=frames / 30, fps=30, size=list(size), audio=False,
                          decode_passed=True, full_decode_passed=True, frame_count_passed=True,
                          source_exe_sha256=identity["sha256"], export_identity_sha256=delivery.sha(delivery.IDENTITY),
                          native_invocation_sha256=invocation_hash, native_report_sha256=report_hash,
                          native_frame_inventory_sha256=inventory_hash, label=spec["label"],
                          scope=recording.get("scope", report.get("method", "Bounded native authored fixture.")),
                          method="Exact fresh invocation-bound JPG range encoded at 30 fps with an explicit review label; full FFmpeg decode and independent frame-count/duration check. Silent staged footage, separate from campaign traversal and artistic acceptance.")
        delivery.atomic_write(E / (name + "_movie_validation.json"), delivery.json_bytes(validation))
        print("V044_REVIEW_MOVIE", json.dumps(validation))
        return validation
    finally:
        temporary.unlink(missing_ok=True)
        overlay.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["board", *MOVIES, "movies", "all"], nargs="?", default="all")
    args = parser.parse_args()
    if args.operation in ["board", "all"]:
        board()
    for name in MOVIES:
        if args.operation in [name, "movies", "all"]:
            movie(name)


if __name__ == "__main__":
    try:
        main()
    except (delivery.DeliveryError, OSError, ValueError, KeyError, IndexError) as error:
        print("v0.4.4 review failed: " + str(error), file=sys.stderr)
        raise SystemExit(1)
