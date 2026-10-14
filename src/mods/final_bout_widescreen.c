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

static int hud_anchor(uint32_t packet, uint32_t words, uint32_t opcode,
                      int *anchor) {
    uint32_t role = (packet - FB_HUD_BASE) % FB_HUD_STRIDE;
    /* 8006A538..8006AC10 initializes these exact packet starts; the
     * 8006B0A0 submitter uses the same offsets. Never classify packet interiors
     * or accept another command shape merely because it is inside the bank. */
    if (words == 4u && (opcode & 0xFCu) == 0x64u) {
        switch (role) {
        case 0x08u: case 0x1Cu: /* VS / PAUSE */
            *anchor = 0; return 1;
        case 0x30u: case 0xBCu: case 0xD0u: case 0x10Cu: case 0x120u:
        case 0x44u: case 0xE4u: case 0xF8u: case 0x134u: case 0x148u:
        case 0x58u: case 0x6Cu: case 0x80u: case 0x94u: case 0xA8u:
            break;
        default: return 0;
        }
    } else if (words == 8u && (opcode & 0xFDu) == 0x38u) {
        switch (role) {
        case 0x15Cu: case 0x180u: case 0x1A4u: case 0x1C8u:
        case 0x27Cu: case 0x2A0u:
        case 0x1ECu: case 0x210u: case 0x234u: case 0x258u:
        case 0x2C4u: case 0x2E8u:
            break;
        default: return 0;
        }
    } else return 0;
    /* Preserve the observed signed-X rule for all qualified noncentre fields.
     * Dynamic status producers can change sides; hidden +512 fields must stay
     * beyond the right reveal even when their usual player role is left. */
    *anchor = (int16_t)psx_mod_read_half(packet + 8u) < 0 ? -1 : 1;
    return 1;
}

static int gradient_shape_matches(uint32_t packet, uint32_t words, uint32_t opcode) {
    if (words != 8u || opcode != 0x38u) return 0;
    /* The two G4s span the whole authored sky/floor, with equal colours
     * across each horizontal edge. Do not stretch geometry sharing a pool. */
    return (int16_t)psx_mod_read_half(packet + 8u) == -256 &&
        (int16_t)psx_mod_read_half(packet + 16u) == 256 &&
        (int16_t)psx_mod_read_half(packet + 24u) == -256 &&
        (int16_t)psx_mod_read_half(packet + 32u) == 256 &&
        (int16_t)psx_mod_read_half(packet + 10u) ==
            (int16_t)psx_mod_read_half(packet + 18u) &&
        (int16_t)psx_mod_read_half(packet + 26u) ==
            (int16_t)psx_mod_read_half(packet + 34u) &&
        (int16_t)psx_mod_read_half(packet + 10u) <
            (int16_t)psx_mod_read_half(packet + 26u) &&
        (psx_mod_read_word(packet + 4u) & 0xFFFFFFu) ==
            (psx_mod_read_word(packet + 12u) & 0xFFFFFFu) &&
        psx_mod_read_word(packet + 20u) == psx_mod_read_word(packet + 28u);
}

static int is_gradient(uint32_t packet, uint32_t words, uint32_t opcode) {
    if (packet != 0x801D0000u && packet != 0x801D0024u &&
        packet != 0x801D3000u && packet != 0x801D3024u) return 0;
    return gradient_shape_matches(packet, words, opcode);
}

/* 8004D534 submits the stage panorama object through 80020C3C. Its source
 * map is 32 columns by four rows of 32px tiles; the authored view is 512x128.
 * Earlier effects share the packet pool, so discover the completed composite
 * from its contents and links rather than assuming it starts at the pool base.
 * Unknown object/map layouts retain the original presentation. */
static int sky_layout_matches(int *top) {
    if (psx_mod_read_word(0x8004D534u) != 0x0C00830Fu ||
        psx_mod_read_word(0x80020C3Cu) != 0x27BDFF58u ||
        psx_mod_read_word(0x80020C80u) != 0x8DE90014u ||
        (psx_mod_read_word(0x800A9BDCu) & 0x80000000u) ||
        psx_mod_read_word(0x800A9BE4u) != 0x00800200u ||
        psx_mod_read_word(0x800A9BECu) != 0x00808080u ||
        psx_mod_read_word(0x800A9BF0u) != 0x800A9C00u ||
        psx_mod_read_word(0x800A9BF4u) != 0x00400100u ||
        psx_mod_read_half(0x800A9BEAu) != 0u ||
        psx_mod_read_word(0x800A9C00u) != 0x00202020u ||
        psx_mod_read_word(0x800A9C04u) != 4u ||
        psx_mod_read_word(0x800A9C08u) != 0x801B1008u ||
        psx_mod_read_word(0x800A9C0Cu) != 0x801B0008u ||
        (int16_t)psx_mod_read_half(0x800A9BE0u) +
            (int16_t)psx_mod_read_half(0x8003BC4Au) != 0) return 0;
    *top = (int16_t)psx_mod_read_half(0x800A9BE2u) - 64 +
        (int16_t)psx_mod_read_half(0x8003BC4Cu);
    return 1;
}

