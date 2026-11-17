"""Self-validation tests proving every static and CDP validator is non-tautological.

Runs exclusively against ephemeral ``tmp_path`` mock fixtures so it passes
independently of Implementation Track completion and never mutates repo files.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Callable

from PIL import Image
import pytest

from tests.cdp_harness import (
    CDPHarness,
    LocalSiteServer,
    check_svg_dark_canvas,
    check_svg_size_budget,
    extract_readme_images_metadata,
    extract_readme_links,
    extract_readme_local_assets,
    find_ocean_theme_artifacts,
    find_svg_csp_violations,
    run_python_subprocess,
    validate_png,
    validate_svg_xml,
)

pytestmark = pytest.mark.self_validation


# ---------------------------------------------------------------------------
# 1. Static SVG XML, CSP, Size, Ocean-Theme & README Asset Validators
# ---------------------------------------------------------------------------


def test_validate_svg_xml_positive_and_negative(tmp_path: Path) -> None:
    good = tmp_path / "good.svg"
    good.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 300">'
        '<rect width="880" height="300" fill="#080A0F"/></svg>',
        encoding="utf-8",
    )
    root = validate_svg_xml(good)
    assert root.get("viewBox") == "0 0 880 300"

    broken = tmp_path / "broken.svg"
    broken.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 300"><g></svg>',
        encoding="utf-8",
    )
    with pytest.raises(AssertionError, match="Invalid XML"):
        validate_svg_xml(broken)

    non_svg = tmp_path / "html.svg"
    non_svg.write_text("<html><body>not svg</body></html>", encoding="utf-8")
    with pytest.raises(AssertionError, match="Expected <svg>"):
        validate_svg_xml(non_svg)

    no_vb = tmp_path / "no_vb.svg"
    no_vb.write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>', encoding="utf-8")
    with pytest.raises(AssertionError, match="Missing viewBox"):
        validate_svg_xml(no_vb)


def test_find_svg_csp_violations_positive_and_negatives(tmp_path: Path) -> None:
    clean = tmp_path / "clean.svg"
    clean.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 240">'
        "<defs>"
        '<linearGradient id="amberGlow"><stop offset="0%" stop-color="#FF5A1F"/></linearGradient>'
        '<g id="node"><circle r="4" fill="#34D399"/></g>'
        "</defs>"
        '<rect x="0" y="0" width="880" height="240" fill="url(#amberGlow)"/>'
        '<use href="#node" x="40" y="40"/>'
        '<rect x="10" y="10" width="20" height="20" style="fill:url(#amberGlow)"/>'
        '<circle cx="100" cy="100" r="5" fill="#F59E0B">'
        '<animate attributeName="opacity" values="1;0.5;1" dur="3s" repeatCount="indefinite"/>'
        "</circle>"
        "</svg>",
        encoding="utf-8",
    )
    assert find_svg_csp_violations(clean) == []

    negatives = {
        "script_tag.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><script>alert(1)</script></svg>',
        "onload_attr.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><rect onload="alert(1)" width="10" height="10"/></svg>',
        "foreign_obj.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><foreignObject width="100" height="50"><div>x</div></foreignObject></svg>',
        "external_href.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><image href="https://evil.test/x.png" width="10" height="10"/></svg>',
        "css_import.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><style>@import url("https://fonts.example/f.css");</style></svg>',
        "inline_external_url.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><rect style="fill:url(https://evil.test/a)" width="10" height="10"/></svg>',
        "js_uri.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"><a href="javascript:alert(1)"><text x="10" y="20">x</text></a></svg>',
    }
    for fname, body in negatives.items():
        p = tmp_path / fname
        p.write_text(body, encoding="utf-8")
        violations = find_svg_csp_violations(p)
        assert violations, f"Expected CSP violation for {fname}, got none"


def test_check_svg_size_budget_positive_and_negatives(tmp_path: Path) -> None:
    p1 = tmp_path / "p1.svg"
    p2 = tmp_path / "p2.svg"
    p1.write_bytes(b"<svg/>" + b" " * (40 * 1024))
    p2.write_bytes(b"<svg/>" + b" " * (60 * 1024))
    stats = check_svg_size_budget([p1, p2])
    assert stats["total"] == p1.stat().st_size + p2.stat().st_size

    oversized = tmp_path / "big.svg"
    oversized.write_bytes(b"<svg/>" + b" " * (155 * 1024))
    with pytest.raises(AssertionError, match="per-file budget"):
        check_svg_size_budget([oversized])

    c1 = tmp_path / "c1.svg"
    c2 = tmp_path / "c2.svg"
    c3 = tmp_path / "c3.svg"
    for c in (c1, c2, c3):
        c.write_bytes(b"<svg/>" + b" " * (140 * 1024))
    with pytest.raises(AssertionError, match="total budget"):
        check_svg_size_budget([c1, c2, c3])


def test_find_ocean_theme_artifacts_and_maritime_watch_guard() -> None:
    safe_text = (
        "OBSIDIAN ATLAS // ISTANBUL SYSTEMS MONOGRAPH. "
        "Maritime Watch Türkiye integrates multi-source weather, AIS telemetry, "
        "and marine navigational warnings into Go / Caution / No-Go decisions."
    )
    assert find_ocean_theme_artifacts(safe_text, "safe") == []

    for bad_sample in (
        "KEREM.AERO Control Surface",
        "assets/kerem-living-world-v9.svg",
        "function initOceanAudio() {}",
        '<div id="depth-indicator">200m</div>',
        "Frutiger Aero glassmorphism",
        "Welcome to the Living Engineering Ocean 🫧",
    ):
        hits = find_ocean_theme_artifacts(bad_sample, "bad")
        assert hits, f"Expected ocean-theme detection for: {bad_sample!r}"


def test_extract_readme_local_assets(tmp_path: Path) -> None:
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "atlas-hero.svg").write_text("<svg/>", encoding="utf-8")
    (assets_dir / "atlas-systems.svg").write_text("<svg/>", encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text(
        '<img src="assets/atlas-hero.svg?raw=true#gh-dark-mode-only" alt="Obsidian Atlas Hero Plate" />\n'
        "![Obsidian Atlas Systems](assets/atlas-systems.svg)\n"
        "![Badge](https://img.shields.io/badge/test-pass-green)\n",
        encoding="utf-8",
    )
    local_assets = extract_readme_local_assets(readme)
    assert [p.name for p in local_assets] == ["atlas-hero.svg", "atlas-systems.svg"]
    meta = extract_readme_images_metadata(readme)
    assert len(meta) == 3
    assert meta[0]["alt"] == "Obsidian Atlas Hero Plate"
    assert meta[2]["is_local"] is False


# ---------------------------------------------------------------------------
# 2. Headless Chromium CDP Validators (Geometry, Overflow, WCAG, Errors, PNG)
# ---------------------------------------------------------------------------


def test_cdp_svg_host_geometry_positive_and_negatives(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    good_svg = tmp_path / "good_plate.svg"
    good_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect x="0" y="0" width="880" height="200" fill="#0F141D"/>'
        '<text x="40" y="60" fill="#F1F5F9" font-size="22" font-family="sans-serif">OBSIDIAN ATLAS</text>'
        '<text x="40" y="120" fill="#94A3B8" font-size="14" font-family="monospace">41.0082 N, 28.9784 E</text>'
        "</svg>",
        encoding="utf-8",
    )
    clipped_svg = tmp_path / "clipped_plate.svg"
    clipped_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect x="0" y="0" width="880" height="200" fill="#0F141D"/>'
        '<text x="840" y="80" fill="#F1F5F9" font-size="18" font-family="sans-serif">ClippedBeyond880Width</text>'
        "</svg>",
        encoding="utf-8",
    )
    overlap_svg = tmp_path / "overlap_plate.svg"
    overlap_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect x="0" y="0" width="880" height="200" fill="#0F141D"/>'
        '<text x="100" y="80" fill="#F1F5F9" font-size="18" font-family="sans-serif">Alpha Label</text>'
        '<text x="105" y="83" fill="#F59E0B" font-size="18" font-family="sans-serif">Beta Label</text>'
        "</svg>",
        encoding="utf-8",
    )
    low_contrast_svg = tmp_path / "low_contrast_plate.svg"
    low_contrast_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect x="0" y="0" width="880" height="200" fill="#0F141D"/>'
        '<text x="40" y="80" fill="#18202C" font-size="14" font-family="sans-serif">Low Contrast Ink</text>'
        "</svg>",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((880, 900)) as page:
        good_res = page.inspect_svg_host(srv.base_url, "/good_plate.svg", width=880)
        page.assert_clean_runtime()
        assert good_res["viewBox"]["width"] == 880
        assert abs(good_res["svgRect"]["width"] - 880) <= 1.5
        assert good_res["clipped"] == []
        assert good_res["overlaps"] == []
        assert good_res["contrast_failures"] == []
        assert len(good_res["texts"]) == 2

        clip_res = page.inspect_svg_host(srv.base_url, "/clipped_plate.svg", width=880)
        assert clip_res["clipped"], "Expected clipped <text> detection beyond 880px"

        ov_res = page.inspect_svg_host(srv.base_url, "/overlap_plate.svg", width=880)
        assert ov_res["overlaps"], "Expected overlapping <text> detection"

        lc_res = page.inspect_svg_host(srv.base_url, "/low_contrast_plate.svg", width=880)
        assert lc_res["contrast_failures"], "Expected low-contrast SVG <text> detection"


def test_cdp_overflow_collisions_and_wcag_positive_and_negatives(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    good_html = tmp_path / "good.html"
    good_html.write_text(
        "<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        "<body style='margin:0;background:#080A0F;color:#F1F5F9;font-family:sans-serif;'>"
        "<main style='max-width:100%;padding:16px;box-sizing:border-box;'>"
        "<h1 style='font-size:28px;margin:0 0 12px 0;'>Kerem Kalyoncu</h1>"
        "<div style='background:rgba(15,20,29,0.92);padding:12px;'>"
        "<p style='font-size:15px;color:#94A3B8;margin:0 0 8px 0;'>Software Engineer in Istanbul.</p>"
        "<button style='background:#FF5A1F;color:#080A0F;font-weight:700;border:0;padding:8px 14px;'>Inspect</button>"
        "</div></main></body></html>",
        encoding="utf-8",
    )

    overflow_html = tmp_path / "overflow.html"
    overflow_html.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<div style='width:650px;'>Wide overflowing block</div></body></html>",
        encoding="utf-8",
    )

    collision_html = tmp_path / "collision.html"
    collision_html.write_text(
        "<!doctype html><html><body style='margin:0;padding:20px;background:#080A0F;color:#F1F5F9;font-family:sans-serif;'>"
        "<p style='margin:0;line-height:20px;margin-bottom:-16px;'>First colliding line</p>"
        "<p style='margin:0;line-height:20px;'>Second colliding line</p>"
        "</body></html>",
        encoding="utf-8",
    )

    low_contrast_html = tmp_path / "low_contrast.html"
    low_contrast_html.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<div style='background:rgba(255,255,255,0.04);padding:16px;'>"
        "<p style='font-size:14px;color:#2B3544;'>Unreadable dark paragraph</p>"
        "<button style='background:transparent;color:#334155;border:1px solid #1E293B;'>Dim Button</button>"
        "</div></body></html>",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{srv.base_url}/good.html")
        page.assert_clean_runtime()
        for w, h in ((1440, 900), (390, 844)):
            layout = page.check_overflow_and_collisions(w, h)
            assert layout["doc_scroll_width"] <= layout["inner_width"]
            assert layout["collisions"] == []
            wcag = page.check_wcag_contrast()
            assert wcag["checked_count"] >= 3
            assert wcag["failures"] == []

        page.goto(f"{srv.base_url}/overflow.html")
        ov = page.check_overflow_and_collisions(390, 844)
        assert ov["doc_scroll_width"] > 390

        page.goto(f"{srv.base_url}/collision.html")
        col = page.check_overflow_and_collisions(1440, 900)
        assert col["collisions"], "Expected overlapping HTML text collision"

        page.goto(f"{srv.base_url}/low_contrast.html")
        lc = page.check_wcag_contrast()
        assert len(lc["failures"]) >= 2, f"Expected >=2 WCAG failures, got {lc}"


def test_cdp_runtime_error_collectors_and_png_validation(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    broken_html = tmp_path / "broken.html"
    broken_html.write_text(
        "<!doctype html><html><body style='background:#0d1117;color:#F1F5F9;'>"
        "<img src='/missing.png' alt='missing'/>"
        "<script>"
        "console.error('boom_console');"
        "setTimeout(() => { throw new Error('uncaught_boom'); }, 10);"
        "</script>"
        "</body></html>",
        encoding="utf-8",
    )

    clean_html = tmp_path / "clean_shot.html"
    clean_html.write_text(
        "<!doctype html><html><body style='margin:0;background:#0d1117;color:#F1F5F9;font-family:sans-serif;'>"
        "<div style='width:880px;padding:32px;box-sizing:border-box;'>"
        "<h1 style='color:#FF5A1F;margin:0;'>OBSIDIAN ATLAS</h1>"
        "<p style='color:#94A3B8;'>Non-blank dark-theme verification target.</p>"
        "</div></body></html>",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((880, 400)) as page:
        page.goto(f"{srv.base_url}/broken.html", settle_ms=150)
        assert any("boom_console" in e for e in page.console_errors)
        assert any("uncaught_boom" in e for e in page.js_exceptions)
        assert any(err["status"] == 404 and "/missing.png" in err["url"] for err in page.http_errors)

        page.goto(f"{srv.base_url}/clean_shot.html")
        page.assert_clean_runtime()
        assert page.external_requests() == []
        shot = tmp_path / "clean.png"
        page.screenshot_png(shot, full_page=True)
        info = validate_png(shot, expected_width=880, min_stddev=2.0, max_median_luminance=0.35)
        assert info["width"] == 880

    blank_png = tmp_path / "blank.png"
    Image.new("RGB", (880, 200), (0, 0, 0)).save(blank_png)
    with pytest.raises(AssertionError, match="blank/uniform"):
        validate_png(blank_png, expected_width=880)


def test_cdp_tier3_discovery_cascade_against_mock_interactive_site(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify the 4-layer opaque-box discovery helpers work against semantic HTML."""
    interactive = tmp_path / "interactive.html"
    interactive.write_text(
        """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; background: #080A0F; color: #F1F5F9; font-family: sans-serif; }
  .hidden { display: none !important; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 16px; }
  .card { background: #0F141D; border: 1px solid #1E293B; padding: 16px; cursor: pointer; min-height: 90px; }
  .card.dim { opacity: 0.35; }
  .card.active { border-color: #FF5A1F; box-shadow: 0 0 0 2px #FF5A1F; }
  aside[role="dialog"] { position: fixed; right: 0; top: 0; width: 420px; height: 100vh; background: #0F141D; padding: 20px; border-left: 1px solid #334155; }
  div.palette[role="dialog"] { position: fixed; left: 25%; top: 15%; width: 50%; background: #0F141D; padding: 20px; border: 1px solid #FF5A1F; }
</style>
</head>
<body>
  <header style="padding:12px 16px;display:flex;gap:12px;">
    <button id="motion-btn" aria-pressed="false">Pause Motion</button>
    <div id="filters">
      <button data-cat="all" aria-pressed="true">All</button>
      <button data-cat="prod" aria-pressed="false">Production Systems</button>
      <button data-cat="back" aria-pressed="false">Backend & Microservices</button>
      <button data-cat="ai" aria-pressed="false">AI & Data Lab</button>
    </div>
  </header>
  <section class="grid" id="cards">
    <article class="card" tabindex="0" data-cat="prod" data-skills="Python,Leaflet"><h3>Maritime Watch</h3><p>AIS telemetry</p></article>
    <article class="card" tabindex="0" data-cat="prod" data-skills="React,PostgreSQL"><h3>Inventra</h3><p>Inventory platform</p></article>
    <article class="card" tabindex="0" data-cat="back" data-skills="Java,Docker"><h3>Restofy</h3><p>QR microservices</p></article>
    <article class="card" tabindex="0" data-cat="prod" data-skills="Python,React Native"><h3>Shifha</h3><p>Clinical AI</p></article>
    <article class="card" tabindex="0" data-cat="back" data-skills="Java"><h3>KriptoParaTakip</h3><p>Market engine</p></article>
    <article class="card" tabindex="0" data-cat="ai" data-skills="Python,Scikit-Learn"><h3>ML & Data Lab</h3><p>Predictive modeling</p></article>
  </section>
  <section id="stack" style="padding:16px;">
    <h2>Stack Matrix</h2>
    <button class="skill" data-skill="Python">Python</button>
    <button class="skill" data-skill="Docker">Docker</button>
    <button class="skill" data-skill="Java">Java</button>
  </section>
  <aside id="drawer" role="dialog" aria-modal="true" class="hidden">
    <h2 id="drawer-title"></h2>
    <svg width="360" height="80">
      <g role="button" tabindex="0" data-node="ingest"><rect x="10" y="10" width="90" height="30" fill="#151C28"/><text x="20" y="30" fill="#F1F5F9">AIS Ingest</text></g>
      <g role="button" tabindex="0" data-node="score"><rect x="140" y="10" width="90" height="30" fill="#151C28"/><text x="150" y="30" fill="#F1F5F9">Risk Engine</text></g>
    </svg>
    <p id="node-readout">Select a node</p>
  </aside>
  <div id="palette" class="palette hidden" role="dialog" aria-modal="true">
    <input id="pal-input" type="search" placeholder="Search systems...">
    <div id="pal-results"></div>
  </div>
  <script>
    const cards = Array.from(document.querySelectorAll('.card'));
    const drawer = document.getElementById('drawer');
    const drawerTitle = document.getElementById('drawer-title');
    const nodeReadout = document.getElementById('node-readout');
    const palette = document.getElementById('palette');
    const palInput = document.getElementById('pal-input');
    const palResults = document.getElementById('pal-results');

    document.getElementById('motion-btn').addEventListener('click', (e) => {
      const next = e.currentTarget.getAttribute('aria-pressed') !== 'true';
      e.currentTarget.setAttribute('aria-pressed', String(next));
      e.currentTarget.textContent = next ? 'Resume Motion' : 'Pause Motion';
      document.documentElement.dataset.motion = next ? 'paused' : 'running';
    });

    document.querySelectorAll('#filters button').forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.cat;
        cards.forEach(c => c.classList.toggle('hidden', cat !== 'all' && c.dataset.cat !== cat));
      });
    });

    function openDrawer(title) {
      drawerTitle.textContent = title;
      nodeReadout.textContent = 'Select a node';
      drawer.classList.remove('hidden');
    }
    cards.forEach(c => c.addEventListener('click', () => openDrawer(c.querySelector('h3').textContent)));
    drawer.querySelectorAll('[data-node]').forEach(n => {
      n.addEventListener('click', () => { nodeReadout.textContent = 'Node: ' + n.dataset.node; });
    });

    document.querySelectorAll('#stack .skill').forEach(btn => {
      btn.addEventListener('click', () => {
        const sk = btn.dataset.skill;
        cards.forEach(c => {
          const has = c.dataset.skills.split(',').includes(sk);
          c.classList.toggle('active', has);
          c.classList.toggle('dim', !has);
        });
      });
    });

    function renderPal(q) {
      const matches = cards.map(c => c.querySelector('h3').textContent).filter(t => t.toLowerCase().includes(q.toLowerCase()));
      palResults.innerHTML = matches.map(m => '<div class="pal-item">' + m + '</div>').join('');
    }
    palInput.addEventListener('input', () => renderPal(palInput.value));
    palInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const first = palResults.querySelector('.pal-item');
        if (first) { palette.classList.add('hidden'); openDrawer(first.textContent); }
      }
    });
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        palette.classList.remove('hidden');
        palInput.value = '';
        renderPal('');
        palInput.focus();
      } else if (e.key === 'Escape') {
        palette.classList.add('hidden');
        drawer.classList.add('hidden');
      }
    });
  </script>
</body>
</html>""",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{srv.base_url}/interactive.html")
        page.assert_clean_runtime()

        pills = page.discover_filter_pills()
        assert len(pills) == 4
        assert len(page.discover_project_cards()) == 6

        page.click_filter_pill("Backend")
        assert len(page.discover_project_cards()) == 2
        page.click_filter_pill("All")
        assert len(page.discover_project_cards()) == 6

        dlg = page.open_project_drawer("Maritime Watch")
        assert "Maritime Watch" in dlg["text"]
        nodes = page.discover_arch_nodes_in_dialog()
        assert len(nodes) == 2
        page.click_point(
            nodes[0]["rect"]["left"] + nodes[0]["rect"]["width"] / 2.0,
            nodes[0]["rect"]["top"] + nodes[0]["rect"]["height"] / 2.0,
        )
        t1 = page.discover_open_dialog()["text"]
        page.click_point(
            nodes[1]["rect"]["left"] + nodes[1]["rect"]["width"] / 2.0,
            nodes[1]["rect"]["top"] + nodes[1]["rect"]["height"] / 2.0,
        )
        t2 = page.discover_open_dialog()["text"]
        assert t1 != t2 and "Node: score" in t2

        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        pal = page.open_command_palette_via_shortcut()
        assert pal["focused"] is True
        page.type_text("shif")
        pal_after = page.discover_command_palette()
        assert "Shifha" in pal_after["text"]
        page.press_key("Enter", "Enter", 13)
        dlg2 = page.discover_open_dialog()
        assert dlg2 is not None and "Shifha" in dlg2["text"]
        page.press_key("Escape", "Escape", 27)

        skills = page.discover_stack_skills()
        assert any(s["text"] == "Python" for s in skills)
        page.click_stack_skill("Python")
        styled = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert float(styled["Maritime Watch"]["opacity"]) > float(styled["Restofy"]["opacity"])

        motion = page.discover_motion_toggle()
        assert motion is not None
        m_before = page.get_motion_state()
        page.click_point(
            motion["rect"]["left"] + motion["rect"]["width"] / 2.0,
            motion["rect"]["top"] + motion["rect"]["height"] / 2.0,
        )
        motion_after = page.discover_motion_toggle()
        assert motion_after["ariaPressed"] == "true"
        m_after = page.get_motion_state()
        assert m_after["htmlData"].get("motion") == "paused" and m_after != m_before
        page.assert_clean_runtime()


# ---------------------------------------------------------------------------
# 3. Round 2 Hardening Regressions (Subprocess, CSP, README, SVG, WCAG, Overflow, Tier 3)
# ---------------------------------------------------------------------------


def test_subprocess_and_tmp_repo_clean_outputs_catches_noop_generator(
    tmp_repo_factory: Callable[..., Path],
) -> None:
    """Verify run_python_subprocess (stdin=DEVNULL) and tmp_repo_factory(clean_outputs=True) catch no-op builds."""
    work = tmp_repo_factory("noop_check", clean_outputs=True)
    assert not (work / "index.html").exists()
    assert not list((work / "assets").glob("atlas-*.svg"))

    # Replace build_site.py in the isolated copy with a no-op script
    (work / "source" / "build_site.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    proc = run_python_subprocess([sys.executable, "source/build_site.py"], cwd=work, timeout=15)
    assert proc.returncode == 0
    assert not (work / "index.html").exists(), "clean_outputs=True must ensure no-op build_site.py produces no index.html"

    # Now replace with a deterministic generator and confirm it works cleanly with stdin=DEVNULL
    (work / "source" / "build_site.py").write_text(
        "from pathlib import Path\n"
        "Path('index.html').write_text('<html><body>Obsidian Atlas</body></html>', encoding='utf-8')\n",
        encoding="utf-8",
    )
    proc2 = run_python_subprocess([sys.executable, "source/build_site.py"], cwd=work, timeout=15)
    assert proc2.returncode == 0
    assert (work / "index.html").exists()


def test_find_svg_csp_violations_round2_hardened_bypasses(tmp_path: Path) -> None:
    """Verify Round 2 CSP bypass vectors and white-canvas SVG detection fail closed."""
    bypasses = {
        "style_xml_comment_import.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style><!--c-->@import "https://evil.com/a.css";</style></svg>'
        ),
        "style_xml_comment_url.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style><!--c-->rect{background:url("https://evil.com/x.png")}</style></svg>'
        ),
        "css_hex_escape_import.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>@\\69mport "https://evil.com/a.css";</style></svg>'
        ),
        "css_comment_inside_url.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>rect{fill:url(/*c*/"https://evil.com/a.svg#g");}</style></svg>'
        ),
        "css_hex_escape_scheme.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>rect{fill:url("https\\3a//evil.com/a.svg#g");}</style></svg>'
        ),
        "set_onbegin.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<rect width="10" height="10"><set attributeName="onbegin" to="alert(1)"/></rect></svg>'
        ),
        "animate_href_to.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<a><animate attributeName="href" to="https://evil.com/x"/><text x="10" y="20">x</text></a></svg>'
        ),
        "animate_href_values.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<image width="10" height="10"><animate attributeName="href" values="https://evil.com/1;https://evil.com/2"/></image></svg>'
        ),
        "tab_in_javascript_uri.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<a href="java&#x09;script:alert(1)"><text x="10" y="20">x</text></a></svg>'
        ),
        "presentation_fill_url.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<rect width="10" height="10" fill="url(https://evil.com/g.svg#g)"/></svg>'
        ),
        "presentation_filter_url.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<rect width="10" height="10" filter="url(https://evil.com/f.svg#f)"/></svg>'
        ),
        "xml_stylesheet_pi.svg": (
            '<?xml-stylesheet type="text/css" href="https://evil.com/x.css"?>'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100"/>'
        ),
        "image_root_relative.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<image href="/leak.png" width="10" height="10"/></svg>'
        ),
        "css_root_relative.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>rect{background:url("/assets/leak.png")}</style></svg>'
        ),
    }
    for fname, body in bypasses.items():
        p = tmp_path / fname
        p.write_text(body, encoding="utf-8")
        v = find_svg_csp_violations(p)
        assert v, f"Expected CSP violation for {fname}, got none"

    # White-canvas SVG with dark <defs> stop must be rejected by check_svg_dark_canvas
    white_svg = tmp_path / "white_canvas.svg"
    white_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 300">'
        '<defs><linearGradient id="g"><stop stop-color="#080A0F"/></linearGradient></defs>'
        '<rect width="880" height="300" fill="#FFFFFF"/>'
        '<text x="20" y="40" fill="#111111">White canvas</text></svg>',
        encoding="utf-8",
    )
    canvas = check_svg_dark_canvas(white_svg)
    assert not canvas["backdrop_dark_lums"] and canvas["backdrop_light_lums"]


