"""Metadata and head-tag component detectors."""

from __future__ import annotations

from core.parser import LabelRange, attr_value, comment_ranges, element_ranges_by_start_tag, has_attr, make_label_range, START_TAG_RE, find_matching_element_end


def find_meta_block(html: str) -> list[LabelRange]:
    return comment_ranges(html, "META-BLOCK", lambda comment: "PAGE_META" in comment, "PAGE_META comment")


def find_og_tags(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "OG-TAGS", lambda tag: (attr_value(tag, "property") or "").startswith("og:"), "meta[property^=og:]", "meta")


def find_analytics(html: str) -> list[LabelRange]:
    patterns = ("google-analytics", "googletagmanager", "gtag(", "plausible", "analytics")
    ranges: list[LabelRange] = []
    for match in START_TAG_RE.finditer(html):
        if match.group("tag").lower() != "script":
            continue
        end = find_matching_element_end(html, match)
        fragment = html[match.start() : end].lower()
        if any(pattern in fragment for pattern in patterns):
            ranges.append(make_label_range(html, match.start(), end, "ANALYTICS", "analytics script"))
    return ranges
