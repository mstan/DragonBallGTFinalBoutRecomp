"""Inventory the supported BT3 donor locally; output metadata, never recordings.

Pinned community AFL metadata can be supplied in --source-cache or downloaded
with explicit --fetch-labels. Character/form labels remain unverified leads.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import struct
import json
import re
import urllib.request
import probe_sources as p
LABEL_REVISION = '9183d9c3ae94e77e2c14bf3dfa37b6ea5b624560'
LABEL_BASE = 'https://raw.githubusercontent.com/ViveTheModder/vivethemodder.github.io/' + LABEL_REVISION + '/assets/AFLs_new/'

def load_labels(source_cache: Path, archive: str, fetch: bool=False):
    """Read fingerprinted metadata; network access occurs only with fetch=True."""
    _, _, count, _, expected_hash = p.ARCHIVES[archive]
    path = source_cache / (archive + '.AFL')
    if path.exists():
        labels = path.read_bytes()
    else:
        p.require(fetch, 'Missing pinned ' + path.name + '; use --fetch-labels or supply it in --source-cache')
        with urllib.request.urlopen(LABEL_BASE + path.name, timeout=30) as response:
            labels = response.read(16 + 32 * count + 1)
        p.require(p.sha(labels) == expected_hash and len(labels) == 16 + 32 * count, 'Downloaded AFL fingerprint mismatch')
        source_cache.mkdir(parents=True, exist_ok=True)
        path.write_bytes(labels)
    p.require(p.sha(labels) == expected_hash and len(labels) == 16 + 32 * count, 'Unrecognized AFL cache content: ' + path.name)
    return [labels[16 + i * 32:48 + i * 32].split(b'\x00')[0].decode('ascii') for i in range(count)]

def inventory(donor_iso: Path, source_cache: Path, fetch_labels: bool=False):
    result = {'schema': 1, 'identity_scope': 'PVD + both AFS tables + hashes of inspected full entry payloads; not full ISO hash', 'banks': [], 'adx_blocks': []}
    with donor_iso.open('rb') as iso:

        def read(off, size):
            iso.seek(off)
            d = iso.read(size)
            p.require(len(d) == size, 'short read')
            return d
        p.require(donor_iso.stat().st_size == 3020816384, 'ISO size')
        p.require(p.sha(read(32768, 2048)) == p.PVD_SHA256, 'PVD mismatch')
        archives = {}
        for archive, (lba, size, count, th, lh) in p.ARCHIVES.items():
            t = read(lba * 2048, 8 + count * 8 + 8)
            p.require(p.sha(t) == th, 'table mismatch')
            names = load_labels(source_cache, archive, fetch_labels)
            archives[archive] = (lba * 2048, list(struct.iter_unpack('<II', t[8:-8])), names)
        base, entries, names = archives['PZS3US1']
        for index, name in enumerate(names):
            if not name.endswith('_Voice_US.pak'):
                continue
            off, size = entries[index]
            data = read(base + off, size)
            members = p.pak_members(data)
            p.require(len(members) == 3, 'voice member count')
            bd, hd, sq = [data[slice(*m)] for m in members]
            bank = p.sony_waves(hd, bd)
            setb = hd.find(b'IECSbteS')
            sesq = sq.find(b'IECSqseS')
            p.require(setb >= 0 and sesq >= 0, 'missing Setb/Sesq')
            bank['sound_to_wave'] = []
            for w in bank['waves']:
                w['max_decoded_samples'] = w['size'] // 16 * 28
                w['duration_upper_bound_seconds'] = w['max_decoded_samples'] / w['sample_rate']
                sample = bd[w['offset']:w['offset'] + w['size']]
                end = next((i + 16 for i in range(0, len(sample), 16) if sample[i + 1] & 1), None)
                w['first_end_decoded_samples'] = end // 16 * 28 if end else None
                w['first_end_flag'] = sample[end - 15] if end else None
                ident = w['index']
                seqoff = sesq + p.u32(sq, sesq + 52 + 4 * ident)
                p.require(sq[seqoff + 16:seqoff + 19] == b'\x00\x90\x00', 'non-simple note-on sequence')
                timbre = sq[seqoff + 19]
                record = setb + 36 + timbre * hd[setb + 32]
                wave = struct.unpack_from('<H', hd, record)[0]
                bank['sound_to_wave'].append(dict(sound=ident, timbre=timbre, wave=wave))
            bank.update(index=index, label=name, archive_offset=off, pak_size=size, pak_sha256=p.sha(data), members=members, unique_encoded_wave_count=len({w['adpcm_sha256'] for w in bank['waves']}))
            result['banks'].append(bank)
        off, size = entries[1]
        data = read(base + off, size)
        members = p.pak_members(data)
        voice = data[slice(*members[5])]
        p.require(len(voice) >= 57 * 8, 'voice table truncated')
        result['voice_kind_table'] = {'archive': 'PZS3US1', 'index': 1, 'member': 5, 'member_offset': members[5][0], 'pak_sha256': p.sha(data), 'table_sha256': p.sha(voice), 'table_bytes': len(voice), 'entries': [dict(kind=i, first=first, count=count, cooldown_seconds=interval) for i, (first, count, interval) in enumerate(struct.iter_unpack('<hhf', voice[:57 * 8]))]}
        base, entries, names = archives['PZS3US2']
        wanted = re.compile('^(?:Goku|GT_Goku|Gohan|Piccolo|Vegeta|Majin_Vegeta|Trunks|Pan|Frieza|Cell|Buu|Baby_Vegeta)(?:_[0-9AB])?_500_US\\.adx$')
        for start, label in enumerate(names):
            if not wanted.match(label):
                continue
            blockname = label.removesuffix('_500_US.adx')
            first = entries[start][0]
            lastoff, lastsize = entries[start + 99]
            blockdata = read(base + first, lastoff + lastsize - first)
            rows = []
            for idx in range(start, start + 100):
                off, size = entries[idx]
                data = blockdata[off - first:off - first + size]
                info = p.adx_info(data)
                info.update(index=idx, label=names[idx], line=idx - start, label_number=500 + idx - start, size=size, archive_offset=off, sha256=p.sha(data), duration=info['samples'] / info['sample_rate'])
                rows.append(info)
            result['adx_blocks'].append(dict(name=blockname, start=start, entries=rows, unique_encoded_count=len({r['sha256'] for r in rows}), sub_100ms_lines=[r['line'] for r in rows if r['duration'] < 0.1]))
            print(blockname, start, 'unique', result['adx_blocks'][-1]['unique_encoded_count'], flush=True)
        result['menu_announcer_candidates'] = []
        for start, stop in [(32219, 32265), (32525, 32633), (65060, 65116)]:
            first = entries[start][0]
            lastoff, lastsize = entries[stop - 1]
            blockdata = read(base + first, lastoff + lastsize - first)
            for idx in range(start, stop):
                off, size = entries[idx]
                data = blockdata[off - first:off - first + size]
                info = p.adx_info(data)
                info.update(index=idx, label=names[idx], size=size, archive_offset=off, sha256=p.sha(data), duration=info['samples'] / info['sample_rate'])
                result['menu_announcer_candidates'].append(info)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--donor-iso', type=Path, required=True)
    parser.add_argument('--source-cache', type=Path, required=True, help='Directory holding fingerprinted PZS3US1.AFL and PZS3US2.AFL metadata')
    parser.add_argument('--fetch-labels', action='store_true', help='Download missing AFL metadata at the pinned revision; never downloads audio')
    parser.add_argument('--out', type=Path, required=True, help='Output inventory JSON')
    args = parser.parse_args()
    p.require(args.out.suffix.lower() == '.json' and args.out.resolve() != args.donor_iso.resolve(),
              'Output must be a JSON metadata file separate from the donor image')
    result = inventory(args.donor_iso, args.source_cache, args.fetch_labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print('Inventoried', len(result['banks']), 'banks;', len(result['adx_blocks']), 'ADX blocks')

if __name__ == '__main__':
    main()
