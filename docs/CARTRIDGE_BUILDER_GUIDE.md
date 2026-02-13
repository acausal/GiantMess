# Cartridge Builder - Usage Guide

## Quick Start

### 1. Basic Usage (Markdown)

```bash
python cartridge_builder.py \
    --name bioplastics \
    --input example_bioplastics.md \
    --format markdown
```

This will:
- Extract all bullet points and numbered lists from the markdown
- Create default annotations (confidence: 0.75)
- Build keyword indices automatically
- Save to `./cartridges/bioplastics.kbc/`

### 2. Interactive Mode

```bash
python cartridge_builder.py \
    --name bioplastics \
    --input example_bioplastics.md \
    --interactive
```

Interactive mode lets you:
- Select which facts to include (Enter/skip/quit)
- Manually set confidence scores
- Add source citations
- Tag contexts (applies_to)

### 3. CSV Import (Best for Structured Data)

```bash
python cartridge_builder.py \
    --name bioplastics \
    --input example_bioplastics.csv \
    --format csv
```

CSV columns:
- `fact` (required): The fact text
- `confidence` (optional): 0.0-1.0
- `source` (optional): Citation
- `domain` (optional): Domain tag
- `applies_to` (optional): Comma-separated contexts

### 4. JSON Import (Most Flexible)

```bash
python cartridge_builder.py \
    --name bioplastics \
    --input example_bioplastics.json \
    --format json
```

JSON format:
```json
[
    {
        "fact": "PLA requires 60°C for gelling",
        "confidence": 0.92,
        "sources": ["Handbook_2023", "Research_2024"],
        "domain": "bioplastics",
        "applies_to": ["PLA", "synthetic_polymers"],
        "derivations": [
            {
                "type": "positive_dependency",
                "target": "temperature",
                "strength": 0.95
            }
        ]
    }
]
```

---

## Common Workflows

### Workflow 1: Convert Research Notes to Cartridge

**You have:** Markdown notes with bullet-point facts

**Steps:**
1. Organize notes into sections (headings)
2. Use bullet points or numbered lists for facts
3. Run builder in interactive mode to review
4. Preview before saving

```bash
python cartridge_builder.py \
    --name my_research \
    --input my_notes.md \
    --interactive \
    --preview
```

### Workflow 2: Import Structured Database

**You have:** CSV export from database or spreadsheet

**Steps:**
1. Export with columns: fact, confidence, source, domain, applies_to
2. Import via CSV format
3. Preview to validate
4. Save directly

```bash
python cartridge_builder.py \
    --name chemistry_db \
    --input chemistry_export.csv \
    --preview
```

### Workflow 3: Build Cartridge from Scratch

**You have:** Nothing yet, building manually

**Steps:**
1. Start with empty cartridge
2. Use Python API to add facts programmatically

```python
from cartridge_builder import CartridgeBuilder

builder = CartridgeBuilder("my_cartridge")

# Add facts manually
builder.add_fact_with_annotation(
    "Water boils at 100°C at sea level",
    annotation_template="default"
)

builder.add_fact_with_annotation(
    "Pressure affects boiling point",
    annotation_override={
        "metadata": {
            "confidence": 0.95,
            "sources": ["Physics_Textbook"]
        },
        "derivations": [
            {"type": "positive_dependency", "target": "pressure"}
        ],
        "relationships": [],
        "context": {
            "domain": "thermodynamics",
            "applies_to": ["water", "phase_transitions"]
        }
    }
)

builder.preview()
builder.save()
```

---

## Output Structure

After running, you'll get:

```
./cartridges/
└── bioplastics.kbc/
    ├── facts.db               # SQLite with all facts
    ├── annotations.jsonl      # One line per fact
    ├── indices/
    │   ├── keyword.idx        # For fast lookup
    │   ├── content_hash.idx   # Deduplication
    │   └── access_log.idx     # Empty (for runtime)
    ├── metadata.json          # Health metrics
    └── manifest.json          # Version, dependencies
```

---

## Validation & Preview

Always use `--preview` to check before saving:

```bash
python cartridge_builder.py \
    --name test_cart \
    --input data.md \
    --preview
```

Preview shows:
- Total fact count
- Sample facts (first 5)
- Top keywords
- Validation issues (if any)

**Common validation issues:**
- Facts with confidence < 0.5
- Missing sources
- Fact/annotation count mismatch

---

## Advanced Usage

