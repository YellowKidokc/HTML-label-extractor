# html-component-labeler

Modular HTML component scanner and labeler for the Theophysics publication pipeline.

## What it does

Scans HTML article files and wraps every recognized component with canonical markers:

```html
<!-- BEGIN: HERO:grid -->
<section class="hero-grid">...</section>
<!-- END: HERO:grid -->

<!-- BEGIN: TAB-PAPER -->
<section id="paper">...</section>
<!-- END: TAB-PAPER -->

<!-- BEGIN: PAPER-EQUATION -->
$$dS/dt \geq 0$$
<!-- END: PAPER-EQUATION -->
```

These markers make the HTML machine-readable — scripts can find, extract, replace, or validate any component without parsing the full DOM.

## Canonical Component Vocabulary

**Source of truth:** `Template_Builder__standalone_.html` PARTS registry, mirrored in `components/registry.py`.

The Template Builder defines 9 top-level component slots with 37 visual variants. The labeler detects those slots and records which variant is in use. The assembler can import the same registry so all tools share one vocabulary: Template Builder defines → Labeler detects → Assembler fills.

| # | Slot | Variants | Labeler Marker |
|---|------|----------|----------------|
| 01 | Header | Classic, Watermark, Forensic, Centered sun | `HEADER` |
| 02 | Middle Bar (Tabs) | Sticky underline, Pill row, Numbered, Segmented | `TAB-BAR` |
| 03 | TTS / Audio Player | Inline bar, Big media card, Docked mini, Dual player | `AUDIO-DOCK` |
| 04 | Hero Intro | Grid w/ sidecards, Pull quote, Stat row, Equation of motion | `HERO` |
| 05 | Story Body | Single column, TOC sidebar, Roman-numeral §, With callout boxes | `MAIN-LAYOUT` |
| 05b | Content Blocks | None, Stat row, Accent grid, Ghost quotes, Callout, Split cards, Timeline, Pill badges, Hero card, Shadow box, Mixed | `CONTENT-BLOCK` |
| 06 | Media Cards | Stacked list, Resource grid, Scroll strip | `MEDIA-CARDS` |
| 07 | Series Navigation | Left rail, Breadcrumb, Prev/next, Dot position | `SERIES-NAV` |
| 08 | Footer | Minimal, Colophon, Signature mark | `FOOTER` |

Variant-aware ranges use qualified marker names such as `HEADER:watermark`, `TAB-BAR:pill`, and `CONTENT-BLOCK:timeline` in both injected HTML markers and JSON inventory output.

The labeler also detects sub-components within these slots, including tab contents, equations, kill cards, metadata, and MDA-specific blocks.

## Component Types

### Template Builder top-level slots
| Marker | What it finds |
|--------|--------------|
| `HEADER:*` | Header slot variants from `data-part="header"`, header classes, or legacy site header markup |
| `TAB-BAR:*` | Middle/tab bar variants from `data-part="bar"`, tab classes, or reading tab markup |
| `AUDIO-DOCK:*` | Audio/TTS player variants from `data-part="player"`, audio dock classes, or audio player IDs |
| `HERO:*` | Hero intro variants from `data-part="hero"`, hero classes, or article hero wrappers |
| `MAIN-LAYOUT:*` | Story body variants from `data-part="body"` or main layout containers |
| `CONTENT-BLOCK:*` | Content block variants from `data-part="blocks"` or block-specific classes |
| `MEDIA-CARDS:*` | Media card variants from `data-part="media"` or media card classes |
| `SERIES-NAV:*` | Series navigation variants from `data-part="snav"`, breadcrumbs, rails, dots, or prev/next links |
| `FOOTER:*` | Footer variants from `data-part="footer"`, `<footer>`, or site footer classes |

### Legacy structural aliases
| Marker | What it finds | Detection method |
|--------|--------------|-----------------|
| `TOPBAR` | Site navigation bar | `class="site-header"` / `class="canon-bar"` |
| `SIDEBAR-NAV` | Series sidebar navigation | `nav.sidebar` |
| `BOTTOM-NAV` | Prev/next article links | `class="bottom-nav"` / `class="article-nav"` |

### Tab System
| Marker | What it finds |
|--------|--------------|
| `TAB-EXECUTIVE-SUMMARY` | Summary tab (`section#summary`) |
| `TAB-PAPER` | Main paper/story tab (`section#paper`) |
| `TAB-EXPLAIN-IT-SIMPLE` | Simple explanation tab (`section#simple`) |
| `TAB-RIGOR-KILL-CONDITIONS` | Kill conditions tab (`section#rigor`) |
| `TAB-WATCH-LISTEN` | Media tab (`section#media`) |

