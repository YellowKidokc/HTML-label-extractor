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

# Codex Issue Prompts for html-component-labeler
# ================================================
# Create these as GitHub Issues. Codex picks them up and creates PRs.

---

## Issue 1: Refactor monolith into modular architecture

**Title:** Refactor 02_label_gtq_sections.py into modular component architecture

**Body:**
The current `02_label_gtq_sections.py` (508 lines) is a single monolithic file. Refactor into:

```
label_sections.py          # Entry point, CLI
components/
  structural.py            # TOPBAR, SIDEBAR-NAV, HERO, MAIN-LAYOUT, BOTTOM-NAV, FOOTER, AUDIO-DOCK
  tabs.py                  # TAB-BAR, TAB-EXECUTIVE-SUMMARY, TAB-PAPER, TAB-EXPLAIN-IT-SIMPLE, TAB-RIGOR-KILL-CONDITIONS, TAB-WATCH-LISTEN
  content.py               # PAPER-EQUATION, KILL-SIDEBAR, KILL-CARD-*, ARTICLE-STATS
  metadata.py              # (new) META-BLOCK, OG-TAGS, ANALYTICS
core/
  parser.py                # DOM traversal utilities (has_class, has_id, find_matching_element_end, etc.)
  marker.py                # BEGIN/END marker injection logic
  inventory.py             # JSON inventory builder
```

Preserve ALL existing detection logic exactly. This is a pure structural refactor — same inputs, same outputs.

Add a `COMPONENT_FINDERS` registry list in `label_sections.py` so new components are just new functions added to the list.

**Labels:** refactor, good-first-issue

---

## Issue 2: Add MDA-specific component detectors

**Title:** Add detection for MDA-specific HTML components

**Body:**
The labeler currently handles GTQ components. Add detection for these MDA-specific components:

1. `PROOF-LAYER` — Proof pressure panels. Look for `class="proof-panel"`, `class="proof-pressure"`, or `data-component="proof"`.
2. `MATH-TRANSLATION` — Collapsible math-to-English blocks. Look for `class="math-translation"`, `class="collapsible-math"`, or `data-layer="math-translation"`.
3. `DATA-TABLE` — Evidence data tables. Look for `<table>` elements with `class="data-table"`, `class="evidence-table"`, or inside a `div.data-panel`.
4. `CITATION-BLOCK` — Source citation sections. Look for `class="citation"`, `class="sources"`, `class="references"`, or `id="citations"`.
5. `ONE-BREATH` — One-breath summary. Look for `class="one-breath"`, `class="article-summary"`, or first `<p>` with `class="lead"`.
6. `FACTS-CARD` — FACTS methodology card. Look for `class="facts-card"` or content containing "Falsifiable, Anchored, Cross-domain, Testable, Structurally".
7. `RIGOR-CARD` — Rigor/falsification card. Look for `class="rigor-card"` or `class="falsification-card"`.

Each detector should follow the existing pattern:
```python
def find_component(html: str) -> list[LabelRange]:
    return element_ranges_by_start_tag(html, "MARKER-NAME", predicate, "pattern-description")
```

Add test fixtures with sample MDA HTML for each component type.

**Labels:** enhancement, mda

---

## Issue 3: Add paragraph classification (jusText-style)

**Title:** Add paragraph-level classification using jusText scoring patterns

**Body:**
Currently the labeler marks structural components but doesn't classify individual paragraphs. Add a paragraph classifier that scores each `<p>` element as:

- `NARRATIVE` — regular prose content (>50 words, no special markers)
- `CLAIM` — contains strong claim language (proves, must, cannot, always, never)
- `EVIDENCE` — contains data/citation markers (data, sigma, correlation, source, table)
- `DEFINITION` — contains definition patterns (:=, "is defined as", em-dash definitions)
- `TRANSITION` — starts with transition words (however, therefore, moreover)
- `BOILERPLATE` — navigation text, copyright, repeated phrases across pages

