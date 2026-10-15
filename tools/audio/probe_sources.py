"""Reproduce the first FuniDub source investigation; never installs a pack.

Python standard library only. Optional example decoding requires an explicitly
selected FFmpeg executable. Outputs must remain in this checkout's ignored
analysis/ or local-audio/ directory. Community labels are research leads.
"""
from __future__ import annotations

import argparse
import array
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[2]
TARGET_SHA1 = "8a2373f133788256cba64a1a0ba9fbb4b4667f71"
PVD_SHA256 = "ff7f5b8c457ed31bcca4c29be44e606e52fc79bc1cfe05d9c48db09560aa4c6c"
ARCHIVES = {
    "PZS3US1": (1990, 1462016000, 3399,
                 "c2e142912b88c1f6ca58d0498fd86fba3b86766d932250361970d096cc847565",
                 "c8f40cae7023d5d3da7d74dd02f29135383d2b75e1880df61a7b216817752049"),
    "PZS3US2": (715866, 1220337664, 65201,
                 "d4725b21070997b5ccae51039de818dbe01a21d0c56915e0c4e2220cc41f046e",
                 "31023bee54c056ba1a1fc6cbea09c96fed13e6740f7d96cc8a711218f234a8ea"),
}


def require(valid, message):
    if not valid:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def u32(data, offset):
    require(0 <= offset <= len(data) - 4, "truncated integer")
    return struct.unpack_from("<I", data, offset)[0]


def pak_members(data):
    count = u32(data, 0)
    require(0 < count <= 4096, "unsupported PAK member count")
    table_end = 4 + (count + 1) * 4
    require(table_end <= len(data), "truncated PAK table")
    offsets = struct.unpack_from("<" + "I" * (count + 1), data, 4)
    require(offsets[0] >= table_end, "PAK member overlaps its table")
    require(all(a <= b <= len(data) for a, b in zip(offsets, offsets[1:])),
            "invalid PAK member extent")
    return [(a, b) for a, b in zip(offsets, offsets[1:])]


def sony_waves(hd, bd):
    """Read Sony IECS HD/BD metadata; layout corroborated by vgmstream hd_bd.c.

    Account for a populated extra Vagi record, aliases and alignment padding.
    No guessed sampling rate is used for these donor banks.
    """
    require(hd[:8] == b"IECSsreV" and hd[16:24] == b"IECSdaeH", "not Sony HD")
    hd_size, bd_size, vagi = u32(hd, 28), u32(hd, 32), u32(hd, 48)
    require(hd_size <= len(hd) and bd_size <= len(bd), "truncated HD/BD")
    require(vagi + 16 <= hd_size and hd[vagi:vagi + 8] == b"IECSigaV", "missing Vagi")
    block_size, nominal = u32(hd, vagi + 8), u32(hd, vagi + 12)
    require(0 < nominal <= 4096 and vagi + block_size <= hd_size, "invalid Vagi size")
    require(vagi + 20 + nominal * 4 <= hd_size, "truncated Vagi pointers")
    count = nominal + (u32(hd, vagi + 16 + nominal * 4) != 0)
    records = []
    for index in range(count):
        relative = u32(hd, vagi + 16 + index * 4)
        info = vagi + relative
        require(relative >= 16 + count * 4 and info + 8 <= vagi + block_size,
                "Vagi record outside section")
        start, rate, flags, unknown = struct.unpack_from("<IHBB", hd, info)
        require(start <= bd_size and flags <= 1 and unknown in (0, 255), "invalid Vagi record")
        if start == bd_size and index == count - 1:
            continue  # Some banks include an end-of-body sentinel.
        require(0 < rate <= 192000, "invalid donor sampling rate")
        records.append(dict(index=index, offset=start, sample_rate=rate, loop=bool(flags & 1)))
    require(all(a["offset"] <= b["offset"] for a, b in zip(records, records[1:])),
            "unordered Sony waves")
    for index, record in enumerate(records):
        start = record["offset"]
        end = next((r["offset"] for r in records[index + 1:] if r["offset"] > start), bd_size)
        require(start <= end and start % 16 == 0 and (end - start) % 16 == 0, "unaligned Sony wave")
        record.update(size=end - start, adpcm_sha256=sha(bd[start:end]))
    return dict(nominal_waves=nominal, hd_size=hd_size, bd_size=bd_size,
                hd_sha256=sha(hd[:hd_size]), bd_sha256=sha(bd[:bd_size]), waves=records)


