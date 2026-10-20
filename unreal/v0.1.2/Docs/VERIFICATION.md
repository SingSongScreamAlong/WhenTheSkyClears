# v0.1.2 room-study verification

{
  "utc": "2026-10-20T01:15:49.360718+00:00",
  "version": "0.1.2 art study",
  "project": "WTSC_LOCAL_WORKSPACE\\WTSC_Survival_Prototype_v0_1_2\\WTSC_Survival.uproject",
  "package": "WTSC_LOCAL_WORKSPACE\\WTSC_Survival_Prototype_v0_1_2\\Deliverables\\WTSC_Shelter_Study_Win64_v0.1.2_ArtStudy.zip",
  "package_bytes": 354521939,
  "package_sha256": "4f6fc6b64b82be5b74a1b2b1c3870c57ceae72890a7d287565864c22d2dee7f7",
  "package_crc_verified": true,
  "runtime_files": 48,
  "tests_passed": 11,
  "test_game_seconds": 57.42914581298828,
  "test_type": "Actual native engine simulated key events, not an OS/human playtest",
  "matched_before_after": true,
  "room_geometry": {
    "parts": 748,
    "vertices": 75207,
    "triangles": 34535,
    "material_slots": 20
  },
  "retained_detailed_props": 7,
  "video_bytes": 2025022,
  "video_seconds": 11.0,
  "real_video_frames": 327,
  "actual_capture_fps": 29.678366617428082,
  "runtime_fps_during_art_capture": 164.18218347474112,
  "no_duplicated_smoothing_frames": true,
  "art_approved": false,
  "source_provenance": "Code-authored geometry and SVG surface graphics with editable sources, not imagegen mockups or artist hand-painted frames",
  "remaining_gaps": [
    "Child cutout shoulder gaps, stiffness, expression and companion behavior remain unresolved",
    "One room only: upper floor, other rooms, shop and exterior remain at previous prototype quality",
    "Foreground/photo-prop/painted-backdrop style integration is still an art study requiring user review",
    "No new gameplay systems or map expansion; upstairs remains inaccessible"
  ],
  "interruption": "First packaged regression lost its process connection and stopped before a final receipt; log retained; complete rerun passed through existing Desktop Commander background route"
}

The eleven checks preserve ObjectiveFix: fresh state, cache arrival, crouched reach, finite search, no duplicate loot, home arrival objective, deposit before commit, completed storage, save/readback, food/water use, reset. Full event-level objectives and inventory states are in Evidence/Regression/PackagedGameplayReplay.json.

MatchedCameraComparison.json proves identical focus-camera and initial character fields for the actual before/after stills. The old full shelter view remains beside a final overview at its original framing. Art-study completion is not a regression pass or art approval.

ActualCaptureFrames.csv retains each real viewport sample, wall timestamp, engine frame ID, dimensions, size and checksum. VFR movie timing preserves those real intervals; full decode counts match. No fake high-rate interpolation or duplicated-frame smoothing is used. The clip is silent.

BaselinePreservationFinal.json verifies the prior 102-file checkpoint and original source copies. All v0.1.1 deliverables remain untouched. Recovery logs and earlier failed-material review remain in Evidence.
