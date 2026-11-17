"""Tier 1 E2E Feature Coverage Tests (F1–F7, >=5 parameterized items per feature)."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from typing import Callable

from lxml import etree
import pytest

from tests.cdp_harness import (
    CDPHarness,
    CORE_PROJECT_KEYWORDS,
    LocalSiteServer,
    check_svg_dark_canvas,
    check_svg_size_budget,
    extract_readme_images_metadata,
    extract_readme_links,
    extract_readme_local_assets,
    find_ocean_theme_artifacts,
    find_svg_csp_violations,
    parse_css_color,
    relative_luminance,
    run_python_subprocess,
    validate_svg_xml,
)
from tests.conftest import ATLAS_PLATES

pytestmark = [pytest.mark.e2e, pytest.mark.tier1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# F1: New Visual Concept ("Obsidian Atlas") & Zero-Ocean Departure (9 items)
# ---------------------------------------------------------------------------


def test_readme_zero_ocean_terms(readme_path: Path) -> None:
    """T1-F1-01: README.md contains zero legacy Frutiger Aero / ocean artifacts."""
    text = readme_path.read_text(encoding="utf-8")
    hits = find_ocean_theme_artifacts(text, "README.md")
    assert hits == [], f"Legacy ocean theme artifacts in README.md: {hits}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_readme_svgs_zero_ocean_terms(repo_root: Path, plate: str) -> None:
    """T1-F1-02: Each Obsidian Atlas SVG plate contains zero legacy ocean artifacts."""
    svg_path = repo_root / "assets" / plate
    assert svg_path.exists(), f"Missing expected SVG plate: {svg_path}"
    text = svg_path.read_text(encoding="utf-8")
    hits = find_ocean_theme_artifacts(text, plate)
    assert hits == [], f"Legacy ocean theme artifacts in {plate}: {hits}"


def test_site_zero_ocean_terms(
    index_html_path: Path, live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F1-03: index.html source and rendered DOM contain zero legacy ocean artifacts."""
    assert index_html_path.exists(), f"Missing {index_html_path}"
    raw_hits = find_ocean_theme_artifacts(
        index_html_path.read_text(encoding="utf-8"), "index.html(source)"
    )
    assert raw_hits == [], f"Legacy ocean artifacts in index.html source: {raw_hits}"

    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.assert_clean_runtime()
        dom_text = page.eval_js("document.body ? document.body.innerText : ''") or ""
        dom_hits = find_ocean_theme_artifacts(dom_text, "index.html(DOM)")
        assert dom_hits == [], f"Legacy ocean artifacts in rendered DOM: {dom_hits}"


