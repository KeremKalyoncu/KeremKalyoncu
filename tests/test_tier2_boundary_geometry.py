"""Tier 2 E2E Boundary, Geometry, Multi-Viewport Layout & WCAG Contrast Tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Callable
from urllib.parse import quote

import pytest

from tests.cdp_harness import (
    CDPHarness,
    LocalSiteServer,
    extract_readme_links,
    extract_readme_local_assets,
    parse_svg_viewbox,
    run_python_subprocess,
)
from tests.conftest import ATLAS_PLATES, VIEWPORTS

pytestmark = [pytest.mark.e2e, pytest.mark.tier2]


# ---------------------------------------------------------------------------
# F1: Contrast & Theme Boundaries (11 items)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_site_body_text_wcag_aa_contrast(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F1-01: Normal text (including normal-size button/link text) achieves >= 4.5:1 WCAG AA contrast."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        wcag = page.check_wcag_contrast()
        assert wcag["checked_count"] > 0, f"Zero visible text nodes evaluated for contrast at {w}x{h}"
        normal_failures = [f for f in wcag["failures"] if f["required"] >= 4.5]
        assert normal_failures == [], f"WCAG normal-text contrast failures at {w}x{h}: {normal_failures}"


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_site_large_headings_and_controls_wcag_contrast(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F1-02: Large headings (>=24px or >=18.66px bold) achieve >= 3.0:1 WCAG contrast across viewports."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        wcag = page.check_wcag_contrast()
        assert wcag["checked_count"] > 0, f"Zero visible text nodes evaluated for contrast at {w}x{h}"
        large_failures = [f for f in wcag["failures"] if f["required"] < 4.5]
        assert large_failures == [], f"WCAG large-text contrast failures at {w}x{h}: {large_failures}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_text_elements_dark_theme_contrast(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, plate: str
) -> None:
    """T2-F1-03: Visible SVG <text> nodes achieve WCAG contrast against local backdrop on #0d1117."""
    with cdp_harness.new_page((880, 900)) as page:
        res = page.inspect_svg_host(live_server.base_url, f"/assets/{plate}", width=880)
        page.assert_clean_runtime()
        assert res["contrast_failures"] == [], (
            f"SVG text contrast failures in {plate}: {res['contrast_failures']}"
        )


# ---------------------------------------------------------------------------
# F2: Content & Viewport Completeness Boundaries (6 items)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_all_projects_visible_above_zero_bbox(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F2-01: All 6 core projects render with non-collapsed dimensions (>=200x80) on every viewport."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        cards = page.discover_project_cards()
        assert len(cards) == 6, f"Expected 6 cards at {w}x{h}, got {[c['project'] for c in cards]}"
        for card in cards:
            r = card["rect"]
            assert r["width"] >= 200 and r["height"] >= 80, (
                f"Card {card['project']} collapsed at {w}x{h}: {r}"
            )


