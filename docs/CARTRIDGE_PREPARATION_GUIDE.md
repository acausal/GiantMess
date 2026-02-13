# **Cartridge Preparation Guide for Phase 2B**
**Purpose:** Prepare test cartridges to enable Phase 2B query stream integration  
**Created:** February 12, 2026

---

## **OVERVIEW**

Phase 2B needs **cartridges to query against**. You don't yet have:

1. Test cartridges with actual facts
2. A query interface that returns fact hits
3. A DeltaRegistry to track query statistics

This guide walks you through creating both.

---

## **WHAT YOU NEED**

### **1. Cartridge Data (Input)**

You need **fact databases** to populate cartridges. These can be:

- **Markdown files** (structured, human-readable)
- **CSV files** (spreadsheets)
- **JSON files** (programmatic)
- **Plain text** (simple list of facts)

**Scope:** For Phase 2B testing, you need:
- **2-3 test cartridges** (small, diverse domains)
- **500-1000 facts per cartridge** (enough to generate patterns)
- **Domain diversity** (so queries hit multiple facts)

### **2. Cartridge Infrastructure**

From your existing code, you have:
- ✅ `Cartridge` class (fact storage, indexing)
- ✅ `CartridgeBuilder` class (populate from files)
- ✅ `AnnotationMetadata` (confidence, sources, context)
- ✅ `DeltaRegistry` (query tracking)

**What's missing:**
- ❓ Query interface (how to ask cartridges for facts)
- ❓ Query result structure (what does a "hit" look like)
- ❓ Integration with Shannon Grain tracking

---

## **STEP 1: CREATE TEST DATA**

You have three options. I recommend **Option A** (markdown) for clarity.

### **Option A: Markdown Format (RECOMMENDED)**

**File: `data/philosophy.md`**

```markdown
# Philosophy

## Epistemology
- Knowledge requires justified true belief | Plato | 0.95
- Empiricism claims all knowledge comes from experience | Locke | 0.90
- Rationalism claims knowledge comes from reason | Descartes | 0.92
- The problem of induction questions whether we can justify generalization | Hume | 0.88

## Metaphysics
- Aristotle believed substances have forms and matter | Aristotle | 0.93
- Idealism claims only minds and ideas are real | Berkeley | 0.85
- Materialism claims only matter is fundamentally real | Democritus | 0.87
- Free will vs determinism remains unresolved | Various | 0.75

## Ethics
- Utilitarianism seeks to maximize overall happiness | Mill | 0.88
- Deontological ethics focuses on duties and rules | Kant | 0.89
- Virtue ethics emphasizes character development | Aristotle | 0.91
- The trolley problem tests moral intuitions | Thomson | 0.80
```

**File: `data/biology.md`**

```markdown
# Biology

## Cell Biology
- Cells are the basic unit of life | Schwann/Schleiden | 0.99
- Mitochondria are the powerhouse of the cell | Various | 0.95
- DNA carries genetic information | Watson/Crick | 0.99
- Proteins are synthesized via the ribosome | Various | 0.96
- Osmosis is the movement of water across membranes | Various | 0.94

## Evolution
- Evolution occurs through natural selection | Darwin | 0.95
- Genetic drift affects small populations more | Wright | 0.91
- Speciation happens through reproductive isolation | Dobzhansky | 0.88
- The fossil record shows species transitions | Various | 0.87
- Adaptation is when organisms fit their environment | Various | 0.92

## Genetics
- Genes are units of inheritance | Mendel | 0.98
- DNA has a double helix structure | Watson/Crick | 0.99
- Mutations can be beneficial or harmful | Various | 0.93
- Epigenetics affects gene expression without changing DNA | Various | 0.85
```

**File: `data/computer_science.md`**

```markdown
# Computer Science

## Algorithms
- Big O notation measures algorithm complexity | Bachmann | 0.97
- Sorting algorithms vary in efficiency | Various | 0.98
- Recursion breaks problems into subproblems | Various | 0.96
- Divide and conquer is an effective strategy | Various | 0.95
- Graph algorithms solve connectivity problems | Various | 0.93

## Data Structures
- Arrays provide O(1) random access | Various | 0.98
- Linked lists allow O(1) insertion | Various | 0.96
- Hash tables provide average O(1) lookup | Various | 0.94
- Trees organize hierarchical data | Various | 0.97
- Heaps maintain partial ordering | Various | 0.95

## Machine Learning
- Neural networks approximate arbitrary functions | Various | 0.90
- Backpropagation trains deep networks | Rumelhart et al | 0.94
- Gradient descent optimizes loss functions | Various | 0.96
- Overfitting occurs when models memorize noise | Various | 0.95
- Cross-validation estimates generalization error | Various | 0.93
```

