# Redis Schema Integration Guide

The **Redis schema** is the "nervous system's working memory" - a fast cache layer for the reflex path.

## What It Stores

### 1. **CMS (Cache Management System)** - Query Resonance
Tracks which queries are important right now.

```python
# Every query hit updates resonance
cms:a1b2c3d4e5f6 → {
    "count": 47,
    "resonance_score": 0.87,  # Decays over time
    "last_accessed": "2026-02-12T20:00:00Z"
}

# Associated grains for this query
cms:a1b2c3d4e5f6:grains → [grain_42, grain_17, grain_88]

# Decay counter (multiplied by 0.9 per cycle)
cms:a1b2c3d4e5f6:resonance → 0.726
```

### 2. **Grain Signatures** - Fast Ternary Lookup
Pre-computed grain data for <0.5ms lookup.

```python
# Grain metadata
grain:42:sig → {
    "popcount": 156,
    "axiom": "thermodynamics",
    "weight": 1.58
}

# Positive bit-array (for +1 weights)
grain:42:bits:+ → (binary data)

# Negative bit-array (for -1 weights)
grain:42:bits:- → (binary data)

# Index of all grains
grain:index → {grain_1, grain_2, ..., grain_1000}
```

### 3. **Ghost Signals** - Speculative Activation
When a query has high resonance, pre-load its grains.

```python
# Top 3 grains to load for this query
ghost:a1b2c3d4e5f6 → "42,17,88"

# Count successful pre-loads
ghost:activations → 12847
```

### 4. **Hat Context** - Persona Switching
Instant context switching via XOR masks.

```python
# Current active persona
hat:current → "analytical"

# XOR mask for each hat (changes interpretation)
hat:analytical:mask → (256-bit binary data)
hat:creative:mask → (256-bit binary data)
```

### 5. **Metrics** - Performance Tracking
Monitor system health.

```python
metrics:queries:count → 4827       # Total queries
metrics:latency:p95 → 8.3          # 95th percentile (ms)
metrics:latency:p99 → 12.7         # 99th percentile
metrics:grains:lookups → 38472     # Grain signature accesses
metrics:cache:hits → 3847          # CMS cache hits
```

---

## Performance Targets

All Redis operations hit <1ms:
- CMS record lookup: **O(1)** 
- Grain signature get: **O(1)**
- Ghost activation: **O(1)**
- Hat context switch: **O(1)**

**Total reflex path latency: <0.5ms**

---

## Memory Budget

For realistic load (10,000 active queries + 1,000 grains):
- **Total: ~9-10MB**
- Per 1000 queries: ~3.8MB
- Per 100 grains: ~2.1MB

Scales linearly. Even with 100,000 queries: ~90MB.

---

## Integration with Cartridge + Registry

### Workflow: Query → Redis → Reflex Response

```python
from kitbash_redis_schema import RedisSchemaSpec, RedisClient

# Initialize
redis = RedisClient()

# User query arrives
query = "what is DNA?"
query_hash = sha256(query).hexdigest()

# Step 1: Check CMS for resonance
cms_data = redis.cms_record_get(query_hash)
if cms_data and cms_data['resonance_score'] > 0.8:
    # High-resonance: use speculative activation
    ghost_grains = redis.ghost_signal_get(query_hash)
    # Pre-load these grains into L3 cache
else:
    # Low-resonance: normal query path
    ghost_grains = []

# Step 2: Look up grain signatures for fast ternary matching
for grain_id in ghost_grains:
    sig = redis.grain_signature_get(grain_id)
    bits_plus = redis.get_grain_bits_plus(grain_id)
    bits_minus = redis.get_grain_bits_minus(grain_id)
    
    # XOR with current hat mask for context
    current_hat = redis.hat_context_switch()
    mask = redis.get_hat_mask(current_hat)
    
    # Bit-sliced ternary lookup: XOR + POPCOUNT
    result = popcount(bits_plus & ~bits_minus)
    # Result is ternary: +1, -1, or void

# Step 3: Record metrics
redis.metrics_record_query(latency_ms=2.3)

# Step 4: Update CMS for next query
redis.cms_record_set(
    query_hash,
    {
        "count": cms_data['count'] + 1,
        "resonance": new_resonance_score,
        "grains": matching_grain_ids,
    }
)
```

---

## Key Design Decisions

### 1. **Flat Key Structure**
All keys are flat (`cms:hash`, `grain:id:sig`), not nested objects.
- Simpler to reason about
- Faster lookups
- Easier to expire

### 2. **Time Decay on Resonance**
Every cycle, resonance multiplies by 0.9:
```
resonance_t = resonance_0 * (0.9 ^ cycles_elapsed)
```
This ensures recent queries are prioritized.

### 3. **Ghost Signals**
High-resonance queries pre-load their grains:
- If `resonance > 0.8`: load top-3 grains speculatively
- If successful: increment `ghost:activations`
- Measures cache warming effectiveness

### 4. **Hat Masks**
Context switching via XOR is instant:
- Get current hat
- Get its XOR mask
- XOR mask with grain bits
- Reinterprets grain for different context

### 5. **Metrics for Tuning**
Track everything needed for optimization:
- Query count (throughput)
- Latency percentiles (performance)
- Grain lookups (reflex activation)
- Cache hits (CMS effectiveness)

---

## Operational Considerations

### Expiration Policy

| Key Type | TTL | Reason |
|----------|-----|--------|
| CMS record | 24h | Queries fade over days |
| CMS grains | 24h | Associated grains stale quickly |
| Resonance | 5d | Keep history longer |
| Grain signatures | None | Permanent (until grain updated) |
| Grain bits | None | Permanent |
| Ghost signals | 1h | High-resonance queries change quickly |
| Hat masks | None | Permanent |
| Metrics | None | Keep for analysis |

### Scaling Strategy

**Small load (1000 queries, 100 grains):**
- Single Redis instance
- Memory: ~1-2MB

**Medium load (10000 queries, 1000 grains):**
- Single Redis instance
- Memory: ~9-10MB
- Consider replication for backup

**Large load (100000 queries, 10000 grains):**
- Redis Cluster with sharding by query_hash
- Each shard: ~90MB
- Locality-preserving hashing (queries routed to same shard)

---

## Testing the Schema

```python
from kitbash_redis_schema import RedisSchemaSpec, MemoryBudget

# Verify key naming
key = RedisSchemaSpec.cms_record_key("test_hash")
assert key == "cms:test_hash"

# Estimate memory for your load
memory_mb = MemoryBudget.estimate_total_mb()
print(f"Estimated Redis memory: {memory_mb}MB")

# Check performance targets
assert RedisSchemaSpec.cms_record_key("x") is not None
assert RedisSchemaSpec.grain_signature_key(1) is not None
```

---

## Implementation Checklist

- [ ] Redis instance running
- [ ] Schema keys defined (RedisSchemaSpec)
- [ ] CMS records populated from DeltaRegistry
- [ ] Grain signatures loaded from Cartridge
- [ ] Ghost signals computed
- [ ] Hat masks initialized
- [ ] Metrics collection started
- [ ] Performance targets validated (<0.5ms)
- [ ] Memory usage monitored
- [ ] Expiration policies set

---

## Next Steps (Week 2)

1. **Connect to DeltaRegistry** - Feed phantom data into Redis
2. **Load grains** - When crystallized, update grain signatures in Redis
3. **Compute ghost signals** - For high-resonance queries
4. **Measure reflex latency** - Validate <0.5ms target
5. **Tune thresholds** - Adjust resonance decay, ghost thresholds

---

**Redis = the reflex path's working memory. Fast, simple, and efficient.**