### Adding Derivations (Python API)

```python
builder = CartridgeBuilder("physics")

builder.add_fact_with_annotation(
    "Force equals mass times acceleration",
    annotation_override={
        "metadata": {
            "confidence": 1.0,
            "sources": ["Newton_Principia"]
        },
        "derivations": [
            {
                "type": "equation",
                "formula": "F = ma",
                "variables": ["force", "mass", "acceleration"]
            },
            {
                "type": "positive_dependency",
                "target": "mass",
                "strength": 1.0
            },
            {
                "type": "positive_dependency",
                "target": "acceleration",
                "strength": 1.0
            }
        ],
        "relationships": [],
        "context": {
            "domain": "classical_mechanics",
            "applies_to": ["Newtonian_physics"]
        }
    }
)
```

### Linking Facts (Relationships)

```python
# First fact
fact1_id = builder.add_fact_with_annotation(
    "PLA requires 60°C for gelling",
    annotation_template="default"
)

# Second fact that references first
builder.add_fact_with_annotation(
    "Temperature variance affects gel consistency",
    annotation_override={
        "metadata": {"confidence": 0.85, "sources": ["Research_2024"]},
        "derivations": [],
        "relationships": [
            {
                "type": "affects",
                "target_fact_id": fact1_id,
                "description": "Influences gelling temperature requirement"
            }
        ],
        "context": {"domain": "bioplastics"}
    }
)
```

---

## Tips for Week 1

### Start Small
Build 1-2 cartridges with 10-20 facts each to validate the pipeline.

### Use CSV for Bulk Import
If you have lots of facts, CSV is easier to prepare than JSON.

### Iterate on Confidence
Start with default confidence (0.75), refine later based on source quality.

### Tag Generously
The `applies_to` field feeds keyword indexing - more tags = better routing.

### Validate Before Saving
Always use `--preview` to catch issues early.

---

## Example Session

```bash
$ python cartridge_builder.py --name bioplastics --input example_bioplastics.md --interactive

=== Loading from markdown: example_bioplastics.md ===

Found 21 potential facts

--- Fact Selection ---
Review each fact. Press Enter to include, 's' to skip, 'q' to quit:

[1/21] PLA requires 60°C ±5°C for optimal gelling [Enter/s/q]: 
  ✓ Added
[2/21] Glass transition temperature of PLA is approximately 60°C [Enter/s/q]: 
  ✓ Added
[3/21] PLA is a biodegradable thermoplastic polyester [Enter/s/q]: 
  ✓ Added
...

Selected 15/21 facts

✓ Added fact #1: PLA requires 60°C ±5°C for optimal gelling...
✓ Added fact #2: Glass transition temperature of PLA is approximately ...
...

============================================================
CARTRIDGE PREVIEW: bioplastics
============================================================

Facts: 15
Annotations: 15
Keyword index size: 47 keywords
Content hash index: 15 unique hashes

--- Sample Facts (first 5) ---
1. [0.75] PLA requires 60°C ±5°C for optimal gelling...
2. [0.75] Glass transition temperature of PLA is approximately...
3. [0.75] PLA is a biodegradable thermoplastic polyester...
4. [0.75] Crystallinity affects mechanical properties of PLA...
5. [0.75] Molecular weight influences melt viscosity...

--- Top Keywords ---
  pla: 8 facts
  temperature: 5 facts
  crystallinity: 4 facts
  affects: 4 facts
  polymer: 3 facts
  ...

--- Validation ---
✓ All checks passed

============================================================

Save cartridge? [Y/n]: y

=== Saving cartridge to ./cartridges/bioplastics.kbc ===

✓ Saved facts.db (15 facts)
✓ Saved annotations.jsonl (15 annotations)
✓ Saved keyword.idx (47 keywords)
✓ Saved content_hash.idx (15 hashes)
✓ Saved access_log.idx (empty)
✓ Saved metadata.json
✓ Saved manifest.json

✓ Cartridge saved successfully!
  Location: ./cartridges/bioplastics.kbc
  Facts: 15
  Size: 23 KB
```

---

## Next Steps

Once you have cartridges built:

1. **Test loading:** Use the cartridge loader (Week 1 implementation)
2. **Query facts:** Test keyword-based retrieval
3. **Iterate:** Add more facts, refine annotations
4. **Build more:** Create cartridges for different domains

The builder gets you from raw knowledge to properly-formatted cartridges without manual file manipulation.
