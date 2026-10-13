#include "cpu_state.h"
#include "gpu.h"
#include "mod_plugins.h"

#include <stdint.h>

/* SLUS-00493: static PsyQ DMA-list submit, before writing DMA2 MADR/CHCR.
 * Combat HUD initializer 80054018 copies 30C bytes into the second bank;
 * 80054754..68 selects bank = scratchpad[0] * 30C. See docs/WIDESCREEN.md.
 * All changes are renderer tags: neither guest packets nor GTE are changed. */
#define FB_SUBMIT 0x80028D80u
#define FB_HUD_BASE 0x80072A14u
#define FB_HUD_STRIDE 0x30Cu
#define FB_WALK_LIMIT 16384u

static int combat_layout_matches(void) {
    return psx_mod_display_width() == 512u &&
        psx_mod_read_word(0x80053FC0u) == 0x26102A14u &&
        psx_mod_read_word(0x80054020u) == 0x2606030Cu &&
        psx_mod_read_word(0x8006A538u) == 0x27BDFFC8u &&
        psx_mod_read_word(0x8006AC1Cu) == 0x8C42868Cu;
}

static int hud_anchor(uint32_t packet) {
    uint32_t role = (packet - FB_HUD_BASE) % FB_HUD_STRIDE;
    /* VS emblem and PAUSE form centred screen overlays. */
    if (role == 0x08u || role == 0x1Cu) return 0;
    /* Remaining sprites and health/energy quads are paired player fields.
     * Their X coordinates are relative to the combat draw offset (+256).
     * Hidden fields use +512: right anchoring keeps them outside the reveal. */
    return (int16_t)psx_mod_read_half(packet + 8u) < 0 ? -1 : 1;
}

static int is_gradient(uint32_t packet, uint32_t words, uint32_t opcode) {
    if (words != 8u || opcode != 0x38u) return 0;
    if (packet != 0x801D0000u && packet != 0x801D0024u &&
        packet != 0x801D3000u && packet != 0x801D3024u) return 0;
    /* The two G4s span the whole authored sky/floor, with equal colours
     * across each horizontal edge. Do not stretch geometry sharing a pool. */
    return (int16_t)psx_mod_read_half(packet + 8u) == -256 &&
        (int16_t)psx_mod_read_half(packet + 16u) == 256 &&
        (int16_t)psx_mod_read_half(packet + 24u) == -256 &&
        (int16_t)psx_mod_read_half(packet + 32u) == 256 &&
        (psx_mod_read_word(packet + 4u) & 0xFFFFFFu) ==
            (psx_mod_read_word(packet + 12u) & 0xFFFFFFu) &&
        psx_mod_read_word(packet + 20u) == psx_mod_read_word(packet + 28u);
}

static void tag_list(CPUState *cpu, uint32_t address) {
    uint32_t current = cpu->gpr[4] & 0x1FFFFFFFu;
    uint32_t visited;
    if (address != FB_SUBMIT || psx_mod_widescreen_view_x_margin() <= 0 ||
        !combat_layout_matches()) return;

    for (visited = 0; visited < FB_WALK_LIMIT; ++visited) {
        uint32_t packet, tag, words, opcode;
        if ((current & 3u) || current > 0x1FFFFBu) break;
        packet = current | 0x80000000u;
        tag = psx_mod_read_word(packet);
        words = tag >> 24;
        if (words > (0x200000u - current - 4u) / 4u) break;
        opcode = words ? psx_mod_read_word(packet + 4u) >> 24 : 0;
        if (packet >= FB_HUD_BASE &&
            packet < FB_HUD_BASE + 2u * FB_HUD_STRIDE &&
            ((words == 4u && (opcode & 0xFCu) == 0x64u) ||
             (words == 8u && (opcode & 0xFDu) == 0x38u))) {
            psx_mod_anchor_hud_primitive(packet, hud_anchor(packet));
            psx_mod_counter_add("finalbout.ws.hud", 1u);
        } else if (is_gradient(packet, words, opcode)) {
            gpu_ws_tag_background_prim(packet);
            psx_mod_counter_add("finalbout.ws.gradient", 1u);
        }
        current = tag & 0xFFFFFFu;
        if (current == 0xFFFFFFu) break;
    }
    if (visited == FB_WALK_LIMIT)
        psx_mod_counter_add("finalbout.ws.walk_limit", 1u);
}

static void fixed_activate(void) {
    (void)psx_mod_set_fixed_display_aspect(16u, 9u);
}

static void adaptive_activate(void) {
    (void)psx_mod_set_fixed_display_aspect(16u, 9u);
    (void)psx_mod_set_adaptive_display_aspect(21u, 9u);
}

PSX_MOD_CONSTRUCTOR(final_bout_register_widescreen) {
    (void)psx_mod_register_activation_plugin("finalbout.widescreen.fixed", fixed_activate);
    (void)psx_mod_register_activation_plugin("finalbout.widescreen.adaptive", adaptive_activate);
    (void)psx_mod_register_function_entry_plugin("finalbout.widescreen.packets", FB_SUBMIT, tag_list);
}
