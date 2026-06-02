"""BEGIN/END marker injection utilities."""

from __future__ import annotations

from collections import Counter
import re

from core.parser import LabelRange


BEGIN_RE = re.compile(r"<!--\s*BEGIN:\s*([A-Z0-9-]+)\s*-->")
END_RE = re.compile(r"<!--\s*END:\s*([A-Z0-9-]+)\s*-->")


def inject_markers(html: str, ranges: list[LabelRange]) -> str:
    """Wrap ranges with canonical component markers.

    Marker events are composed against the original offsets in one pass. This
    keeps nested component ranges valid without offset drift from earlier
    insertions. Duplicate exact ranges are ignored.
    """

    deduped = list({(item.start, item.end, item.marker): item for item in ranges}.values())
    starts: dict[int, list[LabelRange]] = {}
    ends: dict[int, list[LabelRange]] = {}
    for item in deduped:
        if item.start < 0 or item.end > len(html) or item.start >= item.end:
            continue
        starts.setdefault(item.start, []).append(item)
        ends.setdefault(item.end, []).append(item)

    parts: list[str] = []
    for position in range(len(html) + 1):
        if position in ends:
            for item in sorted(ends[position], key=lambda r: r.start, reverse=True):
                parts.append(f"\n<!-- END: {item.marker} -->")
        if position in starts:
            for item in sorted(starts[position], key=lambda r: r.end, reverse=True):
                parts.append(f"<!-- BEGIN: {item.marker} -->\n")
        if position < len(html):
            parts.append(html[position])
    return "".join(parts)


def marker_balance(html: str) -> dict[str, dict[str, int | bool]]:
    begins = Counter(BEGIN_RE.findall(html))
    ends = Counter(END_RE.findall(html))
    markers = sorted(set(begins) | set(ends))
    return {
        marker: {"begin": begins[marker], "end": ends[marker], "balanced": begins[marker] == ends[marker]}
        for marker in markers
    }
