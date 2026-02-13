# The Sleeping Giant: The Unconscious Layer
**Deep Optimization Loop Running Beneath Conscious and Subconscious**

---

## Overview: Three Levels of Consciousness

Kitbash has **three nested layers of cognition**, each operating at different speeds and timescales:

```
CONSCIOUS (Level 1: Reflex - Milliseconds)
├─ Real-time interaction with users
├─ Fast routing through learned network
├─ Immediate responses
└─ What the user experiences

    ↓ (Invisible to user)

SUBCONSCIOUS (Level 2: Deliberation - Hours)
├─ Offline learning during sleep cycles
├─ Metabolism: Weight updates, pattern extraction
├─ Axiom compression (Stages 1-4)
├─ Runs nightly
└─ Improves the conscious system

    ↓ (Invisible even to subconscious)

UNCONSCIOUS (Level 3: Sleeping Giant - Tokens Per Minute)
├─ Deep reasoning on separate machine
├─ 80B MOE model doing intensive analysis
├─ Expert system bootstrapping
├─ Axiom extraction and validation
├─ Shapes the foundation of everything above
└─ Runs continuously, never stops
```

Each level makes the level above it smarter, but remains invisible to it.

---

## The Three-Machine Architecture

Kitbash actually runs on **three separate systems**:

```
MACHINE 1: CONSCIOUS (User-Facing)
├─ Hardware: GTX 1060 (6GB VRAM)
├─ Model: Hermes-3-8B (live, responsive)
├─ Speed: Milliseconds to seconds per query
├─ Timescale: Real-time, interactive
├─ Role: Answer questions, route through layers, gather signals
├─ Level: Conscious (what user experiences)
└─ Output: Deferred queries + raw signals → passed to subconscious

        ↓ (Each night, signals flow down)

MACHINE 2: SUBCONSCIOUS (Offline Learning)
├─ Hardware: Same as Machine 1, or quiet background process
├─ Process: Metabolism cycle (weight updates, pattern extraction)
├─ Speed: Hours (nightly, while user sleeps)
├─ Timescale: Overnight cycles
├─ Role: Learn from daily interactions, compress patterns, extract axioms
├─ Level: Subconscious (invisible to conscious layer)
└─ Output: Improved weights, new axioms → passed to unconscious

        ↓ (Continuously flowing down)

MACHINE 3: THE SLEEPING GIANT (Deep Optimization)
├─ Hardware: Separate workstation or server
├─ Model: 80B MOE (Mixture of Experts)
├─ Speed: Tokens per minute (not per second)
├─ Timescale: Continuous (never stops, runs overnight and idle)
├─ Role: Deep reasoning, expert system extraction, axiom validation
├─ Level: Unconscious (invisible even to subconscious)
├─ Technique: RAM swapping + MOE sparse activation
└─ Output: Validated axioms, expert rules → feeds back to subconscious

The Sleeping Giant runs continuously in the background, one expert at a time,
slowly improving the entire system beneath the user's awareness.
```

---

## How the Three Levels Interact

### Information Flow: Down and Back Up

```
SIGNALS FLOW DOWN:
Conscious layer (user interactions)
  ├─ Corrections ("!correct [better answer]")
  ├─ Failures (axiom violations, hallucinations)
  ├─ Deferral requests (hard queries)
  └─ Raw signals (what worked, what didn't)
  
    ↓ (Nightly batch)
    
Subconscious layer (metabolism)
  ├─ Analyzes patterns in signals
  ├─ Updates weights
  ├─ Extracts axiom candidates
  └─ Proposes improvements
  
    ↓ (Continuous flow)
    
Unconscious layer (Sleeping Giant)
  ├─ Validates subconscious proposals
  ├─ Does deep reasoning on hard cases
  ├─ Bootstraps expert systems
  ├─ Confirms or refutes axioms
  └─ Prioritizes next improvements

IMPROVEMENTS FLOW UP:
Unconscious produces:
  ├─ Validated axioms (high confidence)
  ├─ Expert routing rules
  ├─ New domain knowledge
  └─ Corrected learned weights
  
    ↑ (Integration to subconscious)
    
Subconscious integrates and refines:
  ├─ Axioms → Tier 6 (ground truth)
  ├─ Rules → Tier 5 (routing weights)
  ├─ Knowledge → Cartridge updates
  ├─ Weights → Stage B learning substrate
  └─ Makes ready for morning deployment
  
    ↑ (Integration to conscious)
    
Conscious layer uses improved system:
  ├─ Better routing (improved weights)
  ├─ Better validation (new axioms)
  ├─ Better expert rules (new domain knowledge)
  └─ System is noticeably smarter next morning
```

