"""Lightweight HTML scanning helpers for component detectors."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable, Iterable


@dataclass(frozen=True)
class LabelRange:
    """A byte/character range that should be wrapped with a component marker."""

    start: int
    end: int
    marker: str
    pattern: str
    snippet: str = ""

    def as_dict(self) -> dict[str, object]:
        return {
            "marker": self.marker,
            "start": self.start,
            "end": self.end,
            "pattern": self.pattern,
            "snippet": self.snippet,
        }


START_TAG_RE = re.compile(r"<(?P<tag>[a-zA-Z][\w:-]*)(?P<attrs>\s[^<>]*?)?>", re.DOTALL)
COMMENT_RE = re.compile(r"<!--[\s\S]*?-->")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_tags(html_fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", html_fragment)
    return normalize_space(without_tags)


def iter_start_tags(html: str, tag_name: str | None = None) -> Iterable[re.Match[str]]:
    """Yield start-tag regex matches, optionally restricted to one tag name."""

    wanted = tag_name.lower() if tag_name else None
    for match in START_TAG_RE.finditer(html):
        found = match.group("tag").lower()
        if wanted is None or found == wanted:
            yield match


def attr_value(tag: str, attr: str) -> str | None:
    """Return a case-insensitive attribute value from a start tag."""

    pattern = re.compile(
        rf"\b{re.escape(attr)}\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(tag)
    if not match:
        return None
    return next(group for group in match.groups() if group is not None)


def has_attr(tag: str, attr: str, value: str | None = None) -> bool:
    found = attr_value(tag, attr)
    if found is None:
        return False
    return value is None or found == value


def has_id(tag: str, id_value: str) -> bool:
    return attr_value(tag, "id") == id_value


def has_class(tag: str, class_name: str) -> bool:
    classes = attr_value(tag, "class")
    if not classes:
        return False
    return class_name in classes.split()


def has_any_class(tag: str, class_names: Iterable[str]) -> bool:
    return any(has_class(tag, class_name) for class_name in class_names)


def find_matching_element_end(html: str, start_match: re.Match[str]) -> int:
    """Find the end offset for the element that begins at start_match.

    The scanner is intentionally lightweight and tolerant: if markup is malformed,
    it returns the end of the start tag instead of raising.
    """

    tag_name = start_match.group("tag").lower()
    start_tag = start_match.group(0)
    if start_tag.rstrip().endswith("/>"):
        return start_match.end()

    tag_re = re.compile(rf"</?{re.escape(tag_name)}\b[^>]*>", re.IGNORECASE | re.DOTALL)
    depth = 0
    for match in tag_re.finditer(html, start_match.start()):
        text = match.group(0)
        if text.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not text.rstrip().endswith("/>"):
            depth += 1
    return start_match.end()


def make_label_range(html: str, start: int, end: int, marker: str, pattern: str) -> LabelRange:
    return LabelRange(start, end, marker, pattern, strip_tags(html[start:end])[:120])


def element_ranges_by_start_tag(
    html: str,
    marker: str,
    predicate: Callable[[str], bool],
    pattern: str,
    tag_name: str | None = None,
) -> list[LabelRange]:
    ranges: list[LabelRange] = []
    for match in iter_start_tags(html, tag_name):
        tag = match.group(0)
        if predicate(tag):
            ranges.append(make_label_range(html, match.start(), find_matching_element_end(html, match), marker, pattern))
    return ranges


def comment_ranges(html: str, marker: str, predicate: Callable[[str], bool], pattern: str) -> list[LabelRange]:
    return [make_label_range(html, m.start(), m.end(), marker, pattern) for m in COMMENT_RE.finditer(html) if predicate(m.group(0))]
