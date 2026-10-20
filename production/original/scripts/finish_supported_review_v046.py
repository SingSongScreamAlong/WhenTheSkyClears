"""Seal local v046 review notes without resaving any Blender source or movie."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / 'notes/world_v016'


def read(name):
    return json.loads((NOTES / name).read_text(encoding='utf-8'))


def write(name, value):
    (NOTES / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


build = read('motion_trial_build_v046.json')
export = read('export_completed_v046.json')
qa = read('media_qa_v046.json')
cold = [read('v046_cold_' + name + '.json') for name in
        ['baseline_preview', 'candidate_keys', 'candidate_preview']]

verified = {}
for path, expected in build['preserved_inputs'].items():
    actual = digest(path)
    assert actual == expected, path
    verified[path] = actual
for key in ['source', 'baseline_source', 'baseline', 'candidate', 'comparison']:
    item = export[key]
    assert digest(item['path']) == item['sha256'], item['path']
    assert Path(item['path']).stat().st_size == item['bytes']
for row in export['critical_actual_4K_frames']:
    for key in ['baseline_4K', 'candidate_4K']:
        item = row[key]
        assert digest(item['path']) == item['sha256'], item['path']
assert digest(build['snapshot']['snapshot']) == build['snapshot']['snapshot_sha256']
assert all(v == 0 for v in build['all120_errors'].values())
assert all(c['cold_open_verified'] and c['all120_frozen_stage_error'] == 0 for c in cold)
assert all(c['world_fingerprint'] == build['world_protected_fingerprint'] for c in cold)
assert cold[0]['view_settings'] == cold[2]['view_settings']
assert cold[0]['master_view_settings'] == cold[2]['master_view_settings']
heads = cold[2]['head_exposures']
assert len(heads) == 120 and all(row['visible_girl_head'] for row in heads)
assert export['frame_count'] == 120 and export['fps'] == 24

now = datetime.now(timezone.utc).isoformat()
evidence = ROOT / 'renders/world_v016/integration_v046/review_evidence'
review = {
    'completed_utc': now,
    'status': 'Bounded review complete; preserved candidate, not artistic acceptance.',
    'source_sha256': export['source']['sha256'],
    'method': {
        'actual_candidate_chronology': '40 actual 1080p decoded frames at 8 fps, all five chronology sheets inspected.',
        'critical_boot_motion': 'All 22 consecutive actual HD samples, frames 1837-1858, inspected.',
        'post_stop': '14 matched actual HD samples at three-frame intervals, 1881-1920, all four sheets inspected.',
        'shot_size': 'Eight matched whole-frame baseline/candidate samples inspected.',
        'native4K': 'Actual 3840x2160 rendered images; native-pixel head, boot, recovery, and fingertip crops inspected.',
        'native4K_frames': build['critical_4K_frames'],
        'limits': 'Decoded chronological samples and full-file decode, not a claim of real-time audiovisual playback or every 4K movie frame.',
    },
    'visible_improvements': [
        'Distinct boot and shin paths reduce the folded-boy-leg overlap with the supporting leg; negative space is visibly better.',
        'The girl stabilizes and turns toward the boy; the boy attends to his thigh, prepares, reaches, and rises. The stop reads as recovery.',
        'The painterly charcoal identities and near-age proportions remain; the boy is slightly larger at his standing basis.',
        'The retained v045c background separation and original coherent foreground remain visible in both matched renders.',
    ],
    'remaining_art_faults': [
        {'priority': 'major', 'frames': [1844, 1845], 'global_seconds': [76.791666667, 76.833333333],
         'finding': 'Girl passing head is a flat faceted charcoal disc with paint streaks, switching to the reflected original painted profile at 1846. This is not a convincing turn.',
         'future_work': 'Purpose-drawn turning silhouettes with neck and shoulder response. No drawing or timing was silently changed in v046.'},
        {'priority': 'major', 'finding': 'Angular wrists, shoulders, elbows, and exposed forearm wedges still reveal planar cutout construction.'},
        {'priority': 'major', 'finding': 'Late hand meeting is a projected light fingertip cue; a small gap remains in native crops. It is not an interlocked or load-bearing clasp. Feet and thigh brace carry weight.'},
        {'priority': 'unfinished', 'finding': 'Route ends in the recovery/offered-hand pose. No authored restart or first step is included.'},
        {'priority': 'unfinished', 'finding': 'Original foreground repeats and existing FXv003 limitations remain. Future crater, debris, lighting, and FX work is pending.'},
    ],
    'technical_checks_are_not_artistic_acceptance': True,
    'source_drawings_and_timing_preserved': True,
    'full_trailer_propagation': False,
    'artistic_acceptance': False,
    'evidence_directory': str(evidence),
    'head_evidence': qa['native4K_head_exposure_sheet'],
    'boot_evidence': qa['native4K_boot_negative_space_sheet'],
    'recovery_evidence': qa['native4K_support_rise_sheets'],
    'hand_evidence': qa['native4K_fingertip_cue_sheet'],
}
write('visual_review_v046.json', review)

staging = {
    'source_sha256': export['source']['sha256'],
    'source_motion': build['snapshot'],
    'configured': build['configured'],
    'anchor': build['anchor'],
    'scale': build['scale'],
    'frames': [1801, 1920], 'fps': 24,
    'all120_errors': build['all120_errors'],
    'protected_world_fingerprint': build['world_protected_fingerprint'],
    'cold_open_fingerprints_match': True,
    'cold_open_all120_frozen_stage_errors': [c['all120_frozen_stage_error'] for c in cold],
    'head_exposures_all120': heads,
    'head_exposure_limit': 'One visible drawing per frame checks exposure integrity only; frames 1844-1845 remain an artistic defect.',
    'camera_comparison': 'Camera matrices and visual data preserved. Process-local RNA session_uid excluded from cold-open comparison.',
    'contact_limit': 'Zero evaluated foot/sole geometry errors preserve the existing foot contract; this does not establish cinematic contact or artistic motion acceptance.',
    'original_light_binding': build['new_materials_bound_to_actual_existing_light'],
    'contacts': build['contacts'],
    'frozen_baseline_staging_receipt': str(NOTES / 'motion_trial_build_v046.json'),
}
write('frozen_staging_comparison_v046.json', staging)

checkpoint = {
    'completed_utc': now,
    'status': 'Preserved v046 local review candidate. Hold; no full-trailer propagation.',
    'native': export['source'],
    'baseline_native': export['baseline_source'],
    'motion_snapshot': build['snapshot'],
    'previews': {key: export[key] for key in ['baseline', 'candidate', 'comparison']},
    'native_saved_resolution': [3840, 2160],
    'review_resolution': [1920, 1080],
    'comparison_resolution': [3840, 1080],
    'frames': 120, 'fps': 24, 'global_range': [1801, 1920],
    'all_three_movies_full_decode_passed': True,
    'critical_4K_frames': export['critical_actual_4K_frames'],
    'all120_errors': build['all120_errors'],
    'protected_world_fingerprint': build['world_protected_fingerprint'],
    'preserved_inputs_rechecked': verified,
    'preserved_input_count': len(verified),
    'audio_original_75_80_correlation': qa['audio_original_75_80_correlation'],
    'baseline_candidate_audio_max_sample_difference': qa['baseline_candidate_audio_max_sample_difference'],
    'visual_review': str(NOTES / 'visual_review_v046.json'),
    'staging_receipt': str(NOTES / 'frozen_staging_comparison_v046.json'),
    'media_qa': str(NOTES / 'media_qa_v046.json'),
    'guide': str(ROOT / 'WHEN_THE_SKY_CLEARS_SUPPORTED_REVIEW_v046.txt'),
    'source_not_resaved_by_review': True,
    'owned_render_jobs_remaining': 0,
    'artistic_acceptance': False,
    'full_trailer_propagated': False,
    'library': 'Local files only. No upload or bypass attempted.',
}
write('integration_checkpoint_v046.json', checkpoint)
export['status'] = 'Actual previews, critical4K images, decoded-sample review and local handoff complete. Preserved review candidate; not artistic acceptance.'
export['visual_review'] = str(NOTES / 'visual_review_v046.json')
write('export_completed_v046.json', export)
qa['decoded_sample_and_native_crop_inspection_complete'] = True
qa['artistic_review_pending'] = True
qa['artistic_review_pending_meaning'] = 'Further craft refinement and human review remain; local decoded-sample inspection is complete.'
write('media_qa_v046.json', qa)
write('render_status_v046.json', {
    'phase': 'Complete; preserved v046 review candidate; hold for review.',
    'owned_render_jobs_remaining': 0,
    'candidate': export['candidate']['path'],
    'comparison': export['comparison']['path'],
    'native': export['source']['path'],
    'native_4K_preserved': True,
    'decoded_sample_review_complete': True,
    'artistic_acceptance': False,
    'full_trailer_propagated': False,
})

guide = f"""WHEN THE SKY CLEARS -- SUPPORTED RECOVERY REVIEW v046
Review completed {now}

