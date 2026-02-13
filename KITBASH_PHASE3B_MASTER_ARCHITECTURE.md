# Kitbash Phase 3B: Master Architecture Document
**Complete Reference for Redis-Coordinated Multi-Process Orchestration**

*Last Updated: February 13, 2026*
*Status: Design Complete, Ready for Implementation*

---

## Executive Summary

Kitbash is evolving from a single-process knowledge management system to a **distributed orchestrator** that coordinates multiple inference engines (BitNet, Cartridge Synthesis, Kobold LLM) across local and remote devices.

**Key Design Principle:** Users see one unified Kitbash interface. Internally, Kitbash core orchestrates stateless worker subprocesses via a Redis Blackboard—a shared state substrate where all processes read/write query results, diagnostics, and health information.

**Scope of Phase 3B:**
- Implement Redis Blackboard coordination (no logic changes, just plumbing)
- Support both serial execution (now) and async parallelization (Phase 4) on same code
- Prepare for edge device microservices (Phase 5+) without redesign
- Containerize everything (Docker + env vars, no YAML hardcoding)

**Timeline:** 2 weeks (infrastructure + basic orchestration testing)
**Team:** One engineer (can parallelize with V0/Claude Code once architecture is clear)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────┐
│                      USER INTERFACE                      │
│  (REPL, Gradio, or API - all same backend)              │
└─────────────────────┬─────────────────────────────────┘
                      │
         ┌────────────▼─────────────┐
         │  KITBASH ORCHESTRATOR    │
         │  (Device A - Main)       │
         │  ├─ Layer 0 Reflex       │
         │  │  (Grain Router)       │
         │  ├─ Query Router         │
         │  ├─ Subprocess Manager   │
         │  └─ Diagnostics Sink     │
         └────────────┬─────────────┘
                      │
         ┌────────────▼─────────────────────────┐
         │        REDIS BLACKBOARD              │
         │  (Shared State, All Processes See)   │
         │                                      │
         │  - Query state and results           │
         │  - Subprocess health/status          │
         │  - Diagnostic event log              │
         │  - Model weights (Phase 4+)          │
         │  - Metrics (latency, accuracy)       │
         └────────────┬─────────────────────────┘
                      │
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
   ┌────▼───┐    ┌───▼──┐    ┌────▼────┐    ┌───▼────┐
   │ BitNet │    │Cart. │    │ Kobold  │    │ Edge   │
   │Worker  │    │Worker│    │ Worker  │    │Proxy   │
   │(Dev A) │    │(Dev A)│    │(Dev C)  │    │(Phase5)│
   │Layer 1 │    │Layer2 │    │Layer 4  │    │        │
   └────────┘    └───────┘    └─────────┘    └────────┘
```

**Key insight:** Kitbash doesn't call subprocesses directly. Instead:
1. Kitbash writes a request to Redis: `query:{id}:{layer}:request`
2. Worker listens, sees work, picks it up
3. Worker does computation
4. Worker writes result to Redis: `query:{id}:{layer}:result`
5. Kitbash polls Redis, sees result, continues
6. No blocking calls, no tight coupling, enables parallelization later

---

## Data Model: Redis Key Schema

### Query Lifecycle Keys

All keys use consistent pattern: `query:{query_id}:...`

```python
# Initialization (Kitbash sets)
query:{query_id}:state = "processing" | "waiting" | "complete" | "failed"
query:{query_id}:user_query = "what is ATP?"
query:{query_id}:submitted_at = 1707847200.5

# Layer 0 Results (Kitbash writes)
query:{query_id}:layer0:result = {
    "found": true,
    "grain_id": "sg_abc123",
    "fact_id": 42,
    "answer": "ATP is adenosine...",
    "confidence": 0.95,
    "latency_ms": 0.17
}

# Layer 1 Request & Result (Kitbash writes request, BitNet worker writes result)
query:{query_id}:layer1:request = {
    "query": "what is ATP?",
    "context": {},
    "created_at": 1707847200.52,
    "timeout_ms": 2000
}

query:{query_id}:layer1:result = {
    "engine": "bitnet",
    "answer": "ATP is a nucleotide...",
    "confidence": 0.82,
    "latency_ms": 1.8,
    "completed_at": 1707847200.54,
    "facts_used": [45, 67, 89]
}

# Pending work tracking (Kitbash adds, workers remove when done)
query:{query_id}:pending = set("bitnet")  # Engines still working