def test_site_uses_obsidian_atlas_dark_palette(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F1-04: Rendered index.html uses Obsidian Atlas dark canvas (not cyan ocean)."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        bg_vals = page.eval_js(
            """(() => ({
                htmlBg: getComputedStyle(document.documentElement).backgroundColor,
                bodyBg: getComputedStyle(document.body).backgroundColor,
                bodyFg: getComputedStyle(document.body).color,
            }))()"""
        )
        # Prefer bodyBg if opaque, else htmlBg
        chosen = None
        for key in ("bodyBg", "htmlBg"):
            parsed = parse_css_color(bg_vals[key])
            if parsed and parsed[3] > 0.5:
                chosen = (parsed[0], parsed[1], parsed[2])
                break
        assert chosen is not None, f"Neither body nor html has opaque dark background: {bg_vals}"
        lum = relative_luminance(chosen)
        assert lum < 0.05, f"Expected dark-theme canvas (L < 0.05), got RGB {chosen} (L={lum:.3f})"
        # Explicitly verify not legacy ocean cyan/teal (#075077 / #074252 -> B,G >> R)
        assert not (chosen[2] > 90 and chosen[0] < 30), f"Background looks cyan-ocean: {chosen}"
        assert not (
            chosen[2] > 1.5 * max(chosen[0], 1.0)
            and chosen[1] > 1.3 * max(chosen[0], 1.0)
            and chosen[2] > 60
        ), f"Background exhibits cyan/teal ocean hue dominance: {chosen}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_readme_svgs_dark_canvas_native(repo_root: Path, plate: str) -> None:
    """T1-F1-05: Each README SVG uses a dark-theme primary canvas (<rect> >=80% area, L < 0.08) and light ink."""
    svg_path = repo_root / "assets" / plate
    root = validate_svg_xml(svg_path)
    canvas = check_svg_dark_canvas(svg_path)
    assert canvas["backdrop_dark_lums"], (
        f"{plate} lacks a visible primary dark background <rect> (>=80% viewBox area, L < 0.08): {canvas}"
    )
    assert not canvas["backdrop_light_lums"], (
        f"{plate} has non-dark full-canvas background <rect> (L >= 0.08): {canvas['backdrop_light_lums']}"
    )

    fills: list[str] = []
    for el in root.iter():
        for attr in ("fill", "stop-color", "stroke"):
            val = el.get(attr)
            if val and val.startswith("#"):
                fills.append(val)
    style_text = "".join(
        "".join(el.itertext()) for el in root.iter() if isinstance(el.tag, str) and etree.QName(el).localname == "style"
    )
    fills.extend(re.findall(r"#[0-9a-fA-F]{3,8}\b", style_text))

    parsed_rgb = []
    for hx in fills:
        c = parse_css_color(hx)
        if c:
            parsed_rgb.append((c[0], c[1], c[2]))

    light_inks = [c for c in parsed_rgb if relative_luminance(c) > 0.45]
    assert light_inks, f"{plate} lacks high-contrast light ink/accent colors (L > 0.45)"


# ---------------------------------------------------------------------------
# F2: Shared Canonical Profile, Education & Community Coverage (10 items)
# ---------------------------------------------------------------------------


