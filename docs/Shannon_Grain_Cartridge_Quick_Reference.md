# Quick Reference: Shannon Grain ↔ Cartridge Component Mapping

**Purpose:** One-page reference for how every Shannon Grain concept maps to cartridge infrastructure  
**Use:** Keep this while implementing  

---

## The Core Mapping

| Shannon Grain Concept | Cartridge Equivalent | What It Does |
|---|---|---|
| **Grain** | Single crystallized fact + its derivations | Core unit of learning |
| **Phantom** (Φ) | High-frequency query pattern in Delta Registry | Signal marked for promotion |
| **Harmonic Lock** | >50 cycle stable trend in metabolic cycle | Ready for grain creation |
| **Ternary Crush** | Derivation → {-1, 0, 1} mapping | Compress to 1.58-bit |
| **Sicherman Validation** | Fact validation (axiom + confidence checks) | Gate-keeping before creation |
| **Pointer Map** | Cartridge fact indices + cross-references | Fast lookup structure |
| **Lock State** | Confidence milestone + validation status | Quality assurance |
| **Grain Registry** | Cartridge's grain_inventory in manifest | Catalog of created grains |

---

## The Data Flow: Where Grains Live in Your Cartridge

```
cartridge.kbc (or .md)
│
├─ facts.db
│  └─ [fact_pla_gelling_temp: "PLA requires 60°C"]
│
├─ annotations.jsonl
│  ├─ metadata: [source, confidence 0.92, temporal_valid]
│  ├─ relationships: [links_to: polymer_crystallinity, gelling_mechanism]
│  └─ derivations: [
│      {"type": "positive_dependency", "target": "temperature"},
│      {"type": "boundary", "target": "synthetic_polymers_only"}
│     ]
│
├─ indices/
│  ├─ content_hash.idx (git-like, deduplicatable)
│  ├─ semantic.idx (not needed once grains active)
│  └─ access_log.idx (Delta Registry data here)
│
├─ metadata.json
│  └─ health metrics, split_status, last_updated
│
├─ manifest.json
│  └─ dependencies, grain_inventory (NEW)
│
└─ grains/ (NEW)
   ├─ sg_0x7F3A.json (grain for this domain)
   │  ├─ grain_id: "sg_0x7F3A"
   │  ├─ axiom_link: "Thermodynamic_Dependency"
   │  ├─ weight: 1.58
   │  ├─ delta: {pos: [temperature], neg: [ambient_temp], void: []}
   │  ├─ lock_state: "Sicherman_Validated"
   │  └─ pointer_map: {...}
   │
   └─ sg_0x8E4B.json (another grain)
```

---

## The Lifecycle: Where Grains Come From

### Stage 1: Your Query Arrives

```
User: "What temperature for PLA gelling?"
  ↓
Cartridge routes → bioplastics_cartridge
  ↓
Load hot facts (existing behavior)
```

### Stage 2: Hit Recorded (EXTENDED)

```python
# EXISTING CODE (Week 1)
delta_registry.record_query_hit(
    fact_id="pla_gelling_temp",
    cartridge_id="bioplastics_hot",
    confidence=0.92
)

# NEW CODE (Week 2)
# Same call, but now also tracks:
phantom_key = "bioplastics_hot:pla_gelling_temp"
if phantom_key not in delta_registry.phantoms:
    delta_registry.phantoms[phantom_key] = {
        'hit_count': 1,
        'confidence_history': [0.92]
    }
else:
    delta_registry.phantoms[phantom_key]['hit_count'] += 1
    delta_registry.phantoms[phantom_key]['confidence_history'].append(0.92)
```

### Stage 3: Phantom Identified (NEW)

```
After 5 hits with avg confidence > 0.75:

phantom_key: "bioplastics_hot:pla_gelling_temp"
  status: "persistent"
  hit_count: 7
  avg_confidence: 0.91
  
→ Ready for promotion
```

### Stage 4: Metabolic Cycle (~every 100 queries)

```python
cartridge.metabolic_cycle()
  ├─ Cycle count: 342
  ├─ Persistent phantoms: [pla_gelling_temp, temp_crystallinity_link]
  │
  └─ For each phantom:
     ├─ Track trend over cycles
     ├─ After cycle 390 (50+ cycles persistent):
     │  └─ Trend is stable (variance < 0.05)
     │     └─ HARMONIC LOCK DETECTED
     │        └─ Phantom promoted to crystallization
```

### Stage 5: Validation (NEW)

