# Kitbash Redis Blackboard Architecture
**Subprocess Orchestration via Redis Message Bus**

---

## Core Concept: Redis as Coordination Substrate

Instead of:
- Direct HTTP calls (point-to-point coupling)
- RPC (blocking, hard to parallelize)
- Queues (one-way, no state sharing)

Use Redis as a **shared blackboard**:
- Kitbash writes query state to Redis
- Subprocesses watch Redis, pick up work
- Subprocesses write results back to Redis
- Kitbash reads results, makes next decision
- All processes see the same evolving state
- Enables serial execution (Kitbash blocks on result) OR async (Kitbash polls multiple queries)

```
┌─────────────────────────────────────────────────────┐
│                   REDIS BLACKBOARD                  │
│                                                     │
│  query:abc123:state = "layer1_request"             │
│  query:abc123:layer1:request = {...}               │
│  query:abc123:pending = ["bitnet", "cartridge"]    │
│                                                     │
│  subprocess:bitnet:alive = true                    │
│  subprocess:bitnet:status = "idle"                 │
│  subprocess:kobold:alive = true                    │
│  subprocess:kobold:status = "processing"           │
│                                                     │
│  diagnostics:abc123 = [...]                       │
└─────────────────────────────────────────────────────┘
     ↑                    ↑                    ↑
     │                    │                    │
  Kitbash            Bitnet Subprocess    Kobold Subprocess
  (Controller)       (Stateless Worker)   (Stateless Worker)
```

---

## Data Model: Redis Keys & Structures

### Query State (Hierarchical)

```python
# Primary query state
query:{query_id}:state = "processing" | "waiting_layer1" | "waiting_layer4" | "complete" | "failed"
query:{query_id}:user_query = "what is ATP?"
query:{query_id}:submitted_at = 1707847200.5

# Layer 0 results (Kitbash writes, everyone reads)
query:{query_id}:layer0:result = {
    "found": true,
    "grain_id": "sg_abc123",
    "fact_id": 42,
    "answer": "ATP is adenosine...",
    "confidence": 0.95,
    "latency_ms": 0.17
}

# Layer 1 request (Kitbash writes, Bitnet subprocess reads)
query:{query_id}:layer1:request = {
    "query": "what is ATP?",
    "context": {...},
    "created_at": 1707847200.52,
    "timeout_ms": 2000
}

# Layer 1 result (Bitnet writes, Kitbash reads)
query:{query_id}:layer1:result = {
    "engine": "bitnet",
    "answer": "ATP is a nucleotide...",
    "confidence": 0.82,
    "latency_ms": 1.8,
    "completed_at": 1707847200.54,
    "facts_used": [45, 67, 89]
}

# Pending work (set of subprocesses waiting)
query:{query_id}:pending = ["bitnet", "cartridge_synthesis"]

# Result aggregation (for consensus/voting)
query:{query_id}:results = {
    "layer0": {...},
    "layer1": {...},
    "layer3": {...}
}

# Final decision
query:{query_id}:final_result = {
    "answer": "...",
    "confidence": 0.88,
    "sources": ["layer1:bitnet", "layer3:cartridge"],
    "method": "consensus|escalate|fallback"
}
```

### Subprocess Management

```python
# Subprocess heartbeat (subprocess sets, Kitbash monitors)
subprocess:{name}:alive = true
subprocess:{name}:pid = 12345
subprocess:{name}:started_at = 1707847100.5
subprocess:{name}:last_heartbeat = 1707847210.2

# Subprocess status
subprocess:{name}:status = "idle" | "processing" | "error"
subprocess:{name}:current_job = "query:abc123:layer1"
subprocess:{name}:load = 0.3  # Current load (0-1)

# Subprocess capabilities (for routing)
subprocess:{name}:capabilities = ["layer1:bitnet", "layer3:cartridge"]

# Subprocess discovery (registered at startup)
subprocesses:available = {
    "bitnet_local": {
        "type": "local",
        "pid": 12345,
        "layers": ["layer1"]
    },
    "kobold_remote": {
        "type": "remote",
        "host": "device_c",
        "port": 5555,
        "layers": ["layer4"]
    }
}
```