static int sky_texture_matches(uint32_t draw_mode, uint32_t uv,
                               uint32_t width) {
    uint32_t i;
    /* Each submitted tile must belong to this object's actual source atlas.
     * Edge tiles may crop U; the qualified producer has no vertical crop. */
    for (i = 0; i < 128u; ++i) {
        uint32_t source_uv = psx_mod_read_word(0x801B1008u + i * 8u);
        uint32_t source_page = psx_mod_read_word(0x801B100Cu + i * 8u) >> 16;
        int u_delta = (int)(uv & 255u) - (int)(source_uv & 255u);
        if (draw_mode == (0xE1000200u | (source_page & 0x1FFu)) &&
            (uv & 0xFFFFFF00u) == (source_uv & 0xFFFFFF00u) &&
            u_delta >= 0 && (uint32_t)u_delta + width <= 32u)
            return 1;
    }
    return 0;
}

static int tag_sky_composite(uint32_t first) {
    uint32_t bank, packet, row, count = 0;
    int top;
    if (first >= 0x801D0000u && first < 0x801D3000u) bank = 0x801D0000u;
    else if (first >= 0x801D3000u && first < 0x801D6000u) bank = 0x801D3000u;
    else return 0;
    if ((int16_t)psx_mod_read_half(first + 12u) != -256 ||
        !sky_layout_matches(&top) ||
        (int16_t)psx_mod_read_half(first + 14u) != top) return 0;
    packet = first;
    for (row = 0; row < 4u; ++row) {
        int x = -256;
        uint32_t columns = 0;
        while (x < 256) {
            uint32_t tag, size, width, next;
            if (packet > bank + 0x3000u - 24u || columns == 17u) return 0;
            tag = psx_mod_read_word(packet);
            size = psx_mod_read_word(packet + 20u);
            width = size & 0xFFFFu;
            /* Last tile links back to the selected four-entry sky OT, not
             * to the adjacent gradient (which sorts in a different OT). */
            next = row == 3u && x + (int)width == 256
                ? (bank == 0x801D0000u ? 0x001E3000u : 0x001E4000u)
                : ((packet + 24u) & 0xFFFFFFu);
            if ((tag >> 24) != 5u ||
                (tag & 0xFFFFFFu) != next ||
                psx_mod_read_word(packet + 8u) != 0x64808080u ||
                (int16_t)psx_mod_read_half(packet + 12u) != x ||
                (int16_t)psx_mod_read_half(packet + 14u) != top + (int)row * 32 ||
                !width || width > 32u || (size >> 16) != 32u ||
                x + (int)width > 256 ||
                (columns && x + (int)width < 256 && width != 32u) ||
                !sky_texture_matches(psx_mod_read_word(packet + 4u),
                                     psx_mod_read_word(packet + 16u), width))
                return 0;
            x += (int)width;
            packet += 24u;
            ++columns;
            ++count;
        }
    }
    /* The same producer's full-width gradient follows the tiled sky. Validate
     * it before tagging anything: failed composites cannot leave partial tags. */
    if (packet > bank + 0x3000u - 36u ||
        !gradient_shape_matches(packet, psx_mod_read_word(packet) >> 24,
                                psx_mod_read_word(packet + 4u) >> 24)) return 0;
    gpu_ws_tag_background_prim(packet);
    for (row = 0; row < count; ++row)
        /* The compound E1 precedes SPRT; the service adds four to this word. */
        gpu_ws_tag_background_prim(first + row * 24u + 4u);
    psx_mod_counter_add("finalbout.ws.sky", count);
    psx_mod_counter_add("finalbout.ws.gradient", 1u);
    return 1;
}

static void tag_list(CPUState *cpu, uint32_t address) {
    uint32_t current = cpu->gpr[4] & 0x1FFFFFFFu;
    uint32_t visited;
    if (address != FB_SUBMIT || psx_mod_widescreen_view_x_margin() <= 0 ||
        !combat_layout_matches()) return;

    for (visited = 0; visited < FB_WALK_LIMIT; ++visited) {
        uint32_t packet, tag, words, opcode;
        int anchor;
        if ((current & 3u) || current > 0x1FFFFBu) break;
        packet = current | 0x80000000u;
        tag = psx_mod_read_word(packet);
        words = tag >> 24;
        if (words > (0x200000u - current - 4u) / 4u) break;
        opcode = words ? psx_mod_read_word(packet + 4u) >> 24 : 0;
        if (packet >= FB_HUD_BASE &&
            packet < FB_HUD_BASE + 2u * FB_HUD_STRIDE &&
            hud_anchor(packet, words, opcode, &anchor)) {
            psx_mod_anchor_hud_primitive(packet, anchor);
            psx_mod_counter_add("finalbout.ws.hud", 1u);
        } else if (is_gradient(packet, words, opcode)) {
            gpu_ws_tag_background_prim(packet);
            psx_mod_counter_add("finalbout.ws.gradient", 1u);
        } else if (words == 5u && opcode == 0xE1u) {
            (void)tag_sky_composite(packet);
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
