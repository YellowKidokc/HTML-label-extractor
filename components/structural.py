"""Structural component detectors."""

from __future__ import annotations

from core.parser import LabelRange, element_ranges_by_start_tag, has_any_class, has_class, has_id


def find_topbar(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "TOPBAR", lambda tag: has_any_class(tag, ["site-header", "canon-bar"]), "site-header / canon-bar")


def find_sidebar_nav(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "SIDEBAR-NAV", lambda tag: tag.lower().startswith("<nav") and has_class(tag, "sidebar"), "nav.sidebar", "nav")


def find_hero(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "HERO", lambda tag: has_any_class(tag, ["hero-grid", "article-hero-wrap"]), "hero-grid / article-hero-wrap")


def find_main_layout(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "MAIN-LAYOUT",
        lambda tag: tag.lower().startswith("<main") and has_any_class(tag, ["main-layout", "container"]),
        "main.main-layout / main.container",
        "main",
    )


def find_bottom_nav(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "BOTTOM-NAV", lambda tag: has_any_class(tag, ["bottom-nav", "article-nav"]), "bottom-nav / article-nav")


def find_footer(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "FOOTER", lambda tag: tag.lower().startswith("<footer") or has_class(tag, "site-footer"), "footer / site-footer")


def find_audio_dock(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "AUDIO-DOCK", lambda tag: has_id(tag, "audioDock") or has_class(tag, "audio-dock"), "audioDock / audio-dock")
