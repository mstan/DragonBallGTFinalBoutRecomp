#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

// Local preparation only. No host-clock playback or guest state lives here.
// Codec version is part of the prepared-pack identity.
namespace finalbout::funidub {
using Bytes = std::vector<uint8_t>;
struct Sound {
    uint32_t rate = 0;
    std::vector<int16_t> pcm;
};
struct History { int32_t previous = 0, older = 0; };
constexpr const char* codec_version = "fb-integer-audio-1";

Sound decode_spu(const Bytes& adpcm, uint32_t rate);
Sound decode_adx(const Bytes& adx);
// Decode one original mono 4-bit XA sector at its native rate (4032 samples).
// Caller retains one history per selected channel in original sector order.
// Unsupported/malformed sectors are rejected without changing that history.
Sound decode_xa_mono(const std::array<uint8_t,2352>& sector, History& history);
// Source boundaries are in decoded samples. Output is padded with silence;
// it is never time-stretched to occupy the complete original slot.
Sound edit(const Sound& source, size_t first, size_t end, uint32_t rate,
           size_t capacity, int32_t gain_q16 = 65536, unsigned fade_ms = 5,
           uint32_t rate_denominator = 1);
// Preserve every original flag byte and the complete encoded length.
Bytes encode_spu(const Sound& sound, const Bytes& original);
// Mono 4-bit XA audio only. Preserve control bytes and reserved tail bytes.
// Recompute a present Form2 EDC; retain zero when that optional checksum is absent.
// Caller retains one history per original channel and feeds exactly 4032 samples.
std::array<uint8_t,2352> encode_xa_mono(
    const std::array<uint8_t,2352>& original,
    const int16_t* pcm, size_t samples, History& history);
}
