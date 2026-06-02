"""Content component detectors."""

from __future__ import annotations

import re

from components.registry import PART_BY_ID
from core.parser import LabelRange, attr_value, element_ranges_by_start_tag, has_any_class, has_attr, has_class, make_label_range


def _classes(tag: str) -> set[str]:
    return set((attr_value(tag, "class") or "").split())


def _variant_for(part_id: str, tag: str, fallback: str, aliases: dict[str, list[str]]) -> str:
    part = PART_BY_ID[part_id]
    explicit = attr_value(tag, "data-variant") or attr_value(tag, f"data-{part_id}-variant")
    if explicit in part.variant_ids:
        return explicit
    classes = _classes(tag)
    for variant in part.variant_ids:
        candidates = {variant, f"{part_id}-{variant}", f"variant-{variant}", *aliases.get(variant, [])}
        if classes & candidates:
            return variant
    return fallback


def find_content_blocks(html: str) -> list[LabelRange]:
    part = PART_BY_ID["blocks"]
    aliases = {
        "stat4": ["stat-row", "stats-row", "article-stats"],
        "accent": ["accent-grid"],
        "ghost": ["ghost-quotes", "ghost-quote"],
        "callout": ["callout", "callout-box"],
        "split": ["split-cards", "split-card"],
        "timeline": ["timeline"],
        "pills": ["pill-badges", "badges"],
        "hero": ["hero-card"],
        "shadow": ["shadow-box"],
        "mix": ["mixed", "mixed-blocks"],
    }
    ranges: list[LabelRange] = []
    for variant in part.variant_ids:
        ranges.extend(
            element_ranges_by_start_tag(
                html,
                "CONTENT-BLOCK",
                lambda tag, variant=variant: (
                    has_any_class(tag, ["content-block", "stat-row", "accent-grid", "ghost-quote", "callout", "split-cards", "timeline", "pill-badges", "hero-card", "shadow-box", "mixed-blocks"])
                    or has_attr(tag, "data-part", "blocks")
                    or has_attr(tag, "data-slot", "blocks")
                )
                and _variant_for("blocks", tag, "mix", aliases) == variant,
                "Template PART blocks / content block variants",
                variant=variant,
            )
        )
    return ranges


def find_media_cards(html: str) -> list[LabelRange]:
    part = PART_BY_ID["media"]
    aliases = {"stacked": ["media-stacked", "stacked-list"], "grid": ["media-grid", "resource-grid"], "strip": ["media-strip", "scroll-strip"]}
    ranges: list[LabelRange] = []
    for variant in part.variant_ids:
        ranges.extend(
            element_ranges_by_start_tag(
                html,
                "MEDIA-CARDS",
                lambda tag, variant=variant: (
                    has_any_class(tag, ["media-cards", "media-grid", "resource-grid", "media-strip", "scroll-strip", "media-stacked"])
                    or has_attr(tag, "data-part", "media")
                    or has_attr(tag, "data-slot", "media")
                )
                and _variant_for("media", tag, "stacked", aliases) == variant,
                "Template PART media / media card variants",
                variant=variant,
            )
        )
    return ranges


def find_paper_equation(html: str) -> list[LabelRange]:
    ranges = element_ranges_by_start_tag(html, "PAPER-EQUATION", lambda tag: has_class(tag, "math-box"), "math-box")
    for match in re.finditer(r"\$\$[\s\S]*?\$\$", html):
        ranges.append(make_label_range(html, match.start(), match.end(), "PAPER-EQUATION", "$$...$$"))
    return ranges


def _kill_type(tag: str) -> str | None:
    for attr in ("data-kill-type", "data-rigor", "data-card-type"):
        value = attr_value(tag, attr)
        if value:
            return value
    return None


def find_kill_sidebar(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "KILL-SIDEBAR",
        lambda tag: tag.lower().startswith(("<aside", "<section", "<div"))
        and has_any_class(tag, ["kill-sidebar", "kill-conditions", "kill-panel", "falsification-sidebar", "falsification-panel", "rigor-sidebar"]),
        "aside.kill-sidebar / MDA kill-conditions or falsification panel",
    )


def find_kill_card_destructive(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "KILL-CARD-DESTRUCTIVE",
        lambda tag: (has_any_class(tag, ["kill-card", "condition-card", "rigor-card", "falsification-card"]) and has_any_class(tag, ["destructive", "kill-card--destructive", "is-destructive"]))
        or _kill_type(tag) == "destructive",
        "kill-card.destructive / MDA destructive kill card",
    )


def find_kill_card_suggestive(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "KILL-CARD-SUGGESTIVE",
        lambda tag: (has_any_class(tag, ["kill-card", "condition-card", "rigor-card", "falsification-card"]) and has_any_class(tag, ["suggestive", "kill-card--suggestive", "is-suggestive"]))
        or _kill_type(tag) == "suggestive",
        "kill-card.suggestive / MDA suggestive kill card",
    )


def find_kill_card_load_bearing(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "KILL-CARD-LOAD-BEARING",
        lambda tag: (has_any_class(tag, ["kill-card", "condition-card", "rigor-card", "falsification-card"]) and has_any_class(tag, ["load-bearing", "kill-card--load-bearing", "is-load-bearing"]))
        or _kill_type(tag) == "load-bearing",
        "kill-card.load-bearing / MDA load-bearing kill card",
    )


def find_article_stats(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "ARTICLE-STATS", lambda tag: has_any_class(tag, ["article-stats", "stats-block"]), "article-stats / stats-block")
