# Kitbash Multi-Device Networking Architecture
**Design Specification for Locally Networked Integration**

---

## Problem Statement

You want Kitbash to work across **locally networked devices** (same network, no cloud) without retrofitting later. This means:
- Device A might run Kitbash core (grain router + cartridges)
- Device B might run bitnet.cpp inference
- Device C might run kobold.cpp LLM inference
- They need to orchestrate without redesigning Layer 1+ later

Current state: Everything runs locally on GTX 1060. No networking code exists yet.

---

## Constraint Analysis

### What Must NOT Happen

1. **No tight coupling to local file paths** 
   - Current: `GrainRouter("./cartridges")` assumes cartridges on same device
   - Future: Cartridges might live on Device A, bitnet on Device B
   - Hook needed: Cartridge load interface abstracted from storage location

2. **No single inference engine hardcoding**
   - Current: `process_query()` returns single response
   - Future: Kitbash decides "send to bitnet" vs "send to kobold" vs "answer locally"
   - Hook needed: Inference routing interface, not direct LLM calls

3. **No monolithic diagnostic output**
   - Current: Metrics built into response
   - Future: Different devices need to see different data (worker vs. orchestrator)
   - Hook needed: Structured logging that can be consumed/filtered remotely

4. **No assumption of synchronous request/response**
   - Current: REPL blocks on query
   - Future: Network latency means some queries might timeout or need queuing
   - Hook needed: Status tracking, job IDs, result polling

### What CAN Stay Local (For Now)

- Grain router (fast, in-memory hash table)
- Cartridge loading (read-only, no network I/O initially)
- Layer 0 processing (deterministic, no side effects)
- Local diagnostics (printed to stdout)

---

## Proposed Architecture

### Design Principle: **Layered Abstraction**

```
Layer 0: Local Reflexive Routing
  ├─ Grain router (stays local)
  ├─ Cartridge loading (stays local, but interface abstracted)
  ├─ Query preprocessing (stays local)
  └─ Response validation (stays local)

Layer 1+: Distributed Inference
  ├─ BitNet reflex gates (could run locally OR remotely)
  ├─ Cartridge synthesis (could run locally OR remotely)
  ├─ SmolML specialist models (remote on Device B)
  └─ Full LLM (remote on Device C)

Orchestration: Routing Decisions
  ├─ Kitbash decides: "This query → Layer 0" (local)
  ├─ Kitbash decides: "This query → bitnet@Device_B" (network)
  ├─ Kitbash decides: "This query → kobold@Device_C" (network)
  └─ Kitbash decides: "This query → cartridge + validation" (local)

Diagnostic Feed: Structured Logging
  ├─ Query ID (tracked end-to-end)
  ├─ Routing decision (which layer, which device)
  ├─ Latency breakdown (network + inference)
  ├─ Result confidence and source
  └─ Consumable by monitoring tools (CLI, Gradio, metrics)
```

---

## Implementation Hooks (To Add Now)

### 1. Cartridge Storage Abstraction

**Current (coupled to local filesystem):**
```python
def __init__(self, cartridges_dir: str = "./cartridges"):
    self.grain_router = GrainRouter(cartridges_dir)
```

**Future (abstracted, local at first):**
```python
class CartridgeLoader:
    """Interface for loading cartridges from anywhere."""
    def load(self, cartridge_name: str) -> Cartridge:
        raise NotImplementedError
    
    def list_cartridges(self) -> List[str]:
        raise NotImplementedError

class LocalCartridgeLoader(CartridgeLoader):
    """Load from local filesystem."""
    def __init__(self, cartridges_dir: str):
        self.cartridges_dir = cartridges_dir
    
    def load(self, cartridge_name: str) -> Cartridge:
        # Current implementation: load from disk
        pass

class RemoteCartridgeLoader(CartridgeLoader):
    """Future: Load from network (Device A's cartridge server)."""
    def __init__(self, device_url: str):
        self.device_url = device_url
    
    def load(self, cartridge_name: str) -> Cartridge:
        # Future: HTTP GET to Device A's /cartridge/{name} endpoint
        pass

# Usage (same for both local and remote):
loader = LocalCartridgeLoader("./cartridges")  # or RemoteCartridgeLoader("http://device_a:5000")
cartridge = loader.load("physics")
```

