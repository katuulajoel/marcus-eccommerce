# Celery Setup for AI Assistant Auto-Indexing

## Overview

The AI Assistant uses **Celery** for background task processing, specifically for:
- Auto-rebuilding the vector index when products change
- Scheduled periodic index refreshes
- Async processing to avoid blocking API requests

---

## Architecture

```
Django Model Save/Delete
    ↓
Django Signal (signals.py)
    ↓
Schedule Celery Task (30s delay for batching)
    ↓
Celery Worker picks up task
    ↓
Index rebuilds in background
    ↓
New products immediately searchable!
```

---

## Docker Compose Services

### Services Added

We have **3 services** for Celery:

#### 1. **celery** (Worker)
Processes background tasks (index updates)

```yaml
celery:
  build: .
  command: celery -A ecommerce_backend worker -l info
  volumes:
    - .:/app
    - chromadb_data:/app/chroma_db  # ← Access to vector DB
  environment:
    - REDIS_URL=redis://redis:6379/0
    - OPENAI_API_KEY=${OPENAI_API_KEY:-}
  depends_on:
    - redis
    - db
```

#### 2. **celery-beat** (Scheduler)
Schedules periodic tasks (nightly refreshes)

```yaml
celery-beat:
  build: .
  command: celery -A ecommerce_backend beat -l info
  volumes:
    - .:/app
  environment:
    - REDIS_URL=redis://redis:6379/0
  depends_on:
    - redis
    - db
```

#### 3. **redis** (Message Broker)
Already exists - used for Celery task queue

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

---

## Django Settings

### Celery Configuration

File: `ecommerce_backend/settings.py`

```python
# Celery configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max
```

### Celery App Initialization

File: `ecommerce_backend/celery.py`

```python
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
app = Celery('ecommerce_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # ← Finds tasks.py in all apps
```

File: `ecommerce_backend/__init__.py`

```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

---

## AI Assistant Tasks

### Available Tasks

File: `apps/ai_assistant/tasks.py`

#### 1. `rebuild_ai_index` (Full Rebuild)
```python
@shared_task(name='ai_assistant.rebuild_index')
def rebuild_ai_index():
    """Full rebuild of AI knowledge index"""
    index_service = get_index_service()
    index_service.rebuild_index()
```

**When to use:**
- Major database changes
- Corrupted index
- Initial setup

#### 2. `update_ai_index` (Incremental Update)
```python
@shared_task(name='ai_assistant.update_index')
def update_ai_index():
    """Incremental update of AI index"""
    index_service = get_index_service()
    index_service.build_index()
```

**When to use:**
- Single product added
- Product updated
- Auto-triggered by signals

#### 3. `scheduled_index_refresh` (Periodic)
```python
@shared_task(name='ai_assistant.scheduled_index_refresh')
def scheduled_index_refresh():
    """Scheduled nightly refresh"""
    # Checks cache to avoid too-frequent updates
    rebuild_ai_index.delay()
```

**When to use:**
- Nightly cron job
- Scheduled maintenance

---

## Auto-Indexing Signals

### How It Works

File: `apps/ai_assistant/signals.py`

```python
@receiver([post_save, post_delete], sender=PreConfiguredProduct)
def handle_product_change(sender, instance, **kwargs):
    """Trigger index update when products change"""
    schedule_index_update()

def schedule_index_update():
    """Schedule update with 30s delay for batching"""
    if cache.get('ai_index_update_scheduled'):
        return  # Already scheduled

    cache.set('ai_index_update_scheduled', True, timeout=60)
    update_ai_index.apply_async(countdown=30)  # 30s delay
```

### Models That Trigger Auto-Indexing

- ✅ `PreConfiguredProduct` (save/delete)
- ✅ `Category` (save/delete)
- ✅ `PartOption` (save/delete)
- ✅ `IncompatibilityRule` (save/delete)
- ✅ `PriceAdjustmentRule` (save/delete)

### Debouncing Logic

**Problem:** If admin adds 10 products rapidly, we don't want 10 index rebuilds!

**Solution:**
1. First save triggers signal
2. Task scheduled with 30-second delay
3. Cache flag set for 60 seconds
4. Subsequent saves within 60s are ignored
5. After 30s, index rebuilds once with all changes

---

## Starting Celery

### With Docker Compose (Automatic)

```bash
# Start all services including Celery
docker compose up -d

# Check Celery worker logs
docker compose logs -f celery

# Check Celery beat logs
docker compose logs -f celery-beat
```

### Manually (For Testing)

```bash
# In separate terminals:

# Terminal 1: Celery worker
docker compose exec web celery -A ecommerce_backend worker -l info

# Terminal 2: Celery beat (scheduler)
docker compose exec web celery -A ecommerce_backend beat -l info
```

---

## Monitoring Celery

### Check Worker Status

```bash
# List active workers
docker compose exec web celery -A ecommerce_backend inspect active

# Check registered tasks
docker compose exec web celery -A ecommerce_backend inspect registered

# Check worker stats
docker compose exec web celery -A ecommerce_backend inspect stats
```

### View Task Queue

```bash
# Using Redis CLI
docker compose exec redis redis-cli

> KEYS celery*
> LLEN celery  # Queue length
```

### Live Monitoring

```bash
# Watch Celery logs in real-time
docker compose logs -f celery

# Filter for AI assistant tasks
docker compose logs -f celery | grep "ai_assistant"
```

---

## Manual Task Execution

### Django Shell

```bash
docker compose exec web python manage.py shell
```

```python
# Import task
from apps.ai_assistant.tasks import rebuild_ai_index, update_ai_index

# Execute synchronously (blocks)
rebuild_ai_index()