**Why markdown?**
- Human-readable (easy to edit, review)
- Natural hierarchy (domain → subdomain → facts)
- Metadata inline (confidence, sources)
- CartridgeBuilder has built-in support

---

### **Option B: CSV Format**

If you prefer spreadsheet format:

**File: `data/philosophy.csv`**

```csv
domain,subdomain,content,source,confidence
Epistemology,,Knowledge requires justified true belief,Plato,0.95
Epistemology,,Empiricism claims all knowledge comes from experience,Locke,0.90
Epistemology,,Rationalism claims knowledge comes from reason,Descartes,0.92
Epistemology,,The problem of induction questions whether we can justify generalization,Hume,0.88
Metaphysics,,Aristotle believed substances have forms and matter,Aristotle,0.93
Metaphysics,,Idealism claims only minds and ideas are real,Berkeley,0.85
...
```

---

### **Option C: JSON Format**

**File: `data/philosophy.json`**

```json
{
  "domain": "Philosophy",
  "facts": [
    {
      "content": "Knowledge requires justified true belief",
      "source": "Plato",
      "confidence": 0.95,
      "subdomain": "Epistemology"
    },
    {
      "content": "Empiricism claims all knowledge comes from experience",
      "source": "Locke",
      "confidence": 0.90,
      "subdomain": "Epistemology"
    }
  ]
}
```

---

## **STEP 2: BUILD CARTRIDGES FROM DATA**

Using your existing `CartridgeBuilder`:

```python
#!/usr/bin/env python3
"""
Build test cartridges for Phase 2B integration testing.
"""

from kitbash_builder import CartridgeBuilder
from pathlib import Path

def build_test_cartridges():
    """Create three test cartridges from markdown files."""
    
    cartridge_configs = [
        ("philosophy", "data/philosophy.md"),
        ("biology", "data/biology.md"),
        ("computer_science", "data/computer_science.md"),
    ]
    
    for cart_name, data_file in cartridge_configs:
        print(f"\n{'='*60}")
        print(f"Building cartridge: {cart_name}")
        print(f"{'='*60}")
        
        # Create builder
        builder = CartridgeBuilder(cart_name, "./cartridges")
        
        # Create empty cartridge
        builder.build()
        
        # Load facts from markdown
        builder.from_markdown(data_file)
        
        # Save to disk
        builder.save()
        
        # Report
        print(f"✓ Cartridge saved to: ./cartridges/{cart_name}.kbc/")

if __name__ == "__main__":
    build_test_cartridges()
```

**Run it:**
```bash
python3 build_test_carts.py
```

**Result:**
```
cartridges/
├── philosophy.kbc/
│   ├── facts.db
│   ├── annotations.jsonl
│   ├── indices/
│   │   ├── keyword.idx
│   │   └── content_hash.idx
│   ├── metadata.json
│   └── manifest.json
├── biology.kbc/
└── computer_science.kbc/
```

---

## **STEP 3: CREATE A QUERY INTERFACE**

Cartridges exist, but you need a way to **query them and get hits**. Create:

**File: `kitbash_query_engine.py`**

