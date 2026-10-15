"""Attach pinned source categories and verify short donor placeholders offline.

Requires a donor inventory and the fingerprinted AFL metadata in --source-cache.
FFmpeg decodes to memory only; this tool never plays or writes recordings.
Output remains candidate data without Final Bout cue or performer assignments.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import subprocess
import struct
import probe_sources as p
from inventory_donor import load_labels

def curate(inventory_path: Path, donor_iso: Path, source_cache: Path, ffmpeg: Path):
    raw = inventory_path.read_bytes()
    x = json.loads(raw)
    labels = {name: load_labels(source_cache, name) for name in p.ARCHIVES}
    p.require(donor_iso.stat().st_size == 3020816384, 'ISO size')
    decoder_version = subprocess.run([str(ffmpeg), '-version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    x['curation_status'] = 'source categories only; no Final Bout cue, transcript or actor assignments'
    x['inventory_sha256'] = p.sha(raw)
    x['source_code_pin'] = 'https://github.com/z3xox/BT3-Decompiled/tree/95b950367364137130758ef82a218e607a54b703'
    wave_categories = {**{i: 'hit-reaction-0' for i in range(6)}, **{i: 'hit-reaction-1' for i in range(6, 10)}, **{i: 'hit-reaction-3' for i in range(12, 14)}, **{i: 'attack-record-voice-1' for i in range(16, 19)}, **{i: 'attack-record-voice-2' for i in range(19, 22)}, **{i: 'attack-record-voice-3' for i in range(22, 26)}, 30: 'guarded-hit-reaction', 31: 'guarded-hit-reaction', 33: 'ki-blast-emission', 34: 'ki-blast-emission', 35: 'ki-charge-start', 36: 'form-change-animation'}
    for cls in range(2, 5):
        for i in range(37 + cls * 4, 41 + cls * 4):
            wave_categories[i] = 'technique-class-' + str(cls)
    for cls in (0, 1):
        for i in range(37 + cls * 4, 40 + cls * 4):
            wave_categories[i] = 'technique-class-' + str(cls)
    adx_categories = {0: 'generic-intro-0', 1: 'generic-intro-1', 3: 'generic-victory-0', 4: 'generic-victory-1', 42: 'non-winning-result'}
    for cls in range(5):
        for i in range(83 + cls * 2, 85 + cls * 2):
            adx_categories[i] = 'technique-class-' + str(cls)
    checks = {}
    cached_banks = {}
    with donor_iso.open('rb') as iso:

        def read(off, size):
            iso.seek(off)
            d = iso.read(size)
            p.require(len(d) == size, 'short read')
            return d

        def check(data, codec, samples, rate, driver_stop=None):
            if codec == 'vag':
                header = bytearray(48)
                header[:4] = b'VAGp'
                struct.pack_into('>I', header, 4, 32)
                struct.pack_into('>I', header, 12, len(data))
                struct.pack_into('>I', header, 16, rate)
                data = header + data
            run = subprocess.run([str(ffmpeg), '-hide_banner', '-loglevel', 'error', '-f', codec, '-i', 'pipe:0', '-af', 'atrim=end_sample=' + str(samples), '-f', 's16le', '-c:a', 'pcm_s16le', 'pipe:1'], input=data, capture_output=True, check=True)
            p.require(len(run.stdout) == samples * 2, 'decoded count')
            vals = struct.unpack('<' + 'h' * samples, run.stdout)
            active = vals[:driver_stop] if driver_stop is not None else vals
            return {'samples': samples, 'rate': rate, 'pcm_sha256': p.sha(run.stdout), 'peak': max(map(abs, vals), default=0), 'all_zero_pcm': not any(vals), 'driver_stop_samples': driver_stop, 'driver_stop_peak': max(map(abs, active), default=0), 'driver_stop_all_zero_pcm': not any(active), 'decoder': decoder_version, 'method': 'offline pipe decode, no playback'}
        p.require(p.sha(read(32768, 2048)) == p.PVD_SHA256, 'PVD mismatch')
        for name, (lba, _, count, table_hash, _) in p.ARCHIVES.items():
            p.require(p.sha(read(lba * 2048, 8 + count * 8 + 8)) == table_hash, 'AFS table mismatch')
        for bank in x['banks']:
            p.require(bank['label'] == labels['PZS3US1'][bank['index']], 'Bank label mismatch')
            for w in bank['waves']:
                w['candidate_category'] = wave_categories.get(w['index'])
                if 37 <= w['index'] <= 44:
                    w['category_source'] = 'src/battle/btl_char_api_2.c:BtlCharApi_PlayTechniqueSound + src/battle/eft_shot.c:EftShot_PlayFireSound'
                    w['api_supported_category'] = 'technique-class-' + str((w['index'] - 37) // 4)
                    w['runtime_caller_found_for_slot'] = w['index'] not in (40, 44)
                elif 45 <= w['index'] <= 56:
                    w['category_source'] = 'src/battle/btl_char_sound.c:BtlCharSnd_PlayTechSounds'
                key = w['adpcm_sha256']
                if w['duration_upper_bound_seconds'] < 0.1 and key not in checks:
                    if bank['index'] not in cached_banks:
                        data = read(1990 * 2048 + bank['archive_offset'], bank['pak_size'])
                        p.require(p.sha(data) == bank['pak_sha256'], 'bank changed')
                        cached_banks[bank['index']] = data
                    data = cached_banks[bank['index']]
                    start = bank['members'][0][0] + w['offset']
                    sample = data[start:start + w['size']]
                    p.require(p.sha(sample) == key, 'wave mismatch')
                    checks[key] = check(sample, 'vag', w['max_decoded_samples'], w['sample_rate'], w['first_end_decoded_samples'])
                w['placeholder_pcm_check'] = checks.get(key)
                w['verified_silent_placeholder'] = checks.get(key, {}).get('driver_stop_all_zero_pcm', False)
        for block in x['adx_blocks']:
            block['character_id'] = (block['start'] - 48874) // 100
            block['us1_bank_index'] = 3194 + block['character_id']
            for r in block['entries']:
                p.require(r['label'] == labels['PZS3US2'][r['index']], 'ADX label mismatch')
                r['candidate_category'] = adx_categories.get(r['line'])
                key = r['sha256']
                if r['duration'] < 0.1 and key not in checks:
                    data = read(715866 * 2048 + r['archive_offset'], r['size'])
                    p.require(p.sha(data) == key, 'ADX mismatch')
                    checks[key] = check(data, 'adx', r['samples'], r['sample_rate'])
                r['placeholder_pcm_check'] = checks.get(key)
                r['verified_silent_placeholder'] = checks.get(key, {}).get('all_zero_pcm', False)
        for r in x['menu_announcer_candidates']:
            r['candidate_category'] = None
            if 65060 <= r['index'] < 65116:
                r['announcer_id'] = (r['index'] - 65060) // 7
                r['announcer_slot'] = (r['index'] - 65060) % 7
                r['candidate_category'] = ['ready', 'fight', 'ko-variant-0', 'ko-variant-1', 'finish-reason-bit-2', 'time-up', None][r['announcer_slot']]
    x['short_pcm_checks'] = checks
    return x

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True, help='Input donor inventory JSON')
    parser.add_argument('--donor-iso', type=Path, required=True)
    parser.add_argument('--source-cache', type=Path, required=True, help='Directory holding the pinned AFL metadata used by inventory_donor.py')
    parser.add_argument('--ffmpeg', type=Path, required=True, help='Explicit FFmpeg executable')
    parser.add_argument('--out', type=Path, required=True, help='Output candidate curation JSON')
    args = parser.parse_args()
    inputs = (args.inventory, args.donor_iso, args.ffmpeg)
    p.require(args.out.suffix.lower() == '.json' and all(args.out.resolve() != path.resolve() for path in inputs),
              'Output must be a JSON metadata file separate from every input')
    result = curate(args.inventory, args.donor_iso, args.source_cache, args.ffmpeg)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print('Short checks:', len(result['short_pcm_checks']))
    print('Silent ADX slots:', sum((r['verified_silent_placeholder'] for b in result['adx_blocks'] for r in b['entries'])))
    print('Silent bank slots:', sum((w['verified_silent_placeholder'] for b in result['banks'] for w in b['waves'])))

if __name__ == '__main__':
    main()
