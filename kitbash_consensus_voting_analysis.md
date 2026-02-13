# Consensus Voting: Simple vs. Weighted Average
**Implementation Cost vs. Migration Complexity Analysis**

---

## The Core Question

When you have three engines' answers:
- **Bitnet:** "ATP is energy molecule" (confidence 0.72)
- **Cartridge:** "ATP transfers phosphate bonds" (confidence 0.78)
- **Kobold:** "Adenosine triphosphate provides cellular energy currency" (confidence 0.91)

**Simple Average:** `(0.72 + 0.78 + 0.91) / 3 = 0.80`

**Weighted Average:** `(0.72×w1 + 0.78×w2 + 0.91×w3) / (w1 + w2 + w3)`

Where `w1, w2, w3` are learned weights (e.g., `w1=0.8, w2=0.9, w3=0.95` based on historical accuracy).

---

## Strategy 1: Simple Average

### Implementation (Phase 3B)

```python
def consensus_simple(results: List[Dict]) -> Dict:
    """Average confidence, pick most detailed answer."""
    
    confidences = [r['confidence'] for r in results]
    avg_confidence = sum(confidences) / len(confidences)
    
    # Pick longest answer (usually most detailed = best)
    best_result = max(results, key=lambda r: len(r['answer']))
    
    return {
        "answer": best_result['answer'],
        "confidence": avg_confidence,
        "method": "simple_average",
        "sources": [r['engine'] for r in results],
        "individual_confidences": {r['engine']: r['confidence'] for r in results},
        "avg_confidence": avg_confidence
    }
```

**Time to implement:** 15 minutes

### Pros