```python
"""
Query Engine for Cartridges
Provides a unified interface to query cartridges and return hits.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from kitbash_cartridge import Cartridge

class QueryResult:
    """Result of a query against a cartridge."""
    
    def __init__(self, query_text: str, fact_ids: Set[int], 
                 confidences: Dict[int, float], source: str = ""):
        self.query_text = query_text
        self.fact_ids = fact_ids
        self.confidences = confidences  # fact_id -> confidence
        self.source = source
        self.avg_confidence = (
            sum(confidences.values()) / len(confidences) 
            if confidences else 0.0
        )
    
    def __repr__(self):
        return f"QueryResult(query='{self.query_text}', hits={len(self.fact_ids)}, confidence={self.avg_confidence:.2f})"


class CartridgeQueryEngine:
    """
    Query engine for multiple cartridges.
    Supports keyword search, semantic search (basic), and fact retrieval.
    """
    
    def __init__(self, cartridge_dir: str = "./cartridges"):
        self.cartridge_dir = Path(cartridge_dir)
        self.cartridges: Dict[str, Cartridge] = {}
        self.load_all_cartridges()
    
    def load_all_cartridges(self):
        """Load all .kbc directories as cartridges."""
        if not self.cartridge_dir.exists():
            print(f"Cartridge directory not found: {self.cartridge_dir}")
            return
        
        for kbc_path in self.cartridge_dir.glob("*.kbc"):
            cart_name = kbc_path.stem
            try:
                cart = Cartridge(cart_name, str(self.cartridge_dir))
                cart.load()
                self.cartridges[cart_name] = cart
                print(f"✓ Loaded cartridge: {cart_name} ({len(cart.facts)} facts)")
            except Exception as e:
                print(f"✗ Failed to load {cart_name}: {e}")
    
    def keyword_query(self, query_text: str, cartridge_name: str = None) -> QueryResult:
        """
        Simple keyword matching across facts.
        
        Args:
            query_text: Words to search for (space-separated)
            cartridge_name: Specific cartridge, or None to search all
        
        Returns:
            QueryResult with matching fact IDs and confidences
        """
        query_words = set(query_text.lower().split())
        matching_facts = {}
        
        # Search specified cartridge or all
        carts_to_search = (
            {cartridge_name: self.cartridges[cartridge_name]} 
            if cartridge_name else self.cartridges
        )
        
        for cart_name, cart in carts_to_search.items():
            for fact_id, fact in cart.facts.items():
                fact_words = set(fact.lower().split())
                
                # Count matching words
                match_count = len(query_words & fact_words)
                
                if match_count > 0:
                    # Confidence is fraction of query words that matched
                    match_confidence = match_count / len(query_words)
                    
                    # Combine with fact's own confidence if available
                    fact_confidence = cart.annotations.get(fact_id, {}).get('confidence', 0.8)
                    combined = (match_confidence + fact_confidence) / 2
                    
                    matching_facts[fact_id] = combined
        
        return QueryResult(query_text, set(matching_facts.keys()), 
                          matching_facts, cartridge_name or "all")
    
    def get_fact(self, fact_id: int, cartridge_name: str) -> str:
        """Retrieve a single fact by ID."""
        if cartridge_name not in self.cartridges:
            return None
        return self.cartridges[cartridge_name].facts.get(fact_id)
    
    def get_fact_confidence(self, fact_id: int, cartridge_name: str) -> float:
        """Get confidence for a fact."""
        if cartridge_name not in self.cartridges:
            return 0.0
        cart = self.cartridges[cartridge_name]
        return cart.annotations.get(fact_id, {}).get('confidence', 0.8)


# Example usage
if __name__ == "__main__":
    engine = CartridgeQueryEngine("./cartridges")
    
    # Test queries
    queries = [
        "knowledge belief justified",
        "DNA genetic inheritance",
        "algorithm complexity sorting",
        "evolution natural selection",
    ]
    
    for query in queries:
        result = engine.keyword_query(query)
        print(f"\nQuery: {result.query_text}")
        print(f"Hits: {len(result.fact_ids)}, Avg Confidence: {result.avg_confidence:.2f}")
        for fact_id in list(result.fact_ids)[:3]:  # Show first 3
            cart_name = "unknown"
            for cn, cart in engine.cartridges.items():
                if fact_id in cart.facts:
                    cart_name = cn
                    break
            fact_text = engine.get_fact(fact_id, cart_name)
            print(f"  - [{result.confidences[fact_id]:.2f}] {fact_text[:60]}...")
```

---

## **STEP 4: IMPLEMENT DELTA REGISTRY**

The DeltaRegistry tracks query statistics (hit counts, frequencies, etc.).

**File: `kitbash_delta_registry.py`**