Reference jusText's approach at `reference/JUSTEXT_PATTERNS.md`:
- Short paragraphs near links → likely navigation (BOILERPLATE)
- Long paragraphs with high link density → likely boilerplate
- Paragraphs with no links and >40 words → likely content

Output paragraph classifications in the JSON inventory, not as HTML markers (too noisy for inline marking).

**Labels:** enhancement, nlp

---

## Issue 4: Add --audit-only mode with coverage report

**Title:** Add audit mode that reports component coverage without modifying files

**Body:**
Add `--audit-only` flag that scans HTML files and reports:

1. **Per-file component inventory** — which components are present, which are missing
2. **Coverage matrix** — files × component types, showing gaps
3. **Balance check** — BEGIN/END markers matched
4. **Template conformance** — which components does each file have vs. what the canonical template expects

Output as both JSON and markdown table.

Example output:
```
Component Coverage Report
========================
File                          TOPBAR  HERO  TAB-BAR  EQUATIONS  PROOF-LAYER  AUDIO-DOCK
mda-01-introduction.html        ✅     ✅      ✅        ❌          ❌           ✅
mda-02-phase-transition.html    ✅     ✅      ✅        ✅          ✅           ❌
...

Missing components by frequency:
  PROOF-LAYER:      45/62 files missing
  MATH-TRANSLATION: 52/62 files missing
  DATA-TABLE:       38/62 files missing
```

**Labels:** enhancement, audit

---

## Issue 5: Add test suite with fixture HTML files

**Title:** Create test suite with GTQ and MDA fixture files

**Body:**
Create `tests/` directory with:

1. `fixtures/gtq_full.html` — A complete GTQ article with all component types present
2. `fixtures/mda_full.html` — A complete MDA article with all component types present
3. `fixtures/minimal.html` — Article with only TOPBAR + MAIN-LAYOUT + FOOTER
4. `fixtures/broken.html` — Intentionally malformed HTML (unclosed tags, nested errors)
5. `fixtures/no_components.html` — Plain HTML with no recognizable components

Test cases:
- Each component detector finds its target in the full fixture
- Each detector returns empty list for the minimal fixture (where component is absent)
- Broken HTML doesn't crash the scanner
- BEGIN/END markers are properly balanced in output
- `--in-place` creates backup before modifying
- JSON inventory contains all detected components with correct byte offsets

**Labels:** testing, good-first-issue

---

## Issue 6: Markdown-to-component marker pipeline

**Title:** Build reverse pipeline — mark Markdown source files with component tags

**Body:**
The labeler works HTML→marked HTML. Build the reverse: Markdown→marked Markdown.

Given a raw Markdown article, scan it and inject component markers:

```markdown
<!--@ COMPONENT: HERO | image: images/mda-01-hero.jpg -->
<!--@ COMPONENT: TITLE | The FACTS Framework -->
<!--@ COMPONENT: ONE-BREATH | Before diagnosing America's decline... -->

## Introduction
<!--@ COMPONENT: SECTION | intro -->

Regular prose here...

<!--@ COMPONENT: MATH-BLOCK | law5-entropy -->
$$dS/dt \geq 0$$
<!--@ COMPONENT: MATH-TRANSLATION | The disorder in the system always increases. -->
```

Detection rules for Markdown:
- `# Heading` at top → TITLE
- First paragraph after title → ONE-BREATH candidate
- `$$...$$` blocks → MATH-BLOCK
- `![image](path)` → IMAGE (HERO if first image)
- `> blockquote` → QUOTE or CALLOUT
- Tables → DATA-TABLE
- Links to other articles in the series → CROSS-REFERENCE

This is the Stage 2 scanner from the full pipeline design.

**Labels:** enhancement, pipeline, milestone:v2

## Origin

Based on `02_label_gtq_sections.py` from the Theophysics HTML production pipeline (POF 2828).
