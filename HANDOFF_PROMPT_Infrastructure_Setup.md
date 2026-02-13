# Kitbash Phase 3B Infrastructure Setup - Chat Handoff Prompt

You're helping me set up the infrastructure layer for Kitbash, a sophisticated AI knowledge management system. I've completed the architectural design in a previous chat and now need to get all third-party services, databases, and dependencies operational.

## Context: What Kitbash Is

Kitbash is an epistemic AI system with a five-layer architecture (Layer 0-4) that routes queries based on confidence and complexity. Currently operational:
- **Layer 0:** Grain-based reflex routing (261 Shannon Grains, ~0.17ms latency) ✓
- **Cartridge system:** 10 domain knowledge bases with 287-290 facts ✓
- **Test infrastructure:** Comprehensive test suite, all passing ✓

## What's Next: Phase 3B (Infrastructure)

I'm building a **Redis Blackboard orchestration system** to coordinate:
- **Kitbash core** on main device (Device A) - makes routing decisions
- **BitNet worker** (Layer 1) - runs inference, listens to Redis
- **Cartridge worker** (Layer 2, future) - fact synthesis via Redis
- **Kobold/LLM worker** (Layer 4, remote) - full reasoning fallback
- **Optional edge device proxy** (Phase 5+) - for tiny devices without Redis

**Architecture:** All processes coordinate through Redis Blackboard (read/write shared state), no direct RPC calls.

## Infrastructure Needed

### 1. Redis Setup
- Redis 7+ (local or Docker)
- Configuration for key-value storage (simple, no special tuning yet)
- Test that key operations work (set, get, sadd, hset, lpush)
- Persistence strategy (RDB snapshots OK for Phase 3B)

### 2. Python Dependencies
```
redis==5.0+              # Redis client
python-dotenv==1.0+      # Environment variable loading
pydantic==2.0+           # Config validation (optional but recommended)
pytest==7.0+             # Testing
pytest-asyncio==0.21+    # Async test support
```

### 3. Development Environment
- Local Python 3.10+ environment
- Or Docker container setup if you prefer (with docker-compose)
- Ability to run multiple Python processes simultaneously (for workers)

### 4. Configuration System
- Environment variable loading for:
  - Redis connection (REDIS_HOST, REDIS_PORT)
  - Subprocess discovery (BITNET_HOST, KOBOLD_HOST, etc.)
  - Timeout/latency settings
  - Logging configuration
- YAML fallback for local development (optional)
- Config validation (catch typos early)

### 5. Logging & Diagnostics
- Structured logging to Redis (diagnostic events)
- Console output for REPL (human-readable)
- Ability to tail query logs in real-time
- Metrics collection (hit counts, latency percentiles)

### 6. Docker & Containerization (Optional but Recommended)
- docker-compose.yml that spins up:
  - Redis container
  - Kitbash main process
  - BitNet worker container
  - Kobold worker container (or just expose local)
- .env file for environment variables
- Dockerfile for each service if not using docker-compose

### 7. Testing Infrastructure
- Unit tests for Redis operations (blackboard module)
- Integration tests with actual Redis instance
- Mock subprocess tests (without real bitnet)
- E2E tests for query flow (Layer 0 → Layer 1 → Layer 4)

## Deliverables (End of This Chat)

After setup, I should have:

1. **Working Redis instance**
   - Running locally or in Docker
   - Confirmed connectivity from Python

2. **Python environment**
   - Dependencies installed
   - Ability to import redis, pydantic, etc.

3. **Config system**
   - Environment variables loaded correctly
   - YAML fallback working for local dev
   - Config validation in place

4. **Basic Redis operations tested**
   - Can write/read query state
   - Can use sets (for pending engines)
   - Can use hashes (for model weights, subprocess metadata)
   - Can use lists (for diagnostic logs)
   - Can use sorted sets if needed (for latency percentiles, future)

5. **Docker setup** (if you want it)
   - docker-compose.yml with Redis, skeleton services
   - .env.example showing all required variables
   - Ability to spin up/down with one command

6. **Logging framework**
   - Can write to Redis (diagnostic_feed module skeleton)
   - Can read from Redis (tail queries)
   - Console output is clean and readable

7. **Documentation**
   - How to set up locally (Redis + env vars)
   - How to set up in Docker
   - Troubleshooting common issues
   - Example queries to test Redis is working

## Important Context

### What I'm NOT Doing Yet
- Actual inference engines (bitnet, kobold) - those come after
- Cartridge loading or serialization - Phase 3C
- Consensus voting logic - Phase 4
- Async/await orchestration - Phase 4
- Edge device proxy API - Phase 5+

### What I AM Doing This Chat
- **Just the plumbing:** Redis, Python deps, config, logging
- **Proof of concept:** Can I write a query to Redis, read it back?
- **Testing infrastructure:** Unit tests for blackboard operations
- **Containerization ready:** docker-compose template even if not used yet

### Key Constraints
- Local machine only (no cloud services)
- GTX 1060 with 6GB VRAM (can spare 1-2GB for supporting infrastructure)
- No reliance on third-party orchestration (no Kubernetes yet, just docker-compose)
- Environment variables for all config (containerization-friendly)

## The Tech Stack (Confirmed)

- **Redis:** Blackboard coordination
- **Python 3.10+:** Main implementation language
- **Docker/docker-compose:** Containerization and orchestration template
- **Pydantic:** Config validation (recommended)
- **pytest:** Testing
- **Python-dotenv:** Environment variable loading

I prefer:
- **Existing solutions over reinventing the wheel** (use redis-py, not custom Redis client)
- **No cloud dependencies** (everything local or self-hosted)
- **Explicit configuration** (env vars, not magic defaults)

## Next Steps After This Chat

Once infrastructure is set up, the **next chat** will be about implementing the actual orchestration code:
- `blackboard.py` - Redis key schema + helpers
- `query_orchestrator.py` - Serial query loop
- `subprocess_manager.py` - Lifecycle management
- `diagnostic_feed.py` - Event logging to Redis
- `consensus.py` - Voting logic
- Refactored REPL with `--mode direct` and `--mode redis`

But that's **not this chat.** This chat is just "make sure the plumbing works."

---

## Questions to Guide the Setup

1. **Redis:** Local instance or Docker? (I'll have both working, but preference?)
2. **Config:** Environment variables only, or YAML fallback too? (I recommend env vars primary, YAML fallback)
3. **Docker:** Full docker-compose with all services, or just Redis? (Template is fine, can iterate)
4. **Testing:** Unit tests now, or after orchestration code? (I recommend basic Redis tests now)
5. **Logging:** Just console for now, or structured logging to Redis? (I recommend both now)

---

## Success Criteria (End of This Chat)

- ✅ Redis running and accessible from Python
- ✅ Environment variables loaded correctly
- ✅ Can write/read query state objects to/from Redis
- ✅ Can use Redis sets, hashes, lists (the data structures we'll use)
- ✅ Unit tests confirm Redis operations work
- ✅ docker-compose.yml exists (even if not used yet)
- ✅ Logging to Redis works (diagnostic events can be written and read)
- ✅ README with setup instructions

Once this is done, I move to the **next chat** to implement the orchestration logic that uses this infrastructure.