### Content
| Marker | What it finds |
|--------|--------------|
| `PAPER-EQUATION` | Math blocks (`class="math-box"` / `$$...$$`) |
| `KILL-SIDEBAR` | Kill condition sidebar (`aside.kill-sidebar`) |
| `KILL-CARD-*` | Kill cards (destructive/suggestive/load-bearing) |
| `ARTICLE-STATS` | Statistics block after kill cards |

### MDA-specific
| Marker | What it finds |
|--------|-------------|
| `PROOF-LAYER` | Proof pressure panels |
| `MATH-TRANSLATION` | Collapsible math-to-English translation blocks |
| `DATA-TABLE` | Evidence data tables |
| `CITATION-BLOCK` | Source citation blocks |
| `META-BLOCK` | PAGE_META comment block |
| `OG-TAGS` | Open Graph meta tags |
| `ANALYTICS` | Analytics script tags |
| `ONE-BREATH` | One-breath summary line |
| `FACTS-CARD` | FACTS methodology card |
| `RIGOR-CARD` | Rigor/falsification card |

## Usage

```bash
# Label a single file (writes labeled copy alongside original)
python label_sections.py article.html

# Label a folder recursively
python label_sections.py path/to/articles --recursive

# Label in-place (modifies original, creates backup)
python label_sections.py article.html --in-place

# Audit label coverage (report only, no changes)
python label_sections.py path/to/articles --audit-only

# Output JSON inventory of detected components
python label_sections.py article.html --json

# Print the Template Builder PARTS vocabulary
python label_sections.py --registry
python label_sections.py --registry --json
```

## Architecture

```
html-component-labeler/
├── label_sections.py          # Main entry point and CLI
├── components/                # One file per detector family
│   ├── registry.py            # Template Builder PARTS registry (source-of-truth mirror)
│   ├── structural.py          # HEADER, HERO, MAIN-LAYOUT, SERIES-NAV, FOOTER, aliases
│   ├── tabs.py                # TAB-BAR variants and TAB-* contents
│   ├── content.py             # CONTENT-BLOCK, MEDIA-CARDS, EQUATION, KILL-CARD, etc.
│   ├── mda_specific.py        # PROOF-LAYER, MATH-TRANSLATION, etc.
│   └── metadata.py            # META-BLOCK, OG-TAGS, ANALYTICS
├── core/
│   ├── parser.py              # DOM traversal utilities
│   ├── marker.py              # BEGIN/END marker injection
│   └── inventory.py           # JSON inventory builder and paragraph classification
├── tests/
│   ├── fixtures/              # Sample HTML files for testing
│   ├── test_cli.py
│   └── test_components.py
├── reference/                 # Classification patterns from other tools
├── requirements.txt
└── README.md
```

## Adding a new component type

1. Add a detection function in the appropriate `components/*.py` file:

```python
def find_proof_layer(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(
        html,
        "PROOF-LAYER",
        lambda tag: has_class(tag, "proof-panel") or has_class(tag, "proof-pressure"),
        "proof-panel / proof-pressure",
    )
```

2. Register it in `label_sections.py`:

```python
COMPONENT_FINDERS = [
    find_header,
    find_topbar,
    find_sidebar_nav,
    find_hero,
    # ...
    find_proof_layer,
]
```

3. If it is a Template Builder top-level slot or variant, update `components/registry.py` first and ensure the detector emits the proper variant.

4. Add a test fixture and test case.

5. Run: `python -m pytest tests/`

## Reference tools

These repos informed the classification approach:
- [trafilatura](https://github.com/adbar/trafilatura) — content extraction + metadata
- [jusText](https://github.com/miso-belica/jusText) — paragraph classification
- [readability](https://github.com/mozilla/readability) — readable content isolation
- [goose3](https://github.com/goose3/goose3) — article extraction

## Origin

Based on `02_label_gtq_sections.py` from the Theophysics HTML production pipeline (POF 2828).

Component vocabulary is derived from `Template_Builder__standalone_.html` PARTS registry — a visual configurator that lets you pick which variant of each component slot to use per article. The PARTS registry is the single source of truth: Template Builder defines → Labeler detects → Assembler fills.

### Pipeline Architecture

```
Template Builder (PARTS registry)     ← defines what components exist
        ↓
Stage 1: Template                     ← canonical HTML with all slots
        ↓
Stage 2: Labeler (this repo)          ← marks components in existing HTML
        ↓
Stage 3: Markdown Scanner             ← marks source markdown with component tags
        ↓
Stage 4: Assembler                    ← fills template slots from marked markdown
        ↓
Stage 5: Audit                        ← validates all labels present and balanced
```
