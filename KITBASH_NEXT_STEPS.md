# Kitbash: What's Next - Immediate Roadmap
**Based on Current State: Phase 3A Complete, Ready for Layer Integration**

---

## 🎯 THE GOAL THIS WEEK

Get from "working components" to "working query system you can talk to."

Current state: You have grain routing (Layer 0) validated. You need to:
1. Add a way to manually test queries
2. Integrate the remaining layers (Layer 1-4)
3. Connect to KoboldCpp so you have a complete pipeline

---

## 📋 IMMEDIATE NEXT STEPS (This Week)

### QUICK WIN #1: Python REPL for Manual Query Testing
**Time: 2 hours | Value: High**

Build a simple command-line interface so you can test queries interactively:

```python
# query_repl.py (already exists, but enhance it)
from grain_router import GrainRouter
from layer0_query_processor import Layer0QueryProcessor

router = GrainRouter('./cartridges')
processor = Layer0QueryProcessor('./cartridges')

while True:
    query = input("> ")
    result = processor.process_query(query)
    print(f"Layer: {result['layer']}")
    print(f"Latency: {result['latency_ms']:.2f}ms")
    if result['layer'] == 'GRAIN':
        print(f"Grain ID: {result.get('grain_id')}")
    print()
```

**Why:** 
- Validate that Layer 0 actually works on real queries you care about
- See latency numbers in practice (not just tests)
- Identify which queries hit grains vs. escalate
- Build confidence in the system

**Deliverable:** Working REPL with metrics display

---

### QUICK WIN #2: Diagnostic Metrics Feed
**Time: 3 hours | Value: High**

Add a parallel output stream showing routing decisions:

```python
# What you'll see:
Query: "Tell me about energy metabolism"
  ✓ Layer 0 hit (grain sg_93386D2A)
  ✓ Latency: 0.19ms
  ✓ Confidence: 0.9559
  → Would return to user
  
Query: "Combine physics and biology to explain photosynthesis"
  ✗ No grain match
  → Escalate to Layer 1 (cartridge lookup)
  → Would use thermodynamics + biochemistry cartridges
```

**Why:**
- See which queries are hitting your grains
- Understand where the 80% hit rate comes from
- Identify gaps (queries that need more layers)
- Real data for optimizing next phases

**Deliverable:** Metrics logged to file + displayed to terminal

---

### TASK #3: Measure Actual Popcount Distribution
**Time: 2 hours | Value: Medium**

The blocker status mentions this: you have 261 grains, but you've never measured the actual popcount (bit) distribution.

```python
# grain_inspection_tool.py
from grain_router import GrainRouter
import statistics

router = GrainRouter('./cartridges')

# For each grain, get its ternary representation
# Count non-zero bits (popcount)
popcounts = []

for grain_id, grain in router.grains.items():
    # Extract ternary weights
    positive_weight = len(grain.get('delta', {}).get('positive', []))
    negative_weight = len(grain.get('delta', {}).get('negative', []))
    popcount = positive_weight + negative_weight
    popcounts.append(popcount)

print(f"Popcount distribution:")
print(f"  Min: {min(popcounts)}")
print(f"  Max: {max(popcounts)}")
print(f"  Mean: {statistics.mean(popcounts):.1f}")
print(f"  Median: {statistics.median(popcounts):.1f}")
print(f"  Stdev: {statistics.stdev(popcounts):.1f}")

# Percentile distribution
for pct in [10, 25, 50, 75, 90]:
    val = statistics.quantiles(popcounts, n=100)[pct-1]
    print(f"  {pct}th percentile: {val:.0f}")
```

**Why:**
- Blocker #2 needs empirical validation
- Know if your Layer 0 activation thresholds (200, 120, <120) are realistic
- Understand actual bit-sliced lookup performance
- Can't optimize what you don't measure

**Deliverable:** Popcount statistics + histogram

---

## 🔧 NEXT WEEK: Layer Integration (Week 2)

### Phase 3B: Build Layer 1 (Reflex Gates)
**Time: 8-10 hours | Complexity: Medium**

Layer 1 is the first escalation path. It's fast (2-5ms) because it uses:
- BitNet ternary models (lightweight)
- Cartridge keyword index lookup
- Simple confidence threshold routing

```
Query comes to Layer 1 if:
  - Layer 0 found no grain match, OR
  - Layer 0 grain confidence < 0.75

Layer 1 does:
  1. Extract keywords from query (spaCy)
  2. Look up keywords in cartridge indices
  3. Find candidate facts (15-50ms)
  4. Return if confidence > threshold
  5. Otherwise escalate to Layer 2
```

**Files to create:**
- `layer1_reflex_gates.py` - BitNet lookup + cartridge routing
- `test_layer1_integration.py` - Integration tests

**Success criteria:**
- Layer 1 hits on 50-70% of escalated queries
- Latency stays <5ms (should be <2ms)
- Proper escalation to Layer 2 when needed

---

### Phase 3C: Connect to KoboldCpp (Chat Interface)
**Time: 6-8 hours | Complexity: Low-Medium**

Right now your system runs standalone. Connect it to KoboldCpp so you can chat:

```
User: "Tell me about PLA plastic"
  ↓
Kitbash Layer 0: "Is this a routing/domain question?"
  → No grain match
  ↓
Kitbash Layer 1: "Does a cartridge know this?"
  → Found in engineering cartridge (fact 42)
  → Confidence 0.88
  ↓
Return to user via KoboldCpp chat interface
```

