"""Reading-level tab system detectors."""

from __future__ import annotations

from collections.abc import Iterable

from components.registry import PART_BY_ID
from core.parser import LabelRange, attr_value, element_ranges_by_start_tag, has_any_class, has_attr, has_id

GTQ_TAB_BAR_CLASSES = ["tab-shell", "tab-nav", "tab-bar", "tabs", "reading-tabs"]
MDA_TAB_BAR_CLASSES = ["mda-tabs", "mda-tab-nav", "mda-tab-shell", "reading-levels", "reading-level-nav", "reading-level-tabs", "level-tabs", "article-tabs", "tablist"]

SUMMARY_IDS = ["summary", "executive-summary", "exec-summary", "tab-summary", "overview"]
PAPER_IDS = ["paper", "story", "main-paper", "article-paper", "tab-paper", "deep-dive"]
SIMPLE_IDS = ["simple", "explain-it-simple", "plain-english", "simple-explanation", "tab-simple", "eli5"]
RIGOR_IDS = ["rigor", "kill", "kill-conditions", "falsification", "rigor-kill-conditions", "tab-rigor"]
MEDIA_IDS = ["media", "watch-listen", "listen", "audio", "video", "tab-media"]


def _classes(tag: str) -> set[str]:
    return set((attr_value(tag, "class") or "").split())


def _has_role(tag: str, role: str) -> bool:
    return (attr_value(tag, "role") or "").lower() == role


def _tab_name(tag: str) -> str | None:
    for attr in ("data-tab", "data-panel", "data-tab-panel", "aria-labelledby"):
        value = attr_value(tag, attr)
        if value:
            return value.lower()
    return None


def _matches_panel(tag: str, ids: Iterable[str]) -> bool:
    names = set(ids)
    tag_id = (attr_value(tag, "id") or "").lower()
    tab_name = _tab_name(tag)
    return tag_id in names or bool(tab_name and tab_name in names)


def _variant_for_tab_bar(tag: str) -> str:
    part = PART_BY_ID["bar"]
    explicit = attr_value(tag, "data-variant") or attr_value(tag, "data-bar-variant")
    if explicit in part.variant_ids:
        return explicit
    aliases: dict[str, Iterable[str]] = {
        "sticky": ["sticky-underline", "tabs-sticky"],
        "pill": ["pill-row", "tabs-pill", "pills"],
        "numbered": ["numbered-tabs", "tabs-numbered"],
        "segmented": ["segmented-tabs", "tabs-segmented", "segmented"],
    }
    classes = _classes(tag)
    for variant in part.variant_ids:
        candidates = {variant, f"bar-{variant}", f"tab-bar-{variant}", f"variant-{variant}", *aliases[variant]}
        if classes & candidates:
            return variant
    return "sticky"


def find_tab_bar(html: str) -> list[LabelRange]:
    part = PART_BY_ID["bar"]
    ranges: list[LabelRange] = []
    for variant in part.variant_ids:
        ranges.extend(
            element_ranges_by_start_tag(
                html,
                "TAB-BAR",
                lambda tag, variant=variant: (
                    has_any_class(tag, [*GTQ_TAB_BAR_CLASSES, *MDA_TAB_BAR_CLASSES])
                    or has_attr(tag, "data-part", "bar")
                    or has_attr(tag, "data-slot", "bar")
                    or _has_role(tag, "tablist")
                )
                and _variant_for_tab_bar(tag) == variant,
                "Template PART bar / GTQ tab shell/nav / MDA reading-level tabs",
                variant=variant,
            )
        )
    return ranges


def find_tab_executive_summary(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-EXECUTIVE-SUMMARY", lambda tag: _matches_panel(tag, SUMMARY_IDS), "summary / executive-summary / overview", "section")


def find_tab_paper(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-PAPER", lambda tag: _matches_panel(tag, PAPER_IDS), "paper / story / deep-dive", "section")


def find_tab_explain_it_simple(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-EXPLAIN-IT-SIMPLE", lambda tag: _matches_panel(tag, SIMPLE_IDS), "simple / plain-english / eli5", "section")


def find_tab_rigor_kill_conditions(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-RIGOR-KILL-CONDITIONS", lambda tag: _matches_panel(tag, RIGOR_IDS), "rigor / kill-conditions / falsification", "section")


def find_tab_watch_listen(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-WATCH-LISTEN", lambda tag: _matches_panel(tag, MEDIA_IDS), "media / watch-listen / audio", "section")
