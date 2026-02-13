# Kitbash Phase 3B Architecture Summary
**Complete Design for Redis-Coordinated, Multi-Device Orchestration**

---

## Architecture Overview

You're building Kitbash as a **hierarchical orchestrator** that:
- Presents as one unified system to users
- Internally coordinates subprocesses (bitnet on Device B, kobold on Device C)
- Uses **Redis Blackboard** as the coordination substrate
- Scales from local (all processes on GTX 1060) to distributed (subprocesses on remote devices)
- Supports future edge device microservices without redesign

**Key principle:** Kitbash controls, subprocesses execute. Subprocesses are stateless workers that read/write Redis.

---

## Three Foundational Decisions (Made)

### Decision 1: Redis Blackboard (Not HTTP RPC)

**Why Redis instead of direct HTTP/gRPC?**

| Aspect | HTTP/gRPC | Redis Blackboard |
|--------|-----------|------------------|
| Serial execution | Blocking calls | Poll-based, easily adapts |
| Async parallelism | Futures/promises | asyncio.gather() on same code |
| State visibility | Hidden in responses | Queryable, debuggable |
| Subprocess discovery | Hard-coded or registry | Self-register at startup |
| Edge device support | Need reverse proxies | Simple HTTP proxy layer |

**You chose:** Redis Blackboard
- Scales from serial to async without architecture change
- Unified view of all in-flight queries
- Edge device proxy works straightforwardly
- Fits your "unified orchestrator" model

### Decision 2: Environment-Based Config (Not YAML)

**Why env vars instead of YAML config files?**

| Aspect | YAML | Environment Variables |
|--------|------|----------------------|
| Containerization | Needs volume mounts | Native Docker/K8s |
| Secrets management | Hardcoded or sidecar | Integrated with orchestration |
| Runtime changes | Requires restart | Hot-reloadable (optional) |
| Development | Easy local testing | Needs .env files |

**You chose:** Environment variables
- Docker/K8s native (matters for "other people" using Kitbash)
- Fallback to YAML for local dev (file-based, zero setup)
- Better for containerized deployment

### Decision 3: Simple Average Consensus (Not Weighted/Typed)

**Why start simple, graduate to complex later?**

| Strategy | Phase 3B | Phase 4 | Phase 5+ |
|----------|----------|---------|---------|
| **Simple Average** | 15 min to code | Switch to weighted in 30 min | Drop-in replacement |
| **Weighted** | 30 min, needs data | Learn from feedback | Refinement |
| **Weighted Typed** | 2+ hrs, complex | Needs query classification | Overkill if simple works |

**You chose:** Simple Average
- No tuning needed, works immediately
- Collect 1000+ queries of data in Phase 3B
- Switch to weighted in Phase 4 without architecture changes
- Cost of migration: 30 minutes, low risk

---

## Phase 3B Implementation Plan

### What You're Building

A **three-layer orchestration system**:

```
┌─────────────────────────────────┐
│  KITBASH ORCHESTRATOR (Device A)│
│  ├─ Layer 0: Grain routing (0.17ms)
│  ├─ Query Router (decision logic)
│  └─ Subprocess Manager (health, discovery)
└──────────────┬──────────────────┘
               │
         ┌─────▼─────┐
         │    REDIS  │
         │ BLACKBOARD│
         └─────▬─────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼──┐  ┌───▼───┐
│Bitnet │  │Cart.│  │Kobold │
│(Dev B)│  │(Dev)│  │(Dev C)│
└───────┘  └─────┘  └───────┘
```

**Components to build:**

1. **Redis Blackboard** (`blackboard.py`)
   - Key schema (query state, results, subprocess health)
   - Helpers for common operations (get/set with retry)
   - ~100 lines

2. **Query Orchestrator** (`query_orchestrator.py`)
   - Serial execution loop (Phase 3B)
   - Layer 0 → Layer 1 → Layer 4 escalation
   - Logging diagnostic events
   - ~200 lines

3. **Subprocess Manager** (`subprocess_manager.py`)
   - Discovery from env vars or YAML
   - Spawn/monitor local processes
   - Health check loop
   - Lifecycle management
   - ~300 lines

4. **Diagnostic Feed** (`diagnostic_feed.py`)
   - Events to Redis (append-only)
   - Multiple consumers (CLI, metrics, future Gradio)
   - Query-specific logs for post-mortem
   - ~150 lines

