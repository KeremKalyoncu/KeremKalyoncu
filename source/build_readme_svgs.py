"""Pure-SVG Obsidian Atlas plate generator and README.md builder.

Run from repository root:
    python source/build_readme_svgs.py

Generates:
    - assets/atlas-hero.svg      (viewBox="0 0 880 356")
    - assets/atlas-systems.svg   (viewBox="0 0 880 624")
    - assets/atlas-trajectory.svg(viewBox="0 0 880 400")
    - README.md
"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SOURCE_DIR.parent
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import profile_spec as spec  # noqa: E402

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

PALETTE = spec.PALETTE
FONTS = spec.FONTS
BRAND = spec.BRAND
PROFILE = spec.PROFILE
PROJECTS = spec.PROJECTS
SUPPORTING_REPOS = spec.SUPPORTING_REPOS
TIMELINE = spec.TIMELINE
TECH_PILLARS = spec.TECH_PILLARS

# Closed-polygon chamfered vector lettering on 0..100 cap-height grid (fill-rule="evenodd").
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


def q(tag: str) -> str:
    return f"{{{SVG_NS}}}{tag}"


def el(parent: ET.Element | None, tag: str, text: str | None = None, **attrs: str) -> ET.Element:
    node = ET.Element(q(tag), attrs) if parent is None else ET.SubElement(parent, q(tag), attrs)
    if text is not None:
        node.text = text
    return node


def render_vector_text(
    parent: ET.Element,
    text: str,
    x: float,
    y: float,
    height: float = 44.0,
    gap: float = 14.0,
    fill: str = PALETTE["ink_primary"],
) -> float:
    scale = height / 100.0
    cursor = 0.0
    group = el(parent, "g", transform=f"translate({x:.2f},{y:.2f}) scale({scale:.4f})")
    for ch in text.upper():
        adv, d = GLYPHS[ch]
        if d:
            el(
                group,
                "path",
                d=d,
                transform=f"translate({cursor:.2f},0)",
                fill=fill,
                **{"fill-rule": "evenodd"},
            )
        cursor += adv + gap
    return max(0.0, (cursor - gap) * scale)


def create_svg_root(width: int, height: int, title: str) -> tuple[ET.Element, ET.Element]:
    root = el(
        None,
        "svg",
        viewBox=f"0 0 {width} {height}",
        width=str(width),
        height=str(height),
        role="img",
        **{"aria-label": title},
    )
    el(root, "title", title)
    defs = el(root, "defs")

    style_css = (
        f".mono {{ font-family: {FONTS['mono']}; }}\n"
        f".sans {{ font-family: {FONTS['sans']}; }}\n"
        "@keyframes busFlow { from { stroke-dashoffset: 0; } to { stroke-dashoffset: -48; } }\n"
        ".bus-pulse { stroke-dasharray: 10 38; stroke-dashoffset: 0; animation: busFlow 2.8s linear infinite; }"
    )
    el(defs, "style", style_css)

    pat_grid = el(defs, "pattern", id="micro-grid", width="24", height="24", patternUnits="userSpaceOnUse")
    el(
        pat_grid,
        "path",
        d="M 24 0 L 0 0 0 24",
        fill="none",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "0.6", "stroke-opacity": "0.55"},
    )

    flt_grain = el(defs, "filter", id="slate-grain", x="0%", y="0%", width="100%", height="100%")
    el(
        flt_grain,
        "feTurbulence",
        type="fractalNoise",
        baseFrequency="0.80",
        numOctaves="3",
        stitchTiles="stitch",
        result="noise",
    )
    el(
        flt_grain,
        "feColorMatrix",
        type="matrix",
        values="0 0 0 0 0.94  0 0 0 0 0.96  0 0 0 0 0.98  0 0 0 0.045 0",
        **{"in": "noise"},
    )

    flt_glow = el(defs, "filter", id="amber-glow", x="-80%", y="-80%", width="260%", height="260%")
    el(flt_glow, "feGaussianBlur", stdDeviation="4.5", result="blur")
    merge = el(flt_glow, "feMerge")
    el(merge, "feMergeNode", **{"in": "blur"})
    el(merge, "feMergeNode", **{"in": "SourceGraphic"})

    # Frutiger Aero ambient top-glow & glossy card surface gradients
    canvas_glow = el(defs, "radialGradient", id="aero-canvas-glow", cx="50%", cy="0%", r="75%")
    el(canvas_glow, "stop", offset="0%", **{"stop-color": "#00D4FF", "stop-opacity": "0.11"})
    el(canvas_glow, "stop", offset="55%", **{"stop-color": "#0EA5E9", "stop-opacity": "0.04"})
    el(canvas_glow, "stop", offset="100%", **{"stop-color": PALETTE["bg_void"], "stop-opacity": "0"})

    card_glass = el(defs, "linearGradient", id="aero-card-glass", x1="0%", y1="0%", x2="0%", y2="100%")
    el(card_glass, "stop", offset="0%", **{"stop-color": "#0F243C"})
    el(card_glass, "stop", offset="45%", **{"stop-color": PALETTE["bg_plate"]})
    el(card_glass, "stop", offset="100%", **{"stop-color": "#081423"})

    top_sheen = el(defs, "linearGradient", id="aero-top-sheen", x1="0%", y1="0%", x2="100%", y2="0%")
    el(top_sheen, "stop", offset="0%", **{"stop-color": "#F0FAFF", "stop-opacity": "0.05"})
    el(top_sheen, "stop", offset="35%", **{"stop-color": "#00D4FF", "stop-opacity": "0.45"})
    el(top_sheen, "stop", offset="70%", **{"stop-color": "#34D399", "stop-opacity": "0.35"})
    el(top_sheen, "stop", offset="100%", **{"stop-color": "#F0FAFF", "stop-opacity": "0.05"})

    # Base canvas + Aero ambient glow + micro-grid + subtle grain + border + corner brackets
    el(root, "rect", width=str(width), height=str(height), rx="12", fill=PALETTE["bg_void"])
    el(root, "rect", width=str(width), height=str(height), rx="12", fill="url(#aero-canvas-glow)")
    el(root, "rect", width=str(width), height=str(height), rx="12", fill="url(#micro-grid)")
    el(root, "rect", width=str(width), height=str(height), rx="12", filter="url(#slate-grain)")
    el(
        root,
        "rect",
        x="0.5",
        y="0.5",
        width=str(width - 1),
        height=str(height - 1),
        rx="11.5",
        fill="none",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    el(
        root,
        "line",
        x1="24",
        y1="1",
        x2=str(width - 24),
        y2="1",
        stroke="url(#aero-top-sheen)",
        **{"stroke-width": "1.2"},
    )

    brackets = (
        f"M10,18 V10 H18 "
        f"M{width - 18},10 H{width - 10} V18 "
        f"M10,{height - 18} V{height - 10} H18 "
        f"M{width - 18},{height - 10} H{width - 10} V{height - 18}"
    )
    el(
        root,
        "path",
        d=brackets,
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1.2"},
    )
    return root, defs


def build_hero_plate() -> ET.Element:
    width, height = 880, 356
    title = (
        f"Obsidian Atlas Plate 01 — {PROFILE['name']}, {PROFILE['role_short']} in "
        f"{PROFILE['location']} ({PROFILE['coordinates']}), {PROFILE['university']} {PROFILE['graduation_years']}"
    )
    root, defs = create_svg_root(width, height, title)

    sheen = el(defs, "linearGradient", id="plate-sheen", x1="0%", y1="0%", x2="100%", y2="100%")
    el(sheen, "stop", offset="0%", **{"stop-color": "#102842"})
    el(sheen, "stop", offset="55%", **{"stop-color": PALETTE["bg_plate"]})
    el(sheen, "stop", offset="100%", **{"stop-color": "#071525"})

    bosphorus_water = el(defs, "linearGradient", id="bosphorus-water", x1="0%", y1="0%", x2="100%", y2="100%")
    el(bosphorus_water, "stop", offset="0%", **{"stop-color": "#06233D"})
    el(bosphorus_water, "stop", offset="50%", **{"stop-color": "#093358"})
    el(bosphorus_water, "stop", offset="100%", **{"stop-color": "#051B30"})

    aura = el(defs, "radialGradient", id="beacon-aura", cx="50%", cy="50%", r="50%")
    el(aura, "stop", offset="0%", **{"stop-color": PALETTE["accent_orange"], "stop-opacity": "0.26"})
    el(aura, "stop", offset="65%", **{"stop-color": PALETTE["accent_emerald"], "stop-opacity": "0.08"})
    el(aura, "stop", offset="100%", **{"stop-color": PALETTE["accent_orange"], "stop-opacity": "0"})

    sub_dots = el(defs, "pattern", id="sub-dots", width="8", height="8", patternUnits="userSpaceOnUse")
    el(
        sub_dots,
        "circle",
        cx="1.5",
        cy="1.5",
        r="0.7",
        fill=PALETTE["border_active"],
        **{"fill-opacity": "0.35"},
    )

    topo_clip = el(defs, "clipPath", id="topo-clip")
    el(topo_clip, "rect", x="574", y="54", width="286", height="240", rx="6")

    # Top Telemetry Bar
    el(
        root,
        "rect",
        x="20",
        y="14",
        width="840",
        height="28",
        rx="4",
        fill="url(#aero-card-glass)",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    for div_x in (162, 412, 650):
        el(
            root,
            "line",
            x1=str(div_x),
            y1="19",
            x2=str(div_x),
            y2="37",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )

    dot = el(root, "circle", cx="34", cy="28", r="3.5", fill=PALETTE["accent_emerald"], opacity="1")
    el(
        dot,
        "animate",
        attributeName="opacity",
        values="1;0.35;1",
        dur="2.2s",
        repeatCount="indefinite",
    )
    el(
        root,
        "text",
        "ONLINE · ISTANBUL",
        x="46",
        y="32",
        fill=PALETTE["accent_emerald"],
        **{"class": "mono", "font-size": "10", "font-weight": "700", "letter-spacing": "0.6"},
    )
    el(
        root,
        "text",
        BRAND["plate_code"],
        x="174",
        y="32",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "10", "letter-spacing": "0.6"},
    )
    el(
        root,
        "text",
        PROFILE["coordinates_compact"],
        x="426",
        y="32",
        fill=PALETTE["accent_amber"],
        **{"class": "mono", "font-size": "10", "letter-spacing": "0.5"},
    )
    el(
        root,
        "text",
        PROFILE["degree_badge"],
        x="848",
        y="32",
        fill=PALETTE["ink_secondary"],
        **{"class": "mono", "font-size": "10", "text-anchor": "end", "letter-spacing": "0.4"},
    )

    # Hero Left Column
    el(
        root,
        "rect",
        x="20",
        y="54",
        width="542",
        height="240",
        rx="6",
        fill="url(#plate-sheen)",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    el(
        root,
        "line",
        x1="28",
        y1="54.8",
        x2="554",
        y2="54.8",
        stroke="url(#aero-top-sheen)",
        **{"stroke-width": "1"},
    )
    el(root, "rect", x="20", y="55", width="3", height="238", rx="1.5", fill=PALETTE["accent_orange"])

    el(
        root,
        "text",
        f"{PROFILE['role_short']}  ·  {PROFILE['location_upper']}",
        x="40",
        y="78",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )

    first_name, last_name = PROFILE["name"].split(" ", 1)
    render_vector_text(root, first_name, 40, 96, height=44.0, gap=14.0, fill=PALETTE["ink_primary"])
    el(root, "rect", x="250", y="106", width="36", height="3", fill=PALETTE["accent_emerald"])
    el(
        root,
        "text",
        BRAND["revision"],
        x="250",
        y="126",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "10", "letter-spacing": "0.6"},
    )
    render_vector_text(root, last_name, 40, 150, height=44.0, gap=14.0, fill=PALETTE["ink_primary"])

    el(
        root,
        "line",
        x1="40",
        y1="208",
        x2="542",
        y2="208",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    el(
        root,
        "text",
        PROFILE["lead"],
        x="40",
        y="229",
        fill=PALETTE["ink_primary"],
        **{"class": "sans", "font-size": "13.5", "font-weight": "700"},
    )
    el(
        root,
        "text",
        PROFILE["bio_lines"][0],
        x="40",
        y="250",
        fill=PALETTE["ink_secondary"],
        **{"class": "sans", "font-size": "12"},
    )
    el(
        root,
        "text",
        PROFILE["bio_lines"][1],
        x="40",
        y="268",
        fill=PALETTE["ink_secondary"],
        **{"class": "sans", "font-size": "12"},
    )
    el(
        root,
        "text",
        PROFILE["kpi_line"],
        x="40",
        y="285",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5", "letter-spacing": "0.6"},
    )

    # Hero Right Cartography Bay — Real Bosphorus Strait (İstanbul Boğazı)
    el(
        root,
        "rect",
        x="574",
        y="54",
        width="286",
        height="240",
        rx="6",
        fill="url(#bosphorus-water)",
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    topo_group = el(root, "g", **{"clip-path": "url(#topo-clip)"})
    el(topo_group, "rect", x="574", y="54", width="286", height="240", fill="url(#sub-dots)")

    # Authentic Bosphorus Strait Coastlines & Landmasses (Rumeli West & Anadolu East)
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
    el(
        topo_group,
        "path",
        d=rumeli_land,
        fill=PALETTE["bg_plate"],
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1.3", "stroke-linejoin": "round"},
    )
    el(
        topo_group,
        "path",
        d=anadolu_land,
        fill=PALETTE["bg_plate"],
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1.3", "stroke-linejoin": "round"},
    )

    # Topographic inland elevation isolines on Rumeli & Anadolu shores
    inland_contours = [
        ("M 574,72 L 696,72 C 686,90 664,106 656,124 C 650,140 668,154 662,174 C 654,192 634,196 574,186", "#163654", "0.9"),
        ("M 574,244 C 604,244 630,248 626,264 C 620,278 596,286 574,288", "#163654", "0.9"),
        ("M 860,82 L 778,82 C 760,102 746,124 744,150 C 742,176 752,196 736,222 C 728,236 746,258 788,284 L 860,284", "#163654", "0.9"),
        ("M 860,118 L 798,118 C 778,138 768,162 768,190 C 768,218 778,242 812,268 L 860,268", "#1E4970", "0.8"),
    ]
    for path_d, stroke_hex, sw in inland_contours:
        el(topo_group, "path", d=path_d, fill="none", stroke=stroke_hex, **{"stroke-width": sw})

    # Bosphorus 3 Suspension Bridges (YSS North, FSM Hisarlar Narrows, 15 Temmuz Ortaköy-Beylerbeyi)
    for bx1, by1, bx2, by2 in ((714, 68, 752, 68), (696, 151, 716, 153), (676, 198, 718, 202)):
        el(
            topo_group,
            "line",
            x1=str(bx1),
            y1=str(by1),
            x2=str(bx2),
            y2=str(by2),
            stroke=PALETTE["accent_amber"],
            **{"stroke-width": "1.2", "stroke-dasharray": "2 1.5", "stroke-opacity": "0.8"},
        )

    # Bosphorus Traffic Separation Scheme (TSS) Animated Shipping Channel
    tss_lane = "M 744,54 C 724,84 704,112 706,152 C 708,180 694,204 678,234 C 668,256 682,278 696,294"
    el(
        topo_group,
        "path",
        d=tss_lane,
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1.0", "stroke-dasharray": "3 3", "stroke-opacity": "0.75"},
    )
    el(
        topo_group,
        "path",
        d=tss_lane,
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"class": "bus-pulse", "stroke-width": "1.8", "stroke-linecap": "round"},
    )

    # Live AIS Vessel Nodes in the Strait
    for vx, vy, vcol in ((720, 96, PALETTE["accent_emerald"]), (680, 228, PALETTE["accent_amber"])):
        el(topo_group, "circle", cx=str(vx), cy=str(vy), r="2.3", fill=vcol)

    # Target Reticle at Bosphorus Narrows (706, 164)
    rx, ry = 706, 164
    el(topo_group, "circle", cx=str(rx), cy=str(ry), r="60", fill="url(#beacon-aura)")
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="20",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1", "stroke-opacity": "0.65"},
    )
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="42",
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "0.9", "stroke-dasharray": "3 3", "stroke-opacity": "0.75"},
    )
    el(
        topo_group,
        "path",
        d=f"M612,{ry} H800 M{rx},84 V244",
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "0.75", "stroke-opacity": "0.5"},
    )
    pulse_ring = el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="12",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1.2", "stroke-opacity": "0.85"},
    )
    el(pulse_ring, "animate", attributeName="r", values="12;34", dur="3.6s", repeatCount="indefinite")
    el(
        pulse_ring,
        "animate",
        attributeName="stroke-opacity",
        values="0.85;0",
        dur="3.6s",
        repeatCount="indefinite",
    )
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="3.8",
        fill=PALETTE["accent_orange"],
        filter="url(#amber-glow)",
    )
    el(topo_group, "circle", cx=str(rx), cy=str(ry), r="1.7", fill=PALETTE["ink_primary"])

    # Cartography callouts (placed clear of reticle crosshairs)
    el(
        root,
        "text",
        BRAND["topo_label"],
        x="588",
        y="74",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5", "letter-spacing": "0.5"},
    )
    el(
        root,
        "text",
        "AIS LIVE",
        x="846",
        y="74",
        fill=PALETTE["accent_emerald"],
        **{"class": "mono", "font-size": "9.5", "font-weight": "700", "text-anchor": "end"},
    )
    el(
        root,
        "text",
        PROFILE["lat"],
        x="588",
        y="262",
        fill=PALETTE["accent_amber"],
        **{"class": "mono", "font-size": "10", "font-weight": "700"},
    )
    el(
        root,
        "text",
        PROFILE["lon"],
        x="588",
        y="278",
        fill=PALETTE["accent_amber"],
        **{"class": "mono", "font-size": "10", "font-weight": "700"},
    )
    el(
        root,
        "text",
        BRAND["topo_datum"],
        x="846",
        y="278",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5", "text-anchor": "end"},
    )

    # Bottom 4-Cell Strip sourced from TIMELINE
    strip_ids = ["vollsign", "x-etc", "dogus-bsc", "gdg-dogus"]
    timeline_by_id = {t["id"]: t for t in TIMELINE}
    strip_labels = {
        "vollsign": (
            "VOLLSIGN · AUG 2026–PRESENT",
            "Software Engineer · Dev & QA",
        ),
        "x-etc": (
            "X-ETC. · FEB–AUG 2026 (7M)",
            "Full-Stack Software Engineer",
        ),
        "dogus-bsc": (
            "DOĞUŞ UNIV. · 2023–2027",
            "BSc Software Engineering",
        ),
        "gdg-dogus": (
            "GDG DOĞUŞ · 2025–2026",
            "Social Media & Design Lead",
        ),
    }

    for idx, tid in enumerate(strip_ids):
        item = timeline_by_id[tid]
        cell_x = 20 + idx * (204 + 8)
        accent_hex = PALETTE[item["accent"]]
        el(
            root,
            "rect",
            x=str(cell_x),
            y="304",
            width="204",
            height="40",
            rx="5",
            fill="url(#aero-card-glass)",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(root, "rect", x=str(cell_x), y="305", width="2.5", height="38", rx="1.2", fill=accent_hex)
        top_txt, sub_txt = strip_labels[tid]
        el(
            root,
            "text",
            top_txt,
            x=str(cell_x + 12),
            y="320",
            fill=accent_hex,
            **{"class": "mono", "font-size": "9", "font-weight": "700", "letter-spacing": "0.5"},
        )
        el(
            root,
            "text",
            sub_txt,
            x=str(cell_x + 12),
            y="336",
            fill=PALETTE["ink_primary"],
            **{"class": "sans", "font-size": "11", "font-weight": "600"},
        )

    return root


def draw_emblem(parent: ET.Element, project_id: str, ox: int, oy: int) -> None:
    """Render bespoke 76x76 vector emblem inside local coordinate space."""
    g = el(parent, "g", transform=f"translate({ox},{oy})")

    if project_id == "maritime-watch":
        # AIS Radar Sweep & Transponder (zero waves)
        el(
            g,
            "path",
            d="M38,8 V68 M8,38 H68",
            fill="none",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        for rad, col in ((10, PALETTE["border_grid"]), (20, PALETTE["border_active"]), (29, PALETTE["border_active"])):
            el(g, "circle", cx="38", cy="38", r=str(rad), fill="none", stroke=col, **{"stroke-width": "1"})
        sweep = el(g, "g")
        el(
            sweep,
            "path",
            d="M38,38 L38,9 A29,29 0 0,1 63,23 Z",
            fill=PALETTE["accent_orange"],
            **{"fill-opacity": "0.24"},
        )
        el(
            sweep,
            "line",
            x1="38",
            y1="38",
            x2="38",
            y2="9",
            stroke=PALETTE["accent_orange"],
            **{"stroke-width": "1.6"},
        )
        el(
            sweep,
            "animateTransform",
            attributeName="transform",
            type="rotate",
            **{"from": "0 38 38", "to": "360 38 38", "dur": "5.5s", "repeatCount": "indefinite"},
        )
        el(g, "circle", cx="52", cy="24", r="2.5", fill=PALETTE["accent_emerald"])
        el(g, "circle", cx="24", cy="49", r="2.2", fill=PALETTE["accent_amber"])
        el(g, "circle", cx="38", cy="38", r="2.8", fill=PALETTE["accent_orange"])

    elif project_id == "inventra":
        # Isometric SKU Wireframe Cube
        el(
            g,
            "polygon",
            points="38,11 62,25 62,51 38,65 14,51 14,25",
            fill=PALETTE["bg_plate"],
            stroke=PALETTE["border_active"],
            **{"stroke-width": "1.4"},
        )
        el(
            g,
            "path",
            d="M14,25 L38,38 L62,25 M38,38 V65",
            fill="none",
            stroke=PALETTE["accent_amber"],
            **{"stroke-width": "1.4"},
        )
        el(
            g,
            "polygon",
            points="38,24 49,30 49,44 38,50 27,44 27,30",
            fill="none",
            stroke=PALETTE["accent_orange"],
            **{"stroke-width": "1.2"},
        )
        for vx, vy in ((38, 11), (62, 25), (62, 51), (38, 65), (14, 51), (14, 25)):
            el(g, "circle", cx=str(vx), cy=str(vy), r="2", fill=PALETTE["ink_primary"])

    elif project_id == "restofy":
        # Modular Order-Dispatch Grid
        cells = [(11, 14), (31, 14), (51, 14), (11, 30), (31, 30), (51, 30)]
        for cx, cy in cells:
            if (cx, cy) == (31, 14):
                fill_c, stroke_c = PALETTE["accent_orange"], PALETTE["accent_orange"]
            elif (cx, cy) == (51, 30):
                fill_c, stroke_c = PALETTE["accent_emerald"], PALETTE["accent_emerald"]
            else:
                fill_c, stroke_c = PALETTE["bg_plate"], PALETTE["border_active"]
            el(
                g,
                "rect",
                x=str(cx),
                y=str(cy),
                width="14",
                height="10",
                rx="2",
                fill=fill_c,
                stroke=stroke_c,
                **{"stroke-width": "1.1"},
            )
        el(
            g,
            "path",
            d="M18,40 V46 H38 V51 M38,40 V51 M58,40 V46 H38",
            fill="none",
            stroke=PALETTE["border_active"],
            **{"stroke-width": "1.2"},
        )
        el(
            g,
            "rect",
            x="24",
            y="51",
            width="28",
            height="13",
            rx="2",
            fill=PALETTE["bg_hover"],
            stroke=PALETTE["accent_amber"],
            **{"stroke-width": "1.2"},
        )
        el(g, "circle", cx="38", cy="57.5", r="2.2", fill=PALETTE["accent_emerald"])

    elif project_id == "shifha":
        # Clinical ECG / Protocol Waveform
        el(
            g,
            "path",
            d="M8,24 H68 M8,38 H68 M8,52 H68 M20,10 V66 M38,10 V66 M56,10 V66",
            fill="none",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "0.7"},
        )
        el(
            g,
            "path",
            d="M8,41 H19 L23,35 L27,41 L31,46 L36,15 L41,59 L45,41 L52,33 L57,41 H68",
            fill="none",
            stroke=PALETTE["accent_orange"],
            **{"stroke-width": "2", "stroke-linecap": "round", "stroke-linejoin": "round"},
        )
        el(g, "circle", cx="36", cy="15", r="2.5", fill=PALETTE["ink_primary"])
        proto_dot = el(g, "circle", cx="52", cy="33", r="2.6", fill=PALETTE["accent_indigo"], opacity="1")
        el(
            proto_dot,
            "animate",
            attributeName="opacity",
            values="1;0.35;1",
            dur="2.4s",
            repeatCount="indefinite",
        )

    elif project_id == "kriptoparatakip":
        # Candlestick & Delta Sparkline
        el(
            g,
            "path",
            d="M10,60 H66 M10,14 V60",
            fill="none",
            stroke=PALETTE["border_active"],
            **{"stroke-width": "1"},
        )
        candles = [
            (18, 36, 54, 41, 10, PALETTE["accent_emerald"]),
            (28, 34, 52, 39, 9, PALETTE["accent_orange"]),
            (38, 22, 46, 28, 12, PALETTE["accent_emerald"]),
            (48, 26, 48, 31, 10, PALETTE["accent_orange"]),
            (58, 16, 38, 21, 12, PALETTE["accent_emerald"]),
        ]
        for cx, wy1, wy2, by, bh, col in candles:
            el(g, "line", x1=str(cx), y1=str(wy1), x2=str(cx), y2=str(wy2), stroke=col, **{"stroke-width": "1.2"})
            el(g, "rect", x=str(cx - 2.5), y=str(by), width="5", height=str(bh), rx="1", fill=col)
        el(
            g,
            "path",
            d="M14,48 L28,44 L38,30 L48,36 L62,19",
            fill="none",
            stroke=PALETTE["accent_amber"],
            **{"stroke-width": "1.6", "stroke-linecap": "round", "stroke-linejoin": "round"},
        )
        el(g, "circle", cx="62", cy="19", r="2.5", fill=PALETTE["accent_amber"])

    else:
        # ml-data-lab: 3-4-2 Neural Node Topology
        inp = [(15, 20), (15, 38), (15, 56)]
        hid = [(38, 14), (38, 30), (38, 46), (38, 62)]
        out = [(61, 28), (61, 48)]
        dominant = {
            ((15, 20), (38, 30)),
            ((15, 38), (38, 46)),
            ((38, 30), (61, 28)),
            ((38, 46), (61, 48)),
        }
        for p1 in inp:
            for p2 in hid:
                is_dom = (p1, p2) in dominant
                el(
                    g,
                    "line",
                    x1=str(p1[0]),
                    y1=str(p1[1]),
                    x2=str(p2[0]),
                    y2=str(p2[1]),
                    stroke=PALETTE["accent_indigo"] if is_dom else PALETTE["border_active"],
                    **{"stroke-width": "1.2" if is_dom else "0.8", "stroke-opacity": "0.95" if is_dom else "0.65"},
                )
        for p1 in hid:
            for p2 in out:
                is_dom = (p1, p2) in dominant
                el(
                    g,
                    "line",
                    x1=str(p1[0]),
                    y1=str(p1[1]),
                    x2=str(p2[0]),
                    y2=str(p2[1]),
                    stroke=PALETTE["accent_indigo"] if is_dom else PALETTE["border_active"],
                    **{"stroke-width": "1.2" if is_dom else "0.8", "stroke-opacity": "0.95" if is_dom else "0.65"},
                )
        for nx, ny in inp + hid:
            el(
                g,
                "circle",
                cx=str(nx),
                cy=str(ny),
                r="3.2",
                fill=PALETTE["bg_plate"],
                stroke=PALETTE["accent_indigo"],
                **{"stroke-width": "1.3"},
            )
        for nx, ny in out:
            el(
                g,
                "circle",
                cx=str(nx),
                cy=str(ny),
                r="3.4",
                fill=PALETTE["bg_plate"],
                stroke=PALETTE["accent_amber"],
                **{"stroke-width": "1.4"},
            )


def build_systems_plate() -> ET.Element:
    width, height = 880, 736
    title = (
        f"Obsidian Atlas Plate 02 — {len(PROJECTS)} Core Engineering Systems & Specialist Practices: "
        + ", ".join(p["title"] for p in PROJECTS)
    )
    root, _ = create_svg_root(width, height, title)

    # Header
    el(
        root,
        "text",
        "DEPLOYED SYSTEMS & ENGINEERING ARCHITECTURE",
        x="20",
        y="31",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )
    el(
        root,
        "text",
        f"{len(PROJECTS):02d} CORE SYSTEMS  ·  PRODUCTION & RESEARCH",
        x="860",
        y="31",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "10", "text-anchor": "end", "letter-spacing": "0.5"},
    )
    el(root, "line", x1="20", y1="46", x2="860", y2="46", stroke=PALETTE["border_grid"], **{"stroke-width": "1"})

    # Central Orthogonal Bus Channel (x=416..464, spine=440)
    bus = el(root, "g")
    el(bus, "path", d="M440,104 V540", fill="none", stroke=PALETTE["border_grid"], **{"stroke-width": "1.6"})
    for mid_y in (142, 324, 506):
        el(
            bus,
            "path",
            d=f"M416,{mid_y} H464",
            fill="none",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1.4"},
        )

    cross_routes = [
        ("M416,104 H430 V324 H464", PALETTE["accent_orange"]),
        ("M464,180 H450 V506 H416", PALETTE["accent_emerald"]),
        ("M440,142 V506", PALETTE["accent_amber"]),
    ]
    for route_d, pulse_col in cross_routes:
        el(bus, "path", d=route_d, fill="none", stroke=PALETTE["border_active"], **{"stroke-width": "1.2"})
        el(
            bus,
            "path",
            d=route_d,
            fill="none",
            stroke=pulse_col,
            **{"class": "bus-pulse", "stroke-width": "1.8", "stroke-linecap": "round"},
        )

    for port_x in (416, 464):
        for port_y in (104, 142, 180, 324, 506):
            el(
                bus,
                "circle",
                cx=str(port_x),
                cy=str(port_y),
                r="3",
                fill=PALETTE["bg_plate"],
                stroke=PALETTE["border_active"],
                **{"stroke-width": "1.2"},
            )

    # 2x3 Card Grid driven by PROJECTS
    card_positions = [
        (20, 60),
        (464, 60),
        (20, 242),
        (464, 242),
        (20, 424),
        (464, 424),
    ]

    for proj, (cx, cy) in zip(PROJECTS, card_positions):
        accent_hex = PALETTE[proj["accent"]]
        card = el(root, "g")
        el(
            card,
            "rect",
            x=str(cx),
            y=str(cy),
            width="396",
            height="164",
            rx="6",
            fill="url(#aero-card-glass)",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(
            card,
            "line",
            x1=str(cx + 8),
            y1=str(cy + 0.8),
            x2=str(cx + 388),
            y2=str(cy + 0.8),
            stroke="url(#aero-top-sheen)",
            **{"stroke-width": "0.9"},
        )
        el(
            card,
            "line",
            x1=str(cx),
            y1=str(cy + 32),
            x2=str(cx + 396),
            y2=str(cy + 32),
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(card, "circle", cx=str(cx + 14), cy=str(cy + 16), r="2.5", fill=accent_hex)
        el(
            card,
            "text",
            proj["category"].upper(),
            x=str(cx + 24),
            y=str(cy + 20),
            fill=accent_hex,
            **{"class": "mono", "font-size": "9.5", "font-weight": "700", "letter-spacing": "0.6"},
        )
        el(
            card,
            "text",
            proj["status"],
            x=str(cx + 382),
            y=str(cy + 20),
            fill=accent_hex,
            **{"class": "mono", "font-size": "9.5", "font-weight": "700", "text-anchor": "end", "letter-spacing": "0.6"},
        )

        # Emblem bay
        el(
            card,
            "rect",
            x=str(cx + 14),
            y=str(cy + 44),
            width="76",
            height="76",
            rx="4",
            fill=PALETTE["bg_bay"],
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        draw_emblem(card, proj["id"], cx + 14, cy + 44)

        # Text column
        el(
            card,
            "text",
            proj["title"],
            x=str(cx + 104),
            y=str(cy + 60),
            fill=PALETTE["ink_primary"],
            **{"class": "sans", "font-size": "14", "font-weight": "700"},
        )
        el(
            card,
            "text",
            proj["plate_desc_lines"][0],
            x=str(cx + 104),
            y=str(cy + 80),
            fill=PALETTE["ink_secondary"],
            **{"class": "sans", "font-size": "11.5"},
        )
        el(
            card,
            "text",
            proj["plate_desc_lines"][1],
            x=str(cx + 104),
            y=str(cy + 96),
            fill=PALETTE["ink_secondary"],
            **{"class": "sans", "font-size": "11.5"},
        )
        el(
            card,
            "text",
            proj["plate_metric"],
            x=str(cx + 104),
            y=str(cy + 116),
            fill=PALETTE["accent_amber"],
            **{"class": "mono", "font-size": "10", "font-weight": "600", "letter-spacing": "0.3"},
        )

        # Stack pills
        px = cx + 14
        py = cy + 132
        for pill in proj["plate_pills"]:
            pw = round(len(pill) * 6.0 + 16)
            el(
                card,
                "rect",
                x=str(px),
                y=str(py),
                width=str(pw),
                height="20",
                rx="3",
                fill=PALETTE["bg_bay"],
                stroke=PALETTE["border_grid"],
                **{"stroke-width": "1"},
            )
            el(
                card,
                "text",
                pill,
                x=str(px + pw / 2),
                y=str(py + 13.5),
                fill=PALETTE["ink_secondary"],
                **{"class": "mono", "font-size": "9.5", "text-anchor": "middle"},
            )
            px += pw + 6

    # Specialist Field Builds & Consulting Band (y=600..700)
    practices = getattr(spec, "SPECIALIST_PRACTICES", [])
    for idx, pr in enumerate(practices[:3]):
        bx = 20 + idx * (272 + 12)
        by = 600
        bw = 272
        bh = 94
        p_acc = PALETTE[pr["accent"]]
        p_card = el(root, "g")
        el(
            p_card,
            "rect",
            x=str(bx),
            y=str(by),
            width=str(bw),
            height=str(bh),
            rx="6",
            fill="url(#aero-card-glass)",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(p_card, "rect", x=str(bx + 1), y=str(by), width=str(bw - 2), height="2", rx="1", fill=p_acc)
        el(
            p_card,
            "text",
            pr["title"],
            x=str(bx + 14),
            y=str(by + 24),
            fill=PALETTE["ink_primary"],
            **{"class": "sans", "font-size": "12.5", "font-weight": "700"},
        )
        el(
            p_card,
            "text",
            pr["subtitle"],
            x=str(bx + 14),
            y=str(by + 44),
            fill=PALETTE["ink_secondary"],
            **{"class": "sans", "font-size": "11"},
        )
        el(
            p_card,
            "text",
            pr["metric"],
            x=str(bx + 14),
            y=str(by + 74),
            fill=p_acc,
            **{"class": "mono", "font-size": "9.5", "font-weight": "700", "letter-spacing": "0.4"},
        )

    # Footer legend driven by SUPPORTING_REPOS & PROJECTS
    featured_supporting = [r["title"] for r in SUPPORTING_REPOS if r["id"] not in ("dinamik-css-portfolyo", "cybersecurity-consulting")]
    el(
        root,
        "text",
        "REPOS & BUILDS: " + " · ".join(featured_supporting[:4]),
        x="20",
        y="718",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5"},
    )
    el(
        root,
        "text",
        f"ALL {len(PROJECTS)} CORE SYSTEMS + 3 PRACTICES",
        x="860",
        y="718",
        fill=PALETTE["accent_emerald"],
        **{"class": "mono", "font-size": "9.5", "font-weight": "700", "text-anchor": "end"},
    )

    return root


def build_trajectory_plate() -> ET.Element:
    width, height = 880, 516
    title = (
        f"Obsidian Atlas Plate 03 — {PROFILE['name']} Career Experience, Community Leadership "
        f"({', '.join(t['organization'] for t in TIMELINE)}), and {len(TECH_PILLARS)}-Pillar Stack"
    )
    root, _ = create_svg_root(width, height, title)

    # Header
    el(
        root,
        "text",
        "CAREER EXPERIENCE, EDUCATION & TECHNICAL STACK",
        x="20",
        y="31",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )
    el(
        root,
        "text",
        "VOLLSIGN · X-ETC · SHIFHA · ERYAZ · DOĞUŞ UNIV. (2023 → 2027)",
        x="860",
        y="31",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5", "text-anchor": "end", "letter-spacing": "0.4"},
    )
    el(root, "line", x1="20", y1="46", x2="860", y2="46", stroke=PALETTE["border_grid"], **{"stroke-width": "1"})

    # Band A — 2x4 Career, Community & Certifications Grid (All 8 LinkedIn Milestones)
    for idx, milestone in enumerate(TIMELINE[:8]):
        row = idx // 4
        col = idx % 4
        card_x = 20 + col * (204 + 8)
        card_y = 58 + row * (96 + 10)
        accent_hex = PALETTE[milestone["accent"]]

        el(
            root,
            "rect",
            x=str(card_x),
            y=str(card_y),
            width="204",
            height="96",
            rx="5",
            fill="url(#aero-card-glass)",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(root, "rect", x=str(card_x + 1), y=str(card_y), width="202", height="2.2", rx="1", fill=accent_hex)
        el(root, "circle", cx=str(card_x + 14), cy=str(card_y + 18), r="2.5", fill=accent_hex)
        el(
            root,
            "text",
            milestone["plate_period"],
            x=str(card_x + 24),
            y=str(card_y + 21),
            fill=accent_hex,
            **{"class": "mono", "font-size": "9", "font-weight": "700", "letter-spacing": "0.4"},
        )
        el(
            root,
            "text",
            milestone["plate_org"],
            x=str(card_x + 12),
            y=str(card_y + 44),
            fill=PALETTE["ink_primary"],
            **{"class": "sans", "font-size": "12", "font-weight": "700"},
        )
        el(
            root,
            "text",
            milestone["plate_lines"][0],
            x=str(card_x + 12),
            y=str(card_y + 64),
            fill=PALETTE["ink_secondary"],
            **{"class": "sans", "font-size": "10.5"},
        )
        el(
            root,
            "text",
            milestone["plate_lines"][1],
            x=str(card_x + 12),
            y=str(card_y + 82),
            fill=PALETTE["ink_caption"],
            **{"class": "mono", "font-size": "9", "letter-spacing": "0.3"},
        )

    # Band B — 4-Pillar Tech Matrix (y=276..422)
    for idx, pillar in enumerate(TECH_PILLARS):
        col_x = 20 + idx * (204 + 8)
        accent_hex = PALETTE[pillar["accent"]]
        el(
            root,
            "rect",
            x=str(col_x),
            y="276",
            width="204",
            height="146",
            rx="6",
            fill="url(#aero-card-glass)",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(root, "rect", x=str(col_x + 1), y="276", width="202", height="2.5", rx="1", fill=accent_hex)
        el(
            root,
            "text",
            pillar["title"].upper(),
            x=str(col_x + 14),
            y="298",
            fill=accent_hex,
            **{"class": "mono", "font-size": "10", "font-weight": "700", "letter-spacing": "0.6"},
        )
        el(
            root,
            "line",
            x1=str(col_x + 12),
            y1="308",
            x2=str(col_x + 192),
            y2="308",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )

        for row_i, line_txt in enumerate(pillar["plate_lines"]):
            row_y = 328 + row_i * 22
            el(root, "circle", cx=str(col_x + 15), cy=str(row_y - 3.5), r="2", fill=accent_hex)
            el(
                root,
                "text",
                line_txt,
                x=str(col_x + 26),
                y=str(row_y),
                fill=PALETTE["ink_secondary"],
                **{"class": "sans", "font-size": "11.5"},
            )

    # Band C — Direct Contact & Companion Portal Strip (y=436..496)
    el(
        root,
        "rect",
        x="20",
        y="436",
        width="840",
        height="60",
        rx="6",
        fill="url(#aero-card-glass)",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1"},
    )
    el(
        root,
        "circle",
        cx="38",
        cy="466",
        r="7",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1", "stroke-opacity": "0.4"},
    )
    el(root, "circle", cx="38", cy="466", r="3.5", fill=PALETTE["accent_orange"])
    el(
        root,
        "text",
        "DIRECT CONTACT & INTERACTIVE PORTAL",
        x="54",
        y="459",
        fill=PALETTE["ink_primary"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "0.6"},
    )
    el(
        root,
        "text",
        f"{PROFILE.get('email', 'keremkalyoncu.dev@gmail.com')}  ·  {PROFILE.get('email_secondary', 'gskerem200553@outlook.com')}",
        x="54",
        y="479",
        fill=PALETTE["ink_secondary"],
        **{"class": "mono", "font-size": "10"},
    )
    el(
        root,
        "rect",
        x="598",
        y="453",
        width="252",
        height="26",
        rx="4",
        fill=PALETTE["bg_hover"],
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1"},
    )
    site_label = PROFILE["links"]["site"].removeprefix("https://").rstrip("/")
    el(
        root,
        "text",
        site_label,
        x="724",
        y="470",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "9.2", "font-weight": "700", "text-anchor": "middle"},
    )

    return root


def serialize_svg(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def build_readme_markdown() -> str:
    links = PROFILE["links"]
    site_url = links["site"]
    github_url = links["github"]
    linkedin_url = links["linkedin"]
    site_display = site_url.removeprefix("https://").rstrip("/")
    github_display = github_url.removeprefix("https://")
    linkedin_display = linkedin_url.removeprefix("https://www.").rstrip("/")

    project_nav_items = [
        f'  <a href="{html.escape(p["url"], quote=True)}">{html.escape(p["title"].replace(" Türkiye", ""))}</a>'
        for p in PROJECTS
    ]
    project_nav_block = "\n  &nbsp;·&nbsp;\n".join(project_nav_items)

    timeline_lines = []
    for item in TIMELINE:
        org = item["organization"]
        if item.get("url"):
            domain_label = item["url"].removeprefix("https://").rstrip("/")
            org_md = f"**{org}** ([{domain_label}]({item['url']}))"
        else:
            org_md = f"**{org}**"
        timeline_lines.append(f"- {org_md} — {item['role']} (`{item['period']}`)")

    project_lines = []
    for idx, p in enumerate(PROJECTS, 1):
        extra = ""
        if p["sub_repos"] and p["id"] == "ml-data-lab":
            extras = [
                f"[{sr['name'].split(' ')[0]}]({sr['url']})"
                for sr in p["sub_repos"][1:]
            ]
            if extras:
                extra = f" ({', '.join(extras)})"
        stack_str = ", ".join(p["stack"])
        project_lines.append(
            f"{idx}. **[{p['title']}]({p['url']})** *({p['code']} · {p['category']})* — "
            f"{p['summary']}{extra} *Stack:* {stack_str}."
        )

    supporting_parts = []
    for r in SUPPORTING_REPOS:
        if r["url"]:
            supporting_parts.append(f"[{r['title']}]({r['url']})")
        else:
            supporting_parts.append(f"`{r['title']}` *(private)*")

    pillar_lines = [
        f"- **{pl['title']}:** {', '.join(pl['items'])}"
        for pl in TECH_PILLARS
    ]

    hero_alt = (
        f"Obsidian Atlas Plate 01 — {PROFILE['name']}, {PROFILE['role_short'].title()} in "
        f"{PROFILE['location']} ({PROFILE['coordinates']}), {PROFILE['university']} "
        f"{PROFILE['degree']} {PROFILE['graduation_years']}."
    )
    systems_alt = (
        "Obsidian Atlas Plate 02 — Core Engineering Systems: "
        + ", ".join(p["title"] for p in PROJECTS)
        + "."
    )
    trajectory_alt = (
        "Obsidian Atlas Plate 03 — Engineering Trajectory, Community Leadership "
        "(GDG on Campus Doğuş, Huawei AI Academy, BTK AI Fundamentals, VollSign), and 4-Pillar Technical Stack."
    )

    lines = [
        '<div align="center">',
        "",
        '<p align="center">',
        f'  <strong><a href="{html.escape(site_url, quote=True)}">Interactive Companion Site ↗</a></strong>',
        "  &nbsp;·&nbsp;",
        f'  <a href="{html.escape(github_url, quote=True)}">GitHub</a>',
        "  &nbsp;·&nbsp;",
        f'  <a href="{html.escape(linkedin_url, quote=True)}">LinkedIn</a>',
        "  &nbsp;·&nbsp;",
        f'  <a href="mailto:{html.escape(PROFILE.get("email", "keremkalyoncu.dev@gmail.com"), quote=True)}">keremkalyoncu.dev@gmail.com</a>',
        "</p>",
        "",
        '<p align="center">',
        f'  <a href="{html.escape(site_url, quote=True)}">',
        f'    <img src="assets/atlas-hero.svg" width="100%" alt="{html.escape(hero_alt, quote=True)}" />',
        "  </a>",
        "</p>",
        "",
        '<p align="center">',
        f'  <a href="{html.escape(github_url + "?tab=repositories", quote=True)}">',
        f'    <img src="assets/atlas-systems.svg" width="100%" alt="{html.escape(systems_alt, quote=True)}" />',
        "  </a>",
        "</p>",
        "",
        '<p align="center">',
        f'  <a href="{html.escape(linkedin_url, quote=True)}">',
        f'    <img src="assets/atlas-trajectory.svg" width="100%" alt="{html.escape(trajectory_alt, quote=True)}" />',
        "  </a>",
        "</p>",
        "",
        '<p align="center">',
        project_nav_block,
        "</p>",
        "",
        "</div>",
        "",
        "---",
        "",
        "## Engineering Focus & What I Build",
        "",
        "I'm **Kerem Kalyoncu** — a Software Engineer based in **İstanbul, Türkiye** (`Doğuş University · BSc Software Engineering, 2023–2027`) currently working as a **Software Engineer at [VollSign](https://vollsign.com)** in Beyoğlu Teknopark.",
        "",
        "- **Software Engineering & Systematic QA (@VollSign):** Developing production software while systematically testing UI workflows, API integrations, and end-to-end user journeys.",
        "- **Enterprise Full-Stack Systems (Inventra @X-ETC):** Engineered [Inventra](https://x-etc.online) end-to-end with **ASP.NET Core**, **React.js**, **Material UI**, and **PostgreSQL** for large-scale multi-warehouse inventory and workforce management.",
        "- **Applied Clinical AI (@Shifha):** Built AI-driven healthcare features in **Python** for an AI-powered doctor assistant supporting clinical triage and medical decision workflows.",
        "- **Independent Cybersecurity & Penetration Testing:** Building an independent security consulting practice — delivering security assessments, vulnerability analysis, and penetration testing for small and medium businesses.",
        "- **Real-World Field & Quant Engineering:** Created **[Maritime Watch Türkiye](https://keremkalyoncu.github.io/maritime-watch)** (24/7 Bosphorus AIS & weather safety engine running on a ~1.2W edge node), **Klima Gaz Defteri** (digital service & refrigerant tracking suite for my family's automotive AC business), and a **statistically rigorous cryptocurrency strategy backtesting platform**.",
        "- **Developer Community Leadership (@GDG On Campus Doğuş):** Coordinated the Social Media & Design team for over a year, scaling technical content and developer community engagement.",
        "",
        "---",
        "",
        "## Professional Experience & Leadership",
        "",
        "| Period | Organization | Role & Location | Focus & Impact |",
        "| :--- | :--- | :--- | :--- |",
        "| **Aug 2026 – Present** | **[VollSign](https://vollsign.com)** | Software Engineer · *Beyoğlu, İstanbul (Teknopark)* | Full-cycle software development, systematic UI/API functional testing & quality assurance. |",
        "| **Feb 2026 – Aug 2026** | **[X-ETC.](https://x-etc.online)** | Software Engineer (Full-Stack) · *Pendik, İstanbul* | End-to-end architecture & delivery of the **Inventra** enterprise inventory platform (`ASP.NET Core`, `React.js`). |",
        "| **Feb 2026 – Aug 2026** | **Shifha** | Software Engineer · *İstanbul* | Built Python AI-powered doctor assistant features & structured clinical NLP workflows. |",
        "| **Sep 2025 – Sep 2026** | **[GDG On Campus Doğuş](https://tr.linkedin.com/company/gdg-on-campus-dogus)** | Social Media Coordinator · *İstanbul* | Led the social media & design team (1 yr 1 mo), content production & campus developer outreach. |",
        "| **Aug 2024 – Sep 2024** | **Eryaz Bilgi Teknolojileri A.Ş.** | Software Developer · *İstanbul* | Enterprise software development using `C#`, `ASP.NET`, `JavaScript`, `HTML/CSS`, and `SQL`. |",
        "",
        "---",
        "",
        "## Core Systems, Field Builds & Security Practice",
        "",
        *project_lines,
        "7. **Klima Gaz Defteri** *(FIELD-01 · Production Field Tool)* — Custom digital service ledger, vehicle AC maintenance workflow, and refrigerant tracking tools engineered for my family's automotive air-conditioning service business.",
        "8. **Independent Cybersecurity & Penetration Testing** *(SEC-02 · Security Consulting)* — Security assessments, web/API vulnerability discovery, and penetration testing helping small businesses identify and remediate weak points in their systems.",
        "9. **FonDedektifi** *(FIN-03 · Financial Forensics)* — TEFAS funds & BIST equities forensic analytics platform built with `Python`, `FastAPI`, and `DuckDB` (DTL liquidity risk, HHI concentration & anomaly detection).",
        "",
        "---",
        "",
        "## Education, Certifications & Technical Stack",
        "",
        "- **Education:** **Doğuş Üniversitesi** — *BSc Software Engineering (Yazılım Mühendisliği)* (`2023 – 2027`)",
        "- **Certifications:**",
        "  - **Huawei Student Developers (HSD)** — *Veri Bilimi ve Makine Öğrenmesi (Data Science & Machine Learning)*",
        "  - **GDG On Campus** — *Core Team Certificate of Completion*",
        "  - **BTK Akademi** — *Yapay Zekaya Giriş (Introduction to AI)*",
        "",
        *pillar_lines,
        "",
        "---",
        "",
        "<details>",
        "  <summary><strong>Türkçe Özet / Bilingual Profile & Plain-Text ATS Index</strong></summary>",
        "",
        "### [TR] Hakkımda",
        "Merhaba, ben **Kerem** — İstanbul'da yaşayan bir yazılım mühendisliği öğrencisiyim (`Doğuş Üniversitesi, 2023–2027`). Şu anda **VollSign**'da (Beyoğlu Teknopark) **Yazılım Mühendisi** olarak çalışıyor, aynı zamanda QA/fonksiyonel test süreçlerinde (UI, API ve kullanıcı akışları) yer alıyorum.",
        "- **X-ETC (Inventra):** `ASP.NET Core` ve `React.js` ile büyük ölçekli kurumsal envanter yönetim sisteminde uçtan uca (full-stack) geliştirme.",
        "- **Shifha:** Yapay zekâ destekli doktor asistanı üzerinde `Python` ile klinik özellik geliştirme.",
        "- **Siber Güvenlik & Pentest:** Küçük işletmelere bağımsız güvenlik değerlendirmesi ve sızma testi (penetration testing) danışmanlığı.",
        "- **Özel Ürünler & Araştırma:** **Maritime Watch Türkiye** (Boğaz canlı AIS & hava karar motoru), **Klima Gaz Defteri** (ailemin otomotiv klima servisi için geliştirdiğim dijital operasyon araçları) ve **istatistiksel sağlamlık odaklı kripto para strateji backtest platformu**.",
        "",
        "### Profile & Experience Index",
        f"- **Name:** {PROFILE['name']} (`{PROFILE['handle']}`)",
        f"- **Role:** {PROFILE['title']}",
        f"- **Location:** {PROFILE['location']} (`{PROFILE['coordinates']}`)",
        f"- **Education:** {PROFILE['university']} — {PROFILE['degree']} (`{PROFILE['graduation_years']}`)",
        *timeline_lines,
        "",
        "### Supporting Repositories",
        "- " + " · ".join(supporting_parts),
        "",
        "### Direct Contact Channels",
        f"- **Email:** [keremkalyoncu.dev@gmail.com](mailto:keremkalyoncu.dev@gmail.com) · [gskerem200553@outlook.com](mailto:gskerem200553@outlook.com)",
        f"- **Interactive Companion Site:** [{site_display}]({site_url})",
        f"- **GitHub:** [{github_display}]({github_url})",
        f"- **LinkedIn:** [{linkedin_display}]({linkedin_url})",
        "",
        "</details>",
        "",
        '<p align="center">',
        f"  <sub>{BRAND['monograph']} · {PROFILE['name']} © 2026</sub>",
        "</p>",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    assets_dir = REPO_ROOT / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[tuple[Path, str]] = [
        (assets_dir / "atlas-hero.svg", serialize_svg(build_hero_plate())),
        (assets_dir / "atlas-systems.svg", serialize_svg(build_systems_plate())),
        (assets_dir / "atlas-trajectory.svg", serialize_svg(build_trajectory_plate())),
        (REPO_ROOT / "README.md", build_readme_markdown()),
    ]

    for path, content in outputs:
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)} ({len(content.encode('utf-8')):,} bytes)")


if __name__ == "__main__":
    main()
