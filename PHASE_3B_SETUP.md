# Kitbash Phase 3B Infrastructure Setup Guide

This document covers setting up the Redis blackboard infrastructure for Kitbash Phase 3B orchestration.

**Status**: ✅ Infrastructure ready for testing
**Phase**: 3B (Infrastructure layer)
**Next Phase**: 3B Orchestration implementation

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all Phase 3B dependencies
pip install -r requirements.txt
```

**Installed packages**:
- `redis==5.0.1` - Redis client library
- `python-dotenv==1.0.0` - Environment variable loading
- `pydantic==2.5.2` - Configuration validation
- `PyYAML==6.0.1` - YAML configuration parsing
- `pytest==7.4.3` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support

### 2. Start Redis (Local Instance)

**Option A: Via Homebrew (macOS)**
```bash
brew install redis
brew services start redis
```

**Option B: Via Package Manager (Linux)**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Fedora/CentOS
sudo dnf install redis
sudo systemctl start redis
```

**Option C: Via Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name kitbash_redis redis:7-alpine
```

**Verify Redis is running**:
```bash
redis-cli ping
# Output: PONG
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional, defaults are fine for local dev)
# Important variables:
#   REDIS_HOST=localhost
#   REDIS_PORT=6379
#   KITBASH_ENVIRONMENT=development
#   KITBASH_LOG_LEVEL=DEBUG
```

The configuration system loads in this order:
1. Environment variables (from .env or shell)
2. YAML file (kitbash_config.yaml)
3. Pydantic defaults

### 4. Test the Setup

```bash
# Test Redis connection
python redis_blackboard.py

# Output:
# ✅ All blackboard tests passed!

# Test configuration loading
python config.py

# Output:
# Configuration loaded successfully!
# Redis: localhost:6379
# Environment: development
# Layers: dict_keys(['layer0', 'layer1', 'layer2', 'layer3', 'layer4'])

# Test diagnostic feed
python diagnostic_feed.py

# Output:
# ✅ All diagnostic feed tests passed!

# Run full unit test suite
pytest test_redis_operations.py -v

# Output:
# test_redis_operations.py::TestRedisConnection::test_redis_connection PASSED
# test_redis_operations.py::TestRedisBlackboard::test_query_creation PASSED
# ... [15+ tests total]
# ✅ All tests passed!
```

## Configuration Files

### .env File
Environment variables that override defaults:
- `REDIS_HOST`, `REDIS_PORT` - Redis connection
- `KITBASH_ENVIRONMENT` - development/staging/production
- `LAYER*_TIMEOUT_MS` - Timeout for each layer
- `BITNET_HOST`, `CARTRIDGE_HOST`, `KOBOLD_HOST` - Worker locations

See `.env.example` for complete list.

### kitbash_config.yaml
YAML defaults for local development (overridden by .env):
- Redis connection settings
- Layer timeout and enable/disable
- Worker configuration
- Diagnostics and performance tuning
- Redis key namespace

### config.py
Configuration loader that:
- Reads YAML file
- Overrides with environment variables
- Validates with Pydantic
- Provides typed config objects

**Usage**:
```python
from config import get_config

config = get_config()
redis_config = config.redis_config()
print(f"Redis: {redis_config.host}:{redis_config.port}")
```

## Core Infrastructure Modules

### redis_blackboard.py
Abstraction layer for all Redis operations:
- Query state management (create, update, retrieve)
- Query queue operations (enqueue, dequeue)
- Grain storage and retrieval
- Diagnostic event logging
- Worker health tracking
- Metrics collection

**Usage**:
```python
from redis_blackboard import RedisBlackboard

bb = RedisBlackboard()

# Create query
bb.create_query("q_001", "What is AI?")

# Update status
bb.update_query_status("q_001", "layer0_hit", {"confidence": 0.99})

# Enqueue for processing
bb.enqueue_query("q_001")

# Process queue
query_id = bb.dequeue_query()
```

### diagnostic_feed.py
Structured logging to Redis:
- Query lifecycle events (created, started, completed)
- Layer processing events (attempt, hit, miss, timeout)
- Escalation events
- Worker health updates
- Metrics recording

**Usage**:
```python
from diagnostic_feed import DiagnosticFeed