1. **Zero tuning required** - Works immediately, no historical data needed
2. **Interpretable** - Easy to understand and explain why an answer got 0.80 confidence
3. **Fair** - Treats all engines equally (good for early phase when you don't know which is better)
4. **Easy to debug** - Can see individual engine confidences clearly
5. **Migrates trivially** - Switching to weighted is a small code change (add weight lookup)

### Cons

1. **Doesn't learn from data** - If Kobold is right 95% and Bitnet 70%, still treating equally
2. **Assumes equal capability** - Wrong! Kobold handles synthesis, Bitnet is pattern matcher
3. **Penalizes high-confidence engines** - If Kobold returns 0.95 and Bitnet 0.60, average is 0.775 (worse than Kobold alone)
4. **No specialization signal** - Can't route "synthesis queries" preferentially to Cartridge

### Migration Cost to Weighted (Later)

**Low.** Just add a weights table to Redis:

```python
# Add to Redis at startup
redis.hset("model:weights", mapping={
    "bitnet": 0.80,
    "cartridge": 0.90,
    "kobold": 0.95
})

# Minimal code change
def consensus_weighted(results: List[Dict]) -> Dict:
    weights = redis.hgetall("model:weights")
    
    weighted_conf = sum(
        r['confidence'] * float(weights.get(r['engine'], 1.0))
        for r in results
    ) / sum(float(weights.get(r['engine'], 1.0)) for r in results)
    
    return {..., "confidence": weighted_conf, "method": "weighted_average"}
```

**Migration effort:** 30 minutes (mostly testing)

---

## Strategy 2: Weighted Average

### Implementation (Phase 3B)

```python
def consensus_weighted(results: List[Dict]) -> Dict:
    """Weighted average using per-engine reliability weights."""
    
    # Load weights from Redis (updated by metabolism cycle)
    weights = redis.hgetall("model:weights")
    
    # Default weight if not set
    default_weight = 1.0
    
    weighted_conf_sum = 0
    weight_sum = 0
    
    for result in results:
        engine = result['engine']
        confidence = result['confidence']
        weight = float(weights.get(engine, default_weight))
        
        weighted_conf_sum += confidence * weight
        weight_sum += weight
    
    avg_confidence = weighted_conf_sum / weight_sum if weight_sum > 0 else 0.5
    
    # Still pick longest answer (content quality independent of engine)
    best_result = max(results, key=lambda r: len(r['answer']))
    
    return {
        "answer": best_result['answer'],
        "confidence": avg_confidence,
        "method": "weighted_average",
        "sources": [r['engine'] for r in results],
        "individual_confidences": {r['engine']: r['confidence'] for r in results},
        "weights_applied": {r['engine']: float(weights.get(r['engine'], default_weight)) for r in results},
        "avg_confidence": avg_confidence
    }

# Weights are learned from query logs (Phase 4+)
def update_weights_from_feedback(feedback_log: List[Dict]):
    """
    When a user confirms an answer is correct, update the engine's weight.
    E.g., Kobold was right 950/1000 times → weight 0.95
    """
    
    engine_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    
    for feedback in feedback_log:
        if feedback.get('correct'):
            engine_stats[feedback['engine']]['correct'] += 1
        engine_stats[feedback['engine']]['total'] += 1
    
    new_weights = {}
    for engine, stats in engine_stats.items():
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0.5
        new_weights[engine] = accuracy
    
    # Store in Redis
    redis.hset("model:weights", mapping=new_weights)
```

**Time to implement:** 30 minutes (mostly the weight lookup logic)

### Pros

1. **Learns over time** - Weights improve as you get feedback
2. **Specialization aware** - Can weight Cartridge higher for factual queries, Kobold for synthesis
3. **Handles degradation** - If Bitnet breaks (crashes, low accuracy), automatically downweights
4. **No human tuning** - Weights self-calibrate from real feedback
5. **Flexible** - Can have per-query-type weights (weights for "factual" vs "synthesis" vs "open-ended")

### Cons

1. **Requires feedback data** - Need 50+ queries per engine to learn good weights
2. **Cold start problem** - First 100 queries run at equal weights until you have data
3. **Feedback dependency** - Weights only improve if users confirm answers
4. **Complexity** - More moving parts, harder to debug ("why did confidence drop to 0.73?")
5. **Potential instability** - If one engine crashes, weights might oscillate
6. **Storage overhead** - Need to track per-engine accuracy over time

### Migration Cost from Simple (Backward Compat)

**Medium.** You need to:
1. Initialize weights to 1.0 for all engines (neutral, same as simple)
2. Add feedback loop to update weights (separate system)
3. Gradually introduce weighting as feedback arrives

**Migration effort:** 2-3 hours (mostly feedback infrastructure)

---

## Strategy 3: Weighted + Per-Query-Type

### Implementation (Phase 4+)

```python
def consensus_intelligent(results: List[Dict], query_type: str) -> Dict:
    """
    Use different weights based on query classification.
    E.g., factual queries trust Cartridge more, synthesis queries trust Kobold more.
    """
    
    # Classify query once (in orchestrator)
    # query_type = "factual" | "synthesis" | "open_ended"
    
    weights = redis.hgetall(f"model:weights:{query_type}")
    
    # ... same weighted average logic as Strategy 2 ...
```

**Cost to implement from Strategy 2:** 2-3 hours (query classification + per-type weight storage)

### Pros
- Most accurate (engines are good at different things)
- Self-tuning (learns what works best per scenario)
- Best long-term performance

### Cons
- Requires query classification (adds latency, complexity)
- Need more feedback data (50+ per engine × 3 query types = 450 queries)
- Hardest to debug

---

## Decision Matrix: What to Choose Now

| Factor | Simple | Weighted | Weighted+Typed |
|--------|--------|----------|----------------|
| **Phase 3B Complexity** | 15 min | 30 min | Not yet |
| **Dependency on Data** | None | Feedback needed | More feedback needed |
| **Cold Start (0 data)** | Works great | Works (equal weight) | Works (equal weight) |
| **Learns Over Time** | No | Yes | Yes |
| **Accuracy (100+ queries)** | ~0.80 | ~0.82-0.85 | ~0.85-0.88 |
| **Debuggability** | High | Medium | Low |
| **Migration Cost** | N/A | Low (30 min) | Medium (2-3 hr) |

---

## My Recommendation: Hybrid Approach

**Phase 3B:** Implement **Simple Average**
- Zero tuning friction
- Works immediately
- Get 1000+ queries of baseline data
- Analyze which engines are actually accurate

**Phase 4 (with data):** Add **Weighted Average**
- Use feedback from Phase 3B to initialize weights
- Gradually improve over time
- Still simple, but data-driven

**Phase 5+ (optional):** Add **Per-Query-Type**
- Only if weighted average isn't delivering 0.85+ confidence
- If you find "synthesis queries need Cartridge higher", implement it
- Otherwise, weighted alone is good enough

**Why this works:**
- You don't commit to complex infrastructure before you have data
- Migration path is smooth (Simple → Weighted → Typed)
- Feedback loop is in place for Weighted but optional for Simple
- You can measure if each upgrade actually helps

---

## Implementation for Phase 3B (Simple + Hooks for Weighted)

```python
# consensus.py

from typing import List, Dict, Optional
import redis

redis_client = redis.Redis(host='localhost', port=6379)

class ConsensusEngine:
    """Voting logic for multi-engine consensus."""
    
    def __init__(self, strategy: str = "simple"):
        """
        strategy: "simple" | "weighted" | "weighted_typed"
        """
        self.strategy = strategy
    
    def vote(self, results: List[Dict], query_type: Optional[str] = None) -> Dict:
        """
        Combine multiple engine results into consensus answer.
        
        Args:
            results: List of {engine, answer, confidence, ...}
            query_type: Optional classification (for weighted_typed)
        
        Returns:
            Consensus result with final answer and confidence
        """
        
        if not results:
            return {
                "answer": "No results available",
                "confidence": 0.0,
                "method": "error",
                "sources": []
            }
        
        if self.strategy == "simple":
            return self._vote_simple(results)
        elif self.strategy == "weighted":
            return self._vote_weighted(results)
        elif self.strategy == "weighted_typed":
            return self._vote_weighted_typed(results, query_type)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def _vote_simple(self, results: List[Dict]) -> Dict:
        """Simple average: all engines weighted equally."""
        
        confidences = [r['confidence'] for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Pick longest answer (usually most detailed)
        best_result = max(results, key=lambda r: len(r.get('answer', '')))
        
        return {
            "answer": best_result['answer'],
            "confidence": avg_confidence,
            "method": "simple_average",
            "sources": [r['engine'] for r in results],
            "individual_confidences": {r['engine']: r['confidence'] for r in results},
        }
    
    def _vote_weighted(self, results: List[Dict]) -> Dict:
        """Weighted average: engine accuracy from feedback."""
        
        # Load weights from Redis (default 1.0 if not set)
        weights = {}
        for result in results:
            engine = result['engine']
            weight = redis_client.hget("model:weights", engine)
            weights[engine] = float(weight) if weight else 1.0
        
        # Weighted average confidence
        weighted_conf_sum = sum(
            r['confidence'] * weights[r['engine']]
            for r in results
        )
        weight_sum = sum(weights[r['engine']] for r in results)
        avg_confidence = weighted_conf_sum / weight_sum if weight_sum > 0 else 0.5
        
        # Still pick longest answer
        best_result = max(results, key=lambda r: len(r.get('answer', '')))
        
        return {
            "answer": best_result['answer'],
            "confidence": avg_confidence,
            "method": "weighted_average",
            "sources": [r['engine'] for r in results],
            "individual_confidences": {r['engine']: r['confidence'] for r in results},
            "weights_applied": weights,
        }
    
    def _vote_weighted_typed(self, results: List[Dict], query_type: str) -> Dict:
        """Weighted average per query type (Phase 4+)."""
        
        if not query_type:
            # Fall back to untyped weighted
            return self._vote_weighted(results)
        
        # Load query-type-specific weights
        weights = {}
        for result in results:
            engine = result['engine']
            weight = redis_client.hget(f"model:weights:{query_type}", engine)
            weights[engine] = float(weight) if weight else 1.0
        
        # ... same weighted logic ...
        weighted_conf_sum = sum(
            r['confidence'] * weights[r['engine']]
            for r in results
        )
        weight_sum = sum(weights[r['engine']] for r in results)
        avg_confidence = weighted_conf_sum / weight_sum if weight_sum > 0 else 0.5
        
        best_result = max(results, key=lambda r: len(r.get('answer', '')))
        
        return {
            "answer": best_result['answer'],
            "confidence": avg_confidence,
            "method": "weighted_average_typed",
            "query_type": query_type,
            "sources": [r['engine'] for r in results],
            "individual_confidences": {r['engine']: r['confidence'] for r in results},
            "weights_applied": weights,
        }

# Usage:

# Phase 3B: Simple voting
engine = ConsensusEngine(strategy="simple")
final = engine.vote([bitnet_result, cartridge_result, kobold_result])

# Phase 4: Switch to weighted (no other code changes)
engine = ConsensusEngine(strategy="weighted")
final = engine.vote([bitnet_result, cartridge_result, kobold_result])

# Phase 4+: Switch to typed (just add query_type)
engine = ConsensusEngine(strategy="weighted_typed")
final = engine.vote(
    [bitnet_result, cartridge_result, kobold_result],
    query_type="synthesis"
)
```

---

## Feedback Loop (For Weighted Weight Learning)

```python
class FeedbackAggregator:
    """Track answer correctness to update engine weights."""
    
    def record_feedback(self, query_id: str, engine: str, correct: bool):
        """User confirmed answer correct or incorrect."""
        
        # Store feedback in Redis
        redis_client.lpush(
            "feedback:log",
            json.dumps({
                "query_id": query_id,
                "engine": engine,
                "correct": correct,
                "timestamp": time.time()
            })
        )
        
        # Increment counter
        if correct:
            redis_client.incr(f"engine:accuracy:{engine}:correct")
        redis_client.incr(f"engine:accuracy:{engine}:total")
    
    def update_weights(self):
        """Called periodically (e.g., daily) to recompute weights."""
        
        engines = ['bitnet', 'cartridge', 'kobold']
        new_weights = {}
        
        for engine in engines:
            correct = int(redis_client.get(f"engine:accuracy:{engine}:correct") or 0)
            total = int(redis_client.get(f"engine:accuracy:{engine}:total") or 0)
            
            if total > 0:
                accuracy = correct / total
                new_weights[engine] = accuracy
            else:
                new_weights[engine] = 1.0  # Default if no data
        
        # Update Redis weights
        redis_client.hset("model:weights", mapping=new_weights)
        
        # Log for diagnostics
        print(f"Updated weights: {new_weights}")

# Usage:
aggregator = FeedbackAggregator()
aggregator.record_feedback("query_abc123", "kobold", correct=True)
aggregator.update_weights()  # Run daily
```

---

## Decision: What You Should Commit To Now

**For Phase 3B:**
- ✅ Use **Simple Average** consensus
- ✅ Build infrastructure to support switching later
- ✅ Add `ConsensusEngine` class with strategy parameter
- ✅ Add `FeedbackAggregator` (logs feedback but doesn't use it yet)
- ✅ Design Redis keys for weights (even if unused)

**For Phase 4 (after you have data):**
- ✅ Switch `ConsensusEngine` to `strategy="weighted"`
- ✅ Activate `FeedbackAggregator.update_weights()` to compute initial weights
- ✅ Measure improvement (confidence, user satisfaction)

**For Phase 5+ (optional):**
- ❓ Add query type classification
- ❓ Switch to `strategy="weighted_typed"` if needed
- ❓ Per-query-type weight learning

---

## Summary: Implementation Difficulty vs. Migration Cost

| Decision | Difficulty Now | Cost to Change Later | Certainty Needed |
|----------|-----------------|---------------------|------------------|
| **Simple Average** | 15 min | Low (30 min to weighted) | None - you can try it |
| **Weighted Average** | 30 min | Medium (need feedback infrastructure) | Moderate - assumes you'll get feedback |
| **Weighted Typed** | 2+ hrs | High (complex infrastructure) | High - only if you have query classification |

**Best approach:** Code for Simple, but structure code so switching to Weighted is a flag change. Build the feedback infrastructure now (you'll need it Phase 4 anyway).

---

## Final Answer to Your Question

**My recommendation:** Go with **Simple Average for Phase 3B**.

**Rationale:**
- You need to understand your actual data distribution before committing to weighted learning
- Simple works immediately, no tuning
- Switching to weighted later is genuinely low-friction (one flag change)
- You might discover weighted doesn't matter (many use cases simple average is good enough)
- Consensus logic in Phase 3B is "nice to have" anyway—pure escalation (Strategy A from consensus document) is your main path

**Implementation cost:** 30 minutes to add the ConsensusEngine class + feedback infrastructure scaffolding

**Storage cost:** ~100 bytes per query to track which engines answered

**Switching cost (to weighted):** 30 minutes when you're ready

This is the "build it once, prove it works before over-engineering" approach.
