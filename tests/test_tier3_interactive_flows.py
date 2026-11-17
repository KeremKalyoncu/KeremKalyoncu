"""Tier 3 Pairwise Cross-Feature Interactive Browser Flow Tests (>= 7 tests)."""

from __future__ import annotations

import time

import pytest

from tests.cdp_harness import CDPHarness, LocalSiteServer

pytestmark = [pytest.mark.e2e, pytest.mark.tier3]


def test_category_filter_pills_dynamically_filter_cards(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-01: Clicking category filter pills dynamically filters visible project cards."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        initial = {c["project"] for c in page.discover_project_cards()}
        assert len(initial) == 6

        page.click_filter_pill("Production")
        prod_cards = {c["project"] for c in page.discover_project_cards()}
        assert 0 < len(prod_cards) < len(initial)
        assert "Maritime Watch" in prod_cards

        page.click_filter_pill("Backend")
        back_cards = {c["project"] for c in page.discover_project_cards()}
        assert 0 < len(back_cards) < len(initial)
        assert "Restofy" in back_cards
        assert back_cards != prod_cards

        page.click_filter_pill("AI")
        ai_cards = {c["project"] for c in page.discover_project_cards()}
        assert 0 < len(ai_cards) < len(initial)
        assert "ML & Data Lab" in ai_cards

        page.click_filter_pill("All")
        restored = {c["project"] for c in page.discover_project_cards()}
        assert restored == initial
        page.assert_clean_runtime()


def test_project_card_opens_drawer_and_node_click_updates_telemetry(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-02: Clicking Maritime Watch opens drawer; clicking >=2 arch nodes updates readout; Escape closes."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        dlg = page.open_project_drawer("Maritime Watch")
        assert dlg["rect"]["width"] > 200
        assert "maritime watch" in dlg["text"].lower()

        nodes = page.discover_arch_nodes_in_dialog()
        assert len(nodes) >= 2, f"Expected >=2 clickable arch nodes in drawer, got {nodes}"

        page.click_point(
            nodes[0]["rect"]["left"] + nodes[0]["rect"]["width"] / 2.0,
            nodes[0]["rect"]["top"] + nodes[0]["rect"]["height"] / 2.0,
        )
        time.sleep(0.08)
        text_after_n0 = page.discover_open_dialog()["text"]

        page.click_point(
            nodes[1]["rect"]["left"] + nodes[1]["rect"]["width"] / 2.0,
            nodes[1]["rect"]["top"] + nodes[1]["rect"]["height"] / 2.0,
        )
        time.sleep(0.08)
        text_after_n1 = page.discover_open_dialog()["text"]

        assert text_after_n0 != text_after_n1, (
            "Clicking distinct architecture nodes inside drawer did not update telemetry readout"
        )

        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None
        page.assert_clean_runtime()


def test_command_palette_ctrl_k_fuzzy_search_and_enter_navigation(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-03: Ctrl+K opens Command Palette, 'shif' filters to Shifha, Enter opens Shifha inspector."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        pal = page.open_command_palette_via_shortcut()
        assert pal["focused"] is True, "Command palette search input did not receive focus"

        page.type_text("shif")
        time.sleep(0.08)
        filtered = page.discover_command_palette()
        assert filtered is not None
        assert "shifha" in filtered["text"].lower()
        assert "kriptoparatakip" not in filtered["text"].lower()

        page.press_key("Enter", "Enter", 13)
        time.sleep(0.15)
        dlg = page.discover_open_dialog()
        assert dlg is not None and "shifha" in dlg["text"].lower(), (
            f"Enter in Command Palette did not open Shifha inspector: {dlg}"
        )
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_stack_matrix_skill_click_highlights_matching_projects(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-04: Clicking Stack Matrix skills ('Python', 'Docker') cross-highlights matching projects."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        baseline = {c["project"]: c["style"] for c in page.discover_project_cards()}

        page.click_stack_skill("Python")
        time.sleep(0.1)
        py_state = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert py_state["Maritime Watch"] != py_state["Restofy"], (
            "Clicking 'Python' did not visually differentiate Python project (Maritime Watch) from non-Python (Restofy)"
        )
        assert (
            py_state["Maritime Watch"] != baseline["Maritime Watch"]
            or py_state["Restofy"] != baseline["Restofy"]
        )

        page.click_stack_skill("Docker")
        time.sleep(0.1)
        dk_state = {c["project"]: c["style"] for c in page.discover_project_cards()}
        assert dk_state["Restofy"] != dk_state["KriptoParaTakip"], (
            "Clicking 'Docker' did not differentiate Docker project (Restofy) from KriptoParaTakip"
        )

        # Toggle active skill off to restore
        page.click_stack_skill("Docker")
        time.sleep(0.1)
        page.assert_clean_runtime()


def test_pause_motion_toggle_disables_animations_zero_errors(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-05: Pause Motion button toggles ARIA/label & measurable motion state cleanly back and forth."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        btn_before = page.discover_motion_toggle()
        assert btn_before is not None
        motion_before = page.get_motion_state()

        page.click_point(
            btn_before["rect"]["left"] + btn_before["rect"]["width"] / 2.0,
            btn_before["rect"]["top"] + btn_before["rect"]["height"] / 2.0,
        )
        time.sleep(0.1)
        btn_paused = page.discover_motion_toggle()
        assert btn_paused is not None
        assert (
            btn_paused["ariaPressed"] != btn_before["ariaPressed"]
            or btn_paused["ariaChecked"] != btn_before["ariaChecked"]
            or btn_paused["text"] != btn_before["text"]
        ), f"Motion toggle state did not change on click: {btn_before} -> {btn_paused}"

        motion_paused = page.get_motion_state()
        motion_changed = (
            motion_paused["htmlData"] != motion_before["htmlData"]
            or motion_paused["bodyData"] != motion_before["bodyData"]
            or motion_paused["htmlClass"] != motion_before["htmlClass"]
            or motion_paused["bodyClass"] != motion_before["bodyClass"]
            or motion_paused["pausedAnims"] > motion_before["pausedAnims"]
        )
        assert motion_changed, (
            f"Motion toggle did not produce measurable reduced-motion DOM/animation pause effect: "
            f"{motion_before} -> {motion_paused}"
        )

        page.click_point(
            btn_paused["rect"]["left"] + btn_paused["rect"]["width"] / 2.0,
            btn_paused["rect"]["top"] + btn_paused["rect"]["height"] / 2.0,
        )
        time.sleep(0.1)
        btn_resumed = page.discover_motion_toggle()
        assert btn_resumed is not None
        assert btn_resumed["ariaPressed"] == btn_before["ariaPressed"]
        assert btn_resumed["ariaChecked"] == btn_before["ariaChecked"]
        assert btn_resumed["text"] == btn_before["text"]
        motion_resumed = page.get_motion_state()
        assert (
            motion_resumed["htmlData"] == motion_before["htmlData"]
            and motion_resumed["bodyData"] == motion_before["bodyData"]
            and motion_resumed["htmlClass"] == motion_before["htmlClass"]
            and motion_resumed["bodyClass"] == motion_before["bodyClass"]
            and motion_resumed["pausedAnims"] <= motion_before["pausedAnims"]
        ), f"Motion state did not restore on second toggle: {motion_before} -> {motion_resumed}"
        page.assert_clean_runtime()


def test_pairwise_filter_plus_drawer_plus_escape(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-06: Filter to Backend -> open Restofy drawer -> Escape preserves active category filter."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.click_filter_pill("Backend")
        filtered_before = {c["project"] for c in page.discover_project_cards()}
        assert "Restofy" in filtered_before and len(filtered_before) < 6

        dlg = page.open_project_drawer("Restofy")
        assert "restofy" in dlg["text"].lower()
        page.press_key("Escape", "Escape", 27)
        assert page.discover_open_dialog() is None

        filtered_after = {c["project"] for c in page.discover_project_cards()}
        assert filtered_after == filtered_before, (
            f"Category filter lost after drawer Escape: {filtered_before} -> {filtered_after}"
        )
        page.assert_clean_runtime()


def test_pairwise_stack_matrix_plus_category_filter_coexistence(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-07: Activating Stack Matrix skill ('Java') + switching category filter coexists without errors."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        page.click_stack_skill("Java")
        time.sleep(0.08)
        page.click_filter_pill("Backend")
        time.sleep(0.08)
        cards = page.discover_project_cards()
        names = {c["project"] for c in cards}
        assert "Restofy" in names and "KriptoParaTakip" in names
        page.click_filter_pill("All")
        assert len(page.discover_project_cards()) == 6
        page.assert_clean_runtime()


def test_pairwise_palette_opens_over_drawer_or_switches_project(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-08: Opening Inventra drawer then using Ctrl+K to jump to Restofy transitions cleanly."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        d1 = page.open_project_drawer("Inventra")
        assert "inventra" in d1["text"].lower()

        page.open_command_palette_via_shortcut()
        page.type_text("Restofy")
        time.sleep(0.08)
        page.press_key("Enter", "Enter", 13)
        time.sleep(0.15)

        d2 = page.discover_open_dialog()
        assert d2 is not None and "restofy" in d2["text"].lower()
        assert "inventra" not in d2["text"].lower()
        page.press_key("Escape", "Escape", 27)
        page.assert_clean_runtime()


def test_timeline_and_chapter_navigation_anchors_scroll_cleanly(
    live_server: LocalSiteServer, cdp_harness: CDPHarness
) -> None:
    """T3-09: Clicking in-page chapter navigation anchors advances scrollY cleanly."""
    with cdp_harness.new_page((1440, 900)) as page:
        page.goto(f"{live_server.base_url}/index.html")
        anchors = page.eval_js(
            """(() => {
                return Array.from(document.querySelectorAll('nav a[href^="#"], header a[href^="#"]')).filter(a => {
                    const r = a.getBoundingClientRect();
                    return r.width > 10 && r.height > 10 && a.getAttribute('href').length > 1;
                }).map(a => ({
                    href: a.getAttribute('href'),
                    text: (a.innerText || '').trim(),
                    rect: {left: a.getBoundingClientRect().left, top: a.getBoundingClientRect().top, width: a.getBoundingClientRect().width, height: a.getBoundingClientRect().height},
                }));
            })()"""
        )
        assert len(anchors) >= 3, f"Expected >=3 navigation chapter anchors, got {anchors}"
        target = anchors[-1]
        page.click_point(
            target["rect"]["left"] + target["rect"]["width"] / 2.0,
            target["rect"]["top"] + target["rect"]["height"] / 2.0,
        )
        time.sleep(0.25)
        scroll_y = page.eval_js("window.scrollY")
        assert scroll_y > 100, f"Clicking nav anchor {target['href']} did not scroll page (scrollY={scroll_y})"
        page.assert_clean_runtime()
