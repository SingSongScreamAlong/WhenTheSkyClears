"""Package the isolated cloth comparison without touching frozen sources."""
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[1]
E = P / "evidence"
V = P / "previews"
source = ROOT / "locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend"
candidate = P / "native/WTSC_Controlled_Fluid_Coat_v051.blend"
production = ROOT / "shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend"
expected = {
    source: "1721ae5ce9146e9d0379419d153c64ef09a122074a972a8e4bd68fb1953d176e",
    candidate: "e888f7b7ab4c01040e675fc7d974e575a09df5e16f991897cae63629ec7dfd4f",
    production: "f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661",
}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


for path, digest in expected.items():
    assert sha(path) == digest, (path, "frozen source changed")

travel = P / "TRAVEL_CURVE_v051.csv"
shutil.copyfile(ROOT / "locomotion/face_hand_finish_v050/TRAVEL_CURVE_v050.csv", travel)
build = json.loads((E / "FLUID_COAT_BUILD.json").read_text())
samples = build["samples"]
assert len(samples) == 129 and samples[0]["source_frame"] == 1 and samples[-1]["source_frame"] == 33
hem = P / "HEM_RESPONSE_v051.csv"
with hem.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["source_frame_30fps", "seconds_since_F1", "hem_inertia_x_m", "hem_settling_z_m"])
    w.writeheader()
    for row in samples:
        frame = row["source_frame"]
        w.writerow({"source_frame_30fps": frame, "seconds_since_F1": (frame - 1) / 30,
                    "hem_inertia_x_m": row["hem_x_m"], "hem_settling_z_m": row["hem_z_m"]})

movies = json.loads((E / "ENCODED_COAT_VALIDATION.json").read_text())["movies"]
assert len(movies) == 3 and all(m["under_20_MB"] for m in movies)
for movie in movies:
    assert sha(V / movie["file_name"]) == movie["sha256"]

names = {
    "silhouette": "WTSC_v050_v051_Same_Pose_Coat_And_Silhouette.png",
    "neutral": "WTSC_v050_v051_Same_Gait_Full_Pose_Proof.png",
    "actual": movies[0]["file_name"],
    "comparison": movies[1]["file_name"],
    "detail": movies[2]["file_name"],
}
receipt_paths = {
    "silhouette": E / "LIBRARY_VERIFIED_LIBRARY_SILHOUETTE_CREATE_RESULT.json",
    "neutral": E / "LIBRARY_VERIFIED_LIBRARY_NEUTRAL_CREATE_RESULT.json",
    "movies": E / "LIBRARY_VERIFIED_LIBRARY_MOTION_CREATE_RESULT.json",
}
verified = {}
for kind, path in receipt_paths.items():
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("files", data.get("items", data))
    assert isinstance(data, list), (kind, type(data))
    for item in data:
        assert item["metadata_verified"] is True and item["version"] == 0
        verified[item["file_name"]] = {"library_file_id": item["library_file_id"], "version": 0,
                                        "metadata_verified": True}
assert set(names.values()) == set(verified)

review = {
    "status": "cloth-only candidate, not artistic acceptance",
    "frozen_gait_and_body_timing": True,
    "visual_assessment": "Neutral hem and waist contour are softer; actual coat movement is subtle at full shot size. No new visible contact or anchor issue in the decoded review boards. The paired walk still reads mechanically regular, and this cloth test does not solve that.",
    "separate_body_timing_findings": "Near and far upper arms are exact opposing pendulums, near/far elbow flex shares effectively identical timing, and the torso counterrotation is small. Rework body performance separately after evaluating the cloth A/B.",
    "remaining_scene_work": "Fixed face/hand expression, girl dress and braid dynamics, recovery-to-walking step and supportive clasp are outside v051.",
    "continuous_player_observed_by_agent": False,
    "technical_checks_are_not_artistic_approval": True,
}
delivery = {"version": "v051", "native_candidate_sha256": expected[candidate],
            "frozen_baseline_sha256": expected[source], "source_and_production_unchanged": True,
            "preview_names": names, "verified_private_library": verified,
            "movies": movies, "review": review}
(E / "DELIVERY_METADATA.json").write_text(json.dumps(delivery, indent=2))

relative = [
    "locomotion/coat_fluidity_v051/native/WTSC_Controlled_Fluid_Coat_v051.blend",
    "locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend",
    "locomotion/connected_model_fit_v049/scripts/model_spec.py",
    "locomotion/coat_fluidity_v051/IMPORT_TIMING_AND_ASSESSMENT_v051.txt",
    "locomotion/coat_fluidity_v051/TRAVEL_CURVE_v051.csv",
    "locomotion/coat_fluidity_v051/HEM_RESPONSE_v051.csv",
]
relative += [f"locomotion/coat_fluidity_v051/scripts/{name}" for name in (
    "inspect_coat.py", "build_fluid_coat.py", "cold_validate_coat.py",
    "render_static_coat.py", "render_motion_coat.py", "assemble_static_coat.py",
    "encode_coat.py", "record_body_diagnosis.py")]
relative += [f"locomotion/coat_fluidity_v051/evidence/{name}" for name in (
    "SOURCE_COAT_DIAGNOSIS.json", "FLUID_COAT_BUILD.json", "STATIC_COAT_PROOF.json",
    "COLD_COAT_VALIDATION.json", "ROBOTIC_MOTION_DIAGNOSIS.json",
    "ACTUAL_V051_MOTION_RENDER.json", "NEUTRAL_MODEL_RENDER.json",
    "ENCODED_COAT_VALIDATION.json", "DELIVERY_METADATA.json")]
relative += [f"locomotion/coat_fluidity_v051/previews/{name}" for name in (
    *names.values(), "WTSC_v050_v051_Fabric_Phases.png",
    "DECODED_FULL_COMPARISON.jpg", "DECODED_COAT_DETAIL_COMPARISON.jpg",
    "DECODED_V051_CYCLE_1.jpg", "DECODED_V051_CYCLE_2.jpg",
    "DECODED_V051_CYCLE_3.jpg", "DECODED_V051_CYCLE_4.jpg")]
assert len(relative) == len(set(relative))
files = [{"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": sha(ROOT / name)} for name in relative]
archive = P / "WTSC_Controlled_Fluid_Coat_v051_Review.zip"
assert not archive.exists(), "Never replace an earlier archive"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for item in files:
        z.write(ROOT / item["path"], item["path"])
    z.writestr("ARCHIVE_MANIFEST.json", json.dumps({"files": files}, indent=2))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == {item["path"] for item in files} | {"ARCHIVE_MANIFEST.json"}
assert all(sha(path) == digest for path, digest in expected.items())
handoff = dict(delivery)
handoff["archive"] = {"path": str(archive), "bytes": archive.stat().st_size,
                       "sha256": sha(archive), "zip_crc_verified": True,
                       "file_count": len(files) + 1}
(E / "FINAL_HANDOFF.json").write_text(json.dumps(handoff, indent=2))
print(json.dumps({"archive": handoff["archive"], "private_library": verified}, indent=2))