```python
ShannonGrainValidator().validate_grain(
    phantom={
        'fact_id': 'pla_gelling_temp',
        'hit_count': 87,
        'confidence': 0.91,
        'cycles_locked': 52
    }
)

Checks:
├─ Persistence: Fact confidence 0.92 > 0.7? ✓
├─ Resistance: Derivations compress to ternary? ✓
│  (4 of 5 derivations are {-1, 0, 1} expressible)
└─ Independence: Axiom aligned? ✓
   (Pattern aligns with 3 of 4 domain axioms)

Result: lock_state = "Sicherman_Validated"
```

### Stage 6: Ternary Crush (NEW)

```python
TernaryCrush().crush_phantom_to_grain(phantom, validator_result)

Input (phantom context):
├─ fact_text: ~1KB
├─ related_facts: 5
├─ hit_history: 87 hits over 52 cycles
├─ confidence_trend: [0.88, 0.90, 0.91, 0.92, 0.91, ...]
└─ derivations: [5 related rules]

↓ [Extract 20% that matters]

Ternary mapping:
├─ +1 Reinforcement: [temperature, crystallinity_dependency]
├─ -1 Dampening: [ambient_temperature_noise]
└─  0 Void: [unrelated_polymers]

↓ [Calculate weight]

weight = 1.58 * (hit_score: 0.87 * grelconfi: 0.91 * lock: 0.52)
       = 1.58 * 0.77
       = 1.22

Output (grain):
├─ grain_id: "sg_0x7F3A"
├─ axiom_link: "Thermodynamic_Dependency"
├─ weight: 1.22
├─ delta: {
│    pos: ['fact_polymer_crystallinity', 'fact_gelling_threshold'],
│    neg: ['noise_ambient_temp'],
│    void: []
│  }
├─ lock_state: "Sicherman_Validated"
└─ pointer_map: {...}

RESULT: ~250 bytes core (compressed from ~1KB phantom)
```

### Stage 7: Storage (NEW)

```
cartridge/bioplastics_hot/
├─ grains/
│  └─ sg_0x7F3A.json ← Grain saved here
│
└─ manifest.json
   └─ grain_inventory:
      └─ "sg_0x7F3A": {
         "axiom_link": "Thermodynamic_Dependency",
         "phantom_origin": "pla_gelling_temp",
         "lock_state": "Sicherman_Validated"
      }
```

### Stage 8: Next Query (Activation)

```
User: "What's the PLA gelling temperature?"
  ↓
Cartridge loads hot facts (existing)
  ↓
Cartridge loads associated grains (NEW)
  ├─ L3 cache: sg_0x7F3A pointer_map
  └─ grain_lookup_table registered
  ↓
Ternary grain lookup: <0.5ms
  (vs 50ms semantic search)
  ↓
Return: "60°C, confidence 0.91" (much faster)
```

---

## Side-by-Side: What Changes

### WEEK 1 (Current - Cartridge Only)

```python
class DeltaRegistry:
    def record_query_hit(self, fact_id, cartridge_id, confidence):
        self.hits.append({
            'fact_id': fact_id,
            'confidence': confidence,
            'timestamp': now()
        })
        # That's it
```

### WEEK 2 (Cartridge + Grains)

```python
class DeltaRegistry:
    def __init__(self):
        self.hits = []  # Existing
        self.phantoms = {}  # NEW
    
    def record_query_hit(self, fact_id, cartridge_id, confidence):
        self.hits.append({...})  # Existing
        
        # NEW: Track phantoms
        phantom_key = f"{cartridge_id}:{fact_id}"
        if phantom_key not in self.phantoms:
            self.phantoms[phantom_key] = {
                'hit_count': 1,
                'confidence_history': [confidence],
                'status': 'incubating'
            }
        else:
            self.phantoms[phantom_key]['hit_count'] += 1
            self.phantoms[phantom_key]['confidence_history'].append(confidence)
            
            # Promote if: 5+ hits AND avg confidence > 0.75
            if (self.phantoms[phantom_key]['hit_count'] >= 5 and
                mean(self.phantoms[phantom_key]['confidence_history']) > 0.75):
                self.phantoms[phantom_key]['status'] = 'persistent'
    
    def get_persistent_phantoms(self):
        return [p for p in self.phantoms.values() 
               if p['status'] == 'persistent']
```

**That's the core change. Everything else builds on this foundation.**

---

## The Three Validators (Quick Reference)

### Validator 1: Persistence

