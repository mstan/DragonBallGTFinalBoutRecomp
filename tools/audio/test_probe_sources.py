"""Malformed-container checks using synthetic, source-owned fixtures only."""
import struct
import unittest

from probe_sources import adx_info, pak_members, sony_waves


def synthetic_bank(offsets=(0,), nominal=None, bd_size=64):
    count = len(offsets)
    nominal = count if nominal is None else nominal
    hd = bytearray(256)
    hd[:8] = b"IECSsreV"
    hd[16:24] = b"IECSdaeH"
    struct.pack_into("<II", hd, 28, len(hd), bd_size)
    struct.pack_into("<I", hd, 48, 80)
    hd[80:88] = b"IECSigaV"
    struct.pack_into("<II", hd, 88, 176, nominal)
    for index, start in enumerate(offsets):
        relative = 48 + index * 8
        struct.pack_into("<I", hd, 96 + index * 4, relative)
        struct.pack_into("<IHBB", hd, 80 + relative, start, 16000, 0, 255)
    return hd, bytes(bd_size)


class SourceParserTests(unittest.TestCase):
    def test_pak_zero_length_slots_are_preserved(self):
        data = struct.pack("<IIII", 2, 16, 16, 20) + b"data"
        self.assertEqual(pak_members(data), [(16, 16), (16, 20)])

    def test_pak_refuses_reverse_overlapping_and_truncated_extents(self):
        for data in (b"", struct.pack("<IIII", 2, 16, 20, 17) + b"data",
                     struct.pack("<III", 1, 4, 12), struct.pack("<III", 1, 12, 40)):
            with self.subTest(data=data), self.assertRaises(ValueError):
                pak_members(data)

    def test_sony_extra_vagi_record_and_body_padding(self):
        hd, bd = synthetic_bank((0, 32), nominal=1)
        bank = sony_waves(hd, bd + b"padding")
        self.assertEqual(bank["nominal_waves"], 1)
        self.assertEqual([w["size"] for w in bank["waves"]], [32, 32])

    def test_sony_aliases_share_the_same_wave(self):
        hd, bd = synthetic_bank((0, 0, 32))
        waves = sony_waves(hd, bd)["waves"]
        self.assertEqual(waves[0]["adpcm_sha256"], waves[1]["adpcm_sha256"])
        self.assertEqual([w["size"] for w in waves], [32, 32, 32])

    def test_sony_body_end_sentinel_is_not_a_sample(self):
        hd, bd = synthetic_bank((0, 64))
        self.assertEqual(len(sony_waves(hd, bd)["waves"]), 1)

    def test_sony_refuses_out_of_bounds_wave_pointer(self):
        hd, bd = synthetic_bank()
        struct.pack_into("<I", hd, 96, 180)
        with self.assertRaises(ValueError):
            sony_waves(hd, bd)

    def test_sony_refuses_bad_body_extent_and_missing_body_bytes(self):
        for offsets, length in (((80,), 64), ((0,), 32), ((1,), 64)):
            hd, bd = synthetic_bank(offsets)
            with self.subTest(offsets=offsets, length=length), self.assertRaises(ValueError):
                sony_waves(hd, bd[:length])

    def test_adx_uses_declared_samples_instead_of_block_padding(self):
        data = bytearray(40 + 2 * 18)
        data[:4] = b"\x80\0\0\x24"
        data[4:8] = bytes((3, 18, 4, 1))
        struct.pack_into(">II", data, 8, 24000, 33)
        data[18:20] = b"\x04\0"
        data[34:40] = b"(c)CRI"
        self.assertEqual(adx_info(data)["samples"], 33)
        with self.assertRaises(ValueError):
            adx_info(data[:-1])


if __name__ == "__main__":
    unittest.main()
