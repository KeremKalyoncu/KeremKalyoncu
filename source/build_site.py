"""Zero-CDN Obsidian Atlas interactive companion site generator.

Run from repository root:
    python source/build_site.py
or via thin root launcher:
    python build_site.py
or from source/:
    python build_site.py

Deterministically writes root `index.html` from canonical `source/profile_spec.py`.
Does NOT modify `README.md` or `assets/atlas-*.svg`.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
import sys

SOURCE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SOURCE_DIR.parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import profile_spec as spec  # noqa: E402

PALETTE = spec.PALETTE
FONTS = spec.FONTS
BRAND = spec.BRAND
PROFILE = spec.PROFILE
PROJECTS = spec.PROJECTS
SUPPORTING_REPOS = spec.SUPPORTING_REPOS
TIMELINE = spec.TIMELINE
TECH_PILLARS = spec.TECH_PILLARS

# Closed-polygon chamfered vector lettering on 0..100 cap-height grid (shared with M1 plates).
GLYPHS: dict[str, tuple[int, str]] = {
    "A": (78, "M28,0 H50 L78,100 H59 L52,74 H26 L19,100 H0 Z M39,20 L29,56 H49 Z"),
    "C": (74, "M12,0 H62 L74,12 V30 H56 V18 H18 V82 H56 V70 H74 V88 L62,100 H12 L0,88 V12 Z"),
    "E": (68, "M0,0 H68 V18 H18 V41 H58 V59 H18 V82 H68 V100 H0 Z"),
    "K": (76, "M0,0 H18 V100 H0 Z M18,44 L54,0 H76 L38,48 L76,100 H54 L18,54 Z"),
    "L": (64, "M0,0 H18 V82 H64 V100 H0 Z"),
    "M": (88, "M0,0 H20 L44,46 L68,0 H88 V100 H70 V34 L49,74 H39 L18,34 V100 H0 Z"),
    "N": (78, "M0,0 H20 L60,68 V0 H78 V100 H58 L18,32 V100 H0 Z"),
    "O": (78, "M12,0 H66 L78,12 V88 L66,100 H12 L0,88 V12 Z M22,18 H56 L60,22 V78 L56,82 H22 L18,78 V22 Z"),
    "R": (76, "M0,0 H62 L74,12 V44 L62,56 H48 L76,100 H54 L28,56 H18 V100 H0 Z M18,18 H53 L56,21 V35 L53,38 H18 Z"),
    "U": (76, "M0,0 H18 V78 L22,82 H54 L58,78 V0 H76 V88 L64,100 H12 L0,88 Z"),
    "Y": (76, "M0,0 H21 L38,38 L55,0 H76 L47,56 V100 H29 V56 Z"),
    " ": (32, ""),
}

RIDGE_CONTOURS: list[tuple[str, str, str]] = [
    ("M582,196 C606,120 664,84 726,92 C792,100 842,138 854,194 C862,232 824,274 756,280 C686,286 566,252 582,196 Z", "#1E293B", "1.1"),
    ("M602,188 C622,130 670,102 722,108 C778,114 820,146 832,190 C840,222 806,256 750,262 C692,268 588,236 602,188 Z", "#233044", "1.1"),
    ("M624,180 C642,136 680,116 720,120 C764,126 798,150 808,186 C814,212 786,238 744,244 C698,250 612,218 624,180 Z", "#283548", "1.1"),
    ("M646,170 C660,140 688,128 718,132 C752,136 776,154 784,180 C790,200 768,220 736,226 C702,232 636,200 646,170 Z", "#2D3B50", "1.2"),
    ("M666,162 C676,144 696,138 716,142 C738,146 756,158 762,174 C766,188 748,202 728,206 C704,210 658,184 666,162 Z", "#334155", "1.2"),
    ("M682,156 C690,146 702,144 714,148 C726,152 736,160 738,170 C740,178 728,186 716,188 C702,190 676,170 682,156 Z", "#334155", "1.3"),
    ("M734,182 C742,172 758,170 768,176 C778,182 782,194 774,202 C766,210 748,210 738,202 C730,196 728,188 734,182 Z", "#283548", "1.0"),
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_json_embed(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return raw.replace("</", "<\\/").replace("<!--", "<\\!--")


def render_wordmark_svg() -> str:
    """Render animated chamfered KK emblem + KEREM KALYONCU wordmark (frame-0 visible)."""
    parts: list[str] = [
        '<svg class="hero-wordmark-svg" viewBox="0 0 680 112" role="img" '
        'aria-label="KEREM KALYONCU geometric vector wordmark" aria-hidden="true">'
    ]
    # Geometric KK monogram badge (0..54, 4..58)
    parts.append(
        '<g class="kk-monogram" transform="translate(2,6)">'
        f'<polygon points="6,0 52,0 58,6 58,52 52,58 6,58 0,52 0,6" fill="{PALETTE["bg_bay"]}" '
        f'stroke="{PALETTE["accent_orange"]}" stroke-width="1.6"/>'
        f'<path class="glyph-draw" style="--glyph-delay:0ms" d="M11,11 H18 V47 H11 Z M18,28 L33,11 H42 L25,29 L42,47 H33 L18,30 Z" '
        f'fill="{PALETTE["accent_orange"]}" fill-rule="evenodd" stroke="{PALETTE["accent_orange"]}" stroke-width="0.9"/>'
        f'<path d="M40,11 H47 V47 H40 Z" fill="{PALETTE["ink_primary"]}" opacity="0.85"/>'
        "</g>"
    )

    # Row 1: KEREM (x=76, y=4, scale=0.44)
    # Row 2: KALYONCU (x=76, y=60, scale=0.44)
    rows = [("KEREM", 76.0, 4.0, 0), ("KALYONCU", 76.0, 60.0, 5)]
    scale = 0.44
    gap = 14.0
    for word, start_x, start_y, idx_offset in rows:
        parts.append(f'<g transform="translate({start_x:.1f},{start_y:.1f}) scale({scale:.4f})">')
        cursor = 0.0
        for i, ch in enumerate(word):
            adv, d = GLYPHS[ch]
            if d:
                delay = (idx_offset + i) * 45
                fill_col = PALETTE["ink_primary"]
                stroke_col = PALETTE["accent_orange"] if (idx_offset == 0 and i == 0) else PALETTE["ink_primary"]
                parts.append(
                    f'<path class="glyph-draw" style="--glyph-delay:{delay}ms" '
                    f'd="{d}" transform="translate({cursor:.1f},0)" '
                    f'fill="{fill_col}" fill-rule="evenodd" '
                    f'stroke="{stroke_col}" stroke-width="2.2" stroke-linejoin="round"/>'
                )
            cursor += adv + gap
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def render_topo_bay_svg() -> str:
    """Render authentic Bosphorus Strait vector cartography + live TSS lane + reticle inside Hero Topo Bay."""
    rumeli_land = (
        "M 574,54 L 724,54 "
        "C 716,74 694,90 682,108 "
        "C 672,122 688,136 696,150 "
        "C 702,162 686,178 678,194 "
        "C 670,208 660,218 648,220 "
        "C 628,214 608,204 596,198 "
        "C 604,210 626,222 646,228 "
        "C 656,236 654,254 638,274 "
        "C 624,286 600,294 574,294 Z"
    )
    anadolu_land = (
        "M 860,54 L 764,54 "
        "C 750,74 734,94 726,114 "
        "C 720,130 714,142 716,154 "
        "C 718,166 728,178 722,194 "
        "C 716,208 702,220 704,234 "
        "C 706,248 724,264 748,282 "
        "L 768,294 L 860,294 Z"
    )
    inland_contours = [
        ("M 574,72 L 696,72 C 686,90 664,106 656,124 C 650,140 668,154 662,174 C 654,192 634,196 574,186", "#163654", "0.9"),
        ("M 574,244 C 604,244 630,248 626,264 C 620,278 596,286 574,288", "#163654", "0.9"),
        ("M 860,82 L 778,82 C 760,102 746,124 744,150 C 742,176 752,196 736,222 C 728,236 746,258 788,284 L 860,284", "#163654", "0.9"),
        ("M 860,118 L 798,118 C 778,138 768,162 768,190 C 768,218 778,242 812,268 L 860,268", "#1E4970", "0.8"),
    ]
    tss_lane = "M 744,54 C 724,84 704,112 706,152 C 708,180 694,204 678,234 C 668,256 682,278 696,294"

    parts: list[str] = [
        '<svg class="topo-svg" viewBox="574 54 286 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
        "<defs>"
        '<radialGradient id="hero-beacon-aura" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{PALETTE["accent_orange"]}" stop-opacity="0.28"/>'
        f'<stop offset="60%" stop-color="{PALETTE["accent_emerald"]}" stop-opacity="0.08"/>'
        f'<stop offset="100%" stop-color="{PALETTE["accent_orange"]}" stop-opacity="0"/>'
        "</radialGradient>"
        "</defs>"
    ]
    parts.append(
        f'<path d="{rumeli_land}" fill="{PALETTE["bg_plate"]}" stroke="{PALETTE["border_active"]}" stroke-width="1.3" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<path d="{anadolu_land}" fill="{PALETTE["bg_plate"]}" stroke="{PALETTE["border_active"]}" stroke-width="1.3" stroke-linejoin="round"/>'
    )
    for d, col, sw in inland_contours:
        parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"/>')

    for bx1, by1, bx2, by2 in ((714, 68, 752, 68), (696, 151, 716, 153), (676, 198, 718, 202)):
        parts.append(
            f'<line x1="{bx1}" y1="{by1}" x2="{bx2}" y2="{by2}" stroke="{PALETTE["accent_amber"]}" '
            'stroke-width="1.2" stroke-dasharray="2 1.5" stroke-opacity="0.8"/>'
        )
    parts.append(
        f'<path d="{tss_lane}" fill="none" stroke="{PALETTE["border_active"]}" stroke-width="1" stroke-dasharray="3 3" stroke-opacity="0.75"/>'
    )
    parts.append(
        f'<path d="{tss_lane}" fill="none" stroke="{PALETTE["accent_orange"]}" stroke-width="1.6" stroke-dasharray="8 24"/>'
    )
    parts.append(f'<circle cx="720" cy="96" r="2.3" fill="{PALETTE["accent_emerald"]}"/>')
    parts.append(f'<circle cx="680" cy="228" r="2.3" fill="{PALETTE["accent_amber"]}"/>')

    rx, ry = 706, 164
    parts.append('<g class="topo-reticle-layer">')
    parts.append(f'<circle cx="{rx}" cy="{ry}" r="60" fill="url(#hero-beacon-aura)"/>')
    parts.append(
        f'<circle cx="{rx}" cy="{ry}" r="20" fill="none" stroke="{PALETTE["accent_orange"]}" '
        'stroke-width="1.1" stroke-opacity="0.65"/>'
    )
    parts.append(
        f'<circle cx="{rx}" cy="{ry}" r="42" fill="none" stroke="{PALETTE["border_active"]}" '
        'stroke-width="0.9" stroke-dasharray="3 3" stroke-opacity="0.75"/>'
    )
    parts.append(
        f'<path d="M612,{ry} H800 M{rx},84 V244" fill="none" stroke="{PALETTE["border_active"]}" '
        'stroke-width="0.75" stroke-opacity="0.5"/>'
    )
    parts.append(
        f'<circle class="reticle-pulse" cx="{rx}" cy="{ry}" r="16" fill="none" '
        f'stroke="{PALETTE["accent_orange"]}" stroke-width="1.3"/>'
    )
    parts.append(f'<circle cx="{rx}" cy="{ry}" r="4" fill="{PALETTE["accent_orange"]}"/>')
    parts.append(f'<circle cx="{rx}" cy="{ry}" r="1.7" fill="{PALETTE["ink_primary"]}"/>')
    parts.append("</g></svg>")
    return "".join(parts)


def render_project_micro_diagram(project: dict) -> str:
    """Render bespoke dual-layer 320x112 inline SVG micro-diagram for each core system."""
    pid = project["id"]
    accent = PALETTE[project["accent"]]
    bg_plate = PALETTE["bg_plate"]
    bg_bay = PALETTE["bg_bay"]
    bg_hover = PALETTE["bg_hover"]
    grid = PALETTE["border_grid"]
    active = PALETTE["border_active"]
    ink_p = PALETTE["ink_primary"]
    ink_s = PALETTE["ink_secondary"]
    ink_c = PALETTE["ink_caption"]
    orange = PALETTE["accent_orange"]
    amber = PALETTE["accent_amber"]
    emerald = PALETTE["accent_emerald"]
    indigo = PALETTE["accent_indigo"]

    parts: list[str] = [
        f'<svg class="micro-svg" viewBox="0 0 320 112" role="img" '
        f'aria-label="{esc(project["title"])} live telemetry micro-diagram">'
        # Left emblem container (0..92) + separator
        f'<rect x="6" y="8" width="82" height="96" rx="5" fill="{bg_plate}" stroke="{grid}" stroke-width="1"/>'
        f'<rect x="96" y="8" width="218" height="96" rx="5" fill="{bg_plate}" stroke="{grid}" stroke-width="1"/>'
    ]

    if pid == "maritime-watch":
        # Left: AIS Radar Sweep (centered at 47, 56)
        parts.append('<g transform="translate(9,18)">')
        parts.append(f'<path d="M38,8 V68 M8,38 H68" fill="none" stroke="{grid}" stroke-width="1"/>')
        for r, col in ((10, grid), (20, active), (29, active)):
            parts.append(f'<circle cx="38" cy="38" r="{r}" fill="none" stroke="{col}" stroke-width="1"/>')
        parts.append(
            '<g class="radar-sweep">'
            f'<path d="M38,38 L38,9 A29,29 0 0,1 63,23 Z" fill="{orange}" fill-opacity="0.24"/>'
            f'<line x1="38" y1="38" x2="38" y2="9" stroke="{orange}" stroke-width="1.6"/>'
            "</g>"
        )
        parts.append(f'<circle cx="52" cy="24" r="2.6" fill="{emerald}"/>')
        parts.append(f'<circle cx="24" cy="49" r="2.2" fill="{amber}"/>')
        parts.append(f'<circle cx="38" cy="38" r="2.8" fill="{orange}"/>')
        parts.append("</g>")

        # Right: Go / Caution / No-Go deterministic pipeline
        parts.append(
            f'<rect x="106" y="16" width="54" height="20" rx="3" fill="{bg_hover}" stroke="{emerald}" stroke-width="1.2"/>'
            f'<circle cx="116" cy="26" r="3" fill="{emerald}"/>'
            f'<text x="124" y="29.5" class="svg-mono" fill="{emerald}" font-size="9" font-weight="700">GO</text>'
            f'<rect x="166" y="16" width="66" height="20" rx="3" fill="{bg_bay}" stroke="{amber}" stroke-width="0.9"/>'
            f'<text x="199" y="29.5" text-anchor="middle" class="svg-mono" fill="{amber}" font-size="8.5">CAUTION</text>'
            f'<rect x="238" y="16" width="66" height="20" rx="3" fill="{bg_bay}" stroke="{orange}" stroke-width="0.9"/>'
            f'<text x="271" y="29.5" text-anchor="middle" class="svg-mono" fill="{orange}" font-size="8.5">NO-GO</text>'
        )
        # 3-tier pipeline
        parts.append(
            f'<path d="M164,66 H184 M242,66 H258" fill="none" stroke="{active}" stroke-width="1.4"/>'
            f'<path class="bus-pulse" d="M164,66 H184 M242,66 H258" fill="none" stroke="{emerald}" stroke-width="1.8"/>'
            f'<rect x="106" y="48" width="58" height="36" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="135" y="63" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8.5" font-weight="700">AIS+METEO</text>'
            f'<text x="135" y="76" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7.5">INGEST</text>'
            f'<rect x="184" y="48" width="58" height="36" rx="4" fill="{bg_hover}" stroke="{emerald}" stroke-width="1.2"/>'
            f'<text x="213" y="63" text-anchor="middle" class="svg-mono" fill="{emerald}" font-size="8.5" font-weight="700">NOTE 4</text>'
            f'<text x="213" y="76" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="7.5">~1.2W CORE</text>'
            f'<rect x="258" y="48" width="46" height="36" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="281" y="63" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8.5" font-weight="700">PWA</text>'
            f'<text x="281" y="76" text-anchor="middle" class="svg-mono" fill="{amber}" font-size="7.5">/mayday</text>'
        )

    elif pid == "inventra":
        # Left: Isometric SKU Wireframe Cube
        parts.append('<g transform="translate(9,18)">')
        parts.append(
            f'<polygon points="38,11 62,25 62,51 38,65 14,51 14,25" fill="{bg_bay}" stroke="{active}" stroke-width="1.4"/>'
            f'<path d="M14,25 L38,38 L62,25 M38,38 V65" fill="none" stroke="{amber}" stroke-width="1.4"/>'
            f'<polygon points="38,24 49,30 49,44 38,50 27,44 27,30" fill="none" stroke="{orange}" stroke-width="1.2"/>'
        )
        for vx, vy in ((38, 11), (62, 25), (62, 51), (38, 65), (14, 51), (14, 25)):
            parts.append(f'<circle cx="{vx}" cy="{vy}" r="2.1" fill="{ink_p}"/>')
        parts.append("</g>")

        # Right: Hub-and-spoke inventory & audit ledger
        parts.append(
            f'<path d="M162,56 H182 M238,56 L256,34 M238,56 L256,78" fill="none" stroke="{active}" stroke-width="1.4"/>'
            f'<path class="bus-pulse" d="M162,56 H182 M238,56 L256,34 M238,56 L256,78" fill="none" stroke="{orange}" stroke-width="1.8"/>'
            f'<rect x="106" y="38" width="56" height="36" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="134" y="53" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8.5" font-weight="700">REACT</text>'
            f'<text x="134" y="65" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7.5">MUI CLIENT</text>'
            f'<rect x="182" y="36" width="56" height="40" rx="4" fill="{bg_hover}" stroke="{orange}" stroke-width="1.2"/>'
            f'<text x="210" y="52" text-anchor="middle" class="svg-mono" fill="{orange}" font-size="8.5" font-weight="700">ASP.NET</text>'
            f'<text x="210" y="65" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="7.5">REST / JWT</text>'
            f'<rect x="256" y="18" width="48" height="30" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="280" y="31" text-anchor="middle" class="svg-mono" fill="{amber}" font-size="8" font-weight="700">PGSQL</text>'
            f'<text x="280" y="42" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7">ACID</text>'
            f'<rect x="256" y="64" width="48" height="30" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="280" y="77" text-anchor="middle" class="svg-mono" fill="{emerald}" font-size="8" font-weight="700">AUDIT</text>'
            f'<text x="280" y="88" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7">LEDGER</text>'
        )

    elif pid == "restofy":
        # Left: Modular Order-Dispatch Grid
        parts.append('<g transform="translate(9,18)">')
        for cx, cy in ((11, 14), (31, 14), (51, 14), (11, 30), (31, 30), (51, 30)):
            if (cx, cy) == (31, 14):
                fc, sc = orange, orange
            elif (cx, cy) == (51, 30):
                fc, sc = emerald, emerald
            else:
                fc, sc = bg_bay, active
            parts.append(f'<rect x="{cx}" y="{cy}" width="14" height="10" rx="2" fill="{fc}" stroke="{sc}" stroke-width="1.1"/>')
        parts.append(
            f'<path d="M18,40 V46 H38 V51 M38,40 V51 M58,40 V46 H38" fill="none" stroke="{active}" stroke-width="1.2"/>'
            f'<rect x="24" y="51" width="28" height="13" rx="2" fill="{bg_hover}" stroke="{amber}" stroke-width="1.2"/>'
            f'<circle cx="38" cy="57.5" r="2.2" fill="{emerald}"/>'
            "</g>"
        )

        # Right: Microservices bus + Docker mesh
        parts.append(
            f'<rect x="224" y="16" width="80" height="80" rx="5" fill="{bg_bay}" stroke="{amber}" stroke-dasharray="3 3" stroke-width="1"/>'
            f'<text x="264" y="28" text-anchor="middle" class="svg-mono" fill="{amber}" font-size="7.5" font-weight="700">DOCKER MESH</text>'
            f'<path d="M150,56 H166 M212,56 L232,44 M212,56 L232,72" fill="none" stroke="{active}" stroke-width="1.3"/>'
            f'<path class="bus-pulse" d="M150,56 H166 M212,56 L232,44 M212,56 L232,72" fill="none" stroke="{amber}" stroke-width="1.8"/>'
            f'<rect x="106" y="38" width="44" height="36" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="128" y="53" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8.5" font-weight="700">QR</text>'
            f'<text x="128" y="65" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7.5">TABLE</text>'
            f'<rect x="166" y="38" width="46" height="36" rx="4" fill="{bg_hover}" stroke="{amber}" stroke-width="1.2"/>'
            f'<text x="189" y="53" text-anchor="middle" class="svg-mono" fill="{amber}" font-size="8.5" font-weight="700">API</text>'
            f'<text x="189" y="65" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="7.5">GW</text>'
            f'<rect x="232" y="34" width="64" height="22" rx="3" fill="{bg_plate}" stroke="{orange}"/>'
            f'<text x="264" y="48" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8">ORDER SVC</text>'
            f'<rect x="232" y="64" width="64" height="22" rx="3" fill="{bg_plate}" stroke="{emerald}"/>'
            f'<text x="264" y="78" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8">MENU SVC</text>'
        )

    elif pid == "shifha":
        # Left: Clinical ECG / Protocol Waveform
        parts.append('<g transform="translate(9,18)">')
        parts.append(
            f'<path d="M8,24 H68 M8,38 H68 M8,52 H68 M20,10 V66 M38,10 V66 M56,10 V66" fill="none" stroke="{grid}" stroke-width="0.7"/>'
            f'<path d="M8,41 H19 L23,35 L27,41 L31,46 L36,15 L41,59 L45,41 L52,33 L57,41 H68" '
            f'fill="none" stroke="{orange}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="36" cy="15" r="2.5" fill="{ink_p}"/>'
            f'<circle class="pulse-dot" cx="52" cy="33" r="2.8" fill="{indigo}"/>'
            "</g>"
        )

        # Right: Clinical NLP triage + confidence bars
        parts.append(
            f'<path d="M158,56 H176 M228,56 H244" fill="none" stroke="{active}" stroke-width="1.3"/>'
            f'<path class="bus-pulse" d="M158,56 H176 M228,56 H244" fill="none" stroke="{indigo}" stroke-width="1.8"/>'
            f'<rect x="106" y="38" width="52" height="36" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="132" y="53" text-anchor="middle" class="svg-mono" fill="{ink_p}" font-size="8" font-weight="700">RN APP</text>'
            f'<text x="132" y="65" text-anchor="middle" class="svg-mono" fill="{ink_c}" font-size="7.5">NOTES</text>'
            f'<rect x="176" y="36" width="52" height="40" rx="4" fill="{bg_hover}" stroke="{indigo}" stroke-width="1.2"/>'
            f'<text x="202" y="52" text-anchor="middle" class="svg-mono" fill="{indigo}" font-size="8" font-weight="700">MED NLP</text>'
            f'<text x="202" y="65" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="7.5">EXTRACT</text>'
            f'<rect x="244" y="20" width="60" height="72" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<text x="274" y="33" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="7.5" font-weight="700">TRIAGE</text>'
            f'<rect x="252" y="42" width="44" height="6" rx="2" fill="{grid}"/>'
            f'<rect x="252" y="42" width="41" height="6" rx="2" fill="{emerald}"/>'
            f'<rect x="252" y="56" width="44" height="6" rx="2" fill="{grid}"/>'
            f'<rect x="252" y="56" width="36" height="6" rx="2" fill="{indigo}"/>'
            f'<rect x="252" y="70" width="44" height="6" rx="2" fill="{grid}"/>'
            f'<rect x="252" y="70" width="29" height="6" rx="2" fill="{amber}"/>'
        )

    elif pid == "kriptoparatakip":
        # Left: Candlesticks
        parts.append('<g transform="translate(9,18)">')
        parts.append(f'<path d="M10,60 H66 M10,14 V60" fill="none" stroke="{active}" stroke-width="1"/>')
        for cx, wy1, wy2, by, bh, col in (
            (18, 36, 54, 41, 10, emerald),
            (28, 34, 52, 39, 9, orange),
            (38, 22, 46, 28, 12, emerald),
            (48, 26, 48, 31, 10, orange),
            (58, 16, 38, 21, 12, emerald),
        ):
            parts.append(f'<line x1="{cx}" y1="{wy1}" x2="{cx}" y2="{wy2}" stroke="{col}" stroke-width="1.2"/>')
            parts.append(f'<rect x="{cx - 2.5}" y="{by}" width="5" height="{bh}" rx="1" fill="{col}"/>')
        parts.append(
            f'<path d="M14,48 L28,44 L38,30 L48,36 L62,19" fill="none" stroke="{amber}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<circle cx="62" cy="19" r="2.5" fill="{amber}"/>'
            "</g>"
        )

        # Right: Volatility threshold sparkline + REST -> JSON -> GUI
        parts.append(
            f'<rect x="106" y="16" width="198" height="58" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<line x1="112" y1="36" x2="298" y2="36" stroke="{orange}" stroke-width="1" stroke-dasharray="4 3"/>'
            f'<text x="294" y="28" text-anchor="end" class="svg-mono" fill="{orange}" font-size="7.5">ALERT THRESHOLD</text>'
            f'<polyline points="114,62 138,54 160,59 182,42 204,48 228,25 252,38 274,29 294,23" '
            f'fill="none" stroke="{emerald}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle class="pulse-dot" cx="228" cy="25" r="3.4" fill="{orange}"/>'
            f'<circle cx="294" cy="23" r="2.6" fill="{amber}"/>'
            f'<text x="205" y="92" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="8.5">'
            'REST STREAM  →  JSON RULES  →  JAVA DESKTOP ALERTS'
            "</text>"
        )

    else:
        # ml-data-lab: Left 3-4-2 Neural Topology
        parts.append('<g transform="translate(9,18)">')
        inp = [(15, 20), (15, 38), (15, 56)]
        hid = [(38, 14), (38, 30), (38, 46), (38, 62)]
        out = [(61, 28), (61, 48)]
        dom = {((15, 20), (38, 30)), ((15, 38), (38, 46)), ((38, 30), (61, 28)), ((38, 46), (61, 48))}
        for p1 in inp:
            for p2 in hid:
                is_d = (p1, p2) in dom
                parts.append(
                    f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
                    f'stroke="{indigo if is_d else active}" stroke-width="{1.2 if is_d else 0.8}" '
                    f'stroke-opacity="{0.95 if is_d else 0.6}"/>'
                )
        for p1 in hid:
            for p2 in out:
                is_d = (p1, p2) in dom
                parts.append(
                    f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
                    f'stroke="{indigo if is_d else active}" stroke-width="{1.2 if is_d else 0.8}" '
                    f'stroke-opacity="{0.95 if is_d else 0.6}"/>'
                )
        for nx, ny in inp + hid:
            parts.append(f'<circle cx="{nx}" cy="{ny}" r="3.2" fill="{bg_plate}" stroke="{indigo}" stroke-width="1.3"/>')
        for nx, ny in out:
            parts.append(f'<circle cx="{nx}" cy="{ny}" r="3.4" fill="{bg_plate}" stroke="{amber}" stroke-width="1.4"/>')
        parts.append("</g>")

        # Right: Regression fit curve + K-Fold CV
        parts.append(
            f'<rect x="106" y="16" width="198" height="58" rx="4" fill="{bg_bay}" stroke="{grid}"/>'
            f'<path d="M118,64 C152,60 184,48 214,38 C242,29 268,24 294,22" fill="none" stroke="{indigo}" stroke-width="2"/>'
        )
        for sx, sy, sc in (
            (126, 61, emerald), (144, 54, amber), (162, 57, emerald),
            (182, 44, indigo), (202, 45, emerald), (224, 34, amber),
            (248, 32, emerald), (272, 23, indigo), (288, 25, emerald),
        ):
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="2.3" fill="{sc}"/>')
        parts.append(
            f'<text x="116" y="28" class="svg-mono" fill="{indigo}" font-size="7.5" font-weight="700">FIT: R² / K-FOLD CV</text>'
            f'<text x="205" y="92" text-anchor="middle" class="svg-mono" fill="{ink_s}" font-size="8.5">'
            'PANDAS FE  →  GRIDSEARCHCV  →  LR · KNN · DT'
            "</text>"
        )

    parts.append("</svg>")
    return "".join(parts)


def render_hero_strip() -> str:
    timeline_by_id = {t["id"]: t for t in TIMELINE}
    cells = [
        ("vollsign", "VOLLSIGN · AUG 2026–PRESENT", "Software Engineer · Dev & QA"),
        ("x-etc", "X-ETC. · FEB–AUG 2026 (7M)", "Full-Stack Software Engineer"),
        ("dogus-bsc", f"DOĞUŞ UNIV. · {timeline_by_id['dogus-bsc']['period']}", "BSc Software Engineering"),
        ("gdg-dogus", f"GDG DOĞUŞ · {timeline_by_id['gdg-dogus']['period']}", "Social Media & Design Lead"),
    ]
    out: list[str] = ['<div class="hero-strip">']
    for tid, top_txt, sub_txt in cells:
        accent_hex = PALETTE[timeline_by_id[tid]["accent"]]
        out.append(
            f'<div class="strip-cell" style="--cell-accent:{accent_hex}">'
            f'<span class="strip-eyebrow">{esc(top_txt)}</span>'
            f'<span class="strip-value">{esc(sub_txt)}</span>'
            "</div>"
        )
    out.append("</div>")
    return "".join(out)


def render_project_cards() -> str:
    out: list[str] = []
    for idx, p in enumerate(PROJECTS):
        accent_hex = PALETTE[p["accent"]]
        span_cls = "bento-wide" if idx == 0 else ("bento-medium" if idx == 1 else "bento-half")
        stack_html = "".join(
            f'<span class="stack-pill">{esc(s)}</span>' for s in p["stack"][:4]
        )
        diagram_svg = render_project_micro_diagram(p)

        ext_url = p.get("url")
        ext_link_html = ""
        if ext_url:
            link_label = "Live Portal ↗" if "github.com" not in ext_url else "Repository ↗"
            ext_link_html = (
                f'<a class="btn-card-ext" href="{esc(ext_url)}" target="_blank" '
                f'rel="noopener noreferrer">{esc(link_label)}</a>'
            )

        out.append(
            f'<article class="bento-card {span_cls}" data-project-id="{esc(p["id"])}" '
            f'data-category="{esc(p["category"])}" style="--card-accent:{accent_hex}">'
            '<div class="card-top">'
            '<div class="card-meta">'
            f'<span class="card-code">{esc(p["code"])}</span>'
            f'<span class="card-cat">{esc(p["category"])}</span>'
            "</div>"
            f'<span class="status-pill" style="--pill-color:{accent_hex}">{esc(p["status"])}</span>'
            "</div>"
            f'<div class="diagram-bay">{diagram_svg}</div>'
            '<div class="card-copy">'
            f'<h3 class="card-title">{esc(p["title"])}</h3>'
            f'<p class="card-tagline">{esc(p["tagline"])}</p>'
            "</div>"
            f'<div class="card-stack">{stack_html}</div>'
            '<div class="card-actions">'
            f'<button type="button" class="btn-inspect" data-inspect-project="{esc(p["id"])}">'
            'Inspect Architecture <span aria-hidden="true">→</span></button>'
            f"{ext_link_html}"
            "</div>"
            "</article>"
        )
    return "".join(out)


def render_supporting_repos() -> str:
    out: list[str] = []
    for repo in SUPPORTING_REPOS:
        stack_html = "".join(
            f'<span class="mini-pill">{esc(s)}</span>' for s in repo["stack"][:3]
        )
        if repo.get("url"):
            action_html = (
                f'<a class="repo-link" href="{esc(repo["url"])}" target="_blank" '
                f'rel="noopener noreferrer">GitHub ↗</a>'
            )
            badge_html = '<span class="repo-vis repo-vis-pub">PUBLIC</span>'
        else:
            action_html = '<span class="repo-private-note">Private Repository</span>'
            badge_html = '<span class="repo-vis repo-vis-priv">PRIVATE</span>'

        out.append(
            f'<article class="repo-card" data-repo-id="{esc(repo["id"])}">'
            '<div class="repo-head">'
            f'{badge_html}'
            f'<h4 class="repo-title">{esc(repo["title"])}</h4>'
            "</div>"
            f'<p class="repo-summary">{esc(repo["summary"])}</p>'
            f'<div class="repo-stack">{stack_html}</div>'
            f'<div class="repo-foot">{action_html}</div>'
            "</article>"
        )
    return "".join(out)


def render_timeline_cards() -> str:
    out: list[str] = []
    for item in TIMELINE:
        accent_hex = PALETTE[item["accent"]]
        link_html = ""
        if item.get("url"):
            link_html = (
                f'<a class="tl-link" href="{esc(item["url"])}" target="_blank" '
                f'rel="noopener noreferrer">External Reference ↗</a>'
            )
        else:
            link_html = f'<span class="tl-cat">{esc(item["category"].upper())}</span>'

        out.append(
            f'<article class="tl-card" data-timeline-id="{esc(item["id"])}" '
            f'style="--tl-accent:{accent_hex}">'
            '<div class="tl-node-row">'
            '<span class="tl-beacon" aria-hidden="true"></span>'
            f'<span class="tl-period">{esc(item["period"])}</span>'
            "</div>"
            f'<h3 class="tl-org">{esc(item["organization"])}</h3>'
            f'<p class="tl-role">{esc(item["role"])}</p>'
            f'<p class="tl-summary">{esc(item["summary"])}</p>'
            f'<div class="tl-foot">{link_html}</div>'
            "</article>"
        )
    return "".join(out)


def render_stack_pillars() -> str:
    out: list[str] = []
    for pillar in TECH_PILLARS:
        accent_hex = PALETTE[pillar["accent"]]
        chips_html = "".join(
            f'<button type="button" class="skill-chip" data-skill="{esc(skill)}" '
            f'aria-pressed="false">{esc(skill)}</button>'
            for skill in pillar["items"]
        )
        out.append(
            f'<article class="pillar-card" data-pillar-id="{esc(pillar["id"])}" '
            f'style="--pillar-accent:{accent_hex}">'
            '<div class="pillar-head">'
            f'<span class="pillar-code">{esc(pillar["code"])}</span>'
            f'<h3 class="pillar-title">{esc(pillar["title"])}</h3>'
            "</div>"
            f'<div class="pillar-chips">{chips_html}</div>'
            "</article>"
        )
    return "".join(out)


def render_principles() -> str:
    return "".join(
        f'<li class="principle-item"><span class="p-idx">0{i + 1}</span><span>{esc(text)}</span></li>'
        for i, text in enumerate(PROFILE["principles"])
    )


def build_css() -> str:
    p = PALETTE
    return f"""
