"""Reading-level tab system detectors."""

from __future__ import annotations

from core.parser import LabelRange, element_ranges_by_start_tag, has_any_class, has_id


def find_tab_bar(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-BAR", lambda tag: has_any_class(tag, ["tab-bar", "tabs", "reading-tabs"]), "tab-bar / tabs / reading-tabs")


def find_tab_executive_summary(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-EXECUTIVE-SUMMARY", lambda tag: has_id(tag, "summary"), "section#summary", "section")


def find_tab_paper(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-PAPER", lambda tag: has_id(tag, "paper"), "section#paper", "section")


def find_tab_explain_it_simple(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-EXPLAIN-IT-SIMPLE", lambda tag: has_id(tag, "simple"), "section#simple", "section")


def find_tab_rigor_kill_conditions(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-RIGOR-KILL-CONDITIONS", lambda tag: has_id(tag, "rigor"), "section#rigor", "section")


def find_tab_watch_listen(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TAB-WATCH-LISTEN", lambda tag: has_id(tag, "media"), "section#media", "section")
