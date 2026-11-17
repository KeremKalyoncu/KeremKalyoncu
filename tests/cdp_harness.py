"""Opaque-box Chromium CDP harness & static SVG/README validators for E2E tests.

Uses async ``choreographer.Browser`` (never ``BrowserSync``) inside a dedicated
background asyncio event loop thread, paired with an ephemeral local HTTP server,
``lxml.etree`` strict XML/CSP checks, and ``Pillow`` PNG verification.
"""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass, field
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from html import escape as html_escape
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from typing import Any
from urllib.parse import parse_qs, quote, urlparse, urlsplit

import choreographer
from lxml import etree
from PIL import Image, ImageStat

SVG_NS = "http://www.w3.org/2000/svg"

DISALLOWED_SVG_TAGS = frozenset(
    {
        "script",
        "foreignobject",
        "iframe",
        "object",
        "embed",
        "applet",
        "audio",
        "video",
        "canvas",
    }
)

URI_ATTR_LOCALNAMES = frozenset(
    {"href", "src", "poster", "data", "action", "formaction"}
)

OCEAN_THEME_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("KEREM.AERO", re.compile(r"\bkerem\.aero\b", re.IGNORECASE)),
    ("kerem-living-world", re.compile(r"kerem-living-world", re.IGNORECASE)),
    ("Frutiger Aero", re.compile(r"\bfrutiger\s*aero\b", re.IGNORECASE)),
    ("initOceanAudio", re.compile(r"\binitoceanaudio\b", re.IGNORECASE)),
    ("depth-indicator", re.compile(r"\bdepth-indicator\b", re.IGNORECASE)),
    ("Engineering Ocean", re.compile(r"\bengineering\s+ocean\b", re.IGNORECASE)),
    ("Open Water Portal", re.compile(r"\bopen\s+water\s+portal\b", re.IGNORECASE)),
    (
        "Living Engineering Ocean",
        re.compile(r"\bliving\s+engineering\s+ocean\b", re.IGNORECASE),
    ),
    ("bubble-layer", re.compile(r"\bbubble-layer\b", re.IGNORECASE)),
    ("sonar-ping", re.compile(r"\bsonar-ping\b", re.IGNORECASE)),
    ("abyssal", re.compile(r"\babyssal\b", re.IGNORECASE)),
    ("ocean-emoji", re.compile(r"[🫧🌊🐠🐙🐳🐬]")),
)

DEFAULT_VIEWPORTS: tuple[tuple[int, int], ...] = (
    (1440, 900),
    (1280, 800),
    (768, 1024),
    (390, 844),
)

CORE_PROJECT_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Maritime Watch", ("maritime watch",)),
    ("Inventra", ("inventra",)),
    ("Restofy", ("restofy",)),
    ("Shifha", ("shifha",)),
    ("KriptoParaTakip", ("kriptoparatakip",)),
    ("ML & Data Lab", ("ml & data lab", "ml-final-odev", "ml data lab", "ml lab")),
)


# ---------------------------------------------------------------------------
# Subprocess Helper (Windows WinError 6 Safe)
# ---------------------------------------------------------------------------


def run_python_subprocess(
    args: list[str],
    cwd: Path,
    timeout: float = 30.0,
) -> subprocess.CompletedProcess[str]:
    """Run a child Python process with explicit stdin=DEVNULL for Windows handle safety."""
    return subprocess.run(
        args,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Color & WCAG 2.1 Utilities
# ---------------------------------------------------------------------------


def _parse_alpha_token(raw_a: str | None) -> float:
    if raw_a is None:
        return 1.0
    t = raw_a.strip().lower()
    if t == "none":
        return 0.0
    if t.endswith("%"):
        return max(0.0, min(1.0, float(t[:-1]) / 100.0))
    return max(0.0, min(1.0, float(t)))


def _lin_srgb_to_255(c: float) -> float:
    c = max(0.0, min(1.0, c))
    srgb = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1.0 / 2.4)) - 0.055
    return max(0.0, min(255.0, srgb * 255.0))


def _oklab_to_rgba(l_val: float, a_val: float, b_val: float, alpha: float) -> tuple[float, float, float, float]:
    l_ = l_val + 0.3963377774 * a_val + 0.2158037573 * b_val
    m_ = l_val - 0.1055613458 * a_val - 0.0638541728 * b_val
    s_ = l_val - 0.0894841775 * a_val - 1.2914855480 * b_val

    l_c = l_ * l_ * l_
    m_c = m_ * m_ * m_
    s_c = s_ * s_ * s_

    r_lin = +4.0767416621 * l_c - 3.3077115913 * m_c + 0.2309699292 * s_c
    g_lin = -1.2684380046 * l_c + 2.6097574011 * m_c - 0.3413193965 * s_c
    b_lin = -0.0041960863 * l_c - 0.7034186147 * m_c + 1.7076147010 * s_c

    return (_lin_srgb_to_255(r_lin), _lin_srgb_to_255(g_lin), _lin_srgb_to_255(b_lin), alpha)


def _parse_oklab_component(tok: str, pct_scale: float) -> float:
    t = tok.strip().lower()
    if t == "none":
        return 0.0
    if t.endswith("%"):
        return float(t[:-1]) / 100.0 * pct_scale
    return float(t)


def _parse_hue_deg(tok: str) -> float:
    t = tok.strip().lower()
    if t == "none":
        return 0.0
    if t.endswith("deg"):
        return float(t[:-3])
    if t.endswith("rad"):
        return math.degrees(float(t[:-3]))
    if t.endswith("grad"):
        return float(t[:-4]) * 0.9
    if t.endswith("turn"):
        return float(t[:-4]) * 360.0
    return float(t)


def parse_css_color(color_str: str | None) -> tuple[float, float, float, float] | None:
    """Parse CSS rgb()/rgba(), hex, oklab(), oklch(), or color(srgb ...) into (r, g, b, a)."""
    if not color_str:
        return None
    s = color_str.strip().lower()
    if s in ("transparent", "none"):
        return (0.0, 0.0, 0.0, 0.0)
    m = re.match(
        r"^rgba?\(\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)\s*,\s*([0-9.]+%?)(?:\s*,\s*([0-9.]+%?))?\s*\)$",
        s,
    )
    if m:
        def _rgb_c(tok: str) -> float:
            return float(tok[:-1]) * 2.55 if tok.endswith("%") else float(tok)

        r = _rgb_c(m.group(1))
        g = _rgb_c(m.group(2))
        b = _rgb_c(m.group(3))
        a = _parse_alpha_token(m.group(4))
        return (r, g, b, a)
    # Modern CSS space-separated rgb(r g b / a)
    m_space = re.match(
        r"^rgba?\(\s*([0-9.]+%?)\s+([0-9.]+%?)\s+([0-9.]+%?)(?:\s*/\s*([0-9.]+%?))?\s*\)$",
        s,
    )
    if m_space:
        def _rgb_c2(tok: str) -> float:
            return float(tok[:-1]) * 2.55 if tok.endswith("%") else float(tok)

        r = _rgb_c2(m_space.group(1))
        g = _rgb_c2(m_space.group(2))
        b = _rgb_c2(m_space.group(3))
        a = _parse_alpha_token(m_space.group(4))
        return (r, g, b, a)

    # oklab(L a b [/ alpha])
    m_oklab = re.match(
        r"^oklab\(\s*([^\s/]+)\s+([^\s/]+)\s+([^\s/)]+)(?:\s*/\s*([^\s)]+))?\s*\)$",
        s,
    )
    if m_oklab:
        try:
            l_val = _parse_oklab_component(m_oklab.group(1), 1.0)
            a_val = _parse_oklab_component(m_oklab.group(2), 0.4)
            b_val = _parse_oklab_component(m_oklab.group(3), 0.4)
            alpha = _parse_alpha_token(m_oklab.group(4))
            return _oklab_to_rgba(l_val, a_val, b_val, alpha)
        except ValueError:
            return None

    # oklch(L C H [/ alpha])
    m_oklch = re.match(
        r"^oklch\(\s*([^\s/]+)\s+([^\s/]+)\s+([^\s/)]+)(?:\s*/\s*([^\s)]+))?\s*\)$",
        s,
    )
    if m_oklch:
        try:
            l_val = _parse_oklab_component(m_oklch.group(1), 1.0)
            c_val = _parse_oklab_component(m_oklch.group(2), 0.4)
            h_deg = _parse_hue_deg(m_oklch.group(3))
            alpha = _parse_alpha_token(m_oklch.group(4))
            h_rad = math.radians(h_deg)
            return _oklab_to_rgba(l_val, c_val * math.cos(h_rad), c_val * math.sin(h_rad), alpha)
        except ValueError:
            return None

    # color(srgb r g b [/ alpha])
    m_srgb = re.match(
        r"^color\(\s*srgb\s+([^\s/]+)\s+([^\s/]+)\s+([^\s/)]+)(?:\s*/\s*([^\s)]+))?\s*\)$",
        s,
    )
    if m_srgb:
        try:
            def _srgb_c(tok: str) -> float:
                if tok == "none":
                    return 0.0
                v = float(tok[:-1]) / 100.0 if tok.endswith("%") else float(tok)
                return max(0.0, min(1.0, v)) * 255.0

            r = _srgb_c(m_srgb.group(1))
            g = _srgb_c(m_srgb.group(2))
            b = _srgb_c(m_srgb.group(3))
            alpha = _parse_alpha_token(m_srgb.group(4))
            return (r, g, b, alpha)
        except ValueError:
            return None

    if s.startswith("#"):
        hex_part = s[1:]
        if len(hex_part) == 3:
            r, g, b = (int(c * 2, 16) for c in hex_part)
            return (float(r), float(g), float(b), 1.0)
        if len(hex_part) == 4:
            r, g, b, a_i = (int(c * 2, 16) for c in hex_part)
            return (float(r), float(g), float(b), a_i / 255.0)
        if len(hex_part) == 6:
            r = int(hex_part[0:2], 16)
            g = int(hex_part[2:4], 16)
            b = int(hex_part[4:6], 16)
            return (float(r), float(g), float(b), 1.0)
        if len(hex_part) == 8:
            r = int(hex_part[0:2], 16)
            g = int(hex_part[2:4], 16)
            b = int(hex_part[4:6], 16)
            a_i = int(hex_part[6:8], 16)
            return (float(r), float(g), float(b), a_i / 255.0)
    return None


def _extract_gradient_stops(bg_image: str | None) -> list[tuple[float, float, float, float]]:
    """Extract RGBA color stops from CSS linear-gradient/radial-gradient/conic-gradient."""
    if not bg_image or bg_image.strip().lower() == "none":
        return []
    if "gradient(" not in bg_image.lower():
        return []
    stops: list[tuple[float, float, float, float]] = []
    # Match color functions, hex tokens, and 'transparent'
    token_re = re.compile(
        r"(?:rgba?|oklch|oklab|color)\([^)]+\)|#[0-9a-fA-F]{3,8}\b|\btransparent\b",
        re.IGNORECASE,
    )
    for m in token_re.finditer(bg_image):
        parsed = parse_css_color(m.group(0))
        if parsed is not None:
            stops.append(parsed)
    return stops