# Result aggregation (for consensus voting, Phase 4+)
query:{query_id}:results = {
    "layer0": {...},
    "layer1": {...},
    "layer4": {...}
}

# Final answer (Kitbash writes when complete)
query:{query_id}:final_result = {
    "answer": "ATP is...",
    "confidence": 0.88,
    "sources": ["layer1:bitnet"],
    "method": "escalation",
    "total_latency_ms": 1.97
}
```

### Subprocess Health & Status Keys

```python
# Heartbeat (subprocess sets periodically, Kitbash monitors)
subprocess:{name}:alive = "true" | "false"
subprocess:{name}:pid = 12345
subprocess:{name}:started_at = 1707847100.5
subprocess:{name}:last_heartbeat = 1707847210.2

# Current state (subprocess updates as it works)
subprocess:{name}:status = "idle" | "processing" | "error"
subprocess:{name}:current_job = "query:abc123:layer1"
subprocess:{name}:load = 0.3  # 0-1 scale

# Capabilities (set at startup, Kitbash uses for routing)
subprocess:{name}:layers = list("layer1", "layer2")  # What can this process do?

# Discovery registry (subprocesses register at startup)
subprocesses:registry = hash(
    bitnet_local: {type: "local", pid: 12345, layers: ["layer1"]},
    kobold_remote: {type: "remote", host: "device_c", port: 5555, layers: ["layer4"]}
)
```

### Diagnostic & Metrics Keys

```python
# Event log (append-only, queryable)
diagnostics:{query_id}:events = list(
    {timestamp: 1707847200.5, event: "query_received", level: "info"},
    {timestamp: 1707847200.51, event: "layer0_attempt", layer: "0", level: "debug"},
    {timestamp: 1707847200.52, event: "layer0_hit", confidence: 0.95, latency_ms: 0.17, level: "info"},
    {timestamp: 1707847200.521, event: "query_complete", final_confidence: 0.95, level: "info"}
)

# Metrics aggregation (updated periodically)
metrics:queries:total = 1250
metrics:queries:layer0_hit_rate = 0.78
metrics:queries:avg_latency_ms = 5.2
metrics:subprocess:bitnet:requests = 275
metrics:subprocess:bitnet:avg_latency_ms = 1.9
metrics:subprocess:bitnet:error_rate = 0.01

# Feedback for learning (Phase 4+)
feedback:log = list(
    {query_id: "abc123", engine: "kobold", correct: true, timestamp: 1707847500},
    {query_id: "def456", engine: "bitnet", correct: false, timestamp: 1707847600}
)

engine:accuracy:{engine}:correct = N
engine:accuracy:{engine}:total = M
model:weights = hash(bitnet: 0.80, cartridge: 0.90, kobold: 0.95)  # Phase 4+
```

### Data Structure Summary

| Key Pattern | Type | Purpose | Set By | Read By |
|-------------|------|---------|--------|---------|
| `query:{id}:state` | String | Query status | Kitbash | All |
| `query:{id}:{layer}:request` | JSON | Work assignment | Kitbash | Worker |
| `query:{id}:{layer}:result` | JSON | Work result | Worker | Kitbash |
| `query:{id}:pending` | Set | Engines still working | Kitbash | All |
| `subprocess:{name}:alive` | String | Health signal | Worker | Kitbash |
| `subprocess:{name}:status` | String | Current state | Worker | Kitbash |
| `diagnostics:{id}:events` | List | Event log | Kitbash/Workers | Debugging |
| `metrics:*` | String/Hash | Aggregated stats | Kitbash | Monitoring |

---

## Core Components to Implement

### 1. Redis Blackboard Module (`redis/blackboard.py`)

Handles all Redis interactions with abstraction layer.

```python
class RedisBlackboard:
    """Redis key-value store abstraction for query coordination."""
    
    def __init__(self, host: str, port: int):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
    
    # Query State Operations
    def set_query_state(self, query_id: str, state: str) -> None:
        """Set query status (processing, complete, failed)."""
        
    def get_query_state(self, query_id: str) -> str:
        """Get current query status."""
        
    def set_layer_result(self, query_id: str, layer: str, result: Dict) -> None:
        """Worker writes result: query:{id}:{layer}:result"""
        
    def get_layer_result(self, query_id: str, layer: str, timeout_ms: int = 2000) -> Optional[Dict]:
        """Kitbash waits for result, polls Redis."""
        
    # Pending Work Tracking
    def add_pending_work(self, query_id: str, engine: str) -> None:
        """Add engine to pending set."""
        
    def remove_pending_work(self, query_id: str, engine: str) -> None:
        """Engine removes itself when done."""
        
    def get_pending_work(self, query_id: str) -> List[str]:
        """Get list of engines still working."""
    
    # Subprocess Health
    def set_subprocess_alive(self, subprocess_name: str, alive: bool) -> None:
        """Subprocess heartbeat."""
        
    def is_subprocess_alive(self, subprocess_name: str) -> bool:
        """Check if subprocess is healthy."""
        
    def set_subprocess_status(self, subprocess_name: str, status: str) -> None:
        """Update subprocess state (idle, processing, error)."""