def adx_info(data):
    require(len(data) >= 40 and data[:2] == b"\x80\0", "not ADX")
    offset = struct.unpack_from(">H", data, 2)[0] + 4
    rate, samples = struct.unpack_from(">II", data, 8)
    require(data[4:8] == bytes((3, 18, 4, 1)) and data[18:20] == b"\x04\0",
            "unsupported ADX encoding/version")
    require(40 <= offset <= len(data) and data[offset - 6:offset] == b"(c)CRI", "invalid ADX header")
    require(rate > 0 and samples > 0 and offset + math.ceil(samples / 32) * 18 <= len(data),
            "truncated ADX samples")
    return dict(sample_rate=rate, samples=samples, channels=1, data_offset=offset)


def target_inventory(path):
    raw = path.read_bytes()
    require(hashlib.sha1(raw).hexdigest() == TARGET_SHA1, "unsupported Final Bout source revision")

    def read(lba, size):
        require(0 <= lba and 0 <= size and (lba + math.ceil(size / 2048)) * 2352 <= len(raw),
                "ISO extent outside source")
        return b"".join(raw[i * 2352 + 24:i * 2352 + 2072]
                        for i in range(lba, lba + math.ceil(size / 2048)))[:size]

    def record(data):
        require(len(data) >= 34 and 33 + data[32] <= len(data), "truncated ISO record")
        lba, size = u32(data, 2), u32(data, 10)
        require(lba == struct.unpack_from(">I", data, 6)[0]
                and size == struct.unpack_from(">I", data, 14)[0], "ISO endian mismatch")
        require(not data[25] & 0x80, "multi-extent ISO files unsupported")
        return lba, size, data[25], data[33:33 + data[32]]

    pvd = read(16, 2048)
    require(pvd[:7] == b"\x01CD001\x01", "missing ISO PVD")
    files, seen = [], set()

    def directory(lba, size, prefix):
        require((lba, size) not in seen and size <= 4 * 1024 * 1024, "invalid ISO directory")
        seen.add((lba, size))
        data, pos = read(lba, size), 0
        while pos < len(data):
            length = data[pos]
            if not length:
                pos = (pos // 2048 + 1) * 2048
                continue
            require(length >= 34 and pos + length <= len(data), "invalid ISO directory record")
            child_lba, child_size, flags, name = record(data[pos:pos + length])
            pos += length
            if name in (b"\0", b"\1"):
                continue
            child = prefix + "/" + name.decode("ascii")
            if flags & 2:
                directory(child_lba, child_size, child)
            else:
                files.append(dict(path=child, lba=child_lba, size=child_size))

    directory(*record(pvd[156:190])[:2], "")
    result = dict(source_sha1=TARGET_SHA1, source_sha256=sha(raw), files=files,
                  victory_candidates=[], xa_streams=[], mixed_resource_files=[], unclassified_adpcm_banks=[])
    examples = []
    for entry in files:
        name, lba, size = entry["path"], entry["lba"], entry["size"]
        if name == "/BATTLE/BTWINV.DAT;1":
            data = read(lba, size)
            require(all(data[i] >> 4 <= 4 and data[i] & 15 <= 12 and data[i + 1] <= 7
                        for i in range(0, len(data), 16)), "victory bank is not aligned ADPCM")
            starts = [i for i in range(0, len(data), 16) if data[i + 1] == 4]
            ends = [i for i in range(0, len(data), 16) if data[i + 1] == 1]
            require(len(starts) == len(ends) == 54, "unexpected victory sample structure")
            for index, (start, last) in enumerate(zip(starts, ends)):
                end = last + 16
                require(start <= last and data[end:end + 2] == b"\0\x07", "missing ADPCM terminator")
                require(index + 1 == len(starts) or end < starts[index + 1], "overlapping samples")
                sample = data[start:end]
                cue = dict(id=f"slus00493:btwinv:{start:08x}", file=name, offset=start, size=len(sample),
                           adpcm_sha256=sha(sample), decoded_samples=len(sample) // 16 * 28,
                           sample_rate=None, speaker=None, runtime_trigger=None)
                result["victory_candidates"].append(cue)
                if index < 3:
                    examples.append(dict(label=f"original-win-{index:03d}-pitch-unverified", codec="vag",
                                         data=sample, rate=44100, samples=cue["decoded_samples"],
                                         provenance=cue, pitch_assumed=True))
        elif name.endswith(".STR;1"):
            groups = defaultdict(list)
            for sector_lba in range(lba, lba + math.ceil(size / 2048)):
                sector = raw[sector_lba * 2352:(sector_lba + 1) * 2352]
                require(sector[16:20] == sector[20:24], "XA subheader mismatch")
                if sector[18] & 4:
                    require(sector[18] & 32, "unexpected Form-1 audio")
                    groups[(sector[16], sector[17], sector[19])].append((sector_lba, sector))
            for (file_id, channel, coding), sectors in sorted(groups.items()):
                require(not coding & ~0x15, "unsupported XA coding")
                channels = 2 if coding & 1 else 1
                rate = 18900 if coding & 4 else 37800
                frames_per_sector = (2016 if coding & 16 else 4032) // channels
                stream = dict(id=f"slus00493:{name.lower()}:xa:{file_id}:{channel}:{coding:02x}",
                              file=name, xa_file=file_id, xa_channel=channel, coding=coding,
                              channels=channels, sample_rate=rate, sectors=len(sectors),
                              decoded_samples=len(sectors) * frames_per_sector,
                              first_lba=sectors[0][0], last_lba=sectors[-1][0],
                              raw_sector_sha256=sha(b"".join(s for _, s in sectors)),
                              submodes=dict(Counter(str(s[18]) for _, s in sectors)),
                              speaker=None, runtime_trigger=None)
                result["xa_streams"].append(stream)
                if name == "/BATTLE/DEMOXA03.STR;1" and (file_id, channel) == (1, 0):
                    examples.append(dict(label="original-demoxa03-f1-ch0", codec="psxstr",
                                         data=b"".join(s for _, s in sectors), rate=rate,
                                         samples=stream["decoded_samples"], provenance=stream))
        elif name in ("/TITLE/TENKAWIN.BIN;1", "/TITLE/VABDATA.BIN;1"):
            data = read(lba, size)
            require(len(data) % 16 == 0 and
                    all(data[i] >> 4 <= 4 and data[i] & 15 <= 12 and data[i + 1] <= 7
                        for i in range(0, len(data), 16)), "unexpected other ADPCM bank format")
            result["unclassified_adpcm_banks"].append(dict(file=name, size=size, file_sha256=sha(data),
                                                          frame_flags=dict(Counter(str(data[i + 1])
                                                                                   for i in range(0, len(data), 16)))))
        elif name.startswith("/TITLE/"):
            data = read(lba, size)
            if b"Psdp" in data:
                result["mixed_resource_files"].append(dict(file=name, size=size, first_psdp=data.find(b"Psdp"),
                                                           file_sha256=sha(data), classification="not a flat audio bank"))
    return result, examples


def donor_inventory(path, labels_dir):
    size = path.stat().st_size
    require(size == 3020816384, "unsupported BT3 image size")
    result = dict(image_size=size, identity_scope="PVD + AFS tables + selected payload hashes; not full ISO hash",
                  pvd_sha256=PVD_SHA256, archives={}, voice_banks=[], adx_candidates=[])
    examples = []
    with path.open("rb") as iso:
        def read(offset, length):
            require(0 <= offset <= size and 0 <= length <= size - offset, "donor read outside image")
            iso.seek(offset)
            data = iso.read(length)
            require(len(data) == length, "short donor read")
            return data

        require(sha(read(16 * 2048, 2048)) == PVD_SHA256, "BT3 PVD mismatch")
        for archive, (lba, archive_size, count, table_sha, afl_sha) in ARCHIVES.items():
            base = lba * 2048
            table = read(base, 8 + count * 8 + 8)
            require(table[:4] == b"AFS\0" and u32(table, 4) == count and sha(table) == table_sha,
                    "BT3 AFS identity mismatch")
            labels = (labels_dir / (archive + ".AFL")).read_bytes()
            require(sha(labels) == afl_sha and len(labels) == 16 + 32 * count, "unrecognized AFL labels")
            names = [labels[16 + i * 32:48 + i * 32].split(b"\0")[0].decode("ascii") for i in range(count)]
            entries = list(struct.iter_unpack("<II", table[8:-8]))
            require(all(0 <= off <= archive_size and length <= archive_size - off for off, length in entries),
                    "AFS entry outside archive")
            result["archives"][archive] = dict(lba=lba, size=archive_size, entries=count,
                                              table_sha256=table_sha, labels_sha256=afl_sha)
            if archive.endswith("1"):
                result["english_voice_labels"] = sum(n.endswith("_Voice_US.pak") for n in names)
                wanted = {"Goku_0_Voice_US.pak", "GT_Goku_0_Voice_US.pak",
                          "GT_Goku_3_Voice_US.pak", "Pan_Voice_US.pak"}
                for index, name in enumerate(names):
                    if name not in wanted:
                        continue
                    offset, length = entries[index]
                    data = read(base + offset, length)
                    members = pak_members(data)
                    require(len(members) == 3, "unrecognized voice PAK")
                    bd = data[slice(*members[0])]
                    hd = data[slice(*members[1])]
                    bank = sony_waves(hd, bd)
                    bank.update(archive=archive, index=index, community_label=name, label_is_unverified=True,
                                archive_offset=offset, pak_sha256=sha(data), members=members)
                    result["voice_banks"].append(bank)
                    if name == "GT_Goku_0_Voice_US.pak":
                        first = bank["waves"][0]
                        sample = bd[first["offset"]:first["offset"] + first["size"]]
                        examples.append(dict(label=f"bt3-us1-{index}-wave-000", codec="vag", data=sample,
                                             rate=first["sample_rate"], samples=len(sample) // 16 * 28,
                                             provenance=dict(archive=archive, index=index, wave=first)))
                require(len(result["voice_banks"]) == len(wanted), "missing expected donor banks")
            else:
                for index in (49574, 49874, 55174, 62874):
                    offset, length = entries[index]
                    data = read(base + offset, length)
                    info = adx_info(data)
                    info.update(archive=archive, index=index, archive_offset=offset, size=length,
                                community_label=names[index], label_is_unverified=True, encoded_sha256=sha(data))
                    result["adx_candidates"].append(info)
                    examples.append(dict(label=f"bt3-us2-{index}", codec="adx", data=data,
                                         rate=info["sample_rate"], samples=info["samples"], provenance=info))
    return result, examples


def decode_examples(examples, destination, ffmpeg):
    directory = destination / "examples"
    directory.mkdir(exist_ok=True)
    version = subprocess.run([str(ffmpeg), "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    receipts = []
    for example in examples:
        data, codec = example["data"], example["codec"]
        if codec == "vag":
            header = bytearray(48)
            header[:4] = b"VAGp"
            struct.pack_into(">I", header, 4, 0x20)
            struct.pack_into(">I", header, 12, len(data))
            struct.pack_into(">I", header, 16, example["rate"])
            data = header + data
        source = directory / (example["label"] + (".str" if codec == "psxstr" else "." + codec))
        output = source.with_suffix(".wav")
        source.write_bytes(data)
        command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
        if codec == "psxstr":
            command += ["-f", "psxstr"]
        command += ["-i", str(source), "-vn"]
        if codec == "adx":
            command += ["-af", f"atrim=end_sample={example['samples']}"]
        command += ["-c:a", "pcm_s16le", str(output)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"FFmpeg failed: {run.stderr}")
        with wave.open(str(output), "rb") as wav:
            require(wav.getsampwidth() == 2 and wav.getnchannels() == 1, "unexpected example PCM format")
            require(wav.getnframes() == example["samples"] and wav.getframerate() == example["rate"],
                    "decoded sample count/rate mismatch")
            pcm = wav.readframes(wav.getnframes())
        samples = array.array("h", pcm)
        if sys.byteorder != "little":
            samples.byteswap()
        receipts.append(dict(label=example["label"], decoder=version, command=command,
                             source_sha256=sha(example["data"]), provenance=example["provenance"],
                             samples=example["samples"], sample_rate=example["rate"],
                             pitch_assumed=example.get("pitch_assumed", False), pcm_sha256=sha(pcm),
                             peak=max((abs(v) for v in samples), default=0),
                             clipped_samples=sum(v in (-32768, 32767) for v in samples)))
    return receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-bin", type=Path, required=True)
    parser.add_argument("--donor-iso", type=Path, required=True)
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ffmpeg", type=Path, help="Also extract and decode nine local research examples")
    args = parser.parse_args()
    destination = args.out.resolve()
    require(any(destination.is_relative_to(ROOT / name) for name in ("analysis", "local-audio")),
            "output must be under this checkout's ignored analysis/ or local-audio/")
    target, original_examples = target_inventory(args.target_bin)
    donor, donor_examples = donor_inventory(args.donor_iso, args.labels_dir)
    destination.mkdir(parents=True, exist_ok=True)
    result = dict(schema=1, target=target, donor=donor)
    if args.ffmpeg:
        result["example_decodes"] = decode_examples(original_examples + donor_examples, destination, args.ffmpeg.resolve())
    (destination / "inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Target: {len(target['files'])} files; {len(target['victory_candidates'])} victory candidates; "
          f"{len(target['xa_streams'])} XA channels including the opening movie")
    print(f"Donor: {donor['english_voice_labels']} English community bank labels; "
          f"{len(donor['voice_banks'])} inspected Sony banks; {len(donor['adx_candidates'])} ADX candidates")
    print(f"Decoded local examples: {len(result.get('example_decodes', []))}; report: {destination / 'inventory.json'}")


if __name__ == "__main__":
    main()
