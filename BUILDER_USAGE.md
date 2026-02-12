# Cartridge + CartridgeBuilder Integration

Two files, one workflow:
- **`kitbash_cartridge.py`** - Storage & retrieval
- **`kitbash_builder.py`** - Population from data sources

## Common Workflows

### 1. Create from Markdown
```python
from kitbash_builder import CartridgeBuilder

builder = CartridgeBuilder("biology")
builder.build()
builder.from_markdown("facts.md")
builder.set_metadata(
    description="Biology knowledge",
    domains=["genetics", "ecology"],
)
builder.save()
```

Markdown format:
```markdown
# Genetics
## DNA
- DNA contains genetic information | TextBook | 0.99
- Genes are units of heredity | Research | 0.95

## Proteins
- Proteins fold into 3D structures | Handbook | 0.9
```

### 2. Create from CSV
```python
builder = CartridgeBuilder("materials")
builder.build()
builder.from_csv("properties.csv", domain_col="material", content_col="property")
builder.save()
```

CSV format (headers required):
```
material,property,confidence,source
PLA,Requires 60°C for gelling,0.92,Handbook_2023
Steel,High tensile strength,0.99,Physics
Aluminum,Lightweight,0.95,Engineering
```

### 3. Create from JSON
```python
builder = CartridgeBuilder("config")
builder.build()
builder.from_json("facts.json")
builder.save()
```

JSON format:
```json
[
  {
    "content": "API endpoint is localhost:8000",
    "metadata": {
      "domain": "configuration",
      "confidence": 0.9,
      "sources": ["deployment_guide"]
    }
  }
]
```

### 4. Manual Addition
```python
builder = CartridgeBuilder("quick")
builder.build()

# Add one fact
builder.add_fact("Water boils at 100°C", domain="physics", confidence=0.99)

# Add batch
builder.add_batch([
    ("Temperature affects viscosity", "thermodynamics", 0.9),
    ("Pressure affects boiling point", "thermodynamics", 0.85),
], domain="physics")

builder.save()
```

### 5. Mix Sources
```python
builder = CartridgeBuilder("comprehensive")
builder.build()

# Load from multiple formats
builder.from_markdown("core_facts.md")
builder.from_csv("measurements.csv")
builder.from_json("derivations.json")

# Add manual overrides
builder.add_fact("Custom correction factor applies", domain="calibration", confidence=0.8)

builder.set_metadata(
    description="Comprehensive knowledge base",
    domains=["physics", "chemistry", "materials"],
    tags=["experimental", "validated"],
)
builder.save()
```

### 6. Load and Query
```python
from kitbash_cartridge import Cartridge

# Load existing cartridge
cart = Cartridge("biology")
cart.load()

# Query
results = cart.query("DNA genetics inheritance")
for fact_id, data in cart.query_detailed("DNA genetics").items():
    print(f"{data['content']}")
    print(f"  Confidence: {data['annotation'].confidence}")
    print(f"  Domain: {data['annotation'].context_domain}")

# Check phantoms
phantoms = cart.get_phantom_candidates()
for fact_id, phantom_data in phantoms:
    print(f"Phantom {fact_id}: {phantom_data['consistency']:.2f} consistency")
```

## Supported Formats

### Markdown
- Hierarchical structure (# domain, ## subdomain)
- Bullet points for facts
- Optional metadata: `fact | source | confidence`

### CSV
- Header row defines columns
- Required: `content` column
- Optional: `domain`, `confidence`, `source`
- Other columns → context tags

### JSON
- Array of objects or single object
- Required: `content` key
- Optional: `metadata` dict with `confidence`, `domain`, `sources`

### Plain Text
- One fact per line (default)
- Or sentence-split mode
- Uniform confidence/domain for all

### Directory
- Loads multiple files at once
- Auto-detects format by extension (.md, .csv, .json, .txt)
- Optional: use subdirectory names as domain

## Key Methods

**Builder Setup**
```python
builder = CartridgeBuilder("name")
builder.build()          # Create cartridge
builder.load_cartridge() # Load existing
```

**Load Data**
```python
builder.from_markdown(path)
builder.from_csv(path)
builder.from_json(path)
builder.from_text(path)
builder.from_directory(dirpath)
```

**Add Facts**
```python
builder.add_fact(content, domain, confidence)
builder.add_batch([(content, tag, confidence), ...])
```

**Finalize**
```python
builder.set_metadata(description, domains, tags, author)
builder.save()
```

**Query**
```python
cart = builder.cart  # Get underlying Cartridge
cart.query("keywords")
cart.query_detailed("keywords")
cart.get_phantom_candidates()
```

## File Structure After Build

```
cartridges/
└── cartridge_name.kbc/
    ├── facts.db           # All facts (SQLite)
    ├── annotations.jsonl  # Metadata for each fact
    ├── manifest.json      # Version, domains, tags
    ├── metadata.json      # Health, statistics
    └── indices/
        ├── keyword.idx
        ├── content_hash.idx
        └── access_log.idx
```

## Performance Notes

**Load time** (from builder):
- Small files (<100 facts): ~100ms
- Medium files (100-1000): ~500ms
- Large files (1000+): ~2s

**Query time** (after load):
- Keyword query: <10ms (O(1) index lookup)
- Phantom detection: depends on access patterns

**Storage**:
- Markdown 1MB → cartridge 300KB (3:1 compression)
- CSV parsing: line-by-line, memory efficient
- JSON: loads full file, requires pre-validation

## Edge Cases

**Duplicate facts:**
- Same content hash → same fact_id (automatic dedup)
- Different annotations → create separate facts with different content

**Missing metadata:**
- Uses defaults: domain="general", confidence=0.8, source="<format>"

**Special characters:**
- Markdown: handled as-is
- CSV: respects quotes and escaping
- JSON: standard JSON parsing
- Text: no special handling

**Large files:**
- CSV: line-by-line, constant memory
- JSON: loads all at once (watch memory for huge files)
- Markdown: line-by-line, constant memory
- Text: loads all, no batching

## Troubleshooting

**"File not found"**
- Check file path is absolute or relative to working directory

**"CSV missing header"**
- Ensure first line has column names

**"JSON parse error"**
- Validate JSON is valid (use `python -m json.tool file.json`)

**"No facts loaded"**
- Check fact extraction patterns match your format
- Use explicit `content_col`, `domain_col` parameters

**"Facts not persisting"**
- Call `builder.save()` at end
- Without save, facts are in memory only

## Integration with Cartridge

Builder is a convenience wrapper. For advanced usage:

```python
# Builder creates a Cartridge instance
builder = CartridgeBuilder("name")
builder.build()

# Access it directly
cart = builder.cart
cart.add_fact("custom fact")  # Add directly
cart.query("search")          # Query directly

# Or get a fresh Cartridge for an existing cartridge
cart2 = Cartridge("name")
cart2.load()
```

## Next Steps (Week 2)

After populating cartridges:

1. **Analyze distribution** - Call `cart.analyze_access_distribution()`
2. **Implement hot/cold split** - Use distribution analysis
3. **Start phantom tracking** - Call `cart.get_phantom_candidates()`
4. **Feed crystallization** - Pass phantoms to Week 2 system

---

**Ready to populate your Kitbash system with data!**
