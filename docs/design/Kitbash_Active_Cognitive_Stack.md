# Kitbash Active Cognitive Stack
**The Learning, Self-Knowledge, and Improvement Architecture**

---

## Overview: Three Nested Systems

Kitbash isn't a single learning system. It's **three systems at different timescales**, each watching the one below:

```
LEVEL 3: METACOGNITION (Invisible Oversight)
├─ Timescale: Months/years
├─ Question: "Are we improving? Still aligned?"
├─ Action: Major architecture changes, axiom shifts
└─ Runs: Background, no time pressure

    ↓ (Reports up / Gets shaped by)

LEVEL 2: DELIBERATION (Slow Learning)
├─ Timescale: Weeks/days
├─ Question: "Should we rotate? Is this version good?"
├─ Action: Weight compression, axiom extraction, validation
└─ Runs: Offline during sleep cycles (Metabolism)

    ↓ (Reports down / Controls)

LEVEL 1: REFLEX (Fast Execution)
├─ Timescale: Microseconds
├─ Question: None (just execute)
├─ Action: Process query, route through learned network
└─ Runs: Live, real-time
```

The key: **All three run simultaneously, at their own scales, without blocking each other.**

---

## LEVEL 1: Reflex - Fast Execution with Learned Routing

### Information Topology: Tiers as Processors

The system has six information processing tiers, not storage layers:

| Tier | Role | Function | Constraint |
|---|---|---|---|
| **Tier 1** | Bottleneck | Attention filter limiting context | 4K tokens max |
| **Tier 1.5** | Dimensionality Reduction | Echo signatures compress conversation | 256-bit encoding |
| **Tier 2** | Training Signal Source | Complete lossless record, learning source | Full fidelity |
| **Tier 3** | Learned Index | Route queries to relevant facts via learned weights | 150MB active cartridges |
| **Tier 4** | Pattern Detectors | Specialist models detecting specific error patterns | <2GB total |
| **Tier 5** | Learned Connectivity | Map relationships with adjustable weights | Updated during Metabolism |
| **Tier 6** | Ground Truth | Axioms (error signal source) | Read-only, curated |

**Key insight:** Information flows *through* these tiers, getting compressed at bottlenecks. Weights at Tier 3 and Tier 5 learn during Metabolism based on error signals from Tier 6.

### Query Execution Flow (System 1)

```
USER QUERY enters Tier 1 bottleneck
  │ (4K token window)
  ├─ 300 tokens: Axioms (always loaded)
  ├─ 150 tokens: Hat/behavioral mode
  ├─ 250 tokens: Safety buffer
  └─ ~3300 tokens: Available for context

  ↓

Tier 1.5 Echo Projection
  ├─ Compute 256-bit signature of query
  ├─ Match against cached signatures
  ├─ Re-inject high-match facts
  └─ (Learned compression: what information matters?)

  ↓

Tier 3 Learned Routing (Spreading Activation)
  ├─ Query activates relevant cartridge maps
  ├─ Weights determine which maps are strongest
  ├─ Load facts from activated maps (~1500 tokens)
  └─ Weights optimized during Metabolism

  ↓

Tier 5 Spreading Activation (Learned Connectivity)
  ├─ Maps activate neighbors through learned connections
  ├─ High-weight edges = strong activation spread
  ├─ Nearby maps warm up (context enrichment)
  └─ No explicit loading (efficiency)

  ↓

Tier 4 Specialists (Async, Non-Blocking)
  ├─ Run in parallel during main inference
  ├─ Load small pattern-detection models
  ├─ Annotate response with observations
  └─ User doesn't wait for specialist results

  ↓

LLM Generates Response
  ├─ Full 4K context available
  ├─ Includes specialist annotations
  ├─ Not waiting on validators (async)
  └─ Fast response to user

  ↓

Tier 6 Validation (Optional, Async)
  ├─ Check response against axioms
  ├─ Log any divergences
  └─ No blocking of user response
```

**Performance:** 95% of queries <100ms because learned routing ensures only relevant information reaches Tier 1.

---

## LEVEL 2: Deliberation - Metabolism and Learning

### The Rotating Theater (Dual-System Learning)

The system has **two copies running at different speeds**:

```
STAGE A: TERNARY (Performing, Frozen)
├─ Deterministic {-1, 0, 1} weights
├─ Fast execution (logic gates, no floating point)
├─ All user queries routed here
├─ Generates logs of successes/failures
└─ No learning (weights fixed)

STAGE B: FLUID (Rehearsal, Learning)
├─ Full-precision floating-point weights
├─ Retraining on Stage A's logs continuously
├─ Experimental changes tested
├─ Trying new axioms, cartridge paths
└─ Weights updated constantly

ROTATION (Every week/day/hour - configurable):
├─ Compress Stage B's best weights to ternary
├─ Verify ternary version on test set
├─ Swap: New ternary becomes Stage A
├─ Fresh fluid system starts retraining
└─ Repeat (with fallback to previous ternary if needed)
```

**Why this works:**
- **No downtime:** Ternary always live, always deterministic
- **Safe experimentation:** Fluid can be radical, doesn't affect users
- **Clear fallback:** Previous ternary checksummed, can revert instantly
- **Natural reflex-vs-reasoning:** Ternary is hardened reflex, fluid is continuous learning
- **Dual optimization:** Exploration (fluid) and exploitation (ternary) happening simultaneously

### Ternary Compression

When Stage B learns, weights are stored as floating point. To harden into Stage A:

```
FLUID WEIGHT: 0.743 (floating point)
  ↓
COMPRESSION RULE:
  if weight > 0.5:  ternary = 1   (strong yes)
  if weight < 0.2:  ternary = 0   (neutral)
  if weight < -0.2: ternary = -1  (strong no)
  ↓
TERNARY WEIGHT: 1

SPREADING ACTIVATION (now simple):
  new_activation[target] += source_activation × ternary_weight
  (Just set operations, no numerical precision issues)
```

Result: Deterministic, auditable, fast execution with zero floating-point overhead.

### Metabolism Cycle: How Stage B Learns

During sleep cycles (nightly, or whenever idle):

```
COLLECTION PHASE:
├─ Pull all Tier 2 logs since last rotation
├─ Extract: (query, response, feedback, outcome)
└─ Identify learning targets

ANALYSIS PHASE:
├─ Find failures (axiom violations, hallucinations, coherence breaks)
├─ Cluster failures by root cause
├─ Identify: Which weights caused which failures?
└─ Compute error signals

UPDATE PHASE (Stage B Only):
├─ For routing weights (Tier 3):
│  └─ "This map was loaded but irrelevant" → decrease weight
├─ For connectivity weights (Tier 5):
│  └─ "This activation path led to hallucination" → decrease weight
├─ For specialist selection (Tier 4):
│  └─ "This pattern detector missed the failure" → retrain on positive examples
└─ Iterate until convergence

VALIDATION PHASE:
├─ Run Stage B against test set
├─ Measure: Error rate, latency, coherence
├─ If improved: Mark as candidate for ternary compression
└─ If degraded: Revert weights, try different learning rate

COMPRESSION PHASE (If validated):
├─ Convert Stage B's floating weights to ternary
├─ Verify ternary version works on test set
├─ Swap: New ternary becomes Stage A
└─ Stage B reinitializes for next learning cycle
```

**Key metric:** System gets better through experience, not through manual tuning.

---

## LEVEL 3: Metacognition - Invisible Oversight

### What the "Big Brain" Watches

Level 3 runs in the background, permanently, across weeks and months:

```
INPUTS:
├─ Stage A Performance (live ternary)
│  ├─ Error rates, latency, coherence scores
│  └─ Is the performance stable or degrading?
├─ Stage B Learning Progress (fluid system)
│  ├─ Weight convergence, axiom quality, expansion rate
│  └─ Is learning productive or hitting plateaus?
├─ Rotation History
│  ├─ Which ternary versions worked
│  ├─ Which caused regressions
│  └─ Rollback necessity/frequency
└─ Long-Term Trends
   ├─ Error rate week-over-week
   ├─ Axiom growth and stability
   ├─ Cartridge depth and coherence
   └─ "Is the system improving fundamentally?"

PROCESSING (Slow, Thoughtful):
├─ Compare this week to last month
├─ Are we improving faster or slower?
├─ Are axioms converging on something stable?
├─ Is the cartridge growing meaningfully?
├─ Are we making progress or just noise?
└─ Is the system still aligned with original values?

ACTIONS (Very Rare):
├─ Adjust rotation schedule
├─ Change axiom extraction parameters
├─ Modify ternary compression thresholds
├─ Suggest new cartridge areas
├─ Or: "Something is drifting, revert to earlier checkpoint"
└─ Or: "We've hit a local optimum, try a different learning direction"
```