def test_supporting_repos_and_ats_details_accessible(
    repo_root: Path, live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F2-02: Supporting repos are accessible and hero section does not bloat above the fold."""
    combined = (repo_root / "README.md").read_text(encoding="utf-8") + "\n" + (
        repo_root / "index.html"
    ).read_text(encoding="utf-8")
    assert any(
        repo in combined
        for repo in (
            "Gelismis_Kutuphane_Sistemi",
            "FonDedektifi",
            "Envanter-Stok-Takibi",
            "Benzin_Istasyonu_Otamasyon",
        )
    ), "Supporting repositories missing from README.md / index.html"

    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        hero_h = page.eval_js(
            """(() => {
                const hero = document.querySelector('main section, section');
                return hero ? hero.getBoundingClientRect().height : 0;
            })()"""
        )
        assert 200 <= hero_h <= 1.5 * 900, f"Hero height {hero_h}px outside [200, 1350] above-fold bound"


def test_unicode_turkish_diacritics_preserved(
    repo_root: Path, live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F2-03: Turkish diacritics (Doğuş, Türkiye, İstanbul) render cleanly without replacement glyphs."""
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "\ufffd" not in readme_text

    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        dom_text = page.eval_js("document.body.innerText") or ""
        assert "\ufffd" not in dom_text, "Unicode replacement glyph U+FFFD found in site DOM"
        assert "Doğuş" in dom_text
        assert "Türkiye" in dom_text
        assert "İstanbul" in dom_text or "Istanbul" in dom_text


# ---------------------------------------------------------------------------
# F3: SVG #0d1117 @ 880px Geometry & BVA (12 items)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_viewbox_width_880_and_non_zero_height(repo_root: Path, plate: str) -> None:
    """T2-F3-01: Each SVG viewBox is 0 0 880 H with 200 < H <= 2200."""
    vx, vy, vw, vh = parse_svg_viewbox(repo_root / "assets" / plate)
    assert vx == 0 and vy == 0
    assert vw == 880, f"{plate} viewBox width expected 880, got {vw}"
    assert 200 < vh <= 2200, f"{plate} viewBox height {vh} outside (200, 2200]"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_text_no_clipping_on_0d1117_880px(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, plate: str
) -> None:
    """T2-F3-02: Zero visible <text> elements clip outside [0, 880]x[0, H] on #0d1117."""
    with cdp_harness.new_page((880, 900)) as page:
        res = page.inspect_svg_host(live_server.base_url, f"/assets/{plate}", width=880)
        assert abs(res["svgRect"]["width"] - 880) <= 1.5
        assert res["clipped"] == [], f"Clipped <text> elements in {plate}: {res['clipped']}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_text_no_overlapping_labels_on_0d1117_880px(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, plate: str
) -> None:
    """T2-F3-03: Zero pairwise overlapping <text> labels inside each SVG plate."""
    with cdp_harness.new_page((880, 900)) as page:
        res = page.inspect_svg_host(live_server.base_url, f"/assets/{plate}", width=880)
        assert res["overlaps"] == [], f"Overlapping <text> pairs in {plate}: {res['overlaps']}"


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_svg_frame0_complete_visibility(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, plate: str
) -> None:
    """T2-F3-04: At t=0 under reduced-motion, primary SVG text and shapes are immediately visible."""
    with cdp_harness.new_page((880, 900)) as page:
        res = page.inspect_svg_host(
            live_server.base_url, f"/assets/{plate}", width=880, reduced_motion=True
        )
        assert len(res["texts"]) >= 3, f"{plate} has too few visible frame-0 text nodes: {len(res['texts'])}"
        assert res["visibleShapes"] >= 5, f"{plate} lacks visible frame-0 vector geometry"


# ---------------------------------------------------------------------------
# F4: README Boundary Cases (7 items)
# ---------------------------------------------------------------------------