**Integration point:** Use FastAPI to wrap Kitbash, call from KoboldCpp

```python
# fastapi_bridge.py
from fastapi import FastAPI
from grain_router import GrainRouter
from layer0_query_processor import Layer0QueryProcessor
from layer1_reflex_gates import Layer1RefGates

app = FastAPI()
router = GrainRouter('./cartridges')
l0 = Layer0QueryProcessor('./cartridges')
l1 = Layer1RefGates('./cartridges')

@app.post("/query")
def process_query(query: str):
    result = l0.process_query(query)
    
    if result['layer'] == 'NO_GRAIN':
        result = l1.process_query(query)
    
    return {
        'response': result.get('text'),
        'layer': result.get('layer'),
        'confidence': result.get('confidence'),
        'latency_ms': result.get('latency_ms')
    }
```

Then in KoboldCpp, route queries through this endpoint.

---

## 📊 DECISION POINT: Layer 3+ Strategy

After you complete Layers 0-1 and see real data, you'll need to decide:

### Option A: "Lean" Kitbash (Layers 0-1 only + KoboldCpp)
- Use grains + cartridges for fast answers
- Hand off complex queries to KoboldCpp's full LLM
- Simpler, faster to implement
- Metabolism can wait

### Option B: "Full Stack" Kitbash (Layers 0-4 complete)
- Layer 2: Hot cartridge synthesis
- Layer 3: Specialist SmolML models
- Layer 4: Full LLM with validation
- Includes metabolism + grain crystallization
- More ambitious, better long-term learning

**Recommendation:** Build Option A first (Layers 0-1 + KoboldCpp). Run it for a week. Collect data on:
- Which queries hit which layers
- How often Layer 1 answers are correct
- Where the system struggles
- What patterns emerge

Then use that data to decide if Layer 2+ is worth the complexity.

---

## 🗺️ 30-DAY ROADMAP

### Week 1 (This Week)
- [x] Phase 3A validation ✓
- [ ] Python REPL for manual testing
- [ ] Diagnostic metrics feed
- [ ] Popcount distribution analysis

### Week 2
- [ ] Layer 1 implementation (reflex gates)
- [ ] Layer 1 integration tests
- [ ] KoboldCpp bridge (FastAPI wrapper)
- [ ] Live chat interface

### Week 3
- [ ] Real query data collection (1000+ queries)
- [ ] Hit rate analysis
- [ ] Identify Layer 2 requirements
- [ ] Metabolism cycle planning

### Week 4
- [ ] Decision: Layer 2+ or stabilize current system?
- [ ] If Layer 2: Build cartridge synthesis layer
- [ ] If stable: Focus on metabolism + learning
- [ ] Performance tuning based on real data

---

## 🎯 SUCCESS METRICS (30 Days)

By end of Week 4, you want:

1. **Working Chat Interface** ✓
   - Talk to Kitbash through KoboldCpp
   - Get answers from grains + cartridges
   - See routing decisions

2. **Measured Performance** ✓
   - Layer 0: 0.17ms (confirmed)
   - Layer 1: <5ms (target)
   - Hit rates: 80% L0 + 50-70% L1

3. **Real Data** ✓
   - 1000+ actual queries run
   - Know which queries work, which don't
   - Clear picture of next phase

4. **Informed Decision** ✓
   - Know if Layer 2+ is needed
   - Have data to guide architecture
   - Can estimate effort + value

---

## 🛠️ DEPENDENCY CHECK

### What You Have
- ✓ Grain router (261 grains, 0.17ms lookup)
- ✓ Cartridge system (10 domains, indexed)
- ✓ Layer 0 processor (0.17ms latency)
- ✓ Test suite (comprehensive)
- ✓ KoboldCpp set up and working

### What You Need
- [ ] Layer 1 implementation
- [ ] FastAPI wrapper
- [ ] REPL interface
- [ ] Metrics/diagnostics
- [ ] KoboldCpp integration

### Hardware Check
```
GTX 1060: 6GB VRAM
  - Grain router: <1MB
  - Cartridges: ~2MB
  - Running queries: ~100MB
  - Available for KoboldCpp: 4-5GB ✓

GTX 1070 Ti: 
  - Available when needed for specialist models
  - Not required for Layers 0-2
```

---

## 🚀 START HERE (Next 2 Hours)

1. **Create REPL** (30 min)
   ```bash
   python query_repl.py
   > "what is energy"
   Layer: GRAIN
   Latency: 0.18ms
   Confidence: 0.9559
   ```

2. **Add metrics** (45 min)
   - Show routing decisions
   - Log to file for analysis

3. **Measure popcounts** (45 min)
   - Get distribution statistics
   - Validate assumptions

Then you'll have:
- Working query interface ✓
- Real performance data ✓
- Clear picture of what's next ✓

---

## 🎓 KEY INSIGHT

You're not building Kitbash from scratch anymore. You're building on a proven foundation.

**Layers 0-1 (this week) can handle 80-90% of straightforward queries.** After that, you have real data to decide if more complexity is worth it.

The metabolism cycle can wait. The learning engine can wait. What matters now is getting the system talking to you so you can measure what actually works.

Build the interface. Collect the data. Then optimize.