```

**Responsibility:** All Redis operations go through this class. If you need to change Redis, it's one place.

### 2. Query Orchestrator (`core/query_orchestrator.py`)

Main serial loop that routes queries through layers.

```python
class QueryOrchestratorRedis:
    """Routes queries through layers using Redis coordination."""
    
    def __init__(self, config: Dict, blackboard: RedisBlackboard):
        self.config = config
        self.blackboard = blackboard
        self.diagnostics = DiagnosticFeed(blackboard)
    
    def process_query(self, query_id: str, user_query: str) -> Dict:
        """
        Main orchestration loop:
        1. Try Layer 0 (local, fast)
        2. If miss, try Layer 1 (bitnet via Redis)
        3. If still low conf, try Layer 4 (kobold via Redis)
        4. Return best result
        """
        
        # Initialize
        self.blackboard.set_query_state(query_id, "processing")
        self.diagnostics.log(query_id, "query_received")
        
        # Layer 0: Grain lookup (local, no Redis)
        l0_result = self._layer0_grain_lookup(user_query)
        self.blackboard.set_layer_result(query_id, "layer0", l0_result)
        
        if l0_result['confidence'] > 0.85:
            self.blackboard.set_query_state(query_id, "complete")
            return l0_result
        
        # Layer 1: BitNet (via Redis worker)
        self.diagnostics.log(query_id, "layer1_request", engine="bitnet")
        l1_result = self._escalate_to_layer(query_id, "layer1", "bitnet", timeout_ms=2000)
        
        if l1_result and l1_result['confidence'] > 0.80:
            self.blackboard.set_query_state(query_id, "complete")
            return l1_result
        
        # Layer 4: Kobold (via Redis worker)
        self.diagnostics.log(query_id, "layer4_request", engine="kobold")
        l4_result = self._escalate_to_layer(query_id, "layer4", "kobold", timeout_ms=5000)
        
        self.blackboard.set_query_state(query_id, "complete")
        return l4_result
    
    def _escalate_to_layer(self, query_id: str, layer: str, engine: str, timeout_ms: int) -> Optional[Dict]:
        """Send work to subprocess via Redis, wait for result."""
        
        # Write request
        request = {
            "query": self.blackboard.get(f"query:{query_id}:user_query"),
            "created_at": time.time(),
            "timeout_ms": timeout_ms
        }
        self.blackboard.set_layer_request(query_id, layer, request)
        self.blackboard.add_pending_work(query_id, engine)
        
        # Wait for result (poll Redis)
        result = self.blackboard.get_layer_result(query_id, layer, timeout_ms=timeout_ms)
        
        if result:
            self.blackboard.remove_pending_work(query_id, engine)
            self.diagnostics.log(query_id, f"{layer}_complete", 
                               engine=engine, latency=result['latency_ms'])
            return result
        else:
            self.diagnostics.log(query_id, f"{layer}_timeout", engine=engine)
            self.blackboard.remove_pending_work(query_id, engine)
            return None
```

**Responsibility:** Decide which layer to use, coordinate with workers via Redis. All actual inference happens in workers.

### 3. Subprocess Manager (`core/subprocess_manager.py`)

Monitors and manages worker process lifecycle.

```python
class SubprocessManager:
    """Spawns, monitors, and restarts subprocesses."""
    
    def __init__(self, config: Dict, blackboard: RedisBlackboard):
        self.config = config  # Loaded from env vars
        self.blackboard = blackboard
        self.subprocesses = {}  # {name: process}
    
    def ensure_subprocess(self, name: str) -> bool:
        """Start subprocess if not running."""
        
        # Check if already running
        if name in self.subprocesses and self.subprocesses[name].poll() is None:
            return True  # Already alive
        
        spec = self.config['subprocesses'][name]
        
        if spec['type'] == 'local':
            # Spawn locally
            proc = subprocess.Popen(spec['command'].split())
            self.subprocesses[name] = proc
            self.blackboard.set_subprocess_alive(name, True)
            return True
        
        elif spec['type'] == 'remote':
            # Assume already running, just mark available
            self.blackboard.set_subprocess_alive(name, True)
            return True
    
    def health_check(self) -> None:
        """Monitor subprocesses, restart if dead."""
        
        for name in self.config['subprocesses'].keys():
            if name in self.subprocesses:
                if self.subprocesses[name].poll() is not None:
                    # Process died
                    if self.config['subprocesses'][name].get('auto_spawn'):
                        self.ensure_subprocess(name)
                    else:
                        self.blackboard.set_subprocess_alive(name, False)
