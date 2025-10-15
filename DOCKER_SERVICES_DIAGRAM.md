# Docker Services Architecture

## Complete Service Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MARCUS E-COMMERCE                            │
│                     Docker Compose Stack                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│     WEB      │         │    CELERY    │         │ CELERY-BEAT  │
│  (Django)    │         │   (Worker)   │         │ (Scheduler)  │
│              │         │              │         │              │
│ Port: 8000   │         │ Processes:   │         │ Schedules:   │
│              │         │ - AI index   │         │ - Nightly    │
│ Volumes:     │         │   updates    │         │   refreshes  │
│ - app code   │         │ - Background │         │              │
│ - chromadb   │         │   tasks      │         │ Volumes:     │
│              │         │              │         │ - app code   │
│ Depends on:  │         │ Volumes:     │         │              │
│ - db         │         │ - app code   │         │ Depends on:  │
│ - redis      │         │ - chromadb   │         │ - redis      │
│              │         │              │         │ - db         │
│ Connects:    │         │ Depends on:  │         │              │
│ - PostgreSQL │         │ - redis      │         │              │
│ - Redis      │         │ - db         │         │              │
│ - ChromaDB   │         │              │         │              │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │                        │                        │
       └────────────────────────┼────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │       REDIS           │
                    │   (Message Broker)    │
                    │                       │
                    │   Port: 6379          │
                    │                       │
                    │   Used for:           │
                    │   - Celery queue      │
                    │   - Task results      │
                    │   - Caching           │
                    └───────────────────────┘

       ┌────────────────────────┐
       │      POSTGRESQL        │
       │      (Database)        │
       │                        │
       │   Port: 5433→5432      │
       │                        │
       │   Stores:              │
       │   - Products           │
       │   - Categories         │
       │   - Orders             │
       │   - Chat sessions      │
       │   - Recommendations    │
       │                        │
       │   Volume:              │
       │   - postgres_data      │
       └────────────────────────┘

       ┌────────────────────────┐
       │       MAILHOG          │
       │   (Email Testing)      │
       │                        │
       │   Ports:               │
       │   - 1025 (SMTP)        │
       │   - 8025 (Web UI)      │
       └────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENT VOLUMES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   postgres_data      │      │   chromadb_data      │        │
│  │                      │      │                      │        │
│  │  Stores:             │      │  Stores:             │        │
│  │  - All database      │      │  - Vector embeddings │        │
│  │    tables            │      │  - Product index     │        │
│  │  - User data         │      │  - Semantic search   │        │
│  │  - Product catalog   │      │    data              │        │
│  │                      │      │                      │        │
│  │  Persists:           │      │  Persists:           │        │
│  │  ✓ Container restart │      │  ✓ Container restart │        │
│  │  ✓ compose down      │      │  ✓ compose down      │        │
│  │  ✗ compose down -v   │      │  ✗ compose down -v   │        │
│  └──────────────────────┘      └──────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Communication Flow

### 1. API Request Flow

```
User Browser
    │
    ▼
Django Web (Port 8000)
    │
    ├──→ PostgreSQL (Read product data)
    │
    ├──→ ChromaDB (Semantic search via LlamaIndex)
    │
    ├──→ OpenAI API (LLM inference via LangChain)
    │
    └──→ Redis (Session cache)
```

### 2. Background Task Flow

```
Django ORM Save
    │
    ▼
Django Signal
    │
    ▼
Push Task to Redis Queue
    │
    ▼
Celery Worker picks up task
    │
    ├──→ Read from PostgreSQL
    │
    ├──→ Generate embeddings (OpenAI)
    │
    └──→ Update ChromaDB
```

### 3. Scheduled Task Flow

```
Celery Beat (Scheduler)
    │
    ▼
Schedule Task (3 AM daily)
    │
    ▼
Push to Redis Queue
    │
    ▼
Celery Worker processes
    │
    └──→ Rebuild AI Index
```

---

## Environment Variables Flow

```
.env file (local)
    │
    ▼
compose.yaml (reads ${OPENAI_API_KEY})
    │
    ├──→ web service environment
    ├──→ celery service environment
    └──→ celery-beat service environment
         │
         ▼
    Django settings.py
         │
         ├──→ os.getenv('OPENAI_API_KEY')
         ├──→ os.getenv('REDIS_URL')
         └──→ CELERY_BROKER_URL
```

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Network: app-network                │
│                       (Bridge Driver)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  web:8000 ←→ db:5432                                        │
│  web:8000 ←→ redis:6379                                     │
│  web:8000 ←→ mailhog:1025                                   │
│                                                              │
│  celery ←→ redis:6379                                       │
│  celery ←→ db:5432                                          │
│                                                              │
│  celery-beat ←→ redis:6379                                  │
│  celery-beat ←→ db:5432                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘

External Access:
┌────────────────────────────────────────────────────────────┐
│  Host Machine                                               │
│  ├── localhost:8000  → web:8000      (Django API)         │
│  ├── localhost:5433  → db:5432       (PostgreSQL)         │
│  ├── localhost:6379  → redis:6379    (Redis)              │
│  ├── localhost:1025  → mailhog:1025  (SMTP)               │
│  └── localhost:8025  → mailhog:8025  (MailHog UI)         │
└────────────────────────────────────────────────────────────┘
```

---

## Startup Sequence

```
1. docker compose up -d

2. ┌─────────────┐
   │   Redis     │  ← Starts first (no dependencies)
   │ Healthcheck │
   └──────┬──────┘
          │
3. ┌─────▼──────┐
   │ PostgreSQL │  ← Starts next (no dependencies)
   │ Healthcheck│
   └──────┬─────┘
          │