### Diagnostic Feed

```python
# Stream of events (append-only, queryable)
diagnostics:{query_id}:events = [
    {
        "timestamp": 1707847200.5,
        "event": "query_received",
        "level": "info"
    },
    {
        "timestamp": 1707847200.51,
        "event": "layer0_attempt",
        "layer": "0",
        "device": "local",
        "level": "debug"
    },
    {
        "timestamp": 1707847200.52,
        "event": "layer0_hit",
        "layer": "0",
        "confidence": 0.95,
        "latency_ms": 0.17,
        "level": "info"
    },
    {
        "timestamp": 1707847200.521,
        "event": "query_complete",
        "final_confidence": 0.95,
        "level": "info"
    }
]

# Metrics aggregation (for monitoring)
metrics:queries:total = 1250
metrics:queries:layer0_hit_rate = 0.78
metrics:subprocess:bitnet:avg_latency_ms = 1.9
metrics:subprocess:kobold:avg_latency_ms = 450
```

---

## Execution Model: Serial First, Async Ready

### Serial Execution (Phase 3B - Today)

```python
def process_query_serial(query_id: str, user_query: str):
    """Kitbash orchestrates synchronously."""
    
    # 1. Initialize query state
    redis.set(f"query:{query_id}:state", "processing")
    redis.set(f"query:{query_id}:user_query", user_query)
    log_diagnostic(query_id, "query_received")
    
    # 2. Try Layer 0 (local, fast)
    layer0_result = layer0_grain_lookup(user_query)
    redis.set(f"query:{query_id}:layer0:result", json.dumps(layer0_result))
    log_diagnostic(query_id, "layer0_complete", latency=layer0_result['latency_ms'])
    
    if layer0_result['confidence'] > 0.85:
        redis.set(f"query:{query_id}:final_result", json.dumps(layer0_result))
        redis.set(f"query:{query_id}:state", "complete")
        return layer0_result
    
    # 3. Layer 1 needed - send to bitnet subprocess
    log_diagnostic(query_id, "layer1_request", engine="bitnet")
    redis.set(f"query:{query_id}:layer1:request", json.dumps({
        "query": user_query,
        "context": {},
        "created_at": time.time(),
        "timeout_ms": 2000
    }))
    redis.sadd(f"query:{query_id}:pending", "bitnet")
    
    # 4. Wait for bitnet result (BLOCKING - serial)
    bitnet_result = wait_for_result(query_id, "bitnet", timeout_ms=2000)
    
    if not bitnet_result:
        log_diagnostic(query_id, "layer1_timeout", engine="bitnet")
        # Handle timeout (escalate or fail gracefully)
    else:
        redis.set(f"query:{query_id}:layer1:result", json.dumps(bitnet_result))
        log_diagnostic(query_id, "layer1_complete", 
                      latency=bitnet_result['latency_ms'],
                      confidence=bitnet_result['confidence'])
        
        if bitnet_result['confidence'] > 0.75:
            redis.set(f"query:{query_id}:final_result", json.dumps(bitnet_result))
            redis.set(f"query:{query_id}:state", "complete")
            return bitnet_result
    
    # 5. Layer 4 last resort - send to kobold
    log_diagnostic(query_id, "layer4_request", engine="kobold")
    redis.set(f"query:{query_id}:layer4:request", json.dumps({...}))
    redis.sadd(f"query:{query_id}:pending", "kobold")
    
    kobold_result = wait_for_result(query_id, "kobold", timeout_ms=5000)
    redis.set(f"query:{query_id}:layer4:result", json.dumps(kobold_result))
    redis.set(f"query:{query_id}:final_result", json.dumps(kobold_result))
    redis.set(f"query:{query_id}:state", "complete")
    
    return kobold_result

def wait_for_result(query_id: str, engine: str, timeout_ms: int) -> Optional[Dict]:
    """Block until engine writes result or timeout."""
    result_key = f"query:{query_id}:{engine_to_layer(engine)}:result"
    
    start = time.time()
    while (time.time() - start) * 1000 < timeout_ms:
        result = redis.get(result_key)
        if result:
            return json.loads(result)
        time.sleep(0.01)  # Poll every 10ms
    
    return None  # Timeout
```