RESULT
Clear acting/blocking improvement over v006 on the same retained v045c art.
The folded leg reads better and the recovery has distinct roles. Preserved as a
local review candidate. This is not full-trailer cinematic acceptance.

OPEN THESE
Candidate (actual 5 seconds, 120 frames / 24 fps, 3.12 MB, 1080p):
{export['candidate']['path']}

Matched comparison (v006 LEFT / v007 RIGHT, both freshly rendered on v045c,
same camera, route, EEVEE, AA, light and FXv003; 5.35 MB):
{export['comparison']['path']}

Editable Blender source (saved 3840 x 2160):
{export['source']['path']}
Master scene: {export['master_scene']}
World scene: {export['world_scene']}
Global frames 1801-1920 inclusive, 75-80 seconds, 24 fps.
Native SHA256: {export['source']['sha256']}
Movie previews are 1080p review renders. The side-by-side file is 3840x1080,
two 1080p panels; it is not a 4K review movie. Native defaults remain UHD 4K.

ACTUAL 4K EVIDENCE
Directory: {evidence.parent}
Native_v046_<frame>_4K.png: {', '.join(str(f) for f in build['critical_4K_frames'])}
Matched native-pixel crops and decoded chronology:
{evidence}
Five baseline 4K keys reuse verified v045c renders; missing baseline keys
1844, 1845, 1846 and 1889 were freshly rendered. The manifest identifies each.