**Action:** Add `CartridgeLoader` interface now (even if only `LocalCartridgeLoader` exists). Don't hard-code file paths deeper than this layer.

---

### 2. Inference Engine Abstraction

**Current (direct calls):**
```python
def process_query(self, query: str) -> Dict:
    # Hard assumption: returns answer immediately
    return {'answer': ..., 'layer': 'GRAIN'}
```

**Future (routable):**
```python
class InferenceEngine:
    """Interface for any inference source."""
    async def infer(self, query: str, context: Dict) -> InferenceResult:
        """Send query to this engine, get structured result."""
        raise NotImplementedError

class LocalBitNetEngine(InferenceEngine):
    """BitNet ternary model, runs locally."""
    async def infer(self, query: str, context: Dict) -> InferenceResult:
        # Run bitnet.cpp locally
        pass

class RemoteBitNetEngine(InferenceEngine):
    """BitNet model on Device B."""
    async def infer(self, query: str, context: Dict) -> InferenceResult:
        # HTTP POST to Device B's /infer/bitnet endpoint
        # Wait for result with timeout
        pass

class KoboldCppEngine(InferenceEngine):
    """KoboldCpp LLM on Device C."""
    async def infer(self, query: str, context: Dict) -> InferenceResult:
        # HTTP POST to Device C's /completion endpoint
        pass

class QueryRouter:
    """Orchestrator: decides which engine to use."""
    def __init__(self, engines: Dict[str, InferenceEngine]):
        self.engines = engines
    
    async def route_query(self, query: str) -> InferenceResult:
        """Kitbash decides which layer/engine."""
        # Layer 0: grain lookup (local, no network)
        grain_result = layer0_lookup(query)
        if grain_result.confidence > 0.85:
            return grain_result  # No network needed
        
        # Layer 1: BitNet reflex
        bitnet_result = await self.engines['bitnet'].infer(query, {})
        if bitnet_result.confidence > 0.75:
            return bitnet_result
        
        # Layer 4: Full LLM (last resort)
        llm_result = await self.engines['kobold'].infer(query, {})
        return llm_result
```

**Action:** 
1. Create `InferenceEngine` interface (abstract base)
2. Create local stub implementations (`LocalBitNetEngine`, mock)
3. Extract current Layer 1+ logic into `LocalBitNetEngine` (even if just keyword matching)
4. Plan `RemoteBitNetEngine` as a TODO for Phase 3C

---

### 3. Structured Diagnostic Feed

**Current (baked into response):**
```python
return {
    'layer': 'GRAIN',
    'latency_ms': 0.17,
    'confidence': 0.95
}
```

**Future (structured, multi-consumer):**
```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class DiagnosticLevel(Enum):
    DEBUG = "debug"      # All routing decisions, timing
    INFO = "info"        # Key decisions, layer selection
    WARNING = "warning"  # Confidence drops, escalations
    ERROR = "error"      # Failures, retries
    SUMMARY = "summary"  # User sees this (final answer only)

@dataclass
class DiagnosticEvent:
    """Single routing/timing event."""
    query_id: str          # Unique per query (UUID)
    timestamp: float       # Unix time
    event_type: str        # "layer0_hit", "escalate_to_layer1", "network_request", etc.
    level: DiagnosticLevel
    device: str            # "local" or "device_b" or "device_c"
    layer: str             # Which layer (0, 1, 2, etc.)
    engine: str            # Which engine ("grain", "bitnet", "kobold", etc.)
    latency_ms: float      # Time for this step
    confidence: float      # Result confidence
    details: Dict          # Extra context (grain_id, fact_id, etc.)

class DiagnosticFeed:
    """Structured logging for all routing decisions."""
    
    def __init__(self):
        self.events: List[DiagnosticEvent] = []
        self.handlers = []  # Can attach listeners
    
    def log_event(self, event: DiagnosticEvent):
        """Record diagnostic event."""
        self.events.append(event)
        
        # Notify listeners (for streaming to Gradio, logging, etc.)
        for handler in self.handlers:
            handler(event)
    
    def attach_handler(self, handler):
        """Attach a consumer (e.g., Gradio WebSocket, file logger)."""
        self.handlers.append(handler)
    
    def query_log(self, query_id: str) -> List[DiagnosticEvent]:
        """Get all events for a single query (for post-mortem analysis)."""
        return [e for e in self.events if e.query_id == query_id]

# Usage:
feed = DiagnosticFeed()

# Attach multiple consumers:
feed.attach_handler(lambda e: print(f"[{e.level.value}] {e.event_type}: {e.latency_ms:.2f}ms"))  # CLI
feed.attach_handler(lambda e: metrics_db.insert(e))  # Metrics database
feed.attach_handler(lambda e: websocket.send(e))     # Gradio real-time

# During query processing:
event = DiagnosticEvent(
    query_id="abc123",
    timestamp=time.time(),
    event_type="layer0_hit",
    level=DiagnosticLevel.INFO,
    device="local",
    layer="0",
    engine="grain",
    latency_ms=0.17,
    confidence=0.95,
    details={"grain_id": "sg_abc123", "fact_id": 42}
)
feed.log_event(event)
```