5. **Consensus Engine** (`consensus.py`)
   - Simple average voting (extensible to weighted)
   - Feedback aggregation infrastructure
   - ~200 lines

6. **Bitnet Worker Stub** (`subprocesses/bitnet_worker.py`)
   - Listens to Redis for `query:{id}:layer1:request`
   - Runs bitnet inference (or mock)
   - Writes to `query:{id}:layer1:result`
   - ~100 lines

7. **REPL Refactored** (`query_repl.py`)
   - `--mode direct` (Phase 3B testing, no Redis)
   - `--mode redis` (Phase 3C testing, with Redis)
   - Show Layer 0 → Layer 1 → Layer 4 flow
   - ~200 lines

**Total: ~1200 lines of code, clear separation of concerns**

### Phase 3B Timeline

**Week 1 (5-6 days):**
- [ ] Implement `blackboard.py` (1 day)
- [ ] Implement `query_orchestrator.py` serial loop (1.5 days)
- [ ] Implement `subprocess_manager.py` (1.5 days)
- [ ] Implement `diagnostic_feed.py` (0.5 days)
- [ ] Implement `consensus.py` simple voting (0.5 days)
- [ ] Create `bitnet_worker.py` stub (0.5 days)

**Week 2 (3-4 days):**
- [ ] Refactor REPL with `--mode` flag (1 day)
- [ ] Write integration tests (Redis + mocked subprocesses) (1 day)
- [ ] Manual testing: run 100+ queries, collect data (1 day)
- [ ] Document observed behavior (0.5 days)

**End of Phase 3B:** You have:
- ✅ Serial Redis orchestration working
- ✅ 100+ queries logged with confidence scores
- ✅ Diagnostic feed showing all routing decisions
- ✅ Real latency numbers (Layer 0, 1, 4)
- ✅ Infrastructure ready for Phase 4

---

## Data You'll Collect (Critical for Phase 4)

```
Query: "what is ATP?"
  Layer 0: grain hit, confidence 0.95, latency 0.17ms → RETURNED

Query: "explain photosynthesis at molecular level"
  Layer 0: miss
  Layer 1 (bitnet): confidence 0.68, latency 1.2ms → ESCALATE
  Layer 4 (kobold): confidence 0.91, latency 450ms → RETURNED

Query: "best debugging tools for C++"
  Layer 0: miss
  Layer 1 (bitnet): confidence 0.73, latency 1.1ms → ESCALATE
  Layer 4 (kobold): confidence 0.74, latency 445ms → RETURNED

[After 1000 queries]
Layer 0 hit rate: 78%
Layer 1 avg confidence when returned: 0.82
Layer 1 avg confidence when escalated: 0.67
Layer 4 avg latency: 450ms (95th percentile 520ms)
Timeout rate: 0.3% (3 queries out of 1000)

Observation: Layer 1 confidence 0.70-0.80 range is ambiguous
  → Phase 4: Implement consensus logic for these cases
```

---

## Phase 3C/4 Evolution (Preview)

### Phase 3C: Add Consensus (If Data Shows Value)

```python
# Same orchestrator, new branch:
if l1_result['confidence'] < 0.75:
    # Spawn Layer 2 (cartridge synthesis) in parallel
    l2_result = await get_cartridge_result(query_id, timeout=500ms)
    
    if l2_result:
        final = consensus([l1_result, l2_result])
        if final['confidence'] > 0.80:
            return final  # Consensus was helpful
    
    # Otherwise escalate to Layer 4
```

### Phase 4: Full Async

```python
# Replace serial waits with asyncio.gather()
results = await asyncio.gather(
    get_bitnet_result(query_id, timeout=2s),
    get_cartridge_result(query_id, timeout=2s),
    return_exceptions=True
)
# Same Redis coordination, now parallel!
```

### Phase 5+: Edge Devices

```python
# Proxy server on device with Redis access
@app.post("/submit_work")
def edge_device_submits(device_id, query_id, result):
    # Write to Redis as if subprocess submitted it
    redis.set(f"query:{query_id}:{layer}:result", result)
    return {"ok": true}
```

---

## File Structure (Phase 3B End State)