:root {{
  --bg-void: {p["bg_void"]};
  --bg-plate: {p["bg_plate"]};
  --bg-bay: {p["bg_bay"]};
  --bg-hover: {p["bg_hover"]};
  --border-grid: {p["border_grid"]};
  --border-active: {p["border_active"]};
  --ink-primary: {p["ink_primary"]};
  --ink-secondary: {p["ink_secondary"]};
  --ink-caption: {p["ink_caption"]};
  --accent-orange: {p["accent_orange"]};
  --accent-amber: {p["accent_amber"]};
  --accent-emerald: {p["accent_emerald"]};
  --accent-indigo: {p["accent_indigo"]};
  --font-mono: {FONTS["mono"]};
  --font-sans: {FONTS["sans"]};
  --radius-plate: 10px;
  --radius-bay: 6px;
  --radius-pill: 4px;
  --nav-h: 58px;
}}

*, *::before, *::after {{ box-sizing: border-box; }}

[hidden] {{ display: none !important; }}

html {{
  background: var(--bg-void);
  color: var(--ink-primary);
  font-family: var(--font-sans);
  font-size: 16px;
  scroll-padding-top: calc(var(--nav-h) + 20px);
  overflow-x: clip;
}}

body {{
  margin: 0;
  min-height: 100vh;
  background: var(--bg-void);
  color: var(--ink-primary);
  line-height: 1.55;
  overflow-x: clip;
  -webkit-font-smoothing: antialiased;
}}