### Subprocess (Bitnet Example)

```python
def bitnet_subprocess_worker():
    """Stateless worker listening to Redis."""
    
    # 1. Register self
    subprocess_name = "bitnet_local"
    redis.set(f"subprocess:{subprocess_name}:alive", "true")
    redis.set(f"subprocess:{subprocess_name}:status", "idle")
    redis.set(f"subprocess:{subprocess_name}:pid", os.getpid())
    
    # 2. Watch for Layer 1 requests
    while True:
        try:
            # Find all pending requests
            pending_queries = redis.keys("query:*:pending")
            
            for pending_key in pending_queries:
                query_id = pending_key.split(":")[1]
                pending_engines = redis.smembers(f"query:{query_id}:pending")
                
                if "bitnet" in pending_engines:
                    # Claim this work
                    redis.set(f"subprocess:{subprocess_name}:status", "processing")
                    redis.set(f"subprocess:{subprocess_name}:current_job", 
                             f"query:{query_id}:layer1")
                    
                    # Get request details
                    request = json.loads(
                        redis.get(f"query:{query_id}:layer1:request")
                    )
                    
                    # Do the work
                    start = time.time()
                    result = run_bitnet_inference(request['query'])
                    latency_ms = (time.time() - start) * 1000
                    
                    # Write result
                    redis.set(f"query:{query_id}:layer1:result", json.dumps({
                        "engine": "bitnet",
                        "answer": result['text'],
                        "confidence": result['confidence'],
                        "latency_ms": latency_ms,
                        "completed_at": time.time()
                    }))
                    
                    # Remove from pending
                    redis.srem(f"query:{query_id}:pending", "bitnet")
                    
                    # Update metrics
                    redis.incr(f"metrics:subprocess:bitnet:requests")
                    redis.lpush(f"metrics:subprocess:bitnet:latencies", latency_ms)
                    
                    # Return to idle
                    redis.set(f"subprocess:{subprocess_name}:status", "idle")
                    redis.delete(f"subprocess:{subprocess_name}:current_job")
            
            time.sleep(0.1)  # Poll every 100ms
        
        except Exception as e:
            log_error(f"Bitnet subprocess error: {e}")
            redis.set(f"subprocess:{subprocess_name}:status", "error")
            time.sleep(1)  # Back off before retry
```

### Async Execution (Phase 4 - Later, No Code Changes)

```python
async def process_query_async(query_id: str, user_query: str):
    """Kitbash orchestrates multiple subprocesses in parallel."""
    
    # Same setup as serial...
    redis.set(f"query:{query_id}:state", "processing")
    
    # Layer 0 (local)
    layer0_result = layer0_grain_lookup(user_query)
    if layer0_result['confidence'] > 0.85:
        return layer0_result
    
    # Layer 1: Send to MULTIPLE engines in parallel
    # (bitnet AND cartridge synthesis simultaneously)
    tasks = [
        send_to_engine(query_id, "bitnet"),
        send_to_engine(query_id, "cartridge"),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Consensus voting on results
    valid_results = [r for r in results if not isinstance(r, Exception)]
    final = consensus(valid_results)
    
    redis.set(f"query:{query_id}:final_result", json.dumps(final))
    return final

async def send_to_engine(query_id: str, engine: str):
    """Async wait for subprocess result."""
    redis.sadd(f"query:{query_id}:pending", engine)
    
    result_key = f"query:{query_id}:{engine_to_layer(engine)}:result"
    start = time.time()
    
    while (time.time() - start) < 2.0:  # 2s timeout
        result = redis.get(result_key)
        if result:
            return json.loads(result)
        await asyncio.sleep(0.01)
    
    raise TimeoutError(f"{engine} did not respond in time")
```