feed = DiagnosticFeed()

# Log events
feed.log_query_created("q_001", "What is AI?")
feed.log_layer_hit("q_001", "layer0", 0.99, 0.17)
feed.log_query_completed("q_001", "layer0", 0.99, 0.17)

# Retrieve timeline
timeline = feed.get_query_timeline("q_001")
for event in timeline:
    print(f"{event['timestamp']}: {event['event_type']}")

# Get statistics
stats = feed.get_query_statistics("q_001")
print(f"Total latency: {stats['total_latency_ms']}ms")
```

### config.py
Configuration management:
- Pydantic models for all config sections
- Environment variable overrides
- YAML fallback for local development
- Validation and defaults

**Usage**:
```python
from config import ConfigLoader, setup_logging

loader = ConfigLoader()
config = loader.get()

setup_logging(config)

# Access configuration
print(f"Redis: {config.redis.host}:{config.redis.port}")
print(f"Layer 0 timeout: {config.layers['layer0'].timeout_ms}ms")
```

## Unit Tests

Run tests to validate infrastructure:

```bash
# Run all tests with verbose output
pytest test_redis_operations.py -v

# Run specific test class
pytest test_redis_operations.py::TestRedisBlackboard -v

# Run with coverage report
pytest test_redis_operations.py --cov=redis_blackboard --cov=diagnostic_feed

# Run in watch mode (requires pytest-watch)
ptw test_redis_operations.py
```

**Test Coverage**:
- ✅ Redis connection and basic operations
- ✅ Query state management (CRUD)
- ✅ Query queue operations
- ✅ Grain storage and retrieval
- ✅ Diagnostic event logging
- ✅ Layer and query statistics
- ✅ Worker health tracking
- ✅ Metrics collection
- ✅ Configuration loading and validation
- ✅ Full end-to-end query flow

## Docker Setup (Full Containerization)

### Quick Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services in docker-compose.yml

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| redis | 6379 | Blackboard coordination | Active |
| kitbash_core | - | Main orchestrator | Skeleton |
| bitnet_worker | 5001 | Layer 1 inference | Skeleton |
| cartridge_worker | 5002 | Layer 2 facts | Skeleton |
| kobold_worker | 5003 | Layer 4 LLM | Optional profile |

### Start with Docker Compose

```bash
# Core services (redis + kitbash + workers)
docker-compose up -d

# With Kobold LLM support
docker-compose --profile kobold up -d

# Scale BitNet workers
docker-compose up -d --scale bitnet_worker=3
```

### Access Redis from Container

```bash
# Shell into Redis
docker-compose exec redis redis-cli

# Monitor all commands
docker-compose exec redis redis-cli MONITOR

# Check database size
docker-compose exec redis redis-cli DBSIZE
```

### Check Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f kitbash_core
docker-compose logs -f bitnet_worker

# Last 50 lines
docker-compose logs --tail=50 redis
```

### Docker Images

Dockerfiles provided:
- `Dockerfile.kitbash` - Main orchestrator process
- `Dockerfile.worker` - Worker service template

Build custom images:
```bash
docker build -f Dockerfile.kitbash -t kitbash:core .
docker build -f Dockerfile.worker -t kitbash:worker --build-arg WORKER_TYPE=bitnet .
```

## Troubleshooting

### Redis Connection Failed

```
Error: [Errno 111] Connection refused
```

**Solutions**:
1. Verify Redis is running: `redis-cli ping`
2. Check host/port in .env: `REDIS_HOST=localhost REDIS_PORT=6379`
3. Try local Redis: `docker run -p 6379:6379 redis:7-alpine`
4. Check firewall: `sudo ufw allow 6379`

### Configuration Not Loading

```
Warning: Config file not found at ./kitbash_config.yaml
```

**Solutions**:
1. Ensure `kitbash_config.yaml` exists in working directory
2. Set `KITBASH_CONFIG_PATH=/path/to/config.yaml` in .env
3. Check YAML syntax: `python -m yaml kitbash_config.yaml`

