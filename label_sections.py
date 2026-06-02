#!/usr/bin/env python3
"""CLI entry point for the modular HTML component labeler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Callable

from components.content import (
    find_article_stats,
    find_content_blocks,
    find_kill_card_destructive,
    find_kill_card_load_bearing,
    find_kill_card_suggestive,
    find_kill_sidebar,
    find_media_cards,
    find_paper_equation,
)
from components.mda_specific import (
    find_citation_block,
    find_data_table,
    find_facts_card,
    find_math_translation,
    find_one_breath,
    find_proof_layer,
    find_rigor_card,
)
from components.metadata import find_analytics, find_meta_block, find_og_tags
from components.registry import PARTS, registry_as_dict, registry_markdown_table
from components.structural import (
    find_audio_dock,
    find_bottom_nav,
    find_footer,
    find_header,
    find_hero,
    find_main_layout,
    find_series_nav,
    find_sidebar_nav,
    find_topbar,
)
from components.tabs import (
    find_tab_bar,
    find_tab_executive_summary,
    find_tab_explain_it_simple,
    find_tab_paper,
    find_tab_rigor_kill_conditions,
    find_tab_watch_listen,
)
from core.inventory import build_inventory
from core.marker import inject_markers, marker_balance
from core.parser import LabelRange

ComponentFinder = Callable[[str], list[LabelRange]]

EXCLUDE_DIRS = {"_backup", "_CHECKPOINT", "_ARCHIVE", "_ARCHIVE_WORKFLOW_ARTIFACTS", "__pycache__", ".git", "node_modules"}

COMPONENT_FINDERS: list[ComponentFinder] = [
    find_header,
    find_topbar,
    find_sidebar_nav,
    find_hero,
    find_main_layout,
    find_bottom_nav,
    find_series_nav,
    find_footer,
    find_audio_dock,
    find_tab_bar,
    find_tab_executive_summary,
    find_tab_paper,
    find_tab_explain_it_simple,
    find_tab_rigor_kill_conditions,
    find_tab_watch_listen,
    find_content_blocks,
    find_media_cards,
    find_paper_equation,
    find_kill_sidebar,
    find_kill_card_destructive,
    find_kill_card_suggestive,
    find_kill_card_load_bearing,
    find_article_stats,
    find_proof_layer,
    find_math_translation,
    find_data_table,
    find_citation_block,
    find_one_breath,
    find_facts_card,
    find_rigor_card,
    find_meta_block,
    find_og_tags,
    find_analytics,
]

CANONICAL_COMPONENTS = [
    *(part.marker for part in PARTS),
    "TOPBAR",
    "SIDEBAR-NAV",
    "BOTTOM-NAV",
    "TAB-EXECUTIVE-SUMMARY",
    "TAB-PAPER",
    "TAB-EXPLAIN-IT-SIMPLE",
    "TAB-RIGOR-KILL-CONDITIONS",
    "TAB-WATCH-LISTEN",
    "PAPER-EQUATION",
    "KILL-SIDEBAR",
    "KILL-CARD-DESTRUCTIVE",
    "KILL-CARD-SUGGESTIVE",
    "KILL-CARD-LOAD-BEARING",
    "ARTICLE-STATS",
    "PROOF-LAYER",
    "MATH-TRANSLATION",
    "DATA-TABLE",
    "CITATION-BLOCK",
    "ONE-BREATH",
    "FACTS-CARD",
    "RIGOR-CARD",
    "META-BLOCK",
    "OG-TAGS",
    "ANALYTICS",
]


def detect_components(html: str) -> list[LabelRange]:
    ranges: list[LabelRange] = []
    for finder in COMPONENT_FINDERS:
        ranges.extend(finder(html))
    return sorted(ranges, key=lambda item: (item.start, item.end, item.marker))


def label_html(html: str) -> tuple[str, list[LabelRange]]:
    ranges = detect_components(html)
    return inject_markers(html, ranges), ranges


def html_files(path: Path, recursive: bool = False) -> list[Path]:
    if path.is_file():
        return [path]
    if recursive:
        return sorted(
            candidate
            for candidate in path.rglob("*.html")
            if candidate.is_file() and not any(excluded in candidate.parts for excluded in EXCLUDE_DIRS)
        )
    return sorted(path.glob("*.html"))


def output_path_for(path: Path) -> Path:
    return path.with_name(f"{path.stem}.labeled{path.suffix}")


def process_file(path: Path, in_place: bool = False) -> dict[str, object]:
    html = path.read_text(encoding="utf-8")
    labeled, ranges = label_html(html)
    if in_place:
        backup = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, backup)
        path.write_text(labeled, encoding="utf-8")
        output = path
    else:
        output = output_path_for(path)
        output.write_text(labeled, encoding="utf-8")
    inventory = build_inventory(html, ranges)
    inventory["file"] = str(path)
    inventory["output"] = str(output)
    return inventory


def audit_file(path: Path) -> dict[str, object]:
    html = path.read_text(encoding="utf-8")
    ranges = detect_components(html)
    inventory = build_inventory(html, ranges)
    found = set(inventory["component_counts"].keys())
    inventory.update(
        {
            "file": str(path),
            "present": sorted(found),
            "missing": [component for component in CANONICAL_COMPONENTS if component not in found],
            "balanced": all(item["balanced"] for item in marker_balance(html).values()),
        }
    )
    return inventory


def markdown_coverage_table(rows: list[dict[str, object]]) -> str:
    visible_components = [component for component in CANONICAL_COMPONENTS if any(component in row["present"] for row in rows)]
    if not visible_components:
        visible_components = CANONICAL_COMPONENTS[:]
    header = ["File", *visible_components, "Markers Balanced"]
    lines = ["Component Coverage Report", "=========================", "", "| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in rows:
        present = set(row["present"])
        cells = [Path(str(row["file"])).name, *["✅" if component in present else "❌" for component in visible_components], "✅" if row["balanced"] else "❌"]
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(["", "Missing components by frequency:"])
    for component in CANONICAL_COMPONENTS:
        missing_count = sum(1 for row in rows if component in row["missing"])
        if missing_count:
            lines.append(f"  {component}: {missing_count}/{len(rows)} files missing")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan HTML files and wrap recognized components with canonical markers.")
    parser.add_argument("path", type=Path, nargs="?", help="HTML file or directory to scan")
    parser.add_argument("--recursive", action="store_true", help="Recurse into directories when path is a folder")
    parser.add_argument("--in-place", action="store_true", help="Modify source files in place after creating .bak backups")
    parser.add_argument("--audit-only", action="store_true", help="Report component coverage without writing labeled files")
    parser.add_argument("--json", action="store_true", help="Emit JSON inventory instead of human-readable text")
    parser.add_argument("--registry", action="store_true", help="Print the Template Builder PARTS vocabulary and exit")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.registry:
        print(json.dumps(registry_as_dict(), indent=2) if args.json else registry_markdown_table())
        return 0
    if args.path is None:
        print("A path is required unless --registry is used", file=sys.stderr)
        return 1

    paths = html_files(args.path, args.recursive)
    if not paths:
        print(f"No HTML files found at {args.path}", file=sys.stderr)
        return 1

    if args.audit_only:
        rows = [audit_file(path) for path in paths]
        print(json.dumps(rows, indent=2) if args.json else markdown_coverage_table(rows))
        return 0

    inventories = [process_file(path, args.in_place) for path in paths]
    if args.json:
        print(json.dumps(inventories[0] if len(inventories) == 1 else inventories, indent=2))
    else:
        for item in inventories:
            print(f"Labeled {item['file']} -> {item['output']} ({len(item['components'])} components)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