**Key point:** Serial and async use the same Redis substrate. No architectural change needed—just add asyncio.gather() and you get parallelism.

---

## Subprocess Discovery & Lifecycle

### Environment-Based Config (Containerization-Ready, Phase 3B)

```python
# Load from environment variables (Docker/K8s friendly)
import os

SUBPROCESS_CONFIG = {
    'bitnet_local': {
        'type': os.getenv('BITNET_TYPE', 'local'),
        'command': os.getenv('BITNET_COMMAND', 'python -m bitnet_worker'),
        'host': os.getenv('BITNET_HOST', 'localhost'),
        'port': int(os.getenv('BITNET_PORT', '6379')),
        'layers': ['layer1'],
        'auto_spawn': os.getenv('BITNET_AUTO_SPAWN', 'true').lower() == 'true',
        'timeout_ms': int(os.getenv('BITNET_TIMEOUT', '2000')),
    },
    'cartridge_local': {
        'type': os.getenv('CARTRIDGE_TYPE', 'local'),
        'command': os.getenv('CARTRIDGE_COMMAND', 'python -m cartridge_worker'),
        'host': os.getenv('CARTRIDGE_HOST', 'localhost'),
        'port': int(os.getenv('CARTRIDGE_PORT', '6379')),
        'layers': ['layer2', 'layer3'],
        'auto_spawn': os.getenv('CARTRIDGE_AUTO_SPAWN', 'true').lower() == 'true',
        'timeout_ms': int(os.getenv('CARTRIDGE_TIMEOUT', '2000')),
    },
    'kobold_remote': {
        'type': os.getenv('KOBOLD_TYPE', 'remote'),
        'host': os.getenv('KOBOLD_HOST', 'localhost'),
        'port': int(os.getenv('KOBOLD_PORT', '5555')),
        'layers': ['layer4'],
        'auto_spawn': False,
        'timeout_ms': int(os.getenv('KOBOLD_TIMEOUT', '5000')),
    }
}

# Example Docker Compose setup:
# services:
#   kitbash:
#     environment:
#       - BITNET_HOST=bitnet_worker
#       - BITNET_PORT=6379
#       - KOBOLD_HOST=kobold_remote
#       - KOBOLD_PORT=5555
#   bitnet_worker:
#     image: kitbash/bitnet:latest
#     environment:
#       - REDIS_HOST=redis
#   kobold_remote:
#     image: oobabooga/text-generation-webui:latest
#     ports:
#       - "5555:5555"
#   redis:
#     image: redis:7-alpine
```

### YAML Fallback (For Non-Containerized Setups)

```python
# Still support YAML for local development
import yaml

def load_config(config_path: str = None):
    """Load from env vars first, YAML as fallback."""
    
    # If running in container, env vars set by docker-compose
    if os.getenv('BITNET_HOST'):
        return SUBPROCESS_CONFIG
    
    # Fallback to YAML for local development
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)['subprocesses']
    
    # Default: all local
    return SUBPROCESS_CONFIG
```

### Dynamic Registration (Advanced, Phase 4+)

```python
# Subprocesses self-register at startup
class SubprocessManager:
    def register_subprocess(self, name: str, config: Dict):
        redis.hset(f"subprocesses:registry", name, json.dumps(config))
        redis.set(f"subprocess:{name}:alive", "true")
        redis.set(f"subprocess:{name}:status", "idle")
    
    def list_available(self) -> Dict[str, Dict]:
        """Get all registered subprocesses."""
        return {
            name: json.loads(config)
            for name, config in redis.hgetall(f"subprocesses:registry").items()
        }
```

