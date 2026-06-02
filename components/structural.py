"""Structural and Template Builder top-level component detectors."""

from __future__ import annotations

from collections.abc import Iterable

from components.registry import PART_BY_ID
from core.parser import (
    LabelRange,
    attr_value,
    element_ranges_by_start_tag,
    has_any_class,
    has_attr,
    has_class,
    has_id,
)

GTQ_TOPBAR_CLASSES = ["site-header", "canon-bar", "gtq-canon-bar"]
MDA_TOPBAR_CLASSES = ["mda-topbar", "mda-header", "mda-nav", "topbar", "top-bar", "top-nav", "article-topbar", "masthead", "global-header"]

GTQ_HERO_CLASSES = ["hero-grid", "article-hero-wrap"]
MDA_HERO_CLASSES = ["mda-hero", "article-hero", "hero", "hero-wrap", "intro-hero", "article-intro", "mda-intro", "opening-panel"]

GTQ_SIDEBAR_CLASSES = ["sidebar"]
MDA_SIDEBAR_CLASSES = ["mda-sidebar", "article-sidebar", "toc-sidebar", "sidebar-nav", "side-nav", "article-toc", "toc-nav", "series-rail", "left-rail", "rail-nav"]

GTQ_MAIN_CLASSES = ["main-layout", "container"]
MDA_MAIN_CLASSES = ["mda-main", "article-main", "article-body", "article-content", "story-body", "story-content", "paper-body", "paper-content", "content-shell", "reading-shell"]

GTQ_BOTTOM_NAV_CLASSES = ["bottom-nav", "article-nav"]
MDA_BOTTOM_NAV_CLASSES = ["mda-bottom-nav", "prev-next", "prevnext", "post-nav", "pager", "article-footer-nav", "series-footer-nav", "series-next-prev"]

GTQ_AUDIO_CLASSES = ["audio-dock", "tts-player", "audio-player", "media-card"]
MDA_AUDIO_CLASSES = ["mda-audio-dock", "mda-audio", "narration-player", "tts-dock", "tts-bar", "mini-player", "audio-controls", "audio-module"]
MDA_AUDIO_IDS = ["audioDock", "ttsDock", "narrationDock", "playerDock", "audioPlayer", "ttsPlayer"]

GTQ_SERIES_NAV_CLASSES = ["series-nav", "bottom-nav", "article-nav", "breadcrumb", "breadcrumbs", "series-rail", "dot-nav"]
MDA_SERIES_NAV_CLASSES = ["mda-series-nav", "series-footer-nav", "series-next-prev", "chapter-nav", "story-nav", *MDA_BOTTOM_NAV_CLASSES]


def _class_tokens(tag: str) -> set[str]:
    classes = attr_value(tag, "class") or ""
    return set(classes.split())


def _data_variant(tag: str, part_id: str) -> str | None:
    for attr in ("data-variant", "data-part-variant", f"data-{part_id}-variant"):
        value = attr_value(tag, attr)
        if value:
            return value
    return None


def _has_any_id(tag: str, ids: Iterable[str]) -> bool:
    return any(has_id(tag, id_value) for id_value in ids)


def _part_match(tag: str, part_id: str) -> bool:
    part = PART_BY_ID[part_id]
    return (
        has_attr(tag, "data-part", part_id)
        or has_attr(tag, "data-component", part_id)
        or has_attr(tag, "data-slot", part_id)
        or has_class(tag, f"part-{part_id}")
        or has_class(tag, f"slot-{part_id}")
        or has_class(tag, part.marker.lower())
    )


def _variant_for(tag: str, part_id: str, fallback: str, aliases: dict[str, Iterable[str]] | None = None) -> str:
    part = PART_BY_ID[part_id]
    allowed = set(part.variant_ids)
    explicit = _data_variant(tag, part_id)
    if explicit in allowed:
        return explicit

    classes = _class_tokens(tag)
    for variant in part.variant_ids:
        candidates = {
            variant,
            f"{part_id}-{variant}",
            f"{part.marker.lower()}-{variant}",
            f"variant-{variant}",
        }
        if aliases and variant in aliases:
            candidates.update(aliases[variant])
        if classes & candidates:
            return variant
    return fallback