```python
"""
Delta Registry: Tracks query statistics over time.
Used by Shannon Grain crystallization to detect patterns.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Set, List
from collections import defaultdict
import json
from pathlib import Path


@dataclass
class QueryStatistics:
    """Statistics for a single fact_id over time."""
    fact_id: int
    cartridge_name: str
    hit_count: int = 0           # How many times queried
    total_confidence: float = 0.0 # Sum of confidences
    first_hit_cycle: int = 0
    last_hit_cycle: int = 0
    cycles_active: int = 0        # How many cycles had hits


class DeltaRegistry:
    """
    Tracks query hits over time. Feeds phantom tracking.
    """
    
    def __init__(self, storage_path: str = "./registry"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Current cycle
        self.current_cycle = 0
        
        # fact_id -> QueryStatistics
        self.fact_stats: Dict[int, QueryStatistics] = {}
        
        # Track hits in current cycle
        self.current_cycle_hits: List[Tuple[int, float]] = []
    
    def record_hit(self, fact_id: int, cartridge_name: str, confidence: float):
        """
        Record that a fact was retrieved.
        
        Args:
            fact_id: ID of the fact
            cartridge_name: Which cartridge it came from
            confidence: Confidence of the hit (0-1)
        """
        # Create or update stats
        if fact_id not in self.fact_stats:
            self.fact_stats[fact_id] = QueryStatistics(
                fact_id=fact_id,
                cartridge_name=cartridge_name
            )
        
        stats = self.fact_stats[fact_id]
        stats.hit_count += 1
        stats.total_confidence += confidence
        stats.last_hit_cycle = self.current_cycle
        
        if stats.first_hit_cycle == 0:
            stats.first_hit_cycle = self.current_cycle
        
        # Track for current cycle
        self.current_cycle_hits.append((fact_id, confidence))
    
    def advance_cycle(self):
        """
        Move to next cycle (e.g., end of query batch or hour).
        Updates active cycle count.
        """
        for fact_id, conf in self.current_cycle_hits:
            if fact_id in self.fact_stats:
                self.fact_stats[fact_id].cycles_active += 1
        
        self.current_cycle += 1
        self.current_cycle_hits = []
    
    def get_fact_stats(self, fact_id: int) -> QueryStatistics:
        """Get statistics for a fact."""
        return self.fact_stats.get(fact_id)
    
    def get_hot_facts(self, top_k: int = 20) -> List[QueryStatistics]:
        """Get the K most frequently hit facts."""
        sorted_facts = sorted(
            self.fact_stats.values(),
            key=lambda s: s.hit_count,
            reverse=True
        )
        return sorted_facts[:top_k]
    
    def get_average_confidence(self, fact_id: int) -> float:
        """Get average confidence for a fact across all hits."""
        stats = self.fact_stats.get(fact_id)
        if not stats or stats.hit_count == 0:
            return 0.0
        return stats.total_confidence / stats.hit_count
    
    def save(self):
        """Persist registry to disk."""
        data = {
            'current_cycle': self.current_cycle,
            'facts': {
                str(fid): asdict(stats) 
                for fid, stats in self.fact_stats.items()
            }
        }
        registry_file = self.storage_path / "delta_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load registry from disk."""
        registry_file = self.storage_path / "delta_registry.json"
        if not registry_file.exists():
            return
        
        with open(registry_file, 'r') as f:
            data = json.load(f)
        
        self.current_cycle = data['current_cycle']
        for fid_str, stats_dict in data['facts'].items():
            fact_id = int(fid_str)
            stats = QueryStatistics(**stats_dict)
            self.fact_stats[fact_id] = stats


# Example usage
if __name__ == "__main__":
    registry = DeltaRegistry()
    
    # Simulate query hits
    for cycle in range(10):
        # Simulate some queries
        registry.record_hit(1, "philosophy", 0.95)
        registry.record_hit(2, "philosophy", 0.90)
        registry.record_hit(1, "philosophy", 0.92)  # Repeat
        registry.record_hit(5, "biology", 0.87)
        
        registry.advance_cycle()
    
    # Check what we recorded
    print("Hot facts:")
    for stats in registry.get_hot_facts(5):
        print(f"  Fact {stats.fact_id}: {stats.hit_count} hits, "
              f"avg conf={registry.get_average_confidence(stats.fact_id):.2f}")
```

---

## **STEP 5: INTEGRATION TEST**

Put it all together:

**File: `test_cartridge_integration.py`**