```

**Responsibility:** Manage subprocess lifecycle (start, monitor, restart). Health checks run periodically.

### 4. Diagnostic Feed (`redis/diagnostic_feed.py`)

Logs all routing decisions and events for observability.

```python
class DiagnosticFeed:
    """Append-only event log to Redis, queryable by query_id."""
    
    def __init__(self, blackboard: RedisBlackboard):
        self.blackboard = blackboard
    
    def log(self, query_id: str, event: str, level: str = "info", **details) -> None:
        """Record a diagnostic event to Redis."""
        
        event_obj = {
            "timestamp": time.time(),
            "event": event,
            "level": level,
            **details
        }
        
        self.blackboard.redis.lpush(
            f"diagnostics:{query_id}:events",
            json.dumps(event_obj)
        )
    
    def query_log(self, query_id: str) -> List[Dict]:
        """Get all events for a query (debugging, post-mortem)."""
        
        return self.blackboard.redis.lrange(f"diagnostics:{query_id}:events", 0, -1)
```

**Responsibility:** Structured logging. Every routing decision, every layer, every timeout—all recorded.

### 5. Consensus Engine (`redis/consensus.py`)

Voting logic for multi-engine results (Phase 4+, but scaffolding now).

```python
class ConsensusEngine:
    """Combine multiple engine results into consensus answer."""
    
    def __init__(self, strategy: str = "simple"):
        """
        strategy: "simple" (Phase 3B) | "weighted" (Phase 4) | "weighted_typed" (Phase 5+)
        """
        self.strategy = strategy
    
    def vote(self, results: List[Dict], query_type: Optional[str] = None) -> Dict:
        """Average confidence, pick best answer."""
        
        if self.strategy == "simple":
            # All engines weighted equally
            avg_confidence = sum(r['confidence'] for r in results) / len(results)
            best_result = max(results, key=lambda r: len(r['answer']))
            
            return {
                "answer": best_result['answer'],
                "confidence": avg_confidence,
                "method": "simple_average",
                "sources": [r['engine'] for r in results],
                "individual_confidences": {r['engine']: r['confidence'] for r in results}
            }
        
        elif self.strategy == "weighted":
            # Weighted by engine accuracy (Phase 4+)
            # Load weights from Redis, compute weighted average
            pass
        
        elif self.strategy == "weighted_typed":
            # Different weights per query type (Phase 5+)
            pass
```

**Responsibility:** Voting logic. Pluggable strategies, starts simple, upgrades with data.

### 6. Worker Process Stub (`subprocesses/bitnet_worker.py`)

Template for any worker subprocess (BitNet, Cartridge, Kobold proxy).

```python
class BitNetWorker:
    """Listens to Redis, runs inference, writes results back."""
    
    def __init__(self, config: Dict):
        self.blackboard = RedisBlackboard(config['redis_host'], config['redis_port'])
        self.bitnet_model = load_bitnet_model()  # Or mock for testing
    
    def run(self) -> None:
        """Main loop: look for work, do work, write results."""
        
        # Register self
        self.blackboard.set_subprocess_alive("bitnet", True)
        self.blackboard.set_subprocess_status("bitnet", "idle")
        
        while True:
            try:
                # Find pending queries
                pending_queries = self.blackboard.redis.keys("query:*:pending")
                
                for pending_key in pending_queries:
                    query_id = pending_key.split(":")[1]
                    pending_engines = self.blackboard.get_pending_work(query_id)
                    
                    if "bitnet" in pending_engines:
                        # We have work!
                        self.blackboard.set_subprocess_status("bitnet", "processing")
                        self.blackboard.redis.set(f"subprocess:bitnet:current_job", 
                                                f"query:{query_id}:layer1")
                        
                        # Get request details
                        request = json.loads(
                            self.blackboard.redis.get(f"query:{query_id}:layer1:request")
                        )
                        
                        # Do the work
                        start = time.time()
                        result_text = self.bitnet_model.infer(request['query'])
                        latency_ms = (time.time() - start) * 1000
                        
                        # Write result
                        result = {
                            "engine": "bitnet",
                            "answer": result_text,
                            "confidence": 0.75,  # Mock for now
                            "latency_ms": latency_ms,
                            "completed_at": time.time()
                        }
                        
                        self.blackboard.set_layer_result(query_id, "layer1", result)
                        self.blackboard.remove_pending_work(query_id, "bitnet")
                        
                        # Return to idle
                        self.blackboard.set_subprocess_status("bitnet", "idle")
                
                time.sleep(0.1)  # Poll every 100ms
            
            except Exception as e:
                self.blackboard.set_subprocess_status("bitnet", "error")
                time.sleep(1)