def test_readme_renders_cleanly_in_github_markdown_width_880px(
    readme_path: Path, repo_root: Path, live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F4-01: Stacked README SVGs fit within GitHub's 880px column with zero horizontal overflow."""
    local_assets = extract_readme_local_assets(readme_path)
    svg_srcs = [
        "/" + p.relative_to(repo_root).as_posix()
        for p in local_assets
        if p.suffix.lower() == ".svg"
    ]
    assert len(svg_srcs) >= 3
    stack_url = f"{live_server.base_url}/__e2e_svg_stack__?srcs={quote(','.join(svg_srcs), safe='/,')}&w=880&bg=%230d1117"
    with cdp_harness.new_page((880, 900)) as page:
        page.goto(stack_url, settle_ms=250)
        page.assert_clean_runtime()
        dims = page.eval_js("({sw: document.documentElement.scrollWidth, iw: window.innerWidth})")
        assert dims["sw"] <= 880, f"README SVG stack overflowed 880px width: {dims}"


def test_readme_total_markdown_size_practical(readme_path: Path) -> None:
    """T2-F4-02: README.md size is practical (< 20 KB)."""
    sz = readme_path.stat().st_size
    assert 500 <= sz < 20 * 1024, f"README.md size {sz} bytes outside [500, 20480)"


def test_readme_no_duplicate_or_dead_anchors(readme_path: Path, repo_root: Path) -> None:
    """T2-F4-03: All links in README.md are non-empty valid URLs, valid anchors, or existing repo paths."""
    readme_text = readme_path.read_text(encoding="utf-8")
    links = extract_readme_links(readme_path)
    assert links, "README.md has zero links"

    # Build valid internal GitHub heading slugs + HTML id/name anchors
    anchors: set[str] = {"top", "readme"}
    for m_id in re.finditer(r"""\b(?:id|name)\s*=\s*(?:"([^"]+)"|'([^']+)')""", readme_text, re.I):
        anchors.add((m_id.group(1) or m_id.group(2) or "").strip().lower())
    for m_h in re.finditer(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", readme_text, re.MULTILINE):
        raw_h = re.sub(r"[`*_\[\]()]", "", m_h.group(1)).strip().lower()
        slug = re.sub(r"[^\w\s-]", "", raw_h, flags=re.UNICODE).replace(" ", "-")
        if slug:
            anchors.add(slug)

    for href in links:
        assert href, f"Empty anchor/href in README.md: {href!r}"
        if href.startswith("#"):
            frag = href[1:].strip().lower()
            assert frag and frag in anchors, f"Dead internal anchor {href!r} in README.md (known={sorted(anchors)})"
        elif href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:"):
            assert len(href) > 10
        else:
            target = (repo_root / href.split("#", 1)[0].split("?", 1)[0]).resolve()
            assert target.exists(), f"Broken relative README link: {href}"


def test_readme_badge_or_cta_links_present(readme_path: Path) -> None:
    """T2-F4-04: GitHub, LinkedIn, and Companion Site CTAs exist in README.md."""
    joined = "\n".join(extract_readme_links(readme_path)).lower()
    assert "github.com/keremkalyoncu" in joined
    assert "linkedin.com/in/kerem-kalyoncu" in joined
    assert "keremkalyoncu.github.io/keremkalyoncu" in joined


@pytest.mark.parametrize("plate", ATLAS_PLATES)
def test_readme_svg_aspect_ratios_within_bounds(repo_root: Path, plate: str) -> None:
    """T2-F4-05: Each README SVG plate aspect ratio H/880 is within [0.25, 2.5]."""
    _, _, vw, vh = parse_svg_viewbox(repo_root / "assets" / plate)
    ratio = vh / vw
    assert 0.25 <= ratio <= 2.5, f"{plate} aspect ratio {ratio:.2f} outside [0.25, 2.5]"


# ---------------------------------------------------------------------------
# F5: CLI Execution & Contract Boundaries (5 items)
# ---------------------------------------------------------------------------


def test_build_site_works_from_source_subdir_cwd(tmp_repo_factory: Callable[..., Path]) -> None:
    """T2-F5-01: python build_site.py succeeds when invoked with cwd=repo/source."""
    work = tmp_repo_factory("cwd_site", clean_outputs=True)
    assert not (work / "index.html").exists()
    proc = run_python_subprocess(
        [sys.executable, "build_site.py"],
        cwd=work / "source",
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert (work / "index.html").exists()


def test_build_readme_svgs_works_from_source_subdir_cwd(
    tmp_repo_factory: Callable[..., Path]
) -> None:
    """T2-F5-02: python build_readme_svgs.py succeeds when invoked with cwd=repo/source."""
    work = tmp_repo_factory("cwd_svgs", clean_outputs=True)
    for plate in ATLAS_PLATES:
        assert not (work / "assets" / plate).exists()
    proc = run_python_subprocess(
        [sys.executable, "build_readme_svgs.py"],
        cwd=work / "source",
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    for plate in ATLAS_PLATES:
        assert (work / "assets" / plate).exists()


def test_build_site_does_not_clobber_readme(tmp_repo_factory: Callable[..., Path]) -> None:
    """T2-F5-03: build_site.py leaves README.md byte-for-byte untouched."""
    work = tmp_repo_factory("no_clobber", clean_outputs=True)
    readme = work / "README.md"
    readme.write_text("# Custom Sentinel\n", encoding="utf-8")
    before = hashlib.sha256(readme.read_bytes()).hexdigest()
    proc = run_python_subprocess(
        [sys.executable, "source/build_site.py"],
        cwd=work,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert (work / "index.html").exists()
    after = hashlib.sha256(readme.read_bytes()).hexdigest()
    assert before == after, "build_site.py clobbered README.md"


def test_generated_index_html_size_practical(index_html_path: Path) -> None:
    """T2-F5-04: index.html file size is > 10 KB and < 1.5 MB."""
    sz = index_html_path.stat().st_size
    assert 10 * 1024 < sz < 1536 * 1024, f"index.html size {sz} bytes outside (10KB, 1.5MB)"


def test_profile_spec_imports_cleanly_and_exposes_contracts(repo_root: Path) -> None:
    """T2-F5-05: source.profile_spec exposes required Interface Contract constants via subprocess."""
    code = (
        "import json, source.profile_spec as s; "
        "assert isinstance(s.PALETTE, dict) and len(s.PALETTE) >= 10; "
        "assert isinstance(s.PROFILE, dict) and 'Kerem' in s.PROFILE['name']; "
        "assert isinstance(s.PROJECTS, list) and len(s.PROJECTS) >= 6; "
        "assert isinstance(s.TIMELINE, list) and len(s.TIMELINE) >= 4; "
        "assert isinstance(s.TECH_PILLARS, list) and len(s.TECH_PILLARS) == 4; "
        "assert isinstance(s.SUPPORTING_REPOS, list) and len(s.SUPPORTING_REPOS) >= 3; "
        "print(json.dumps({'projects': len(s.PROJECTS), 'pillars': len(s.TECH_PILLARS)}))"
    )
    proc = run_python_subprocess(
        [sys.executable, "-c", code],
        cwd=repo_root,
        timeout=15,
    )
    assert proc.returncode == 0, f"profile_spec contract check failed: {proc.stderr}"
    payload = json.loads(proc.stdout.strip())
    assert payload["projects"] >= 6 and payload["pillars"] == 4


# ---------------------------------------------------------------------------
# F6: 4-Viewport Layout, Overflow & Font Readability Boundaries (12 items)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_site_zero_horizontal_overflow(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F6-01: Zero horizontal overflow (and responsive viewport meta width) across all 4 viewports."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        res = page.check_overflow_and_collisions(w, h)
        assert res["inner_width"] == w, (
            f"Expected responsive innerWidth == {w} (missing <meta name='viewport'>?), got {res['inner_width']}"
        )
        assert res["doc_scroll_width"] <= res["inner_width"] + 1, (
            f"Horizontal overflow at {w}x{h}: docSW={res['doc_scroll_width']}, innerW={res['inner_width']}"
        )
        assert res["body_scroll_width"] <= res["inner_width"] + 1, (
            f"Body horizontal overflow at {w}x{h}: bodySW={res['body_scroll_width']}, innerW={res['inner_width']}"
        )
        assert res["overflow_leaks"] == [], (
            f"Fixed/clipped horizontal overflow leaks at {w}x{h}: {res['overflow_leaks']}"
        )


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_site_zero_unintended_text_collisions(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F6-02: Zero unintended text bounding-box collisions across all 4 viewports."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        res = page.check_overflow_and_collisions(w, h)
        assert res["box_count"] >= 20
        assert res["collisions"] == [], f"Text collisions at {w}x{h}: {res['collisions']}"


@pytest.mark.parametrize("viewport", VIEWPORTS, ids=[f"{w}x{h}" for w, h in VIEWPORTS])
def test_site_minimum_readable_font_sizes(
    live_server: LocalSiteServer, cdp_harness: CDPHarness, viewport: tuple[int, int]
) -> None:
    """T2-F6-03: Primary paragraphs >= 13px and visible text >= 10px across all 4 viewports."""
    w, h = viewport
    with cdp_harness.new_page((w, h)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.set_viewport(w, h)
        too_small = page.eval_js(
            """(() => {
                const bad = [];
                for (const el of document.querySelectorAll('p, li, span, a, button')) {
                    if (el.closest('svg, [aria-hidden="true"]')) continue;
                    const cs = getComputedStyle(el);
                    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity || '1') <= 0.05) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    const hasText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.nodeValue.trim().length > 0);
                    if (!hasText) continue;
                    const fs = parseFloat(cs.fontSize || '14');
                    const tag = el.tagName.toLowerCase();
                    const minReq = (tag === 'p' || tag === 'li') ? 13.0 : 10.0;
                    if (fs < minReq) {
                        bad.push({ tag, fs, minReq, text: el.innerText.trim().slice(0, 40) });
                    }
                }
                return bad;
            })()"""
        )
        assert too_small == [], f"Sub-threshold font sizes at {w}x{h}: {too_small}"


# ---------------------------------------------------------------------------
# F7: Interactive Boundary States (5 items)
# ---------------------------------------------------------------------------


def test_empty_command_palette_search_shows_zero_or_empty_state_gracefully(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F7-01: Non-matching query in Ctrl+K palette produces 0 errors and handles empty results cleanly."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.open_command_palette_via_shortcut()
        page.type_text("zzzznonexistent999")
        pal = page.discover_command_palette()
        assert pal is not None
        assert "maritime watch" not in pal["text"].lower()
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_filter_reset_to_all_restores_full_project_count(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F7-02: Filtering to a subset category then clicking All restores all 6 projects."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        assert len(page.discover_project_cards()) == 6
        page.click_filter_pill("Backend")
        assert len(page.discover_project_cards()) < 6
        page.click_filter_pill("All")
        assert len(page.discover_project_cards()) == 6
        page.assert_clean_runtime()


def test_drawer_close_on_escape_when_already_closed_is_safe(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F7-03: Pressing Escape when no modal/drawer is open produces 0 errors."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None
        page.assert_clean_runtime()


def test_drawer_reopen_different_project_updates_content(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F7-04: Opening Maritime Watch, closing, and opening Restofy updates drawer content."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        d1 = page.open_project_drawer("Maritime Watch")
        assert "maritime watch" in d1["text"].lower()
        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        d2 = page.open_project_drawer("Restofy")
        assert "restofy" in d2["text"].lower()
        assert "maritime watch" not in d2["text"].lower()
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_reduced_motion_media_query_respected(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T2-F7-05: prefers-reduced-motion: reduce loads cleanly with 0 errors and matches CSS media query."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.set_reduced_motion(True)
        page.goto(f"{live_server.base_url}/index.html")
        page.assert_clean_runtime()
        matches = page.eval_js("window.matchMedia('(prefers-reduced-motion: reduce)').matches")
        assert matches is True