ART LIMITS TO KEEP VISIBLE
1. Girl passing head at 1844-1845 / 76.792-76.833s is a faceted flat charcoal
   disc before switching to the reflected painted profile at 1846. It needs
   purpose-drawn transition silhouettes and neck/shoulder response.
2. Wrists, shoulders and elbows remain angular and planar. Late fingertips
   nearly meet; this is a light projected cue, not a load-bearing clasp.
   The feet and thigh brace carry weight.
3. The fixed route ends in recovery. There is no authored restart/first step.
4. Foreground repeats and current FXv003 limits remain unfinished. Future
   crater, debris and FX changes have not been integrated here.
Original v007 drawings and timing were preserved, including the head defect.

VERIFIED SCOPE
Appended sealed WTSC_BATTLEFIELD_DRAWN_PAIR_v007, configured at frame1801,
duration scale1, root motion enabled; no second retime or lead-in applied.
Existing camera, world, route, source light, FX clock and contacts preserved.
All120 frame camera/travel/FX/light/receiver/foot/sole errors are zero.
One visible girl-head exposure per frame; exposure integrity is not art approval.
Both previews use actual sequential native EEVEE renders, AA32 and original
color settings. All three movies decoded all120 frames. Original music75-80s
retained; baseline/candidate audio samples match.
Review used actual decoded samples and actual native4K crops. No claim of
real-time movie playback, every4Kmovieframe inspection, or artistic acceptance.
{len(verified)} preserved input files rehashed successfully after export/review.
No full-trailer propagation, new FX, foreground experiments, title/FPS/duration
changes, or Library upload/bypass. Source files were not resaved by review.

DETAILED RECEIPTS
{NOTES / 'integration_checkpoint_v046.json'}
{NOTES / 'visual_review_v046.json'}
{NOTES / 'frozen_staging_comparison_v046.json'}
{NOTES / 'media_qa_v046.json'}
{NOTES / 'export_completed_v046.json'}
"""
(ROOT / 'WHEN_THE_SKY_CLEARS_SUPPORTED_REVIEW_v046.txt').write_text(guide, encoding='utf-8')
print(json.dumps({'status': checkpoint['status'], 'preserved_input_count': len(verified),
                  'native_sha256': export['source']['sha256'], 'guide': checkpoint['guide']}, indent=2))