```

**Responsibility:** Worker template. Listens to Redis, reads request, runs inference, writes result. Stateless, restartable.

### 7. Configuration Loader (`config/loader.py`)

Environment variables + YAML fallback.

```python
class ConfigLoader:
    """Load config from env vars, YAML fallback."""
    
    @staticmethod
    def load() -> Dict:
        """
        Priority:
        1. Environment variables (Docker/K8s)
        2. YAML file (local dev)
        3. Defaults
        """
        
        config = {
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
            },
            'subprocesses': {
                'bitnet_local': {
                    'type': os.getenv('BITNET_TYPE', 'local'),
                    'command': os.getenv('BITNET_COMMAND', 'python -m bitnet_worker'),
                    'layers': ['layer1'],
                    'auto_spawn': os.getenv('BITNET_AUTO_SPAWN', 'true').lower() == 'true',
                    'timeout_ms': int(os.getenv('BITNET_TIMEOUT', '2000')),
                },
                'kobold_remote': {
                    'type': os.getenv('KOBOLD_TYPE', 'remote'),
                    'host': os.getenv('KOBOLD_HOST', 'localhost'),
                    'port': int(os.getenv('KOBOLD_PORT', '5555')),
                    'layers': ['layer4'],
                    'timeout_ms': int(os.getenv('KOBOLD_TIMEOUT', '5000')),
                }
            }
        }
        
        # Fallback to YAML if env not set
        if not os.getenv('BITNET_TYPE') and os.path.exists('kitbash_config.yaml'):
            with open('kitbash_config.yaml') as f:
                yaml_config = yaml.safe_load(f)
                config.update(yaml_config)
        
        return config
```

**Responsibility:** Load configuration from environment (or YAML), validate, pass to components.

### 8. REPL with Testing Bypass (`interfaces/query_repl.py`)

```python
class QueryREPL:
    def __init__(self, mode: str = "direct"):
        """
        mode: "direct" (Phase 3B testing, no Redis)
              "redis" (Phase 3C testing, with Redis + mocked workers)
        """
        self.mode = mode
        
        if mode == "redis":
            self.orchestrator = QueryOrchestratorRedis(config, blackboard)
        else:
            self.orchestrator = QueryOrchestratorDirect()  # Direct function calls
    
    def run_query(self, user_query: str):
        query_id = str(uuid.uuid4())
        result = self.orchestrator.process_query(query_id, user_query)
        print(f"Result: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Latency: {result.get('latency_ms', 'N/A')}")