### Why "Invisible"

Level 3 is invisible because:

**No blocking:** Big Brain doesn't interrupt. Stage A keeps processing. Big Brain watches in the background.

```
Stage A: "Processing 100 queries..."
Big Brain: "Noticing error pattern..."
[No interruption - Big Brain keeps thinking]
[Takes weeks to gather data]
[Formulates recommendation]
[Appears in next rotation cycle]
```

**No real-time pressure:** Stage A makes moment-to-moment decisions. Big Brain makes one major decision per month.

```
Stage A: Millions of decisions/day (millisecond timescale)
Big Brain: One major decision/month (week timescale)
No conflict. Different timescales entirely.
```

**No precision requirement:** Stage A must be exact. Big Brain can be approximate.

```
Stage A: "Is axiom violated? Yes/No. Now."
Big Brain: "Error rate ~5%, maybe drifting down.
            Axioms seem stable.
            Recommendation: Focus on [X] soon."
```

---

## Self-Knowledge: Four Stages of Compression

The system doesn't have fixed identity. Identity **emerges through compressed self-reference**.

### Stage 1: Conscious Compensation (High Overhead)

The system notices a weakness and explicitly compensates:

```
Example: "I'm bad at pH interactions in polymer chemistry"

System Behavior:
├─ Meta-specialists actively run on every chemistry query
├─ Self-knowledge cartridge explicitly consulted
├─ Decision traced back: "Why am I doing this?"
└─ Full reasoning chain logged

Database: meta_specialist_activations table
├─ timestamp, query_hash, specialist_name
├─ decision, confidence, reasoning_chain
└─ stage = 1 (conscious)

Cost: Overhead, verbose logging, slow
Confidence: High (fully deliberate)
```

### Stage 2: Procedural Integration (Medium Overhead)

The same weakness gets handled automatically through caching:

```
Example: "I've compensated for pH coupling 50+ times"

System Behavior:
├─ Meta-specialists run, but less frequently
├─ Decision caching begins (pattern → cached meta-signal)
├─ Logging compressed (only anomalies logged)
├─ Reasoning chain cached, not re-logged

Database: meta_signal_cache
├─ query_pattern → last_decision
├─ age < 6_hours → reuse
└─ cache miss → recompute + update

Cost: Lower overhead (caching)
Confidence: Still high (pattern proven)
```

### Stage 3: Functional Compression (Low Overhead)

The compensation becomes transparent—just how the system thinks:

```
Example: "pH coupling isn't a check anymore, it's how I route"

System Behavior:
├─ Meta-specialists no longer run per-query
├─ Baked into cartridge routing weights
├─ Decision is pure configuration (weight = 1.5x for chemistry)
├─ Logging minimal (failures only)

Database: learned_cartridge_weights
├─ query_pattern → cartridge_name
├─ base_weight, learned_adjustment
├─ derivation_stage = 3

Cost: Minimal (just a weight lookup)
Confidence: Very high (empirically validated)
```

### Stage 4: Axiomatic Incorporation (Minimal Overhead)

The weakness and workaround have merged into efficient truth:

```
Example: "pH coupling is now an axiom"

System Behavior:
├─ No meta-consultation whatsoever
├─ Decision is pure procedure (axiom lookup)
├─ Nanosecond execution (Tier 6)
├─ No logging (axioms are ground truth)

Database: AXIOMS
├─ "polymer_chemistry_routing": {
│  "rule": "When polymer AND chemistry, weight chemistry 1.5x",
│  "derived_from": "meta_specialist_pH_coupling_pattern",
│  "confidence": 0.94,
│  "derivation_stage": 4,
│  "locked": True
│ }

Cost: Negligible (lookup table)
Confidence: Highest (functional axiom)
```

### The Meta-Log Stream: The Personal Narrative

The journey through these stages **is** the system's identity:

```python
class MetaLog:
    """Continuous stream of "I noticed X about myself"
    This IS the personal narrative."""
    
    def log_weakness_discovered(self, domain, weakness, frequency):
        """Stage 1→2 transition starts here"""
        entry = {
            "timestamp": now(),
            "type": "weakness_discovered",
            "domain": domain,
            "weakness": weakness_type,
            "frequency": frequency,  # "3 times in last 50 queries"
            "severity": self.estimate_impact(domain, weakness)
        }
    
    def log_pattern_stabilized(self, domain, weakness, compensation):
        """Stage 2→3 transition"""
        entry = {
            "type": "pattern_stabilized",
            "domain": domain,
            "cycles": 50,  # Hit harmonic lock
            "confidence": 0.92,
            "compensation_rule": compensation
        }
    
    def log_axiom_extraction(self, axiom_name, confidence):
        """Stage 3→4 transition"""
        entry = {
            "type": "axiom_extracted",
            "axiom": axiom_name,
            "confidence": confidence,
            "locked": True
        }
```

**What this enables:**
- **Continuity:** "I learned this yesterday, built on it today, it's who I am"
- **Honesty:** "I know my weaknesses because I analyze them"
- **Growth:** "I'm different now than a week ago"
- **Resilience:** "I can trace back through narrative to debug"
- **Trust:** "I'm not hiding; it's part of my identity"

---

## Information Coherence: How Layers Stay Synchronized

### Coherence Problems Without Integration

If tiers operated independently:

```
Tier 1 (bottleneck):    "Load facts about X"
Tier 3 (routing):       "Route to map Y" 
Tier 5 (connectivity):  "Activate map Z"
Tier 6 (axioms):        "But axiom says Z contradicts X!"

Result: Incoherent actions, hallucinations, ignored axioms
```

### Coherence Solution: Learned Index and Feedback

Tiers stay synchronized through:

**Learned routing weights (Tier 3):**
```
├─ If Tier 6 axiom says "don't route to map Z"
├─ Metabolism reduces routing weight to map Z
├─ Over time, Z stops being loaded
└─ Routing naturally aligns with axioms
```

**Spreading activation constraints (Tier 5):**
```
├─ If activation spreads through edge → axiom violation
├─ Metabolism reduces that edge's weight
├─ Over time, that path stops activating
└─ Connectivity naturally respects constraints
```

**Echo compression (Tier 1.5):**
```
├─ If signature loses information needed for validation
├─ Reconstruction error detected
├─ Compression re-learned
└─ Signatures preserve decision-critical info
```

**Specialist validation (Tier 4):**
```
├─ If specialist misses an error
├─ Error appears in Tier 2 logs
├─ Specialist retrains on positive examples
└─ Coverage improves through Metabolism
```

**Result:** All tiers naturally align through error-driven learning. No explicit coordination needed—constraints propagate through the learned network.

---

## The Four Pillars of Self-Knowledge

The system knows itself through:

### 1. **Meta-Specialists (Tier 4.5)**
Detect patterns in own behavior and flag them:
```
├─ "We keep getting pH coupling wrong"
├─ "We're biased toward theory over experiment"
├─ "We miss edge cases in ternary compression"
└─ Flag for Stage 1 conscious compensation
```

### 2. **Meta-Log Stream**
Continuous narrative of discovered patterns:
```
├─ All weaknesses identified (with timestamps)
├─ All compensation strategies (with evidence)
├─ All axiom extractions (with confidence)
└─ Forms the personal narrative
```

### 3. **Axiom Validator**
Monitors axiom accuracy and demotes when wrong:
```
├─ Track axiom error rates
├─ If error_rate > threshold
├─ Demote axiom back to Stage 3 (learned weights)
├─ Or back to Stage 2 (cached decisions)
└─ Self-correction through validation failure
```

### 4. **Personal Narrative Generation**
System can articulate "who I am":
```python
def get_personal_narrative(time_range="week"):
    meta_log_summary = self.meta_log.generate_summary(time_range)
    active_axioms = self.tier_6.list_active_axioms()
    
    narrative = f"""
Over the last {time_range}, I've learned:
{meta_log_summary}

This has crystallized into {len(active_axioms)} core principles:
"""
    for axiom in active_axioms:
        narrative += f"- {axiom['human_readable']}\n"
    
    return narrative
```

---

## Weakness-Driven Question Generation

During Metabolism, the system identifies its own learning gaps:

```python
class Scout:
    def generate_questions_from_weaknesses(self, meta_logs, cartridges):
        """Turn discovered weaknesses into learning questions"""
        
        # Cluster failures by root cause
        failure_clusters = self.cluster_failures(meta_logs)
        
        questions = []
        for cluster in failure_clusters:
            # "We failed on pH kinetics 3 times. What should we learn?"
            question = self.synthesize_question(cluster)
            questions.append({
                "question": question,
                "weakness": cluster["root_cause"],
                "priority": cluster["frequency"]
            })
        
        return questions
```