### Lifecycle Management

```python
class SubprocessManager:
    def __init__(self, config: Dict):
        self.config = config
        self.subprocesses = {}  # {name: process}
    
    def ensure_subprocess(self, name: str):
        """Start subprocess if not running."""
        if name in self.subprocesses and self.subprocesses[name].poll() is None:
            return  # Already running
        
        spec = self.config['subprocesses'][name]
        
        if spec['type'] == 'local':
            # Spawn locally
            proc = subprocess.Popen(spec['command'].split())
            self.subprocesses[name] = proc
            redis.set(f"subprocess:{name}:pid", proc.pid)
            redis.set(f"subprocess:{name}:alive", "true")
            
            log_diagnostic("system", f"Spawned subprocess {name} (PID {proc.pid})")
        
        elif spec['type'] == 'remote':
            # Assume already running on Device B, just mark as available
            redis.set(f"subprocess:{name}:alive", "true")
    
    def health_check(self):
        """Monitor subprocess health, restart if dead."""
        for name in self.config['subprocesses'].keys():
            alive = redis.get(f"subprocess:{name}:alive")
            
            if name in self.subprocesses:
                # Local subprocess
                if self.subprocesses[name].poll() is not None:
                    # Crashed, restart if auto_spawn
                    if self.config['subprocesses'][name].get('auto_spawn'):
                        log_diagnostic("system", f"Subprocess {name} crashed, restarting")
                        self.ensure_subprocess(name)
                    else:
                        redis.set(f"subprocess:{name}:alive", "false")
            
            else:
                # Remote subprocess
                if not alive:
                    log_diagnostic("system", f"Remote subprocess {name} unavailable")
    
    def handle_subprocess_death(self, name: str):
        """Gracefully handle subprocess failure."""
        redis.set(f"subprocess:{name}:alive", "false")
        redis.set(f"subprocess:{name}:status", "dead")
        
        # Find all queries waiting for this subprocess
        pending_queries = redis.keys(f"query:*:pending")
        for pending_key in pending_queries:
            query_id = pending_key.split(":")[1]
            if redis.sismember(f"query:{query_id}:pending", name):
                # This query was waiting for dead subprocess
                log_diagnostic(query_id, f"subprocess_failure", engine=name)
                redis.srem(f"query:{query_id}:pending", name)
                # Kitbash will handle escalation on next check
```

---

## Small-Device Proxy API (Microservice Devices)

For devices too small to run Redis client (edge devices, embedded):

```python
# kitbash_proxy_server.py
# Runs on device with Redis access, exposes HTTP for edge devices
from fastapi import FastAPI, Request
import redis
import json

app = FastAPI()
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379)

@app.post("/submit_work")
async def submit_work(request: Request):
    """Edge device submits work to Redis blackboard."""
    data = await request.json()
    
    query_id = data['query_id']
    engine = data['engine']
    layer = data['layer']
    payload = data['payload']
    
    # Write to Redis as if subprocess submitted it
    redis_client.set(
        f"query:{query_id}:{layer}:result",
        json.dumps({
            "engine": engine,
            "answer": payload['answer'],
            "confidence": payload['confidence'],
            "latency_ms": payload['latency_ms'],
            "completed_at": time.time()
        })
    )
    
    redis_client.srem(f"query:{query_id}:pending", engine)
    
    return {"status": "ok"}

@app.get("/get_work")
async def get_work(device_id: str):
    """Edge device polls for work assigned to it."""
    
    # Find pending queries looking for this device
    pending_queries = redis_client.keys("query:*:pending")
    
    for pending_key in pending_queries:
        query_id = pending_key.split(":")[1]
        pending_engines = redis_client.smembers(f"query:{query_id}:pending")
        
        if device_id in pending_engines:
            # Found work for this device
            request_key = f"query:{query_id}:{engine_to_layer(device_id)}:request"
            request = json.loads(redis_client.get(request_key))
            
            return {
                "query_id": query_id,
                "device": device_id,
                "request": request,
                "timeout_ms": 2000
            }
    
    return {"status": "no_work"}

# Usage from edge device (e.g., Raspberry Pi):
# 1. Poll: GET /get_work?device_id=edge_model_1
# 2. Do work locally
# 3. Submit: POST /submit_work with results
# 4. Go back to step 1
```