**Question:** Is this fact real (not a hallucination)?

```
Check: confidence > 0.7 AND fact references valid sources

If ✓: Can proceed to next validator
If ✗: Grain creation blocked (return early)
```

### Validator 2: Resistance (Compression)

**Question:** Can we express this in ternary {-1, 0, 1}?

```
Check: 80%+ of derivations fit ternary patterns
      (e.g., "X depends on Y" = +1 reinforcement)

If ✓: Can proceed to next validator
If ✗: Grain creation blocked (too complex)
```

### Validator 3: Independence (Axiom Alignment)

**Question:** Does this fit the domain's axioms?

```
Check: 60%+ of domain axioms referenced in fact

If ✓: All validators passed → lock_state = "Sicherman_Validated"
If ✗: Grain creation blocked (domain mismatch)
```

**All 3 must pass** before ternary crush.

---

## The Ternary Logic (Visual)

```
Input: "PLA gelling depends on temperature"

TERNARY MAPPING:
┌─────────────────────────────────────────┐
│  +1 (Reinforcement)                     │
│  ├─ temperature (direct dependency)     │
│  └─ crystallinity (affects gelling)     │
├─────────────────────────────────────────┤
│  -1 (Dampening / Filter)                │
│  └─ ambient_temperature (irrelevant)    │
├─────────────────────────────────────────┤
│   0 (Void / Independent)                │
│  ├─ color (not related to gelling)      │
│  └─ mechanical_properties (independent) │
└─────────────────────────────────────────┘

RESULT: Tripartite pointer map
├─ pos_refs: [temperature, crystallinity]
├─ neg_refs: [ambient_temperature]
└─ void_refs: [color, mechanical_properties]

On query: Check input signal against these three lists
          Return: +1, -1, or 0 (instantly, <0.5ms)
```

---

## File Organization

```
Your project after Week 2:

Code/
├─ Stage1/ (Existing)
│  └─ cartridge_system.py
│
└─ Stage2/ (NEW)
   ├─ delta_registry.py (extended with phantoms)
   ├─ cartridge_metabolism.py (add metabolic_cycle with cycle counter)
   ├─ shannon_grain_validator.py (NEW)
   ├─ ternary_crush.py (NEW)
   └─ grain_activation.py (NEW)

Data/
├─ cartridges/
│  └─ bioplastics_hot/
│     ├─ facts.db
│     ├─ annotations.jsonl
│     ├─ indices/
│     ├─ metadata.json
│     ├─ manifest.json
│     └─ grains/ (NEW)
│        ├─ sg_0x7F3A.json
│        └─ sg_0x8E4B.json
│
└─ grain_registry/ (NEW - optional centralized storage)
   └─ [all grains from all cartridges]
```

---

## Performance Summary

| Metric | Week 1 (Cartridge Only) | Week 3 (+ Grains) | Improvement |
|--------|------------------------|-------------------|-------------|
| Fact lookup | 50ms | 15ms | 3x faster |
| Semantic search | 100ms | N/A | N/A |
| Ternary lookup | N/A | 0.5ms | N/A |
| Hot query latency | 160ms | 18ms | **9x faster** |
| Storage per domain | 2.6MB | 1.3MB | **50% reduction** |
| L3 cache for grains | N/A | 64MB active | **enables 3-4x domains** |

---

## Checklist: Is This Integrated?

**Week 2 completion criteria:**

- [ ] DeltaRegistry tracks phantoms (5+ hits)
- [ ] Phantoms reach "persistent" status (avg confidence > 0.75)
- [ ] CartridgeMetabolism.metabolic_cycle() runs (~every 100 queries)
- [ ] Harmonic lock detected (>50 cycles stable)
- [ ] ShannonGrainValidator checks all 3 rules
- [ ] TernaryCrush creates ternary grains (~250 bytes)
- [ ] Grains saved to cartridge/grains/ directory
- [ ] GrainActivation loads grains into L3 cache
- [ ] Ternary lookup < 0.5ms measured
- [ ] First grain created from persistent phantom

**If all checked:** You've successfully integrated Shannon Grain with Cartridge.

---

## One More Thing: Why This Works

The reason cartridges and Shannon Grains work together so perfectly:

**Cartridges ask:** "What are the relationships?"  
**Grains ask:** "What matters most?"

Cartridges provide the **semantic scaffolding** (facts + context).  
Grains provide the **structural compression** (20% that matters).

Together: Knowledge that scales **logarithmically** instead of exponentially.

That's the entire point.
