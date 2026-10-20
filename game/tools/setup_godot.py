"""Install the project's official Godot 4.6 Windows tools without running them.

Uses only the Python standard library. Archives are checked against the publisher
SHA-512 hashes recorded in ENGINE_PROVENANCE.json before selected files are
extracted. Existing tools are preserved unless --force is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile


TOOLS = Path(__file__).resolve().parent
OFFICIAL_SOURCE = (
    "https://github.com/godotengine/godot-builds/releases/download/4.6-stable/"
)
PACKAGES = (
    (
        "Godot_v4.6-stable_win64.exe.zip",
        (
            ("Godot_v4.6-stable_win64.exe", "godot/Godot_v4.6-stable_win64.exe"),
            (
                "Godot_v4.6-stable_win64_console.exe",
                "godot/Godot_v4.6-stable_win64_console.exe",
            ),
        ),
    ),
    (
        "Godot_v4.6-stable_export_templates.tpz",
        (
            ("templates/windows_debug_x86_64.exe", "windows_debug_x86_64.exe"),
            ("templates/windows_release_x86_64.exe", "windows_release_x86_64.exe"),
        ),
    ),
)


def present(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def sha512(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_hashes() -> dict[str, str]:
    with (TOOLS / "ENGINE_PROVENANCE.json").open(encoding="utf-8-sig") as stream:
        provenance = json.load(stream)
    if provenance.get("version") != "4.6.stable":
        raise ValueError("ENGINE_PROVENANCE.json must describe Godot 4.6.stable.")
    if provenance.get("source") != OFFICIAL_SOURCE:
        raise ValueError("The recorded source is not the expected official release URL.")
    hashes = provenance.get("sha512", {})
    for name, _ in PACKAGES:
        if not re.fullmatch(r"[0-9a-fA-F]{128}", hashes.get(name, "")):
            raise ValueError(f"Missing or invalid publisher SHA-512 for {name}.")
    return {name: hashes[name].lower() for name, _ in PACKAGES}


def verified_archive(name: str, expected: str) -> Path:
    archive = TOOLS / name
    if archive.is_file():
        print(f"Checking cached archive: {name}", flush=True)
        if sha512(archive) == expected:
            print("  Publisher SHA-512 matches.", flush=True)
            return archive
        print("  Cached checksum differs; downloading a verified replacement.", flush=True)

    # Keep the previous cache and installed binaries intact until verification
    # succeeds. Each process receives its own partial file.
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=name + ".", suffix=".part", dir=TOOLS, delete=False
        ) as output:
            temporary = Path(output.name)
            request = urllib.request.Request(
                OFFICIAL_SOURCE + name,
                headers={"User-Agent": "WhenTheSkyClears-GodotSetup/1.0"},
            )
            print(f"Downloading official release: {name}", flush=True)
            digest = hashlib.sha512()
            downloaded = 0
            last_report = time.monotonic()
            with urllib.request.urlopen(request, timeout=60) as response:
                total = int(response.headers.get("Content-Length", "0"))
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                    digest.update(chunk)
                    downloaded += len(chunk)
                    now = time.monotonic()
                    if now - last_report >= 10:
                        progress = f"{downloaded / (1024 * 1024):.1f} MiB"
                        if total:
                            progress += f" / {total / (1024 * 1024):.1f} MiB"
                        print("  " + progress, flush=True)
                        last_report = now
            if not downloaded or digest.hexdigest() != expected:
                raise ValueError(f"Publisher SHA-512 verification failed for {name}.")
        os.replace(temporary, archive)
        temporary = None
        print("  Download verified against publisher SHA-512.", flush=True)
        return archive
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install_members(archive: Path, members: tuple, force: bool) -> None:
    # Do not use extractall: only these exact archive entries can become files,
    # and each destination is a fixed project-local path defined above.
    with zipfile.ZipFile(archive) as package:
        all_members = package.infolist()
        selected = []
        for member_name, relative_destination in members:
            matches = [entry for entry in all_members if entry.filename == member_name]
            if len(matches) != 1:
                raise ValueError(f"Archive must contain exactly one {member_name}.")
            entry = matches[0]
            mode = entry.external_attr >> 16
            if entry.is_dir() or stat.S_ISLNK(mode) or not 0 < entry.file_size <= 512 * 1024 * 1024:
                raise ValueError(f"Unexpected archive entry: {member_name}.")
            selected.append((entry, TOOLS / relative_destination))

        for entry, destination in selected:
            if present(destination) and not force:
                print(f"Preserved: {destination.relative_to(TOOLS)}", flush=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    prefix=destination.name + ".", suffix=".part",
                    dir=destination.parent, delete=False,
                ) as output:
                    temporary = Path(output.name)
                    with package.open(entry) as source:
                        shutil.copyfileobj(source, output, length=1024 * 1024)
                if temporary.stat().st_size != entry.file_size:
                    raise ValueError(f"Incomplete extraction: {entry.filename}.")
                os.replace(temporary, destination)
                temporary = None
                print(f"Installed: {destination.relative_to(TOOLS)}", flush=True)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="report whether the four Windows tools are present; do not download or write",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="replace existing tools from verified archives (cached archives are reused)",
    )
    args = parser.parse_args()
    if args.check and args.force:
        parser.error("--check and --force cannot be combined")

    hashes = read_hashes()
    if args.check:
        complete = True
        for _, members in PACKAGES:
            for _, relative_destination in members:
                found = present(TOOLS / relative_destination)
                print(f"{'PRESENT' if found else 'MISSING'} {relative_destination}")
                complete &= found
        print("Presence check only. --force reinstalls tools from verified official archives.")
        return 0 if complete else 1

    for archive_name, members in PACKAGES:
        if not args.force and all(present(TOOLS / target) for _, target in members):
            print(f"Already present; preserved tools from {archive_name}.", flush=True)
            continue
        archive = verified_archive(archive_name, hashes[archive_name])
        install_members(archive, members, args.force)

    print("Ready: open game/project.godot with Godot 4.6, or run game/EDIT.cmd on Windows.")
    print("No downloaded program has been executed. Existing tools were preserved unless --force was used.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, urllib.error.URLError) as error:
        print(f"Godot setup failed: {error}", file=sys.stderr)
        sys.exit(1)