### Pydantic Validation Error

```
pydantic_core._pydantic_core.ValidationError: ...
```

**Solutions**:
1. Check .env variables have correct types (port must be int)
2. Validate YAML syntax: `yamllint kitbash_config.yaml`
3. Check threshold values are 0.0-1.0

### Tests Failing

```
FAILED test_redis_operations.py::TestRedisConnection::test_redis_connection
```

**Solutions**:
1. Start Redis: `docker run -p 6379:6379 redis:7-alpine`
2. Verify connectivity: `redis-cli ping`
3. Check .env has correct Redis settings
4. Run tests with logging: `pytest test_redis_operations.py -v -s`

## Performance Tuning

### Redis Configuration

For local development (current), defaults are fine. For production:

```bash
# Persistence (RDB snapshots)
redis-server --appendonly yes --save 60 1000

# Memory limits
redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### Kitbash Configuration

Edit `kitbash_config.yaml`:

```yaml
performance:
  grain_cache_size: 1000        # Increase for hot queries
  cartridge_cache_size: 100     # Increase if many facts
  escalation_confidence_threshold: 0.60  # Raise to escalate less
```

Or via environment:
```bash
export LAYER0_TIMEOUT_MS=5
export LAYER1_TIMEOUT_MS=8
```

## Next Steps (Phase 3B Orchestration)

Once infrastructure is validated, next chat will implement:

1. **blackboard.py** - Redis key schema helpers
2. **query_orchestrator.py** - Serial query routing loop
3. **subprocess_manager.py** - Worker lifecycle management
4. **consensus.py** - Multi-worker result voting
5. **Refactored REPL** - Direct and Redis modes

Current state:
- ✅ Redis setup (local or Docker)
- ✅ Configuration system (env vars + YAML)
- ✅ Query state management (blackboard)
- ✅ Diagnostic logging (events + statistics)
- ✅ Unit tests for all infrastructure
- ✅ Docker containerization ready

Not yet implemented (Phase 3C+):
- Actual BitNet worker integration
- Cartridge worker integration
- KoboldCpp LLM integration
- Async orchestration (Phase 3C)
- Consensus voting (Phase 4)
- Edge device proxy (Phase 5+)

## Development Tips

### Interactive Testing

```bash
# Test Redis operations
python -i redis_blackboard.py
>>> bb.create_query("q1", "test")
>>> print(bb.get_query("q1"))

# Test diagnostics
python -i diagnostic_feed.py
>>> feed.log_query_created("q1", "test")
>>> print(feed.get_query_timeline("q1"))

# Test configuration
python -i config.py
>>> loader = ConfigLoader()
>>> config = loader.get()
>>> print(config.redis.host)
```

### Monitor Redis in Real-Time

```bash
# Terminal 1: Start Redis monitor
docker exec kitbash_redis redis-cli MONITOR

# Terminal 2: Run tests in another window
pytest test_redis_operations.py -v -s
```

### Debug Logging

```bash
# Set log level
export KITBASH_LOG_LEVEL=DEBUG

# Run tests with full output
pytest test_redis_operations.py -v -s --log-cli-level=DEBUG
```

## Summary

You now have:
- ✅ **Redis** running locally or in Docker
- ✅ **Configuration system** with env vars + YAML fallback
- ✅ **Query management** via RedisBlackboard
- ✅ **Diagnostic logging** with statistics
- ✅ **Unit tests** validating all components
- ✅ **Docker setup** ready for containerization

This infrastructure is ready for Phase 3B orchestration implementation in the next chat.

**Success criteria (all validated)**:
- ✅ Redis running and accessible
- ✅ Environment variables loaded
- ✅ Can write/read query state to Redis
- ✅ Redis data structures working (sets, hashes, lists)
- ✅ Unit tests passing
- ✅ Docker compose setup ready
- ✅ Diagnostic logging working
- ✅ Configuration validated

Next: Implement `query_orchestrator.py`, `subprocess_manager.py`, and other orchestration logic.
