"""Tier 4 Real-World Visitor E2E Journeys & Deterministic Screenshot Capture."""

from __future__ import annotations

from pathlib import Path
import time
from urllib.parse import quote

import pytest

from tests.cdp_harness import (
    CDPHarness,
    LocalSiteServer,
    extract_readme_local_assets,
    validate_png,
)
from tests.conftest import ATLAS_PLATES

pytestmark = [pytest.mark.e2e, pytest.mark.tier4]


def test_e2e_recruiter_desktop_journey(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """S1: Recruiter desktop journey (Hero -> Filter Production -> Maritime Watch -> 2 Nodes -> Escape -> All)."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.assert_clean_runtime()

        body = (page.eval_js("document.body.innerText") or "").lower()
        assert "kerem kalyoncu" in body and "doğuş" in body

        page.click_filter_pill("Production")
        assert any(c["project"] == "Maritime Watch" for c in page.discover_project_cards())

        dlg = page.open_project_drawer("Maritime Watch")
        assert "maritime watch" in dlg["text"].lower()
        nodes = page.discover_arch_nodes_in_dialog()
        assert len(nodes) >= 2
        for node in nodes[:2]:
            page.click_point(
                node["rect"]["left"] + node["rect"]["width"] / 2.0,
                node["rect"]["top"] + node["rect"]["height"] / 2.0,
            )
            time.sleep(0.06)

        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        page.click_filter_pill("All")
        assert len(page.discover_project_cards()) == 6
        page.assert_clean_runtime()


def test_e2e_power_user_keyboard_journey(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """S2: Power-user keyboard journey (Ctrl+K -> Shifha -> Enter -> Escape -> Ctrl+K -> Python -> Escape)."""
    with cdp_harness.new_page((1280, 800)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.open_command_palette_via_shortcut()
        page.type_text("Shifha")
        time.sleep(0.08)
        page.press_key("Enter", "Enter", 13)
        time.sleep(0.15)
        dlg = page.discover_open_dialog()
        assert dlg is not None and "shifha" in dlg["text"].lower()

        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        page.open_command_palette_via_shortcut()
        page.type_text("Python")
        time.sleep(0.08)
        pal = page.discover_command_palette()
        assert pal is not None and "python" in pal["text"].lower()
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_e2e_technical_stack_explorer_journey(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """S3: Stack explorer (Python highlight -> Pause Motion ON -> PostgreSQL highlight -> Pause Motion OFF)."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.click_stack_skill("Python")
        time.sleep(0.08)
        py_cards = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert py_cards["Maritime Watch"] != py_cards["Restofy"]

        toggle = page.discover_motion_toggle()
        assert toggle is not None
        page.click_point(
            toggle["rect"]["left"] + toggle["rect"]["width"] / 2.0,
            toggle["rect"]["top"] + toggle["rect"]["height"] / 2.0,
        )
        time.sleep(0.08)

        page.click_stack_skill("PostgreSQL")
        time.sleep(0.08)
        pg_cards = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert pg_cards["Inventra"] != pg_cards["KriptoParaTakip"]

        toggle2 = page.discover_motion_toggle()
        page.click_point(
            toggle2["rect"]["left"] + toggle2["rect"]["width"] / 2.0,
            toggle2["rect"]["top"] + toggle2["rect"]["height"] / 2.0,
        )
        page.assert_clean_runtime()


def test_e2e_mobile_portrait_visitor_journey(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """S4: Mobile 390x844 portrait journey (0 overflow -> scroll chapters -> open Inventra drawer -> 0 overflow)."""
    with cdp_harness.new_page((390, 844)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        layout = page.check_overflow_and_collisions(390, 844)
        assert layout["inner_width"] == 390
        assert layout["doc_scroll_width"] <= 391
        assert layout["overflow_leaks"] == []
        assert layout["collisions"] == []

        page.eval_js("window.scrollTo(0, document.body.scrollHeight * 0.45)")
        time.sleep(0.1)
        dlg = page.open_project_drawer("Inventra")
        assert "inventra" in dlg["text"].lower()
        assert dlg["rect"]["width"] <= 391, f"Mobile drawer exceeded 390px viewport: {dlg['rect']}"
        sw_after = page.eval_js("document.documentElement.scrollWidth")
        assert sw_after <= 391, f"Mobile drawer caused horizontal overflow: {sw_after}"

        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_e2e_screenshot_capture_harness_and_pillow_validation(
    repo_root: Path,
    readme_path: Path,
    live_server: LocalSiteServer,
    cdp_harness: CDPHarness,
    screenshot_dir: Path,
) -> None:
    """S5: Capture deterministic dark-theme README SVG & companion site PNGs and validate via Pillow."""
    # 1. Stacked README SVGs on #0d1117 @ 880px + per-plate captures
    local_assets = extract_readme_local_assets(readme_path)
    svg_srcs = [
        "/" + p.relative_to(repo_root).as_posix()
        for p in local_assets
        if p.suffix.lower() == ".svg"
    ]
    assert len(svg_srcs) >= 3

    with cdp_harness.new_page((880, 900)) as page:
        stack_url = f"{live_server.base_url}/__e2e_svg_stack__?srcs={quote(','.join(svg_srcs), safe='/,')}&w=880&bg=%230d1117"
        page.goto(stack_url, settle_ms=250)
        page.assert_clean_runtime()
        stack_png = screenshot_dir / "readme_svgs_dark_880px.png"
        page.screenshot_png(stack_png, full_page=True)
        validate_png(stack_png, expected_width=880, min_stddev=2.0, max_median_luminance=0.35)

        for plate in ATLAS_PLATES:
            stem = plate.replace(".svg", "").replace("-", "_")
            host_url = f"{live_server.base_url}/__e2e_svg_host__?src=/assets/{plate}&w=880&bg=%230d1117"
            page.goto(host_url, settle_ms=200)
            page.assert_clean_runtime()
            plate_png = screenshot_dir / f"{stem}_880px.png"
            page.screenshot_png(plate_png, full_page=True)
            validate_png(plate_png, expected_width=880, min_stddev=2.0, max_median_luminance=0.35)

    # 2. Desktop 1440x900 full-page, above-the-fold, open drawer, open Cmd+K palette
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html", settle_ms=250)
        page.assert_clean_runtime()

        fold_png = screenshot_dir / "site_desktop_1440_above_fold.png"
        page.screenshot_png(fold_png, full_page=False)
        validate_png(fold_png, expected_width=1440, min_stddev=2.0, max_median_luminance=0.35)

        full_png = screenshot_dir / "site_desktop_1440_full.png"
        page.screenshot_png(full_png, full_page=True)
        validate_png(full_png, expected_width=1440, min_stddev=2.0, max_median_luminance=0.35)

        # Open Maritime Watch drawer
        page.open_project_drawer("Maritime Watch")
        time.sleep(0.15)
        drawer_png = screenshot_dir / "site_drawer_open_1440.png"
        page.screenshot_png(drawer_png, full_page=False)
        validate_png(drawer_png, expected_width=1440, min_stddev=2.0, max_median_luminance=0.35)
        page.press_key("Escape", "Escape", 27)
        time.sleep(0.1)

        # Open Ctrl+K Command Palette with query "Maritime"
        page.open_command_palette_via_shortcut()
        page.type_text("Maritime")
        time.sleep(0.12)
        palette_png = screenshot_dir / "site_palette_open_1440.png"
        page.screenshot_png(palette_png, full_page=False)
        validate_png(palette_png, expected_width=1440, min_stddev=2.0, max_median_luminance=0.35)
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()

    # 3. Mobile 390x844
    with cdp_harness.new_page((390, 844)) as page:
        page.goto(f"{live_server.base_url}/index.html", settle_ms=250)
        page.assert_clean_runtime()
        mobile_png = screenshot_dir / "site_mobile_390_844.png"
        page.screenshot_png(mobile_png, full_page=True)
        validate_png(mobile_png, expected_width=390, min_stddev=2.0, max_median_luminance=0.35)
