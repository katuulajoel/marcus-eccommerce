# AI Assistant Setup Guide

## Quick Start (Docker)

### 1. Set OpenAI API Key

Create or update `.env` file in the `server` directory:

```bash
# server/.env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

Or set it in your shell:

```bash
export OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 2. Build and Start Services

```bash
# From the server directory
docker compose up --build -d
```

**What happens automatically:**
1. ✓ Database migrations run
2. ✓ Sample data seeded
3. ✓ AI index built from database ← **NEW!**
4. ✓ Django server starts

**Initial build includes:**
- Categories indexed
- Products embedded
- Part options vectorized
- Rules loaded
- ChromaDB initialized

### 3. Verify AI Index

Check the logs to confirm index was built:

```bash
docker compose logs web | grep "AI index"
```

Expected output:
```
✓ Loaded 3 documents from CategoryDocumentLoader
✓ Loaded 25 documents from ProductDocumentLoader
✓ Index built successfully with 190 documents
```

### 4. Test the System

```bash
# Run the test suite
docker compose exec web python -m apps.ai_assistant.test_rag_system
```

All tests should pass!

---

## Manual Index Management

### Rebuild Index (After Major DB Changes)

```bash
docker compose exec web python manage.py build_ai_index --rebuild
```

Use `--rebuild` when:
- You deleted many products
- You changed category structure significantly
- Index seems corrupted
- You want a fresh start

### Update Index (After Minor Changes)

```bash
docker compose exec web python manage.py build_ai_index
```

Use without `--rebuild` for:
- Adding new products
- Updating product descriptions
- Adding new part options

**Note:** Index also auto-updates via signals when you save models!

---

## ChromaDB Persistence

ChromaDB data is stored in a Docker volume for persistence:

```yaml
volumes:
  chromadb_data:
    name: marcus-eccommerce-chromadb-data
```

**Location:** `/app/chroma_db` inside container

**Persistence:**
- Survives container restarts
- Survives `docker compose down`
- Does NOT survive `docker compose down -v` (volumes deleted)

### View ChromaDB Data

```bash
# Check size
docker compose exec web du -sh /app/chroma_db

# List collections
docker compose exec web python -c "
import chromadb
client = chromadb.PersistentClient(path='/app/chroma_db')
print(client.list_collections())
"
```

### Reset ChromaDB

```bash
# Stop services
docker compose down

# Remove ChromaDB volume
docker volume rm marcus-eccommerce-chromadb-data

# Restart (will rebuild index)
docker compose up -d
```

---

## Environment Variables

### Required

```bash
OPENAI_API_KEY=sk-...  # Required for LLM and embeddings
```

### Optional (with defaults)

```bash
OPENAI_MODEL=gpt-4o-mini          # LLM model
OPENAI_TEMPERATURE=0.7            # Response creativity (0-1)
OPENAI_MAX_TOKENS=500            # Max response length
```

### Advanced Configuration

For production, you can override defaults in code:

**LlamaIndex Settings** (`index_service.py`):
```python
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",  # or text-embedding-3-large
    api_key=openai_api_key
)

Settings.llm = OpenAI(
    model="gpt-4o-mini",  # or gpt-4o for better quality
    temperature=0.7
)
```

**LangChain Agent** (`agent_service.py`):
```python
self.llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=500
)
```

---

## Auto-Indexing via Signals

The system automatically rebuilds the index when models change!

**Triggers:**
- `PreConfiguredProduct` saved/deleted → Index update
- `Category` saved/deleted → Index update
- `PartOption` saved/deleted → Index update
- `IncompatibilityRule` saved/deleted → Index update
- `PriceAdjustmentRule` saved/deleted → Index update

**How it works:**
1. Django signal fires
2. Celery task scheduled (30-second delay for batching)
3. Index updates in background
4. User sees updated results

**Check Celery logs:**
```bash
docker compose logs -f web | grep "celery"
```

---