**Benefits:**
- Edge devices don't need Redis or complex networking
- Just HTTP POST/GET
- Proxy handles all Blackboard interactions
- Works on tiny devices (WiFi + basic HTTP)

---

## Consensus & Aggregation Decision Logic

**Key question:** When should low-confidence results trigger consensus vs. escalation?

```python
def consensus(results: List[Dict]) -> Dict:
    """Average confidence, pick most common answer."""
    
    answers = [r['answer'] for r in results]
    confidences = [r['confidence'] for r in results]
    
    avg_confidence = sum(confidences) / len(confidences)
    most_common_answer = mode(answers)  # Most agreed-upon
    
    return {
        "answer": most_common_answer,
        "confidence": avg_confidence,
        "method": "consensus",
        "sources": [r['engine'] for r in results],
        "individual_confidences": {r['engine']: r['confidence'] for r in results}
    }
```

---

## Subprocess Discovery: Best Fit

Given your architecture, **Static Config + Dynamic Discovery** hybrid:

### Phase 3B: Static YAML
- Simple, predictable
- No service registry overhead
- Subprocesses listed in `kitbash_config.yaml`

### Phase 4+: Add Dynamic Registration
- Subprocesses self-register on startup
- Kitbash discovers via Redis
- Enables ad-hoc scaling (add new worker, it auto-registers)

```python
# Hybrid approach
class SubprocessManager:
    def __init__(self, config_path: str):
        # Load static config
        self.config = load_yaml(config_path)
        
        # But also check Redis for dynamic registrations
        self.dynamic = redis.hgetall("subprocesses:registry")
    
    def list_available(self) -> Dict:
        """Return static + dynamic subprocesses."""
        return {**self.config['subprocesses'], **self.dynamic}
```

---

## Failure Mode Details

### Graceful Degradation Chain

```python
async def route_query_with_fallback(query_id: str, user_query: str):
    """Try layers in sequence, gracefully degrade."""
    
    # Layer 0: Fast, local, can't fail
    l0 = layer0_grain_lookup(user_query)
    if l0['confidence'] > 0.85:
        return l0
    
    # Layer 1: Bitnet (2s timeout)
    try:
        l1 = await get_result_or_timeout(query_id, "bitnet", timeout=2.0)
        
        if l1['confidence'] > 0.75:
            return l1  # Good enough
        
        # Low confidence Layer 1, need second opinion
        if should_get_consensus(user_query):
            # Spawn cartridge synthesis in parallel
            l2 = await get_result_or_timeout(query_id, "cartridge", timeout=2.0)
            return consensus([l1, l2])
        
    except TimeoutError:
        log_diagnostic(query_id, "layer1_timeout")
        # Fall through to Layer 4
    except SubprocessDeadError:
        log_diagnostic(query_id, "subprocess_dead", engine="bitnet")
        # Fall through to Layer 4
    
    # Layer 4: Full LLM (5s timeout, last resort)
    try:
        l4 = await get_result_or_timeout(query_id, "kobold", timeout=5.0)
        return l4
    
    except TimeoutError:
        log_diagnostic(query_id, "layer4_timeout", level="warning")
        return {
            "answer": "I'm having trouble processing this query. Could you rephrase or ask the user for clarification?",
            "confidence": 0.0,
            "method": "fallback",
            "reason": "all_layers_timeout"
        }
```

### Subprocess Restart on Failure

