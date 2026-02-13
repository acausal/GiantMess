# Kitbash Consensus vs. Escalation Decision Logic
**Exploring the Low-Confidence Branching Problem**

---

## The Question

When Layer 1 (bitnet) returns a result with confidence 0.72 (too low for direct return, too high to ignore):

**Option A: Escalate Immediately**
- Send to Layer 4 (kobold LLM)
- Single authoritative answer
- Serial execution
- Slower but decisive

**Option B: Get Consensus First**
- Spawn Layer 2/3 (cartridge synthesis) in parallel with Layer 4
- Average results
- Faster (potential parallel computation)
- More confident answer if they agree

**Option C: Query-Dependent Heuristics**
- Simple queries (low entropy) → escalate
- Complex queries (high entropy) → consensus
- Tuned based on historical data

Each has different costs/benefits, and the choice shapes your entire async architecture.

---

## Analysis: Three Scenarios

### Scenario 1: Domain Question (Simple)

**Query:** "What is ATP?"

**Layer 0:** No grain hit (not reflexive)
**Layer 1 (bitnet):** "ATP is adenosine triphosphate, energy molecule. Confidence: 0.82"

**Decision Point:**
- Confidence 0.82 is decent, but not great
- Query is simple (single fact, no synthesis needed)
- Answer is factual, verifiable

**Consensus approach:** Spawn Layer 2 (cartridge synthesis) to double-check? Probably wastes time. This query has a clear answer.

**Escalation approach:** Hand off to kobold anyway? Overkill for a simple factual query.

**Better approach:** For simple queries, confidence 0.80+ is probably fine. Don't get consensus, but don't escalate immediately either—*check if bitnet's answer matches a high-confidence cartridge fact*.

```python
if bitnet_result['confidence'] > 0.80:
    # Check if answer is in cartridges
    cartridge_facts = quick_cartridge_lookup(query)
    if cartridge_facts and bitnet_answer in cartridge_facts:
        return bitnet_result  # Confirmed, no consensus needed
    else:
        # Bitnet disagrees with cartridges, get full consensus
        escalate_to_consensus_vote([bitnet, cartridge, kobold])
```

---

### Scenario 2: Synthesis Question (Complex)

**Query:** "Combine physics and biochemistry to explain how ATP synthase works at a molecular level."

**Layer 0:** No grain hit (complex synthesis)
**Layer 1 (bitnet):** "ATP synthase is a protein complex... uses proton gradient... Confidence: 0.68"

**Decision Point:**
- Confidence 0.68 is borderline
- Query is complex (requires synthesis across domains)
- Answer is inferential (not a single fact)

**Escalation approach:** Send to kobold. It has broader context, better at synthesis. But it's slow (500ms).

**Consensus approach:** Spawn Layer 2 (cartridge synthesis—grab physics + biochemistry facts, combine them) in parallel with Layer 4. Wait 500ms max:
- If cartridge synthesis finishes first (say 200ms), you have: bitnet (0.68) + cartridge (0.75) = average 0.72, safe to return
- If cartridge doesn't finish in time, fall back to kobold

**Better approach:** For complex queries, *always* get consensus if Layer 1 is borderline. Cartridge synthesis is faster than kobold, and two opinions are better than one guess.

```python
if is_complex_query(query) and bitnet_result['confidence'] < 0.85:
    # Spawn cartridge synthesis + kobold in parallel
    results = await asyncio.gather(
        get_cartridge_synthesis(query_id, timeout=500),
        get_kobold_result(query_id, timeout=5000),
        return_exceptions=True
    )
    
    valid_results = [r for r in results if r and not isinstance(r, Exception)]
    return consensus(valid_results)
```

---

### Scenario 3: Ambiguous/Multi-Answer Question

**Query:** "What are the best ways to debug memory leaks?"

**Layer 0:** No grain hit
**Layer 1 (bitnet):** "Use valgrind, gdb, AddressSanitizer... Confidence: 0.74"

**Decision Point:**
- Confidence 0.74 (low-to-medium)
- Query is open-ended (multiple valid answers)
- Different tools are correct for different contexts

**Escalation approach:** Send to kobold. It's better at open-ended reasoning. But is kobold's answer better than bitnet's? Not guaranteed.

**Consensus approach:** Get both answers. They'll likely list different tools. Average them? Or ask the user which they prefer?

**Better approach:** For open-ended questions with low confidence, *escalate to LLM but flag it as synthesized opinion, not fact*. Consensus voting doesn't help with subjective answers.