def test_readme_extractors_round2_picture_nested_badge_and_fragment_rejection(
    tmp_path: Path,
) -> None:
    """Verify <picture><source srcset>, > in alt, unquoted src, [![badge](img)](url), and #frag rejection."""
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "dark.svg").write_text("<svg/>", encoding="utf-8")
    (assets / "hero.svg").write_text("<svg/>", encoding="utf-8")
    (assets / "unquoted.svg").write_text("<svg/>", encoding="utf-8")

    md = tmp_path / "README.md"
    md.write_text(
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/dark.svg 1x, assets/missing-2x.svg 2x">\n'
        '  <img alt="A > B diagram" src="assets/hero.svg?raw=true#gh-dark-mode-only">\n'
        '</picture>\n'
        '<img alt="Unquoted src image" src=assets/unquoted.svg />\n'
        '[![Build](https://img.shields.io/badge/a-b-c)](https://example.com/target)\n'
        '[Ref Link][ref1]\n\n'
        '[ref1]: https://example.com/ref\n',
        encoding="utf-8",
    )
    local = extract_readme_local_assets(md)
    names = [p.name for p in local]
    assert "dark.svg" in names
    assert "missing-2x.svg" in names
    assert "hero.svg" in names
    assert "unquoted.svg" in names

    links = extract_readme_links(md)
    assert "https://example.com/target" in links
    assert "https://img.shields.io/badge/a-b-c" not in links
    assert "https://example.com/ref" in links

    frag_md = tmp_path / "FRAG.md"
    frag_md.write_text('<img alt="Fragment only" src="#gh-dark-mode-only" />\n', encoding="utf-8")
    with pytest.raises(AssertionError, match="empty or fragment-only"):
        extract_readme_local_assets(frag_md)