## Celery Background Tasks

The system uses Celery for async index updates.

### Start Celery Worker (if not running)

```bash
# In a separate terminal
docker compose exec web celery -A ecommerce_backend worker -l info
```

### Available Tasks

1. **`ai_assistant.rebuild_index`** - Full rebuild
2. **`ai_assistant.update_index`** - Incremental update
3. **`ai_assistant.scheduled_index_refresh`** - Periodic refresh

### Manual Task Execution

```python
# In Django shell
from apps.ai_assistant.tasks import rebuild_ai_index

# Sync execution
rebuild_ai_index()

# Async execution
rebuild_ai_index.delay()
```

---

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"

**Solution:**
```bash
# Check if key is set
docker compose exec web env | grep OPENAI

# If not, add to .env and restart
docker compose restart web
```

### Issue: "Index not built"

**Solution:**
```bash
# Manually build
docker compose exec web python manage.py build_ai_index
```

### Issue: ChromaDB Permission Errors

**Solution:**
```bash
# Fix permissions
docker compose exec web chown -R www-data:www-data /app/chroma_db

# Or recreate volume
docker compose down
docker volume rm marcus-eccommerce-chromadb-data
docker compose up -d
```

### Issue: Slow AI Responses

**Causes:**
1. First request loads index (normal)
2. OpenAI API rate limits
3. Large index (many products)

**Solutions:**
```bash
# Reduce top_k in index_service.py (fewer documents retrieved)
# Use GPT-3.5-turbo instead of GPT-4 (faster, cheaper)
# Enable caching for common queries
```

### Issue: Out of Memory

**Cause:** ChromaDB loads index into memory

**Solutions:**
```bash
# Increase Docker memory limit
# Reduce index size (fewer documents)
# Use Pinecone/Weaviate for production (cloud-hosted)
```

---

## Production Deployment

### Recommended Changes

1. **Use Managed Vector DB**
```python
# Instead of ChromaDB local, use Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
import pinecone

pinecone.init(api_key="...", environment="...")
vector_store = PineconeVectorStore(pinecone_index=...)
```

2. **Dedicated Celery Worker**
```yaml
# In docker-compose.yml
celery:
  build: .
  command: celery -A ecommerce_backend worker -l info
  depends_on:
    - redis
    - db
```

3. **Environment-Specific Settings**
```python
# settings.py
if ENVIRONMENT == 'production':
    LLAMAINDEX_CACHE_DIR = '/var/cache/llamaindex'
    CHROMADB_PERSIST_DIR = '/var/lib/chromadb'
```

4. **Monitor with LangSmith**
```python
# Enable tracing
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."
```

---

## Monitoring

### Index Stats

```bash
docker compose exec web python manage.py shell
```

```python
from apps.ai_assistant.services.index_service import get_index_service

index = get_index_service()
index.build_index()  # Load if not loaded
stats = index.get_stats()
print(stats)
```

### Query Performance

```python
import time
from apps.ai_assistant.services.index_service import get_index_service

index = get_index_service()

start = time.time()
results = index.search_products("mountain bike")
elapsed = time.time() - start

print(f"Query took {elapsed:.3f}s")
print(f"Found {len(results)} products")
```

### Agent Tool Usage

```python
from apps.ai_assistant.services.agent_service import get_agent_service

agent = get_agent_service()
response = agent.generate_response("What's your cheapest bike?")

print("Tools used:", response['metadata']['tools_used'])
print("Steps taken:", response['metadata']['agent_steps'])
```

---

## Next Steps

1. ✅ Verify index is built
2. ✅ Test with sample queries
3. ✅ Check Celery is running
4. ✅ Monitor first few conversations
5. Add business-specific FAQs
6. Customize system prompts
7. Extend with custom tools
8. Set up monitoring dashboard

---

## Resources

- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [OpenAI API](https://platform.openai.com/docs)

For implementation details, see [README.md](./README.md)
For migration guide, see [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