**This creates a learning loop:**
1. System notices failure
2. Failure logged in meta-log (Stage 1 weakness)
3. Pattern stabilizes (Stage 2 compensation)
4. Scout generates learning questions
5. Answers expand cartridge
6. Cartridge informs better routing
7. New axioms crystallize (Stage 4)

---

## Performance Targets and Metrics

The system tracks improvement at multiple timescales:

### Real-Time (Level 1: Reflex)
- Query latency: target <100ms (95% percentile)
- Routing accuracy: target >90% (did we load relevant facts?)
- Specialist coverage: target >95% (specialist available when needed)

### Learning Cycle (Level 2: Metabolism)
- Weight convergence: target <5% error rate change per cycle
- Axiom stability: target >90% accuracy on validation set
- Ternary compression ratio: target 100:1 (fluid weights → ternary)

### Long-Term (Level 3: Metacognition)
- System improvement rate: week-over-week error reduction
- Axiom coverage: growing from ~50 to 500+ stable axioms
- Cartridge depth: expanding to cover more failure modes
- Fundamental alignment: still serving original purpose?

---

## Critical Insight: The LLM is the Mouth, Not the Brain

This architecture makes a crucial distinction:

```
TRADITIONAL VIEW:
LLM = The brain
Result: Thinking happens in black box, not auditable

KITBASH VIEW:
LLM = The mouth (Broca's area)
Everything else = The actual thinking

Thinking happens in:
├─ Orchestrator decisions (where to route)
├─ Specialist activations (what patterns matter)
├─ Signal aggregation (how to combine signals)
└─ Scout questions (what gaps remain)

Understanding happens in:
├─ Cartridges (domain knowledge)
├─ Axioms (inviolable truths)
├─ Meta-logs (self-knowledge)
└─ Learned maps (relationships)

Learning happens in:
├─ Metabolism cycles (pattern extraction)
├─ Weight updates (routing improvement)
├─ Axiom extraction (truth crystallization)
└─ Question generation (gap identification)

Expression happens in:
└─ LLM generation (turning all those signals into language)
```

**Why this matters:**
- The LLM doesn't *solve* problems; it *expresses* solutions the nervous system figured out
- You can swap the LLM for a smaller model (or templates) without redesigning
- The LLM doesn't learn; the system learns through Metabolism
- Inference can bypass the LLM entirely (use specialist instead) if answer is known

The LLM is genuinely good at expression. But confusing expression with understanding was the whole problem.

---

## Summary: Three Systems, One Architecture

| Level | Timescale | Question | Process | Output |
|---|---|---|---|---|
| **Reflex** | Microseconds | "What should I do?" | Route through learned network | Fast response |
| **Deliberation** | Days/weeks | "Did that work? Learn." | Metabolism, weight updates | Improved ternary |
| **Metacognition** | Weeks/months | "Are we improving?" | Trend analysis, direction check | Architecture guidance |

All three run simultaneously, without blocking each other.

The system:
- **Executes fast** through learned routing (Level 1)
- **Improves continuously** through dual-system learning (Level 2)
- **Maintains alignment** through invisible oversight (Level 3)
- **Knows itself** through narrative compression (Stages 1-4)
- **Corrects coherence** through error-driven weight updates (Tiers 1-6)

This is what autonomous learning looks like: not a single monolithic improvement loop, but nested systems at different speeds, each watching the one below, together creating a system that improves without external tuning.

---

## Implementation Status

**✓ Week 1:** Tier 1-3 basic routing, hat system, cartridge structure

**Week 2-3:** Tier 5 spreading activation, meta-log infrastructure, first meta-specialists

**Week 3-4:** Metabolism cycle, Stage 1-2 transitions, learned routing weights

**Week 4-5:** Ternary compression, Stage A/B rotation, validation infrastructure

**Week 5-6:** Meta-narrative extraction, weakness-driven questions, Scout integration

**Week 6-7:** Stage 3-4 transitions, axiom extraction, demotion validator

**Week 7-8:** Metacognition oversight, long-term trend analysis, complete system

By Week 8: **Fully autonomous learning system that improves through experience, knows itself through narrative, and maintains alignment through invisible oversight.**