```python
def handle_subprocess_crash(name: str, query_id: str):
    """Subprocess died mid-query."""
    
    redis.set(f"subprocess:{name}:alive", "false")
    log_diagnostic(query_id, "subprocess_crash", engine=name)
    
    # Try to restart (if auto_spawn enabled)
    if self.config['subprocesses'][name].get('auto_spawn'):
        try:
            self.ensure_subprocess(name)
            log_diagnostic("system", f"Restarted subprocess {name}")
            
            # Retry the query
            return await get_result_or_timeout(query_id, name, timeout=2.0)
        
        except Exception as e:
            log_diagnostic(query_id, "subprocess_restart_failed", engine=name, error=str(e))
            # Give up, escalate
            return None
    
    return None  # Escalate to next layer
```

---

## Low-Confidence Consensus Logic

Depends on query and layer:

```python
def should_get_consensus(query: str, current_confidence: float) -> bool:
    """Decide if we need a second opinion."""
    
    # Always get consensus for complex queries
    if is_complex_query(query):
        return current_confidence < 0.90
    
    # For simple queries, only if confidence is borderline
    if current_confidence > 0.80:
        return False  # Single source acceptable
    
    if current_confidence < 0.70:
        return True  # Definitely need consensus
    
    # Borderline (0.70-0.80): check sources
    # If we have time, get second opinion
    return True
```

---

## File Structure

```
kitbash/
├── core/
│   ├── grain_router.py
│   ├── layer0_query_processor.py
│   ├── query_orchestrator.py        (NEW - main serial loop)
│   └── subprocess_manager.py         (NEW - lifecycle + discovery)
├── redis/
│   ├── blackboard.py                (NEW - Redis key management)
│   ├── diagnostic_feed.py            (NEW - event logging to Redis)
│   └── consensus.py                  (NEW - result aggregation)
├── subprocesses/
│   ├── bitnet_worker.py              (NEW - listens to Redis)
│   ├── cartridge_worker.py           (NEW - listens to Redis)
│   └── kobold_worker.py              (NEW - remote, listens to Redis)
├── config/
│   └── kitbash_config.yaml           (NEW - subprocess manifest)
└── cartridges/
    ├── physics/
    ├── chemistry/
    └── ...
```

---

## Testing Strategy

### Unit Tests
- Blackboard key patterns (no collision)
- Diagnostic event logging
- Consensus voting logic
- Timeout handling

### Integration Tests (Serial)
- Full query flow with mocked subprocesses
- Subprocess restart on crash
- Timeout escalation
- Multi-layer orchestration

### Integration Tests (Async)
- Parallel subprocess requests
- Consensus aggregation
- Timeout races
- Handle partial failures

### Multi-Device Tests (Phase 4)
- Subprocess on different machines
- Network latency simulation
- Subprocess discovery/registration
- Failure + recovery

---

## Migration Path: Serial → Async

1. **Phase 3B:** All code uses Redis Blackboard, but Kitbash calls `wait_for_result()` synchronously
2. **Phase 4:** Add asyncio, change `wait_for_result()` → `await send_to_engine()`, wrap in `asyncio.gather()`
3. **Result:** Same Redis substrate, subprocesses unchanged, Kitbash just gets parallelism

---

## Next Steps

1. **Implement Redis schema** (keys, patterns, data structures)
2. **Implement `blackboard.py`** (get/set helpers)
3. **Implement `query_orchestrator.py`** (serial execution loop)
4. **Implement `subprocess_manager.py`** (lifecycle management)
5. **Create `bitnet_worker.py`** stub (listens, returns mock results)
6. **Create `kitbash_config.yaml`** (manifest)
7. **Test with mocked subprocesses** (validate serial flow)
8. **Add async layer** (Phase 4)

---

**This architecture enables:**
- ✅ Serial execution today
- ✅ Async parallelization later (no redesign)
- ✅ Graceful subprocess failure handling
- ✅ Consensus voting on results
- ✅ End-to-end query tracing
- ✅ Subprocess auto-restart
- ✅ Works locally OR across network (same code)
- ✅ Extensible for new layers/engines