body.atlas-overlay-open {{
  overflow: hidden;
}}

main, section, header, footer, article, aside, .atlas-shell, .hero-grid > *, .bento-grid > * {{
  min-width: 0;
}}

:focus-visible {{
  outline: 2px solid var(--accent-orange);
  outline-offset: 2px;
}}

.sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}}

/* Canvas2D Coordinate Field */
#atlas-field {{
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}}

/* Top Telemetry Command Bar */
.topbar {{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 40;
  min-height: var(--nav-h);
  background: rgba(8, 10, 15, 0.94);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-grid);
}}

.topbar-inner {{
  max-width: 1240px;
  margin: 0 auto;
  min-height: var(--nav-h);
  padding: 8px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}

.status-beacon {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent-emerald);
  white-space: nowrap;
}}

.beacon-dot {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
  animation: beaconPulse 2.4s ease-in-out infinite;
}}

.chapter-nav {{
  display: flex;
  align-items: center;
  gap: 2px;
  min-width: 0;
  flex: 1 1 auto;
  justify-content: center;
  overflow-x: auto;
  scrollbar-width: none;
}}
.chapter-nav::-webkit-scrollbar {{ display: none; }}

.nav-link {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 8px;
  border-radius: var(--radius-pill);
  border-bottom: 2px solid transparent;
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ink-secondary);
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: color 0.16s ease, background-color 0.16s ease, border-color 0.16s ease;
}}
.nav-link:hover {{
  color: var(--ink-primary);
  background: var(--bg-hover);
}}
.nav-link.is-active {{
  color: var(--accent-orange);
  border-bottom-color: var(--accent-orange);
}}

.topbar-utils {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}}

.coord-hud {{
  padding: 5px 10px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
  white-space: nowrap;
}}

.util-btn {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  min-height: 32px;
  border-radius: var(--radius-pill);
  background: var(--bg-plate);
  border: 1px solid var(--border-active);
  color: var(--ink-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}}
.util-btn:hover {{
  background: var(--bg-hover);
  border-color: var(--accent-amber);
}}
.util-btn[aria-pressed="true"] {{
  border-color: var(--accent-orange);
  color: var(--accent-orange);
  background: var(--bg-hover);
}}

.util-gh {{
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  min-height: 32px;
  border-radius: var(--radius-pill);
  background: var(--bg-hover);
  border: 1px solid var(--accent-orange);
  color: var(--accent-orange);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}}
.util-gh:hover {{
  background: var(--accent-orange);
  color: var(--bg-void);
}}

/* Main Atlas Shell */
.atlas-shell {{
  position: relative;
  z-index: 1;
  max-width: 1240px;
  margin: 0 auto;
  padding: calc(var(--nav-h) + 28px) 24px 72px;
  display: flex;
  flex-direction: column;
  gap: 56px;
}}

.chapter-section {{
  display: flex;
  flex-direction: column;
  gap: 20px;
}}

.section-header {{
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-grid);
}}

.section-eyebrow {{
  margin: 0 0 4px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.11em;
  color: var(--accent-orange);
  text-transform: uppercase;
}}

.section-title {{
  margin: 0;
  font-size: clamp(1.35rem, 2.2vw, 1.75rem);
  font-weight: 700;
  color: var(--ink-primary);
  letter-spacing: -0.015em;
}}

.section-meta {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--ink-caption);
}}

/* Hero Plate (01 // MONOGRAPH) */
.hero-plate {{
  position: relative;
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-left: 3px solid var(--accent-orange);
  border-radius: var(--radius-plate);
  padding: 26px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}}

.hero-plate::before, .hero-plate::after {{
  content: "";
  position: absolute;
  width: 12px;
  height: 12px;
  pointer-events: none;
  border-color: var(--border-active);
  border-style: solid;
}}
.hero-plate::before {{
  top: 8px;
  right: 8px;
  border-width: 1.5px 1.5px 0 0;
}}
.hero-plate::after {{
  bottom: 8px;
  right: 8px;
  border-width: 0 1.5px 1.5px 0;
}}

.hero-grid {{
  display: grid;
  grid-template-columns: minmax(0, 1.38fr) minmax(0, 0.92fr);
  gap: 24px;
  align-items: stretch;
}}

.hero-left {{
  display: flex;
  flex-direction: column;
  gap: 14px;
}}

.hero-eyebrow {{
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--accent-orange);
}}

.hero-wordmark-svg {{
  display: block;
  width: 100%;
  max-width: 580px;
  height: auto;
}}

.glyph-draw {{
  stroke-dasharray: 420;
  stroke-dashoffset: 420;
  animation: glyphDraw 0.95s ease-out var(--glyph-delay, 0ms) forwards;
}}

.hero-badges {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}

.meta-chip {{
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--ink-secondary);
}}
.meta-chip-amber {{
  color: var(--accent-amber);
  border-color: var(--border-active);
}}

.hero-lead {{
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink-primary);
}}

.hero-summary {{
  margin: 0;
  font-size: 0.94rem;
  color: var(--ink-secondary);
  max-width: 62ch;
}}

.hero-actions {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}}

.btn-primary {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 9px 18px;
  border-radius: var(--radius-pill);
  background: var(--accent-orange);
  color: var(--bg-void);
  border: 1px solid var(--accent-orange);
  font-family: var(--font-mono);
  font-size: 12.5px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: filter 0.15s ease, transform 0.15s ease;
}}
.btn-primary:hover {{
  filter: brightness(1.08);
}}

.btn-secondary {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 9px 16px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  color: var(--ink-primary);
  border: 1px solid var(--border-active);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}}
.btn-secondary:hover {{
  background: var(--bg-hover);
  border-color: var(--accent-orange);
}}

.btn-link-amber {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 40px;
  padding: 9px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-amber);
  text-decoration: none;
}}
.btn-link-amber:hover {{
  text-decoration: underline;
}}

/* Hero Right Topo Bay */
.topo-bay {{
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-bay);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
  overflow: hidden;
}}

.topo-head, .topo-foot {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}}

.topo-label {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
  letter-spacing: 0.06em;
}}

.topo-lock {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-emerald);
}}

.topo-svg-wrap {{
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 196px;
}}

.topo-svg {{
  width: 100%;
  max-height: 220px;
  height: auto;
  display: block;
}}

.topo-reticle-layer {{
  transform: translate(var(--rx, 0px), var(--ry, 0px));
  transition: transform 0.18s ease-out;
}}

.reticle-pulse {{
  transform-origin: 718px 164px;
  animation: reticleExpand 3.4s ease-out infinite;
}}

.topo-coords {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--accent-amber);
}}

/* Hero Bottom 4-Cell Strip */
.hero-strip {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}}

.strip-cell {{
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  border-left: 3px solid var(--cell-accent, var(--accent-orange));
  border-radius: var(--radius-bay);
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}}

.strip-eyebrow {{
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--cell-accent, var(--accent-amber));
}}

.strip-value {{
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-primary);
}}

/* Category Filter Bar (02 // DEPLOYED SYSTEMS) */
.filter-toolbar {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}

.filter-pills {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}

.filter-pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 14px;
  border-radius: var(--radius-pill);
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  color: var(--ink-secondary);
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}}
.filter-pill:hover {{
  background: var(--bg-hover);
  color: var(--ink-primary);
  border-color: var(--border-active);
}}
.filter-pill[aria-pressed="true"] {{
  background: var(--bg-hover);
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}}

.filter-status-wrap {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}}

.filter-status {{
  margin: 0;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--ink-secondary);
}}

.btn-reset {{
  padding: 5px 11px;
  min-height: 30px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--accent-amber);
  color: var(--accent-amber);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}}
.btn-reset:hover {{
  background: var(--bg-hover);
}}

/* Bento Project Grid */
.bento-grid {{
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}}

.bento-wide {{ grid-column: span 7; }}
.bento-medium {{ grid-column: span 5; }}
.bento-half {{ grid-column: span 6; }}

.bento-grid.is-filtered .bento-card:not([hidden]) {{
  grid-column: span 6;
}}

.bento-card {{
  position: relative;
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-top: 2px solid var(--card-accent, var(--accent-orange));
  border-radius: var(--radius-plate);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.18s ease, background-color 0.18s ease, box-shadow 0.18s ease;
}}

.bento-card::before {{
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: radial-gradient(280px circle at var(--mx, -400px) var(--my, -400px), rgba(0, 212, 255, 0.55), transparent 65%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.22s ease;
}}
.bento-card:hover::before, .bento-card:focus-within::before {{ opacity: 1; }}
.bento-card:hover {{
  background: var(--bg-hover);
  border-color: var(--border-active);
}}

.bento-card.is-skill-matched {{
  background: var(--bg-hover);
  border-color: var(--accent-orange);
  box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.5), 0 10px 26px rgba(0, 0, 0, 0.45);
}}

.bento-card.is-skill-dimmed {{
  background: var(--bg-bay);
  border-color: var(--border-grid);
}}

.card-top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}}

.card-meta {{
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}}

.card-code {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--card-accent, var(--accent-orange));
}}

.card-cat {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
}}

.status-pill {{
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--pill-color, var(--border-active));
  color: var(--pill-color, var(--ink-secondary));
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
}}

.diagram-bay {{
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-bay);
  padding: 6px;
}}

.micro-svg {{
  display: block;
  width: 100%;
  height: auto;
}}

.svg-mono {{
  font-family: var(--font-mono);
}}

.bus-pulse {{
  stroke-dasharray: 10 38;
  stroke-dashoffset: 0;
  animation: busFlow 2.8s linear infinite;
}}