```

**Responsibility:** User-facing REPL. Supports both testing modes and production Redis path.

---

## File Structure (End State)

```
kitbash/
├── core/
│   ├── __init__.py
│   ├── grain_router.py                (existing - unchanged)
│   ├── layer0_query_processor.py       (existing - unchanged)
│   ├── query_orchestrator.py           (NEW Phase 3B)
│   └── subprocess_manager.py            (NEW Phase 3B)
│
├── redis/
│   ├── __init__.py
│   ├── blackboard.py                   (NEW Phase 3B - Redis operations)
│   ├── diagnostic_feed.py               (NEW Phase 3B - event logging)
│   └── consensus.py                     (NEW Phase 3B - voting logic)
│
├── subprocesses/
│   ├── __init__.py
│   ├── bitnet_worker.py                 (NEW Phase 3B - template)
│   ├── cartridge_worker.py              (FUTURE - skeleton)
│   └── kobold_worker.py                 (FUTURE - skeleton)
│
├── interfaces/
│   ├── __init__.py
│   ├── query_repl.py                    (REFACTORED Phase 3B - direct vs redis modes)
│   └── orchestrator_interface.py        (NEW Phase 3B - abstract base)
│
├── config/
│   ├── __init__.py
│   ├── loader.py                        (NEW Phase 3B - env vars + YAML)
│   └── config_example.yaml              (NEW Phase 3B - template)
│
├── tests/
│   ├── __init__.py
│   ├── test_blackboard.py               (NEW Phase 3B - Redis operations)
│   ├── test_orchestrator.py             (NEW Phase 3B - query flow)
│   ├── test_consensus.py                (NEW Phase 3B - voting)
│   └── test_integration_redis.py        (NEW Phase 3B - end-to-end)
│
├── cartridges/                          (existing)
│   ├── physics/
│   ├── chemistry/
│   └── ...
│
├── Dockerfile                           (NEW Phase 3B - containerization)
├── docker-compose.yml                   (NEW Phase 3B - multi-service)
├── .env.example                         (NEW Phase 3B - config template)
├── requirements.txt                     (NEW Phase 3B - dependencies)
└── README.md                            (UPDATE - setup instructions)
```

---

## Implementation Sequence

### Phase 3B Week 1: Infrastructure & Core

1. **Setup Redis & Config** (1-2 days)
   - Redis running (local or Docker)
   - ConfigLoader implementation
   - .env and .env.example files

2. **Implement Blackboard** (1 day)
   - RedisBlackboard class
   - All key operations tested
   - Unit tests for Redis operations

3. **Implement Diagnostics** (0.5 days)
   - DiagnosticFeed class
   - Event logging to Redis
   - Query log retrieval

4. **Implement Consensus Scaffold** (0.5 days)
   - ConsensusEngine with "simple" strategy
   - Feedback infrastructure (for Phase 4)
   - Unit tests

### Phase 3B Week 2: Orchestration & Testing

5. **Implement Query Orchestrator** (1.5 days)
   - Serial execution loop
   - Layer 0 → Layer 1 → Layer 4 routing
   - Timeout handling

6. **Implement Subprocess Manager** (1 day)
   - Process spawning (local)
   - Health checks
   - Restart logic

7. **Implement BitNet Worker Stub** (0.5 days)
   - Template for any worker
   - Mock inference for testing

8. **Refactor REPL** (1 day)
   - `--mode direct` (testing, no Redis)
   - `--mode redis` (integration testing)
   - Both paths tested

9. **Integration Testing** (1 day)
   - End-to-end query flow
   - Mocked subprocess coordination
   - Diagnostics verification

---

## Testing Strategy

### Unit Tests (Phase 3B Week 1)

```python
# test_blackboard.py
def test_set_get_query_state():
    bb = RedisBlackboard('localhost', 6379)
    bb.set_query_state('q1', 'processing')
    assert bb.get_query_state('q1') == 'processing'

def test_layer_result_roundtrip():
    bb = RedisBlackboard('localhost', 6379)
    result = {"engine": "test", "answer": "x", "confidence": 0.9}
    bb.set_layer_result('q1', 'layer0', result)
    assert bb.get_layer_result('q1', 'layer0') == result

def test_pending_work_tracking():
    bb = RedisBlackboard('localhost', 6379)
    bb.add_pending_work('q1', 'bitnet')
    assert 'bitnet' in bb.get_pending_work('q1')
    bb.remove_pending_work('q1', 'bitnet')
    assert 'bitnet' not in bb.get_pending_work('q1')
```

### Integration Tests (Phase 3B Week 2)

```python
# test_integration_redis.py - full query flow
def test_query_layer0_hit():
    """Query hits Layer 0 grain, returns immediately."""
    orchestrator = QueryOrchestratorRedis(config, blackboard)
    result = orchestrator.process_query('q1', 'what is ATP?')
    assert result['confidence'] > 0.85
    assert 'layer0' in diagnostics.query_log('q1')

def test_query_layer1_escalation():
    """Query misses Layer 0, escalates to BitNet."""
    # Mock BitNet to write result to Redis
    result = orchestrator.process_query('q2', 'explain photosynthesis')
    assert result['engine'] == 'bitnet'
    events = diagnostics.query_log('q2')
    assert any(e['event'] == 'layer1_request' for e in events)

def test_query_timeout_escalation():
    """BitNet times out, escalates to Kobold."""
    # BitNet deliberately slow/missing
    result = orchestrator.process_query('q3', 'complex query')
    assert result['engine'] == 'kobold' or result.get('error')
    events = diagnostics.query_log('q3')
    assert any(e['event'] == 'layer1_timeout' for e in events)
