"""Inventory Final Bout XA sectors and animation events directly from the disc.

Usage: python tools/audio/inventory_xa.py --target-bin GAME.bin --out REPORT.json
Optional native PCM receipts: --codec-check CODEC_CHECK.exe [--decode-channel
DEMOXA01.STR:0]. Without selectors, --codec-check decodes all 54 mono streams.
Only JSON metadata is retained; temporary raw/PCM files are removed. No playback.
"""
from __future__ import annotations

import argparse
import array
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

from inventory_original import BOOT_SHA256, STEP1_SHA256, STEP40_SHA256
from probe_sources import TARGET_SHA1, require, sha, target_inventory

DISC_SHA256 = "2f9d475fa089bed3f77a3344ea23af0663b30ffe9a2bc0b803bcae389480a15b"
BTCHARA_SHA256 = "7b254f3c843674556ac97170fa64cf3773592ae014f4d68adc5811d848471599"
OVERLAY_BASE = 0x8003dfa0
SECTOR_BYTES = 2352
GUARDS = {0x8004eaec: 0x0c013fae, 0x8005002c: 0x1602000f,
          0x80050054: 0x00220821, 0x80050058: 0x902527fc,
          0x80050060: 0x24040001, 0x8005006c: 0x1602000d,
          0x8005008c: 0x0c005d54, 0x80050110: 0x0c005cbb}
# Full STEP40 identity also binds the script interpreter's command widths.
# These counts include the command word; remaining commands occupy one word.
COMMAND_WORDS = {0x22: 5, 0x23: 5, 0x40: 3, 0x41: 4,
                 0x80: 3, 0x81: 2, 0x84: 3}
XA_FILES = ("DEMOXA01.STR", "DEMOXA02.STR", "DEMOXA03.STR", "FINISH.STR")