```python
#!/usr/bin/env python3
"""
Integration test: Cartridges → Queries → DeltaRegistry
Simulates Phase 2B query stream.
"""

from kitbash_query_engine import CartridgeQueryEngine
from kitbash_delta_registry import DeltaRegistry
import random


def test_integration():
    """
    1. Load cartridges
    2. Run simulated query stream
    3. Track hits in DeltaRegistry
    4. Show results
    """
    
    # Initialize
    engine = CartridgeQueryEngine("./cartridges")
    registry = DeltaRegistry("./registry")
    
    # Simulated queries (like what users would ask)
    test_queries = [
        "knowledge belief justified",
        "DNA genes inheritance",
        "algorithm complexity",
        "evolution natural selection",
        "knowledge epistemology truth",
        "cells mitochondria energy",
        "algorithms sorting efficiency",
        "neural networks learning",
        "evolution adaptation fitness",
        "belief knowledge epistemic",
    ]
    
    print("="*70)
    print("PHASE 2B CARTRIDGE INTEGRATION TEST")
    print("="*70)
    
    # Run 10 query cycles
    for cycle in range(10):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # Pick random queries for this cycle
        cycle_queries = random.sample(test_queries, 5)
        
        for query in cycle_queries:
            result = engine.keyword_query(query)
            print(f"Query: '{query}' → {len(result.fact_ids)} hits")
            
            # Record each hit in registry
            for fact_id in result.fact_ids:
                confidence = result.confidences[fact_id]
                
                # Find which cartridge this fact is from
                cart_name = "unknown"
                for cn, cart in engine.cartridges.items():
                    if fact_id in cart.facts:
                        cart_name = cn
                        break
                
                registry.record_hit(fact_id, cart_name, confidence)
        
        registry.advance_cycle()
    
    # Report
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\nTotal cycles: {registry.current_cycle}")
    print(f"Total unique facts hit: {len(registry.fact_stats)}")
    
    print("\nTop 10 hot facts:")
    for i, stats in enumerate(registry.get_hot_facts(10), 1):
        avg_conf = registry.get_average_confidence(stats.fact_id)
        print(f"  {i}. Fact {stats.fact_id}: {stats.hit_count} hits, "
              f"avg confidence={avg_conf:.2f}, cycles_active={stats.cycles_active}")
    
    # Save for later use
    registry.save()
    print("\n✓ Registry saved to ./registry/")


if __name__ == "__main__":
    test_integration()
```

**Run it:**
```bash
python3 test_cartridge_integration.py
```

**Expected output:**
```
--- Cycle 1 ---
Query: 'knowledge belief justified' → 4 hits
Query: 'DNA genes inheritance' → 3 hits
...

RESULTS
Total cycles: 10
Total unique facts hit: 27

Top 10 hot facts:
  1. Fact 1: 12 hits, avg confidence=0.93, cycles_active=8
  2. Fact 5: 11 hits, avg confidence=0.91, cycles_active=7
  ...
```

---

## **CHECKLIST: CARTRIDGE PREPARATION**

- [ ] Create test data files (3x markdown files, ~50 facts each)
- [ ] Implement/verify CartridgeBuilder works
- [ ] Build 3 test cartridges (`philosophy.kbc`, `biology.kbc`, `computer_science.kbc`)
- [ ] Implement CartridgeQueryEngine (keyword search)
- [ ] Implement DeltaRegistry (statistics tracking)
- [ ] Run integration test (10 cycles, 50+ hits)
- [ ] Verify registry saves/loads
- [ ] Document query interface

---

## **WHY THIS MATTERS FOR PHASE 2B**

Phase 2B's CartridgeQueryBridge will:

```python
engine = CartridgeQueryEngine("./cartridges")
registry = DeltaRegistry("./registry")

# Phase 2B: Feed real hits to phantom tracker
result = engine.keyword_query("knowledge belief")
for fact_id in result.fact_ids:
    phantom_tracker.record_phantom_hit(
        fact_ids={fact_id},
        concepts=["epistemology"],
        confidence=result.confidences[fact_id]
    )
```

**Without** cartridges and a query engine, Phase 2B can't start.

---

## **NEXT STEPS**

1. **This week (Prep):**
   - Create test data files
   - Build cartridges
   - Implement query engine + DeltaRegistry
   - Run integration test

2. **Phase 2B (Week 1):**
   - Connect CartridgeQueryBridge to phantom tracker
   - Feed real query hits over time
   - Lock first phantoms
   - Validate and crystallize

3. **Phase 2B (Week 2):**
   - Collect empirical thresholds
   - Measure real performance
   - Persist grains

---

**Created:** February 12, 2026  
**Ready to execute:** Yes  
**Estimated time:** 1-2 days for prep, then Phase 2B can begin