def test_cdp_svg_host_round2_tspan_hidden_opacity_shapes_and_viewbox(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify <tspan> overlaps, fill-opacity=0, <g opacity=0> backdrop, <path> bg, url(#...) & viewBox."""
    tspan_svg = tmp_path / "tspan_overlap.svg"
    tspan_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect width="880" height="200" fill="#0F141D"/>'
        '<text x="50" y="60" fill="#F1F5F9" font-size="18">'
        '<tspan x="50" y="60">AlphaTspan</tspan><tspan x="52" y="61">BetaTspan</tspan>'
        '</text></svg>',
        encoding="utf-8",
    )

    hidden_deco_svg = tmp_path / "hidden_deco.svg"
    hidden_deco_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect width="880" height="200" fill="#0F141D"/>'
        '<g opacity="0"><rect width="880" height="200" fill="#FFFFFF"/></g>'
        '<text x="40" y="60" fill="#F1F5F9" font-size="18">Primary Visible Label</text>'
        '<text x="40" y="60" fill="#F1F5F9" fill-opacity="0" font-size="18">Ghost Label</text>'
        '<text x="40" y="60" fill="none" font-size="18">None Fill Label</text>'
        '</svg>',
        encoding="utf-8",
    )

    path_and_grad_svg = tmp_path / "path_and_grad.svg"
    path_and_grad_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200">'
        '<rect width="880" height="200" fill="#0F141D"/>'
        '<path d="M 20 20 H 400 V 120 H 20 Z" fill="#FFFFFF"/>'
        '<text x="40" y="70" fill="#F1F5F9" font-size="16">WhiteOnWhitePath</text>'
        '<text x="460" y="70" fill="url(#missingGrad)" font-size="16">UnresolvedGrad</text>'
        '</svg>',
        encoding="utf-8",
    )

    no_vb_svg = tmp_path / "no_vb.svg"
    no_vb_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="880" height="150">'
        '<rect width="880" height="150" fill="#0F141D"/></svg>',
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((880, 900)) as page:
        t_res = page.inspect_svg_host(srv.base_url, "/tspan_overlap.svg", width=880)
        assert t_res["overlaps"], "Expected sibling <tspan> overlap detection"

        h_res = page.inspect_svg_host(srv.base_url, "/hidden_deco.svg", width=880)
        assert h_res["overlaps"] == []
        assert h_res["contrast_failures"] == []
        assert len(h_res["texts"]) == 1

        pg_res = page.inspect_svg_host(srv.base_url, "/path_and_grad.svg", width=880)
        assert len(pg_res["contrast_failures"]) == 2, (
            f"Expected both white-on-white <path> and unresolved url(#missingGrad) failures, got {pg_res['contrast_failures']}"
        )

        with pytest.raises(AssertionError, match="viewBox"):
            page.inspect_svg_host(srv.base_url, "/no_vb.svg", width=880)