```
kitbash/
├── core/
│   ├── grain_router.py              (existing)
│   ├── layer0_query_processor.py    (existing)
│   ├── query_orchestrator.py        (NEW - serial loop)
│   └── subprocess_manager.py         (NEW - lifecycle)
├── redis/
│   ├── __init__.py
│   ├── blackboard.py                (NEW - schema + helpers)
│   ├── diagnostic_feed.py            (NEW - event logging)
│   └── consensus.py                  (NEW - voting logic)
├── subprocesses/
│   ├── __init__.py
│   ├── bitnet_worker.py              (NEW - stub)
│   ├── cartridge_worker.py           (future, stub)
│   └── kobold_worker.py              (future, stub)
├── interfaces/
│   ├── __init__.py
│   ├── query_repl.py                 (refactored - direct vs redis modes)
│   └── orchestrator_interface.py     (NEW - common interface)
├── config/
│   ├── __init__.py
│   ├── loader.py                     (NEW - env var + YAML)
│   └── config_example.yaml           (NEW - YAML template)
├── tests/
│   ├── test_blackboard.py            (NEW)
│   ├── test_orchestrator.py          (NEW)
│   ├── test_consensus.py             (NEW)
│   └── test_integration_redis.py     (NEW)
├── cartridges/                       (existing)
│   ├── physics/
│   ├── chemistry/
│   └── ...
└── docker-compose.yml                (NEW - containerization example)
```

---

## Environment Variables (Reference)

**Phase 3B Setup:**

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Layer 0 (local)
CARTRIDGES_DIR=./cartridges

# Layer 1 (bitnet)
BITNET_TYPE=local                    # "local" or "remote"
BITNET_COMMAND="python -m bitnet_worker"
BITNET_HOST=localhost
BITNET_PORT=6379
BITNET_AUTO_SPAWN=true
BITNET_TIMEOUT=2000

# Layer 2 (cartridge synthesis, future)
CARTRIDGE_TYPE=local
CARTRIDGE_COMMAND="python -m cartridge_worker"
CARTRIDGE_HOST=localhost
CARTRIDGE_PORT=6379
CARTRIDGE_AUTO_SPAWN=true
CARTRIDGE_TIMEOUT=2000

# Layer 4 (kobold LLM)
KOBOLD_TYPE=remote                   # or "local" if running locally
KOBOLD_HOST=localhost
KOBOLD_PORT=5555
KOBOLD_AUTO_SPAWN=false              # Assume already running
KOBOLD_TIMEOUT=5000

# Diagnostics
DIAGNOSTIC_LEVEL=info                # debug, info, warning, error
LOG_TO_FILE=true
LOG_FILE=./kitbash.log
```

**For Docker:**

```yaml
version: '3'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  kitbash:
    build: .
    environment:
      - REDIS_HOST=redis
      - BITNET_HOST=bitnet_worker
      - KOBOLD_HOST=kobold_remote
    depends_on:
      - redis
  
  bitnet_worker:
    build: ./subprocesses/bitnet
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
  
  kobold_remote:
    image: oobabooga/text-generation-webui
    ports:
      - "5555:5555"
```

---

## Key Assumptions (Validate These)

1. **Redis is available** - You're using Redis, right? ✅
2. **Subprocesses can be spawned locally** - `subprocess.Popen()` works for bitnet, etc? ✅
3. **Network latency is acceptable** - Device B → Device A is fast enough? (TBD)
4. **Heartbeat/health checks sufficient** - No need for true RPC error handling? (TBD)
5. **Consensus voting deferred to Phase 4** - Pure escalation for now? ✅

---

## Success Criteria (End of Phase 3B)

- [ ] Redis Blackboard operational
- [ ] Query flows through: Layer 0 → Layer 1 → Layer 4
- [ ] 100+ queries logged to Redis
- [ ] Diagnostic feed shows all routing decisions
- [ ] REPL works in both `--mode direct` and `--mode redis`
- [ ] Latency measured: Layer 0, 1, 4
- [ ] Subprocess health monitoring working
- [ ] Timeout handling proven (timeout + escalate)
- [ ] Documentation of actual behavior vs. aspirational

---

## Next Step: Confirmation

Before coding Phase 3B, confirm:

1. **Redis available?** (Local instance, Docker container, or cloud?)
2. **BitNet strategy?** (Real inference, keyword matching, or mock for now?)
3. **Timeline?** (Want to finish Phase 3B in 2 weeks, or spread it out?)
4. **Metrics priority?** (Care most about latency, confidence scores, or throughput?)

Once you confirm, I can start writing actual Phase 3B code (not just designs).