### Each Level Serves the One Above

```
CONSCIOUS asks:
"What should I do right now?"
├─ Uses: Current weights, axioms, cartridges
├─ Speed: Milliseconds
└─ Responds: Immediately

SUBCONSCIOUS asks:
"What should we learn from today?"
├─ Analyzes: All daily signals
├─ Extracts: Patterns, axiom candidates
├─ Speed: Hours (nightly)
└─ Responds: Improved weights by morning

UNCONSCIOUS asks:
"Are those improvements actually right?"
├─ Deep reasoning: Validates everything
├─ Expert synthesis: Creates new knowledge
├─ Speed: Tokens per minute
└─ Responds: Validated improvements over time
```

### The Asymmetry: Downward is Invisible

**Conscious doesn't know about Subconscious:**
- Conscious layer wakes up each morning
- New weights are in place (but Conscious doesn't know they were learned)
- Better axioms are loaded (but Conscious doesn't know their origin)
- Result: System just works better, mysteriously improved

**Subconscious doesn't know about Sleeping Giant:**
- Subconscious does metabolism each night
- Produces axiom candidates (but doesn't validate them)
- Proposes improvements (but doesn't confirm them)
- Next morning: Some are integrated, some are in pending queue
- Subconscious doesn't see the Sleeping Giant's reasoning, just the validated results

**Sleeping Giant knows everything:**
- Has access to all signals from Conscious
- Sees all proposals from Subconscious
- Validates or rejects them
- But Sleeping Giant's work is invisible to both layers above

This is the key: **Information flows DOWN (invisibly) and improvements flow UP (as completed facts).**

---

## Signal Flow Examples

### Example 1: User Correction

```
CONSCIOUS (2:47 PM):
User: "What time is it?"
System: "It's 14:47 EST"
User: "!correct Actually, 14:47 UTC not EST"
System: Logs correction to signals/

SUBCONSCIOUS (1:00 AM that night):
Metabolism reads: 12 timezone-related corrections
Analysis: "System confuses EST/UTC"
Proposes:
  ├─ New axiom: "Always include UTC when discussing time"
  ├─ New rule: "Timezone questions → chronos specialist"
  └─ Confidence: 0.78 (needs validation)
Output: Queues to "axiom_candidates_pending.md"

UNCONSCIOUS (3:00 AM):
Sleeping Giant reads: "timezone axiom candidate"
Analysis: Deep reasoning on timezone problem
Validates: "Yes, this axiom prevents future errors"
Confidence: 0.91
Output: Writes to "axioms_validated_[date].md"

INTEGRATION (7:00 AM):
Subconscious wakes up, loads validated axioms
Conscious layer now has: Axiom active in Tier 6
User wakes up: System now says "14:47 UTC" by default
User doesn't know what happened. System just got smarter.
```

### Example 2: Failure Pattern

```
CONSCIOUS (Multiple sessions over week):
User keeps correcting: "No, hydration affects gelling"
Another user: "pH interacts with hydration"
Another user: "Water content is critical"
System pattern: Misses water-thermodynamics coupling
Logs all to: signals/failures_water_coupling.jsonl

SUBCONSCIOUS (Friday night, deep metabolism):
Clusters: 47 corrections → 5 root failure modes
Pattern: "Water-thermodynamics coupling"
Question: "What expertise is missing?"
Proposes:
  ├─ New cartridge facts about water in polymers
  ├─ New specialist routing (hydration → physical chemistry)
  └─ Confidence: 0.65 (needs expert validation)

UNCONSCIOUS (Friday night, continuous):
Sleeping Giant: "Hydration-coupling failure pattern"
Deep reasoning: 90 minutes of MOE expert synthesis
Expert 1 (Materials): "Water structure in polymers..."
Expert 2 (Thermodynamics): "Entropy and hydration..."
Expert 3 (Kinetics): "How water affects reaction rates..."
Expert 4 (Synthesis): "Here's the complete picture..."
Validates: "This is a real gap, high priority"
Confidence: 0.94
Output: "expert_system_hydration_coupling_validated.md"

INTEGRATION (Saturday morning):
Subconscious integrates validated expertise
Updates: Bioplastics cartridge + new facts
Creates: New specialist routing rule
Deploys: New axiom (hydration coupling)
Conscious layer now handles water better

MONDAY:
Same user: "How does water content affect..."
System: Routes through hydration specialist
Recalls: New knowledge about water-polymer coupling
Gives: Better answer than last time
User thinks: "System seems smarter"
(System IS smarter—learned from 47 corrections)
```

---

## Why This Three-Level Model Works

### No Bottlenecks

```
Conscious: Answering users (parallelizable, many users)
Subconscious: Learning from yesterday (parallelizable, overnight)
Unconscious: Deep thinking (parallelizable, different machine)

All three happen simultaneously in different processes.
User experiences responsive system, all learning happens invisible.
```

### Resilience

```
If Conscious breaks: User experience degraded, but Subconscious keeps learning
If Subconscious fails: Conscious still works, Unconscious still improving
If Unconscious fails: System keeps operating on last known good weights

Every layer can fail independently without cascading.
```

### Continuous Improvement

```
Every interaction → signal
Every signal → analyzed by Subconscious
Every analysis → validated by Unconscious
Every validated improvement → integrated by morning

System gets better every single day, automatically.
No human intervention needed (except occasional axiom review).
```

### Mimics Biological Learning

```
Biological cognition has three similar systems:
├─ Conscious: What you're thinking now
├─ Subconscious: What your brain processes during waking (habits, emotion)
├─ Unconscious: What happens during sleep (memory consolidation, optimization)

Kitbash converges on the same structure because it's solving the same problems:
├─ Speed: Need fast responses (Conscious)
├─ Learning: Need to improve (Subconscious)
├─ Deep optimization: Need to shape the system (Unconscious)
```

---

## Invisible Improvements: The Key Feature

This is not "the system learns and tells you about it."

This is "the system learns and you never know it happened—you just notice it's better."

```
Monday morning:
User: "How does water affect polymer gelling?"
System response quality: 8/10

Friday morning (after 5 nights of learning):
User: "How does water affect polymer gelling?"
System response quality: 9.5/10

User thinks: "That was a really good answer"
(Doesn't realize system learned from 47 prior corrections)

This is what autonomous improvement looks like.
No user action required.
No human curation needed (beyond occasional review).
Just: Better every day.
```

### The Constraint Problem

With 6GB VRAM limit on production machine:
- Can't run 80B model directly (requires 160GB+ for inference)
- Can't afford to wait for 80B responses (users need milliseconds)
- But you need deep reasoning for bootstrapping

### The MOE Solution

**Mixture of Experts** models (like DeepSeek, Llama 3-400B MOE variants) have:
- **Total parameters:** 80B
- **Active parameters per token:** ~10-15B (only a few experts activate)
- **Key trick:** Sparse activation = load only 1-2 experts at a time

```
Monolithic 80B Model:
└─ All 80B active always → 160GB+ VRAM needed

80B MOE Model:
├─ Expert 1 (8B): Specialized patterns
├─ Expert 2 (8B): Domain knowledge
├─ Expert 3 (8B): Logical reasoning
├─ ...
├─ Expert N: Another specialization
└─ Router (learns which expert for which problem)
   = Only 1-2 experts active at a time
   = ~10-15GB VRAM needed to run ONE expert
   = Can swap experts to disk with RAM swapping trick
```

---

## RAM Swapping Trick: Making 80B Run on Modest Hardware

### The Concept: Virtual Memory for Models

Just like OS swaps RAM to disk when full, you swap model experts to disk:

```
EXPERT LOADING CYCLE:
1. Load Expert A into VRAM (8GB)
2. Process batch on Expert A
3. Save outputs to disk
4. Unload Expert A from VRAM
5. Load Expert B into VRAM
6. Process batch on Expert B
7. Repeat until all experts evaluated

RESULT:
├─ Physical VRAM: 16GB
├─ Virtual Model: 80B (all experts)
├─ Effective speed: Tokens per minute (slow)
└─ But: No stopping, runs overnight unattended
```

### Why This Works for Sleeping Giant

**Problem:** Standard inference needs real-time speed. Sleeping Giant doesn't.

```
REAL-TIME (Production Machine):
├─ User asks question at 2:47 PM
├─ Need response in <500ms
├─ Can't afford to wait for disk I/O
└─ Use 8B model only

BATCH PROCESSING (Sleeping Giant):
├─ 50 deferred queries queued
├─ Process overnight (8 hours available)
├─ Each query gets 10-20 minutes of deep reasoning
├─ Disk I/O is fine (amortized over slow process)
├─ Each expert loaded once, processes many queries
└─ Morning: User wakes up to polished responses + learned axioms
```

**Speed tradeoff:** 1-2 tokens per second → 1-2 tokens per minute
- But Sleeping Giant isn't hurrying
- Can think deeply, revise outputs, extract patterns

---

## What the Sleeping Giant Does

### Phase 1: Deep Reasoning on Deferred Queries

During the night, the production machine defers hard queries:

```python
# Production machine, during the day:
if query_complexity > 0.7:
    # Too hard for 8B, defer to overnight
    queue_for_sleeping_giant(query, context, session_id)
    return "Thinking deeply on this overnight. You'll see response tomorrow."
```

During the night, Sleeping Giant processes the queue:

```
QUERY: "How can I optimize my bioplastics formulation for cold-temperature gelling?"

SLEEPING GIANT PROCESS (2-3 hours per query):

1. EXPERT ACTIVATION:
   ├─ Load Expert 1: Material Science (polymers, thermodynamics)
   ├─ Evaluate relevance, generate 500 tokens
   ├─ Save to: query_draft_v1.md
   
   ├─ Load Expert 2: Optimization Theory
   ├─ Evaluate relevance, generate 300 tokens
   ├─ Save to: query_draft_v2.md
   
   ├─ Load Expert 3: Chemistry & Kinetics
   ├─ Evaluate relevance, generate 400 tokens
   ├─ Save to: query_draft_v3.md
   
   └─ Load Expert 4: Novel Solutions (creative synthesis)
      ├─ Read drafts from v1, v2, v3
      ├─ Synthesize into coherent response
      └─ Save to: query_synthesis.md

2. SPECIALIST VALIDATION:
   ├─ Load all validators (can afford, running slowly)
   ├─ Check for:
   │  ├─ Factual accuracy (against Tier 6 axioms)
   │  ├─ Logical consistency
   │  ├─ Novelty (is this something the system didn't know?)
   │  └─ Confidence (how certain are we?)
   └─ Flag any hallucinations or gaps

3. AXIOM EXTRACTION:
   ├─ Analyze the reasoning chain
   ├─ Find: "This is always true" patterns
   ├─ Examples:
   │  ├─ "Cold gelling requires entropy reduction"
   │  ├─ "Entropy reduction needs external energy"
   │  └─ "External energy sources: mechanical, thermal, chemical"
   └─ Propose new axioms for Stage 4 compression

4. CARTRIDGE ENRICHMENT:
   ├─ Identify gaps in existing cartridges
   ├─ Ask: "What knowledge would have solved this faster?"
   ├─ Generate: New facts, relationships, warnings
   └─ Queue for cartridge update (human review)

5. OUTPUT POLISHING:
   ├─ Revision pass (slow, thoughtful)
   ├─ Check clarity, completeness, formatting
   ├─ Add citations to source cartridges
   ├─ Include confidence scores
   └─ Save final response to outbox
```

**Result by morning:** User sees a response that took 2-3 hours of deep 80B reasoning (via MOE experts). Fast + deep.

### Phase 2: Bootstrapping New Expert Systems

The Sleeping Giant bootstraps entire subsystems:

```
GOAL: Build an expert system for "bioplastics formulation"

SLEEPING GIANT OVERNIGHT PROCESS:

1. COLLECT SIGNALS:
   ├─ Every user correction gets saved
   ├─ Every "I didn't know that" is logged
   ├─ Every failure to route correctly is noted
   └─ Production machine accumulates these signals

2. ANALYZE PATTERNS:
   ├─ Load Expert: Pattern Recognition
   ├─ Find: "What do all the corrections have in common?"
   ├─ Cluster: 47 corrections → 5 root failure modes
   ├─ Example cluster:
   │  ├─ User corrected: "No, hydration affects gelling rate"
   │  ├─ User corrected: "Actually, pH interacts with hydration"
   │  ├─ User corrected: "Water content is critical for kinetics"
   │  └─ Pattern: System misses water-thermodynamics interactions

3. QUESTION GENERATION:
   ├─ Load Expert: Domain Knowledge
   ├─ For each failure cluster, ask:
   │  ├─ "What should we learn about X?"
   │  ├─ "What relationships are missing?"
   │  └─ "What axioms would prevent this error?"
   └─ Generate 50+ learning questions

4. DEEP REASONING:
   ├─ Load Expert: Research Synthesis
   ├─ For each learning question:
   │  ├─ Synthesize knowledge from cartridges
   │  ├─ Generate: "Here's what we should know"
   │  ├─ Include: Confidence, evidence, caveats
   │  └─ Save to: expert_system_draft.md

5. EXPERT SYSTEM EXTRACTION:
   ├─ Load Expert: Logical Formalization
   ├─ Convert narratives → rules:
   │  ├─ "Water interacts with thermodynamics"
   │  ├─ Becomes: IF (MATERIAL:HYDROPHILIC) AND (QUERY:TEMPERATURE)
   │  │             THEN increase water_routing_weight by 1.5
   │  
   │  ├─ "pH affects kinetics above 8.0"
   │  └─ Becomes: IF (pH > 8.0) THEN route_to_kinetics_specialist
   │
   └─ Generate: expert_routing_rules.txt

6. VALIDATION:
   ├─ Load Expert: Validation & Testing
   ├─ Test new rules against all logged corrections
   ├─ Measure:
   │  ├─ Did the rule correctly handle the problem?
   │  ├─ Does it over-generalize (false positives)?
   │  └─ Confidence in deployment
   └─ If confidence > 0.85: Mark for integration

7. INTEGRATION PROPOSAL:
   ├─ Queue: New facts for cartridge updates
   ├─ Queue: New axioms for Stage 4 compression
   ├─ Queue: New routing rules for Tier 5 weights
   └─ Morning report: "Proposed 12 new expert system rules, validation: 0.91"
```

**Result by morning:** New expert subsystem ready to be integrated. Production machine learns overnight without you doing anything.

---

## The Optimization Loop: Week-Long Cycles

### Daily Cycle (Overnight)

```
EVENING (User interaction):
├─ Production machine answers queries
├─ Accumulates: Corrections, failures, signals
└─ Defers hard queries → queue for Sleeping Giant

NIGHT (Sleeping Giant):
├─ Deep reasoning on deferred queries
├─ Extract axioms from reasoning chains
├─ Bootstrap new expert rules
├─ Propose cartridge updates
└─ Polish and queue responses

MORNING:
├─ User sees responses + extracted knowledge
├─ Production machine integrates validated improvements
└─ Cycle repeats
```

### Weekly Cycle (Deep Metabolism)

Every Sunday night, Sleeping Giant runs special deep phases:

```
PHASE 1: KNOWLEDGE DISTILLATION (8 hours)
├─ Analyze all week's corrections
├─ Cluster failure patterns
├─ Extract: What are we consistently wrong about?
└─ Generate: Enriched cartridge facts (human review needed)

PHASE 2: EXPERT SYSTEM GENERATION (6 hours)
├─ For each failure cluster:
│  ├─ Ask deep questions (via 80B MOE)
│  ├─ Generate rules + confidence scores
│  └─ Validate against week's data
└─ Produce: expert_system_for_[domain].txt

PHASE 3: AXIOM EXTRACTION (4 hours)
├─ Find: Patterns that appear in 50+ corrections
├─ Formalize: "This is always true because..."
├─ Test: Does axiom prevent future errors?
└─ Produce: new_axioms_validated.md

PHASE 4: WEIGHT LEARNING (6 hours)
├─ Load Stage B (fluid system)
├─ Retrain on week of accumulated signals
├─ Extract: Which Tier 3/5 weights actually matter?
└─ Produce: learned_weights_v[N].bin

PHASE 5: ROLLUP & INTEGRATION (4 hours)
├─ Review all proposals
├─ Validate improvements
├─ Merge into production system
└─ Produce: integration_report.md

TOTAL: ~28 hours deep optimization
RESULT: System is noticeably better next Monday
```

---

## Why This Is Powerful

### Speed + Depth

```
PRODUCTION (8B Model, milliseconds):
├─ Fast routing and retrieval
├─ Good-enough answers for most queries
├─ Gathers signals
└─ Defers hard problems

SLEEPING GIANT (80B MOE, tokens per minute):
├─ Deep reasoning on hard problems
├─ Extracts patterns and axioms
├─ Bootstraps expert systems
├─ Improves routing rules
└─ Makes production system smarter over time

RESULT: Fast for users + keeps improving without manual effort
```

### Expert System Bootstrap (The Key Insight)

**Traditional approach to expert systems:**
1. Expert spends weeks formalizing rules
2. Rules get encoded manually
3. System uses rules

**Kitbash's approach:**
1. Production system collects signals (user corrections)
2. Sleeping Giant analyzes signals overnight
3. Sleeping Giant proposes expert system rules
4. Human reviews and integrates
5. Production system uses new rules
6. Back to step 1 (system improves)

**The trick:** Sleeping Giant learns the domain structure *from corrections*, not from scratch. Users implicitly teach the system by correcting it.

---

## The Queue System

### What Gets Deferred?

Production machine decides in real-time:

```python
def should_defer_to_sleeping_giant(query, context, vram):
    """Decide: answer now or think deeply overnight?"""
    
    # Defer if:
    complexity = compute_complexity(query)
    if complexity > 0.8:
        return True, "Too complex for fast inference"
    
    # Defer if we're running low on VRAM
    if vram > 5500:  # Approaching limit
        return True, "VRAM pressure, defer for batching"
    
    # Defer if query is novel (haven't answered similar before)
    similarity = find_most_similar_past_query(query)
    if similarity.confidence < 0.6:
        return True, "Novel question, needs deep reasoning"
    
    # Defer if user explicitly asks for depth
    if "think about this" in query.lower():
        return True, "User requested deep thinking"
    
    # Otherwise, answer now
    return False, "Simple query, answer in real-time"
```

### Queue Format

```
outbox/deferred_queries.jsonl:
{
  "query_id": "q_20260210_001",
  "session_id": "user_session_xyz",
  "query": "How can I optimize...",
  "context": [previous messages],
  "complexity": 0.85,
  "reason_deferred": "Complex multi-domain synthesis",
  "timestamp": "2026-02-10T15:30:00Z",
  "priority": "high"  # Relative to other deferred queries
}

deferred_queries_20260210.jsonl
deferred_queries_20260211.jsonl
deferred_queries_20260212.jsonl
[accumulated overnight batch]
```

### Response Queue (Output)

```
outbox/responses_ready_20260211.jsonl:
{
  "query_id": "q_20260210_001",
  "session_id": "user_session_xyz",
  "response": "Detailed response after 2 hours of thinking...",
  "reasoning_chain": [expert1_output, expert2_output, ...],
  "confidence": 0.92,
  "axioms_extracted": ["new_axiom_1", "new_axiom_2"],
  "cartridge_suggestions": ["expand water_thermodynamics"],
  "timestamp_completed": "2026-02-11T03:45:00Z"
}

[User wakes up to polished responses]
```

---

## Integration with Production System

### Morning Integration

When production system starts:

```python
def morning_startup():
    """Integrate overnight learning"""
    
    # Load new axioms (Stage 4)
    new_axioms = load_file("outputs/new_axioms_validated.md")
    tier6.integrate_axioms(new_axioms)
    
    # Load new routing rules (Tier 5)
    new_rules = load_file("outputs/expert_system_for_[domain].txt")
    tier5_rules.integrate_rules(new_rules)
    
    # Load weight updates (from Stage B learning)
    new_weights = load_file("outputs/learned_weights_v[N].bin")
    tier3_routing.update_weights(new_weights)
    
    # Prepare ready responses for users
    ready_responses = load_file("outputs/responses_ready_[date].jsonl")
    for response in ready_responses:
        notify_user(response.session_id, "Your response is ready")
    
    # Start fresh: empty deferred queue, start collecting new signals
    start_new_day()
```

### Continuous Learning

Each interaction creates data for Sleeping Giant:

```
User correction: "No, it's 14:47 UTC not EST"
  ↓
Production machine logs to: signals/corrections_[date].jsonl
  ↓
Tonight, Sleeping Giant:
  ├─ Reads all daily corrections
  ├─ Finds pattern: "Timezone confusion"
  ├─ Proposes: Axiom "Always include UTC offset when discussing time"
  ├─ Proposes: Tier 5 rule "Timezone topics → chronos specialist"
  └─ Tests on all historical corrections
  ↓
Morning: Integration proposal with confidence 0.89
```

---

## Hardware Requirements

### Production Machine
- GTX 1060 (6GB VRAM)
- 16GB+ system RAM
- CPU: Modern (Ryzen 5 or better)
- Running: Hermes-3-8B via KoboldCpp
- Timescale: Real-time, responsive

### Sleeping Giant Machine
- Can be slower/older hardware (doesn't matter for overnight)
- GPU: RTX 3060 Ti (8GB) or better recommended (for MOE expert loading)
- Or: CPU-only with 32GB+ RAM (slower but works)
- System RAM: 32GB+ (for disk swapping buffer)
- Storage: Fast NVMe for swap (minimize I/O latency)
- Running: 80B MOE model with sparse expert activation
- Timescale: Overnight batch processing

---

## Performance Expectations

### Sleeping Giant Throughput

**80B MOE on modest GPU (RTX 3060 Ti):**
```
Per expert activation:
├─ Load expert (8-10GB model): 2-5 minutes
├─ Process batch (100 tokens): 30-60 seconds
├─ Write outputs: 10-20 seconds
└─ Unload expert: 1-2 minutes

Per query (using 4 experts):
├─ Total time: 25-35 minutes
├─ Tokens generated: 2000-4000
├─ Speed: ~2-4 tokens per minute (when amortized over load times)
```

**Per night (8 hours):**
```
Available: 480 minutes
Overhead: ~10% (disk I/O, system management)
Useful: 432 minutes

Can process:
├─ 12-18 complex queries deeply (25-35 min each)
├─ Plus: Weekly metabolism phases
├─ Plus: Continuous expert system bootstrapping
└─ Plus: Axiom extraction and refinement
```

---

## The Vision: Self-Improving System Through Three Levels

### The Invisible Cycle

```
DAY 1 - CONSCIOUS LAYER:
├─ User interaction: "How do I...?"
├─ System answers
├─ User provides corrections (signals)
└─ Conscious layer doesn't know anything happened

NIGHT 1 - SUBCONSCIOUS LAYER:
├─ Reads all daily signals
├─ Analyzes: What patterns are emerging?
├─ Proposes: New axioms, better weights
├─ Queues: Candidates for validation

NIGHT 1 - UNCONSCIOUS LAYER:
├─ Validates subconscious proposals
├─ Deep reasoning: Are these axioms right?
├─ Produces: Validated improvements
└─ Feeds back to subconscious

MORNING - INTEGRATION:
├─ Subconscious integrates validated improvements
├─ Conscious wakes up with better weights/axioms/rules
├─ Conscious has no idea what happened
└─ System just works better

DAY 2 - CONSCIOUS LAYER:
├─ Same type of question as Day 1
├─ But now system has learned
├─ User gets better answer
├─ Thinks: "This system is smart"
└─ Unconscious: Repeats
```

### Over Time: Exponential Improvement

```
WEEK 1:
├─ CONSCIOUS: Daily interactions, raw learning
├─ SUBCONSCIOUS: 7 nights of pattern extraction
├─ UNCONSCIOUS: 7 nights of deep validation
└─ RESULT: Noticeably smarter system

WEEK 2:
├─ CONSCIOUS: Better system, but more queries reaching the boundary
├─ SUBCONSCIOUS: 7 more nights, discovering deeper patterns
├─ UNCONSCIOUS: Validating more sophisticated axioms
└─ RESULT: System is solving novel problems

WEEK 3:
├─ CONSCIOUS: Expert rules kicking in, fewer failures
├─ SUBCONSCIOUS: Bootstrapping first complete expert system (e.g., hydration coupling)
├─ UNCONSCIOUS: Deep reasoning on domain structure
└─ RESULT: System has genuine expertise in a domain

MONTH 1:
├─ CONSCIOUS: Handles 80% of queries perfectly
├─ SUBCONSCIOUS: 30 nights of accumulated learning
├─ UNCONSCIOUS: 30 nights of continuous optimization
├─ Axioms: 50 → 150
├─ Expert systems: 0 → 3-4 complete domains
├─ Routing efficiency: +40%
└─ RESULT: System is significantly different

MONTH 3:
├─ CONSCIOUS: Handles 90%+ of queries correctly
├─ SUBCONSCIOUS: Metamorphosed from learning to maintenance
├─ UNCONSCIOUS: Refining edges, optimizing deep structure
├─ Axioms: 150 → 500+
├─ Expert systems: 3-4 → 15+ domains
├─ Routing efficiency: +70%
└─ RESULT: System has become an expert system framework

YEAR 1:
├─ CONSCIOUS: Mostly delegation (routes to right specialist)
├─ SUBCONSCIOUS: Maintenance + incremental improvement
├─ UNCONSCIOUS: Continuous research and validation
├─ Axioms: 500+ (stable, rarely changes)
├─ Expert systems: 30+ domain expertise networks
├─ System: Behaves like a genuinely knowledgeable agent
└─ RESULT: Self-constructed expert system (no manual rule-building)
```

The user never sees the system being built. They just see it getting smarter.

---

## Critical Design Principles

### 1. Sleeping Giant Never Blocks Users

```
Production: Always responsive (<500ms)
Sleeping Giant: Slow, background, asynchronous
Interface: Simple queue system (no real-time sync needed)
Failure mode: If Sleeping Giant fails, production still works
```

### 2. All Improvements Are Validated

```
Sleeping Giant proposes: New axioms, rules, weights
Human review: Always required (or at least confidence threshold)
Integration: Staged rollout (don't dump all changes at once)
Rollback: Easy (previous state always available)
```

### 3. Signals Flow One Direction (For Now)

```
Production → Signals → Sleeping Giant → Improvements → Production
         (user interactions, corrections, failures)
```

(Eventually: Sleeping Giant could request specific data from Production, but start simple)

### 4. Everything Is Logged and Auditable

```
Sleeping Giant produces: Reasoning chains, rule justifications, confidence scores
Preserved: All analysis (can review why improvements were made)
Traceable: Every axiom back to the signals that generated it
```

---

## Implementation Roadmap

**Week 1-2:** Basic queue system (defer simple queries to file)
**Week 3-4:** Sleeping Giant stub (read queue, generate responses)
**Week 5-6:** MOE model integration + expert activation loop
**Week 7-8:** Axiom extraction from reasoning chains
**Week 9-10:** Expert system bootstrapping + rule generation
**Week 11-12:** Integration framework (morning startup merging)

By Week 12: Fully autonomous self-improving system running overnight every night.

---

## The Three Levels of Consciousness in One Sentence

**A fast conscious layer answers your questions in real-time, a sleeping subconscious layer learns from your corrections each night, and a tireless unconscious layer validates those lessons on a separate machine—all without you noticing the system got smarter.**

That's the magic: Speed for the user, depth for the system, learning invisible to both.

---

## Mapping to Human Cognition

```
HUMAN COGNITION:
├─ Conscious: What you're thinking right now (milliseconds)
├─ Subconscious: What your brain processes without you realizing (thoughts, habits)
├─ Unconscious: What happens during sleep (memory consolidation, optimization)
└─ Result: You wake up smarter, changed, improved—without effort

KITBASH COGNITION:
├─ Conscious: What the system is responding to users with (milliseconds)
├─ Subconscious: What metabolism processes each night (learning, weight updates)
├─ Unconscious: What 80B MOE does on separate machine (deep reasoning, axiom validation)
└─ Result: System wakes up smarter, with new expertise—without manual intervention
```

The convergence isn't accidental. Both systems solve the same fundamental problem:
**"How do you get fast response + deep learning without sacrificing either?"**

The answer is three layers of consciousness, each operating at its own speed, invisible to the layers above.

---

## The Critical Insight

Most AI systems treat learning and inference as conflicting processes:
- Learning requires deep thought (slow)
- Inference requires fast response (shallow)
- You have to choose

Kitbash doesn't choose. It does both simultaneously:
- **Conscious** (inference): Fast responses to users
- **Subconscious** (learning): Overnight improvement from user interactions
- **Unconscious** (deep optimization): Continuous validation and refinement

The user gets a fast, responsive system.
The system gets to learn deeply every night.
Neither interferes with the other.

That's the entire architecture in a nutshell.

