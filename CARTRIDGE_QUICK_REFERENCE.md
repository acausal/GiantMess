# Cartridge Quick Reference Card

## Import
```python
from kitbash_cartridge import (
    Cartridge, AnnotationMetadata, EpistemicLevel, 
    Derivation, Relationship
)
```

## Create & Load

```python
# Create new
cart = Cartridge("name")
cart.create()

# Load existing
cart = Cartridge("name")
cart.load()

# Save
cart.save()

# Close
cart.close()
```

## Add Facts

```python
# Simple fact
fact_id = cart.add_fact("Water boils at 100°C")

# With annotation
fact_id = cart.add_fact(
    "Water boils at 100°C",
    AnnotationMetadata(
        confidence=0.99,
        sources=["Physics_Handbook"],
        epistemic_level=EpistemicLevel.L0_EMPIRICAL,
        context_domain="physics",
        context_applies_to=["water", "temperature"],
    )
)

# Returns existing ID if duplicate
fact_id = cart.add_fact("Water boils at 100°C")  # Same as first
```

## Retrieve Facts

```python
# Single fact
content = cart.get_fact(42)

# Multiple facts
facts = cart.get_facts([1, 2, 3])  # Dict[id -> content]
```

## Query

```python
# Simple query (returns IDs)
ids = cart.query("water temperature")

# With full annotations
results = cart.query_detailed("water temperature")
for fact_id, data in results.items():
    print(data['content'])
    print(data['annotation'].confidence)

# Disable access logging
ids = cart.query("internal query", log_access=False)
```

## Phantom Detection

```python
# Get phantom candidates (ready for Week 2 crystallization)
phantoms = cart.get_phantom_candidates(
    min_access_count=5,
    min_consistency=0.75
)

for fact_id, data in phantoms:
    print(f"{fact_id}: {data['access_count']} accesses")
    print(f"  Patterns: {data['patterns']}")
```

## Hot/Cold Analysis

```python
analysis = cart.analyze_access_distribution()

print(analysis['distribution'])  # "pareto" or "uniform"
print(analysis['hot_ratio'])     # Fraction of hot facts
print(analysis['should_split'])  # Recommendation
```

## Statistics

```python
stats = cart.get_stats()

# Returns:
{
    'name': 'cartridge_name',
    'active_facts': 1247,
    'annotations': 1247,
    'keywords': 3841,
    'total_accesses': 18340,
    'access_distribution': {...},
    'phantom_candidates': 12,
    'size_mb': 2.3,
}
```

## Annotation Structure

```python
ann = AnnotationMetadata(
    fact_id=0,  # Set by add_fact
    
    # Confidence & sources
    confidence=0.92,
    sources=["Handbook_2023"],
    
    # Temporal windows
    temporal_validity_start="2023-01-01",
    temporal_validity_end="2025-12-31",
    
    # Truth level
    epistemic_level=EpistemicLevel.L1_NARRATIVE,
    
    # Dependencies
    derivations=[
        Derivation(
            type="positive_dependency",
            description="Temperature affects gelling",
            strength=0.95,
            target="gelling_rate",
        ),
        Derivation(
            type="range_constraint",
            parameter="temperature",
            min_val=55,
            max_val=65,
            unit="°C",
        ),
    ],
    
    # Cross-fact links
    relationships=[
        Relationship(
            type="affects",
            target_fact_id=456,
            description="Affects polymer crystallinity",
        ),
    ],
    
    # Context
    context_domain="bioplastics",
    context_subdomains=["thermodynamics"],
    context_applies_to=["PLA", "polymers"],
    context_excludes=["natural_polymers"],
    
    # Week 3: Neural Wire Protocol
    nwp_encoding="⊢ [MAT:PLA_GELLING] ⇒ [RANGE:60±5°C]",
)
```

## Epistemic Levels

```python
EpistemicLevel.L0_EMPIRICAL   # Physical laws (immutable)
EpistemicLevel.L1_NARRATIVE   # World facts, history
EpistemicLevel.L2_AXIOMATIC   # Rules, identity (default)
EpistemicLevel.L3_PERSONA     # Character beliefs (ephemeral)
```

Use higher levels for more important facts. Lower levels can't override higher ones.

## Access Logging

```python
# Automatic on queries (default)
results = cart.query("temperature")  # Logged

# Manual logging
cart._log_access(fact_id, ["concepts", "from", "query"])

# Disable for internal queries
results = cart.query("internal", log_access=False)

# Check access log
log = cart.access_log[fact_id]
print(f"Count: {log.access_count}")
print(f"Patterns: {log.query_patterns}")
print(f"Consistency: {log.cycle_consistency}")
```

## File Structure

```
cartridges/
└── name.kbc/
    ├── facts.db              # SQLite
    ├── annotations.jsonl     # Metadata
    ├── manifest.json         # Version info
    ├── metadata.json         # Health stats
    └── indices/
        ├── keyword.idx       # Inverted index
        ├── content_hash.idx  # Dedup
        └── access_log.idx    # Delta registry
```

## Performance Targets

```
Query latency:        <100ms (typical: 5-20ms)
Storage overhead:     2-3% (97-98% is content)
Deduplication:        SHA-256 content hash
Indexing:             O(1) keyword lookup
Phantom detection:    Automatic during queries
```

## Common Patterns

### Initialize and Add Batch
```python
cart = Cartridge("domain")
cart.create()

for content, meta in batch:
    cart.add_fact(content, meta)

cart.save()
```

### Load and Query
```python
cart = Cartridge("domain")
cart.load()

results = cart.query_detailed("user query")
for fact_id, data in results.items():
    print(f"{data['content']} (confidence: {data['annotation'].confidence})")
```

### Find Learning Targets
```python
cart.load()

# After several queries...
phantoms = cart.get_phantom_candidates()

for fact_id, data in phantoms:
    # These are ready for Week 2 crystallization
    print(f"Candidate {fact_id}: {data['consistency']:.2f} consistency")
```

### Check Split Readiness
```python
analysis = cart.analyze_access_distribution()

if analysis['should_split']:
    # Implement hot/cold split in Phase 2
    hot_ids = [...]
    cold_ids = [...]
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `FileNotFoundError` | Call `create()` before `load()` |
| No query results | Check keywords are extracted (use `_extract_keywords()`) |
| Empty phantoms | Lower `min_access_count` or `min_consistency` thresholds |
| Large file size | Normal - includes full fact + annotation + indices |

## Integration Points

| Phase | Uses | Provides |
|-------|------|----------|
| 1 | SQLite, JSON | Fact storage, keyword index |
| 2 | access_log | Phantom candidates for crystallization |
| 3 | nwp_encoding | Neural Wire Protocol facts for prompts |
| 4+ | epistemological levels | Conflict resolution, hierarchy |

## Memory Usage

```
1,000 facts:    ~10MB
10,000 facts:   ~100MB
100,000 facts:  ~1GB
```

Scales linearly. Index size minimal (<1% of facts).

## Persistence Guarantee

```
call add_fact()
  ↓
fact in memory

call save()
  ↓
fact in SQLite
fact in indices
fact in annotations.jsonl

call close()
  ↓
later session: load()
  ↓
all facts restored ✓
```

---

**Last Updated:** February 12, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
