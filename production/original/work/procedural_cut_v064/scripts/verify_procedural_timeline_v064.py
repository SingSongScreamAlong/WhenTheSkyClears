"""Verify completed v064 render evidence without opening Blender or changing sources.

Run only after all four workers finish. Reads every native PNG hash and the
current build hash. If delivery evidence exists, links its decode/audio records
to the actual media and the same world-frame manifest. Writes one JSON report.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import sys
import traceback

O = Path(__file__).resolve().parents[1]
R = O.parents[1]
E = O / 'evidence'
REPORT = E / 'PROCEDURAL_TIMELINE_VERIFIED.json'
RANGES = ((1, 600), (601, 1200), (1201, 1800), (1801, 2400))
TOL = 1.1e-4  # Measured Blender RNA update threshold; see precision evidence.
BOUND_TOL = 2e-6
MONOTONIC_TOL = 1e-7
SOURCES = {
    'v040_native': (
        'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend',
        'c3ed3c15055ae5cd242a68964d6980bb8bda3ff6f7f4882d69fa4198e937819f'),
    'v058_native': (
        'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend',
        '13c2aee075315131eac6f85d9d726b766051a84edffa961f4ec38ecf7029a890'),
    'v063_native': (
        'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend',
        'd1d4393c3afc77bf71fb8989bd001da56866baaa7f682216a5f05e54e9523687'),
    'v040_view_movie': (
        'renders/world_v016/WTSC_Full_Knockout_Trailer_View_v040.mp4',
        '2c6c48fa129c14b6915dd9134946152274436375f76686a9cf097b4df0b6e3e7'),
}
WAV_SHA = '0694b2f40f56df5bbadaa23e1c92ac6a048507a8920cebf5b060fc7493368114'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def smoothstep(frame):
    u = min(1.0, max(0.0, ((frame - 1) / 24.0) / 96.0))
    return u * u * (3.0 - 2.0 * u)


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def close(value, expected, tolerance=TOL):
    return finite_number(value) and abs(value - expected) <= tolerance


def verify():
    checks, examples = {}, {}
    build_path = E / 'FULL_CUT_BUILD.json'
    build_hash = sha(build_path)
    build = read_json(build_path)
    native = Path(build['native'])
    native_sha = build['native_sha256']
    checks['current_native_matches_dynamic_build_hash'] = sha(native) == native_sha
    checks['build_preservation_checks_pass'] = (
        build.get('all_checks_pass') is True
        and bool(build.get('checks'))
        and all(v is True for v in build['checks'].values()))
    checks['global_driver_contract_0_to_96_seconds_no_palette_keys'] = (
        close(build.get('start_seconds'), 0.0, 0.0)
        and close(build.get('finish_seconds'), 96.0, 0.0)
        and build.get('palette_keyframes') == 0
        and build.get('controller') == 'V064 | global procedural color loss | BOTH children'
        and build.get('property') == 'charcoal_progress')

    precision_path = E / 'FLOAT_DRIVER_PRECISION.json'
    precision = read_json(precision_path)
    precision_rows = precision['rows']
    measured = {}
    precision_valid = len(precision_rows) == 81
    for field, summary_key in (('original', 'max_original_error'),
                               ('evaluated', 'max_evaluated_error'),
                               ('mix', 'max_mix_error')):
        maximum = max(abs(r[field] - smoothstep(r['frame'])) for r in precision_rows)
        reported = precision.get(summary_key)
        measured[summary_key] = maximum
        precision_valid = (precision_valid and close(reported, maximum, 1e-10)
                           and maximum <= TOL)
    if 'native_sha256' in precision:
        precision_valid = precision_valid and precision['native_sha256'] == native_sha
    checks['measured_native_RNA_precision_supports_tolerance'] = precision_valid
    precision_policy = {
        'evidence_file': precision_path.name, 'evidence_sha256': sha(precision_path),
        'native_probe_samples': len(precision_rows), 'measured_maximum_errors': measured,
        'absolute_value_tolerance': TOL,
        'applies_to': ['ideal global smoothstep progress', 'mix binding',
                      'saturation binding', 'start/end charcoal values'],
        'reason': 'Measured native RNA/animation update threshold can retain values until a change exceeds approximately 1e-4; the 81-sample maximum is recorded above.',
        'monotonic_drop_tolerance': MONOTONIC_TOL, 'bounds_tolerance': BOUND_TOL,
        'unchanged_requirements': 'Exact frame coverage/order, source/native/PNG hashes, absolute frame clock, monotonic progression, and no worker/shot reset.',
        'pixels_repaired_or_reinterpolated': False}
    expected_workers = {f'world_worker_{a:04d}_{b:04d}.json' for a, b in RANGES}
    found_workers = {p.name for p in E.glob('world_worker_*.json')}
    checks['exactly_four_expected_worker_ranges'] = found_workers == expected_workers
    worker_summary, rows = [], []
    worker_flags = True
    resume_flags = True
    resumed_total = 0
    rendered_or_legacy_fresh_total = 0
    row_order = True
    for first, last in RANGES:
        path = E / f'world_worker_{first:04d}_{last:04d}.json'
        worker = read_json(path)
        frames = worker['frames']
        observed = [r.get('frame') for r in frames]
        row_order = row_order and observed == list(range(first, last + 1))
        flags = (
            worker.get('native_sha256') == native_sha
            and worker.get('native_unchanged') is True
            and worker.get('source_world_frames_fresh') is True
            and worker.get('all_shared_material_driver_checks_pass') is True
            and worker.get('resolution') == [1280, 720])
        worker_flags = worker_flags and flags
        resumed = worker.get('resumed_existing_frames', [])
        provenance_ok = (isinstance(resumed, list)
                         and all(isinstance(f, int) and not isinstance(f, bool)
                                 and first <= f <= last for f in resumed)
                         and len(resumed) == len(set(resumed)))
        has_row_provenance = any('rendered_in_session' in row for row in frames)
        if has_row_provenance:
            replayed = [row.get('frame') for row in frames
                        if row.get('rendered_in_session') is False]
            provenance_ok = (provenance_ok
                             and all(isinstance(row.get('rendered_in_session'), bool)
                                     for row in frames)
                             and replayed == resumed)
        else:
            provenance_ok = provenance_ok and not resumed
        if resumed:
            provenance_ok = (provenance_ok
                             and worker.get('native_driver_replay_for_resumed_frames') is True)
        declared_tolerance = worker.get('driver_numeric_tolerance', 2e-6)
        provenance_ok = (provenance_ok and finite_number(declared_tolerance)
                         and 0 < declared_tolerance <= TOL)
        resume_flags = resume_flags and provenance_ok
        resumed_total += len(resumed)
        rendered_count = sum(row.get('rendered_in_session', True) is True for row in frames)
        rendered_or_legacy_fresh_total += rendered_count
        worker_summary.append({
            'file': path.name, 'file_sha256': sha(path), 'frames': len(frames),
            'range': [first, last], 'native_sha256': worker.get('native_sha256'),
            'native_and_driver_flags_pass': flags,
            'declared_driver_tolerance': declared_tolerance,
            'resumed_existing_frame_count': len(resumed),
            'resumed_frame_range': [min(resumed), max(resumed)] if resumed else None,
            'rendered_in_session_or_legacy_fresh_count': rendered_count,
            'row_provenance_schema': 'explicit session/replay' if has_row_provenance else 'legacy fresh worker',
            'same_native_resume_provenance_pass': provenance_ok})
        rows.extend(frames)
    checks['all_workers_use_current_native_and_fresh_driver_checks'] = worker_flags
    checks['resumed_frames_have_explicit_same_native_driver_replay_provenance'] = resume_flags
    checks['all_2400_frames_consecutive_once_in_order'] = (
        row_order and [r.get('frame') for r in rows] == list(range(1, 2401)))
    if not checks['all_2400_frames_consecutive_once_in_order']:
        raise ValueError('Worker rows are missing, duplicated, reordered or outside 1..2400')

    errors = {'progress_vs_global_smoothstep': 0.0, 'mix_vs_progress': 0.0,
              'saturation_vs_one_minus_progress': 0.0, 'seconds_vs_absolute_frame': 0.0}
    bad = {k: [] for k in ('values', 'bounds', 'progress', 'mix', 'saturation',
                           'seconds', 'monotonic', 'charcoal_hold', 'png_hash')}
    previous = None
    frame_hashes = {}
    progress_range = [1.0, 0.0]
    for row in rows:
        f = row['frame']
        p, mix, sat = (row.get(k) for k in ('progress', 'mix_progress', 'pigment_saturation'))
        if not all(finite_number(v) for v in (p, mix, sat)):
            bad['values'].append(f)
            continue
        want = smoothstep(f)
        errors['progress_vs_global_smoothstep'] = max(errors['progress_vs_global_smoothstep'], abs(p - want))
        errors['mix_vs_progress'] = max(errors['mix_vs_progress'], abs(mix - p))
        errors['saturation_vs_one_minus_progress'] = max(errors['saturation_vs_one_minus_progress'], abs(sat - (1 - p)))
        progress_range = [min(progress_range[0], p), max(progress_range[1], p)]
        if not all(-BOUND_TOL <= v <= 1 + BOUND_TOL for v in (p, mix, sat)): bad['bounds'].append(f)
        if abs(p - want) > TOL: bad['progress'].append(f)
        if abs(mix - p) > TOL: bad['mix'].append(f)
        if abs(sat - (1 - p)) > TOL: bad['saturation'].append(f)
        if previous is not None and p < previous - MONOTONIC_TOL: bad['monotonic'].append(f)
        previous = p
        if f >= 2305 and (abs(p - 1) > TOL or abs(sat) > TOL): bad['charcoal_hold'].append(f)
        if 'seconds' in row:
            sec = row['seconds']
            if not finite_number(sec) or abs(sec - (f - 1) / 24) > 1e-8:
                bad['seconds'].append(f)
            else:
                errors['seconds_vs_absolute_frame'] = max(
                    errors['seconds_vs_absolute_frame'], abs(sec - (f - 1) / 24))
        expected_hash = row.get('sha256', '')
        path = O / 'previews/world_frames' / f'{f:04d}.png'
        if (not isinstance(expected_hash, str)
                or re.fullmatch(r'[0-9a-f]{64}', expected_hash) is None
                or not path.is_file() or sha(path) != expected_hash):
            bad['png_hash'].append(f)
        frame_hashes[f] = expected_hash
    for key, failures in bad.items():
        checks['every_frame_' + key + '_valid'] = not failures
        if failures: examples[key] = {'count': len(failures), 'first_frames': failures[:10]}
    checks['starts_full_color_and_charcoal_by_frame_2305'] = (
        close(rows[0]['progress'], 0) and close(rows[2304]['progress'], 1)
        and close(rows[-1]['progress'], 1))

    joins = []
    for before, after in ((600, 601), (1056, 1057), (1200, 1201), (1800, 1801)):
        a, b = rows[before - 1], rows[after - 1]
        actual_delta = b['progress'] - a['progress']
        expected_delta = smoothstep(after) - smoothstep(before)
        ok = close(a['progress'], smoothstep(before)) and close(b['progress'], smoothstep(after)) and close(actual_delta, expected_delta, 2 * TOL)
        joins.append({'frames': [before, after], 'progress': [a['progress'], b['progress']],
                      'actual_step': actual_delta, 'expected_step': expected_delta, 'pass': ok})
    checks['global_progress_has_no_worker_or_first_danger_join_reset'] = all(r['pass'] for r in joins)
    png_numbers = sorted(int(p.stem) for p in (O / 'previews/world_frames').glob('*.png')
                         if p.stem.isdigit())
    checks['render_directory_contains_exactly_2400_numbered_PNGs'] = png_numbers == list(range(1, 2401))

    preserved = {}
    for label, (relative, expected) in SOURCES.items():
        path = R / relative
        actual = sha(path) if path.is_file() else None
        preserved[label] = {'path': relative, 'expected_sha256': expected,
                            'actual_sha256': actual, 'unchanged': actual == expected}
    checks['v040_v058_v063_natives_and_v040_view_preserved'] = all(r['unchanged'] for r in preserved.values())

    delivery_path = E / 'FULL_CUT_DELIVERY_v064.json'
    delivery_summary = {'present': delivery_path.is_file(), 'verified': None}
    if delivery_path.is_file():
        delivery = read_json(delivery_path)
        before_keys = set(checks)
        checks['delivery_same_native_and_unchanged'] = (
            delivery.get('native_sha256') == native_sha and delivery.get('native_unchanged') is True
            and Path(delivery.get('native', '')).resolve() == native.resolve())
        checks['delivery_fresh_picture_no_frame_synthesis'] = (
            delivery.get('source_frames') == [1, 2400]
            and delivery.get('source_resolution') == [1280, 720]
            and delivery.get('cached_old_world_used') is False
            and delivery.get('frame_interpolation') is False
            and delivery.get('duplicate_or_dropped_frames_added_by_packager') is False
            and delivery.get('unchanged_mask_and_credits_signature') is True)
        manifest = read_json(delivery['world_frame_hash_manifest'])
        checks['delivery_world_frame_hashes_match_every_verified_worker_frame'] = (
            [r.get('frame') for r in manifest] == list(range(1, 2401))
            and all(r.get('sha256') == frame_hashes.get(r.get('frame')) for r in manifest))

        media = {}
        for key, filename, count, seconds, has_audio in (
            ('primary', 'WTSC_Procedural_Full_Knockout_v064.mp4', 2544, 106, True),
            ('unmasked_mute_world_review', 'WTSC_Procedural_Unmasked_World_v064.mp4', 2400, 100, False)):
            record = delivery.get(key)
            path = O / 'previews' / filename
            if key == 'unmasked_mute_world_review' and key in delivery and record is None:
                listed = [Path(p).name for p in delivery.get('deliveries', [])]
                checks['optional_unmasked_review_omission_matches_delivery_list'] = filename not in listed
                media[key] = {'file': filename, 'omitted_by_packager': True,
                              'verified': None}
                continue
            valid_record = isinstance(record, dict)
            if valid_record:
                clock_ok = (
                    record.get('decoded_frames') == count and close(record.get('fps'), 24, 0)
                    and close(record.get('duration_seconds'), seconds, .011)
                    and close(record.get('all_pts_max_error_seconds'), 0, 1e-8)
                    and record.get('has_audio') is has_audio)
                media_hash = sha(path) if path.is_file() else None
                file_ok = (media_hash == record.get('sha256') and path.is_file()
                           and path.stat().st_size == record.get('bytes')
                           and record.get('under_20000000_bytes') is True
                           and path.stat().st_size < 20_000_000)
            else:
                clock_ok = file_ok = False
                media_hash = None
            checks[key + '_decode_clock_and_actual_file_linked'] = clock_ok and file_ok
            media[key] = {'file': filename, 'decoded_frames': record.get('decoded_frames') if valid_record else None,
                          'sha256': media_hash, 'pass': clock_ok and file_ok}
        audio = delivery.get('audio_verification', {})
        wav = R / 'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
        gains = audio.get('single_90_to_100s_fade_gain_checks', [])
        expected_gain_windows = [90.5, 92, 95, 98, 99.5]
        reported_gain_windows = [g.get('seconds') for g in gains]
        checks['delivery_original_music_once_90_to_100_fade_and_silent_credits'] = (
            audio.get('original_wav_sha256') == WAV_SHA and wav.is_file() and sha(wav) == WAV_SHA
            and audio.get('sample_rate') == 48000 and audio.get('channels') == 2
            and audio.get('checked_duration_seconds') == 106
            and audio.get('start_seconds') == 0 and audio.get('fade_count') == 1
            and audio.get('fade_seconds') == [90, 100]
            and finite_number(audio.get('zero_lag_correlation_before_fade'))
            and audio['zero_lag_correlation_before_fade'] > .98
            and finite_number(audio.get('silent_100_to_106s_rms')) and audio['silent_100_to_106s_rms'] < .0001
            and finite_number(audio.get('silent_100_to_106s_peak')) and audio['silent_100_to_106s_peak'] < .001
            and finite_number(audio.get('normalized_error_vs_original_with_one_fade'))
            and audio['normalized_error_vs_original_with_one_fade'] < .20
            and all(t in expected_gain_windows for t in reported_gain_windows)
            and reported_gain_windows == [t for t in expected_gain_windows if t in reported_gain_windows]
            and all(finite_number(g.get('measured_gain'))
                    and finite_number(g.get('single_linear_fade_expected_gain'))
                    and abs(g['measured_gain'] - g['single_linear_fade_expected_gain']) < .04 for g in gains))
        delivery_summary.update({
            'file_sha256': sha(delivery_path), 'media': media,
            'verified': all(checks[k] for k in set(checks) - before_keys),
            'audio_fade_seconds': audio.get('fade_seconds'),
            'unmasked_review_exported': isinstance(delivery.get('unmasked_mute_world_review'), dict),
            'fade_gain_sample_seconds': reported_gain_windows,
            'fade_gain_windows_not_reported': [t for t in expected_gain_windows if t not in reported_gain_windows],
            'fade_gain_window_policy': 'Packager omits source-energy windows <=1e-9; every reported non-silent window must match the single expected fade. Original WAV hash, full-duration waveform error and silent credits remain required.',
            'silent_credits_rms': audio.get('silent_100_to_106s_rms'),
            'silent_credits_peak': audio.get('silent_100_to_106s_peak')})

    checks['native_and_build_unchanged_during_verification'] = (
        sha(native) == native_sha and sha(build_path) == build_hash)
    return {
        'all_checks_pass': all(checks.values()), 'verified_utc': datetime.now(timezone.utc).isoformat(),
        'checks': checks, 'native': str(native), 'native_sha256': native_sha,
        'build_evidence_sha256': build_hash, 'frame_count': len(rows), 'fps': 24,
        'picture_frames': [1, 2400], 'charcoal_hold_frames': [2305, 2400],
        'progress_range': progress_range, 'maximum_errors': errors, 'tolerance': TOL,
        'numeric_precision_policy': precision_policy,
        'resumed_existing_frame_count': resumed_total,
        'rendered_in_session_or_legacy_fresh_count': rendered_or_legacy_fresh_total,
        'joins': joins, 'worker_manifests': worker_summary, 'failures': examples,
        'preserved_originals': preserved, 'delivery': delivery_summary,
        'scope': 'Every frame of native-rendered procedural palette evidence and actual PNG hashes. Same-native resumed PNGs and native driver replay are reported separately from frames rendered in the current session. Diagnostic/archive folders are not scanned. Delivery decode/audio checks are linked only when the completed delivery record exists.',
        'limits': 'No Blender invocation, native save, media synthesis or new decode. This does not judge art, acting, contact anatomy, motion joins, title readability or real-time playback quality.'
    }


def main():
    try:
        report = verify()
    except Exception as exc:
        report = {'all_checks_pass': False, 'verified_utc': datetime.now(timezone.utc).isoformat(),
                  'exception': repr(exc), 'traceback': traceback.format_exc(),
                  'scope': 'Incomplete evidence verification; no source or native was modified.'}
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print('V064_PROCEDURAL_TIMELINE', json.dumps({
        'pass': report['all_checks_pass'], 'report': str(REPORT),
        'failed': [k for k, v in report.get('checks', {}).items() if not v],
        'exception': report.get('exception')}), flush=True)
    return 0 if report['all_checks_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
