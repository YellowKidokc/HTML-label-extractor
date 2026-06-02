"""JSON inventory builder for detected components and paragraph classes."""

from __future__ import annotations

from collections import Counter
import re

from core.marker import marker_balance
from core.parser import LabelRange, START_TAG_RE, attr_value, find_matching_element_end, has_class, strip_tags

CLAIM_WORDS = {"proves", "prove", "must", "cannot", "always", "never"}
EVIDENCE_WORDS = {"data", "sigma", "correlation", "source", "table", "study", "evidence"}
TRANSITIONS = ("however", "therefore", "moreover", "nevertheless", "thus", "consequently")
BOILERPLATE_WORDS = {"copyright", "subscribe", "navigation", "privacy", "terms"}


def classify_paragraph(text: str, link_count: int = 0) -> str:
    normalized = strip_tags(text)
    lower = normalized.lower()
    words = re.findall(r"[A-Za-z0-9’'-]+", normalized)
    word_count = len(words)
    link_density = link_count / max(word_count, 1)

    if any(word in lower for word in BOILERPLATE_WORDS) or (word_count < 12 and link_count > 0) or link_density > 0.15:
        return "BOILERPLATE"
    if lower.startswith(TRANSITIONS):
        return "TRANSITION"
    if ":=" in text or "is defined as" in lower or re.search(r"\w+\s+—\s+", normalized):
        return "DEFINITION"
    if any(re.search(rf"\b{re.escape(word)}\b", lower) for word in CLAIM_WORDS):
        return "CLAIM"
    if any(re.search(rf"\b{re.escape(word)}\b", lower) for word in EVIDENCE_WORDS):
        return "EVIDENCE"
    if word_count > 50 and link_count == 0:
        return "NARRATIVE"
    return "NARRATIVE"


def paragraph_inventory(html: str) -> list[dict[str, object]]:
    paragraphs: list[dict[str, object]] = []
    for match in START_TAG_RE.finditer(html):
        if match.group("tag").lower() != "p":
            continue
        end = find_matching_element_end(html, match)
        fragment = html[match.start() : end]
        text = strip_tags(fragment)
        link_count = len(re.findall(r"<a\b", fragment, re.IGNORECASE))
        paragraphs.append(
            {
                "start": match.start(),
                "end": end,
                "class": classify_paragraph(fragment, link_count),
                "word_count": len(re.findall(r"[A-Za-z0-9’'-]+", text)),
                "link_count": link_count,
                "text": text[:160],
            }
        )
    return paragraphs


def build_inventory(html: str, ranges: list[LabelRange]) -> dict[str, object]:
    counts = Counter(item.marker for item in ranges)
    return {
        "components": [item.as_dict() for item in sorted(ranges, key=lambda r: (r.start, r.end, r.marker))],
        "component_counts": dict(sorted(counts.items())),
        "paragraphs": paragraph_inventory(html),
        "marker_balance": marker_balance(html),
    }
