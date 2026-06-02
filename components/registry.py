"""Template Builder PARTS registry shared by labeler and future assembler.

The PARTS registry mirrors ``Template_Builder__standalone_.html`` and is the
single source of truth for top-level component slots and visual variants.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PartVariant:
    """A visual variant that can be emitted by the Template Builder."""

    id: str
    name: str


@dataclass(frozen=True)
class PartSlot:
    """A top-level component slot from the Template Builder PARTS registry."""

    id: str
    name: str
    num: str
    marker: str
    variants: tuple[PartVariant, ...]
    detector_name: str

    @property
    def variant_ids(self) -> tuple[str, ...]:
        return tuple(variant.id for variant in self.variants)


PARTS: tuple[PartSlot, ...] = (
    PartSlot(
        id="header",
        name="Header",
        num="01",
        marker="HEADER",
        detector_name="find_header",
        variants=(
            PartVariant("classic", "Classic"),
            PartVariant("watermark", "Watermark"),
            PartVariant("forensic", "Forensic"),
            PartVariant("centered", "Centered sun"),
        ),
    ),
    PartSlot(
        id="bar",
        name="Middle Bar (Tabs)",
        num="02",
        marker="TAB-BAR",
        detector_name="find_tab_bar",
        variants=(
            PartVariant("sticky", "Sticky underline"),
            PartVariant("pill", "Pill row"),
            PartVariant("numbered", "Numbered"),
            PartVariant("segmented", "Segmented"),
        ),
    ),
    PartSlot(
        id="player",
        name="TTS / Audio Player",
        num="03",
        marker="AUDIO-DOCK",
        detector_name="find_audio_dock",
        variants=(
            PartVariant("bar", "Inline bar"),
            PartVariant("card", "Big media card"),
            PartVariant("dock", "Docked mini"),
            PartVariant("dual", "Dual player"),
        ),
    ),
    PartSlot(
        id="hero",
        name="Hero Intro",
        num="04",
        marker="HERO",
        detector_name="find_hero",
        variants=(
            PartVariant("grid", "Grid w/ sidecards"),
            PartVariant("pullquote", "Pull quote"),
            PartVariant("stats", "Stat row"),
            PartVariant("formula", "Equation of motion"),
        ),
    ),
    PartSlot(
        id="body",
        name="Story Body",
        num="05",
        marker="MAIN-LAYOUT",
        detector_name="find_main_layout",
        variants=(
            PartVariant("column", "Single column"),
            PartVariant("sidebar", "TOC sidebar"),
            PartVariant("sections", "Roman-numeral §"),
            PartVariant("insight", "With callout boxes"),
        ),
    ),
    PartSlot(
        id="blocks",
        name="Content Blocks",
        num="05b",
        marker="CONTENT-BLOCK",
        detector_name="find_content_blocks",
        variants=(
            PartVariant("none", "None"),
            PartVariant("stat4", "Stat row"),
            PartVariant("accent", "Accent grid"),
            PartVariant("ghost", "Ghost quotes"),
            PartVariant("callout", "Callout"),
            PartVariant("split", "Split cards"),
            PartVariant("timeline", "Timeline"),
            PartVariant("pills", "Pill badges"),
            PartVariant("hero", "Hero card"),
            PartVariant("shadow", "Shadow box"),
            PartVariant("mix", "Mixed"),
        ),
    ),
    PartSlot(
        id="media",
        name="Media Cards",
        num="06",
        marker="MEDIA-CARDS",
        detector_name="find_media_cards",
        variants=(
            PartVariant("stacked", "Stacked list"),
            PartVariant("grid", "Resource grid"),
            PartVariant("strip", "Scroll strip"),
        ),
    ),
    PartSlot(
        id="snav",
        name="Series Navigation",
        num="07",
        marker="SERIES-NAV",
        detector_name="find_series_nav",
        variants=(
            PartVariant("rail", "Left rail"),
            PartVariant("bread", "Breadcrumb"),
            PartVariant("prevnext", "Prev/next"),
            PartVariant("dots", "Dot position"),
        ),
    ),
    PartSlot(
        id="footer",
        name="Footer",
        num="08",
        marker="FOOTER",
        detector_name="find_footer",
        variants=(
            PartVariant("min", "Minimal"),
            PartVariant("colophon", "Colophon"),
            PartVariant("stamp", "Signature mark"),
        ),
    ),
)

PART_BY_ID = {part.id: part for part in PARTS}
PART_BY_MARKER = {part.marker: part for part in PARTS}
TOP_LEVEL_MARKERS = tuple(part.marker for part in PARTS)


def registry_as_dict() -> list[dict[str, object]]:
    """Return a JSON-serializable representation of the PARTS registry."""

    return [
        {
            "id": part.id,
            "name": part.name,
            "num": part.num,
            "marker": part.marker,
            "detector": part.detector_name,
            "variants": [{"id": variant.id, "name": variant.name} for variant in part.variants],
        }
        for part in PARTS
    ]


def registry_markdown_table() -> str:
    """Render the full top-level vocabulary as a Markdown table."""

    lines = [
        "Template Builder PARTS Registry",
        "===============================",
        "",
        "| # | Slot | Marker | Detector | Variants |",
        "| --- | --- | --- | --- | --- |",
    ]
    for part in PARTS:
        variants = ", ".join(f"{variant.id} ({variant.name})" for variant in part.variants)
        lines.append(f"| {part.num} | {part.name} | `{part.marker}` | `{part.detector_name}` | {variants} |")
    return "\n".join(lines)
