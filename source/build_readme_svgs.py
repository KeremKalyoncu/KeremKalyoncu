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

    # Base canvas + micro-grid + subtle matte slate grain + border + corner brackets
    el(root, "rect", width=str(width), height=str(height), rx="12", fill=PALETTE["bg_void"])
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
    el(sheen, "stop", offset="0%", **{"stop-color": "#111824"})
    el(sheen, "stop", offset="100%", **{"stop-color": PALETTE["bg_plate"]})

    aura = el(defs, "radialGradient", id="beacon-aura", cx="50%", cy="50%", r="50%")
    el(aura, "stop", offset="0%", **{"stop-color": PALETTE["accent_orange"], "stop-opacity": "0.24"})
    el(aura, "stop", offset="65%", **{"stop-color": PALETTE["accent_orange"], "stop-opacity": "0.06"})
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
        fill=PALETTE["bg_plate"],
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
        "GO // ISTANBUL",
        x="46",
        y="32",
        fill=PALETTE["accent_emerald"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "0.8"},
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
    el(root, "rect", x="20", y="55", width="3", height="238", rx="1.5", fill=PALETTE["accent_orange"])

    el(
        root,
        "text",
        f"01 // {PROFILE['role_short']} · {PROFILE['location_upper']}",
        x="40",
        y="78",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )

    first_name, last_name = PROFILE["name"].split(" ", 1)
    render_vector_text(root, first_name, 40, 96, height=44.0, gap=14.0, fill=PALETTE["ink_primary"])
    el(root, "rect", x="250", y="106", width="36", height="3", fill=PALETTE["accent_orange"])
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

    # Hero Right Topo Bay
    el(
        root,
        "rect",
        x="574",
        y="54",
        width="286",
        height="240",
        rx="6",
        fill=PALETTE["bg_bay"],
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    topo_group = el(root, "g", **{"clip-path": "url(#topo-clip)"})
    el(topo_group, "rect", x="574", y="54", width="286", height="240", fill="url(#sub-dots)")

    # 7 nested terrestrial ridge elevation isolines (zero ocean waves)
    ridge_contours = [
        ("M582,196 C606,120 664,84 726,92 C792,100 842,138 854,194 C862,232 824,274 756,280 C686,286 566,252 582,196 Z", "#1E293B", "1.0"),
        ("M602,188 C622,130 670,102 722,108 C778,114 820,146 832,190 C840,222 806,256 750,262 C692,268 588,236 602,188 Z", "#233044", "1.0"),
        ("M624,180 C642,136 680,116 720,120 C764,126 798,150 808,186 C814,212 786,238 744,244 C698,250 612,218 624,180 Z", "#283548", "1.0"),
        ("M646,170 C660,140 688,128 718,132 C752,136 776,154 784,180 C790,200 768,220 736,226 C702,232 636,200 646,170 Z", "#2D3B50", "1.1"),
        ("M666,162 C676,144 696,138 716,142 C738,146 756,158 762,174 C766,188 748,202 728,206 C704,210 658,184 666,162 Z", "#334155", "1.1"),
        ("M682,156 C690,146 702,144 714,148 C726,152 736,160 738,170 C740,178 728,186 716,188 C702,190 676,170 682,156 Z", "#334155", "1.2"),
        ("M734,182 C742,172 758,170 768,176 C778,182 782,194 774,202 C766,210 748,210 738,202 C730,196 728,188 734,182 Z", "#283548", "0.9"),
    ]
    for path_d, stroke_hex, sw in ridge_contours:
        el(topo_group, "path", d=path_d, fill="none", stroke=stroke_hex, **{"stroke-width": sw})

    # Target Reticle at (718, 164)
    rx, ry = 718, 164
    el(topo_group, "circle", cx=str(rx), cy=str(ry), r="64", fill="url(#beacon-aura)")
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="22",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1", "stroke-opacity": "0.55"},
    )
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="46",
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1", "stroke-opacity": "0.8"},
    )
    el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="74",
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "0.9", "stroke-dasharray": "3 3", "stroke-opacity": "0.65"},
    )
    el(
        topo_group,
        "path",
        d=f"M610,{ry} H826 M{rx},76 V252",
        fill="none",
        stroke=PALETTE["border_active"],
        **{"stroke-width": "0.8", "stroke-opacity": "0.55"},
    )
    pulse_ring = el(
        topo_group,
        "circle",
        cx=str(rx),
        cy=str(ry),
        r="14",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1.2", "stroke-opacity": "0.85"},
    )
    el(pulse_ring, "animate", attributeName="r", values="14;36", dur="3.6s", repeatCount="indefinite")
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
        r="4",
        fill=PALETTE["accent_orange"],
        filter="url(#amber-glow)",
    )
    el(topo_group, "circle", cx=str(rx), cy=str(ry), r="1.8", fill=PALETTE["ink_primary"])

    # Topo callouts (placed clear of reticle crosshairs)
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
        "LOCK: ACTIVE",
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
    strip_ids = ["dogus-bsc", "gdg-dogus", "huawei-ai", "vollsign"]
    timeline_by_id = {t["id"]: t for t in TIMELINE}
    strip_labels = {
        "dogus-bsc": (
            f"DOĞUŞ UNIV. · {timeline_by_id['dogus-bsc']['period']}",
            "BSc Software Engineering",
        ),
        "gdg-dogus": (
            f"GDG DOĞUŞ · {timeline_by_id['gdg-dogus']['period']}",
            timeline_by_id["gdg-dogus"]["role"],
        ),
        "huawei-ai": (
            f"HUAWEI × AI · {timeline_by_id['huawei-ai']['period']}",
            "AI Academy · Data & ML",
        ),
        "vollsign": (
            "VOLLSIGN · PRODUCTION",
            "Dev / QA & Test Engineering",
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
            fill=PALETTE["bg_plate"],
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
    width, height = 880, 624
    title = (
        f"Obsidian Atlas Plate 02 — {len(PROJECTS)} Deployed Engineering Systems: "
        + ", ".join(p["title"] for p in PROJECTS)
    )
    root, _ = create_svg_root(width, height, title)

    # Header
    el(
        root,
        "text",
        "02 // DEPLOYED SYSTEMS & ARCHITECTURE MATRIX",
        x="20",
        y="31",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )
    el(
        root,
        "text",
        f"NODES: {len(PROJECTS):02d}  ·  BUS: ACTIVE  ·  TOPOLOGY: 2×3",
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
        ("M464,180 H450 V506 H416", PALETTE["accent_indigo"]),
        ("M440,142 V506", PALETTE["accent_orange"]),
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
            fill=PALETTE["bg_plate"],
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
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
            f"{proj['code']} // {proj['category'].upper()}",
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

    # Footer legend driven by SUPPORTING_REPOS & PROJECTS
    featured_supporting = [r["title"] for r in SUPPORTING_REPOS if r["id"] != "dinamik-css-portfolyo"]
    el(
        root,
        "text",
        "SUPPORTING REPOS: " + " · ".join(featured_supporting),
        x="20",
        y="608",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "9.5"},
    )
    el(
        root,
        "text",
        f"ALL {len(PROJECTS)} SYSTEMS DOCUMENTED",
        x="860",
        y="608",
        fill=PALETTE["accent_emerald"],
        **{"class": "mono", "font-size": "9.5", "font-weight": "700", "text-anchor": "end"},
    )

    return root


def build_trajectory_plate() -> ET.Element:
    width, height = 880, 400
    title = (
        f"Obsidian Atlas Plate 03 — {PROFILE['name']} Trajectory Rail, Community Leadership "
        f"({', '.join(t['organization'] for t in TIMELINE)}), and {len(TECH_PILLARS)}-Pillar Stack"
    )
    root, _ = create_svg_root(width, height, title)

    # Header
    el(
        root,
        "text",
        "03 // TRAJECTORY RAIL & ENGINEERING STACK MATRIX",
        x="20",
        y="31",
        fill=PALETTE["accent_orange"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "1.2"},
    )
    el(
        root,
        "text",
        f"CHRONOLOGY: {PROFILE['graduation_years'].replace('–', ' → ')}",
        x="860",
        y="31",
        fill=PALETTE["ink_caption"],
        **{"class": "mono", "font-size": "10", "text-anchor": "end", "letter-spacing": "0.5"},
    )
    el(root, "line", x1="20", y1="46", x2="860", y2="46", stroke=PALETTE["border_grid"], **{"stroke-width": "1"})

    # Band A — Trajectory Rail
    el(
        root,
        "rect",
        x="20",
        y="56",
        width="840",
        height="124",
        rx="6",
        fill=PALETTE["bg_bay"],
        stroke=PALETTE["border_grid"],
        **{"stroke-width": "1"},
    )
    el(root, "path", d="M56,82 H824", fill="none", stroke=PALETTE["border_active"], **{"stroke-width": "1.5"})
    el(
        root,
        "path",
        d="M56,82 H824",
        fill="none",
        stroke=PALETTE["accent_amber"],
        **{"class": "bus-pulse", "stroke-width": "1.8", "stroke-linecap": "round"},
    )

    for idx, milestone in enumerate(TIMELINE):
        card_x = 33 + idx * (158 + 6)
        cx = card_x + 79
        accent_hex = PALETTE[milestone["accent"]]

        el(
            root,
            "text",
            milestone["plate_period"],
            x=str(cx),
            y="71",
            fill=accent_hex,
            **{"class": "mono", "font-size": "9.5", "font-weight": "700", "text-anchor": "middle", "letter-spacing": "0.5"},
        )
        el(
            root,
            "line",
            x1=str(cx),
            y1="87.5",
            x2=str(cx),
            y2="96",
            stroke=PALETTE["border_active"],
            **{"stroke-width": "1.2"},
        )
        el(
            root,
            "circle",
            cx=str(cx),
            cy="82",
            r="5.5",
            fill=PALETTE["bg_plate"],
            stroke=accent_hex,
            **{"stroke-width": "1.6"},
        )
        el(root, "circle", cx=str(cx), cy="82", r="2.2", fill=accent_hex)

        el(
            root,
            "rect",
            x=str(card_x),
            y="96",
            width="158",
            height="74",
            rx="4",
            fill=PALETTE["bg_plate"],
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(root, "rect", x=str(card_x + 1), y="96", width="156", height="2", rx="1", fill=accent_hex)
        el(
            root,
            "text",
            milestone["plate_org"],
            x=str(card_x + 9),
            y="115",
            fill=PALETTE["ink_primary"],
            **{"class": "sans", "font-size": "10.5", "font-weight": "700"},
        )
        el(
            root,
            "text",
            milestone["plate_lines"][0],
            x=str(card_x + 9),
            y="134",
            fill=PALETTE["ink_secondary"],
            **{"class": "sans", "font-size": "10"},
        )
        el(
            root,
            "text",
            milestone["plate_lines"][1],
            x=str(card_x + 9),
            y="152",
            fill=PALETTE["ink_caption"],
            **{"class": "mono", "font-size": "9", "letter-spacing": "0.3"},
        )

    # Band B — 4-Pillar Tech Matrix
    for idx, pillar in enumerate(TECH_PILLARS):
        col_x = 20 + idx * (204 + 8)
        accent_hex = PALETTE[pillar["accent"]]
        el(
            root,
            "rect",
            x=str(col_x),
            y="192",
            width="204",
            height="146",
            rx="6",
            fill=PALETTE["bg_plate"],
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )
        el(root, "rect", x=str(col_x + 1), y="192", width="202", height="2.5", rx="1", fill=accent_hex)
        el(
            root,
            "text",
            f"{pillar['code']} // {pillar['title'].upper()}",
            x=str(col_x + 14),
            y="214",
            fill=accent_hex,
            **{"class": "mono", "font-size": "10", "font-weight": "700", "letter-spacing": "0.6"},
        )
        el(
            root,
            "line",
            x1=str(col_x + 12),
            y1="224",
            x2=str(col_x + 192),
            y2="224",
            stroke=PALETTE["border_grid"],
            **{"stroke-width": "1"},
        )

        for row_i, line_txt in enumerate(pillar["plate_lines"]):
            row_y = 244 + row_i * 22
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

    # Band C — Companion Portal Strip
    el(
        root,
        "rect",
        x="20",
        y="350",
        width="840",
        height="40",
        rx="6",
        fill=PALETTE["bg_plate"],
        stroke=PALETTE["border_active"],
        **{"stroke-width": "1"},
    )
    el(
        root,
        "circle",
        cx="36",
        cy="370",
        r="7",
        fill="none",
        stroke=PALETTE["accent_orange"],
        **{"stroke-width": "1", "stroke-opacity": "0.4"},
    )
    el(root, "circle", cx="36", cy="370", r="3.5", fill=PALETTE["accent_orange"])
    el(
        root,
        "text",
        "COMPANION INTERACTIVE PORTAL",
        x="50",
        y="374",
        fill=PALETTE["ink_primary"],
        **{"class": "mono", "font-size": "10.5", "font-weight": "700", "letter-spacing": "0.6"},
    )
    el(
        root,
        "text",
        "Architecture Inspector & Case Studies",
        x="276",
        y="374",
        fill=PALETTE["ink_secondary"],
        **{"class": "sans", "font-size": "11"},
    )
    el(
        root,
        "rect",
        x="598",
        y="357",
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
        y="374",
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
        "<details>",
        "  <summary><strong>ATS / Recruiter Specification — Plain-Text Index</strong></summary>",
        "",
        "### Profile",
        f"- **Name:** {PROFILE['name']} (`{PROFILE['handle']}`)",
        f"- **Role:** {PROFILE['title']}",
        f"- **Location:** {PROFILE['location']} (`{PROFILE['coordinates']}`)",
        f"- **Education:** {PROFILE['university']} — {PROFILE['degree']} (`{PROFILE['graduation_years']}`)",
        "",
        "### Experience & Community Leadership",
        *timeline_lines,
        "",
        "### Core Systems",
        *project_lines,
        "",
        "### Supporting Repositories",
        "- " + " · ".join(supporting_parts),
        "",
        "### Technical Stack",
        *pillar_lines,
        "",
        "### Channels",
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