def animation_events(bt, step1):
    """Locate each bounded DB table, then walk command boundaries, not payloads."""
    table_at = 0x80053bec - OVERLAY_BASE
    table_bytes = step1[table_at:table_at + 271 * 4]
    require(len(table_bytes) == 271 * 4, "Truncated character resource table")
    characters, used = [], set()
    for character in range(18):
        edges = struct.unpack_from("<16I", table_bytes, character * 15 * 4)
        require(all(a <= b for a, b in zip(edges, edges[1:])) and
                edges[-1] * 2048 <= len(bt), "Invalid character resource bounds")
        lo, hi = edges[0] * 2048, edges[5] * 2048
        hits, position = [], lo
        while position < hi:
            at = bt.find(b"DB", position, hi)
            if at < 0:
                break
            position = at + 2
            if at % 4 or at + 4 > hi:
                continue
            count = struct.unpack_from("<H", bt, at + 2)[0]
            start = at + 4 + count * 4
            if not 150 <= count <= 300 or start > hi:
                continue
            offsets = struct.unpack_from("<" + "I" * count, bt, at + 4)
            valid = [offset for offset in offsets if offset != 0xffffffff]
            if (not valid or offsets[0] != 0 or
                    any(a > b for a, b in zip(valid, valid[1:])) or
                    start + valid[-1] * 4 >= hi):
                continue
            hits.append((at, start, offsets))
        require(len(hits) == 1, f"Expected one bounded animation table for character {character}")
        header, start, offsets = hits[0]
        scripts = []
        for index, relative in enumerate(offsets):
            if relative == 0xffffffff:
                continue
            end_relative = next((v for v in offsets[index + 1:] if v != 0xffffffff),
                                (hi - start) // 4)
            begin, end = start + relative * 4, start + end_relative * 4
            require(start <= begin <= end <= hi, "Animation script exceeds its resource")
            words = struct.unpack_from("<" + "I" * ((end - begin) // 4), bt, begin)
            cursor, events = 0, []
            while cursor < len(words):
                word = words[cursor]
                opcode = word >> 16 & 255
                width = COMMAND_WORDS.get(opcode, 1)
                require(width <= len(words) - cursor, "Truncated animation command")
                if opcode == 0:
                    break
                if opcode == 0x60 and word & 255 >= 0x30:
                    event = word & 255
                    events.append(dict(word=cursor, offset=begin + cursor * 4,
                                       event_id=event, volume=word >> 8 & 255,
                                       frame_field=word >> 24, encoded_word=f"{word:08x}"))
                    if event >= 0x32:
                        used.add(event)
                cursor += width
            if events:
                starts = [n for n, event in enumerate(events)
                          if event["event_id"] == 0x30 or event["event_id"] >= 0x32]
                for n in starts:
                    require(any(event["event_id"] == 0x31 for event in events[n + 1:]),
                            "XA-start script has no later native stop event")
                scripts.append(dict(script=index, source_offset=begin,
                                    source_size=end - begin, source_sha256=sha(bt[begin:end]),
                                    events=events))
        characters.append(dict(character_id=character, finish_channel=character,
                               header_offset=header, script_count=len(offsets),
                               header_sha256=sha(bt[header:start]), scripts=scripts))
    require(used == set(range(0x32, 0x56)) - {0x3c, 0x3d, 0x46, 0x47, 0x4d, 0x4e, 0x51},
            "Unexpected original DEMOXA script associations")
    return characters, used, sha(table_bytes)


def pcm_receipt(codec_check, payload, samples, rate):
    with tempfile.TemporaryDirectory(prefix="finalbout-xa-inventory-") as temporary:
        source = Path(temporary) / "channel.raw"
        destination = Path(temporary) / "channel.pcm"
        source.write_bytes(payload)
        result = subprocess.run([str(codec_check), "xa", str(source), str(destination)],
                                capture_output=True, text=True, timeout=120)
        require(result.returncode == 0, "Native XA decoder failed: " + result.stderr.strip())
        pcm = destination.read_bytes()
        require(len(pcm) == samples * 2, "Native XA decoder returned the wrong sample count")
        require(result.stdout.startswith(f"{rate} Hz, {samples} samples"),
                "Native XA decoder returned the wrong rate")
        values = array.array("h")
        require(values.itemsize == 2, "Unsupported Python signed-short representation")
        values.frombytes(pcm)
        if sys.byteorder != "little":
            values.byteswap()
        first = next((i for i, value in enumerate(values) if value), None)
        last = next((i for i in range(len(values) - 1, -1, -1) if values[i]), None)
        return dict(sha256=sha(pcm), samples=samples, first_nonzero_sample=first,
                    last_nonzero_sample=last,
                    exact_zero_tail_seconds=(samples - last - 1) / rate if last is not None else samples / rate)


def inventory(path, codec_check=None, selectors=()):
    original, _ = target_inventory(path)
    raw = path.read_bytes()
    require(hashlib.sha1(raw).hexdigest() == TARGET_SHA1 and sha(raw) == DISC_SHA256,
            "Source changed during XA inventory")
    files = {entry["path"]: entry for entry in original["files"]}

    def read(name):
        entry = files["/" + name + ";1"]
        start, size = entry["lba"], entry["size"]
        require((start + (size + 2047) // 2048) * SECTOR_BYTES <= len(raw), "Resource exceeds disc")
        return b"".join(raw[i * SECTOR_BYTES + 24:i * SECTOR_BYTES + 2072]
                        for i in range(start, start + (size + 2047) // 2048))[:size]

    boot, step1, step40, bt = (read(name) for name in
                              ("SLUS_004.93", "MENU/STEP01.BIN", "MENU/STEP40.BIN", "TITLE/BTCHARA.DAT"))
    require((sha(boot), sha(step1), sha(step40), sha(bt)) ==
            (BOOT_SHA256, STEP1_SHA256, STEP40_SHA256, BTCHARA_SHA256),
            "Unsupported original executable/script tables")
    for address, expected in GUARDS.items():
        require(struct.unpack_from("<I", step40, address - OVERLAY_BASE)[0] == expected,
                f"XA dispatcher/caller guard failed at {address:08x}")
    characters, used, table_hash = animation_events(bt, step1)
    selected = set(selectors)
    require(codec_check is not None or not selected, "--decode-channel requires --codec-check")
    if codec_check is not None:
        codec_check = Path(codec_check).resolve(strict=True)
    streams, resources, matched = [], [], set()
    for name in XA_FILES:
        entry = files[f"/BATTLE/{name};1"]
        count = (entry["size"] + 2047) // 2048
        begin = entry["lba"] * SECTOR_BYTES
        payload = raw[begin:begin + count * SECTOR_BYTES]
        require(len(payload) == count * SECTOR_BYTES, "Truncated original XA resource")
        resources.append(dict(file=entry["path"], lba=entry["lba"], iso_size=entry["size"],
                              sectors=count, raw_offset=begin, raw_size=len(payload), raw_sha256=sha(payload)))
        groups = defaultdict(list)
        for index in range(count):
            sector = payload[index * SECTOR_BYTES:(index + 1) * SECTOR_BYTES]
            require(sector[15] == 2 and sector[16:20] == sector[20:24], "Invalid original XA subheader")
            if sector[18] & 4:
                require(sector[18] & 0x20 and sector[19] in (0, 4), "Unsupported original XA audio")
                groups[(sector[16], sector[17], sector[19])].append((entry["lba"] + index, sector))
        expected_channels = 18 if name == "FINISH.STR" else 4 if name == "DEMOXA03.STR" else 16
        coding = 4 if name == "FINISH.STR" else 0
        require(set(groups) == {(1, channel, coding) for channel in range(expected_channels)},
                "Unexpected original XA stream identities")
        for (file_number, channel, coding), sectors in sorted(groups.items()):
            channel_bytes = b"".join(sector for _, sector in sectors)
            rate = 18900 if coding == 4 else 37800
            selector = f"{name}:{channel}"
            event = 0x30 if name == "FINISH.STR" else 0x32 + XA_FILES.index(name) * 16 + channel
            item = dict(file=entry["path"], xa_file=file_number, channel=channel, coding=coding,
                        rate=rate, sectors=len(sectors), samples=len(sectors) * 4032,
                        duration_seconds=len(sectors) * 4032 / rate,
                        first_lba=sectors[0][0], last_lba=sectors[-1][0],
                        sector_lbas=[lba for lba, _ in sectors], raw_sector_sha256=sha(channel_bytes),
                        submodes=dict(Counter(str(sector[18]) for _, sector in sectors)),
                        event_id=event, script_referenced=event == 0x30 or event in used)
            if codec_check is not None and (not selected or selector in selected):
                item["pcm"] = pcm_receipt(codec_check, channel_bytes, item["samples"], rate)
                matched.add(selector)
            streams.append(item)
    require(not selected - matched, "Unknown --decode-channel selector: " + ", ".join(sorted(selected - matched)))
    report = dict(schema="final-bout-xa-inventory-v1", disc_sha1=TARGET_SHA1, disc_sha256=DISC_SHA256,
                  boot_sha256=sha(boot), step1_sha256=sha(step1), step40_sha256=sha(step40),
                  btchara_sha256=sha(bt), character_resource_table_sha256=table_hash,
                  guards={f"0x{address:08x}": f"0x{word:08x}" for address, word in GUARDS.items()},
                  command_words={f"0x{opcode:02x}": width for opcode, width in COMMAND_WORDS.items()},
                  frame_field_semantics="Unprocessed high-byte script fields; not absolute times or playback deadlines",
                  characters=characters, demoxa_event_ids_in_raw_scripts=sorted(used),
                  demoxa_event_ids_not_in_raw_scripts=sorted(set(range(0x32, 0x56)) - used),
                  accepted_dispatch_events_without_media=list(range(0x56, 0x5a)),
                  resources=resources, streams=streams,
                  qualification="Disc script associations and raw sectors only; no transcript, speech/effect classification, or runtime route proof")
    if codec_check is not None:
        report["pcm_decoder"] = dict(executable_sha256=sha(codec_check.read_bytes()), codec="native xa", wire="s16le")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-bin", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--codec-check", type=Path)
    parser.add_argument("--decode-channel", action="append", default=[], metavar="FILE:CHANNEL")
    args = parser.parse_args()
    require(args.out.suffix.lower() == ".json", "Inventory output must be a JSON metadata file")
    for source in (args.target_bin, args.codec_check):
        if source is not None:
            require(args.out.resolve() != source.resolve() and
                    not (args.out.exists() and source.exists() and args.out.samefile(source)),
                    "Metadata output must not overwrite an input")
    result = inventory(args.target_bin, args.codec_check, args.decode_channel)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"18 character script tables, {len(result['streams'])} XA streams, "
          f"{len(result['demoxa_event_ids_in_raw_scripts'])} referenced DEMOXA events")


if __name__ == "__main__":
    main()