def composite_source_over(
    fg: tuple[float, float, float, float],
    bg: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Porter-Duff source-over compositing of RGBA over opaque RGB."""
    a = max(0.0, min(1.0, fg[3]))
    return (
        fg[0] * a + bg[0] * (1.0 - a),
        fg[1] * a + bg[1] * (1.0 - a),
        fg[2] * a + bg[2] * (1.0 - a),
    )


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    """Compute WCAG 2.1 relative luminance for 0..255 sRGB triplet."""

    def _chan(v: float) -> float:
        c = max(0.0, min(1.0, v / 255.0))
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * _chan(rgb[0]) + 0.7152 * _chan(rgb[1]) + 0.0722 * _chan(rgb[2])


def contrast_ratio(
    fg_rgb: tuple[float, float, float],
    bg_rgb: tuple[float, float, float],
) -> float:
    """Compute WCAG 2.1 contrast ratio between two opaque RGB colors."""
    l1 = relative_luminance(fg_rgb)
    l2 = relative_luminance(bg_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------------------
# Pure-Static SVG, CSP, Ocean-Departure & README Validators
# ---------------------------------------------------------------------------


def validate_svg_xml(svg_path: Path) -> etree._Element:
    """Strictly parse SVG XML with entity resolution & network disabled."""
    if not svg_path.exists():
        raise AssertionError(f"SVG file does not exist: {svg_path}")
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        huge_tree=False,
        remove_comments=False,
    )
    try:
        tree = etree.parse(str(svg_path), parser=parser)
    except etree.XMLSyntaxError as exc:
        raise AssertionError(f"Invalid XML in {svg_path}: {exc}") from exc

    root = tree.getroot()
    if root is None:
        raise AssertionError(f"Empty XML document: {svg_path}")
    localname = etree.QName(root).localname
    if localname != "svg":
        raise AssertionError(f"Expected <svg> root element in {svg_path}, got <{localname}>")

    viewbox = root.get("viewBox")
    if not viewbox:
        raise AssertionError(f"Missing viewBox attribute on <svg> in {svg_path}")
    parts = re.split(r"[\s,]+", viewbox.strip())
    if len(parts) != 4:
        raise AssertionError(f"Malformed viewBox '{viewbox}' in {svg_path}")
    try:
        _, _, vw, vh = (float(p) for p in parts)
    except ValueError as exc:
        raise AssertionError(f"Non-numeric viewBox '{viewbox}' in {svg_path}") from exc
    if vw <= 0 or vh <= 0:
        raise AssertionError(f"Non-positive viewBox dimensions {vw}x{vh} in {svg_path}")
    return root


def parse_svg_viewbox(svg_path: Path) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, width, height) from an SVG's viewBox."""
    root = validate_svg_xml(svg_path)
    parts = re.split(r"[\s,]+", root.get("viewBox", "").strip())
    vx, vy, vw, vh = (float(p) for p in parts)
    return (vx, vy, vw, vh)


SVG_PRESENTATION_CSS_ATTRS = frozenset(
    {
        "fill",
        "stroke",
        "filter",
        "clip-path",
        "mask",
        "marker-start",
        "marker-mid",
        "marker-end",
    }
)

SMIL_ANIMATION_TAGS = frozenset(
    {"animate", "set", "animatemotion", "animatetransform"}
)


def _decode_css_escapes(text: str) -> str:
    def _hex_sub(m: re.Match[str]) -> str:
        cp = int(m.group(1), 16)
        if cp == 0 or cp > 0x10FFFF or (0xD800 <= cp <= 0xDFFF):
            return "\ufffd"
        return chr(cp)

    decoded = re.sub(r"\\([0-9a-fA-F]{1,6})[ \t\r\n\f]?", _hex_sub, text)
    decoded = re.sub(r"\\([^\n\r\f0-9a-fA-F])", r"\1", decoded)
    return decoded


def _normalize_uri_scheme_text(raw: str) -> str:
    return re.sub(r"[\x00-\x20]+", "", raw.lower())


_CSS_COMMENT_OR_STR_RE = re.compile(
    r'"(?:\\[\s\S]|[^"\\\n\r\f])*"|\'(?:\\[\s\S]|[^\'\\\n\r\f])*\'|(/\*[\s\S]*?\*/)'
)


def _strip_css_comments_preserve_strings(css_text: str) -> str:
    return _CSS_COMMENT_OR_STR_RE.sub(
        lambda m: "" if m.group(1) is not None else m.group(0),
        css_text,
    )


def _is_disallowed_css_uri(target: str) -> bool:
    t = target.strip()
    if not t or t.startswith("#"):
        return False
    norm = _normalize_uri_scheme_text(t)
    return (
        norm.startswith("http://")
        or norm.startswith("https://")
        or norm.startswith("//")
        or norm.startswith("javascript:")
        or norm.startswith("vbscript:")
        or norm.startswith("data:")
        or norm.startswith("/")
    )


def _scan_css_for_external_refs(css_text: str, location: str) -> list[str]:
    violations: list[str] = []
    no_comments = _strip_css_comments_preserve_strings(css_text)
    cleaned = _decode_css_escapes(no_comments)
    cleaned = _strip_css_comments_preserve_strings(cleaned)
    if re.search(r"@import\b", cleaned, re.IGNORECASE):
        violations.append(f"{location}: disallowed @import rule")
    for m in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", cleaned, re.IGNORECASE | re.DOTALL):
        target = m.group(2).strip()
        if _is_disallowed_css_uri(target):
            violations.append(f"{location}: disallowed CSS url({target!r})")
    for m_is in re.finditer(r"(?:-webkit-)?image-set\(", cleaned, re.IGNORECASE):
        depth = 1
        idx = m_is.end()
        in_quote: str | None = None
        while idx < len(cleaned) and depth > 0:
            ch = cleaned[idx]
            if in_quote:
                if ch == "\\" and idx + 1 < len(cleaned):
                    idx += 2
                    continue
                if ch == in_quote:
                    in_quote = None
            else:
                if ch in ("'", '"'):
                    in_quote = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            idx += 1
        inner = cleaned[m_is.end() : idx]
        inner_no_type = re.sub(
            r"\btype\(\s*(['\"]).*?\1\s*\)", "", inner, flags=re.IGNORECASE | re.DOTALL
        )
        for m_q in re.finditer(r"(['\"])(.*?)\1", inner_no_type, re.DOTALL):
            target = m_q.group(2).strip()
            if _is_disallowed_css_uri(target):
                violations.append(f"{location}: disallowed CSS image-set({target!r})")
    return violations


def find_svg_csp_violations(svg_path: Path) -> list[str]:
    """Scan an SVG for GitHub README CSP violations and unsafe/external constructs."""
    root = validate_svg_xml(svg_path)
    violations: list[str] = []

    # Check XML processing instructions anywhere in the document (including prolog)
    doc_tree = root.getroottree()
    for pi in doc_tree.xpath("//processing-instruction()"):
        pi_target = (pi.target or "").lower()
        pi_text = pi.text or ""
        if pi_target == "xml-stylesheet" or "stylesheet" in pi_target:
            violations.append(
                f"Disallowed XML processing instruction <?{pi.target} {pi_text[:60]}?>"
            )
        else:
            violations.extend(_scan_css_for_external_refs(pi_text, f"<?{pi.target}?>"))

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        qname = etree.QName(elem)
        local = qname.localname.lower()

        if local in DISALLOWED_SVG_TAGS:
            violations.append(f"Disallowed element <{qname.localname}>")

        if local == "style":
            style_text = "".join(elem.itertext())
            if style_text.strip():
                violations.extend(_scan_css_for_external_refs(style_text, "<style>"))

        if local in SMIL_ANIMATION_TAGS:
            anim_attr = (elem.get("attributeName") or "").strip().lower()
            anim_attr_local = anim_attr.split(":", 1)[-1]
            if anim_attr_local.startswith("on"):
                violations.append(
                    f"Disallowed SMIL animation targeting event handler {anim_attr!r} on <{qname.localname}>"
                )
            for anim_prop in ("to", "from", "by", "values"):
                raw_prop = elem.get(anim_prop)
                if not raw_prop:
                    continue
                violations.extend(
                    _scan_css_for_external_refs(raw_prop, f"<{qname.localname} {anim_prop}=...>")
                )
                candidates = raw_prop.split(";") if anim_prop == "values" else [raw_prop]
                for cand in candidates:
                    c_strip = cand.strip()
                    if not c_strip or c_strip.startswith("#"):
                        continue
                    c_norm = _normalize_uri_scheme_text(c_strip)
                    if (
                        "javascript:" in c_norm
                        or "vbscript:" in c_norm
                        or "data:text/html" in c_norm
                        or c_norm.startswith(("http://", "https://", "//", "data:"))
                        or (anim_attr_local in URI_ATTR_LOCALNAMES and c_norm.startswith("/"))
                    ):
                        violations.append(
                            f"Disallowed SMIL URI in {anim_prop!r} (attributeName={anim_attr!r}) on <{qname.localname}>: {c_strip[:80]}"
                        )

        for attr_key, attr_val in elem.attrib.items():
            attr_local = etree.QName(attr_key).localname if "}" in attr_key else attr_key
            attr_lower = attr_local.lower()
            val_stripped = (attr_val or "").strip()
            val_norm = _normalize_uri_scheme_text(val_stripped)

            if attr_lower.startswith("on"):
                violations.append(
                    f"Disallowed event handler attribute {attr_local!r} on <{qname.localname}>"
                )

            if (
                "javascript:" in val_norm
                or "vbscript:" in val_norm
                or "data:text/html" in val_norm
            ):
                violations.append(
                    f"Disallowed script URI in {attr_local!r} on <{qname.localname}>: {val_stripped[:80]}"
                )

            if attr_lower in URI_ATTR_LOCALNAMES and val_stripped:
                if not val_stripped.startswith("#"):
                    if (
                        val_norm.startswith("http://")
                        or val_norm.startswith("https://")
                        or val_norm.startswith("//")
                        or val_norm.startswith("data:")
                        or (local in ("image", "use", "feimage") and val_norm.startswith("/"))
                    ):
                        violations.append(
                            f"External/disallowed URI in {attr_local!r} on <{qname.localname}>: {val_stripped[:80]}"
                        )

            if attr_lower == "style" and val_stripped:
                violations.extend(
                    _scan_css_for_external_refs(val_stripped, f"<{qname.localname} style=...>")
                )

            if attr_lower in SVG_PRESENTATION_CSS_ATTRS and val_stripped:
                violations.extend(
                    _scan_css_for_external_refs(
                        val_stripped, f"<{qname.localname} {attr_local}=...>"
                    )
                )

    return violations


def check_svg_dark_canvas(svg_path: Path) -> dict[str, Any]:
    """Verify an SVG plate's primary full-canvas backdrop (<rect> >= 80% of viewBox) is dark-theme (L < 0.08)."""
    root = validate_svg_xml(svg_path)
    _, _, vw, vh = parse_svg_viewbox(svg_path)
    vb_area = vw * vh

    # Build id -> element map for <linearGradient>, <radialGradient>, <pattern>
    defs_by_id: dict[str, etree._Element] = {}
    for el in root.iter():
        if isinstance(el.tag, str) and el.get("id"):
            defs_by_id[el.get("id", "")] = el

    def _resolve_gradient_lums(grad_id: str) -> list[float]:
        g = defs_by_id.get(grad_id)
        if g is None:
            return []
        lums: list[float] = []
        visited: set[str] = set()
        cur: etree._Element | None = g
        while cur is not None:
            for st in cur:
                if isinstance(st.tag, str) and etree.QName(st).localname.lower() == "stop":
                    sc = (st.get("stop-color") or "").strip()
                    if not sc and st.get("style"):
                        m_sc = re.search(r"stop-color\s*:\s*([^;]+)", st.get("style", ""), re.I)
                        if m_sc:
                            sc = m_sc.group(1).strip()
                    parsed = parse_css_color(sc)
                    if parsed is not None:
                        lums.append(relative_luminance((parsed[0], parsed[1], parsed[2])))
            if lums:
                break
            ref = (cur.get("href") or cur.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#")
            if not ref or ref in visited:
                break
            visited.add(ref)
            cur = defs_by_id.get(ref)
        return lums

    def _parse_dim(raw: str | None, full: float) -> float | None:
        if not raw:
            return None
        t = raw.strip()
        if t.endswith("%"):
            try:
                return full * float(t[:-1]) / 100.0
            except ValueError:
                return None
        t = re.sub(r"px$", "", t, flags=re.IGNORECASE)
        try:
            return float(t)
        except ValueError:
            return None

    def _is_hidden_tree(el: etree._Element) -> bool:
        cur: etree._Element | None = el
        while cur is not None:
            if isinstance(cur.tag, str):
                ln = etree.QName(cur).localname.lower()
                if ln in ("defs", "clippath", "mask", "pattern", "symbol"):
                    return True
                if cur.get("display") == "none" or cur.get("visibility") == "hidden":
                    return True
                try:
                    if float(cur.get("opacity", "1")) <= 0.05:
                        return True
                except ValueError:
                    pass
            cur = cur.getparent()
        return False

    backdrop_lums: list[float] = []
    light_backdrops: list[float] = []

    for el in root.iter():
        if not isinstance(el.tag, str) or etree.QName(el).localname.lower() != "rect":
            continue
        if _is_hidden_tree(el):
            continue
        rw = _parse_dim(el.get("width"), vw)
        rh = _parse_dim(el.get("height"), vh)
        if rw is None or rh is None or rw * rh < 0.80 * vb_area:
            continue

        fill = (el.get("fill") or "").strip()
        if not fill and el.get("style"):
            m_f = re.search(r"fill\s*:\s*([^;]+)", el.get("style", ""), re.I)
            if m_f:
                fill = m_f.group(1).strip()
        if not fill or fill.lower() == "none":
            continue
        try:
            if float(el.get("fill-opacity", "1")) <= 0.05:
                continue
        except ValueError:
            pass

        m_url = re.match(r"url\(\s*['\"]?#([^)'\"]+)['\"]?\s*\)", fill, re.IGNORECASE)
        if m_url:
            ref_id = m_url.group(1)
            ref_el = defs_by_id.get(ref_id)
            if ref_el is not None and etree.QName(ref_el).localname.lower() == "pattern":
                continue  # subtle grid overlay pattern
            g_lums = _resolve_gradient_lums(ref_id)
            if g_lums:
                max_g = max(g_lums)
                if max_g < 0.08:
                    backdrop_lums.append(max_g)
                else:
                    light_backdrops.append(max_g)
            continue

        parsed = parse_css_color(fill)
        if parsed is not None and parsed[3] > 0.5:
            lum = relative_luminance((parsed[0], parsed[1], parsed[2]))
            if lum < 0.08:
                backdrop_lums.append(lum)
            else:
                light_backdrops.append(lum)

    return {
        "backdrop_dark_lums": backdrop_lums,
        "backdrop_light_lums": light_backdrops,
    }


def check_svg_size_budget(
    svg_paths: list[Path],
    max_each_bytes: int = 150 * 1024,
    max_total_bytes: int = 400 * 1024,
) -> dict[str, int]:
    """Verify every SVG is non-empty, < max_each_bytes, and total < max_total_bytes."""
    if not svg_paths:
        raise AssertionError("No SVG paths provided to check_svg_size_budget")
    sizes: dict[str, int] = {}
    total = 0
    for p in svg_paths:
        if not p.exists():
            raise AssertionError(f"SVG missing for size check: {p}")
        sz = p.stat().st_size
        if sz <= 0:
            raise AssertionError(f"SVG file is empty: {p}")
        if sz >= max_each_bytes:
            raise AssertionError(
                f"SVG {p.name} size {sz} bytes exceeds per-file budget < {max_each_bytes} bytes"
            )
        sizes[p.name] = sz
        total += sz
    if total >= max_total_bytes:
        raise AssertionError(
            f"Combined SVG size {total} bytes exceeds total budget < {max_total_bytes} bytes ({sizes})"
        )
    sizes["total"] = total
    return sizes


def find_ocean_theme_artifacts(text: str, context_label: str = "content") -> list[str]:
    """Detect legacy Frutiger Aero / ocean-theme artifacts without false-positiving on Maritime Watch."""
    hits: list[str] = []
    for label, pattern in OCEAN_THEME_PATTERNS:
        m = pattern.search(text)
        if m:
            hits.append(f"{context_label}: matched legacy theme marker {label!r} ({m.group(0)!r})")
    return hits


class _ReadmeHTMLParser(HTMLParser):
    """Collect <img>, <source>, and <a> elements with source character offsets."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[int, str, dict[str, str]]] = []
        self._line_starts: list[int] = [0]
        for idx, ch in enumerate(text):
            if ch == "\n":
                self._line_starts.append(idx + 1)

    def _abs_offset(self) -> int:
        lineno, col = self.getpos()
        if 1 <= lineno <= len(self._line_starts):
            return self._line_starts[lineno - 1] + col
        return 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in ("img", "source", "a"):
            attr_map = {k.lower(): (v or "") for k, v in attrs if k}
            self.items.append((self._abs_offset(), t, attr_map))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def extract_readme_images_metadata(readme_path: Path) -> list[dict[str, Any]]:
    """Extract Markdown and HTML <img> / <picture><source> references from README.md in order."""
    if not readme_path.exists():
        raise AssertionError(f"README not found: {readme_path}")
    text = readme_path.read_text(encoding="utf-8")
    positioned: list[tuple[int, dict[str, Any]]] = []

    def _build_entry(kind: str, raw_src: str, alt: str) -> dict[str, Any]:
        raw_s = raw_src.strip()
        clean_src = raw_s.split("?", 1)[0].split("#", 1)[0].strip()
        is_remote = bool(re.match(r"^(?:https?:)?//", clean_src, re.IGNORECASE))
        is_empty_or_frag = not clean_src or raw_s.startswith("#")
        is_local = (not is_remote) and (not is_empty_or_frag)
        return {
            "kind": kind,
            "src": raw_s,
            "clean_src": clean_src,
            "alt": alt.strip(),
            "is_local": is_local,
            "empty_or_fragment": is_empty_or_frag,
            "resolved_path": (readme_path.parent / clean_src).resolve() if is_local else None,
        }

    # Markdown images: ![alt](url "optional title")
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)", text):
        positioned.append((m.start(), _build_entry("markdown", m.group(2), m.group(1))))

    # HTML <img> and <picture><source srcset="..."> via HTMLParser
    parser = _ReadmeHTMLParser(text)
    parser.feed(text)
    parser.close()
    for offset, tag, attrs in parser.items:
        if tag == "img":
            if "src" in attrs:
                positioned.append((offset, _build_entry("html", attrs.get("src", ""), attrs.get("alt", ""))))
            img_srcset = attrs.get("srcset", "").strip()
            if img_srcset:
                for cand in img_srcset.split(","):
                    parts = cand.strip().split()
                    if parts:
                        positioned.append((offset, _build_entry("html_srcset", parts[0], attrs.get("alt", ""))))
        elif tag == "source":
            srcset = attrs.get("srcset", "").strip()
            if srcset:
                for cand in srcset.split(","):
                    parts = cand.strip().split()
                    if parts:
                        positioned.append((offset, _build_entry("html_source", parts[0], attrs.get("alt", ""))))
            elif "src" in attrs:
                positioned.append((offset, _build_entry("html_source", attrs.get("src", ""), attrs.get("alt", ""))))

    positioned.sort(key=lambda pair: pair[0])
    return [item for _, item in positioned]


def extract_readme_local_assets(readme_path: Path) -> list[Path]:
    """Return deduplicated local image/asset Paths referenced in README.md."""
    seen: set[Path] = set()
    result: list[Path] = []
    for item in extract_readme_images_metadata(readme_path):
        if item.get("empty_or_fragment"):
            raise AssertionError(
                f"Invalid empty or fragment-only image src in {readme_path.name}: {item['src']!r}"
            )
        if item["is_local"] and item["resolved_path"] is not None:
            p = item["resolved_path"]
            if p not in seen:
                seen.add(p)
                result.append(p)
    return result


def extract_readme_links(readme_path: Path) -> list[str]:
    """Extract Markdown links (including nested badge links & ref links) and HTML <a href> targets."""
    text = readme_path.read_text(encoding="utf-8")
    links: list[str] = []

    # 1. Reference-style link definitions: [id]: url "optional title"
    ref_map: dict[str, str] = {}
    for m in re.finditer(
        r"^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?(?:\s+[\"'(][^\"')]*[\"')])?\s*$",
        text,
        re.MULTILINE,
    ):
        ref_map[m.group(1).strip().lower()] = m.group(2).strip()

    # 2. Scanner for Markdown [label](url) and [label][ref], supporting nested [![alt](img)](url)
    n = len(text)
    i = 0
    while i < n:
        if text[i] == "\\" and i + 1 < n:
            i += 2
            continue
        if text[i] == "[" and (i == 0 or text[i - 1] != "!"):
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                j += 1
            if depth == 0:
                label_inner = text[i + 1 : j - 1]
                k = j
                if k < n and text[k] == "(":
                    # Inline destination
                    p_depth = 1
                    m_idx = k + 1
                    while m_idx < n and p_depth > 0:
                        if text[m_idx] == "\\" and m_idx + 1 < n:
                            m_idx += 2
                            continue
                        if text[m_idx] == "(":
                            p_depth += 1
                        elif text[m_idx] == ")":
                            p_depth -= 1
                        m_idx += 1
                    if p_depth == 0:
                        dest_raw = text[k + 1 : m_idx - 1].strip()
                        dest_parts = dest_raw.split(None, 1)
                        if dest_parts:
                            dest = dest_parts[0].strip("<>")
                            links.append(dest)
                        i = m_idx
                        continue
                elif k < n and text[k] == "[":
                    end_ref = text.find("]", k + 1)
                    if end_ref != -1:
                        ref_key = text[k + 1 : end_ref].strip().lower() or label_inner.strip().lower()
                        if ref_key in ref_map:
                            links.append(ref_map[ref_key])
                        i = end_ref + 1
                        continue
        i += 1

    # 3. HTML <a href="..."> via HTMLParser
    parser = _ReadmeHTMLParser(text)
    parser.feed(text)
    parser.close()
    for _, tag, attrs in parser.items:
        if tag == "a" and "href" in attrs:
            href = attrs["href"].strip()
            if href:
                links.append(href)

    return links


# ---------------------------------------------------------------------------
# Pillow PNG Validation
# ---------------------------------------------------------------------------


def validate_png(
    png_path: Path,
    expected_width: int | None = None,
    min_stddev: float = 2.0,
    max_median_luminance: float | None = None,
) -> dict[str, Any]:
    """Verify PNG integrity, dimensions, non-blank pixel variance, and optional dark-theme luminance."""
    if not png_path.exists():
        raise AssertionError(f"Screenshot file missing: {png_path}")
    if png_path.stat().st_size <= 0:
        raise AssertionError(f"Screenshot file is empty: {png_path}")

    with Image.open(png_path) as probe:
        if probe.format != "PNG":
            raise AssertionError(f"Expected PNG format for {png_path}, got {probe.format}")
        probe.verify()

    with Image.open(png_path) as img:
        rgb = img.convert("RGB")
        width, height = rgb.size
        if width <= 0 or height <= 0:
            raise AssertionError(f"Invalid PNG dimensions {width}x{height} for {png_path}")
        if expected_width is not None and width != expected_width:
            raise AssertionError(
                f"Expected PNG width {expected_width} for {png_path.name}, got {width}"
            )
        stat = ImageStat.Stat(rgb)
        max_stddev = max(stat.stddev)
        if max_stddev <= min_stddev:
            raise AssertionError(
                f"Screenshot {png_path.name} appears blank/uniform (max channel stddev={max_stddev:.2f} <= {min_stddev})"
            )

        median_lum = None
        if max_median_luminance is not None:
            # Sample down to keep computation fast on tall full-page screenshots
            sample = rgb.copy()
            sample.thumbnail((400, 400))
            pixels = list(
                sample.get_flattened_data()
                if hasattr(sample, "get_flattened_data")
                else sample.getdata()
            )
            lums = sorted(relative_luminance(px) for px in pixels)
            median_lum = lums[len(lums) // 2]
            if median_lum >= max_median_luminance:
                raise AssertionError(
                    f"Screenshot {png_path.name} median luminance {median_lum:.3f} >= {max_median_luminance} (not dark-theme)"
                )

        return {
            "path": str(png_path),
            "width": width,
            "height": height,
            "max_stddev": max_stddev,
            "median_luminance": median_lum,
        }


# ---------------------------------------------------------------------------
# Ephemeral Local HTTP Server (Static Files + Same-Origin SVG Host Routes)
# ---------------------------------------------------------------------------


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/__e2e_svg_host__":
            qs = parse_qs(parsed.query)
            src = qs.get("src", [""])[0]
            width = int(qs.get("w", ["880"])[0])
            bg = qs.get("bg", ["#0d1117"])[0]
            body = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                f"<title>SVG Host</title></head>"
                f"<body style='margin:0;padding:0;background:{html_escape(bg)};'>"
                f"<object id='svg-host' data='{html_escape(src)}' type='image/svg+xml' "
                f"style='display:block;width:{width}px;margin:0;border:0;'></object>"
                "</body></html>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/__e2e_svg_stack__":
            qs = parse_qs(parsed.query)
            srcs = [s for s in qs.get("srcs", [""])[0].split(",") if s]
            width = int(qs.get("w", ["880"])[0])
            bg = qs.get("bg", ["#0d1117"])[0]
            gap = int(qs.get("gap", ["16"])[0])
            objs = "\n".join(
                f"<object class='svg-plate' data='{html_escape(src)}' type='image/svg+xml' "
                f"style='display:block;width:{width}px;margin:0 0 {gap}px 0;border:0;'></object>"
                for src in srcs
            )
            body = (
                "<!doctype html><html><head><meta charset='utf-8'>"
                "<title>README SVG Dark Stack</title></head>"
                f"<body style='margin:0;padding:0;background:{html_escape(bg)};'>"
                f"<main style='width:{width}px;margin:0;'>{objs}</main>"
                "</body></html>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        super().do_GET()


class LocalSiteServer:
    """Ephemeral ``127.0.0.1:0`` HTTP server serving a target directory read-only."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir).resolve()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("LocalSiteServer is not started")
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> "LocalSiteServer":
        handler = functools.partial(_QuietHandler, directory=str(self.root_dir))
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="e2e-local-http",
            daemon=True,
        )
        self._thread.start()
        return self

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None

    def __enter__(self) -> "LocalSiteServer":
        return self.start()

    def __exit__(self, *_: Any) -> None:
        self.stop()


# ---------------------------------------------------------------------------
# Async Loop Runner & Choreographer CDP Harness
# ---------------------------------------------------------------------------


class _LoopRunner:
    """Dedicated background asyncio event-loop thread for driving choreographer.Browser."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, name="e2e-cdp-loop", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5.0)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    def run(self, coro: Any, timeout: float = 30.0) -> Any:
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout=timeout)

    def stop(self) -> None:
        if not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=5.0)
            if not self._thread.is_alive():
                self._loop.close()


def _is_favicon_url(url: str) -> bool:
    return bool(url) and urlsplit(url).path == "/favicon.ico"


@dataclass
class PageSession:
    """Isolated CDP tab session with runtime/network collectors & E2E inspection helpers."""

    harness: "CDPHarness"
    tab: Any
    viewport: tuple[int, int] = (1440, 900)
    console_errors: list[str] = field(default_factory=list)
    js_exceptions: list[str] = field(default_factory=list)
    log_errors: list[str] = field(default_factory=list)
    network_failures: list[dict[str, Any]] = field(default_factory=list)
    http_errors: list[dict[str, Any]] = field(default_factory=list)
    requested_urls: list[str] = field(default_factory=list)
    _request_map: dict[str, dict[str, str]] = field(default_factory=dict)
    _load_event: asyncio.Event | None = None
    _closed: bool = False

    def _run(self, coro: Any, timeout: float = 30.0) -> Any:
        return self.harness._runner.run(coro, timeout=timeout)

    async def _async_init(self) -> None:
        self._load_event = asyncio.Event()

        async def on_console(event: dict[str, Any]) -> None:
            try:
                params = event.get("params", {})
                if params.get("type") in ("error", "assert"):
                    args = params.get("args", [])
                    rendered = " ".join(
                        str(a.get("value", a.get("description", ""))) for a in args
                    ).strip()
                    self.console_errors.append(rendered or params.get("type", "error"))
            except Exception as exc:  # pragma: no cover - defensive callback guard
                self.console_errors.append(f"callback_error: {exc}")

        async def on_exception(event: dict[str, Any]) -> None:
            try:
                details = event.get("params", {}).get("exceptionDetails", {})
                desc = (
                    details.get("exception", {}).get("description")
                    or details.get("text")
                    or "Uncaught JS exception"
                )
                self.js_exceptions.append(str(desc))
            except Exception as exc:  # pragma: no cover
                self.js_exceptions.append(f"callback_error: {exc}")

        async def on_log(event: dict[str, Any]) -> None:
            try:
                entry = event.get("params", {}).get("entry", {})
                if entry.get("level") == "error":
                    url = entry.get("url", "")
                    if not _is_favicon_url(url):
                        self.log_errors.append(f"{entry.get('text', '')} ({url})")
            except Exception:
                pass

        async def on_request(event: dict[str, Any]) -> None:
            try:
                params = event.get("params", {})
                req_id = params.get("requestId", "")
                req = params.get("request", {})
                url = req.get("url", "")
                if req_id:
                    self._request_map[req_id] = {
                        "url": url,
                        "type": params.get("type", ""),
                    }
                if url:
                    self.requested_urls.append(url)
            except Exception:
                pass

        async def on_loading_failed(event: dict[str, Any]) -> None:
            try:
                params = event.get("params", {})
                if params.get("canceled"):
                    return
                req_id = params.get("requestId", "")
                info = self._request_map.get(req_id, {})
                url = info.get("url", "")
                if _is_favicon_url(url):
                    return
                self.network_failures.append(
                    {
                        "url": url,
                        "type": params.get("type", info.get("type", "")),
                        "errorText": params.get("errorText", "loadingFailed"),
                    }
                )
            except Exception:
                pass

        async def on_response(event: dict[str, Any]) -> None:
            try:
                params = event.get("params", {})
                resp = params.get("response", {})
                status = int(resp.get("status", 0))
                url = resp.get("url", "")
                if status >= 400 and not _is_favicon_url(url):
                    self.http_errors.append(
                        {
                            "url": url,
                            "status": status,
                            "type": params.get("type", ""),
                        }
                    )
            except Exception:
                pass

        async def on_load(_: dict[str, Any]) -> None:
            try:
                if self._load_event is not None:
                    self._load_event.set()
            except Exception:
                pass

        self.tab.subscribe("Runtime.consoleAPICalled", on_console)
        self.tab.subscribe("Runtime.exceptionThrown", on_exception)
        self.tab.subscribe("Log.entryAdded", on_log)
        self.tab.subscribe("Network.requestWillBeSent", on_request)
        self.tab.subscribe("Network.loadingFailed", on_loading_failed)
        self.tab.subscribe("Network.responseReceived", on_response)
        self.tab.subscribe("Page.loadEventFired", on_load)

        await self.tab.send_command("Page.enable")
        await self.tab.send_command("Runtime.enable")
        await self.tab.send_command("Network.enable")
        await self.tab.send_command("Log.enable")
        await self.tab.send_command("Emulation.setScrollbarsHidden", {"hidden": True})
        await self._async_set_viewport(self.viewport[0], self.viewport[1])

    async def _async_set_viewport(self, width: int, height: int) -> None:
        await self.tab.send_command(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": width <= 768,
            },
        )
        await asyncio.sleep(0.05)

    def set_viewport(self, width: int, height: int) -> None:
        self.viewport = (width, height)
        self._run(self._async_set_viewport(width, height))

    def set_reduced_motion(self, enabled: bool = True) -> None:
        val = "reduce" if enabled else "no-preference"
        self._run(
            self.tab.send_command(
                "Emulation.setEmulatedMedia",
                {"features": [{"name": "prefers-reduced-motion", "value": val}]},
            )
        )

    def clear_events(self) -> None:
        self.console_errors.clear()
        self.js_exceptions.clear()
        self.log_errors.clear()
        self.network_failures.clear()
        self.http_errors.clear()
        self.requested_urls.clear()
        self._request_map.clear()

    def goto(self, url: str, settle_ms: int = 180, clear_prior: bool = True) -> None:
        if clear_prior:
            self.clear_events()

        async def _nav() -> None:
            assert self._load_event is not None
            self._load_event.clear()
            await self.tab.send_command("Page.navigate", {"url": url})
            await asyncio.wait_for(self._load_event.wait(), timeout=20.0)
            if settle_ms > 0:
                await asyncio.sleep(settle_ms / 1000.0)

        self._run(_nav(), timeout=25.0)

    def eval_js(self, expression: str) -> Any:
        async def _eval() -> Any:
            resp = await self.tab.send_command(
                "Runtime.evaluate",
                {
                    "expression": expression,
                    "returnByValue": True,
                    "awaitPromise": True,
                },
            )
            res = resp.get("result", {})
            if "exceptionDetails" in res:
                details = res["exceptionDetails"]
                msg = (
                    details.get("exception", {}).get("description")
                    or details.get("text")
                    or str(details)
                )
                raise AssertionError(f"JS evaluation error: {msg}")
            return res.get("result", {}).get("value")

        return self._run(_eval(), timeout=25.0)

    def click_point(self, x: float, y: float) -> None:
        async def _click() -> None:
            for event_type in ("mousePressed", "mouseReleased"):
                await self.tab.send_command(
                    "Input.dispatchMouseEvent",
                    {
                        "type": event_type,
                        "x": float(x),
                        "y": float(y),
                        "button": "left",
                        "clickCount": 1,
                    },
                )
            await asyncio.sleep(0.08)

        self._run(_click())

    def click_selector(self, selector: str) -> None:
        rect = self.eval_js(
            f"""(() => {{
                const el = document.querySelector({json.dumps(selector)});
                if (!el) return null;
                el.scrollIntoView({{block: 'center', inline: 'center'}});
                const r = el.getBoundingClientRect();
                return {{left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height}};
            }})()"""
        )
        if not rect or rect["width"] <= 0 or rect["height"] <= 0:
            raise AssertionError(f"Selector not visible/clickable: {selector}")
        self.click_point(rect["left"] + rect["width"] / 2.0, rect["top"] + rect["height"] / 2.0)

    def press_key(
        self,
        key: str,
        code: str,
        windows_vk: int,
        modifiers: int = 0,
    ) -> None:
        async def _key() -> None:
            await self.tab.send_command(
                "Input.dispatchKeyEvent",
                {
                    "type": "rawKeyDown",
                    "modifiers": modifiers,
                    "key": key,
                    "code": code,
                    "windowsVirtualKeyCode": windows_vk,
                },
            )
            await self.tab.send_command(
                "Input.dispatchKeyEvent",
                {
                    "type": "keyUp",
                    "modifiers": modifiers,
                    "key": key,
                    "code": code,
                    "windowsVirtualKeyCode": windows_vk,
                },
            )
            await asyncio.sleep(0.08)

        self._run(_key())

    def type_text(self, text: str) -> None:
        async def _type() -> None:
            await self.tab.send_command("Input.insertText", {"text": text})
            await asyncio.sleep(0.08)

        self._run(_type())

    def screenshot_png(self, out_path: Path | None = None, full_page: bool = True) -> bytes:
        async def _snap() -> bytes:
            params: dict[str, Any] = {"format": "png"}
            if full_page:
                metrics = await self.tab.send_command("Page.getLayoutMetrics")
                content_size = metrics.get("result", {}).get("cssContentSize") or metrics.get(
                    "result", {}
                ).get("contentSize", {})
                w = max(1, math.ceil(float(content_size.get("width", self.viewport[0]))))
                h = max(1, math.ceil(float(content_size.get("height", self.viewport[1]))))
                params["captureBeyondViewport"] = True
                params["clip"] = {
                    "x": 0,
                    "y": 0,
                    "width": w,
                    "height": h,
                    "scale": 1,
                }
            resp = await self.tab.send_command("Page.captureScreenshot", params)
            b64 = resp.get("result", {}).get("data", "")
            return base64.b64decode(b64)

        raw = self._run(_snap(), timeout=30.0)
        if out_path is not None:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(raw)
        return raw

    def external_requests(self) -> list[str]:
        bad: list[str] = []
        for u in self.requested_urls:
            parsed = urlparse(u)
            if parsed.scheme in ("http", "https") and parsed.hostname not in (
                "127.0.0.1",
                "localhost",
            ):
                bad.append(u)
        return bad

    def assert_clean_runtime(self) -> None:
        assert not self.console_errors, f"Console errors observed: {self.console_errors}"
        assert not self.js_exceptions, f"Uncaught JS exceptions observed: {self.js_exceptions}"
        assert not self.log_errors, f"Browser log errors observed: {self.log_errors}"
        assert not self.network_failures, f"Network failures observed: {self.network_failures}"
        assert not self.http_errors, f"HTTP >=400 responses observed: {self.http_errors}"

    # -----------------------------------------------------------------------
    # Tier 2 Geometry, Overflow, Collision & WCAG Evaluators
    # -----------------------------------------------------------------------

    def inspect_svg_host(
        self,
        server_base_url: str,
        svg_url_path: str,
        width: int = 880,
        reduced_motion: bool = False,
    ) -> dict[str, Any]:
        """Host a standalone SVG on #0d1117 at ``width``px and inspect geometry/clipping/overlap/contrast."""
        self.set_viewport(width, 900)
        if reduced_motion:
            self.set_reduced_motion(True)
        src = svg_url_path if svg_url_path.startswith("/") else f"/{svg_url_path}"
        host_url = f"{server_base_url}/__e2e_svg_host__?src={quote(src, safe='/')}&w={width}&bg=%230d1117"
        self.goto(host_url, settle_ms=200)

        data = self.eval_js(
            """(async () => {
                const obj = document.getElementById('svg-host');
                let doc = null;
                for (let i = 0; i < 40; i++) {
                    doc = obj && obj.contentDocument;
                    if (doc && doc.documentElement && doc.documentElement.localName === 'svg') break;
                    await new Promise(r => setTimeout(r, 50));
                }
                if (!doc || !doc.documentElement) {
                    return { error: 'SVG contentDocument did not load' };
                }
                const svg = doc.documentElement;
                const vbAttr = svg.getAttribute('viewBox');
                const vb = (vbAttr && svg.viewBox && svg.viewBox.baseVal) ? {
                    x: svg.viewBox.baseVal.x,
                    y: svg.viewBox.baseVal.y,
                    width: svg.viewBox.baseVal.width,
                    height: svg.viewBox.baseVal.height,
                } : null;
                const sr = svg.getBoundingClientRect();
                const svgRect = { left: sr.left, top: sr.top, right: sr.right, bottom: sr.bottom, width: sr.width, height: sr.height };

                const getEffectiveVisAndOpacity = (node) => {
                    let cur = node;
                    let hidden = false;
                    let accumOpacity = 1.0;
                    while (cur && cur.nodeType === 1) {
                        const cs = doc.defaultView.getComputedStyle(cur);
                        if (cs.display === 'none' || cs.visibility === 'hidden') { hidden = true; break; }
                        const op = parseFloat(cs.opacity || '1');
                        accumOpacity *= (isNaN(op) ? 1.0 : op);
                        if (accumOpacity <= 0.05) { hidden = true; break; }
                        if (cur === svg) break;
                        cur = cur.parentElement;
                    }
                    return { hidden, accumOpacity };
                };

                const resolveUrlFill = (fillStr) => {
                    if (!fillStr) return null;
                    const m = fillStr.match(/url\\(\\s*['"]?[^#)]*#([^)'"]+)['"]?\\s*\\)/i);
                    if (!m) return null;
                    const id = m[1];
                    const refEl = doc.getElementById(id);
                    if (!refEl) return { isUrl: true, unresolved: true, id };
                    const ln = (refEl.localName || '').toLowerCase();
                    if (ln === 'pattern') return { isUrl: true, isPattern: true, id };
                    if (ln === 'lineargradient' || ln === 'radialgradient') {
                        const stops = [];
                        let cur = refEl;
                        const visited = new Set();
                        while (cur && !visited.has(cur)) {
                            visited.add(cur);
                            const stEls = Array.from(cur.querySelectorAll('stop'));
                            if (stEls.length > 0) {
                                for (const st of stEls) {
                                    const scs = doc.defaultView.getComputedStyle(st);
                                    const stopOp = parseFloat(scs.stopOpacity || '1');
                                    stops.push({
                                        color: scs.stopColor || '#000000',
                                        opacity: isNaN(stopOp) ? 1.0 : stopOp,
                                    });
                                }
                                break;
                            }
                            const href = (cur.getAttribute('href') || cur.getAttribute('xlink:href') || '').replace(/^#/, '');
                            cur = href ? doc.getElementById(href) : null;
                        }
                        if (stops.length === 0) return { isUrl: true, unresolved: true, id };
                        return { isUrl: true, gradientStops: stops, id };
                    }
                    return { isUrl: true, unresolved: true, id };
                };

                const shapeCandidates = Array.from(svg.querySelectorAll('rect, path, polygon, circle, ellipse'))
                    .filter(el => !el.closest('defs, clipPath, mask, pattern, symbol'));

                const texts = [];
                const tspanOverlaps = [];
                const textNodes = Array.from(svg.querySelectorAll('text'));
                for (let idx = 0; idx < textNodes.length; idx++) {
                    const el = textNodes[idx];
                    if (el.closest('defs, clipPath, mask, pattern, symbol')) continue;
                    const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (!txt) continue;
                    const vis = getEffectiveVisAndOpacity(el);
                    if (vis.hidden) continue;

                    const cs = doc.defaultView.getComputedStyle(el);
                    const rawFillOp = parseFloat(cs.fillOpacity || '1');
                    const fillOpacity = isNaN(rawFillOp) ? 1.0 : rawFillOp;
                    const rawStrokeOp = parseFloat(cs.strokeOpacity || '1');
                    const strokeOpacity = isNaN(rawStrokeOp) ? 1.0 : rawStrokeOp;
                    const fillInvisible = (cs.fill === 'none' || cs.fill === 'transparent' || cs.fill === 'rgba(0, 0, 0, 0)' || fillOpacity <= 0.05);
                    const strokeInvisible = (cs.stroke === 'none' || cs.stroke === 'transparent' || cs.stroke === 'rgba(0, 0, 0, 0)' || strokeOpacity <= 0.05);
                    if (fillInvisible && strokeInvisible) continue;

                    const r = el.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    let bbox = null;
                    try {
                        const b = el.getBBox();
                        bbox = { x: b.x, y: b.y, width: b.width, height: b.height };
                    } catch (e) {}

                    // Check sibling <tspan> overlaps inside this <text>
                    const tspans = Array.from(el.querySelectorAll('tspan')).filter(ts => {
                        if (!(ts.textContent || '').trim()) return false;
                        const tvis = getEffectiveVisAndOpacity(ts);
                        if (tvis.hidden) return false;
                        const tcs = doc.defaultView.getComputedStyle(ts);
                        const tfo = parseFloat(tcs.fillOpacity || '1');
                        if (tcs.fill === 'none' || (!isNaN(tfo) && tfo <= 0.05)) return false;
                        const tr = ts.getBoundingClientRect();
                        return tr.width > 0 && tr.height > 0;
                    });
                    for (let ti = 0; ti < tspans.length; ti++) {
                        const ra = tspans[ti].getBoundingClientRect();
                        for (let tj = ti + 1; tj < tspans.length; tj++) {
                            if (tspans[ti].contains(tspans[tj]) || tspans[tj].contains(tspans[ti])) continue;
                            const rb = tspans[tj].getBoundingClientRect();
                            const ox = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left);
                            const oy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
                            if (ox > 2.0 && oy > 2.0) {
                                tspanOverlaps.push({
                                    a: (tspans[ti].textContent || '').trim().slice(0, 60),
                                    b: (tspans[tj].textContent || '').trim().slice(0, 60),
                                    overlap_x: ox,
                                    overlap_y: oy,
                                    area: ox * oy,
                                });
                            }
                        }
                    }

                    // Find enclosing filled shapes painted before this text node in DOM order
                    const cx = r.left + r.width / 2;
                    const cy = r.top + r.height / 2;
                    const bgRects = [];
                    for (const shapeEl of shapeCandidates) {
                        if (!(el.compareDocumentPosition(shapeEl) & Node.DOCUMENT_POSITION_PRECEDING)) continue;
                        const svis = getEffectiveVisAndOpacity(shapeEl);
                        if (svis.hidden) continue;
                        const scs = doc.defaultView.getComputedStyle(shapeEl);
                        const sfo = parseFloat(scs.fillOpacity || '1');
                        const shapeFillOpacity = isNaN(sfo) ? 1.0 : sfo;
                        if (scs.fill === 'none' || scs.fill === 'transparent' || scs.fill === 'rgba(0, 0, 0, 0)' || shapeFillOpacity <= 0.05) {
                            continue;
                        }
                        const rr = shapeEl.getBoundingClientRect();
                        if (rr.width > 0 && rr.height > 0 && cx >= rr.left && cx <= rr.right && cy >= rr.top && cy <= rr.bottom) {
                            const urlInfo = resolveUrlFill(scs.fill);
                            if (urlInfo && urlInfo.isPattern) continue;
                            bgRects.push({
                                tag: shapeEl.localName,
                                fill: scs.fill,
                                fillOpacity: shapeFillOpacity,
                                opacity: svis.accumOpacity,
                                urlInfo,
                            });
                        }
                    }

                    texts.push({
                        idx,
                        text: txt.slice(0, 100),
                        rect: { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height },
                        bbox,
                        fontSize: parseFloat(cs.fontSize || '12'),
                        fontWeight: parseInt(cs.fontWeight || '400', 10) || 400,
                        fill: cs.fill,
                        fillInvisible,
                        fillUrlInfo: resolveUrlFill(cs.fill),
                        fillOpacity,
                        opacity: vis.accumOpacity,
                        ariaHidden: el.getAttribute('aria-hidden') === 'true',
                        bgRects,
                    });
                }

                // Check frame-0 non-text visual presence too (paths/rects/circles)
                const visibleShapes = Array.from(svg.querySelectorAll('path, rect, circle, line, polygon')).filter(el => {
                    if (el.closest('defs, clipPath, mask, pattern, symbol')) return false;
                    return !getEffectiveVisAndOpacity(el).hidden;
                }).length;

                return {
                    viewBox: vb,
                    svgRect,
                    texts,
                    tspanOverlaps,
                    visibleShapes,
                    scrollWidth: document.documentElement.scrollWidth,
                    innerWidth: window.innerWidth,
                };
            })()"""
        )
        if not data or data.get("error"):
            raise AssertionError(f"Failed inspecting SVG {svg_url_path}: {data}")

        vb = data.get("viewBox")
        if not vb or float(vb.get("width", 0)) <= 0 or float(vb.get("height", 0)) <= 0:
            raise AssertionError(f"Missing or non-positive SVG viewBox in {svg_url_path}: {vb}")

        svg_rect = data["svgRect"]
        clipped: list[dict[str, Any]] = []
        for t in data["texts"]:
            r = t["rect"]
            if (
                r["width"] <= 0
                or r["height"] <= 0
                or r["left"] < svg_rect["left"] - 1.5
                or r["right"] > svg_rect["right"] + 1.5
                or r["top"] < svg_rect["top"] - 1.5
                or r["bottom"] > svg_rect["bottom"] + 1.5
            ):
                clipped.append(t)

        overlaps: list[dict[str, Any]] = list(data.get("tspanOverlaps", []))
        texts = data["texts"]
        for i in range(len(texts)):
            a = texts[i]["rect"]
            for j in range(i + 1, len(texts)):
                b = texts[j]["rect"]
                ox = min(a["right"], b["right"]) - max(a["left"], b["left"])
                oy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
                if ox > 2.0 and oy > 2.0:
                    overlaps.append(
                        {
                            "a": texts[i]["text"],
                            "b": texts[j]["text"],
                            "overlap_x": ox,
                            "overlap_y": oy,
                            "area": ox * oy,
                        }
                    )

        contrast_failures: list[dict[str, Any]] = []
        base_bg = (13.0, 17.0, 23.0)  # #0d1117 GitHub dark
        for t in texts:
            if t.get("ariaHidden") or t.get("fillInvisible"):
                continue

            # Resolve foreground candidates (single color or gradient stops)
            fg_candidates: list[tuple[float, float, float, float]] = []
            fg_url = t.get("fillUrlInfo")
            if fg_url is not None:
                if fg_url.get("unresolved") or not fg_url.get("gradientStops"):
                    contrast_failures.append(
                        {
                            "text": t["text"],
                            "ratio": 0.0,
                            "required": 4.5,
                            "fontSize": t["fontSize"],
                            "fg": t["fill"],
                            "error": f"Unresolved url(#...) fill on SVG text: {t['fill']}",
                        }
                    )
                    continue
                for st in fg_url["gradientStops"]:
                    parsed_st = parse_css_color(st.get("color"))
                    if parsed_st is not None:
                        fg_candidates.append(
                            (parsed_st[0], parsed_st[1], parsed_st[2], parsed_st[3] * float(st.get("opacity", 1.0)))
                        )
            else:
                fg_parsed = parse_css_color(t["fill"])
                if fg_parsed is None:
                    contrast_failures.append(
                        {
                            "text": t["text"],
                            "ratio": 0.0,
                            "required": 4.5,
                            "fontSize": t["fontSize"],
                            "fg": t["fill"],
                            "error": f"Unparseable SVG text fill: {t['fill']}",
                        }
                    )
                    continue
                fg_candidates.append(fg_parsed)

            # Resolve backdrop candidates across any gradient bg shapes (worst-case stop)
            bg_states: list[tuple[float, float, float]] = [base_bg]
            for br in t.get("bgRects", []):
                b_url = br.get("urlInfo")
                shape_alpha_mul = float(br.get("fillOpacity", 1.0)) * float(br.get("opacity", 1.0))
                if b_url is not None:
                    if b_url.get("isPattern"):
                        continue
                    stops = b_url.get("gradientStops") or []
                    if not stops:
                        continue
                    next_states: list[tuple[float, float, float]] = []
                    # Evaluate all gradient stops (including intermediate stops)
                    for prev_bg in bg_states[:16]:
                        for st in stops:
                            bf = parse_css_color(st.get("color"))
                            if bf is not None:
                                a = bf[3] * float(st.get("opacity", 1.0)) * shape_alpha_mul
                                next_states.append(composite_source_over((bf[0], bf[1], bf[2], a), prev_bg))
                    if next_states:
                        bg_states = next_states
                else:
                    bf = parse_css_color(br.get("fill"))
                    if bf is not None:
                        a = bf[3] * shape_alpha_mul
                        bg_states = [
                            composite_source_over((bf[0], bf[1], bf[2], a), prev_bg)
                            for prev_bg in bg_states
                        ]

            is_large = t["fontSize"] >= 24.0 or (t["fontSize"] >= 18.66 and t["fontWeight"] >= 700)
            req = 3.0 if is_large else 4.5
            worst_ratio = float("inf")
            worst_eff_bg = bg_states[0]
            for fg_c in fg_candidates:
                fg_alpha = fg_c[3] * float(t.get("fillOpacity", 1.0)) * float(t.get("opacity", 1.0))
                for eff_bg in bg_states:
                    eff_fg = composite_source_over((fg_c[0], fg_c[1], fg_c[2], fg_alpha), eff_bg)
                    r_val = contrast_ratio(eff_fg, eff_bg)
                    if r_val < worst_ratio:
                        worst_ratio = r_val
                        worst_eff_bg = eff_bg

            if worst_ratio < req:
                contrast_failures.append(
                    {
                        "text": t["text"],
                        "ratio": round(worst_ratio, 2),
                        "required": req,
                        "fontSize": t["fontSize"],
                        "fg": t["fill"],
                        "eff_bg": tuple(round(c, 1) for c in worst_eff_bg),
                    }
                )

        data["clipped"] = clipped
        data["overlaps"] = overlaps
        data["contrast_failures"] = contrast_failures
        return data

    def check_overflow_and_collisions(
        self,
        width: int,
        height: int,
    ) -> dict[str, Any]:
        """Measure horizontal overflow (incl. fixed/clipped leaks) and TreeWalker/Range text collisions."""
        self.set_viewport(width, height)
        result = self.eval_js(
            """(() => {
                const docSW = document.documentElement.scrollWidth;
                const bodySW = document.body ? document.body.scrollWidth : docSW;
                const iw = window.innerWidth;

                const isVisibleEl = (el) => {
                    let cur = el;
                    while (cur && cur.nodeType === 1) {
                        const cs = getComputedStyle(cur);
                        if (cs.display === 'none' || cs.visibility === 'hidden') return false;
                        if (parseFloat(cs.opacity || '1') <= 0.05) return false;
                        if (cur.getAttribute('aria-hidden') === 'true') return false;
                        const r = cur.getBoundingClientRect();
                        if (cs.overflow === 'hidden' && r.width <= 1 && r.height <= 1) return false;
                        // Skip off-viewport translated closed drawers/modals
                        if (cs.position === 'fixed' && (r.right <= 0 || r.left >= iw || r.bottom <= 0)) return false;
                        cur = cur.parentElement;
                    }
                    return true;
                };

                const hasHorizontalScrollAncestor = (el) => {
                    let cur = el.parentElement;
                    while (cur && cur.nodeType === 1 && cur !== document.body && cur !== document.documentElement) {
                        const cs = getComputedStyle(cur);
                        if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll') && cur.scrollWidth > cur.clientWidth + 1) {
                            return true;
                        }
                        cur = cur.parentElement;
                    }
                    return false;
                };

                const overflowLeaks = [];
                // 1. Detect visible position:fixed / position:sticky elements leaking past viewport edges
                for (const el of document.querySelectorAll('body *')) {
                    const cs = getComputedStyle(el);
                    if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
                    if (!isVisibleEl(el)) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    if (r.left >= iw || r.right <= 0 || r.bottom <= 0) continue;
                    if (r.right > iw + 1.5 || r.left < -1.5) {
                        overflowLeaks.push({
                            kind: cs.position + '_edge_overflow',
                            tag: el.tagName.toLowerCase(),
                            text: (el.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 50),
                            left: Math.round(r.left * 10) / 10,
                            right: Math.round(r.right * 10) / 10,
                            innerWidth: iw,
                        });
                    }
                }

                // 2. Detect overflow-x: hidden/clip wrappers clipping visible text-bearing blocks
                for (const wrap of document.querySelectorAll('body *')) {
                    const wcs = getComputedStyle(wrap);
                    if (wcs.overflowX !== 'hidden' && wcs.overflowX !== 'clip') continue;
                    if (wcs.textOverflow === 'ellipsis') continue;
                    if (!isVisibleEl(wrap)) continue;
                    const wr = wrap.getBoundingClientRect();
                    if (wr.width <= 1 || wr.height <= 1) continue;
                    if (wrap.scrollWidth <= wrap.clientWidth + 2) continue;
                    // Check direct text nodes inside wrap first (in case wrap has no child elements)
                    let reportedWrap = false;
                    const wtag = wrap.tagName.toLowerCase();
                    if (!['script', 'style', 'noscript', 'svg', 'canvas', 'template'].includes(wtag) && !wrap.closest('svg, [aria-hidden="true"]')) {
                        for (const tn of wrap.childNodes) {
                            if (tn.nodeType !== 3 || !tn.nodeValue || !tn.nodeValue.trim()) continue;
                            const tr = document.createRange();
                            tr.selectNodeContents(tn);
                            for (const cr of tr.getClientRects()) {
                                if (cr.width <= 0.5 || cr.height <= 0.5) continue;
                                if (cr.right > wr.right + 1.5 || cr.left < wr.left - 1.5) {
                                    overflowLeaks.push({
                                        kind: 'clipped_overflow_hidden',
                                        tag: wtag,
                                        text: tn.nodeValue.replace(/\\s+/g, ' ').trim().slice(0, 50),
                                        childRight: Math.round(cr.right * 10) / 10,
                                        wrapperRight: Math.round(wr.right * 10) / 10,
                                    });
                                    reportedWrap = true;
                                    break;
                                }
                            }
                            if (reportedWrap) break;
                        }
                    }
                    if (reportedWrap) continue;
                    // Check if any visible text-bearing descendant actually extends past wrap's box
                    for (const child of wrap.querySelectorAll('*')) {
                        const ctag = child.tagName.toLowerCase();
                        if (['script', 'style', 'noscript', 'svg', 'canvas', 'template'].includes(ctag)) continue;
                        if (child.closest('svg, [aria-hidden="true"]')) continue;
                        const hasText = Array.from(child.childNodes).some(
                            n => n.nodeType === 3 && n.nodeValue && n.nodeValue.trim().length > 0
                        );
                        if (!hasText) continue;
                        if (!isVisibleEl(child)) continue;
                        const cr = child.getBoundingClientRect();
                        if (cr.width <= 0 || cr.height <= 0) continue;
                        if (cr.right > wr.right + 1.5 || cr.left < wr.left - 1.5) {
                            overflowLeaks.push({
                                kind: 'clipped_overflow_hidden',
                                tag: ctag,
                                text: (child.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 50),
                                childRight: Math.round(cr.right * 10) / 10,
                                wrapperRight: Math.round(wr.right * 10) / 10,
                            });
                            break;
                        }
                    }
                }

                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode(node) {
                            if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
                            const parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;
                            const tag = parent.tagName.toLowerCase();
                            if (['script', 'style', 'noscript', 'svg', 'canvas', 'template'].includes(tag)) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            if (parent.closest('svg, [aria-hidden="true"]')) {
                                return NodeFilter.FILTER_REJECT;
                            }
                            if (!isVisibleEl(parent)) return NodeFilter.FILTER_REJECT;
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );

                const elemIds = new WeakMap();
                let nextId = 1;
                const getElemId = (el) => {
                    if (!elemIds.has(el)) elemIds.set(el, nextId++);
                    return elemIds.get(el);
                };

                const boxes = [];
                let node;
                while ((node = walker.nextNode())) {
                    const parent = node.parentElement;
                    const range = document.createRange();
                    range.selectNodeContents(node);
                    const rects = Array.from(range.getClientRects());
                    const id = getElemId(parent);
                    const snippet = node.nodeValue.replace(/\\s+/g, ' ').trim().slice(0, 60);
                    const inHScroll = hasHorizontalScrollAncestor(parent);
                    for (const r of rects) {
                        if (r.width <= 0.5 || r.height <= 0.5) continue;
                        if (!inHScroll && (r.right > iw + 1.5 || r.left < -1.5)) {
                            overflowLeaks.push({
                                kind: 'text_viewport_overflow',
                                tag: parent.tagName.toLowerCase(),
                                text: snippet,
                                left: Math.round(r.left * 10) / 10,
                                right: Math.round(r.right * 10) / 10,
                                innerWidth: iw,
                            });
                        }
                        boxes.push({
                            elemId: id,
                            tag: parent.tagName.toLowerCase(),
                            text: snippet,
                            left: r.left,
                            top: r.top,
                            right: r.right,
                            bottom: r.bottom,
                            width: r.width,
                            height: r.height,
                        });
                    }
                }
                return { docSW, bodySW, innerWidth: iw, boxes, overflowLeaks };
            })()"""
        )

        boxes = result["boxes"]
        collisions: list[dict[str, Any]] = []
        # Sort by top to sweep efficiently without O(N^2) blowup on large pages
        sorted_boxes = sorted(boxes, key=lambda b: b["top"])
        for i in range(len(sorted_boxes)):
            a = sorted_boxes[i]
            for j in range(i + 1, len(sorted_boxes)):
                b = sorted_boxes[j]
                if b["top"] >= a["bottom"] - 2.0:
                    break
                if a["elemId"] == b["elemId"]:
                    continue
                ox = min(a["right"], b["right"]) - max(a["left"], b["left"])
                oy = min(a["bottom"], b["bottom"]) - max(a["top"], b["top"])
                if ox > 2.0 and oy > 2.0:
                    collisions.append(
                        {
                            "a": f"<{a['tag']}> {a['text']!r}",
                            "b": f"<{b['tag']}> {b['text']!r}",
                            "overlap_x": round(ox, 2),
                            "overlap_y": round(oy, 2),
                        }
                    )

        return {
            "width": width,
            "height": height,
            "doc_scroll_width": result["docSW"],
            "body_scroll_width": result["bodySW"],
            "inner_width": result["innerWidth"],
            "box_count": len(boxes),
            "collisions": collisions,
            "overflow_leaks": result["overflowLeaks"],
        }

    def check_wcag_contrast(self) -> dict[str, Any]:
        """Verify WCAG 2.1 contrast with group-opacity compositing, gradient stops, and CSS Color 4."""
        items = self.eval_js(
            """(() => {
                const results = [];
                const all = document.querySelectorAll('body *');
                for (const el of all) {
                    const tag = el.tagName.toLowerCase();
                    if (['script', 'style', 'noscript', 'svg', 'canvas', 'template'].includes(tag)) continue;
                    if (el.closest('svg, [aria-hidden="true"]')) continue;
                    const hasDirectText = Array.from(el.childNodes).some(
                        n => n.nodeType === 3 && n.nodeValue && n.nodeValue.trim().length > 0
                    );
                    if (!hasDirectText) continue;

                    // Visibility & stacking-group stack walk (element -> root)
                    let cur = el;
                    let visible = true;
                    let accumOpacity = 1.0;
                    const stack = [];
                    while (cur && cur.nodeType === 1) {
                        const cs = getComputedStyle(cur);
                        if (cs.display === 'none' || cs.visibility === 'hidden') { visible = false; break; }
                        const op = parseFloat(cs.opacity || '1');
                        const layerOp = isNaN(op) ? 1.0 : op;
                        accumOpacity *= layerOp;
                        if (accumOpacity <= 0.05) { visible = false; break; }
                        const r = cur.getBoundingClientRect();
                        if (cs.overflow === 'hidden' && r.width <= 1 && r.height <= 1) { visible = false; break; }
                        if (cs.position === 'fixed' && (r.right <= 0 || r.left >= window.innerWidth)) { visible = false; break; }
                        stack.push({
                            bgColor: cs.backgroundColor,
                            bgImage: cs.backgroundImage || 'none',
                            opacity: layerOp,
                        });
                        cur = cur.parentElement;
                    }
                    if (!visible) continue;

                    const er = el.getBoundingClientRect();
                    if (er.width <= 0 || er.height <= 0) continue;

                    const cs = getComputedStyle(el);
                    const isControl = Boolean(el.closest('button, a, input, select, [role="button"], [role="tab"]'));
                    const textSample = Array.from(el.childNodes)
                        .filter(n => n.nodeType === 3)
                        .map(n => n.nodeValue)
                        .join(' ')
                        .replace(/\\s+/g, ' ')
                        .trim()
                        .slice(0, 80);

                    results.push({
                        tag,
                        text: textSample,
                        fg: cs.color,
                        stack: stack.reverse(),  // root-to-element order
                        fontSize: parseFloat(cs.fontSize || '14'),
                        fontWeight: parseInt(cs.fontWeight || '400', 10) || 400,
                        isControl,
                    });
                }
                return results;
            })()"""
        )

        def _prem_over(
            top: tuple[float, float, float, float],
            bot: tuple[float, float, float, float],
        ) -> tuple[float, float, float, float]:
            # Both top and bot are premultiplied (pr, pg, pb, a)
            inv = 1.0 - top[3]
            return (
                top[0] + bot[0] * inv,
                top[1] + bot[1] * inv,
                top[2] + bot[2] * inv,
                top[3] + bot[3] * inv,
            )

        def _to_prem(rgba: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
            a = max(0.0, min(1.0, rgba[3]))
            return (rgba[0] * a, rgba[1] * a, rgba[2] * a, a)

        def _mul_prem(prem: tuple[float, float, float, float], op: float) -> tuple[float, float, float, float]:
            return (prem[0] * op, prem[1] * op, prem[2] * op, prem[3] * op)

        failures: list[dict[str, Any]] = []
        for item in items:
            is_large = item["fontSize"] >= 24.0 or (
                item["fontSize"] >= 18.66 and item["fontWeight"] >= 700
            )
            required = 3.0 if is_large else 4.5

            fg_parsed = parse_css_color(item["fg"])
            if fg_parsed is None:
                failures.append(
                    {
                        "tag": item["tag"],
                        "text": item["text"],
                        "ratio": 0.0,
                        "required": required,
                        "fontSize": item["fontSize"],
                        "fontWeight": item["fontWeight"],
                        "isControl": item["isControl"],
                        "fg": item["fg"],
                        "error": f"Unparseable CSS foreground color: {item['fg']!r}",
                    }
                )
                continue

            # Build per-layer background candidates (handling CSS gradients on transparent/semi-transparent layers)
            stack = item["stack"]
            layer_bg_options: list[list[tuple[float, float, float, float]]] = []
            parse_error: str | None = None
            for layer in stack:
                bg_c = parse_css_color(layer["bgColor"])
                if bg_c is None:
                    parse_error = f"Unparseable CSS background color: {layer['bgColor']!r}"
                    break
                grad_stops = _extract_gradient_stops(layer.get("bgImage"))
                if grad_stops:
                    sampled = list(dict.fromkeys(grad_stops))
                    opts = []
                    for gs in sampled:
                        # backgroundImage paints over backgroundColor in CSS
                        comp = _prem_over(_to_prem(gs), _to_prem(bg_c))
                        opts.append(comp)
                    layer_bg_options.append(opts)
                else:
                    layer_bg_options.append([_to_prem(bg_c)])

            if parse_error is not None:
                failures.append(
                    {
                        "tag": item["tag"],
                        "text": item["text"],
                        "ratio": 0.0,
                        "required": required,
                        "fontSize": item["fontSize"],
                        "fontWeight": item["fontWeight"],
                        "isControl": item["isControl"],
                        "fg": item["fg"],
                        "error": parse_error,
                    }
                )
                continue

            # Evaluate group-opacity subtree combinations (capped to avoid blowup)
            # Represent each branch as list of chosen own_bg_prem per layer
            branches: list[list[tuple[float, float, float, float]]] = [[]]
            for opts in layer_bg_options:
                if len(opts) == 1:
                    for b in branches:
                        b.append(opts[0])
                else:
                    next_branches: list[list[tuple[float, float, float, float]]] = []
                    for b in branches[:16]:
                        for o in opts:
                            next_branches.append(b + [o])
                    branches = next_branches

            fg_prem = _to_prem(fg_parsed)
            canvas_prem = (255.0, 255.0, 255.0, 1.0)
            worst_ratio = float("inf")
            worst_eff_bg: tuple[float, float, float] = (255.0, 255.0, 255.0)

            for branch in branches:
                # Evaluate leaf-up with exact CSS stacking-context group opacity
                bg_acc = (0.0, 0.0, 0.0, 0.0)
                fg_acc = fg_prem
                # At leaf layer n, text sits on top of leaf's own background
                for idx in range(len(stack) - 1, -1, -1):
                    own_bg = branch[idx]
                    op = max(0.0, min(1.0, float(stack[idx]["opacity"])))
                    bg_acc = _mul_prem(_prem_over(bg_acc, own_bg), op)
                    fg_acc = _mul_prem(_prem_over(fg_acc, own_bg), op)
                final_bg = _prem_over(bg_acc, canvas_prem)
                final_fg = _prem_over(fg_acc, canvas_prem)
                eff_bg = (final_bg[0], final_bg[1], final_bg[2])
                eff_fg = (final_fg[0], final_fg[1], final_fg[2])
                r_val = contrast_ratio(eff_fg, eff_bg)
                if r_val < worst_ratio:
                    worst_ratio = r_val
                    worst_eff_bg = eff_bg

            if worst_ratio < required:
                failures.append(
                    {
                        "tag": item["tag"],
                        "text": item["text"],
                        "ratio": round(worst_ratio, 2),
                        "required": required,
                        "fontSize": item["fontSize"],
                        "fontWeight": item["fontWeight"],
                        "isControl": item["isControl"],
                        "fg": item["fg"],
                        "eff_bg": tuple(round(c, 1) for c in worst_eff_bg),
                    }
                )

        return {"checked_count": len(items), "failures": failures}

    # -----------------------------------------------------------------------
    # 4-Layer Opaque-Box DOM Discovery Cascade (Tier 3 & Tier 4)
    # -----------------------------------------------------------------------

    def discover_filter_pills(self) -> list[dict[str, Any]]:
        """Discover category filter buttons/tabs without relying on CSS class names."""
        return self.eval_js(
            """(() => {
                const btns = Array.from(document.querySelectorAll('button, [role="tab"]')).filter(el => {
                    const cs = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 10 && r.height > 10;
                });
                const isFilterLabel = (t) => /^(all|production|backend|ai|systems|data)/i.test(t.trim());
                const groups = new Map();
                for (const b of btns) {
                    const txt = (b.innerText || b.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (!txt || txt.length > 40) continue;
                    const p = b.parentElement;
                    if (!p) continue;
                    const container = (p.tagName === 'LI' && p.parentElement)
                        ? p.parentElement
                        : (b.closest('[role="tablist"], [role="toolbar"]') || p);
                    if (!groups.has(container)) groups.set(container, []);
                    groups.get(container).push({ el: b, text: txt });
                }
                let bestGroup = [];
                for (const [, arr] of groups.entries()) {
                    const matched = arr.filter(x => isFilterLabel(x.text));
                    if (arr.length >= 3 && matched.length >= 2 && arr.length > bestGroup.length) {
                        bestGroup = arr;
                    }
                }
                return bestGroup.map((item, idx) => {
                    const r = item.el.getBoundingClientRect();
                    return {
                        index: idx,
                        text: item.text,
                        ariaPressed: item.el.getAttribute('aria-pressed'),
                        ariaSelected: item.el.getAttribute('aria-selected'),
                        rect: { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height },
                    };
                });
            })()"""
        )

    def click_filter_pill(self, label_substring: str) -> dict[str, Any]:
        """Click the discovered filter pill matching ``label_substring`` via real mouse event."""
        pills = self.discover_filter_pills()
        target = None
        q = label_substring.strip().lower()
        for p in pills:
            if p["text"].strip().lower() == q:
                target = p
                break
        if target is None:
            for p in pills:
                if q in p["text"].strip().lower():
                    target = p
                    break
        if target is None:
            raise AssertionError(
                f"Filter pill matching {label_substring!r} not found in {[p['text'] for p in pills]}"
            )
        # Scroll into view then click via CDP mouse event
        rect = self.eval_js(
            f"""(() => {{
                const btns = Array.from(document.querySelectorAll('button, [role="tab"]'));
                const el = btns.find(b => (b.innerText || '').replace(/\\s+/g, ' ').trim() === {json.dumps(target['text'])} && b.getBoundingClientRect().width > 10);
                if (!el) return null;
                el.scrollIntoView({{block: 'center', inline: 'center'}});
                const r = el.getBoundingClientRect();
                return {{left: r.left, top: r.top, width: r.width, height: r.height}};
            }})()"""
        )
        assert rect is not None, f"Could not re-locate pill {target['text']}"
        self.click_point(rect["left"] + rect["width"] / 2.0, rect["top"] + rect["height"] / 2.0)
        return target

    def discover_project_cards(self) -> list[dict[str, Any]]:
        """Discover visible project cards using semantic + text-anchor containment."""
        return self.eval_js(
            f"""(() => {{
                const projects = {json.dumps(CORE_PROJECT_KEYWORDS)};
                const found = [];
                const candidates = Array.from(document.querySelectorAll(
                    'article, [role="button"], button, a, div[tabindex], div.card, [class*="card"], [data-project], section div, li'
                ));
                for (const [canonical, aliases] of projects) {{
                    let best = null;
                    let bestArea = Infinity;
                    for (const el of candidates) {{
                        if (el.closest('nav, header, [role="dialog"], dialog, [aria-modal="true"]')) continue;
                        const ownerCard = el.closest('article, [tabindex], [data-project]');
                        if (el.tagName === 'DIV' && ownerCard && ownerCard !== el) continue;
                        const cs = getComputedStyle(el);
                        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.05) continue;
                        const r = el.getBoundingClientRect();
                        if (r.width < 180 || r.height < 70 || r.width > 1420 || r.height > 900) continue;
                        const txt = (el.innerText || '').toLowerCase();
                        if (!aliases.some(a => txt.includes(a))) continue;
                        // Ensure card doesn't swallow multiple distinct projects (e.g. grid wrapper)
                        let matchCount = 0;
                        for (const [, otherAliases] of projects) {{
                            if (otherAliases.some(a => txt.includes(a))) matchCount++;
                        }}
                        if (matchCount > 1) continue;
                        const area = r.width * r.height;
                        if (area < bestArea) {{
                            bestArea = area;
                            best = el;
                        }}
                    }}
                    if (best) {{
                        const r = best.getBoundingClientRect();
                        const cs = getComputedStyle(best);
                        found.push({{
                            project: canonical,
                            tag: best.tagName.toLowerCase(),
                            text: (best.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 200),
                            rect: {{left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height}},
                            style: {{
                                opacity: cs.opacity,
                                borderColor: cs.borderColor,
                                boxShadow: cs.boxShadow,
                                backgroundColor: cs.backgroundColor,
                                outlineColor: cs.outlineColor,
                                transform: cs.transform,
                                className: typeof best.className === 'string' ? best.className : '',
                                dataHighlighted: best.getAttribute('data-highlighted') || best.getAttribute('data-active') || best.getAttribute('data-match') || '',
                            }},
                        }});
                    }}
                }}
                return found;
            }})()"""
        )

    def open_project_drawer(self, project_name: str) -> dict[str, Any]:
        """Click a project card (or its explicit inspect trigger) and return the newly visible dialog/drawer."""
        aliases = next(
            (als for cname, als in CORE_PROJECT_KEYWORDS if project_name.lower() in cname.lower()),
            (project_name.lower(),),
        )
        click_rect = self.eval_js(
            f"""(() => {{
                const aliases = {json.dumps(aliases)};
                const projects = {json.dumps(CORE_PROJECT_KEYWORDS)};
                const candidates = Array.from(document.querySelectorAll(
                    'article, [role="button"], button, div[tabindex], div.card, [class*="card"], [data-project], section div, li'
                ));
                let best = null;
                let bestArea = Infinity;
                for (const el of candidates) {{
                    if (el.closest('nav, header, [role="dialog"], dialog, [aria-modal="true"]')) continue;
                    const ownerCard = el.closest('article, [tabindex], [data-project]');
                    if (el.tagName === 'DIV' && ownerCard && ownerCard !== el) continue;
                    const cs = getComputedStyle(el);
                    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.05) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width < 180 || r.height < 70 || r.width > 1420 || r.height > 900) continue;
                    const txt = (el.innerText || '').toLowerCase();
                    if (!aliases.some(a => txt.includes(a))) continue;
                    let matchCount = 0;
                    for (const [, oals] of projects) {{
                        if (oals.some(a => txt.includes(a))) matchCount++;
                    }}
                    if (matchCount > 1) continue;
                    const area = r.width * r.height;
                    if (area < bestArea) {{ bestArea = area; best = el; }}
                }}
                if (!best) return null;
                // Prioritize explicit inspect/detail triggers ([data-inspect], button, [role="button"] ahead of <a>),
                // excluding external/page-navigating <a href> links unless explicitly marked [data-inspect]
                const rawCandidates = Array.from(best.querySelectorAll('[data-inspect], button, [role="button"], a')).filter(b => {{
                    const bcs = getComputedStyle(b);
                    if (bcs.display === 'none' || bcs.visibility === 'hidden') return false;
                    const br = b.getBoundingClientRect();
                    if (br.width <= 16 || br.height <= 12) return false;
                    if (b.hasAttribute('data-inspect')) return true;
                    if (b.tagName === 'A') {{
                        const rawHref = (b.getAttribute('href') || '').trim();
                        if (rawHref && !rawHref.startsWith('#')) return false;
                    }}
                    const label = ((b.innerText || '') + ' ' + (b.getAttribute('aria-label') || '')).trim();
                    return /inspect|detail|open|case|arch|view|explore/i.test(label);
                }});
                const inspectCandidates = rawCandidates.sort((a, b) => {{
                    const rank = (el) => {{
                        if (el.hasAttribute('data-inspect')) return 0;
                        if (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button') return 1;
                        return 2;
                    }};
                    return rank(a) - rank(b);
                }});
                let target = inspectCandidates.length ? inspectCandidates[0] : null;
                if (!target) {{
                    const heading = best.querySelector('h2, h3, h4');
                    if (heading && heading.getBoundingClientRect().width > 20) {{
                        target = heading;
                    }} else {{
                        target = best;
                    }}
                }}
                target.scrollIntoView({{block: 'center', inline: 'center'}});
                const r = target.getBoundingClientRect();
                return {{left: r.left, top: r.top, width: r.width, height: r.height}};
            }})()"""
        )
        assert click_rect is not None, f"Could not find clickable project card for {project_name!r}"
        self.click_point(
            click_rect["left"] + click_rect["width"] / 2.0,
            click_rect["top"] + click_rect["height"] / 2.0,
        )
        time.sleep(0.15)
        dlg = self.discover_open_dialog()
        assert dlg is not None, f"Drawer/dialog did not open after clicking {project_name!r}"
        return dlg

    def discover_open_dialog(self) -> dict[str, Any] | None:
        """Discover a currently open modal/drawer/palette via ARIA landmarks + visibility."""
        return self.eval_js(
            """(() => {
                const isVisibleDlg = (el) => {
                    const cs = getComputedStyle(el);
                    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.05) return false;
                    if (el.getAttribute('aria-hidden') === 'true') return false;
                    const r = el.getBoundingClientRect();
                    if (r.width < 150 || r.height < 100) return false;
                    if (r.right <= 0 || r.left >= window.innerWidth) return false;
                    return true;
                };
                const primary = Array.from(document.querySelectorAll('[role="dialog"], dialog[open], [aria-modal="true"], aside[role="dialog"], aside[aria-modal="true"]'));
                let match = primary.find(isVisibleDlg);
                if (!match) {
                    const fixedAsides = Array.from(document.querySelectorAll('aside')).filter(el => {
                        if (el.closest('nav, header')) return false;
                        const cs = getComputedStyle(el);
                        const zi = parseInt(cs.zIndex || '0', 10);
                        return cs.position === 'fixed' && !isNaN(zi) && zi >= 20 && isVisibleDlg(el);
                    });
                    match = fixedAsides[0] || null;
                }
                if (!match) return null;
                const r = match.getBoundingClientRect();
                return {
                    tag: match.tagName.toLowerCase(),
                    role: match.getAttribute('role') || '',
                    text: (match.innerText || '').replace(/\\s+/g, ' ').trim(),
                    rect: {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height},
                    hasInput: Boolean(match.querySelector('input, [role="searchbox"], [role="combobox"]')),
                };
            })()"""
        )

    def discover_arch_nodes_in_dialog(self) -> list[dict[str, Any]]:
        """Discover clickable architecture graph nodes inside the active open drawer/dialog."""
        return self.eval_js(
            """(() => {
                const isVisibleDlg = (el) => {
                    const cs = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity || '1') > 0.05 && el.getAttribute('aria-hidden') !== 'true' && r.width > 150 && r.height > 100 && r.right > 0 && r.left < window.innerWidth;
                };
                let dlg = Array.from(document.querySelectorAll('[role="dialog"], dialog[open], [aria-modal="true"], aside[role="dialog"], aside[aria-modal="true"]')).find(isVisibleDlg);
                if (!dlg) {
                    dlg = Array.from(document.querySelectorAll('aside')).find(el => {
                        if (el.closest('nav, header')) return false;
                        const cs = getComputedStyle(el);
                        const zi = parseInt(cs.zIndex || '0', 10);
                        return cs.position === 'fixed' && !isNaN(zi) && zi >= 20 && isVisibleDlg(el);
                    }) || null;
                }
                if (!dlg) return [];

                const validNode = (n) => {
                    const cs = getComputedStyle(n);
                    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
                    const txt = (n.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (!txt || txt.length > 50) return false;
                    const r = n.getBoundingClientRect();
                    return r.width >= 20 && r.height >= 14;
                };

                // 1. Prioritize explicit interactive architecture node elements first
                let nodes = Array.from(dlg.querySelectorAll('svg g[tabindex], svg g[role="button"], svg [data-node], button.arch-node, [data-node]')).filter(validNode);

                // 2. Fallback to bare SVG <g> leaf nodes only if zero explicit interactive nodes exist
                if (nodes.length === 0) {
                    nodes = Array.from(dlg.querySelectorAll('svg g')).filter(n => !n.querySelector('g') && validNode(n));
                }
                if (nodes.length === 0) {
                    nodes = Array.from(dlg.querySelectorAll('[role="button"]')).filter(validNode);
                }
                return nodes.map((n, idx) => {
                    const r = n.getBoundingClientRect();
                    return {
                        index: idx,
                        text: (n.textContent || '').replace(/\\s+/g, ' ').trim(),
                        rect: {left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height},
                    };
                });
            })()"""
        )

    def open_command_palette_via_shortcut(self) -> dict[str, Any]:
        """Trigger Ctrl+K (with Meta+K fallback) via CDP Input.dispatchKeyEvent and return palette state."""
        self.press_key("k", "KeyK", 75, modifiers=2)  # Ctrl+K
        time.sleep(0.12)
        pal = self.discover_command_palette()
        if pal is None:
            self.press_key("k", "KeyK", 75, modifiers=4)  # Meta+K
            time.sleep(0.12)
            pal = self.discover_command_palette()
        assert pal is not None, "Command palette did not open on Ctrl+K / Meta+K"
        return pal

    def discover_command_palette(self) -> dict[str, Any] | None:
        """Locate visible command palette modal/overlay dialog and its search input."""
        return self.eval_js(
            """(() => {
                const dialogs = Array.from(document.querySelectorAll('[role="dialog"], dialog[open], [aria-modal="true"]'));
                for (const el of dialogs) {
                    const cs = getComputedStyle(el);
                    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.05) continue;
                    if (el.getAttribute('aria-hidden') === 'true') continue;
                    const inp = el.querySelector('input[type="search"], input[type="text"], input:not([type]), [role="searchbox"], [role="combobox"]');
                    if (!inp) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width < 150 || r.height < 80) continue;
                    const ir = inp.getBoundingClientRect();
                    return {
                        text: (el.innerText || '').replace(/\\s+/g, ' ').trim(),
                        value: inp.value || '',
                        focused: document.activeElement === inp,
                        inputRect: {left: ir.left, top: ir.top, width: ir.width, height: ir.height},
                        rect: {left: r.left, top: r.top, width: r.width, height: r.height},
                    };
                }
                return null;
            })()"""
        )

    @staticmethod
    def _stack_root_js() -> str:
        return """(() => {
            const headingRe = /stack|matrix|skill|pillar/i;
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4'));
            for (const h of headings) {
                const htxt = (h.innerText || '').trim();
                if (!headingRe.test(htxt)) continue;
                const sec = h.closest('section') || h.parentElement;
                if (!sec) continue;
                const btns = sec.querySelectorAll('button, [role="button"]');
                const stxt = (sec.innerText || '').toLowerCase();
                if (btns.length >= 2 && (stxt.includes('python') || stxt.includes('docker') || stxt.includes('java'))) {
                    return sec;
                }
            }
            const sections = Array.from(document.querySelectorAll('section'));
            const fallback = sections.find(s => {
                const txt = (s.innerText || '').toLowerCase();
                return (txt.includes('stack') || txt.includes('matrix') || txt.includes('skill') || txt.includes('pillar'))
                    && txt.includes('python') && txt.includes('docker');
            });
            return fallback || document.body;
        })()"""

    def discover_stack_skills(self) -> list[dict[str, Any]]:
        """Discover interactive skill buttons/chips strictly inside the Stack Matrix section."""
        root_js = self._stack_root_js()
        return self.eval_js(
            f"""(() => {{
                const root = {root_js};
                const btns = Array.from(root.querySelectorAll('button, [role="button"]')).filter(el => {{
                    if (el.closest('[role="dialog"], dialog, [aria-modal="true"]')) return false;
                    const cs = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 16 && r.height > 12;
                }});
                return btns.map((el, idx) => {{
                    const r = el.getBoundingClientRect();
                    return {{
                        index: idx,
                        text: (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim(),
                        ariaPressed: el.getAttribute('aria-pressed'),
                        rect: {{left: r.left, top: r.top, width: r.width, height: r.height}},
                    }};
                }}).filter(b => b.text.length > 0 && b.text.length <= 40);
            }})()"""
        )

    def click_stack_skill(self, skill_name: str) -> dict[str, Any]:
        """Scroll to and click a Stack Matrix skill chip strictly within the Stack Matrix section."""
        skills = self.discover_stack_skills()
        q = skill_name.strip().lower()
        target = next((s for s in skills if s["text"].strip().lower() == q), None)
        if target is None:
            target = next((s for s in skills if q in s["text"].strip().lower()), None)
        assert target is not None, (
            f"Skill {skill_name!r} not found in discovered stack skills {[s['text'] for s in skills]}"
        )
        root_js = self._stack_root_js()
        rect = self.eval_js(
            f"""(() => {{
                const root = {root_js};
                const btns = Array.from(root.querySelectorAll('button, [role="button"]')).filter(el => {{
                    if (el.closest('[role="dialog"], dialog, [aria-modal="true"]')) return false;
                    const cs = getComputedStyle(el);
                    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 16 && r.height > 12 && (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim() === {json.dumps(target['text'])};
                }});
                if (!btns.length) return null;
                const el = btns[0];
                el.scrollIntoView({{block: 'center', inline: 'center'}});
                const r = el.getBoundingClientRect();
                return {{left: r.left, top: r.top, width: r.width, height: r.height}};
            }})()"""
        )
        assert rect is not None, f"Could not re-locate stack skill {skill_name!r}"
        self.click_point(rect["left"] + rect["width"] / 2.0, rect["top"] + rect["height"] / 2.0)
        return target

    def discover_motion_toggle(self) -> dict[str, Any] | None:
        """Discover the Pause/Resume Motion toggle button or switch."""
        return self.eval_js(
            """(() => {
                const btns = Array.from(document.querySelectorAll('button, [role="switch"], [role="button"]'));
                for (const el of btns) {
                    const label = ((el.innerText || '') + ' ' + (el.getAttribute('aria-label') || '')).replace(/\\s+/g, ' ').trim();
                    if (/motion|animation/i.test(label) && /pause|resume|reduce|stop|play|toggle/i.test(label)) {
                        const r = el.getBoundingClientRect();
                        if (r.width > 10 && r.height > 10) {
                            return {
                                text: (el.innerText || '').replace(/\\s+/g, ' ').trim(),
                                ariaLabel: el.getAttribute('aria-label') || '',
                                ariaPressed: el.getAttribute('aria-pressed'),
                                ariaChecked: el.getAttribute('aria-checked'),
                                rect: {left: r.left, top: r.top, width: r.width, height: r.height},
                            };
                        }
                    }
                }
                return null;
            })()"""
        )

    def get_motion_state(self) -> dict[str, Any]:
        """Capture measurable root/body reduced-motion state and CSS animation play states."""
        return self.eval_js(
            """(() => {
                const html = document.documentElement;
                const body = document.body;
                const anims = document.getAnimations ? document.getAnimations() : [];
                const pausedAnims = anims.filter(a => a.playState === 'paused').length;
                return {
                    htmlData: Object.assign({}, html ? html.dataset : {}),
                    bodyData: Object.assign({}, body ? body.dataset : {}),
                    htmlClass: html ? html.className : '',
                    bodyClass: body ? body.className : '',
                    pausedAnims,
                    totalAnims: anims.length,
                };
            })()"""
        )


class CDPHarness:
    """Session-scoped headless Chromium CDP manager."""

    def __init__(self) -> None:
        self._runner = _LoopRunner()
        self._browser: Any = None

    def open(self) -> "CDPHarness":
        self._browser = choreographer.Browser(headless=True)
        if os.name == "nt":
            orig_get_popen_args = self._browser._browser_impl.get_popen_args

            def _win_safe_popen_args() -> dict[str, Any]:
                args = dict(orig_get_popen_args())
                args.setdefault("stdin", subprocess.DEVNULL)
                args.setdefault("stdout", subprocess.DEVNULL)
                return args

            self._browser._browser_impl.get_popen_args = _win_safe_popen_args
        self._runner.run(self._browser.open(), timeout=25.0)
        return self

    def close(self) -> None:
        try:
            if self._browser is not None:
                self._runner.run(self._browser.close(), timeout=15.0)
                self._browser = None
        finally:
            self._runner.stop()

    def new_page(self, viewport: tuple[int, int] = (1440, 900)) -> "_PageContext":
        return _PageContext(self, viewport=viewport)


class _PageContext:
    def __init__(self, harness: CDPHarness, viewport: tuple[int, int]) -> None:
        self.harness = harness
        self.viewport = viewport
        self.session: PageSession | None = None

    def __enter__(self) -> PageSession:
        assert self.harness._browser is not None, "CDPHarness is not opened"
        tab = self.harness._runner.run(self.harness._browser.create_tab("about:blank"), timeout=15.0)
        self.session = PageSession(harness=self.harness, tab=tab, viewport=self.viewport)
        self.harness._runner.run(self.session._async_init(), timeout=15.0)
        return self.session

    def __exit__(self, *_: Any) -> None:
        if self.session is not None and not self.session._closed:
            self.session._closed = True
            try:
                if self.harness._browser is not None:
                    self.harness._runner.run(
                        self.harness._browser.close_tab(self.session.tab.target_id),
                        timeout=10.0,
                    )
            except Exception:
                pass