.radar-sweep {{
  transform-origin: 38px 38px;
  animation: radarSpin 5.5s linear infinite;
}}

.pulse-dot {{
  animation: dotPulse 2.2s ease-in-out infinite;
}}

.card-copy {{
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.card-title {{
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--ink-primary);
}}

.card-tagline {{
  margin: 0;
  font-size: 14px;
  color: var(--ink-secondary);
}}

.card-stack {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}}

.stack-pill {{
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-secondary);
}}

.card-actions {{
  margin-top: auto;
  padding-top: 6px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}}

.btn-inspect {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-active);
  color: var(--ink-primary);
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease, background-color 0.15s ease;
}}
.btn-inspect:hover {{
  border-color: var(--accent-orange);
  color: var(--accent-orange);
  background: var(--bg-hover);
}}

.btn-card-ext {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--accent-amber);
  text-decoration: none;
  padding: 4px 6px;
}}
.btn-card-ext:hover {{
  text-decoration: underline;
}}

/* Supporting Repositories Subsection */
.supporting-block {{
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}}

.subhead-row {{
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}}

.subhead-title {{
  margin: 0;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ink-secondary);
}}

.supporting-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
  gap: 12px;
}}

.repo-card {{
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-bay);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}}
.repo-card.is-skill-matched {{
  background: var(--bg-hover);
  border-color: var(--accent-emerald);
  box-shadow: 0 0 0 1px rgba(52, 211, 153, 0.45);
}}
.repo-card.is-skill-dimmed {{
  background: var(--bg-bay);
}}

.repo-head {{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}}

.repo-title {{
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--ink-primary);
  overflow-wrap: anywhere;
}}

.repo-vis {{
  flex-shrink: 0;
  padding: 2px 6px;
  border-radius: var(--radius-pill);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
}}
.repo-vis-pub {{
  background: var(--bg-bay);
  border: 1px solid var(--accent-emerald);
  color: var(--accent-emerald);
}}
.repo-vis-priv {{
  background: var(--bg-bay);
  border: 1px solid var(--accent-amber);
  color: var(--accent-amber);
}}

.repo-summary {{
  margin: 0;
  font-size: 13.5px;
  color: var(--ink-secondary);
}}

.repo-stack {{
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}}

.mini-pill {{
  padding: 2px 7px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--ink-caption);
}}

.repo-foot {{
  margin-top: auto;
  padding-top: 4px;
}}

.repo-link {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--accent-amber);
  text-decoration: none;
}}
.repo-link:hover {{ text-decoration: underline; }}

.repo-private-note {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
}}

/* 03 // TRAJECTORY & LEADERSHIP */
.timeline-stage {{
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 14px;
}}

.timeline-rail-wrap {{
  width: 100%;
  height: 22px;
}}

.timeline-rail-svg {{
  display: block;
  width: 100%;
  height: 22px;
}}

.rail-progress {{
  transition: stroke-dashoffset 0.3s ease-out;
}}

.timeline-grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}}

.tl-card {{
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-top: 2px solid var(--tl-accent, var(--accent-amber));
  border-radius: var(--radius-bay);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 1;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}}
.tl-card.is-in-view, .tl-card.is-focused-milestone {{
  border-color: var(--tl-accent, var(--accent-amber));
  background: var(--bg-hover);
}}

.tl-node-row {{
  display: flex;
  align-items: center;
  gap: 8px;
}}

.tl-beacon {{
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--tl-accent, var(--accent-amber));
  flex-shrink: 0;
}}

.tl-period {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--tl-accent, var(--accent-amber));
}}

.tl-org {{
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--ink-primary);
}}

.tl-role {{
  margin: 0;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink-secondary);
}}

.tl-summary {{
  margin: 0;
  font-size: 13.5px;
  color: var(--ink-secondary);
}}

.tl-foot {{
  margin-top: auto;
  padding-top: 4px;
}}

.tl-link {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--accent-amber);
  text-decoration: none;
}}
.tl-link:hover {{ text-decoration: underline; }}

.tl-cat {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
}}

/* 04 // STACK MATRIX */
.matrix-toolbar {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}}

.stack-grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}}

.pillar-card {{
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-top: 2px solid var(--pillar-accent, var(--accent-orange));
  border-radius: var(--radius-plate);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}

.pillar-head {{
  display: flex;
  align-items: baseline;
  gap: 8px;
}}

.pillar-code {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--pillar-accent, var(--accent-orange));
}}

.pillar-title {{
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--ink-primary);
}}

.pillar-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}}

.skill-chip {{
  padding: 6px 10px;
  min-height: 32px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  color: var(--ink-secondary);
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.14s ease, border-color 0.14s ease, color 0.14s ease;
}}
.skill-chip:hover {{
  background: var(--bg-hover);
  border-color: var(--border-active);
  color: var(--ink-primary);
}}
.skill-chip[aria-pressed="true"] {{
  background: var(--accent-orange);
  border-color: var(--accent-orange);
  color: var(--bg-void);
  font-weight: 700;
}}

/* 05 // CHANNELS */
.channels-plate {{
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-plate);
  padding: 22px;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 20px;
}}

.principles-list {{
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}}

.principle-item {{
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 14px;
  color: var(--ink-secondary);
}}

.p-idx {{
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--accent-orange);
  flex-shrink: 0;
}}

.channel-cards {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}}

.channel-card {{
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-bay);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-decoration: none;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}}
.channel-card:hover {{
  background: var(--bg-hover);
  border-color: var(--accent-orange);
}}

.channel-label {{
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-amber);
}}

.channel-value {{
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-primary);
  word-break: break-word;
}}

.site-footer {{
  border-top: 1px solid var(--border-grid);
  padding-top: 18px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--ink-caption);
}}

/* Slide-Over Architecture Inspector Drawer */
.drawer-backdrop {{
  position: fixed;
  inset: 0;
  z-index: 55;
  background: rgba(8, 10, 15, 0.78);
  backdrop-filter: blur(4px);
}}

.drawer {{
  position: fixed;
  top: 0;
  right: 0;
  z-index: 60;
  width: min(100vw, 760px);
  height: 100vh;
  height: 100dvh;
  background: var(--bg-plate);
  border-left: 1px solid var(--border-active);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: -16px 0 48px rgba(0, 0, 0, 0.65);
}}

.drawer-header {{
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg-bay);
  border-bottom: 1px solid var(--border-grid);
  padding: 14px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}

.drawer-meta {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}}

.mono-badge, .cat-badge {{
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  background: var(--bg-plate);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-orange);
}}
.cat-badge {{
  color: var(--ink-secondary);
}}

.drawer-close {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  background: var(--bg-plate);
  border: 1px solid var(--border-active);
  color: var(--ink-primary);
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
}}
.drawer-close:hover {{
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}}

.drawer-close kbd, .cmd-footer kbd {{
  padding: 1px 5px;
  border-radius: 3px;
  background: var(--bg-void);
  border: 1px solid var(--border-active);
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--ink-secondary);
}}

.drawer-body {{
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 22px 22px 36px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}}

.drawer-body h2 {{
  margin: 0;
  font-size: 1.5rem;
  color: var(--ink-primary);
}}

.drawer-tagline {{
  margin: -12px 0 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--accent-amber);
}}

.drawer-summary {{
  margin: 0;
  font-size: 14.5px;
  color: var(--ink-secondary);
}}

.drawer-section {{
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid var(--border-grid);
}}

.drawer-section h3 {{
  margin: 0;
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent-orange);
}}

.drawer-section p {{
  margin: 0;
  font-size: 14px;
  color: var(--ink-secondary);
}}

.drawer-section ul {{
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}}

.drawer-section li {{
  font-size: 14px;
  color: var(--ink-secondary);
}}

.arch-header {{
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}}

.arch-hint {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
}}

.arch-stage {{
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  border-radius: var(--radius-bay);
  padding: 10px;
}}

.arch-svg {{
  display: block;
  width: 100%;
  height: auto;
}}

.arch-node {{
  cursor: pointer;
}}
.arch-node:focus-visible {{
  outline: none;
}}
.arch-node:focus-visible .arch-node-box {{
  stroke: var(--accent-orange);
  stroke-width: 2.4;
}}
.arch-node.is-selected .arch-node-box {{
  stroke: var(--accent-orange);
  stroke-width: 2.2;
  fill: var(--bg-hover);
}}

.arch-edge {{
  transition: opacity 0.15s ease, stroke 0.15s ease;
}}
.arch-edge.is-dimmed {{ opacity: 0.25; }}
.arch-edge.is-connected {{
  opacity: 1;
  stroke-width: 2.2;
}}

.node-readout {{
  background: var(--bg-bay);
  border: 1px solid var(--border-active);
  border-left: 3px solid var(--accent-orange);
  border-radius: var(--radius-bay);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}}

.node-readout-head {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-primary);
}}

.node-readout-meta {{
  font-size: 13.5px;
  color: var(--ink-secondary);
}}

.metric-chips {{
  list-style: none;
  padding: 0 !important;
  flex-direction: row !important;
  flex-wrap: wrap;
  gap: 8px !important;
}}

.metric-chips li {{
  padding: 5px 10px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--accent-emerald);
}}

.stack-chips, .drawer-links {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}

.drawer-link-btn {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-active);
  color: var(--accent-amber);
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
  text-decoration: none;
}}
.drawer-link-btn:hover {{
  border-color: var(--accent-orange);
  background: var(--bg-hover);
}}

/* Cmd+K Command Palette */
.cmd-backdrop {{
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(8, 10, 15, 0.8);
  backdrop-filter: blur(5px);
}}

.cmd-palette {{
  position: fixed;
  top: 72px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 75;
  width: min(640px, calc(100vw - 24px));
  max-height: min(520px, calc(100dvh - 96px));
  background: var(--bg-plate);
  border: 1px solid var(--border-active);
  border-radius: var(--radius-plate);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.72);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}

.cmd-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--bg-bay);
  border-bottom: 1px solid var(--border-grid);
}}

.cmd-prompt {{
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-orange);
}}

#cmd-input {{
  flex: 1 1 auto;
  min-width: 0;
  background: transparent;
  border: 0;
  color: var(--ink-primary);
  font-family: var(--font-mono);
  font-size: 14px;
  outline: none;
}}
#cmd-input::placeholder {{
  color: var(--ink-caption);
}}

.cmd-esc-btn {{
  padding: 4px 9px;
  border-radius: var(--radius-pill);
  background: var(--bg-plate);
  border: 1px solid var(--border-active);
  color: var(--ink-secondary);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}}

.cmd-results {{
  margin: 0;
  padding: 8px;
  list-style: none;
  overflow-y: auto;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}

.cmd-item {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-bay);
  border: 1px solid transparent;
  cursor: pointer;
}}
.cmd-item:hover, .cmd-item.is-selected {{
  background: var(--bg-hover);
  border-color: var(--accent-orange);
}}

.cmd-item-main {{
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}}

.cmd-item-title {{
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink-primary);
}}

.cmd-item-sub {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

.cmd-item-group {{
  flex-shrink: 0;
  padding: 2px 7px;
  border-radius: var(--radius-pill);
  background: var(--bg-bay);
  border: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--accent-amber);
}}

.cmd-empty {{
  padding: 20px 14px;
  text-align: center;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--ink-caption);
}}

.cmd-footer {{
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  padding: 9px 14px;
  background: var(--bg-bay);
  border-top: 1px solid var(--border-grid);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--ink-caption);
}}

/* Animations & Reduced Motion */
@keyframes beaconPulse {{
  0%, 100% {{ opacity: 1; transform: scale(1); }}
  50% {{ opacity: 0.45; transform: scale(0.85); }}
}}

@keyframes glyphDraw {{
  from {{ stroke-dashoffset: 420; }}
  to {{ stroke-dashoffset: 0; }}
}}

@keyframes reticleExpand {{
  0% {{ transform: scale(0.75); opacity: 0.85; }}
  100% {{ transform: scale(1.95); opacity: 0; }}
}}

@keyframes busFlow {{
  from {{ stroke-dashoffset: 0; }}
  to {{ stroke-dashoffset: -48; }}
}}

@keyframes radarSpin {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate(360deg); }}
}}

@keyframes dotPulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.35; }}
}}

html.motion-paused *, html.motion-paused *::before, html.motion-paused *::after,
body.motion-paused *, body.motion-paused *::before, body.motion-paused *::after {{
  animation-play-state: paused !important;
  transition-duration: 0.01ms !important;
}}

@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  .glyph-draw {{ stroke-dashoffset: 0; fill-opacity: 1; }}
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* Responsive Breakpoints: 1280x800, 768x1024, 390x844 */
@media (max-width: 1220px) {{
  .coord-hud {{ display: none; }}
}}

