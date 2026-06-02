# HTML-label-extractor
# html-component-labeler

Modular HTML component scanner and labeler for the Theophysics publication pipeline.

## What it does

Scans HTML article files and wraps every recognized component with canonical markers:

```html
<!-- BEGIN: HERO -->
<section class="hero-grid">...</section>
<!-- END: HERO -->

<!-- BEGIN: TAB-PAPER -->
<section id="paper">...</section>
<!-- END: TAB-PAPER -->

<!-- BEGIN: PAPER-EQUATION -->
$$dS/dt \geq 0$$
<!-- END: PAPER-EQUATION -->
```

These markers make the HTML machine-readable — scripts can find, extract, replace, or validate any component without parsing the full DOM.

## Component Types (current: 17, target: 30+)

### Structural
| Marker | What it finds | Detection method |
|--------|--------------|-----------------|
| `TOPBAR` | Site navigation bar | `class="site-header"` / `class="canon-bar"` |
| `SIDEBAR-NAV` | Series sidebar navigation | `nav.sidebar` |
| `HERO` | Hero image section | `class="hero-grid"` / `class="article-hero-wrap"` |
| `MAIN-LAYOUT` | Main content container | `main.main-layout` / `main.container` |
| `BOTTOM-NAV` | Prev/next article links | `class="bottom-nav"` / `class="article-nav"` |
| `FOOTER` | Page footer | `<footer>` / `class="site-footer"` |
| `AUDIO-DOCK` | Audio player dock | `id="audioDock"` / `class="audio-dock"` |

### Tab System
| Marker | What it finds |
|--------|--------------|
| `TAB-BAR` | Reading-level tab navigation |
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

### Needed (MDA-specific — TODO)
| Marker | What to find |
|--------|-------------|
| `PROOF-LAYER` | Proof pressure panels |
| `MATH-TRANSLATION` | Collapsible math-to-English translation blocks |
| `DATA-TABLE` | Evidence data tables |
| `CITATION-BLOCK` | Source citation blocks |
| `READER-MODE-CONTENT` | Per-reading-level content blocks |
| `INFOGRAPHIC` | Inline infographic images |
| `SERIES-RIBBON` | Series position ribbon |
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
```

## Architecture

```
html-component-labeler/
├── label_sections.py          # Main entry point
├── components/                # One file per component type
│   ├── structural.py          # TOPBAR, SIDEBAR, HERO, FOOTER, etc.
│   ├── tabs.py                # TAB-* components
│   ├── content.py             # EQUATION, KILL-CARD, etc.
│   ├── mda_specific.py        # PROOF-LAYER, MATH-TRANSLATION, etc.
│   └── metadata.py            # META-BLOCK, OG-TAGS, ANALYTICS
├── core/
│   ├── parser.py              # DOM traversal utilities
│   ├── marker.py              # BEGIN/END marker injection
│   └── inventory.py           # JSON inventory builder
├── tests/
│   ├── fixtures/              # Sample HTML files for testing
│   │   ├── gtq_full.html      # Complete GTQ article
│   │   ├── mda_full.html      # Complete MDA article
│   │   ├── minimal.html       # Minimal article (few components)
│   │   └── broken.html        # Intentionally broken HTML
│   ├── test_structural.py
│   ├── test_tabs.py
│   ├── test_content.py
│   └── test_mda_specific.py
├── reference/                 # Classification patterns from other tools
│   ├── JUSTEXT_PATTERNS.md    # Paragraph scoring approach from jusText
│   └── TRAFILATURA_PATTERNS.md # Content extraction heuristics
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
    find_topbar,
    find_sidebar_nav,
    find_hero,
    # ...
    find_proof_layer,  # ← add here
]
```

3. Add a test fixture and test case.

4. Run: `python -m pytest tests/`

## Reference tools

These repos informed the classification approach:
- [trafilatura](https://github.com/adbar/trafilatura) — content extraction + metadata
- [jusText](https://github.com/miso-belica/jusText) — paragraph classification
- [readability](https://github.com/mozilla/readability) — readable content isolation
- [goose3](https://github.com/goose3/goose3) — article extraction

## Origin

Based on `02_label_gtq_sections.py` from the Theophysics HTML production pipeline (POF 2828).
