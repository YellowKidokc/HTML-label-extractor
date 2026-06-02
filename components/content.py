"""Content component detectors."""

from __future__ import annotations

import re

from core.parser import LabelRange, element_ranges_by_start_tag, has_any_class, has_class, make_label_range


def find_paper_equation(html: str) -> list[LabelRange]:
    ranges = element_ranges_by_start_tag(html, "PAPER-EQUATION", lambda tag: has_class(tag, "math-box"), "math-box")
    for match in re.finditer(r"\$\$[\s\S]*?\$\$", html):
        ranges.append(make_label_range(html, match.start(), match.end(), "PAPER-EQUATION", "$$...$$"))
    return ranges


def find_kill_sidebar(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "KILL-SIDEBAR", lambda tag: tag.lower().startswith("<aside") and has_class(tag, "kill-sidebar"), "aside.kill-sidebar", "aside")


def find_kill_card_destructive(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "KILL-CARD-DESTRUCTIVE", lambda tag: has_any_class(tag, ["kill-card", "destructive"]) and has_class(tag, "destructive"), "kill-card.destructive")


def find_kill_card_suggestive(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "KILL-CARD-SUGGESTIVE", lambda tag: has_any_class(tag, ["kill-card", "suggestive"]) and has_class(tag, "suggestive"), "kill-card.suggestive")


def find_kill_card_load_bearing(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "KILL-CARD-LOAD-BEARING", lambda tag: has_any_class(tag, ["kill-card", "load-bearing"]) and has_class(tag, "load-bearing"), "kill-card.load-bearing")


def find_article_stats(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "ARTICLE-STATS", lambda tag: has_any_class(tag, ["article-stats", "stats-block"]), "article-stats / stats-block")