4. ┌─────▼──────┐
   │  MailHog   │  ← Starts (no dependencies)
   └────────────┘
          │
5. ┌─────▼──────────────────────────────┐
   │  Wait for Redis + DB healthy       │
   └─────┬──────────────────────────────┘
          │
6. ┌─────▼──────────────────────────────┐
   │  Django Web Service                │
   │  1. wait-for-db.sh                 │
   │  2. makemigrations                 │
   │  3. migrate                        │
   │  4. setup_views                    │
   │  5. create_superuser               │
   │  6. seed_db                        │
   │  7. refresh_views                  │
   │  8. build_ai_index ← NEW!          │
   │  9. runserver 0.0.0.0:8000         │
   └─────┬──────────────────────────────┘
          │
7. ┌─────▼──────────────────────────────┐
   │  Celery Worker                     │
   │  celery -A ecommerce_backend       │
   │         worker -l info              │
   └─────┬──────────────────────────────┘
          │
8. ┌─────▼──────────────────────────────┐
   │  Celery Beat                       │
   │  celery -A ecommerce_backend       │
   │         beat -l info                │
   └────────────────────────────────────┘

✓ All services running!
```

---

## Resource Usage

### Memory Allocation

```
Service          Memory      CPU       Storage
─────────────────────────────────────────────────
web              512MB       1 core    -
celery           1GB         1 core    -
celery-beat      256MB       0.5 core  -
postgres         512MB       1 core    Volume
redis            128MB       0.5 core  -
mailhog          64MB        0.1 core  -
chromadb_data    -           -         Volume (varies)

Total:           ~2.5GB      4 cores   Volumes
```

### Volume Sizes (Approximate)

```
postgres_data:
  - Empty: ~100MB
  - With sample data: ~200MB
  - Production (10k products): ~1GB

chromadb_data:
  - Empty: ~10MB
  - 100 products: ~50MB
  - 1000 products: ~200MB
  - 10k products: ~1GB
```

---

## Service Health Checks

### Built-in Health Checks

```yaml
# PostgreSQL
test: ["CMD-SHELL", "pg_isready -U ecommerce_user -d ecommerce_db"]
interval: 10s
timeout: 5s
retries: 5

# Redis
test: ["CMD", "redis-cli", "ping"]
interval: 10s
timeout: 5s
retries: 5
```

### Manual Health Checks

```bash
# Check all services
docker compose ps

# Check specific service health
docker compose exec web python manage.py check

# Check Celery worker
docker compose exec web celery -A ecommerce_backend inspect ping

# Check database connection
docker compose exec web python manage.py dbshell

# Check Redis connection
docker compose exec web python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Check ChromaDB
docker compose exec web python -c "import chromadb; client=chromadb.PersistentClient(path='/app/chroma_db'); print(client.heartbeat())"
```

---

## Service Dependencies

```
web:
  ├── depends_on: db (healthy)
  ├── depends_on: redis (healthy)
  └── uses: chromadb_data volume

celery:
  ├── depends_on: db (healthy)
  ├── depends_on: redis (healthy)
  └── uses: chromadb_data volume

celery-beat:
  ├── depends_on: db (healthy)
  └── depends_on: redis (healthy)

db:
  └── uses: postgres_data volume

redis:
  └── no dependencies

mailhog:
  └── no dependencies
```

---

## Scaling Strategy

### Horizontal Scaling

```yaml
# Scale Celery workers
docker compose up -d --scale celery=3

# Result: 3 Celery workers processing tasks in parallel
```

### Production Scaling

```yaml
services:
  web:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G

  celery:
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## Complete Service Matrix

| Service | Port(s) | Volume | Depends On | Role |
|---------|---------|--------|------------|------|
| **web** | 8000 | app, chromadb | db, redis | Django API, serves requests |
| **celery** | - | app, chromadb | db, redis | Background task processor |
| **celery-beat** | - | app | db, redis | Task scheduler (cron) |
| **db** | 5433→5432 | postgres_data | - | PostgreSQL database |
| **redis** | 6379 | - | - | Message broker + cache |
| **mailhog** | 1025, 8025 | - | - | Email testing |

---

## Quick Commands

```bash
# Start all services
docker compose up -d

# View all services
docker compose ps

# View logs for specific service
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f celery-beat

# Restart a service
docker compose restart celery

# Stop all services
docker compose down

# Stop and remove volumes (CAUTION!)
docker compose down -v

# Scale Celery workers
docker compose up -d --scale celery=3

# View resource usage
docker stats

# Access service shell
docker compose exec web bash
docker compose exec celery bash
docker compose exec db psql -U ecommerce_user -d ecommerce_db
docker compose exec redis redis-cli
```

---

## Troubleshooting by Service

### Web Service Issues
```bash
# Check logs
docker compose logs web | tail -100

# Access shell
docker compose exec web bash

# Test database connection
docker compose exec web python manage.py check --database default

# Run migrations
docker compose exec web python manage.py migrate
```

### Celery Issues
```bash
# Check worker status
docker compose exec web celery -A ecommerce_backend inspect active

# Purge task queue
docker compose exec web celery -A ecommerce_backend purge

# Restart worker
docker compose restart celery
```

### Database Issues
```bash
# Access PostgreSQL
docker compose exec db psql -U ecommerce_user -d ecommerce_db

# Check connections
docker compose exec db psql -U ecommerce_user -d ecommerce_db -c "SELECT * FROM pg_stat_activity;"

# Backup database
docker compose exec db pg_dump -U ecommerce_user ecommerce_db > backup.sql
```

### Redis Issues
```bash
# Access Redis CLI
docker compose exec redis redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR

# Check memory usage
INFO memory
```

---

**Complete Docker setup for Marcus E-commerce with AI Assistant!** 🚀