```python
if is_open_ended_query(query) and bitnet_result['confidence'] < 0.80:
    # Escalate to kobold, mark as opinion
    kobold_result = await get_kobold_result(query_id, timeout=5000)
    return {
        **kobold_result,
        "confidence": kobold_result['confidence'] * 0.9,  # Discount slightly
        "answer_type": "synthesized_opinion",
        "note": "Multiple valid answers; this is one perspective"
    }
```

---

## Decision Framework: Three Strategies

### Strategy A: Pure Escalation (Simplest)

```
Layer 0 hits → return
Layer 0 misses → Layer 1
  Layer 1 high conf (>0.85) → return
  Layer 1 low conf (<0.85) → Layer 4 (kobold)
    Layer 4 → return
```

**Pros:**
- Simple to implement (no consensus logic)
- Single authoritative source per query
- Predictable latency

**Cons:**
- Wastes Layer 1 results when confidence is borderline
- Falls back to expensive LLM too often
- Doesn't leverage parallelism

---

### Strategy B: Always Consensus (Maximum Confidence)

```
Layer 0 hits → return
Layer 0 misses → Layer 1 + Layer 2 (parallel)
  Wait up to 500ms for both
    High consensus (both >0.80, agree) → return
    Low consensus (disagree or both <0.80) → Layer 4
      Layer 4 breaks tie → return
```

**Pros:**
- Multiple opinions → higher confidence
- Catches cases where Layer 1 is wrong
- Parallelizable (Layer 1 and Layer 2 run simultaneously)

**Cons:**
- Always pays Layer 1 latency (even for simple queries)
- More complex orchestration
- Harder to tune consensus thresholds

---

### Strategy C: Query-Aware Heuristics (Balanced)

```
Layer 0 hits → return
Layer 0 misses → Layer 1
  If simple query AND high conf (>0.80) → return
  If simple query AND medium conf (0.70-0.80) → quick cartridge check
    Matches → return
    Disagrees → full consensus (Layer 2 + 4)
  
  If complex query AND any conf (<0.95) → parallel consensus (Layer 2 + 4)
    Reach consensus → return
    Can't agree → Layer 4 (LLM tiebreaker)
  
  If open-ended query AND low conf (<0.80) → escalate to Layer 4
```

**Pros:**
- Tuned to query characteristics
- Avoids consensus for trivial questions
- Still parallelizes complex queries
- Can be optimized iteratively with real data

**Cons:**
- More code (query classification logic)
- Harder to predict latency
- Requires historical data to tune thresholds

---

## My Recommendation (For Phase 3B)

**Start with Strategy A (Pure Escalation), collect data, graduate to C:**

**Reasoning:**
1. **Simple to implement** - Focus on getting the Redis orchestration working
2. **Tells you what you need** - After 1000 queries, you'll know:
   - How often Layer 1 confidence is borderline
   - How much slower Layer 4 is compared to Layer 1+2
   - Which queries would benefit from consensus
3. **Easy to optimize later** - Add consensus logic once you have data

**Phase 3B Implementation:**
```python
def route_query_serial(query_id: str, user_query: str):
    # Layer 0
    l0_result = layer0_grain_lookup(user_query)
    if l0_result['confidence'] > 0.85:
        return l0_result
    
    # Layer 1
    l1_result = await get_bitnet_result(query_id, timeout=2000)
    if not l1_result:
        # Timeout, escalate
        pass
    elif l1_result['confidence'] > 0.85:
        return l1_result
    
    # Escalate to Layer 4
    l4_result = await get_kobold_result(query_id, timeout=5000)
    return l4_result
```

**Phase 4 Evolution (with data):**
```python
def route_query_smart(query_id: str, user_query: str):
    # Same Layer 0, 1...
    
    if l1_result['confidence'] > 0.85:
        return l1_result
    
    # Now use data from Phase 3B to decide:
    # "Queries like this benefited from consensus 70% of the time"
    if should_get_consensus(user_query, l1_result):
        # Spawn Layer 2 + 4 in parallel, take consensus
        l2, l4 = await asyncio.gather(
            get_cartridge_synthesis(query_id),
            get_kobold_result(query_id)
        )
        return consensus([l1_result, l2, l4])
    else:
        # Simple query, escalate directly
        l4 = await get_kobold_result(query_id)
        return l4
```

---

## Decision: What You Specify Now

For Phase 3B, I need you to decide:

**Question 1: Consensus Scope**
When you DO consensus (once implemented), what engines participate?
- Option A: Layer 1 (bitnet) + Layer 4 (kobold) only?
- Option B: Layer 1 + Layer 2 (cartridge) + Layer 4?
- Option C: All available engines that can answer?

