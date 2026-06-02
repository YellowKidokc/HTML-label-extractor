"""MDA-specific component detectors."""

from __future__ import annotations

from core.parser import LabelRange, attr_value, element_ranges_by_start_tag, has_any_class, has_attr, has_class, has_id, make_label_range, START_TAG_RE, find_matching_element_end


def find_proof_layer(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "PROOF-LAYER",
        lambda tag: has_any_class(tag, ["proof-panel", "proof-pressure", "proof-layer", "proof-stack", "proof-card", "evidence-panel", "evidence-card"])
        or has_attr(tag, "data-component", "proof")
        or has_attr(tag, "data-layer", "proof"),
        "proof-panel / proof-pressure / proof-layer / evidence-panel / data-component=proof",
    )


def find_math_translation(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "MATH-TRANSLATION",
        lambda tag: has_any_class(tag, ["math-translation", "collapsible-math", "math-english", "equation-translation", "translation-panel", "collapsible-translation"])
        or has_attr(tag, "data-layer", "math-translation")
        or has_attr(tag, "data-component", "math-translation"),
        "math-translation / collapsible-math / math-english / data-layer",
    )


def find_data_table(html: str) -> list[LabelRange]:
    ranges = element_ranges_by_start_tag(html, "DATA-TABLE", lambda tag: has_any_class(tag, ["data-table", "evidence-table"]), "table.data-table / table.evidence-table", "table")
    for match in START_TAG_RE.finditer(html):
        tag = match.group(0)
        if match.group("tag").lower() == "div" and has_class(tag, "data-panel"):
            ranges.append(make_label_range(html, match.start(), find_matching_element_end(html, match), "DATA-TABLE", "div.data-panel"))
    return ranges


def find_citation_block(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "CITATION-BLOCK", lambda tag: has_any_class(tag, ["citation", "sources", "references"]) or has_id(tag, "citations"), "citation / sources / references / #citations")


def find_one_breath(html: str) -> list[LabelRange]:
    ranges = element_ranges_by_start_tag(html, "ONE-BREATH", lambda tag: has_any_class(tag, ["one-breath", "article-summary", "one-breath-summary", "lede", "dek", "mda-summary"]), "one-breath / article-summary / MDA lede or dek")
    for match in START_TAG_RE.finditer(html):
        tag = match.group(0)
        if match.group("tag").lower() == "p" and has_class(tag, "lead"):
            ranges.append(make_label_range(html, match.start(), find_matching_element_end(html, match), "ONE-BREATH", "p.lead"))
            break
    return ranges


def find_facts_card(html: str) -> list[LabelRange]:
    ranges = element_ranges_by_start_tag(html, "FACTS-CARD", lambda tag: has_class(tag, "facts-card"), "facts-card")
    phrase = "Falsifiable, Anchored, Cross-domain, Testable, Structurally"
    index = html.find(phrase)
    if index != -1 and not ranges:
        for match in reversed(list(START_TAG_RE.finditer(html[:index]))):
            end = find_matching_element_end(html, match)
            if end >= index + len(phrase):
                ranges.append(make_label_range(html, match.start(), end, "FACTS-CARD", "FACTS phrase"))
                break
    return ranges


def find_rigor_card(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "RIGOR-CARD", lambda tag: has_any_class(tag, ["rigor-card", "falsification-card"]), "rigor-card / falsification-card")
