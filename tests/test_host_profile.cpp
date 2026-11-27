#include "netplay_host_catalog.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <initializer_list>

static PSXModNetplayHostProfiles installed;
static bool custom_profile;
extern "C" int psx_mod_register_vanilla_host_profiles(PSXModNetplayHostProfiles fn) {
    installed = fn;
    return fn != nullptr;
}
extern "C" const PSXModNetplayProfile *psx_mod_netplay_profile() {
    static PSXModNetplayProfile custom{};
    return custom_profile ? &custom : nullptr;
}

int main() {
    assert(installed);
    uint8_t image[32] = {1};
    PSXModNetplayHostStartup c{};
    c.cpu.architecture = PSX_HOST_ARCH_X64;
    c.cpu.features_known = 1;
    c.cpu.features = 127; // x86 feature bits; ARM/POWER flags are invalid on x64.
    c.compiled_backends = c.available_backends = PSX_HOST_BACKEND_ENHANCED;
    c.fp_contract = 2;
    c.interpreted_overlays_sealed = c.builtin_linked_bios = 1;
    c.actual_executable_sha256 = image;
    c.declared_build_manifest_sha256 = "a123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
    c.declared_build_manifest_schema = 1;
    c.builtin_bios_image_id = "OPENBIOS";
    c.builtin_bios_image_wordsum = 0xc4daeb88u;
    c.slot_count = c.player_count = 2;
    c.occupied_mask = 3;
    c.renderer = 1;
    c.retained_texture_banks = 0; // The normal native HLE renderer keeps software VRAM authority.
    PSXHostProfileCatalog cat{};
    for (int aspect : {0, 1, 2}) {
        c.rollback = 0; c.aspect_index = aspect;
        assert(installed(&c, &cat) && cat.count == 1);
        assert(cat.rules->flags == PSX_HOST_PROFILE_PORTABLE);
        assert(cat.rules->implementation_count == 1);
        assert(cat.rules->implementations[0].required_features == 0);
        PSXHostCapabilities caps;
        assert(psx_host_caps_init(&caps, &c.cpu, c.compiled_backends, c.available_backends, image));
        assert(psx_host_caps_offer(&caps, cat.rules, PSX_HOST_BACKEND_ENHANCED));
        assert(psx_host_caps_validate(&caps, &cat));
    }
    c.direct_loopback_scope = 1;
    c.cpu.features = 0;
    assert(installed(&c, &cat)); // Portable x64 profile does not require optional SIMD.
    auto foreign_cpu = c.cpu;
    foreign_cpu.features = PSX_HOST_NEON;
    PSXHostCapabilities refused_caps;
    assert(!psx_host_caps_init(&refused_caps, &foreign_cpu, c.compiled_backends,
        c.available_backends, image));
#define REFUSE(field, value) do { auto bad = c; bad.field = value; \
    cat.count = 999; assert(!installed(&bad, &cat) && cat.count == 0 && !cat.rules); } while (0)
    REFUSE(interpreted_overlays_sealed, 0);
    REFUSE(builtin_linked_bios, 0);
    REFUSE(builtin_bios_image_wordsum, 0);
    REFUSE(actual_executable_sha256, nullptr);
    REFUSE(declared_build_manifest_schema, 0);
    REFUSE(declared_build_manifest_sha256, "bad");
    REFUSE(cpu.features_known, 0);
    REFUSE(cpu.architecture, PSX_HOST_ARCH_ARM64);
    REFUSE(available_backends, 0);
    REFUSE(fp_contract, 1);
    REFUSE(slot_count, 3);
    REFUSE(player_count, 1);
    REFUSE(occupied_mask, 1);
    REFUSE(rollback, 2);
    REFUSE(rollback, 1); // No title-specific rollback qualification is claimed.
    REFUSE(loading_enabled, 2);
    REFUSE(renderer, 2);
    REFUSE(retained_texture_banks, 1);
    REFUSE(aspect_index, 3);
    REFUSE(observer, 1);
    image[0] = 0;
    assert(!installed(&c, &cat) && cat.count == 0);
    image[0] = 1; custom_profile = true;
    assert(!installed(&c, &cat) && cat.count == 0);
    assert(!installed(nullptr, &cat) && cat.count == 0);
    assert(!installed(&c, nullptr));
    std::puts("Final Bout production host catalog and shared capability validation passed");
}