@media (max-width: 1120px) {{
  :root {{ --nav-h: 96px; }}
  .topbar-inner {{
    flex-wrap: wrap;
    padding: 8px 16px;
    gap: 6px;
  }}
  .chapter-nav {{
    order: 3;
    flex: 0 0 100%;
    width: 100%;
    justify-content: flex-start;
    padding-top: 4px;
    border-top: 1px solid var(--border-grid);
  }}
  .timeline-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .stack-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}

@media (max-width: 1023px) {{
  .hero-grid {{ grid-template-columns: 1fr; }}
  .hero-strip {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .bento-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .bento-wide {{ grid-column: 1 / -1; }}
  .bento-medium, .bento-half, .bento-grid.is-filtered .bento-card:not([hidden]) {{ grid-column: span 1; }}
  .channels-plate {{ grid-template-columns: 1fr; }}
}}

@media (max-width: 760px) {{
  .timeline-grid {{ grid-template-columns: 1fr; }}
  .timeline-rail-wrap {{ display: none; }}
}}

@media (max-width: 639px) {{
  :root {{ --nav-h: 98px; }}
  .topbar-inner {{
    padding: 8px 12px;
  }}
  .topbar-utils {{ gap: 5px; }}
  .util-btn, .util-gh {{ padding: 5px 8px; font-size: 10.5px; min-height: 30px; }}
  .atlas-shell {{
    padding: calc(var(--nav-h) + 18px) 14px 48px;
    gap: 40px;
  }}
  .hero-plate {{ padding: 16px; }}
  .hero-strip {{ grid-template-columns: 1fr; }}
  .bento-grid {{ grid-template-columns: 1fr; }}
  .bento-wide, .bento-medium, .bento-half, .bento-grid.is-filtered .bento-card:not([hidden]) {{
    grid-column: 1 / -1;
  }}
  .stack-grid {{ grid-template-columns: 1fr; }}
  .channel-cards {{ grid-template-columns: 1fr; }}
  .cmd-palette {{ top: 14px; width: calc(100vw - 20px); max-height: calc(100dvh - 28px); }}
  .drawer-body {{ padding: 16px 14px 28px; }}
}}
""".strip()


def build_js() -> str:
    return r"""
(() => {
  "use strict";

  const dataEl = document.getElementById("atlas-data");
  if (!dataEl) return;

  let ATLAS = null;
  try {
    ATLAS = JSON.parse(dataEl.textContent || "{}");
  } catch (err) {
    console.error("Failed to parse #atlas-data:", err);
    return;
  }

  const PALETTE = ATLAS.palette || {};
  const PROJECTS = Array.isArray(ATLAS.projects) ? ATLAS.projects : [];
  const REPOS = Array.isArray(ATLAS.supporting_repos) ? ATLAS.supporting_repos : [];
  const TIMELINE = Array.isArray(ATLAS.timeline) ? ATLAS.timeline : [];
  const PILLARS = Array.isArray(ATLAS.tech_pillars) ? ATLAS.tech_pillars : [];

  const projectsById = new Map(PROJECTS.map((p) => [p.id, p]));
  const reposById = new Map(REPOS.map((r) => [r.id, r]));

  const prefersReducedMotion =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const state = {
    activeCategory: "All",
    activeSkill: null,
    drawerProjectId: null,
    selectedNodeId: null,
    cmdOpen: false,
    cmdQuery: "",
    cmdActiveIndex: 0,
    gridVisible: true,
    motionPaused: prefersReducedMotion,
    activeSection: "monograph",
  };

  let lastFocusedEl = null;

  const SKILL_ALIASES = {
    "C#": { projects: ["inventra"], repos: ["benzin-istasyonu"] },
    "FastAPI": { projects: [], repos: ["fondedektifi"] },
    "TypeScript": { projects: ["inventra", "maritime-watch"], repos: ["dinamik-css-portfolyo"] },
    "Next.js": { projects: ["inventra"], repos: ["dinamik-css-portfolyo"] },
    "HTML5 / CSS3": { projects: ["maritime-watch"], repos: ["dinamik-css-portfolyo"] },
    "Vector SVG": { projects: ["maritime-watch"], repos: ["dinamik-css-portfolyo"] },
    "SQLite": { projects: [], repos: ["gelismis-kutuphane"] },
    "DuckDB": { projects: [], repos: ["fondedektifi"] },
    "Feature Engineering": { projects: ["ml-data-lab"], repos: [] },
    "GitHub Actions": { projects: ["maritime-watch"], repos: [] },
    "Linux / Bash": { projects: ["maritime-watch", "restofy"], repos: [] },
    "CI/CD": { projects: ["maritime-watch", "restofy"], repos: [] },
    "Edge Node (~1.2W)": { projects: ["maritime-watch"], repos: [] },
    "Cron Telemetry": { projects: ["maritime-watch"], repos: [] },
  };

  function matchesProjectSkill(project, skill) {
    const q = skill.trim().toLowerCase();
    if (Array.isArray(project.stack) && project.stack.some((s) => s.trim().toLowerCase() === q)) {
      return true;
    }
    const alias = SKILL_ALIASES[skill];
    return Boolean(alias && Array.isArray(alias.projects) && alias.projects.includes(project.id));
  }

  function matchesRepoSkill(repo, skill) {
    const q = skill.trim().toLowerCase();
    if (Array.isArray(repo.stack) && repo.stack.some((s) => s.trim().toLowerCase() === q)) {
      return true;
    }
    const alias = SKILL_ALIASES[skill];
    return Boolean(alias && Array.isArray(alias.repos) && alias.repos.includes(repo.id));
  }

  // DOM References
  const gridToggleBtn = document.getElementById("gridToggle");
  const motionToggleBtn = document.getElementById("motionToggle");
  const coordHud = document.getElementById("coord-hud");
  const systemsGrid = document.getElementById("systems-grid");
  const systemsStatus = document.getElementById("systems-filter-status");
  const matrixStatus = document.getElementById("matrix-filter-status");
  const resetButtons = Array.from(document.querySelectorAll('[data-action="reset-filters"]'));
  const filterPills = Array.from(document.querySelectorAll("[data-filter-category]"));
  const skillButtons = Array.from(document.querySelectorAll("[data-skill]"));
  const projectCards = Array.from(document.querySelectorAll("[data-project-id]"));
  const repoCards = Array.from(document.querySelectorAll("[data-repo-id]"));
  const navLinks = Array.from(document.querySelectorAll("[data-nav-sec]"));

  // Drawer DOM
  const drawer = document.getElementById("project-drawer");
  const drawerBackdrop = document.getElementById("drawer-backdrop");
  const drawerCloseBtn = document.getElementById("drawer-close");
  const drawerCode = document.getElementById("drawer-code");
  const drawerStatus = document.getElementById("drawer-status");
  const drawerCategory = document.getElementById("drawer-category");
  const drawerTitle = document.getElementById("drawer-title");
  const drawerTagline = document.getElementById("drawer-tagline");
  const drawerSummary = document.getElementById("drawer-summary");
  const drawerProblem = document.getElementById("drawer-problem");
  const drawerArchStage = document.getElementById("drawer-arch-stage");
  const drawerNodeReadout = document.getElementById("drawer-node-readout");
  const drawerTradeoffs = document.getElementById("drawer-tradeoffs");
  const drawerMetrics = document.getElementById("drawer-metrics");
  const drawerStack = document.getElementById("drawer-stack");
  const drawerLinks = document.getElementById("drawer-links");

  // Command Palette DOM
  const cmdPalette = document.getElementById("cmd-palette");
  const cmdBackdrop = document.getElementById("cmd-backdrop");
  const cmdInput = document.getElementById("cmd-input");
  const cmdCloseBtn = document.getElementById("cmd-close");
  const cmdResults = document.getElementById("cmd-results");
  const cmdStatus = document.getElementById("cmd-status");

  // -------------------------------------------------------------------------
  // 1. Canvas2D Coordinate Field Controller
  // -------------------------------------------------------------------------
  const canvas = document.getElementById("atlas-field");
  const ctx = canvas ? canvas.getContext("2d") : null;
  let pointerX = -999;
  let pointerY = -999;
  let targetX = -999;
  let targetY = -999;
  let rafId = 0;

  const NORMALIZED_CONTOURS = [
    [[0.62, 0.28], [0.71, 0.14], [0.83, 0.16], [0.92, 0.28], [0.88, 0.43], [0.72, 0.45], [0.60, 0.36]],
    [[0.65, 0.27], [0.72, 0.17], [0.81, 0.19], [0.88, 0.28], [0.84, 0.40], [0.72, 0.41], [0.64, 0.34]],
    [[0.68, 0.26], [0.74, 0.20], [0.80, 0.22], [0.85, 0.28], [0.81, 0.36], [0.73, 0.37], [0.67, 0.31]],
  ];
  const CONSTELLATION = [
    [0.14, 0.22], [0.28, 0.44], [0.46, 0.31], [0.64, 0.56], [0.79, 0.26], [0.88, 0.68],
  ];

  function resizeCanvas() {
    if (!canvas || !ctx) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = window.innerWidth;
    const h = window.innerHeight;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    renderCanvasFrame();
  }

  function renderCanvasFrame() {
    if (!canvas || !ctx) return;
    const w = window.innerWidth;
    const h = window.innerHeight;
    ctx.clearRect(0, 0, w, h);

    if (state.gridVisible) {
      ctx.strokeStyle = "rgba(30, 41, 59, 0.38)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= w; x += 24) {
        const px = Math.floor(x) + 0.5;
        ctx.moveTo(px, 0);
        ctx.lineTo(px, h);
      }
      for (let y = 0; y <= h; y += 24) {
        const py = Math.floor(y) + 0.5;
        ctx.moveTo(0, py);
        ctx.lineTo(w, py);
      }
      ctx.stroke();

      ctx.strokeStyle = "rgba(51, 65, 85, 0.36)";
      ctx.beginPath();
      for (let x = 0; x <= w; x += 96) {
        for (let y = 0; y <= h; y += 96) {
          ctx.moveTo(x - 4, y + 0.5);
          ctx.lineTo(x + 4, y + 0.5);
          ctx.moveTo(x + 0.5, y - 4);
          ctx.lineTo(x + 0.5, y + 4);
        }
      }
      ctx.stroke();
    }

    // Subtle topographic ridge contours & constellation chords
    ctx.save();
    ctx.strokeStyle = "rgba(51, 65, 85, 0.24)";
    ctx.lineWidth = 1;
    for (const poly of NORMALIZED_CONTOURS) {
      ctx.beginPath();
      poly.forEach((pt, idx) => {
        const x = pt[0] * w;
        const y = pt[1] * h;
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.stroke();
    }

    ctx.setLineDash([3, 5]);
    ctx.strokeStyle = "rgba(124, 142, 166, 0.16)";
    ctx.beginPath();
    CONSTELLATION.forEach((pt, idx) => {
      const x = pt[0] * w;
      const y = pt[1] * h;
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([]);

    for (const pt of CONSTELLATION) {
      ctx.fillStyle = "rgba(56, 189, 248, 0.32)";
      ctx.beginPath();
      ctx.arc(pt[0] * w, pt[1] * h, 2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    // Pointer reactive illumination
    if (pointerX >= 0 && pointerY >= 0) {
      const grad = ctx.createRadialGradient(pointerX, pointerY, 0, pointerX, pointerY, 220);
      grad.addColorStop(0, "rgba(0, 212, 255, 0.085)");
      grad.addColorStop(1, "rgba(0, 212, 255, 0)");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(pointerX, pointerY, 220, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = "rgba(0, 212, 255, 0.32)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.arc(pointerX, pointerY, 18, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }

  function tickCanvas() {
    rafId = 0;
    if (state.motionPaused) {
      renderCanvasFrame();
      return;
    }
    if (targetX >= 0 && targetY >= 0) {
      if (pointerX < 0) {
        pointerX = targetX;
        pointerY = targetY;
      } else {
        pointerX += (targetX - pointerX) * 0.16;
        pointerY += (targetY - pointerY) * 0.16;
      }
    }
    renderCanvasFrame();
    if (Math.abs(targetX - pointerX) > 0.4 || Math.abs(targetY - pointerY) > 0.4) {
      rafId = window.requestAnimationFrame(tickCanvas);
    }
  }

  function scheduleCanvasTick() {
    if (state.motionPaused) {
      renderCanvasFrame();
      return;
    }
    if (!rafId) {
      rafId = window.requestAnimationFrame(tickCanvas);
    }
  }

  window.addEventListener("resize", resizeCanvas);
  window.addEventListener("pointermove", (e) => {
    targetX = e.clientX;
    targetY = e.clientY;
    if (state.motionPaused) {
      pointerX = targetX;
      pointerY = targetY;
    }
    scheduleCanvasTick();

    if (coordHud) {
      const dx = (e.clientX - window.innerWidth / 2) * 0.0001;
      const dy = (window.innerHeight / 2 - e.clientY) * 0.0001;
      const lat = (41.0082 + dy).toFixed(4);
      const lon = (28.9784 + dx).toFixed(4);
      const px = String(Math.round(e.clientX)).padStart(4, "0");
      const py = String(Math.round(e.clientY)).padStart(4, "0");
      coordHud.textContent = `X:${px} Y:${py} // ${lat}°N ${lon}°E`;
    }
  }, { passive: true });

  // Hero topo bay parallax & Bento spotlight border
  const topoBay = document.getElementById("hero-topo-bay");
  if (topoBay) {
    topoBay.addEventListener("pointermove", (e) => {
      if (state.motionPaused) return;
      const r = topoBay.getBoundingClientRect();
      const nx = ((e.clientX - r.left) / Math.max(1, r.width) - 0.5) * 12;
      const ny = ((e.clientY - r.top) / Math.max(1, r.height) - 0.5) * 12;
      topoBay.style.setProperty("--rx", `${nx.toFixed(1)}px`);
      topoBay.style.setProperty("--ry", `${ny.toFixed(1)}px`);
    });
    topoBay.addEventListener("pointerleave", () => {
      topoBay.style.setProperty("--rx", "0px");
      topoBay.style.setProperty("--ry", "0px");
    });
  }

  if (systemsGrid) {
    systemsGrid.addEventListener("pointermove", (e) => {
      for (const card of projectCards) {
        if (card.hidden) continue;
        const r = card.getBoundingClientRect();
        card.style.setProperty("--mx", `${(e.clientX - r.left).toFixed(1)}px`);
        card.style.setProperty("--my", `${(e.clientY - r.top).toFixed(1)}px`);
      }
    }, { passive: true });
  }

  // -------------------------------------------------------------------------
  // 2. Motion & Grid Controls
  // -------------------------------------------------------------------------
  function applyMotionState() {
    document.documentElement.classList.toggle("motion-paused", state.motionPaused);
    document.body.classList.toggle("motion-paused", state.motionPaused);
    if (motionToggleBtn) {
      motionToggleBtn.setAttribute("aria-pressed", String(state.motionPaused));
      motionToggleBtn.textContent = state.motionPaused ? "Resume Motion" : "Pause Motion";
      motionToggleBtn.setAttribute(
        "aria-label",
        state.motionPaused ? "Resume background and SVG motion" : "Pause background and SVG motion"
      );
    }
    if (state.motionPaused && rafId) {
      window.cancelAnimationFrame(rafId);
      rafId = 0;
    }
    renderCanvasFrame();
  }

  function applyGridState() {
    document.documentElement.classList.toggle("grid-hidden", !state.gridVisible);
    if (gridToggleBtn) {
      gridToggleBtn.setAttribute("aria-pressed", String(state.gridVisible));
      gridToggleBtn.textContent = state.gridVisible ? "Grid: ON" : "Grid: OFF";
    }
    renderCanvasFrame();
  }

  function toggleGrid() {
    state.gridVisible = !state.gridVisible;
    applyGridState();
  }

  function toggleMotion() {
    state.motionPaused = !state.motionPaused;
    applyMotionState();
  }

  gridToggleBtn?.addEventListener("click", toggleGrid);
  motionToggleBtn?.addEventListener("click", toggleMotion);

  // -------------------------------------------------------------------------
  // 3. Category Filtering & Stack Matrix Cross-Highlighting
  // -------------------------------------------------------------------------
  function syncFilterUI() {
    const cat = state.activeCategory;
    const skill = state.activeSkill;
    const isFiltered = cat !== "All";
    if (systemsGrid) {
      systemsGrid.classList.toggle("is-filtered", isFiltered);
    }

    for (const pill of filterPills) {
      const pCat = pill.getAttribute("data-filter-category");
      pill.setAttribute("aria-pressed", String(pCat === cat));
    }

    for (const btn of skillButtons) {
      const bSkill = btn.getAttribute("data-skill");
      btn.setAttribute("aria-pressed", String(bSkill === skill));
    }

    let visibleCore = 0;
    let matchedCore = 0;
    for (const card of projectCards) {
      const pid = card.getAttribute("data-project-id");
      const project = projectsById.get(pid);
      if (!project) continue;
      const inCat = cat === "All" || project.category === cat;
      card.hidden = !inCat;
      if (inCat) visibleCore += 1;

      if (skill) {
        const hit = matchesProjectSkill(project, skill);
        card.classList.toggle("is-skill-matched", hit);
        card.classList.toggle("is-skill-dimmed", !hit);
        card.setAttribute("data-highlighted", hit ? "true" : "false");
        if (inCat && hit) matchedCore += 1;
      } else {
        card.classList.remove("is-skill-matched", "is-skill-dimmed");
        card.removeAttribute("data-highlighted");
      }
    }

    let matchedRepos = 0;
    const matchedRepoTitles = [];
    for (const rCard of repoCards) {
      const rid = rCard.getAttribute("data-repo-id");
      const repo = reposById.get(rid);
      if (!repo) continue;
      if (skill) {
        const hit = matchesRepoSkill(repo, skill);
        rCard.classList.toggle("is-skill-matched", hit);
        rCard.classList.toggle("is-skill-dimmed", !hit);
        rCard.setAttribute("data-highlighted", hit ? "true" : "false");
        if (hit) {
          matchedRepos += 1;
          matchedRepoTitles.push(repo.title);
        }
      } else {
        rCard.classList.remove("is-skill-matched", "is-skill-dimmed");
        rCard.removeAttribute("data-highlighted");
      }
    }

    if (systemsStatus) {
      if (skill) {
        const repoPart = matchedRepos > 0 ? ` · ${matchedRepos} supporting (${matchedRepoTitles.join(", ")})` : "";
        systemsStatus.textContent = `Skill "${skill}": ${matchedCore} of ${visibleCore} core systems matched${repoPart}`;
      } else if (cat === "All") {
        systemsStatus.textContent = `Showing ${visibleCore} of ${PROJECTS.length} core systems`;
      } else {
        systemsStatus.textContent = `Showing ${visibleCore} of ${PROJECTS.length} core systems in ${cat}`;
      }
    }

    if (matrixStatus) {
      if (skill) {
        const repoNote = matchedRepos > 0 ? ` · ${matchedRepos} supporting repo(s): ${matchedRepoTitles.join(", ")}` : "";
        matrixStatus.textContent = `Active skill "${skill}": ${matchedCore} core system(s) highlighted${repoNote}`;
      } else {
        matrixStatus.textContent = "Click any capability to highlight matching core systems & supporting repos";
      }
    }

    const showReset = cat !== "All" || skill !== null;
    for (const rBtn of resetButtons) {
      rBtn.hidden = !showReset;
    }
  }

  for (const pill of filterPills) {
    pill.addEventListener("click", () => {
      state.activeCategory = pill.getAttribute("data-filter-category") || "All";
      state.activeSkill = null;
      syncFilterUI();
    });
  }

  for (const btn of skillButtons) {
    btn.addEventListener("click", () => {
      const clicked = btn.getAttribute("data-skill");
      state.activeSkill = state.activeSkill === clicked ? null : clicked;
      if (state.activeSkill !== null) {
        state.activeCategory = "All";
      }
      syncFilterUI();
    });
  }

  for (const rBtn of resetButtons) {
    rBtn.addEventListener("click", () => {
      state.activeCategory = "All";
      state.activeSkill = null;
      syncFilterUI();
    });
  }

  // -------------------------------------------------------------------------
  // 4. Case-Study & Clickable SVG Architecture Inspector Drawer
  // -------------------------------------------------------------------------
  function wrapNodeLabel(label) {
    if (label.length <= 18) return [label];
    const words = label.split(/\s+/);
    const lines = [];
    let current = "";
    for (const w of words) {
      if ((current + " " + w).trim().length <= 18) {
        current = (current + " " + w).trim();
      } else {
        if (current) lines.push(current);
        current = w;
      }
    }
    if (current) lines.push(current);
    return lines.slice(0, 2);
  }

  function selectArchNode(project, nodeId) {
    if (!drawerArchStage || !drawerNodeReadout) return;
    state.selectedNodeId = nodeId;
    const nodes = Array.isArray(project.arch_nodes) ? project.arch_nodes : [];
    const edges = Array.isArray(project.arch_edges) ? project.arch_edges : [];
    const node = nodes.find((n) => n.id === nodeId) || nodes[0];
    if (!node) return;

    const nodeEls = drawerArchStage.querySelectorAll(".arch-node");
    nodeEls.forEach((el) => {
      const isSel = el.getAttribute("data-node-id") === node.id;
      el.classList.toggle("is-selected", isSel);
      el.setAttribute("aria-pressed", String(isSel));
    });

    const edgeEls = drawerArchStage.querySelectorAll(".arch-edge");
    edgeEls.forEach((el) => {
      const src = el.getAttribute("data-src");
      const dst = el.getAttribute("data-dst");
      const connected = src === node.id || dst === node.id;
      el.classList.toggle("is-connected", connected);
      el.classList.toggle("is-dimmed", !connected);
      const path = el.querySelector(".arch-edge-path");
      if (path) {
        path.setAttribute("marker-end", connected ? "url(#arch-arrow-active)" : "url(#arch-arrow)");
      }
    });

    const nodeMap = new Map(nodes.map((n) => [n.id, n.label]));
    const inbound = edges
      .filter(([, dst]) => dst === node.id)
      .map(([src, , lbl]) => `← ${nodeMap.get(src) || src} [${lbl}]`);
    const outbound = edges
      .filter(([src]) => src === node.id)
      .map(([, dst, lbl]) => `→ ${nodeMap.get(dst) || dst} [${lbl}]`);

    drawerNodeReadout.textContent = "";
    const head = document.createElement("div");
    head.className = "node-readout-head";
    head.textContent = `NODE: ${node.label} · ROLE: ${String(node.role || "").toUpperCase()} · TIER ${node.tier}`;
    const meta = document.createElement("div");
    meta.className = "node-readout-meta";
    const inText = inbound.length ? inbound.join(" | ") : "Ingress Source";
    const outText = outbound.length ? outbound.join(" | ") : "Terminal Sink";
    meta.textContent = `Inbound: ${inText}   //   Outbound: ${outText}`;
    drawerNodeReadout.appendChild(head);
    drawerNodeReadout.appendChild(meta);
  }

  function renderDrawerArchitectureSvg(project) {
    if (!drawerArchStage) return;
    drawerArchStage.textContent = "";
    const SVG_NS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("viewBox", "0 0 760 270");
    svg.setAttribute("class", "arch-svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", `Interactive system architecture diagram for ${project.title}`);

    const accentHex = PALETTE[project.accent] || PALETTE.accent_orange || "#FF5A1F";
    const defs = document.createElementNS(SVG_NS, "defs");

    function makeMarker(id, color) {
      const m = document.createElementNS(SVG_NS, "marker");
      m.setAttribute("id", id);
      m.setAttribute("viewBox", "0 0 10 10");
      m.setAttribute("refX", "8");
      m.setAttribute("refY", "5");
      m.setAttribute("markerWidth", "6");
      m.setAttribute("markerHeight", "6");
      m.setAttribute("orient", "auto-start-reverse");
      const p = document.createElementNS(SVG_NS, "path");
      p.setAttribute("d", "M 0 1.5 L 8 5 L 0 8.5 z");
      p.setAttribute("fill", color);
      m.appendChild(p);
      return m;
    }

    defs.appendChild(makeMarker("arch-arrow", PALETTE.ink_caption || "#7C8EA6"));
    defs.appendChild(makeMarker("arch-arrow-active", accentHex));
    svg.appendChild(defs);

    const TIER_X = { 0: 104, 1: 380, 2: 656 };
    const TIER_TITLES = [
      [104, "TIER 0 // INGRESS"],
      [380, "TIER 1 // PROCESSING"],
      [656, "TIER 2 // OUTPUT & STORE"],
    ];
    for (const [tx, title] of TIER_TITLES) {
      const lbl = document.createElementNS(SVG_NS, "text");
      lbl.setAttribute("x", String(tx));
      lbl.setAttribute("y", "22");
      lbl.setAttribute("text-anchor", "middle");
      lbl.setAttribute("fill", PALETTE.ink_caption || "#7C8EA6");
      lbl.setAttribute("font-family", "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace");
      lbl.setAttribute("font-size", "10");
      lbl.setAttribute("font-weight", "700");
      lbl.textContent = title;
      svg.appendChild(lbl);
    }

    const NODE_W = 168;
    const NODE_H = 58;
    const nodes = Array.isArray(project.arch_nodes) ? project.arch_nodes : [];
    const byTier = { 0: [], 1: [], 2: [] };
    for (const n of nodes) {
      const t = Math.max(0, Math.min(2, Number(n.tier) || 0));
      byTier[t].push(n);
    }

    const pos = new Map();
    for (const t of [0, 1, 2]) {
      const list = byTier[t];
      const cx = TIER_X[t];
      list.forEach((n, idx) => {
        let cy = 149;
        if (list.length === 2) {
          cy = idx === 0 ? 92 : 206;
        } else if (list.length >= 3) {
          cy = 46 + ((252 - 46) / (list.length + 1)) * (idx + 1);
        }
        pos.set(n.id, { x: cx, y: cy, tier: t, node: n });
      });
    }

    // Draw edges first
    const edgesGroup = document.createElementNS(SVG_NS, "g");
    const edges = Array.isArray(project.arch_edges) ? project.arch_edges : [];
    for (const [srcId, dstId, edgeLabel] of edges) {
      const s = pos.get(srcId);
      const d = pos.get(dstId);
      if (!s || !d) continue;

      const eg = document.createElementNS(SVG_NS, "g");
      eg.setAttribute("class", "arch-edge");
      eg.setAttribute("data-src", srcId);
      eg.setAttribute("data-dst", dstId);

      let pathD = "";
      let mx = (s.x + d.x) / 2;
      let my = (s.y + d.y) / 2;

      if (s.tier < d.tier) {
        const x1 = s.x + NODE_W / 2;
        const y1 = s.y;
        const x2 = d.x - NODE_W / 2 - 4;
        const y2 = d.y;
        const cx = (x1 + x2) / 2;
        pathD = `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`;
        mx = cx;
        my = (y1 + y2) / 2;
      } else if (s.tier === d.tier) {
        const down = d.y > s.y;
        const x1 = s.x;
        const y1 = s.y + (down ? NODE_H / 2 : -NODE_H / 2);
        const x2 = d.x;
        const y2 = d.y + (down ? -NODE_H / 2 - 4 : NODE_H / 2 + 4);
        pathD = `M ${x1} ${y1} L ${x2} ${y2}`;
        mx = s.x;
        my = (y1 + y2) / 2;
      } else {
        const yCtrl = Math.max(s.y, d.y) + 64;
        pathD = `M ${s.x} ${s.y + NODE_H / 2} C ${s.x} ${yCtrl}, ${d.x} ${yCtrl}, ${d.x} ${d.y + NODE_H / 2 + 4}`;
        mx = (s.x + d.x) / 2;
        my = yCtrl - 10;
      }

      const pathEl = document.createElementNS(SVG_NS, "path");
      pathEl.setAttribute("class", "arch-edge-path");
      pathEl.setAttribute("d", pathD);
      pathEl.setAttribute("fill", "none");
      pathEl.setAttribute("stroke", accentHex);
      pathEl.setAttribute("stroke-width", "1.6");
      pathEl.setAttribute("marker-end", "url(#arch-arrow)");
      eg.appendChild(pathEl);

      const pill = document.createElementNS(SVG_NS, "rect");
      pill.setAttribute("x", String(mx - 42));
      pill.setAttribute("y", String(my - 9));
      pill.setAttribute("width", "84");
      pill.setAttribute("height", "18");
      pill.setAttribute("rx", "4");
      pill.setAttribute("fill", PALETTE.bg_bay || "#0A0D14");
      pill.setAttribute("stroke", PALETTE.border_grid || "#1E293B");
      eg.appendChild(pill);

      const eTxt = document.createElementNS(SVG_NS, "text");
      eTxt.setAttribute("x", String(mx));
      eTxt.setAttribute("y", String(my + 3));
      eTxt.setAttribute("text-anchor", "middle");
      eTxt.setAttribute("fill", PALETTE.ink_secondary || "#94A3B8");
      eTxt.setAttribute("font-family", "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace");
      eTxt.setAttribute("font-size", "9.5");
      eTxt.textContent = edgeLabel;
      eg.appendChild(eTxt);

      edgesGroup.appendChild(eg);
    }
    svg.appendChild(edgesGroup);

    // Draw nodes
    const nodesGroup = document.createElementNS(SVG_NS, "g");
    for (const n of nodes) {
      const p = pos.get(n.id);
      if (!p) continue;
      const ng = document.createElementNS(SVG_NS, "g");
      ng.setAttribute("class", "arch-node");
      ng.setAttribute("role", "button");
      ng.setAttribute("tabindex", "0");
      ng.setAttribute("data-node", n.id);
      ng.setAttribute("data-node-id", n.id);
      ng.setAttribute("aria-pressed", "false");
      ng.setAttribute("aria-label", `Node ${n.label}, role ${n.role}, tier ${n.tier}`);

      const box = document.createElementNS(SVG_NS, "rect");
      box.setAttribute("class", "arch-node-box");
      box.setAttribute("x", String(p.x - NODE_W / 2));
      box.setAttribute("y", String(p.y - NODE_H / 2));
      box.setAttribute("width", String(NODE_W));
      box.setAttribute("height", String(NODE_H));
      box.setAttribute("rx", "8");
      box.setAttribute("fill", PALETTE.bg_plate || "#0F141D");
      box.setAttribute("stroke", PALETTE.border_active || "#334155");
      box.setAttribute("stroke-width", "1.4");
      ng.appendChild(box);

      const roleTxt = document.createElementNS(SVG_NS, "text");
      roleTxt.setAttribute("x", String(p.x));
      roleTxt.setAttribute("y", String(p.y - 11));
      roleTxt.setAttribute("text-anchor", "middle");
      roleTxt.setAttribute("fill", accentHex);
      roleTxt.setAttribute("font-family", "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace");
      roleTxt.setAttribute("font-size", "9.5");
      roleTxt.setAttribute("font-weight", "700");
      roleTxt.textContent = String(n.role || "").toUpperCase() + " ";
      ng.appendChild(roleTxt);

      const lines = wrapNodeLabel(String(n.label || ""));
      const titleTxt = document.createElementNS(SVG_NS, "text");
      titleTxt.setAttribute("x", String(p.x));
      titleTxt.setAttribute("y", String(lines.length > 1 ? p.y + 4 : p.y + 10));
      titleTxt.setAttribute("text-anchor", "middle");
      titleTxt.setAttribute("fill", PALETTE.ink_primary || "#F1F5F9");
      titleTxt.setAttribute("font-family", "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif");
      titleTxt.setAttribute("font-size", "12");
      titleTxt.setAttribute("font-weight", "600");
      lines.forEach((line, idx) => {
        const ts = document.createElementNS(SVG_NS, "tspan");
        ts.setAttribute("x", String(p.x));
        if (idx > 0) ts.setAttribute("dy", "14");
        ts.textContent = line;
        titleTxt.appendChild(ts);
      });
      ng.appendChild(titleTxt);

      ng.addEventListener("click", () => selectArchNode(project, n.id));
      ng.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectArchNode(project, n.id);
        }
      });

      nodesGroup.appendChild(ng);
    }
    svg.appendChild(nodesGroup);
    drawerArchStage.appendChild(svg);

    const defaultNode = nodes.find((n) => Number(n.tier) === 1) || nodes[0];
    if (defaultNode) {
      selectArchNode(project, defaultNode.id);
    }
  }

  function openDrawer(projectId, restoreEl) {
    const project = projectsById.get(projectId);
    if (!project || !drawer || !drawerBackdrop) return;

    if (state.cmdOpen) {
      closeCmd(false);
    }

    lastFocusedEl = restoreEl || document.activeElement;
    state.drawerProjectId = project.id;

    if (drawerCode) drawerCode.textContent = project.code;
    if (drawerStatus) {
      drawerStatus.textContent = project.status;
      drawerStatus.style.setProperty("--pill-color", PALETTE[project.accent] || PALETTE.accent_orange);
    }
    if (drawerCategory) drawerCategory.textContent = project.category;
    if (drawerTitle) drawerTitle.textContent = project.title;
    if (drawerTagline) drawerTagline.textContent = project.tagline;
    if (drawerSummary) drawerSummary.textContent = project.summary;
    if (drawerProblem) drawerProblem.textContent = project.problem;

    renderDrawerArchitectureSvg(project);

    if (drawerTradeoffs) {
      drawerTradeoffs.textContent = "";
      for (const item of project.tradeoffs || []) {
        const li = document.createElement("li");
        li.textContent = item;
        drawerTradeoffs.appendChild(li);
      }
    }

    if (drawerMetrics) {
      drawerMetrics.textContent = "";
      for (const m of project.metrics || []) {
        const li = document.createElement("li");
        li.textContent = m;
        drawerMetrics.appendChild(li);
      }
    }

    if (drawerStack) {
      drawerStack.textContent = "";
      for (const s of project.stack || []) {
        const span = document.createElement("span");
        span.className = "stack-pill";
        span.textContent = s;
        drawerStack.appendChild(span);
      }
    }

    if (drawerLinks) {
      drawerLinks.textContent = "";
      const candidates = [];
      if (project.url) candidates.push({ label: "Primary Deployment / Link ↗", url: project.url });
      if (project.repo_url && project.repo_url !== project.url) {
        candidates.push({ label: "GitHub Repository ↗", url: project.repo_url });
      }
      for (const sub of project.sub_repos || []) {
        if (sub && sub.url && !candidates.some((c) => c.url === sub.url)) {
          candidates.push({ label: `${sub.name} ↗`, url: sub.url });
        }
      }
      if (candidates.length === 0) {
        const note = document.createElement("span");
        note.className = "repo-private-note";
        note.textContent = "Source repository private / internal deployment.";
        drawerLinks.appendChild(note);
      } else {
        for (const c of candidates) {
          const a = document.createElement("a");
          a.className = "drawer-link-btn";
          a.href = c.url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          a.textContent = c.label;
          drawerLinks.appendChild(a);
        }
      }
    }

    drawerBackdrop.hidden = false;
    drawer.hidden = false;
    document.body.classList.add("atlas-overlay-open");
    drawerCloseBtn?.focus();
  }

  function closeDrawer(restoreFocus = true) {
    if (!drawer || !drawerBackdrop) return;
    state.drawerProjectId = null;
    state.selectedNodeId = null;
    drawer.hidden = true;
    drawerBackdrop.hidden = true;
    if (!state.cmdOpen) {
      document.body.classList.remove("atlas-overlay-open");
    }
    if (restoreFocus && lastFocusedEl && typeof lastFocusedEl.focus === "function") {
      lastFocusedEl.focus();
      lastFocusedEl = null;
    }
  }

  for (const card of projectCards) {
    const pid = card.getAttribute("data-project-id");
    const inspectBtn = card.querySelector("[data-inspect-project]");
    inspectBtn?.addEventListener("click", (e) => {
      e.stopPropagation();
      if (pid) openDrawer(pid, inspectBtn);
    });
    card.addEventListener("click", (e) => {
      if (e.target && e.target.closest("a, button")) return;
      if (pid) openDrawer(pid, inspectBtn || card);
    });
  }

  drawerCloseBtn?.addEventListener("click", () => closeDrawer(true));
  drawerBackdrop?.addEventListener("click", () => closeDrawer(true));

  // Focus trap inside Drawer
  drawer?.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    const focusables = Array.from(
      drawer.querySelectorAll('button, a[href], input, [tabindex]:not([tabindex="-1"])')
    ).filter((el) => !el.hasAttribute("disabled") && el.offsetParent !== null);
    if (focusables.length === 0) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  // -------------------------------------------------------------------------
  // 5. Cmd+K / Ctrl+K Command Palette
  // -------------------------------------------------------------------------
  function buildCommandCorpus() {
    const items = [];

    for (const p of PROJECTS) {
      items.push({
        id: `sys-${p.id}`,
        group: "SYSTEMS",
        title: `${p.code} · ${p.title}`,
        sub: `${p.category} · ${p.stack.join(", ")}`,
        keywords: `${p.code} ${p.title} ${p.tagline} ${p.category} ${p.stack.join(" ")} ${p.summary}`.toLowerCase(),
        run: () => {
          const trigger = document.querySelector(`[data-inspect-project="${p.id}"]`);
          openDrawer(p.id, trigger);
        },
      });
    }

    for (const r of REPOS) {
      items.push({
        id: `repo-${r.id}`,
        group: "REPOSITORIES",
        title: r.title,
        sub: `${r.visibility.toUpperCase()} · ${r.stack.join(", ")}`,
        keywords: `${r.title} ${r.visibility} ${r.stack.join(" ")} ${r.summary}`.toLowerCase(),
        run: () => {
          const el = document.querySelector(`[data-repo-id="${r.id}"]`);
          el?.scrollIntoView({ behavior: state.motionPaused ? "auto" : "smooth", block: "center" });
          if (r.url) {
            window.open(r.url, "_blank", "noopener,noreferrer");
          }
        },
      });
    }

    const seenSkills = new Set();
    for (const pillar of PILLARS) {
      items.push({
        id: `pillar-${pillar.id}`,
        group: "STACK MATRIX",
        title: `${pillar.code} · ${pillar.title}`,
        sub: pillar.items.join(" · "),
        keywords: `${pillar.title} ${pillar.items.join(" ")}`.toLowerCase(),
        run: () => {
          document.getElementById("stack")?.scrollIntoView({ behavior: state.motionPaused ? "auto" : "smooth" });
        },
      });
      for (const skill of pillar.items) {
        if (seenSkills.has(skill)) continue;
        seenSkills.add(skill);
        items.push({
          id: `skill-${skill}`,
          group: "STACK SKILL",
          title: skill,
          sub: `Filter systems by ${skill} (${pillar.title})`,
          keywords: `${skill} ${pillar.title} stack filter`.toLowerCase(),
          run: () => {
            state.activeSkill = skill;
            state.activeCategory = "All";
            syncFilterUI();
            document.getElementById("systems")?.scrollIntoView({ behavior: state.motionPaused ? "auto" : "smooth" });
          },
        });
      }
    }

    for (const tl of TIMELINE) {
      items.push({
        id: `tl-${tl.id}`,
        group: "TRAJECTORY",
        title: `${tl.organization} — ${tl.role}`,
        sub: `${tl.period} · ${tl.category}`,
        keywords: `${tl.organization} ${tl.role} ${tl.period} ${tl.summary}`.toLowerCase(),
        run: () => {
          const card = document.querySelector(`[data-timeline-id="${tl.id}"]`);
          card?.scrollIntoView({ behavior: state.motionPaused ? "auto" : "smooth", block: "center" });
          card?.classList.add("is-focused-milestone");
        },
      });
    }

    for (const [secId, label] of [
      ["monograph", "01 // Monograph & Coordinates"],
      ["systems", "02 // Deployed Systems & Supporting Repos"],
      ["trajectory", "03 // Trajectory & Community Leadership"],
      ["stack", "04 // Technical Stack Matrix"],
      ["channels", "05 // Channels & Engineering Principles"],
    ]) {
      items.push({
        id: `chap-${secId}`,
        group: "CHAPTERS",
        title: label,
        sub: `Jump to #${secId}`,
        keywords: `${label} ${secId} chapter section`.toLowerCase(),
        run: () => {
          document.getElementById(secId)?.scrollIntoView({ behavior: state.motionPaused ? "auto" : "smooth" });
        },
      });
    }

    items.push({
      id: "act-grid",
      group: "ACTIONS",
      title: "Toggle Grid",
      sub: "Show or hide Canvas2D architectural coordinate grid",
      keywords: "toggle grid blueprint coordinates canvas background".toLowerCase(),
      run: () => toggleGrid(),
    });

    items.push({
      id: "act-motion",
      group: "ACTIONS",
      title: state.motionPaused ? "Resume Motion" : "Pause Motion",
      sub: "Toggle Canvas2D & SVG motion / animations",
      keywords: "pause resume motion animation reduced".toLowerCase(),
      run: () => toggleMotion(),
    });

    return items;
  }

  function scoreQuery(item, query) {
    const q = query.trim().toLowerCase();
    if (!q) return 1;
    const titleL = item.title.toLowerCase();
    if (titleL === q) return 120;
    if (titleL.startsWith(q)) return 95;
    if (titleL.includes(q)) return 75;

    const tokens = q.split(/\s+/).filter(Boolean);
    if (tokens.every((t) => item.keywords.includes(t) || titleL.includes(t))) {
      return 55;
    }

    // Ordered character subsequence fallback on title only for >=3 chars
    if (q.length >= 3) {
      let qi = 0;
      for (let i = 0; i < titleL.length && qi < q.length; i += 1) {
        if (titleL[i] === q[qi]) qi += 1;
      }
      if (qi === q.length) return 25;
    }
    return 0;
  }

  let currentCmdMatches = [];

  function renderCmdResults() {
    if (!cmdResults || !cmdInput) return;
    const corpus = buildCommandCorpus();
    const q = state.cmdQuery;
    const scored = [];
    for (const item of corpus) {
      const sc = scoreQuery(item, q);
      if (sc > 0) scored.push({ item, sc });
    }
    scored.sort((a, b) => b.sc - a.sc);
    currentCmdMatches = scored.slice(0, 14).map((x) => x.item);

    if (state.cmdActiveIndex >= currentCmdMatches.length) {
      state.cmdActiveIndex = 0;
    }

    cmdResults.textContent = "";
    if (currentCmdMatches.length === 0) {
      const empty = document.createElement("li");
      empty.className = "cmd-empty";
      empty.textContent = `No matching system, skill, or action for "${q}"`;
      cmdResults.appendChild(empty);
      cmdInput.setAttribute("aria-activedescendant", "");
      if (cmdStatus) cmdStatus.textContent = "0 results";
      return;
    }

    currentCmdMatches.forEach((item, idx) => {
      const li = document.createElement("li");
      li.id = `cmd-opt-${idx}`;
      li.className = "cmd-item" + (idx === state.cmdActiveIndex ? " is-selected" : "");
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", String(idx === state.cmdActiveIndex));

      const main = document.createElement("div");
      main.className = "cmd-item-main";
      const t = document.createElement("span");
      t.className = "cmd-item-title";
      t.textContent = item.title;
      const s = document.createElement("span");
      s.className = "cmd-item-sub";
      s.textContent = item.sub;
      main.appendChild(t);
      main.appendChild(s);

      const grp = document.createElement("span");
      grp.className = "cmd-item-group";
      grp.textContent = item.group;

      li.appendChild(main);
      li.appendChild(grp);
      li.addEventListener("click", () => executeCmdItem(item));
      cmdResults.appendChild(li);
    });

    const activeOpt = document.getElementById(`cmd-opt-${state.cmdActiveIndex}`);
    cmdInput.setAttribute("aria-activedescendant", activeOpt ? activeOpt.id : "");
    if (cmdStatus) cmdStatus.textContent = `${currentCmdMatches.length} results available`;
  }

  function executeCmdItem(item) {
    if (!item) return;
    closeCmd(false);
    item.run();
  }

  function openCmd(restoreEl) {
    if (!cmdPalette || !cmdBackdrop || !cmdInput) return;
    if (state.drawerProjectId) {
      closeDrawer(false);
    }
    lastFocusedEl = restoreEl || document.activeElement;
    state.cmdOpen = true;
    state.cmdQuery = "";
    state.cmdActiveIndex = 0;
    cmdInput.value = "";
    cmdBackdrop.hidden = false;
    cmdPalette.hidden = false;
    document.body.classList.add("atlas-overlay-open");
    renderCmdResults();
    cmdInput.focus();
  }

  function closeCmd(restoreFocus = true) {
    if (!cmdPalette || !cmdBackdrop) return;
    state.cmdOpen = false;
    cmdPalette.hidden = true;
    cmdBackdrop.hidden = true;
    if (!state.drawerProjectId) {
      document.body.classList.remove("atlas-overlay-open");
    }
    if (restoreFocus && lastFocusedEl && typeof lastFocusedEl.focus === "function") {
      lastFocusedEl.focus();
      lastFocusedEl = null;
    }
  }

  for (const trigger of document.querySelectorAll('[data-action="open-cmd"]')) {
    trigger.addEventListener("click", () => openCmd(trigger));
  }
  cmdCloseBtn?.addEventListener("click", () => closeCmd(true));
  cmdBackdrop?.addEventListener("click", () => closeCmd(true));

  cmdInput?.addEventListener("input", () => {
    state.cmdQuery = cmdInput.value;
    state.cmdActiveIndex = 0;
    renderCmdResults();
  });

  cmdInput?.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (currentCmdMatches.length > 0) {
        state.cmdActiveIndex = (state.cmdActiveIndex + 1) % currentCmdMatches.length;
        renderCmdResults();
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (currentCmdMatches.length > 0) {
        state.cmdActiveIndex = (state.cmdActiveIndex - 1 + currentCmdMatches.length) % currentCmdMatches.length;
        renderCmdResults();
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (currentCmdMatches.length > 0) {
        executeCmdItem(currentCmdMatches[state.cmdActiveIndex]);
      }
    } else if (e.key === "Escape") {
      e.preventDefault();
      closeCmd(true);
    }
  });

  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (state.cmdOpen) closeCmd(true);
      else openCmd(document.activeElement);
    } else if (e.key === "Escape") {
      if (state.cmdOpen) {
        e.preventDefault();
        closeCmd(true);
      } else if (state.drawerProjectId) {
        e.preventDefault();
        closeDrawer(true);
      }
    }
  });

  // -------------------------------------------------------------------------
  // 6. Chapter Scroll-Spy & Timeline Choreography
  // -------------------------------------------------------------------------
  const railProgress = document.querySelector(".rail-progress");
  const tlCards = Array.from(document.querySelectorAll("[data-timeline-id]"));

  function updateRailProgress() {
    if (!railProgress) return;
    const totalLen = 960;
    if (state.motionPaused || prefersReducedMotion) {
      railProgress.setAttribute("stroke-dashoffset", "0");
      return;
    }
    const sec = document.getElementById("trajectory");
    if (!sec) return;
    const r = sec.getBoundingClientRect();
    const vh = window.innerHeight || 900;
    const raw = (vh - r.top) / (r.height + vh * 0.35);
    const ratio = Math.max(0.2, Math.min(1, raw));
    railProgress.setAttribute("stroke-dashoffset", String(Math.round(totalLen * (1 - ratio))));
  }

  if ("IntersectionObserver" in window) {
    const secObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            state.activeSection = entry.target.id;
            for (const link of navLinks) {
              link.classList.toggle("is-active", link.getAttribute("data-nav-sec") === state.activeSection);
            }
          }
        }
      },
      { rootMargin: "-30% 0px -55% 0px" }
    );
    for (const sec of document.querySelectorAll("main > section[id]")) {
      secObserver.observe(sec);
    }

    const tlObserver = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in-view");
          }
        }
      },
      { threshold: 0.25 }
    );
    for (const c of tlCards) {
      tlObserver.observe(c);
    }
  } else {
    for (const c of tlCards) c.classList.add("is-in-view");
  }

  window.addEventListener("scroll", () => {
    window.requestAnimationFrame(updateRailProgress);
  }, { passive: true });

  // Initialize
  applyMotionState();
  applyGridState();
  resizeCanvas();
  syncFilterUI();
  updateRailProgress();
})();
""".strip()


def build_html() -> str:
    atlas_payload = {
        "brand": BRAND,
        "categories": [
            "All",
            "Production Systems",
            "Backend & Microservices",
            "AI & Data Lab",
        ],
        "palette": PALETTE,
        "profile": PROFILE,
        "projects": PROJECTS,
        "supporting_repos": SUPPORTING_REPOS,
        "tech_pillars": TECH_PILLARS,
        "timeline": TIMELINE,
    }
    json_blob = safe_json_embed(atlas_payload)
    css = build_css()
    js = build_js()

    wordmark_svg = render_wordmark_svg()
    topo_svg = render_topo_bay_svg()
    hero_strip_html = render_hero_strip()
    project_cards_html = render_project_cards()
    supporting_html = render_supporting_repos()
    timeline_html = render_timeline_cards()
    stack_html = render_stack_pillars()
    principles_html = render_principles()

    links = PROFILE["links"]
    page_title = f"{PROFILE['name']} — {BRAND['monograph']}"
    meta_desc = PROFILE["summary"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="{esc(PALETTE['bg_void'])}" />
  <meta name="description" content="{esc(meta_desc)}" />
  <title>{esc(page_title)}</title>
  <style>
{css}
  </style>
</head>
<body>
  <canvas id="atlas-field" aria-hidden="true"></canvas>

  <header class="topbar">
    <div class="topbar-inner">
      <div class="status-beacon">
        <span class="beacon-dot" aria-hidden="true"></span>
        <span>GO // ISTANBUL</span>
      </div>

      <nav class="chapter-nav" aria-label="Primary chapters">
        <a class="nav-link is-active" href="#monograph" data-nav-sec="monograph">01 // MONOGRAPH</a>
        <a class="nav-link" href="#systems" data-nav-sec="systems">02 // SYSTEMS</a>
        <a class="nav-link" href="#trajectory" data-nav-sec="trajectory">03 // TRAJECTORY</a>
        <a class="nav-link" href="#stack" data-nav-sec="stack">04 // STACK</a>
        <a class="nav-link" href="#channels" data-nav-sec="channels">05 // CHANNELS</a>
      </nav>

      <div class="topbar-utils">
        <div id="coord-hud" class="coord-hud" aria-live="off">41.0082°N 28.9784°E</div>
        <button type="button" id="cmdkTrigger" class="util-btn" data-action="open-cmd" aria-keyshortcuts="Meta+K Control+K" aria-label="Open command palette">Cmd+K</button>
        <button type="button" id="gridToggle" class="util-btn" data-action="toggle-grid" aria-pressed="true" aria-label="Toggle coordinate grid">Grid: ON</button>
        <button type="button" id="motionToggle" class="util-btn" data-action="toggle-motion" aria-pressed="false" aria-label="Pause background and SVG motion">Pause Motion</button>
        <a class="util-gh" href="{esc(links['github'])}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>
      </div>
    </div>
  </header>

  <main class="atlas-shell">
    <!-- 01 // MONOGRAPH -->
    <section id="monograph" class="chapter-section" aria-labelledby="monograph-heading">
      <div class="hero-plate">
        <div class="hero-grid">
          <div class="hero-left">
            <div class="hero-eyebrow">01 // {esc(PROFILE['role_short'])} · {esc(PROFILE['location_upper'])}</div>
            <h1 id="monograph-heading" class="sr-only">{esc(PROFILE['name'])} — {esc(PROFILE['title'])}</h1>
            {wordmark_svg}
            <div class="hero-badges">
              <span class="meta-chip">{esc(BRAND['revision'])}</span>
              <span class="meta-chip">{esc(PROFILE['university'])} · {esc(PROFILE['degree'])} ({esc(PROFILE['graduation_years'])})</span>
              <span class="meta-chip meta-chip-amber">{esc(PROFILE['coordinates'])}</span>
            </div>
            <p class="hero-lead">{esc(PROFILE['lead'])}</p>
            <p class="hero-summary">{esc(PROFILE['summary'])}</p>
            <div class="hero-actions">
              <a class="btn-primary" href="#systems">Explore Deployed Systems</a>
              <button type="button" id="heroCmdk" class="btn-secondary" data-action="open-cmd">Command Palette (Cmd+K)</button>
              <a class="btn-link-amber" href="{esc(links['github'])}/{esc(PROFILE['handle'])}#readme" target="_blank" rel="noopener noreferrer">View GitHub README ↗</a>
            </div>
          </div>

          <div id="hero-topo-bay" class="topo-bay">
            <div class="topo-head">
              <span class="topo-label">{esc(BRAND['topo_label'])}</span>
              <span class="topo-lock">LOCK: ACTIVE</span>
            </div>
            <div class="topo-svg-wrap">
              {topo_svg}
            </div>
            <div class="topo-foot">
              <span class="topo-coords">{esc(PROFILE['coordinates_compact'])}</span>
              <span class="topo-label">{esc(BRAND['topo_datum'])}</span>
            </div>
          </div>
        </div>

        {hero_strip_html}
      </div>
    </section>

    <!-- 02 // DEPLOYED SYSTEMS -->
    <section id="systems" class="chapter-section" aria-labelledby="systems-heading">
      <div class="section-header">
        <div>
          <div class="section-eyebrow">02 // DEPLOYED SYSTEMS</div>
          <h2 id="systems-heading" class="section-title">Production Architecture &amp; Telemetry Fleet</h2>
        </div>
        <span class="section-meta">06 CORE SYSTEMS · 05 SUPPORTING REPOSITORIES</span>
      </div>

      <div class="filter-toolbar">
        <div class="filter-pills" role="group" aria-label="Filter systems by category">
          <button type="button" class="filter-pill" data-filter-category="All" aria-pressed="true">All (06)</button>
          <button type="button" class="filter-pill" data-filter-category="Production Systems" aria-pressed="false">Production Systems</button>
          <button type="button" class="filter-pill" data-filter-category="Backend &amp; Microservices" aria-pressed="false">Backend &amp; Microservices</button>
          <button type="button" class="filter-pill" data-filter-category="AI &amp; Data Lab" aria-pressed="false">AI &amp; Data Lab</button>
        </div>
        <div class="filter-status-wrap">
          <p id="systems-filter-status" class="filter-status" aria-live="polite">Showing 6 of 6 core systems</p>
          <button type="button" class="btn-reset" data-action="reset-filters" hidden>Reset Filter</button>
        </div>
      </div>

      <div id="systems-grid" class="bento-grid">
        {project_cards_html}
      </div>

      <div id="supporting-repos" class="supporting-block">
        <div class="subhead-row">
          <h3 class="subhead-title">SUPPORTING REPOSITORY INDEX</h3>
          <span class="section-meta">SPECIALIZED TOOLS, AUTOMATION &amp; FINANCIAL FORENSICS</span>
        </div>
        <div class="supporting-grid">
          {supporting_html}
        </div>
      </div>
    </section>

    <!-- 03 // TRAJECTORY & LEADERSHIP -->
    <section id="trajectory" class="chapter-section" aria-labelledby="trajectory-heading">
      <div class="section-header">
        <div>
          <div class="section-eyebrow">03 // TRAJECTORY &amp; LEADERSHIP</div>
          <h2 id="trajectory-heading" class="section-title">Academic, Community &amp; Engineering Milestones</h2>
        </div>
        <span class="section-meta">{esc(PROFILE['university'])} · GDG ON CAMPUS DOĞUŞ · HUAWEI × AI</span>
      </div>

      <div class="timeline-stage">
        <div class="timeline-rail-wrap" aria-hidden="true">
          <svg id="timeline-rail-svg" class="timeline-rail-svg" viewBox="0 0 1000 22" preserveAspectRatio="none">
            <line x1="20" y1="11" x2="980" y2="11" stroke="{esc(PALETTE['border_grid'])}" stroke-width="2"/>
            <line class="rail-progress" x1="20" y1="11" x2="980" y2="11" stroke="{esc(PALETTE['accent_amber'])}" stroke-width="2.4" stroke-dasharray="960" stroke-dashoffset="0"/>
            <circle cx="20" cy="11" r="4" fill="{esc(PALETTE['accent_amber'])}"/>
            <circle cx="260" cy="11" r="4" fill="{esc(PALETTE['accent_indigo'])}"/>
            <circle cx="500" cy="11" r="4" fill="{esc(PALETTE['accent_orange'])}"/>
            <circle cx="740" cy="11" r="4" fill="{esc(PALETTE['accent_emerald'])}"/>
            <circle cx="980" cy="11" r="4" fill="{esc(PALETTE['accent_amber'])}"/>
          </svg>
        </div>

        <div class="timeline-grid">
          {timeline_html}
        </div>
      </div>
    </section>

    <!-- 04 // STACK MATRIX -->
    <section id="stack" class="chapter-section" aria-labelledby="stack-heading">
      <div class="section-header">
        <div>
          <div class="section-eyebrow">04 // STACK MATRIX</div>
          <h2 id="stack-heading" class="section-title">4-Pillar Technical Capabilities</h2>
        </div>
        <span class="section-meta">INTERACTIVE CROSS-HIGHLIGHTING ACROSS SYSTEMS &amp; REPOS</span>
      </div>

      <div class="matrix-toolbar">
        <p id="matrix-filter-status" class="filter-status" aria-live="polite">Click any capability to highlight matching core systems &amp; supporting repos</p>
        <button type="button" class="btn-reset" data-action="reset-filters" hidden>Reset Filter</button>
      </div>

      <div class="stack-grid">
        {stack_html}
      </div>
    </section>

    <!-- 05 // CHANNELS -->
    <section id="channels" class="chapter-section" aria-labelledby="channels-heading">
      <div class="section-header">
        <div>
          <div class="section-eyebrow">05 // CHANNELS</div>
          <h2 id="channels-heading" class="section-title">Operating Principles &amp; Direct Links</h2>
        </div>
        <span class="section-meta">{esc(PROFILE['location'])} · {esc(PROFILE['coordinates'])}</span>
      </div>

      <div class="channels-plate">
        <div>
          <div class="section-eyebrow">ENGINEERING PRINCIPLES</div>
          <ul class="principles-list">
            {principles_html}
          </ul>
        </div>

        <div class="channel-cards">
          <a class="channel-card" href="{esc(links['github'])}" target="_blank" rel="noopener noreferrer">
            <span class="channel-label">GITHUB PROFILE</span>
            <span class="channel-value">github.com/{esc(PROFILE['handle'])} ↗</span>
          </a>
          <a class="channel-card" href="{esc(links['linkedin'])}" target="_blank" rel="noopener noreferrer">
            <span class="channel-label">LINKEDIN</span>
            <span class="channel-value">linkedin.com/in/kerem-kalyoncu ↗</span>
          </a>
          <a class="channel-card" href="{esc(links['site'])}" target="_blank" rel="noopener noreferrer">
            <span class="channel-label">COMPANION PORTAL</span>
            <span class="channel-value">keremkalyoncu.github.io/KeremKalyoncu ↗</span>
          </a>
          <button type="button" class="channel-card" data-action="open-cmd">
            <span class="channel-label">QUICK LAUNCH</span>
            <span class="channel-value">Open Command Palette (Cmd+K)</span>
          </button>
        </div>
      </div>

      <footer class="site-footer">
        <span>{esc(BRAND['monograph'])} · {esc(BRAND['revision'])}</span>
        <span>{esc(PROFILE['name'])} · {esc(PROFILE['location'])} · ZERO-CDN BUNDLE</span>
      </footer>
    </section>
  </main>

  <!-- Architecture Inspector Drawer -->
  <div id="drawer-backdrop" class="drawer-backdrop" hidden></div>
  <aside
    id="project-drawer"
    class="drawer"
    role="dialog"
    aria-modal="true"
    aria-labelledby="drawer-title"
    aria-describedby="drawer-summary"
    tabindex="-1"
    hidden
  >
    <div class="drawer-header">
      <div class="drawer-meta">
        <span id="drawer-code" class="mono-badge"></span>
        <span id="drawer-status" class="status-pill"></span>
        <span id="drawer-category" class="cat-badge"></span>
      </div>
      <button type="button" id="drawer-close" class="drawer-close" aria-label="Close architecture inspector">
        <span aria-hidden="true">✕</span> <kbd>ESC</kbd>
      </button>
    </div>

    <div class="drawer-body">
      <h2 id="drawer-title"></h2>
      <p id="drawer-tagline" class="drawer-tagline"></p>
      <p id="drawer-summary" class="drawer-summary"></p>

      <section class="drawer-section" aria-labelledby="drawer-prob-h">
        <h3 id="drawer-prob-h">01 // PROBLEM STATEMENT</h3>
        <p id="drawer-problem"></p>
      </section>

      <section class="drawer-section" aria-labelledby="drawer-arch-h">
        <div class="arch-header">
          <h3 id="drawer-arch-h">02 // INTERACTIVE SYSTEM ARCHITECTURE</h3>
          <span class="arch-hint">Click or Tab + Enter any node to inspect signals</span>
        </div>
        <div id="drawer-arch-stage" class="arch-stage"></div>
        <div id="drawer-node-readout" class="node-readout" aria-live="polite"></div>
      </section>

      <section class="drawer-section" aria-labelledby="drawer-trade-h">
        <h3 id="drawer-trade-h">03 // ENGINEERING TRADE-OFFS</h3>
        <ul id="drawer-tradeoffs"></ul>
      </section>

      <section class="drawer-section" aria-labelledby="drawer-metrics-h">
        <h3 id="drawer-metrics-h">04 // TELEMETRY &amp; METRICS</h3>
        <ul id="drawer-metrics" class="metric-chips"></ul>
      </section>

      <section class="drawer-section" aria-labelledby="drawer-links-h">
        <h3 id="drawer-links-h">05 // STACK &amp; CHANNELS</h3>
        <div id="drawer-stack" class="stack-chips"></div>
        <div id="drawer-links" class="drawer-links"></div>
      </section>
    </div>
  </aside>

  <!-- Cmd+K Command Palette -->
  <div id="cmd-backdrop" class="cmd-backdrop" hidden></div>
  <div
    id="cmd-palette"
    class="cmd-palette"
    role="dialog"
    aria-modal="true"
    aria-labelledby="cmd-title"
    hidden
  >
    <div class="cmd-header">
      <span id="cmd-title" class="sr-only">Command Palette</span>
      <span class="cmd-prompt" aria-hidden="true">&gt;_</span>
      <input
        id="cmd-input"
        type="search"
        role="combobox"
        aria-expanded="true"
        aria-controls="cmd-results"
        aria-autocomplete="list"
        aria-activedescendant=""
        autocomplete="off"
        spellcheck="false"
        placeholder="Search systems, stack, milestones, or actions..."
      />
      <button type="button" id="cmd-close" class="cmd-esc-btn" aria-label="Close command palette">ESC</button>
    </div>
    <ul id="cmd-results" class="cmd-results" role="listbox" aria-label="Command palette results"></ul>
    <div id="cmd-status" class="sr-only" aria-live="polite"></div>
    <div class="cmd-footer" aria-hidden="true">
      <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
      <span><kbd>↵</kbd> Execute</span>
      <span><kbd>ESC</kbd> Close</span>
    </div>
  </div>

  <script id="atlas-data" type="application/json">{json_blob}</script>
  <script>
{js}
  </script>
</body>
</html>
"""


def main() -> None:
    html_doc = build_html()
    out_path = REPO_ROOT / "index.html"
    out_path.write_text(html_doc, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