def _top_level_ranges(
    html: str,
    part_id: str,
    fallback_variant: str,
    predicate,
    pattern: str,
    tag_name: str | None = None,
    aliases: dict[str, Iterable[str]] | None = None,
) -> list[LabelRange]:
    part = PART_BY_ID[part_id]
    ranges: list[LabelRange] = []
    for variant in part.variant_ids:
        ranges.extend(
            element_ranges_by_start_tag(
                html,
                part.marker,
                lambda tag, variant=variant: predicate(tag) and _variant_for(tag, part_id, fallback_variant, aliases) == variant,
                pattern,
                tag_name,
                variant,
            )
        )
    return ranges


def find_header(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "header",
        "classic",
        lambda tag: tag.lower().startswith("<header") or has_any_class(tag, [*GTQ_TOPBAR_CLASSES, *MDA_TOPBAR_CLASSES]) or _part_match(tag, "header"),
        "Template PART header / header / GTQ topbar / MDA topbar",
        aliases={"centered": ["centered-sun", "sun-centered"]},
    )


def find_topbar(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "TOPBAR",
        lambda tag: tag.lower().startswith("<header") or has_any_class(tag, [*GTQ_TOPBAR_CLASSES, *MDA_TOPBAR_CLASSES]),
        "site-header / canon-bar / mda-topbar / mda-header / top-nav",
    )


def find_sidebar_nav(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "SIDEBAR-NAV",
        lambda tag: tag.lower().startswith(("<nav", "<aside")) and has_any_class(tag, [*GTQ_SIDEBAR_CLASSES, *MDA_SIDEBAR_CLASSES]),
        "nav.sidebar / MDA sidebar or TOC rail",
    )


def find_hero(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "hero",
        "grid",
        lambda tag: has_any_class(tag, [*GTQ_HERO_CLASSES, *MDA_HERO_CLASSES]) or _part_match(tag, "hero"),
        "Template PART hero / GTQ hero / MDA hero or intro",
        aliases={"pullquote": ["pull-quote", "hero-pullquote"], "stats": ["stat-row", "hero-stats"], "formula": ["equation-motion", "hero-formula"]},
    )


def find_main_layout(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "body",
        "column",
        lambda tag: tag.lower().startswith("<main") or has_any_class(tag, MDA_MAIN_CLASSES) or _part_match(tag, "body"),
        "Template PART body / main.main-layout / main.container / MDA article body",
        aliases={"sections": ["roman-sections", "sectioned"], "insight": ["callout-boxes", "with-callouts"]},
    )


def find_bottom_nav(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "BOTTOM-NAV",
        lambda tag: has_any_class(tag, [*GTQ_BOTTOM_NAV_CLASSES, *MDA_BOTTOM_NAV_CLASSES]),
        "bottom-nav / article-nav / MDA prev-next navigation",
    )


def find_series_nav(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "snav",
        "prevnext",
        lambda tag: has_any_class(tag, [*GTQ_SERIES_NAV_CLASSES, *MDA_SERIES_NAV_CLASSES]) or _part_match(tag, "snav"),
        "Template PART snav / GTQ series nav / MDA series nav",
        aliases={"bread": ["breadcrumb", "breadcrumbs"], "prevnext": ["bottom-nav", "article-nav", "prev-next", "prevnext", "series-next-prev"], "dots": ["dot-nav", "position-dots"], "rail": ["series-rail", "left-rail"]},
    )


def find_footer(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "footer",
        "min",
        lambda tag: tag.lower().startswith("<footer") or has_class(tag, "site-footer") or _part_match(tag, "footer"),
        "Template PART footer / footer / site-footer",
        aliases={"min": ["minimal"], "stamp": ["signature", "signature-mark"]},
    )


def find_audio_dock(html: str) -> list[LabelRange]:
    return _top_level_ranges(
        html,
        "player",
        "dock",
        lambda tag: _has_any_id(tag, MDA_AUDIO_IDS) or has_any_class(tag, [*GTQ_AUDIO_CLASSES, *MDA_AUDIO_CLASSES]) or _part_match(tag, "player"),
        "Template PART player / audioDock / audio-dock / MDA TTS or narration player",
        aliases={"bar": ["inline-bar", "audio-bar", "tts-bar"], "card": ["media-card", "big-media-card", "audio-module"], "dock": ["audio-dock", "docked-mini", "mda-audio-dock", "tts-dock"], "dual": ["dual-player"]},
    )