*Recommendation: B. Cartridge is fast and evidence-based. Good middle ground.*

**Question 2: Confidence Thresholds (Provisional)**
For Phase 3B (pure escalation), what's "high enough"?
- Layer 0: Return if confidence > ?
- Layer 1: Return if confidence > ?
- Layer 4: Always return (it's last resort)

*My suggestion: 0.85 for Layer 0, 0.80 for Layer 1. Adjust with data.*

**Question 3: Open-Ended Detection**
Should system classify queries as:
- Factual (specific answer exists)
- Synthesized (combine multiple ideas)
- Open-ended (multiple valid answers)

And handle each differently?

*My suggestion: Implement simple heuristic (keyword matching) for Phase 3B, refine with Phase 4 data.*

---

## Implementation Roadmap for Consensus Logic

### Phase 3B: No Consensus Yet
- Implement pure escalation (Strategy A)
- Log Layer 1 confidence distribution
- Measure Layer 4 latency

### Phase 3C: Add Parallel Layer 4
- Layer 1 + Layer 4 run in parallel (not sequential)
- Still no consensus voting, but measure timing
- Understand whether Layer 2 (cartridge synthesis) is worth adding

### Phase 4: Add Consensus Logic
- Based on Phase 3 data, implement Strategy C (query-aware heuristics)
- Layer 1 + Layer 2 + Layer 4 in parallel for complex queries
- Simple queries escalate immediately

---

## Testing Strategy for Consensus (Phase 4+)

```python
def test_consensus_voting():
    """Test that consensus picks best answer."""
    
    results = [
        {"answer": "ATP is energy", "confidence": 0.72, "engine": "bitnet"},
        {"answer": "ATP transfers energy", "confidence": 0.78, "engine": "cartridge"},
        {"answer": "Adenosine triphosphate provides cellular energy", "confidence": 0.91, "engine": "kobold"},
    ]
    
    final = consensus(results)
    
    assert final['confidence'] > 0.80  # Average of 3
    assert final['answer'] == "Adenosine triphosphate provides cellular energy"  # Longest/most detailed
    assert set(final['sources']) == {"bitnet", "cartridge", "kobold"}

def test_consensus_disagreement():
    """What happens when engines give different answers?"""
    
    results = [
        {"answer": "Valgrind", "confidence": 0.70, "engine": "bitnet"},
        {"answer": "GDB with memory debugging", "confidence": 0.68, "engine": "cartridge"},
        {"answer": "AddressSanitizer is recommended", "confidence": 0.65, "engine": "kobold"},
    ]
    
    final = consensus(results)
    
    # Probably should escalate further or flag as uncertain
    assert final['confidence'] < 0.70
    assert final.get('answer_type') == 'uncertain'
```

---

## Summary: What to Implement Phase 3B

1. **Pure Escalation Loop** (Strategy A)
   - Layer 0 → Layer 1 → Layer 4
   - No consensus yet
   - Baseline latency measurement

2. **Confidence Thresholds**
   - Layer 0: 0.85 (high bar for reflex answers)
   - Layer 1: 0.80 (accept bitnet if reasonably confident)
   - Layer 4: always (last resort)

3. **Diagnostic Logging**
   - Record every layer decision
   - Log confidence values
   - Measure latency per layer

4. **Redis Schema** (already in other doc)
   - Query state tracking
   - Result storage
   - Metrics aggregation

**After Phase 3B Data (Phase 4):**
- Implement consensus voting
- Query classification (simple vs. complex vs. open-ended)
- Strategy C (query-aware heuristics)

---

## Open Questions for You

1. **Confidence scoring:** How should consensus voting work?
   - Simple average? `(0.72 + 0.78 + 0.91) / 3 = 0.80`?
   - Weighted by engine reliability? (Kobold weighted higher because it's usually right)?
   - Voting system? (Majority answer wins, confidence is % of agreement)?

2. **Answer selection:** When engines give different answers, which wins?
   - Longest/most detailed? (Usually better answers are more specific)
   - Highest individual confidence?
   - Majority vote (most engines said X)?
   - Something else?

3. **Consensus threshold:** How confident must consensus be to return vs. escalate further?
   - If average is 0.75, return or escalate again?
   - If 2/3 engines agree, good enough?

These aren't blocking—you can code Strategy A now and decide these during Phase 4. But it's worth thinking about the data model now (how to store "engine A said X with confidence Y").