def test_site_renders_core_profile_identity(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F2-01: Live site visibly renders Kerem Kalyoncu, Istanbul, Doğuş University (2023–2027)."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        text = page.eval_js("document.body.innerText") or ""
        norm = text.lower()
        assert "kerem kalyoncu" in norm
        assert "istanbul" in norm or "i̇stanbul" in norm or "İstanbul".lower() in norm
        assert "doğuş" in norm or "dogus" in norm
        assert "2023" in text and "2027" in text


def test_site_renders_community_roles(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F2-02: Live site visibly renders GDG on Campus Doğuş, Huawei AI Academy, BTK, VollSign."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        text = (page.eval_js("document.body.innerText") or "").lower()
        assert "gdg on campus" in text
        assert "design" in text and "social media" in text
        assert "huawei" in text and "ai academy" in text
        assert "btk" in text
        assert "vollsign" in text


@pytest.mark.parametrize("project_name,aliases", CORE_PROJECT_KEYWORDS)
def test_site_renders_all_six_projects(
    live_server: LocalSiteServer,
    cdp_harness: CDPHarness,
    project_name: str,
    aliases: tuple[str, ...],
) -> None:
    """T1-F2-03: Each of the 6 core projects renders visibly in Chromium DOM."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        cards = page.discover_project_cards()
        by_name = {c["project"]: c for c in cards}
        assert project_name in by_name, (
            f"Project {project_name!r} not discovered as visible card; found {list(by_name)}"
        )
        assert len(by_name[project_name]["text"]) >= len(project_name) + 10
        _ = aliases


def test_site_renders_valid_social_and_project_links(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F2-04: Valid https:// links exist for GitHub, LinkedIn, Maritime Watch, Inventra, Restofy, KriptoParaTakip."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        hrefs: list[str] = page.eval_js(
            "Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '')"
        )
        joined = "\n".join(hrefs).lower()
        for expected in (
            "https://github.com/keremkalyoncu",
            "https://www.linkedin.com/in/kerem-kalyoncu",
            "https://keremkalyoncu.github.io/maritime-watch",
            "https://x-etc.online",
            "restofy",
            "kriptoparatakip",
        ):
            assert expected in joined, f"Expected link substring {expected!r} missing in {hrefs}"


def test_readme_contains_profile_projects_and_community(
    repo_root: Path, readme_path: Path
) -> None:
    """T1-F2-05: README.md + embedded SVGs represent identity, university, 6 projects, and community."""
    combined_parts = [readme_path.read_text(encoding="utf-8")]
    for plate in ATLAS_PLATES:
        p = repo_root / "assets" / plate
        assert p.exists(), f"Missing required Atlas SVG plate: {p}"
        root = validate_svg_xml(p)
        combined_parts.append(" ".join(root.itertext()))
    combined = "\n".join(combined_parts).lower()

    for token in (
        "kerem kalyoncu",
        "doğuş",
        "2023",
        "2027",
        "maritime watch",
        "inventra",
        "restofy",
        "shifha",
        "kriptoparatakip",
        "gdg on campus",
        "huawei",
    ):
        assert token in combined, f"Token {token!r} missing from README + Atlas SVGs"
    assert any(ml in combined for ml in ("ml & data lab", "ml-final-odev", "ml data lab", "ml lab"))
    assert "istanbul" in combined or "İstanbul".lower() in combined


# ---------------------------------------------------------------------------
# F3: Pure-SVG README Monograph Plates (XML, CSP, Sizes) (13 items)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_xml_well_formed(repo_root: Path, plate: str) -> None:
    """T1-F3-01: SVG plate parses strictly as valid SVG/XML with viewBox."""
    svg_path = repo_root / "assets" / plate
    root = validate_svg_xml(svg_path)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_csp_no_disallowed_elements(repo_root: Path, plate: str) -> None:
    """T1-F3-02: SVG contains zero <script>, <foreignObject>, <iframe>, <object>, <embed>, <audio>, <video>."""
    svg_path = repo_root / "assets" / plate
    violations = [v for v in find_svg_csp_violations(svg_path) if "Disallowed element" in v]
    assert violations == [], f"Disallowed elements in {plate}: {violations}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_csp_no_event_handlers_or_external_urls(repo_root: Path, plate: str) -> None:
    """T1-F3-03: SVG contains zero on* handlers, javascript: URIs, @import, or external URLs."""
    svg_path = repo_root / "assets" / plate
    violations = [v for v in find_svg_csp_violations(svg_path) if "Disallowed element" not in v]
    assert violations == [], f"CSP/URL violations in {plate}: {violations}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_individual_file_size_under_150kb(repo_root: Path, plate: str) -> None:
    """T1-F3-04: Each README SVG plate is > 1 KB and < 150 KB."""
    svg_path = repo_root / "assets" / plate
    stats = check_svg_size_budget([svg_path], max_each_bytes=150 * 1024, max_total_bytes=400 * 1024)
    assert stats[plate] > 1024, f"{plate} unexpectedly tiny ({stats[plate]} bytes)"


def test_svg_total_size_under_400kb(atlas_svg_paths: list[Path]) -> None:
    """T1-F3-05: Combined size of all README SVG plates is < 400 KB."""
    stats = check_svg_size_budget(
        atlas_svg_paths, max_each_bytes=150 * 1024, max_total_bytes=400 * 1024
    )
    assert stats["total"] < 400 * 1024


# ---------------------------------------------------------------------------
# F4: README.md Integration & Asset Integrity (5 items)
# ---------------------------------------------------------------------------


def test_readme_references_obsidian_atlas_svgs(readme_path: Path) -> None:
    """T1-F4-01: README.md references the 3 Obsidian Atlas SVG plates and zero legacy SVGs."""
    local_assets = extract_readme_local_assets(readme_path)
    names = [p.name for p in local_assets]
    for plate in ATLAS_PLATES:
        assert plate in names, f"README.md missing reference to {plate}; found {names}"
    assert not any("kerem-living-world" in n for n in names)


def test_readme_all_local_asset_paths_resolve(readme_path: Path) -> None:
    """T1-F4-02: Every local image asset referenced in README.md exists, is a regular file, and is non-empty."""
    local_assets = extract_readme_local_assets(readme_path)
    assert len(local_assets) >= 3
    for asset in local_assets:
        assert asset.exists(), f"Broken README local asset link: {asset}"
        assert asset.is_file(), f"README local asset path is not a file: {asset}"
        assert asset.stat().st_size > 0, f"Empty README local asset: {asset}"


def test_readme_links_to_interactive_companion_site(readme_path: Path) -> None:
    """T1-F4-03: README.md links explicitly to the interactive companion site."""
    links = extract_readme_links(readme_path)
    assert any("keremkalyoncu.github.io/keremkalyoncu" in l.lower() for l in links), (
        f"Companion site link missing in README.md links: {links}"
    )


def test_readme_svg_alt_text_non_empty(readme_path: Path) -> None:
    """T1-F4-04: Every local SVG image in README.md has descriptive alt text (len >= 10)."""
    imgs = [
        i
        for i in extract_readme_images_metadata(readme_path)
        if i["is_local"]
        and i["kind"] in ("markdown", "html")
        and i["clean_src"].lower().endswith(".svg")
    ]
    assert len(imgs) >= 3
    for img in imgs:
        assert len(img["alt"]) >= 10, f"Image {img['src']} lacks descriptive alt text: {img['alt']!r}"


class _TagBalanceParser(HTMLParser):
    def __init__(self, tracked: set[str]) -> None:
        super().__init__()
        self.tracked = tracked
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in self.tracked:
            self.stack.append(t)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self.tracked:
            if not self.stack or self.stack[-1] != t:
                self.errors.append(f"Mismatched closing </{t}> (stack={self.stack})")
            else:
                self.stack.pop()


def test_readme_no_broken_html_tags(readme_path: Path) -> None:
    """T1-F4-05: README.md HTML wrapper tags are balanced/properly nested and free of placeholders."""
    text = readme_path.read_text(encoding="utf-8")
    for placeholder in ("{{", "}}", "TODO", "TBD"):
        assert placeholder not in text, f"Unresolved placeholder {placeholder!r} in README.md"
    parser = _TagBalanceParser({"details", "summary", "div", "a"})
    parser.feed(text)
    parser.close()
    assert not parser.errors, f"Malformed HTML tag nesting in README.md: {parser.errors}"
    assert not parser.stack, f"Unclosed HTML tags in README.md: {parser.stack}"


# ---------------------------------------------------------------------------
# F5: Reproducible CLI Generation & Zero-CDN Bundle (5 items)
# ---------------------------------------------------------------------------


def test_build_readme_svgs_cli_exits_zero(tmp_repo_factory: Callable[..., Path]) -> None:
    """T1-F5-01: python source/build_readme_svgs.py exits 0 with clean stderr in isolated copy."""
    work = tmp_repo_factory("cli_svgs", clean_outputs=True)
    script = work / "source" / "build_readme_svgs.py"
    assert script.exists(), "source/build_readme_svgs.py does not exist yet"
    for plate in ATLAS_PLATES:
        assert not (work / "assets" / plate).exists()
    proc = run_python_subprocess(
        [sys.executable, "source/build_readme_svgs.py"],
        cwd=work,
        timeout=30,
    )
    assert proc.returncode == 0, f"build_readme_svgs.py failed:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"
    assert "Traceback" not in proc.stderr
    for plate in ATLAS_PLATES:
        assert (work / "assets" / plate).exists()


def test_build_site_cli_exits_zero(tmp_repo_factory: Callable[..., Path]) -> None:
    """T1-F5-02: python source/build_site.py exits 0 with clean stderr in isolated copy."""
    work = tmp_repo_factory("cli_site", clean_outputs=True)
    script = work / "source" / "build_site.py"
    assert script.exists(), "source/build_site.py does not exist yet"
    assert not (work / "index.html").exists()
    proc = run_python_subprocess(
        [sys.executable, "source/build_site.py"],
        cwd=work,
        timeout=30,
    )
    assert proc.returncode == 0, f"build_site.py failed:\nSTDOUT:{proc.stdout}\nSTDERR:{proc.stderr}"
    assert "Traceback" not in proc.stderr
    assert (work / "index.html").exists()


def test_build_readme_svgs_reproducible_determinism(
    repo_root: Path, tmp_repo_factory: Callable[..., Path]
) -> None:
    """T1-F5-03: Running build_readme_svgs.py twice is byte-identical and matches committed outputs."""
    work = tmp_repo_factory("det_svgs", clean_outputs=True)
    for plate in ATLAS_PLATES:
        assert not (work / "assets" / plate).exists()
    for run_idx in range(2):
        proc = run_python_subprocess(
            [sys.executable, "source/build_readme_svgs.py"],
            cwd=work,
            timeout=30,
        )
        assert proc.returncode == 0, proc.stderr
        for plate in ATLAS_PLATES:
            assert (work / "assets" / plate).exists(), f"Generator did not write {plate}"
        if run_idx == 0:
            run1_hashes = {
                plate: _sha256(work / "assets" / plate) for plate in ATLAS_PLATES
            }
            run1_hashes["README.md"] = _sha256(work / "README.md")
        else:
            for plate in ATLAS_PLATES:
                assert _sha256(work / "assets" / plate) == run1_hashes[plate], f"Non-deterministic {plate}"
            assert _sha256(work / "README.md") == run1_hashes["README.md"], "Non-deterministic README.md"

    for plate in ATLAS_PLATES:
        committed = repo_root / "assets" / plate
        assert committed.exists(), f"Missing committed {committed}"
        assert _sha256(committed) == run1_hashes[plate], f"Committed {plate} differs from generator output"
    assert _sha256(repo_root / "README.md") == run1_hashes["README.md"], "Committed README.md differs from generator output"


def test_build_site_reproducible_determinism(
    repo_root: Path, tmp_repo_factory: Callable[..., Path]
) -> None:
    """T1-F5-04: Running build_site.py twice is byte-identical, matches index.html, and leaves README.md untouched."""
    work = tmp_repo_factory("det_site", clean_outputs=True)
    assert not (work / "index.html").exists()
    readme_file = work / "README.md"
    readme_file.write_text("# Sentinel README\nDo not clobber.\n", encoding="utf-8")
    sentinel_hash = _sha256(readme_file)

    hashes: list[str] = []
    for _ in range(2):
        proc = run_python_subprocess(
            [sys.executable, "source/build_site.py"],
            cwd=work,
            timeout=30,
        )
        assert proc.returncode == 0, proc.stderr
        assert (work / "index.html").exists(), "build_site.py did not generate index.html"
        hashes.append(_sha256(work / "index.html"))
        assert _sha256(readme_file) == sentinel_hash, "build_site.py unexpectedly overwrote README.md"

    assert hashes[0] == hashes[1], "build_site.py output is non-deterministic across runs"
    committed_index = repo_root / "index.html"
    assert committed_index.exists()
    assert _sha256(committed_index) == hashes[0], "Committed index.html differs from build_site.py output"


def test_index_html_zero_external_cdn_dependencies(
    index_html_path: Path, live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F5-05: index.html has zero external CDN scripts/stylesheets and fires zero external requests."""
    html = index_html_path.read_text(encoding="utf-8")
    assert not re.search(r"""<script[^>]+src\s*=\s*["'](?:https?:)?//""", html, re.IGNORECASE)
    assert not re.search(r"""<link[^>]+href\s*=\s*["'](?:https?:)?//""", html, re.IGNORECASE)
    assert "fonts.googleapis.com" not in html.lower()
    assert "fonts.gstatic.com" not in html.lower()

    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        assert page.external_requests() == [], f"External requests fired on load: {page.external_requests()}"


# ---------------------------------------------------------------------------
# F6: Interactive Companion Site Load & Readability (5 items)
# ---------------------------------------------------------------------------


def test_site_loads_with_zero_console_errors(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F6-01: index.html produces 0 console.error / console.assert messages."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        assert page.console_errors == []
        assert page.log_errors == []


def test_site_loads_with_zero_uncaught_exceptions(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F6-02: index.html produces 0 uncaught JS runtime exceptions."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        assert page.js_exceptions == []


def test_site_loads_with_zero_network_failures(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F6-03: index.html produces 0 network failures or HTTP >=400 errors."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        assert page.network_failures == []
        assert page.http_errors == []


def test_site_has_meaningful_title_and_five_chapters(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F6-04: index.html has meaningful title and structured 5-chapter narrative."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        info = page.eval_js(
            """(() => ({
                title: document.title || '',
                sections: document.querySelectorAll('main section, section').length,
                bodyText: document.body ? document.body.innerText : '',
            }))()"""
        )
        assert len(info["title"].strip()) >= 8
        assert "kerem.aero" not in info["title"].lower()
        assert info["sections"] >= 5, f"Expected >=5 narrative sections, found {info['sections']}"
        chapters_found = sum(1 for num in ("01", "02", "03", "04", "05") if num in info["bodyText"])
        assert chapters_found >= 4, f"Expected numbered monograph chapters 01..05, found {chapters_found}"


def test_site_renders_non_empty_canvas_or_svg_visuals(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F6-05: Canvas2D and inline SVG diagrams render with non-zero dimensions."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        stats = page.eval_js(
            """(() => {
                const svgs = Array.from(document.querySelectorAll('svg')).filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                }).length;
                const canvases = Array.from(document.querySelectorAll('canvas')).filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                }).length;
                return { svgs, canvases };
            })()"""
        )
        assert stats["svgs"] >= 6, f"Expected >=6 visible inline SVGs (e.g. project micro-diagrams), got {stats}"
        assert stats["canvases"] >= 1, f"Expected >=1 visible Canvas2D coordinate field, got {stats}"


# ---------------------------------------------------------------------------
# F7: Interactive Controls Present (5 items)
# ---------------------------------------------------------------------------


def test_category_filter_controls_present(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F7-01: Category filter pills (All + category filters) are visible."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        pills = page.discover_filter_pills()
        assert len(pills) >= 3, f"Expected >=3 filter pills, found {pills}"
        labels = [p["text"].lower() for p in pills]
        assert any("all" in l for l in labels), f"Missing 'All' filter pill in {labels}"


def test_project_cards_have_interactive_inspection_affordance(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F7-02: All 6 project cards are discoverable and interactive."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        cards = page.discover_project_cards()
        assert len(cards) == 6, f"Expected 6 discoverable project cards, found {[c['project'] for c in cards]}"


def test_command_palette_trigger_present(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F7-03: Command palette trigger or Ctrl+K shortcut opens palette dialog."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        pal = page.open_command_palette_via_shortcut()
        assert pal is not None and pal["rect"]["width"] > 150
        page.press_key("Escape", "Escape", 27)


def test_stack_matrix_skills_present(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F7-04: Interactive Stack Matrix displays 4 pillars and clickable skill chips."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        skills = page.discover_stack_skills()
        labels = {s["text"].lower() for s in skills}
        for required in ("python", "java", "react", "docker", "postgresql"):
            assert any(required in lbl for lbl in labels), (
                f"Skill {required!r} missing in Stack Matrix skills: {sorted(labels)}"
            )


def test_motion_pause_control_present(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T1-F7-05: A Pause/Resume Motion control is visibly rendered and interactive."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        ctrl = page.discover_motion_toggle()
        assert ctrl is not None, "Pause Motion toggle button/switch not found"