```

### End-to-End Test (Phase 3B Week 2)

```python
# test_integration_redis.py - realistic scenario
def test_full_query_workflow():
    """Complete workflow: Layer 0 → Layer 1 → result via Redis."""
    
    # Start Redis, Kitbash, mocked BitNet worker
    orchestrator.process_query('q_test', 'what is energy?')
    
    # Check diagnostics
    events = diagnostics.query_log('q_test')
    assert events[0]['event'] == 'query_received'
    assert any(e['event'] in ['layer0_hit', 'layer1_request'] for e in events)
    assert events[-1]['event'] == 'query_complete'
    
    # Check query state
    assert blackboard.get_query_state('q_test') == 'complete'
    
    # Check result
    final = blackboard.get_final_result('q_test')
    assert final['answer']
    assert final['confidence'] > 0.5
```

---

## Environment Variables (Complete List)

```bash
# Redis Blackboard
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Layer 0 (local grain routing)
GRAIN_CONFIDENCE_THRESHOLD=0.85
CARTRIDGES_DIR=./cartridges

# Layer 1 (BitNet reflex)
BITNET_TYPE=local                       # "local" or "remote"
BITNET_COMMAND="python -m subprocesses.bitnet_worker"
BITNET_HOST=localhost
BITNET_PORT=6379
BITNET_TIMEOUT_MS=2000
BITNET_AUTO_SPAWN=true

# Layer 2 (Cartridge synthesis, future)
CARTRIDGE_TYPE=local
CARTRIDGE_COMMAND="python -m subprocesses.cartridge_worker"
CARTRIDGE_HOST=localhost
CARTRIDGE_PORT=6379
CARTRIDGE_TIMEOUT_MS=2000
CARTRIDGE_AUTO_SPAWN=true

# Layer 4 (Kobold LLM)
KOBOLD_TYPE=remote
KOBOLD_HOST=localhost
KOBOLD_PORT=5555
KOBOLD_TIMEOUT_MS=5000
KOBOLD_AUTO_SPAWN=false

# Diagnostics
DIAGNOSTIC_LEVEL=info                   # debug, info, warning, error
LOG_TO_REDIS=true
LOG_TO_FILE=false
LOG_FILE=./kitbash.log