def test_cdp_wcag_round2_oklch_control_45_group_opacity_and_gradient(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify oklch(), normal-size control 4.5:1 enforcement, group-opacity compositing, and gradients."""
    oklch_html = tmp_path / "oklch_fail.html"
    oklch_html.write_text(
        "<!doctype html><html><body style='margin:0;background:oklch(0.95 0.02 90);font-family:sans-serif;'>"
        "<p style='color:#F1F5F9;font-size:15px;'>Light text on bright oklch background</p>"
        "</body></html>",
        encoding="utf-8",
    )

    ctrl_html = tmp_path / "ctrl_45.html"
    ctrl_html.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<button style='font-size:12px;color:#64748B;background:transparent;border:0;'>Dim 12px Button</button>"
        "<a href='#x' style='font-size:12px;color:#64748B;'>Dim 12px Link</a>"
        "</body></html>",
        encoding="utf-8",
    )

    group_op_html = tmp_path / "group_op.html"
    group_op_html.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<section style='opacity:0.4;background:#FFFFFF;padding:16px;'>"
        "<p style='color:#000000;font-size:14px;'>Group composited text</p>"
        "</section></body></html>",
        encoding="utf-8",
    )

    grad_dark = tmp_path / "grad_dark.html"
    grad_dark.write_text(
        "<!doctype html><html><body style='margin:0;background:linear-gradient(180deg, #080A0F, #0F141D);font-family:sans-serif;'>"
        "<p style='color:#F1F5F9;font-size:15px;'>Readable on dark gradient</p>"
        "</body></html>",
        encoding="utf-8",
    )

    grad_bright_fail = tmp_path / "grad_bright_fail.html"
    grad_bright_fail.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<div style='background:linear-gradient(#FFFFFF, #F8FAFC);padding:16px;'>"
        "<p style='color:#FFFFFF;font-size:15px;'>Invisible white on bright gradient</p>"
        "</div></body></html>",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{srv.base_url}/oklch_fail.html")
        r_ok = page.check_wcag_contrast()
        assert len(r_ok["failures"]) == 1

        page.goto(f"{srv.base_url}/ctrl_45.html")
        r_ctrl = page.check_wcag_contrast()
        assert len(r_ctrl["failures"]) == 2
        assert all(f["required"] == 4.5 for f in r_ctrl["failures"])

        page.goto(f"{srv.base_url}/group_op.html")
        r_grp = page.check_wcag_contrast()
        assert len(r_grp["failures"]) == 1
        assert r_grp["failures"][0]["eff_bg"] == (106.8, 108.0, 111.0)

        page.goto(f"{srv.base_url}/grad_dark.html")
        r_gd = page.check_wcag_contrast()
        assert r_gd["checked_count"] == 1 and r_gd["failures"] == []

        page.goto(f"{srv.base_url}/grad_bright_fail.html")
        r_gb = page.check_wcag_contrast()
        assert len(r_gb["failures"]) == 1


def test_cdp_overflow_round2_missing_meta_viewport_fixed_and_hidden_clip_plus_png_ext(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify missing viewport meta detection, fixed/clipped overflow leaks, external_requests, and validate_png."""
    no_meta = tmp_path / "no_meta.html"
    no_meta.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<div style='width:800px;'>Wide without viewport meta</div></body></html>",
        encoding="utf-8",
    )

    fixed_ov = tmp_path / "fixed_ov.html"
    fixed_ov.write_text(
        "<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        "<body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<div style='position:fixed;left:250px;top:10px;width:400px;'>Leaking fixed banner</div>"
        "</body></html>",
        encoding="utf-8",
    )

    clipped_ov = tmp_path / "clipped_ov.html"
    clipped_ov.write_text(
        "<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        "<body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<main style='overflow-x:hidden;width:100%;'>"
        "<div style='width:1200px;'>Wide clipped block inside overflow-x hidden</div>"
        "</main></body></html>",
        encoding="utf-8",
    )

    ext_html = tmp_path / "ext_req.html"
    ext_html.write_text(
        "<!doctype html><html><body style='background:#080A0F;color:#F1F5F9;'>"
        "<script src='https://cdn.example.invalid/app.js'></script></body></html>",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((390, 844)) as page:
        page.goto(f"{srv.base_url}/no_meta.html")
        r_nm = page.check_overflow_and_collisions(390, 844)
        assert r_nm["inner_width"] != 390, "Missing <meta name='viewport'> should yield 980px innerWidth"

        page.goto(f"{srv.base_url}/fixed_ov.html")
        r_fx = page.check_overflow_and_collisions(390, 844)
        assert any(lk["kind"] == "fixed_edge_overflow" for lk in r_fx["overflow_leaks"])

        page.goto(f"{srv.base_url}/clipped_ov.html")
        r_cl = page.check_overflow_and_collisions(390, 844)
        assert any(lk["kind"] == "clipped_overflow_hidden" for lk in r_cl["overflow_leaks"])

        page.goto(f"{srv.base_url}/ext_req.html", settle_ms=100)
        assert any("cdn.example.invalid" in u for u in page.external_requests())

    # Negative validate_png checks (wrong width + light-theme luminance)
    light_png = tmp_path / "light.png"
    img = Image.new("RGB", (600, 200), (245, 245, 245))
    for x in range(100):
        img.putpixel((x, 50), (20, 20, 20))
    img.save(light_png)
    with pytest.raises(AssertionError, match="Expected PNG width"):
        validate_png(light_png, expected_width=880)
    with pytest.raises(AssertionError, match="not dark-theme"):
        validate_png(light_png, expected_width=600, min_stddev=2.0, max_median_luminance=0.35)


def test_cdp_tier3_realistic_semantic_layout_and_broken_traps(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify Tier 3/4 discovery succeeds on realistic semantic DOM and rejects broken palette/motion traps."""
    realistic = tmp_path / "realistic.html"
    realistic.write_text(
        """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; background: #080A0F; color: #F1F5F9; font-family: sans-serif; }
  .hidden { display: none !important; }
  .perm-rail { width: 220px; background: #0A0D14; padding: 12px; }
  ul.pills { display: flex; gap: 8px; list-style: none; padding: 0; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .card { background: #0F141D; border: 1px solid #1E293B; padding: 14px; }
  .card.active { border-color: #FF5A1F; }
  .card.dim { opacity: 0.3; }
  aside[role="dialog"] { position: fixed; right: 0; top: 0; width: 420px; height: 100vh; background: #0F141D; padding: 20px; z-index: 50; }
</style>
</head>
<body>
  <aside class="perm-rail">Telemetry Rail: ISTANBUL GO</aside>
  <section id="projects-sec">
    <p>Full-stack showcase using Python and Docker in production.</p>
    <ul class="pills">
      <li><button data-cat="all">All</button></li>
      <li><button data-cat="prod">Production Systems</button></li>
      <li><button data-cat="back">Backend & Microservices</button></li>
      <li><button data-cat="ai">AI & Data Lab</button></li>
    </ul>
    <div class="grid">
      <div class="card" data-cat="prod" data-skills="Python"><div class="hd"><h3>Maritime Watch</h3></div><button class="tag" type="button">Python</button><button class="inspect" type="button">Inspect System</button></div>
      <div class="card" data-cat="prod" data-skills="PostgreSQL"><div class="hd"><h3>Inventra</h3></div><button class="tag" type="button">PostgreSQL</button><button class="inspect" type="button">Inspect System</button></div>
      <div class="card" data-cat="back" data-skills="Docker,Java"><div class="hd"><h3>Restofy</h3></div><button class="tag" type="button">Docker</button><button class="inspect" type="button">Inspect System</button></div>
      <div class="card" data-cat="ai" data-skills="Python"><div class="hd"><h3>Shifha</h3></div><button class="tag" type="button">Python</button><button class="inspect" type="button">Inspect System</button></div>
      <div class="card" data-cat="back" data-skills="Java"><div class="hd"><h3>KriptoParaTakip</h3></div><button class="tag" type="button">Java</button><button class="inspect" type="button">Inspect System</button></div>
      <div class="card" data-cat="ai" data-skills="Python"><div class="hd"><h3>ML & Data Lab</h3></div><button class="tag" type="button">Python</button><button class="inspect" type="button">Inspect System</button></div>
    </div>
  </section>
  <section id="stack-sec">
    <h2>Technical Stack Matrix</h2>
    <button class="skill">Python</button>
    <button class="skill">Docker</button>
    <button class="skill">Java</button>
  </section>
  <aside id="drawer" role="dialog" aria-modal="true" class="hidden">
    <h2 id="d-title"></h2>
    <svg width="360" height="80">
      <g><text x="10" y="15" fill="#7C8EA6">LAT 41.0082 N</text></g>
      <g role="button" tabindex="0" data-node="ingest"><rect x="10" y="25" width="90" height="30" fill="#151C28"/><text x="20" y="45" fill="#F1F5F9">AIS Ingest</text></g>
      <g role="button" tabindex="0" data-node="risk"><rect x="140" y="25" width="90" height="30" fill="#151C28"/><text x="150" y="45" fill="#F1F5F9">Risk Engine</text></g>
    </svg>
    <p id="d-readout">Select a node</p>
  </aside>
  <script>
    const cards = Array.from(document.querySelectorAll('.card'));
    const drawer = document.getElementById('drawer');
    document.querySelectorAll('ul.pills button').forEach(b => b.addEventListener('click', () => {
      cards.forEach(c => c.classList.toggle('hidden', b.dataset.cat !== 'all' && c.dataset.cat !== b.dataset.cat));
    }));
    cards.forEach(c => {
      c.querySelector('.tag').addEventListener('click', () => { window.__tagClicked = true; });
      c.querySelector('.inspect').addEventListener('click', () => {
        document.getElementById('d-title').textContent = c.querySelector('h3').textContent;
        document.getElementById('d-readout').textContent = 'Ready';
        drawer.classList.remove('hidden');
      });
    });
    drawer.querySelectorAll('[data-node]').forEach(n => n.addEventListener('click', () => {
      document.getElementById('d-readout').textContent = 'Node: ' + n.dataset.node;
    }));
    document.querySelectorAll('#stack-sec .skill').forEach(b => b.addEventListener('click', () => {
      const sk = b.textContent.trim();
      cards.forEach(c => {
        const has = c.dataset.skills.split(',').includes(sk);
        c.classList.toggle('active', has);
        c.classList.toggle('dim', !has);
      });
    }));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') drawer.classList.add('hidden'); });
  </script>
</body>
</html>""",
        encoding="utf-8",
    )

    broken_traps = tmp_path / "broken_traps.html"
    broken_traps.write_text(
        """<!doctype html>
<html>
<body style="background:#080A0F;color:#F1F5F9;">
  <section>
    <input id="inline-search" type="search" placeholder="Inline search">
    <button id="motion-switch" role="switch" aria-checked="false">Pause Motion</button>
  </section>
  <script>
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        document.getElementById('inline-search').focus();
      }
    });
    document.getElementById('motion-switch').addEventListener('click', (e) => {
      e.currentTarget.setAttribute('aria-checked', 'true');
    });
  </script>
</body>
</html>""",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{srv.base_url}/realistic.html")
        assert page.discover_open_dialog() is None, "Permanent <aside> must not hijack discover_open_dialog"
        assert len(page.discover_filter_pills()) == 4
        assert len(page.discover_project_cards()) == 6

        dlg = page.open_project_drawer("Maritime Watch")
        assert "Maritime Watch" in dlg["text"]
        assert not page.eval_js("Boolean(window.__tagClicked)")
        nodes = page.discover_arch_nodes_in_dialog()
        assert [n["text"] for n in nodes] == ["AIS Ingest", "Risk Engine"]
        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        skills = page.discover_stack_skills()
        assert {s["text"] for s in skills} == {"Python", "Docker", "Java"}
        page.click_stack_skill("Python")
        styles = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert float(styles["Maritime Watch"]["opacity"]) > float(styles["Restofy"]["opacity"])

        page.goto(f"{srv.base_url}/broken_traps.html")
        with pytest.raises(AssertionError, match="Command palette did not open"):
            page.open_command_palette_via_shortcut()
        sw = page.discover_motion_toggle()
        assert sw is not None and sw["ariaChecked"] == "false"
        m0 = page.get_motion_state()
        page.click_point(sw["rect"]["left"] + 10, sw["rect"]["top"] + 10)
        m1 = page.get_motion_state()
        assert m1 == m0, "Broken motion switch produced no measurable DOM/animation state change"


def test_round3_svg_csp_fake_comment_image_set_and_xlink_animate(tmp_path: Path) -> None:
    """Verify Round 3 SVG CSP catches fake-comment strings, image-set(), CSS control-char /, and xlink:href SMIL."""
    safe_svg = tmp_path / "safe_comment_str.svg"
    safe_svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
        "<defs><linearGradient id=\"g\"><stop offset=\"0%\" stop-color=\"#080A0F\"/></linearGradient></defs>"
        '<style>text::before{content:"/*";} rect{fill:url("#g");} text::after{content:"*/";}</style>'
        '<rect width="10" height="10"/><text x="20" y="30" fill="#F1F5F9">Safe</text></svg>',
        encoding="utf-8",
    )
    assert find_svg_csp_violations(safe_svg) == []

    bypasses = {
        "fake_comment_str.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>svg{content:"/*";background-image:url("/leak.png");content:"*/"}</style></svg>'
        ),
        "image_set_str.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>svg{background-image:image-set("/leak.png" 1x);}</style></svg>'
        ),
        "webkit_image_set_nested.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>svg{background-image:-webkit-image-set(url("#g") 1x, "/leak2.png" type("image/png") 2x);}</style></svg>'
        ),
        "css_ctrl_slash.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 100">'
            '<style>rect{background:url("\\1/leak.png")}</style></svg>'
        ),
        "animate_xlink_href.svg": (
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 880 100">'
            '<image width="10" height="10"><animate attributeName="xlink:href" to="/leak.png"/></image></svg>'
        ),
    }
    for fname, body in bypasses.items():
        p = tmp_path / fname
        p.write_text(body, encoding="utf-8")
        v = find_svg_csp_violations(p)
        assert v, f"Expected Round 3 CSP violation for {fname}, got none"


def test_round3_readme_img_srcset_and_direct_text_overflow_hidden(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify <img> srcset extraction and direct-text overflow-x:hidden clipping detection."""
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "hero.svg").write_text("<svg/>", encoding="utf-8")
    md = tmp_path / "README.md"
    md.write_text(
        '<img alt="Obsidian Atlas Hero" src="assets/hero.svg" srcset="assets/missing-img-2x.svg 2x" />\n',
        encoding="utf-8",
    )
    local_names = [p.name for p in extract_readme_local_assets(md)]
    assert "hero.svg" in local_names
    assert "missing-img-2x.svg" in local_names

    direct_clip = tmp_path / "direct_clip.html"
    direct_clip.write_text(
        "<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        "<body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<p style='width:150px;overflow-x:hidden;white-space:nowrap;'>"
        "Very long direct text overflowing 150px box inside 390px viewport</p>"
        "</body></html>",
        encoding="utf-8",
    )
    ellipsis_ok = tmp_path / "ellipsis_ok.html"
    ellipsis_ok.write_text(
        "<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'></head>"
        "<body style='margin:0;background:#080A0F;color:#F1F5F9;'>"
        "<p style='width:150px;overflow-x:hidden;text-overflow:ellipsis;white-space:nowrap;'>"
        "Intentional ellipsis truncation stays permitted</p>"
        "</body></html>",
        encoding="utf-8",
    )
    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((390, 844)) as page:
        page.goto(f"{srv.base_url}/direct_clip.html")
        r_dc = page.check_overflow_and_collisions(390, 844)
        assert any(lk["kind"] == "clipped_overflow_hidden" for lk in r_dc["overflow_leaks"]), (
            f"Expected clipped_overflow_hidden for direct text node, got {r_dc}"
        )

        page.goto(f"{srv.base_url}/ellipsis_ok.html")
        r_el = page.check_overflow_and_collisions(390, 844)
        assert r_el["overflow_leaks"] == []


def test_round3_gradient_opaque_fallback_3stop_and_card_link_priority(
    tmp_path: Path, cdp_harness: CDPHarness
) -> None:
    """Verify opaque fallback+gradient, 3-stop mid-stop contrast (HTML & SVG), and card link priority."""
    grad_opaque_fb = tmp_path / "grad_opaque_fb.html"
    grad_opaque_fb.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<div style='background-color:#080A0F;background-image:linear-gradient(#FFFFFF, #F8FAFC);padding:16px;'>"
        "<p style='color:#FFFFFF;font-size:15px;'>Invisible white over bright grad with dark fallback</p>"
        "</div></body></html>",
        encoding="utf-8",
    )

    grad_3stop_fail = tmp_path / "grad_3stop_fail.html"
    grad_3stop_fail.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<div style='background:linear-gradient(90deg, #080A0F 0%, #FFFFFF 50%, #080A0F 100%);padding:16px;'>"
        "<p style='color:#F1F5F9;font-size:15px;'>Fails over bright 50% middle stop</p>"
        "</div></body></html>",
        encoding="utf-8",
    )

    grad_3stop_pass = tmp_path / "grad_3stop_pass.html"
    grad_3stop_pass.write_text(
        "<!doctype html><html><body style='margin:0;background:#080A0F;font-family:sans-serif;'>"
        "<div style='background:linear-gradient(90deg, #080A0F 0%, #0F141D 50%, #080A0F 100%);padding:16px;'>"
        "<p style='color:#F1F5F9;font-size:15px;'>Readable across all dark stops</p>"
        "</div></body></html>",
        encoding="utf-8",
    )

    svg_3stop_fail = tmp_path / "svg_3stop_fail.svg"
    svg_3stop_fail.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 150">'
        "<defs><linearGradient id=\"g3\" x1=\"0%\" x2=\"100%\">"
        '<stop offset="0%" stop-color="#080A0F"/>'
        '<stop offset="50%" stop-color="#FFFFFF"/>'
        '<stop offset="100%" stop-color="#080A0F"/>'
        "</linearGradient></defs>"
        '<rect width="880" height="150" fill="url(#g3)"/>'
        '<text x="40" y="75" fill="#F1F5F9" font-size="16">Middle stop fails</text>'
        "</svg>",
        encoding="utf-8",
    )

    ext_html = tmp_path / "ext.html"
    ext_html.write_text("<!doctype html><html><body>External Target</body></html>", encoding="utf-8")

    card_link_first = tmp_path / "card_link_first.html"
    card_link_first.write_text(
        """<!doctype html>
<html>
<head><meta charset="utf-8"><style>
  body { margin: 0; background: #080A0F; color: #F1F5F9; font-family: sans-serif; }
  .hidden { display: none !important; }
  .card { width: 320px; background: #0F141D; padding: 16px; }
  aside[role="dialog"] { position: fixed; right: 0; top: 0; width: 360px; height: 100vh; background: #0F141D; padding: 16px; }
</style></head>
<body>
  <article class="card">
    <h3>Maritime Watch</h3>
    <a href="/ext.html">View Live</a>
    <a href="#" id="hash-link">View Notes</a>
    <button class="inspect" type="button">Inspect System</button>
  </article>
  <aside id="drawer" role="dialog" aria-modal="true" class="hidden">
    <h2>Maritime Watch Architecture</h2>
  </aside>
  <script>
    document.getElementById('hash-link').addEventListener('click', (e) => {
      e.preventDefault();
      window.__hashLinkClicked = true;
    });
    document.querySelector('.inspect').addEventListener('click', () => {
      document.getElementById('drawer').classList.remove('hidden');
    });
  </script>
</body>
</html>""",
        encoding="utf-8",
    )

    with LocalSiteServer(tmp_path) as srv, cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{srv.base_url}/grad_opaque_fb.html")
        r_ofb = page.check_wcag_contrast()
        assert len(r_ofb["failures"]) == 1, f"Expected failure over gradient+opaque fallback, got {r_ofb}"

        page.goto(f"{srv.base_url}/grad_3stop_fail.html")
        r_3f = page.check_wcag_contrast()
        assert len(r_3f["failures"]) == 1, f"Expected 3-stop mid-stop HTML failure, got {r_3f}"

        page.goto(f"{srv.base_url}/grad_3stop_pass.html")
        r_3p = page.check_wcag_contrast()
        assert r_3p["checked_count"] == 1 and r_3p["failures"] == []

        s_3f = page.inspect_svg_host(srv.base_url, "/svg_3stop_fail.svg", width=880)
        assert len(s_3f["contrast_failures"]) == 1, f"Expected 3-stop mid-stop SVG failure, got {s_3f}"

        page.goto(f"{srv.base_url}/card_link_first.html")
        dlg = page.open_project_drawer("Maritime Watch")
        assert "Maritime Watch Architecture" in dlg["text"]
        assert page.eval_js("location.pathname") == "/card_link_first.html"
        assert not page.eval_js("Boolean(window.__hashLinkClicked)")
