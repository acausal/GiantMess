# Cartridge System Specification
## Complete Reference for Knowledge Storage & Retrieval in Kitbash

**Version:** 1.0  
**Date:** February 11, 2026  
**Purpose:** Single authoritative specification for implementing the Cartridge system  
**Status:** Week 1 Implementation Ready

---

## Table of Contents

1. [Overview & Principles](#overview--principles)
2. [File Structure](#file-structure)
3. [Data Formats](#data-formats)
4. [Lifecycle & States](#lifecycle--states)
5. [Integration Points](#integration-points)
6. [Implementation Guide](#implementation-guide)
7. [Performance Targets](#performance-targets)
8. [Appendices](#appendices)

---

## Overview & Principles

### What is a Cartridge?

A **Cartridge** is a self-contained, versioned knowledge module containing:
- **Facts**: Content-addressed atomic statements
- **Annotations**: Metadata, derivations, relationships, confidence
- **Indices**: Fast lookup structures (keyword, semantic, hash)
- **Grains**: Crystallized Shannon Grains (learned patterns)
- **Metadata**: Health metrics, dependencies, version info

**Design Principles:**
1. **Content-addressed storage** (git-like, deduplicatable)
2. **2-3% overhead ratio** (structure vs. content)
3. **Pareto-optimized** (20% hot facts, 80% cold)
4. **Auditable** (every fact traceable to source)
5. **Metabolically active** (learns and optimizes itself)

### Core Constraint: The 2-3% Rule

```
Cartridge Composition:
├─ 2-3% : Indices + Metadata (coordination overhead)
└─ 97-98%: Facts + Annotations (substantive content)

This ratio mirrors:
- Shannon Grains: 3% pointer map, 97% representable content
- DNA: 2% coding, 98% regulatory
- Textbooks: 2-3% TOC/index, 97% content
```

This is the **minimal overhead for structural coordination** at knowledge-module scale.

---

## File Structure

### Directory Layout

```
cartridges/
└─ <cartridge_name>.kbc/
    ├─ facts.db               # SQLite database of facts
    ├─ annotations.jsonl      # One annotation per line
    ├─ indices/
    │   ├─ keyword.idx        # Inverted index {word: [fact_ids]}
    │   ├─ content_hash.idx   # Deduplication {hash: fact_id}
    │   └─ access_log.idx     # Delta Registry {fact_id: stats}
    ├─ grains/
    │   ├─ sg_0x7F3A.json     # Shannon Grain (crystallized)
    │   ├─ sg_0x8E4B.json
    │   └─ registry.json      # Grain inventory
    ├─ metadata.json          # Health metrics, stats
    └─ manifest.json          # Dependencies, version, inventory
```

### File Extensions

- `.kbc` = Kitbash Cartridge (directory container)
- `.db` = SQLite database
- `.jsonl` = JSON Lines (one object per line)
- `.idx` = Index file (JSON)
- `.json` = Standard JSON

---

## Data Formats

### 1. Facts Database (facts.db)

**SQLite Schema:**

```sql
CREATE TABLE facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT UNIQUE NOT NULL,  -- SHA-256 of content
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    status TEXT DEFAULT 'active'  -- active, archived, deprecated
);

CREATE INDEX idx_content_hash ON facts(content_hash);
CREATE INDEX idx_access_count ON facts(access_count DESC);
CREATE INDEX idx_status ON facts(status);
CREATE INDEX idx_last_accessed ON facts(last_accessed DESC);
```

**Example Row:**
```sql
INSERT INTO facts (content_hash, content) VALUES (
    'sha256:7f3a2b1c...',
    'PLA requires 60°C ±5°C for optimal gelling'
);
```

**Design Notes:**
- `content_hash` enables deduplication across cartridges
- `access_count` feeds into hot/cold splitting logic
- `status` allows soft deletion without breaking references
- All facts are immutable; updates create new facts

---

### 2. Annotations (annotations.jsonl)

**Format:** JSON Lines (one annotation object per line)

**Schema:**
```json
{
  "fact_id": 123,
  "metadata": {
    "confidence": 0.92,
    "sources": ["Handbook_2023", "Research_2024"],
    "temporal_validity": {
      "start": "2023-01-01",
      "end": "2025-12-31"
    },
    "created_at": "2026-01-15T10:00:00Z",
    "last_validated": "2026-02-10T08:00:00Z"
  },
  "derivations": [
    {
      "type": "positive_dependency",
      "target": "temperature",
      "strength": 0.95,
      "description": "Gelling directly depends on temperature"
    },
    {
      "type": "boundary",
      "applies_to": ["synthetic_polymers"],
      "not_applies_to": ["natural_gelatin", "agar"]
    },
    {
      "type": "range_constraint",
      "parameter": "temperature",
      "min": 55,
      "max": 65,
      "unit": "°C"
    }
  ],
  "relationships": [
    {
      "type": "affects",
      "target_fact_id": 456,
      "description": "Affects polymer crystallinity"
    },
    {
      "type": "required_by",
      "target_fact_id": 789,
      "description": "Required for gel formation mechanism"
    }
  ],
  "context": {
    "domain": "bioplastics",
    "subdomains": ["thermodynamics", "polymer_chemistry"],
    "applies_to": ["PLA", "synthetic_polymers"],
    "excludes": ["natural_polymers", "proteins"]
  },
  "nwp_encoding": "⊢ [MAT:PLA_GELLING] ⇒ [RANGE:60±5°C]"
}
```

**Design Notes:**
- One line per fact (enables streaming reads)
- `derivations` capture logical dependencies (feeds Shannon Grains)
- `relationships` create graph structure across facts
- `nwp_encoding` is the Neural Wire Protocol representation (Week 3+)
- All timestamps in ISO 8601 format

---

### 3. Indices

#### 3.1 Keyword Index (indices/keyword.idx)

**Format:** JSON inverted index

```json
{
  "temperature": [123, 456, 789],
  "PLA": [123, 234, 345],
  "gelling": [123, 567, 890],
  "polymer": [123, 234, 345, 456],
  "synthetic": [123, 234, 345]
}
```

**Build Process:**
```python
# Extract keywords from fact content + annotations
keywords = extract_keywords(fact.content) + annotation.context.applies_to
for keyword in keywords:
    index[keyword.lower()].append(fact.id)
```

**Query Process:**
```python
# Query: "temperature PLA gelling"
query_words = ["temperature", "pla", "gelling"]
candidate_ids = set()
for word in query_words:
    candidate_ids.update(index.get(word, []))
# Returns: {123, 234, 345, 456, 567, 789, 890}
```

---

#### 3.2 Content Hash Index (indices/content_hash.idx)

**Format:** JSON mapping

```json
{
  "sha256:7f3a2b1c...": 123,
  "sha256:8e4b3c2d...": 124,
  "sha256:9f5d4e3f...": 125
}
```

**Purpose:** 
- Deduplication (check if fact already exists)
- Git-like content addressing
- Cross-cartridge fact sharing

**Usage:**
```python
# Before inserting new fact
content_hash = sha256(fact_content)
if content_hash in hash_index:
    return hash_index[content_hash]  # Fact already exists
else:
    # Insert new fact
    fact_id = insert_fact(fact_content, content_hash)
    hash_index[content_hash] = fact_id
```

---

#### 3.3 Access Log (indices/access_log.idx)

**Format:** JSON with access statistics (Delta Registry)

```json
{
  "123": {
    "access_count": 47,
    "last_accessed": "2026-02-10T14:23:00Z",
    "query_patterns": [
      {"concepts": ["temperature", "gelling", "PLA"], "count": 23},
      {"concepts": ["temperature", "polymer"], "count": 15},
      {"concepts": ["PLA", "synthetic"], "count": 9}
    ],
    "cycle_consistency": 0.87,
    "phantom_candidates": ["temperature_gelling_pla"]
  },
  "124": {
    "access_count": 3,
    "last_accessed": "2026-02-09T10:15:00Z",
    "query_patterns": [],
    "cycle_consistency": 0.12,
    "phantom_candidates": []
  }
}
```

**Purpose:**
- Track fact access patterns (feeds hot/cold splitting)
- Detect phantoms (repeated query patterns → grain candidates)
- Measure cycle consistency (>0.8 = stable pattern)

**Update Process:**
```python
def log_access(fact_id, query_concepts):
    log = access_log[fact_id]
    log['access_count'] += 1
    log['last_accessed'] = now()
    
    # Track query pattern
    pattern_key = tuple(sorted(query_concepts))
    log['query_patterns'][pattern_key] += 1
    
    # Compute cycle consistency
    log['cycle_consistency'] = compute_consistency(log['query_patterns'])
    
    # Detect phantom candidates
    if log['cycle_consistency'] > 0.8 and log['access_count'] > 50:
        log['phantom_candidates'].append(create_phantom_signature(pattern_key))
```

---

### 4. Shannon Grains (grains/)

#### 4.1 Grain File (grains/sg_0x7F3A.json)

**Format:** JSON

```json
{
  "grain_id": "sg_0x7F3A",
  "axiom_link": "Thermodynamic_Dependency",
  "weight": 1.58,
  "delta": {
    "pos": ["temperature", "composition_variance"],
    "neg": ["ambient_temp", "color"],
    "void": ["mechanical_properties", "density"]
  },
  "lock_state": "Sicherman_Validated",
  "cycle_count": 237,
  "phantom_origin": "temperature_gelling_pla",
  "cartridge_source": "bioplastics_hot.kbc",
  "created_at": "2026-02-08T12:00:00Z",
  "pointer_map": {
    "fact:123": 1.0,
    "fact:456": 0.8,
    "fact:234": 0.6,
    "fact:789": -0.9
  },
  "validation_hash": "sha256:abc123...",
  "size_bytes": 2048,
  "status": "active"
}
```

**Field Definitions:**
- `grain_id`: Unique hex identifier
- `axiom_link`: Which base axiom this grain validates
- `weight`: 1.58-bit equilibrium weight (ternary compressed)
- `delta`: Ternary classification {pos, neg, void}
- `lock_state`: Validation status (Pending, Validated, Locked)
- `cycle_count`: Number of consistent access cycles
- `phantom_origin`: Original phantom pattern that spawned this grain
- `pointer_map`: Links to specific facts with strength [-1.0, 1.0]
- `validation_hash`: Integrity check

**Design Notes:**
- Grains are immutable once created (status changes to 'locked')
- `pointer_map` enables fast lookup: grain → facts
- `delta` provides semantic clustering (what matters, what doesn't)

---

#### 4.2 Grain Registry (grains/registry.json)

**Format:** JSON

```json
{
  "cartridge_name": "bioplastics",
  "grain_count": 3,
  "total_size_bytes": 6144,
  "last_updated": "2026-02-10T14:23:00Z",
  "grains": {
    "sg_0x7F3A": {
      "description": "Thermodynamic gelling dependency",
      "axiom": "Thermodynamic_Dependency",
      "active": true,
      "created": "2026-02-08T12:00:00Z",
      "fact_count": 4
    },
    "sg_0x8E4B": {
      "description": "Polymer composition classification",
      "axiom": "Material_Classification",
      "active": true,
      "created": "2026-02-09T09:30:00Z",
      "fact_count": 7
    },
    "sg_0x9F2C": {
      "description": "Crystallinity effect mapping",
      "axiom": "Structural_Effects",
      "active": false,
      "created": "2026-02-07T16:00:00Z",
      "fact_count": 3
    }
  }
}
```

**Purpose:**
- Quick lookup: which grains exist in this cartridge
- Status tracking: active grains loaded, inactive archived
- Size accounting: grain storage budget tracking

---

### 5. Metadata (metadata.json)

**Format:** JSON

```json
{
  "cartridge_name": "bioplastics",
  "created_at": "2026-01-15T10:00:00Z",
  "last_updated": "2026-02-10T14:23:00Z",
  "last_accessed": "2026-02-10T14:30:00Z",
  "version": "1.2.3",
  "status": "active",
  "split_status": "intact",
  "health": {
    "fact_count": 1247,
    "active_facts": 1198,
    "archived_facts": 49,
    "annotation_count": 1247,
    "grain_count": 3,
    "index_size_kb": 142,
    "total_size_mb": 2.3,
    "access_distribution": "pareto",
    "hot_fact_ratio": 0.23,
    "avg_confidence": 0.87,
    "last_validation": "2026-02-09T08:00:00Z",
    "validation_pass_rate": 0.94
  },
  "performance": {
    "avg_query_latency_ms": 28,
    "p95_query_latency_ms": 45,
    "p99_query_latency_ms": 67,
    "cache_hit_rate": 0.76,
    "last_24h_queries": 1834
  },
  "flags": {
    "needs_split": false,
    "needs_consolidation": false,
    "needs_reindex": false,
    "needs_grain_crystallization": true
  }
}
```

**Design Notes:**
- `split_status`: intact, hot, cold, consolidated
- `health.access_distribution`: Used to trigger hot/cold split
- `flags`: Automation triggers for maintenance tasks

---

### 6. Manifest (manifest.json)

**Format:** JSON

```json
{
  "cartridge_name": "bioplastics",
  "version": "1.2.3",
  "api_version": "1.0",
  "created": "2026-01-15T10:00:00Z",
  "last_updated": "2026-02-10T14:23:00Z",
  "author": "Kitbash System",
  "description": "Knowledge about bioplastics, PLA polymers, and biodegradable materials",
  "domains": ["bioplastics", "polymers", "materials_science"],
  "tags": ["PLA", "biodegradable", "thermoplastic", "polyester"],
  "dependencies": [
    {
      "cartridge": "thermodynamics",
      "version": ">=1.0.0",
      "reason": "Temperature-dependent properties"
    },
    {
      "cartridge": "chemistry",
      "version": ">=2.1.0",
      "reason": "Polymer chemistry fundamentals"
    }
  ],
  "provides": [
    "PLA_properties",
    "bioplastic_processing",
    "polymer_gelling"
  ],
  "grain_inventory": {
    "sg_0x7F3A": "Thermodynamic gelling dependency",
    "sg_0x8E4B": "Polymer composition classification",
    "sg_0x9F2C": "Crystallinity effect mapping"
  },
  "axiom_coverage": [
    "Thermodynamic_Dependency",
    "Material_Classification",
    "Structural_Effects"
  ],
  "license": "CC-BY-4.0",
  "compression": {
    "format": "ternary_grains",
    "ratio": 0.23,
    "original_size_mb": 10.0,
    "compressed_size_mb": 2.3
  }
}
```

**Purpose:**
- Dependency resolution (like package.json)
- Version compatibility checking
- Auto-discovery of cartridge capabilities
- Grain inventory for fast loading decisions

---

## Lifecycle & States

### Cartridge States

```
┌─────────────┐
│   INTACT    │  Single unified cartridge
│  (default)  │  All facts together
└──────┬──────┘
       │ Access pattern analysis
       │ (if hot_ratio < 0.30)
       ↓
┌─────────────┐
│    SPLIT    │  Hot/Cold separation
│ (optimized) │  Hot: 20% facts, 80% access
└──────┬──────┘  Cold: 80% facts, 20% access
       │ Periodic re-analysis
       │ (if hot_ratio > 0.50)
       ↓
┌─────────────┐
│ CONSOLIDATED│  Merge hot/cold back
│ (normalized)│  Access pattern stabilized
└──────┬──────┘
       │ Long-term stability
       │ (if access_count very low)
       ↓
┌─────────────┐
│  ARCHIVED   │  Moved to cold storage
│   (stale)   │  Available on-demand
└─────────────┘
```

### Fact States

```
ACTIVE    → Normal queryable fact
ARCHIVED  → Low-access, moved to cold storage
DEPRECATED→ Replaced by newer fact, kept for history
TOMBSTONE → Deleted, placeholder for content_hash
```

### Grain States

```
PHANTOM       → Detected pattern, <50 cycles
INDUCTION     → 20-49 cycles, axiom validation active
CRYSTALLIZING → 50+ cycles, LoRA delta extraction
FOSSILIZED    → Ternary crush complete, saved to disk
LOCKED        → Permanent, immutable, active in L3 cache
ARCHIVED      → Low-access, moved to cold storage
```

---

## Integration Points

### 1. Tier 1.5 Integration (Bloom Filter Echo)

**Cartridge provides to Bloom:**
```python
# Extract concepts for Bloom encoding
concepts = []
for fact in cartridge.get_all_facts():
    annotation = cartridge.get_annotation(fact.id)
    concepts.extend(annotation['context']['applies_to'])
    concepts.extend(extract_keywords(fact.content))

# Bloom encoder creates 256-bit signature
bloom_signature = bloom_encoder.encode_concepts(concepts)
```

**Bloom provides to Cartridge:**
```python
# Query routing uses Bloom to select cartridges
query_bloom = bloom_encoder.encode_query(query_text)
matched_cartridges = compare_blooms(query_bloom, all_cartridge_blooms)

# Load facts from top 3 cartridges
for cartridge_name in matched_cartridges[:3]:
    cartridge = load_cartridge(cartridge_name)
    facts = cartridge.query_facts(query_text)
```

---

### 2. Tier 3 Integration (HDC Routing)

**Cartridge provides to HDC:**
```python
# Register cartridge with HDC router
keywords = cartridge.manifest['tags']
hdc_router.register_cartridge(
    name=cartridge.name,
    keywords=keywords
)
```

**HDC provides to Cartridge:**
```python
# HDC returns top candidates
hdc_candidates = hdc_router.route_query(query_text)

# Cartridge system loads winners
for cart_name, score in hdc_candidates[:3]:
    load_cartridge(cart_name)
```

---

### 3. Shannon Grain Integration

**Cartridge spawns Grains:**
```python
# During metabolism, check for phantoms ready to crystallize
for phantom in cartridge.access_log.get_phantoms():
    if phantom.cycle_count >= 50 and phantom.consistency > 0.8:
        grain = crystallize_grain(
            phantom=phantom,
            facts=cartridge.get_facts(phantom.fact_ids),
            annotations=cartridge.get_annotations(phantom.fact_ids)
        )
        cartridge.save_grain(grain)
```

**Grains accelerate Cartridge:**
```python
# When cartridge loaded, activate associated grains
cartridge = load_cartridge("bioplastics")
grains = [load_grain(gid) for gid in cartridge.grain_inventory.keys()]

# Query uses grains for fast ternary lookup
query_vector = encode_query(query_text)
grain_matches = [g for g in grains if g.ternary_match(query_vector)]

# Grains point to specific facts
relevant_fact_ids = []
for grain in grain_matches:
    relevant_fact_ids.extend(grain.pointer_map.keys())

facts = cartridge.get_facts(relevant_fact_ids)
```

---

### 4. Neural Wire Protocol Integration

**Cartridge stores NWP:**
```python
# Annotations include NWP encoding
annotation = {
    "fact_id": 123,
    "nwp_encoding": "⊢ [MAT:PLA_GELLING] ⇒ [RANGE:60±5°C]",
    # ... other fields
}
```

**NWP accelerates retrieval:**
```python
# When building context for LLM
facts_natural = cartridge.get_facts(fact_ids)  # 200 tokens
facts_nwp = [a['nwp_encoding'] for a in cartridge.get_annotations(fact_ids)]  # 20 tokens

# Use NWP for token efficiency
context = f"""
AXIOMS: {axioms}
FACTS (NWP):
{chr(10).join(facts_nwp)}
QUERY: {query}
"""
# 90% token reduction vs. natural language facts
```

---

## Implementation Guide

### Week 1: Core Infrastructure

#### Day 1-2: Database & File I/O

**Tasks:**
1. Create SQLite schema for `facts.db`
2. Implement fact insertion with content hashing
3. Create annotation JSONL writer/reader
4. Build keyword index generator
5. Implement content_hash index

**Deliverable:**
```python
# Can create cartridge, insert facts, save to disk
cart = Cartridge("bioplastics")
fact_id = cart.add_fact("PLA requires 60°C for gelling")
cart.add_annotation(fact_id, {
    "confidence": 0.92,
    "sources": ["Handbook_2023"]
})
cart.save()  # Writes all files to disk
```

---

#### Day 3-4: Loading & Querying

**Tasks:**
1. Implement cartridge loader
2. Build keyword-based fact query
3. Create access log tracking
4. Implement hot/cold slot management

**Deliverable:**
```python
# Can load cartridge and query facts
cart = load_cartridge("bioplastics")
results = cart.query("temperature PLA gelling")
# Returns: [fact_123, fact_456, fact_789] with annotations
# Logs access to access_log.idx
```

---

#### Day 5-7: Phantom Tracking

**Tasks:**
1. Implement Delta Registry (access_log.idx)
2. Build phantom detection logic
3. Track cycle consistency
4. Detect harmonic lock (>50 cycles)

**Deliverable:**
```python
# System tracks query patterns
for i in range(100):
    results = cart.query("temperature PLA gelling")
    # Access log accumulates

# After 50+ consistent queries
phantoms = cart.get_phantoms()
# Returns: [{"pattern": "temperature_gelling_pla", "cycles": 57}]
```

---

### Week 2: Grain Crystallization

#### Day 1-3: Grain Creation

**Tasks:**
1. Implement grain extraction from phantoms
2. Build ternary delta computation
3. Create pointer map generation
4. Implement grain serialization

**Deliverable:**
```python
# Can crystallize phantom into grain
phantom = cart.get_phantom("temperature_gelling_pla")
grain = crystallize_grain(phantom, cart)
cart.save_grain(grain)
# Grain saved to grains/sg_0x7F3A.json
```

---

#### Day 4-7: Grain Activation

**Tasks:**
1. Implement grain loading on cartridge load
2. Build ternary match logic
3. Create grain-based fact retrieval
4. Optimize for <0.5ms grain lookup

**Deliverable:**
```python
# Grains accelerate queries
cart = load_cartridge("bioplastics")  # Auto-loads grains
results = cart.query("temperature PLA")
# Uses grains for fast ternary match
# Returns facts in <1ms (vs. 28ms without grains)
```

---

### Week 3: Hot/Cold Splitting

**Tasks:**
1. Implement Pareto analysis
2. Build cartridge splitter
3. Create hot/cold cartridge pair
4. Implement automatic split triggers

**Deliverable:**
```python
# System automatically splits cartridges
cart = load_cartridge("bioplastics")
if cart.should_split():
    hot_cart, cold_cart = split_cartridge(cart)
    # Hot: 23% facts, 80% access
    # Cold: 77% facts, 20% access
```

---

### Week 4: Metabolism Integration

**Tasks:**
1. Implement background phantom processing
2. Build automatic grain crystallization
3. Create entropy re-balancing
4. Integrate with Sleeping Giant

**Deliverable:**
```python
# Cartridges learn in background
while system_idle():
    for cart in unslotted_cartridges:
        cart.digest()  # Process phantoms → grains
        cart.rebalance()  # Optimize structure
```

---

## Performance Targets

### Latency Targets

| Operation | Target | Measured | Status |
|-----------|--------|----------|--------|
| Load cartridge | <50ms | TBD | ⏳ |
| Query facts (keyword) | <28ms | TBD | ⏳ |
| Query facts (grain) | <1ms | TBD | ⏳ |
| Add fact | <10ms | TBD | ⏳ |
| Save cartridge | <100ms | TBD | ⏳ |
| Crystallize grain | <500ms | TBD | ⏳ |

### Storage Targets

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Overhead ratio | 2-3% | TBD | ⏳ |
| Grain size | ~250KB | TBD | ⏳ |
| Hot cartridge | <64MB | TBD | ⏳ |
| Index size | <5% of facts | TBD | ⏳ |

### Quality Targets

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Avg confidence | >0.85 | TBD | ⏳ |
| Validation pass rate | >0.90 | TBD | ⏳ |
| Grain lock cycles | >50 | TBD | ⏳ |
| Phantom consistency | >0.80 | TBD | ⏳ |

---

## Appendices

### Appendix A: Example Cartridge

**bioplastics.kbc/** (minimal example)

**facts.db:**
```sql
-- 5 example facts
INSERT INTO facts VALUES (1, 'sha256:7f3a...', 'PLA requires 60°C ±5°C for optimal gelling', '2026-01-15 10:00:00', 47, '2026-02-10 14:23:00', 'active');
INSERT INTO facts VALUES (2, 'sha256:8e4b...', 'Hydration significantly affects polymer kinetics', '2026-01-15 10:05:00', 23, '2026-02-10 12:15:00', 'active');
INSERT INTO facts VALUES (3, 'sha256:9f5d...', 'PLA is a biodegradable thermoplastic polyester', '2026-01-15 10:10:00', 15, '2026-02-09 18:30:00', 'active');
INSERT INTO facts VALUES (4, 'sha256:1a6c...', 'Glass transition temperature of PLA is approximately 60°C', '2026-01-15 10:15:00', 9, '2026-02-08 09:45:00', 'active');
INSERT INTO facts VALUES (5, 'sha256:2b7d...', 'Crystallinity affects mechanical properties of PLA', '2026-01-15 10:20:00', 3, '2026-02-07 16:20:00', 'active');
```

**annotations.jsonl:** (5 lines)
```json
{"fact_id": 1, "metadata": {"confidence": 0.92, "sources": ["Handbook_2023"]}, "derivations": [{"type": "positive_dependency", "target": "temperature"}], "context": {"domain": "bioplastics", "applies_to": ["PLA", "synthetic_polymers"]}}
{"fact_id": 2, "metadata": {"confidence": 0.87, "sources": ["Research_2024"]}, "derivations": [{"type": "positive_dependency", "target": "hydration"}], "context": {"domain": "bioplastics", "applies_to": ["polymers"]}}
{"fact_id": 3, "metadata": {"confidence": 0.95, "sources": ["ISO_Standard"]}, "derivations": [{"type": "classification", "target": "material_type"}], "context": {"domain": "materials_science", "applies_to": ["PLA"]}}
{"fact_id": 4, "metadata": {"confidence": 0.90, "sources": ["Handbook_2023"]}, "derivations": [{"type": "property", "target": "glass_transition"}], "context": {"domain": "thermodynamics", "applies_to": ["PLA"]}}
{"fact_id": 5, "metadata": {"confidence": 0.88, "sources": ["Research_2024"]}, "derivations": [{"type": "affects", "target": "mechanical_properties"}], "context": {"domain": "materials_science", "applies_to": ["PLA"]}}
```

**indices/keyword.idx:**
```json
{
  "pla": [1, 3, 4, 5],
  "temperature": [1, 4],
  "gelling": [1],
  "polymer": [2, 3],
  "biodegradable": [3],
  "crystallinity": [5]
}
```

**manifest.json:**
```json
{
  "cartridge_name": "bioplastics",
  "version": "0.1.0",
  "fact_count": 5,
  "domains": ["bioplastics"],
  "tags": ["PLA", "polymer", "biodegradable"],
  "dependencies": []
}
```

---

### Appendix B: File Size Reference

**For a cartridge with 1000 facts:**

| File | Size | Percentage |
|------|------|------------|
| facts.db | ~800 KB | 80% |
| annotations.jsonl | ~150 KB | 15% |
| indices/ | ~30 KB | 3% |
| grains/ | ~15 KB | 1.5% |
| metadata.json | ~3 KB | 0.3% |
| manifest.json | ~2 KB | 0.2% |
| **Total** | **~1 MB** | **100%** |

Overhead = 50 KB / 1000 KB = **5%** (Week 1 target, will optimize to 2-3%)

---

### Appendix C: Query Execution Flow

```
USER QUERY: "How does temperature affect PLA gelling?"
    ↓
1. HDC + Bloom routing (1.2ms)
    └─> Top 3 cartridges: [bioplastics, thermodynamics, chemistry]
    ↓
2. Load cartridges into hot slots (25ms)
    ├─> Load facts.db
    ├─> Load indices
    └─> Load grains
    ↓
3. Query execution per cartridge (28ms)
    ├─> Keyword index lookup (0.5ms)
    │   └─> Keywords: ["temperature", "PLA", "gelling"]
    │   └─> Matching fact IDs: [1, 4]
    ├─> Grain acceleration (0.3ms)
    │   └─> Check sg_0x7F3A (thermodynamic grain)
    │   └─> Ternary match: +1 (strong match)
    │   └─> Additional fact IDs from pointer_map: [2]
    ├─> Retrieve facts + annotations (2ms)
    │   └─> Facts: [1, 2, 4]
    │   └─> Load from facts.db + annotations.jsonl
    ├─> Score by confidence (0.2ms)
    │   └─> Fact 1: 0.92, Fact 4: 0.90, Fact 2: 0.87
    └─> Return top 10 (25ms)
        └─> [fact_1, fact_4, fact_2]
    ↓
4. Synthesize answer (3ms)
    └─> Combine facts into coherent response
    └─> Include sources + confidence
    ↓
5. Log access (1ms)
    └─> Update access_log.idx
    └─> Increment fact access counts
    └─> Track query pattern
    ↓
TOTAL: ~58ms (within 100ms target)
```

---

### Appendix D: Code Skeleton

**Minimal implementation structure:**

```python
class Cartridge:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.db = None  # SQLite connection
        self.indices = {}
        self.grains = {}
        self.metadata = {}
        self.manifest = {}
    
    def load(self):
        """Load cartridge from disk"""
        self.db = sqlite3.connect(f"{self.path}/facts.db")
        self.indices = self._load_indices()
        self.grains = self._load_grains()
        self.metadata = json.load(open(f"{self.path}/metadata.json"))
        self.manifest = json.load(open(f"{self.path}/manifest.json"))
    
    def query(self, query_text):
        """Query facts by keywords"""
        keywords = extract_keywords(query_text)
        fact_ids = self._keyword_lookup(keywords)
        facts = self._get_facts(fact_ids)
        annotations = self._get_annotations(fact_ids)
        self._log_access(fact_ids, keywords)
        return facts, annotations
    
    def add_fact(self, content, annotation):
        """Add new fact with annotation"""
        content_hash = sha256(content)
        if content_hash in self.indices['content_hash']:
            return self.indices['content_hash'][content_hash]
        
        fact_id = self._insert_fact(content, content_hash)
        self._add_annotation(fact_id, annotation)
        self._update_indices(fact_id, content, annotation)
        return fact_id
    
    def save(self):
        """Save cartridge to disk"""
        self._save_indices()
        self._save_metadata()
        self.db.commit()
    
    def _keyword_lookup(self, keywords):
        """Fast keyword index lookup"""
        candidate_ids = set()
        for kw in keywords:
            candidate_ids.update(self.indices['keyword'].get(kw, []))
        return list(candidate_ids)
    
    def _get_facts(self, fact_ids):
        """Retrieve facts from database"""
        cursor = self.db.cursor()
        placeholders = ','.join('?' * len(fact_ids))
        cursor.execute(f"SELECT * FROM facts WHERE id IN ({placeholders})", fact_ids)
        return cursor.fetchall()
    
    def _get_annotations(self, fact_ids):
        """Retrieve annotations from JSONL"""
        annotations = []
        with open(f"{self.path}/annotations.jsonl") as f:
            for line in f:
                ann = json.loads(line)
                if ann['fact_id'] in fact_ids:
                    annotations.append(ann)
        return annotations
```

---

## End of Specification

**Version:** 1.0  
**Status:** Ready for Week 1 implementation  
**Next Steps:** Create example cartridge, implement loader, test query flow

---

## Change Log

- **2026-02-11**: Initial specification created from integration analysis documents
- **Future**: Will be updated as implementation progresses

---

## References

- Shannon Grain Specification
- Neural Wire Protocol Integration
- Complete System Master Integration
- Cartridge Grain Routing Implementation