# Consensus (Phase 4+)
CONSENSUS_STRATEGY=simple               # simple, weighted, weighted_typed
CONFIDENCE_THRESHOLDS={"layer0": 0.85, "layer1": 0.80, "layer4": 0.5}
```

---

## Docker Setup (Phase 3B)

### docker-compose.yml

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  kitbash:
    build: .
    environment:
      - REDIS_HOST=redis
      - BITNET_HOST=bitnet_worker
      - KOBOLD_HOST=kobold_remote
      - DIAGNOSTIC_LEVEL=info
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./cartridges:/app/cartridges:ro

  bitnet_worker:
    build:
      context: .
      dockerfile: subprocesses/Dockerfile.bitnet
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis

volumes:
  redis_data:
```

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "interfaces.query_repl", "--mode", "redis"]
```

---

## Success Criteria (Phase 3B Complete)

- ✅ Redis Blackboard fully operational
- ✅ Query flow: Layer 0 → Layer 1 → Layer 4 (serial, via Redis)
- ✅ 100+ queries logged with confidence scores and latency
- ✅ Diagnostic events show all routing decisions
- ✅ Subprocess health monitoring working
- ✅ Timeout handling proven (timeout + escalate)
- ✅ REPL works with `--mode direct` (fast testing) and `--mode redis` (realistic)
- ✅ docker-compose.yml spins up complete system
- ✅ All unit and integration tests passing
- ✅ Actual data collection: Layer 0 hit rate, Layer 1 confidence distribution, latencies

---

## Handoff to Phase 3C/4 (What Changes)

### Phase 3C: Async + Consensus (If Data Justifies)

- Same Redis Blackboard (no changes)
- Same worker subprocess template (no changes)
- New: Layer 1 + Layer 2 run **in parallel** via `asyncio.gather()`
- New: Consensus voting when confidence is borderline
- No architectural change, just new execution pattern on same substrate

### Phase 4: Full LLM Integration

- Same orchestrator loop
- New: Layer 4 subprocess for Kobold proxy
- New: NWP axiom validation (response checking)
- No architectural change, just new workers + validation

### Phase 5+: Edge Devices

- Same Redis Blackboard
- New: HTTP proxy server for tiny devices
- New: Device registration mechanism
- No architectural change, just new input source

**Key principle:** Phase 3B is the foundation. Everything after is adding workers and logic on top of the same Redis infrastructure.

---

## Glossary

- **Blackboard:** Shared state (Redis) where all processes read/write
- **Worker/Subprocess:** Stateless process that listens for work on Redis, does computation, writes results back
- **Query ID:** UUID that tracks one complete query through all layers
- **Layer:** Stage of processing (Layer 0 = reflex, Layer 1 = BitNet, Layer 4 = LLM)
- **Pending:** Set of engines still working on a query
- **Diagnostic Event:** Timestamped record of a routing decision (layer hit, timeout, escalation)
- **Orchestrator:** Kitbash core, makes routing decisions
- **Consensus:** Voting logic when multiple engines provide answers
- **Confidence:** Score (0-1) indicating how sure an answer is

---

## Common Implementation Patterns

### Pattern 1: Add New Worker Type

1. Create `subprocesses/new_worker.py` from `bitnet_worker.py` template
2. Implement `load_model()` and `infer()` functions
3. Update env vars: `NEW_WORKER_TYPE`, `NEW_WORKER_TIMEOUT`
4. Update `subprocess_manager.py` to spawn it
5. Update orchestrator routing logic to call it

### Pattern 2: Add New Layer

1. Add case to `query_orchestrator.py` escalation logic
2. Create worker subprocess for that layer
3. Add diagnostics for success/failure
4. Test with mocked subprocess

### Pattern 3: Change Voting Strategy

1. Update `ConsensusEngine.__init__(strategy="weighted")`
2. Implement `_vote_weighted()` method
3. Load model weights from Redis
4. No other code changes needed

### Pattern 4: Monitor Performance

1. Read `diagnostics:{query_id}:events` from Redis
2. Calculate latency from timestamps
3. Aggregate confidence scores
4. Update `metrics:*` keys periodically

---

## Known Limitations (Phase 3B)

1. **No consensus voting yet** - Single best answer per layer (Phase 4)
2. **No query classification** - Can't distinguish simple vs. complex queries (Phase 4)
3. **No weighted voting** - All engines treated equally (Phase 4)
4. **No async parallelization** - Layers run sequentially (Phase 4)
5. **No edge device proxy** - Requires tiny device support (Phase 5+)
6. **No NWP validation** - Responses not checked against axioms (Phase 4+)

These are **not blockers**, just deferred to data-driven later phases.

---

## Quick Start (For Coding Environments)

### For V0 / Claude Code:
1. Read this document completely
2. Start with **"Setup Redis & Config"** section
3. Implement in order: ConfigLoader → Blackboard → DiagnosticFeed → Orchestrator
4. Each component has ~100 lines, clear responsibility
5. Test after each component

### For GitHub Copilot / Other Tools:
1. Paste "Core Components to Implement" section
2. Each component has pseudocode
3. Ask: "Implement RedisBlackboard.set_query_state() according to this spec"
4. Paste test cases from "Testing Strategy"
5. Iterate until tests pass

### For Next Chat (Infrastructure Setup):
1. Paste this document's "Environment Variables" section
2. Task: "Get Redis running, confirm all env vars load correctly"
3. Task: "Implement ConfigLoader and test it with Docker"
4. Task: "Create docker-compose.yml and verify it spins up"

### For Next-Next Chat (Orchestration Implementation):
1. Paste "Core Components to Implement" + "Testing Strategy"
2. Task: "Implement query_orchestrator.py serial loop"
3. Task: "Implement subprocess_manager.py"
4. Task: "Run integration tests, debug until they pass"
5. Task: "Collect 100 queries of data"

---

## Final Notes

- **This is the foundation.** Everything in Phase 4+ builds on this infrastructure without major changes.
- **Keep it simple in Phase 3B.** Serial execution, pure escalation, no fancy consensus logic.
- **Data drives Phase 4 decisions.** After 1000 queries, you'll know what actually helps.
- **Architecture supports all future work.** Edge devices, async parallelization, distributed subprocesses—all designed in from the start, just not implemented yet.
- **Code is more important than perfect design.** If something doesn't fit the architecture, bring it back here and revise. This document is a guide, not gospel.

---

**Version:** 1.0  
**Last Updated:** February 13, 2026  
**Status:** Ready for Implementation  
**Next Phase:** Infrastructure Setup (Redis + Config)  
**Handoff:** See HANDOFF_PROMPT_Infrastructure_Setup.md