# Execute asynchronously (returns immediately)
task = rebuild_ai_index.delay()
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")

# Check result
task.wait()  # Block until done
print(task.result)
```

### Via API (Optional)

You can create an admin-only endpoint to trigger rebuilds:

```python
# In views.py
@api_view(['POST'])
@permission_classes([IsAdminUser])
def trigger_index_rebuild(request):
    from .tasks import rebuild_ai_index
    task = rebuild_ai_index.delay()
    return Response({
        'task_id': task.id,
        'status': 'Rebuild scheduled'
    })
```

---

## Scheduled Tasks (Optional)

### Using Celery Beat

File: `ecommerce_backend/settings.py`

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'refresh-ai-index-nightly': {
        'task': 'ai_assistant.scheduled_index_refresh',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
}
```

**Restart celery-beat after adding:**
```bash
docker compose restart celery-beat
```

---

## Troubleshooting

### Issue: Celery Not Processing Tasks

**Check:**
```bash
# 1. Is Celery worker running?
docker compose ps celery

# 2. Are there errors in logs?
docker compose logs celery

# 3. Is Redis accessible?
docker compose exec web python -c "import redis; r = redis.from_url('redis://redis:6379/0'); print(r.ping())"

# 4. Are tasks registered?
docker compose exec web celery -A ecommerce_backend inspect registered
```

### Issue: Tasks Stuck in Queue

**Solution:**
```bash
# Purge all tasks
docker compose exec web celery -A ecommerce_backend purge

# Restart worker
docker compose restart celery
```

### Issue: Index Not Auto-Updating

**Check:**
1. Are signals connected? (Check `apps.py` has `ready()` method)
2. Is Celery worker running?
3. Check signal logs:

```python
# In signals.py, add logging
import logging
logger = logging.getLogger(__name__)

def schedule_index_update():
    logger.info("Scheduling index update...")
    # ... rest of code
```

### Issue: "Connection refused" Errors

**Cause:** Celery can't reach Redis

**Solution:**
```bash
# Check Redis is running
docker compose ps redis

# Check network connectivity
docker compose exec celery ping redis

# Verify REDIS_URL in environment
docker compose exec celery env | grep REDIS_URL
```

### Issue: Memory Errors During Indexing

**Cause:** ChromaDB loading large index

**Solution:**
```yaml
# In compose.yaml, increase memory limit
celery:
  deploy:
    resources:
      limits:
        memory: 2G
```

---

## Production Considerations

### 1. Separate Celery Worker

For production, run Celery on separate machines:

```yaml
# production-compose.yaml
celery:
  image: your-registry/marcus-ecommerce:latest
  command: celery -A ecommerce_backend worker -l warning
  deploy:
    replicas: 3  # Multiple workers
    resources:
      limits:
        memory: 2G
```

### 2. Monitoring with Flower

Add Celery Flower for web-based monitoring:

```yaml
flower:
  image: mher/flower
  command: celery flower --broker=redis://redis:6379/0
  ports:
    - "5555:5555"
  depends_on:
    - redis
```

Access at: http://localhost:5555

### 3. Task Routing

For large-scale deployments, route tasks to specific workers:

```python
# settings.py
CELERY_TASK_ROUTES = {
    'ai_assistant.rebuild_index': {'queue': 'ai_heavy'},
    'ai_assistant.update_index': {'queue': 'ai_light'},
}
```

```bash
# Start specialized workers
celery -A ecommerce_backend worker -Q ai_heavy -n heavy@%h
celery -A ecommerce_backend worker -Q ai_light -n light@%h
```

### 4. Error Handling

```python
# In tasks.py
@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def rebuild_ai_index(self):
    try:
        index_service = get_index_service()
        index_service.rebuild_index()
    except Exception as exc:
        logger.error(f"Index rebuild failed: {exc}")
        raise self.retry(exc=exc)
```

---

## Testing Celery

### Unit Tests

```python
# In tests.py
from django.test import TestCase
from apps.ai_assistant.tasks import update_ai_index

class CeleryTaskTests(TestCase):
    def test_update_index_task(self):
        result = update_ai_index.delay()
        self.assertEqual(result.status, 'SUCCESS')
```

### Integration Test

```bash
# 1. Start services
docker compose up -d

# 2. Add a product
docker compose exec web python manage.py shell
>>> from apps.preconfigured_products.models import PreConfiguredProduct
>>> PreConfiguredProduct.objects.create(...)

# 3. Wait 30 seconds

# 4. Check Celery logs
docker compose logs celery | grep "ai_assistant"

# 5. Verify index updated
>>> from apps.ai_assistant.services.index_service import get_index_service
>>> index = get_index_service()
>>> results = index.search_products("new product name")
>>> assert len(results) > 0
```

---

## Summary

### What Celery Does for AI Assistant

✅ **Auto-Indexing:** Products added → Index updates automatically
✅ **Async Processing:** Index rebuilds don't block API requests
✅ **Batching:** Multiple rapid changes trigger single rebuild
✅ **Scheduling:** Optional nightly refreshes
✅ **Scalability:** Can add more workers as load increases

### Key Commands

```bash
# Start all services
docker compose up -d

# View Celery worker logs
docker compose logs -f celery

# Check worker status
docker compose exec web celery -A ecommerce_backend inspect active

# Manual task execution
docker compose exec web python manage.py shell
>>> from apps.ai_assistant.tasks import rebuild_ai_index
>>> rebuild_ai_index.delay()

# Purge task queue
docker compose exec web celery -A ecommerce_backend purge
```

---

**Your Celery setup is now complete!** Background index updates will happen automatically when you add/edit products! 🎉
