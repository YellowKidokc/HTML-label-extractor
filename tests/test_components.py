from pathlib import Path

from components.content import find_article_stats, find_paper_equation
from components.mda_specific import (
    find_citation_block,
    find_data_table,
    find_facts_card,
    find_math_translation,
    find_one_breath,
    find_proof_layer,
    find_rigor_card,
)
from components.structural import find_footer, find_hero, find_main_layout, find_topbar
from components.tabs import find_tab_bar, find_tab_paper
from core.marker import inject_markers, marker_balance
from label_sections import detect_components

FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def markers(ranges):
    return {item.marker for item in ranges}


def test_structural_detectors_find_gtq_targets():
    html = read_fixture("gtq_full.html")
    assert find_topbar(html)
    assert find_hero(html)
    assert find_main_layout(html)
    assert find_footer(html)


def test_tab_and_content_detectors_find_gtq_targets():
    html = read_fixture("gtq_full.html")
    assert find_tab_bar(html)
    assert find_tab_paper(html)
    assert len(find_paper_equation(html)) == 2
    assert find_article_stats(html)


def test_mda_detectors_find_mda_targets():
    html = read_fixture("mda_full.html")
    found = markers(detect_components(html))
    assert {"PROOF-LAYER", "MATH-TRANSLATION", "DATA-TABLE", "CITATION-BLOCK", "ONE-BREATH", "FACTS-CARD", "RIGOR-CARD"} <= found
    assert find_proof_layer(html)
    assert find_math_translation(html)
    assert find_data_table(html)
    assert find_citation_block(html)
    assert find_one_breath(html)
    assert find_facts_card(html)
    assert find_rigor_card(html)


def test_mda_detectors_return_empty_for_minimal_fixture():
    html = read_fixture("minimal.html")
    assert find_proof_layer(html) == []
    assert find_math_translation(html) == []
    assert find_data_table(html) == []
    assert find_citation_block(html) == []
    assert find_facts_card(html) == []
    assert find_rigor_card(html) == []


def test_broken_html_does_not_crash_scanner():
    html = read_fixture("broken.html")
    ranges = detect_components(html)
    assert markers(ranges) >= {"TOPBAR", "HERO", "MAIN-LAYOUT"}


def test_injected_markers_are_balanced():
    html = read_fixture("gtq_full.html")
    labeled = inject_markers(html, detect_components(html))
    balance = marker_balance(labeled)
    assert balance
    assert all(item["balanced"] for item in balance.values())


def test_no_components_fixture_returns_empty():
    html = read_fixture("no_components.html")
    assert detect_components(html) == []


def test_template_builder_registry_variants_are_detectable():
    from components.registry import PARTS

    html = read_fixture("template_parts.html")
    qualified = {item.qualified_marker for item in detect_components(html)}
    expected = {f"{part.marker}:{variant.id}" for part in PARTS for variant in part.variants}
    assert expected <= qualified


def test_mda_sample_structural_patterns_are_detected():
    html = read_fixture("mda_sample.html")
    found = markers(detect_components(html))
    assert {
        "TOPBAR",
        "HEADER",
        "HERO",
        "SIDEBAR-NAV",
        "TAB-BAR",
        "TAB-EXECUTIVE-SUMMARY",
        "TAB-PAPER",
        "TAB-EXPLAIN-IT-SIMPLE",
        "TAB-RIGOR-KILL-CONDITIONS",
        "TAB-WATCH-LISTEN",
        "MAIN-LAYOUT",
        "BOTTOM-NAV",
        "SERIES-NAV",
        "AUDIO-DOCK",
        "KILL-SIDEBAR",
        "KILL-CARD-DESTRUCTIVE",
        "KILL-CARD-SUGGESTIVE",
        "KILL-CARD-LOAD-BEARING",
        "ONE-BREATH",
        "PROOF-LAYER",
        "MATH-TRANSLATION",
    } <= found