**Action:**
1. Create `DiagnosticEvent` and `DiagnosticFeed` classes
2. Thread `feed` through `Layer0QueryProcessor` and future layers
3. Start logging events for every decision (no events lost)
4. Design with multiple consumers in mind (file, CLI, metrics DB, websocket)

---

### 4. Query Tracking & Status

**Current (synchronous only):**
```python
result = processor.process_query("what is ATP?")
print(result['answer'])
```

**Future (with job IDs for network latency):**
```python
@dataclass
class QueryJob:
    """Track query across potentially async network calls."""
    query_id: str          # UUID, unique per request
    user_query: str
    status: str            # "queued", "processing", "layer1_wait", "complete", "failed"
    submitted_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    current_layer: int
    current_device: str
    result: Optional[Dict]
    error: Optional[str]

class QueryTracker:
    """Manages in-flight queries."""
    
    def __init__(self):
        self.jobs: Dict[str, QueryJob] = {}
    
    def create_job(self, query_text: str) -> str:
        """Create new job, return query_id."""
        query_id = str(uuid.uuid4())
        self.jobs[query_id] = QueryJob(
            query_id=query_id,
            user_query=query_text,
            status="queued",
            submitted_at=time.time(),
            started_at=None,
            completed_at=None,
            current_layer=0,
            current_device="local",
            result=None,
            error=None
        )
        return query_id
    
    def get_status(self, query_id: str) -> QueryJob:
        """Check status of in-flight query."""
        return self.jobs.get(query_id)
    
    def update_job(self, query_id: str, **kwargs):
        """Update job status (called by processor)."""
        if query_id in self.jobs:
            for key, value in kwargs.items():
                setattr(self.jobs[query_id], key, value)

# Usage (today):
tracker = QueryTracker()
query_id = tracker.create_job("what is ATP?")
result = processor.process_query("what is ATP?", query_id=query_id)
tracker.update_job(query_id, status="complete", result=result)

# Usage (future, with network):
query_id = tracker.create_job("complex synthesis question")
# Kitbash sends to Device B for bitnet inference
# Can poll: tracker.get_status(query_id) to see if Device B finished
# Result comes back async
tracker.update_job(query_id, status="complete", result=...)
```

**Action:**
1. Create `QueryJob` and `QueryTracker` classes
2. Add `query_id` parameter throughout query processing
3. Update diagnostic events to reference `query_id`
4. Plan status endpoint (WSGI/FastAPI) for future multi-device polling

---

## Implementation Roadmap

### Phase 3B Week 1: Add Abstraction Layers (Do This Now)
- [ ] Create `CartridgeLoader` interface + `LocalCartridgeLoader` implementation
- [ ] Create `InferenceEngine` interface + `LocalBitNetEngine` stub
- [ ] Create `DiagnosticEvent` and `DiagnosticFeed` classes
- [ ] Create `QueryJob` and `QueryTracker` classes
- [ ] Thread these through existing `Layer0QueryProcessor`
- [ ] Update REPL to show structured diagnostics
- [ ] **No network code yet**, just interfaces

