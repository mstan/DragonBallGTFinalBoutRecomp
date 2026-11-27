/* Final Bout qualification metadata for the shared pre-frame-zero admission gate.
 * Runtime qualification of both public artifacts is required before release. */
#include "mod_plugins.h"
#include "netplay_host_catalog.h"
#include "execution_profile.h"
#include "psx_sha256.h"
#include <cstdio>
#include <cstring>

#if defined(__GNUC__) && !defined(__clang__) && defined(__x86_64__) && \
    ((defined(_WIN32) && defined(_WIN64) && defined(__MINGW64__) && \
      __GNUC__ == 15 && __GNUC_MINOR__ == 2 && __GNUC_PATCHLEVEL__ == 0) || \
     (defined(__linux__) && __GNUC__ == 13 && __GNUC_MINOR__ == 3 && __GNUC_PATCHLEVEL__ == 0))
#define FINAL_BOUT_HOST_COMPILER 1
#else
#define FINAL_BOUT_HOST_COMPILER 0
#endif

#if defined(__linux__)
#define FINAL_BOUT_HOST_PROFILE "finalbout.linux64.native"
#define FINAL_BOUT_HOST_ABI "linux-gnu-gcc13.3.0"
#else
#define FINAL_BOUT_HOST_PROFILE "finalbout.win64.native"
#define FINAL_BOUT_HOST_ABI "win64-mingw-gcc15.2.0"
#endif
#define FINAL_BOUT_HOST_EXECUTION "13c9da33d6a6cfbe8cfeea05b8f7d28d03a51476292eb60b11dd386550d03ccb"
#define FINAL_BOUT_HOST_POLICY FINAL_BOUT_HOST_PROFILE "/v1;abi=" FINAL_BOUT_HOST_ABI ";execution=" FINAL_BOUT_HOST_EXECUTION ";kernel=host-native-v1;cpu=x64-portable-known;fp=2;bios=OPENBIOS:c4daeb88;overlays=interpreted-sealed;manifest=sha256-v1;artifact=exact;seats=2;mode=delay;renderer=opengl-dual-raster;texture-banks=off;aspect=0-2;loading=0-1;pgxp=compiled;observer=off;debug=off;route=normal"

static bool valid_sha(const char *s) {
    if (!s || std::strlen(s) != 64) return false;
    unsigned nonzero = 0;
    for (unsigned i = 0; i < 64; ++i) {
        const unsigned ch = static_cast<unsigned char>(s[i]);
        if (!((ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f'))) return false;
        nonzero |= ch != '0';
    }
    return nonzero != 0;
}

static int refuse_context(const PSXModNetplayHostStartup *c) {
    if (c) std::fprintf(stderr,
        "final_bout.host refused context: cpu=%u known=%u features=%llx backend=%u/%u fp=%u sealed=%d bios=%s/%08x schema=%u seats=%d/%d/%x rollback=%d loading=%d renderer=%d banks=%d aspect=%d observer=%d\n",
        c->cpu.architecture, c->cpu.features_known, static_cast<unsigned long long>(c->cpu.features),
        c->compiled_backends, c->available_backends, c->fp_contract,
        c->interpreted_overlays_sealed, c->builtin_bios_image_id ? c->builtin_bios_image_id : "none",
        c->builtin_bios_image_wordsum, c->declared_build_manifest_schema,
        c->slot_count, c->player_count, c->occupied_mask, c->rollback, c->loading_enabled,
        c->renderer, c->retained_texture_banks, c->aspect_index, c->observer);
    return 0;
}

static int final_bout_native_host_profiles(const PSXModNetplayHostStartup *c, PSXHostProfileCatalog *out) {
    if (!out) return 0;
    out->rules = nullptr;
    out->count = 0;
#if FINAL_BOUT_HOST_COMPILER && defined(PSX_NO_DEBUG_TOOLS) && defined(PSX_PGXP) && PSX_PGXP
    if (!c || !c->actual_executable_sha256 || !PSX_EXECUTION_ENHANCED ||
        std::strcmp(PSX_EXECUTION_ID, FINAL_BOUT_HOST_EXECUTION) || psx_mod_netplay_profile()) return refuse_context(c);
    unsigned image_nonzero = 0;
    for (unsigned i = 0; i < 32; ++i) image_nonzero |= c->actual_executable_sha256[i];
    const int players = c->player_count ? c->player_count : c->slot_count;
    const uint32_t seats = c->occupied_mask ? c->occupied_mask : 3u;
    if (!image_nonzero || c->cpu.architecture != PSX_HOST_ARCH_X64 ||
        c->cpu.features_known != 1 || (c->cpu.features & ~uint64_t(PSX_HOST_FEATURES_ALL)) ||
        c->compiled_backends != PSX_HOST_BACKEND_ENHANCED ||
        c->available_backends != PSX_HOST_BACKEND_ENHANCED || c->fp_contract != 2 ||
        c->interpreted_overlays_sealed != 1 || c->builtin_linked_bios != 1 ||
        !c->builtin_bios_image_id || std::strcmp(c->builtin_bios_image_id, "OPENBIOS") ||
        c->builtin_bios_image_wordsum != 0xc4daeb88u ||
        c->slot_count != 2 || players != 2 || seats != 3u ||
        c->rollback != 0 ||
        (c->loading_enabled != 0 && c->loading_enabled != 1) ||
        c->renderer != 1 || c->retained_texture_banks != 0 ||
        c->aspect_index < 0 || c->aspect_index > 2 || c->observer ||
        (c->direct_loopback_scope != 0 && c->direct_loopback_scope != 1) ||
        c->declared_build_manifest_schema != 1 || !valid_sha(c->declared_build_manifest_sha256)) return refuse_context(c);
    static PSXHostProfileRule rule;
    static_assert(sizeof(FINAL_BOUT_HOST_PROFILE) <= sizeof rule.profile,
        "Final Bout profile name exceeds the shared host-profile field");
    std::memset(&rule, 0, sizeof rule);
    std::memcpy(rule.profile, FINAL_BOUT_HOST_PROFILE, sizeof(FINAL_BOUT_HOST_PROFILE));
    rule.revision = 1;
    rule.priority = 1;
    rule.flags = PSX_HOST_PROFILE_PORTABLE;
    rule.implementation_count = 1;
    rule.implementations[0] = {PSX_HOST_BACKEND_ENHANCED, 1u << PSX_HOST_ARCH_X64, 0};
    psx_sha256_compute(reinterpret_cast<const uint8_t *>(FINAL_BOUT_HOST_POLICY),
        std::strlen(FINAL_BOUT_HOST_POLICY), rule.qualification);
    std::fprintf(stderr, "final_bout.host: declared manifest schema=%u sha256=%s rollback=%d aspect=%d\n",
        c->declared_build_manifest_schema, c->declared_build_manifest_sha256, c->rollback, c->aspect_index);
    out->rules = &rule;
    out->count = 1;
    return 1;
#else
    (void)c;
    return 0;
#endif
}

PSX_MOD_CONSTRUCTOR(register_final_bout_native_host_catalog) {
    psx_mod_register_vanilla_host_profiles(final_bout_native_host_profiles);
}