**Time estimate:** 4-5 hours (mostly refactoring existing code)

### Phase 3B Week 2: Layer 1 Experimentation
- [ ] Implement `LocalBitNetEngine` (actual BitNet or keyword matching, TBD)
- [ ] Test routing logic: grain → bitnet escalation
- [ ] Validate diagnostic feed records all decisions
- [ ] Collect real latency data
- **Still no network**, just preparing for it

### Phase 3C: Network Integration (Future, Now Architected For)
- [ ] Implement `RemoteBitNetEngine` (HTTP to Device B)
- [ ] Add timeout/retry logic for network failures
- [ ] Implement HTTP API endpoints (FastAPI)
- [ ] Multi-device orchestration tests
- [ ] Gradio UI pulls from `DiagnosticFeed` websocket

---

## File Structure (Post-Refactor)

```
kitbash/
├── core/
│   ├── grain_router.py          (unchanged)
│   ├── layer0_query_processor.py (updated: uses abstractions)
│   ├── cartridge_loader.py       (NEW)
│   ├── inference_engine.py       (NEW)
│   ├── query_tracker.py          (NEW)
│   └── diagnostic_feed.py        (NEW)
├── local/
│   ├── local_cartridge_loader.py (NEW)
│   └── local_bitnet_engine.py    (NEW)
├── remote/
│   ├── remote_bitnet_engine.py   (NEW, Phase 3C)
│   ├── remote_kobold_engine.py   (NEW, Phase 3C)
│   └── query_router.py           (NEW, Phase 3C)
├── interfaces/
│   ├── fastapi_server.py         (NEW, Phase 3C)
│   └── cli_repl.py               (updated query_repl.py)
└── cartridges/
    ├── physics/
    ├── chemistry/
    └── ...
```

---

## Key Design Principles

1. **Interfaces first, implementations second**
   - Define contract, then implement locally, then swap in remote
   - Prevents "oops, we hardcoded Device A's hostname"

2. **Query IDs everywhere**
   - Every request gets a UUID
   - Diagnostic events reference it
   - Enables end-to-end tracing across devices

3. **Structured diagnostics, not strings**
   - Not: `print("Found grain in 0.17ms")`
   - Yes: `feed.log_event(DiagnosticEvent(...))`
   - Allows Gradio, metrics, monitoring to consume programmatically

4. **Cartridges are read-only data**
   - Future: Can cache on multiple devices
   - No distributed write coordination needed
   - Simple distribution model (copy cartridge once, read many)

5. **Inference engines are pluggable**
   - New engine type? Add a class implementing `InferenceEngine`
   - Router sends to it? Update routing logic
   - No core code changes needed

---

## Testing Strategy

### Unit Tests (Phase 3B)
- Test `CartridgeLoader` abstraction (local only)
- Test `InferenceEngine` interface with mocks
- Test `DiagnosticFeed` event logging
- Test `QueryTracker` status updates

### Integration Tests (Phase 3C)
- Mock remote engine (simulate network latency)
- Test routing decisions with failures
- Test query timeout/retry logic
- Test diagnostic feed with multiple handlers

### Multi-Device Tests (Phase 4+)
- Actually run on two machines on same network
- Test cartridge distribution
- Test inference on remote device
- Monitor diagnostic feed across network

---

## Decision Points

**Q: Should cartridges be cached on Device B (bitnet)?**
- A: Later. Start with cartridges only on Device A. Phase 4+ can optimize distribution.

**Q: What's the minimum viable remote engine?**
- A: HTTP endpoint that accepts JSON query, returns JSON result. FastAPI stub is 10 lines.

**Q: Should Layer 1 BitNet be local or remote in Phase 3B?**
- A: Start local (faster iteration). Phase 3C moves it to Device B if needed.

**Q: How do we handle network failures?**
- A: Timeout + fallback (escalate to next layer). Implement once you have actual network calls.

---

**Status: Ready for Phase 3B implementation**

These abstractions cost 4-5 hours to add now, save 20+ hours retrofitting later.
