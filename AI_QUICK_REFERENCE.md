# AI Assistant Quick Reference Card

## 🚀 Essential Commands

### Setup
```bash
# Set API key
export OPENAI_API_KEY=sk-your-key

# Start services
docker compose up --build -d

# Build AI index
docker compose exec web python manage.py build_ai_index

# Run tests
docker compose exec web python -m apps.ai_assistant.test_rag_system
```

### Index Management
```bash
# Update index (incremental)
docker compose exec web python manage.py build_ai_index

# Rebuild index (full)
docker compose exec web python manage.py build_ai_index --rebuild

# Check index status
docker compose exec web python manage.py shell
>>> from apps.ai_assistant.services.index_service import get_index_service
>>> get_index_service().get_stats()
```

### Monitoring
```bash
# View logs
docker compose logs -f web

# Check ChromaDB size
docker compose exec web du -sh /app/chroma_db

# Monitor Celery worker
docker compose logs -f celery

# Check Celery status
docker compose exec web celery -A ecommerce_backend inspect active
```

---

## 📁 File Structure

```
server/apps/ai_assistant/
├── services/
│   ├── document_loaders.py      # Django models → Documents
│   ├── index_service.py         # Vector search (LlamaIndex)
│   ├── langchain_tools.py       # Agent tools (LangChain)
│   ├── agent_service.py         # Intelligent agent
│   ├── rag_service_new.py       # RAG retrieval
│   ├── context_builder.py       # Database queries
│   ├── llm_service.py           # OLD (deprecated)
│   └── rag_service.py           # OLD (deprecated)
├── management/commands/
│   └── build_ai_index.py        # CLI command
├── tasks.py                     # Celery tasks
├── signals.py                   # Auto-indexing triggers
├── models.py                    # Database models
├── views.py                     # API endpoints
├── README.md                    # Full documentation
├── SETUP.md                     # Setup guide
├── MIGRATION_GUIDE.md           # Migration guide
└── test_rag_system.py           # Test suite
```

---

## 🔧 Architecture Flow

```
User Query
    ↓
LangChain Agent (decides which tools to use)
    ↓
LangChain Tools (search, validate, calculate)
    ↓
LlamaIndex (semantic search in vector DB)
    ↓
Django Models (via document loaders)
```

---

## 🎯 Key Features

| Feature | Implementation |
|---------|---------------|
| **No Hardcoding** | Everything from database |
| **Semantic Search** | Vector embeddings (OpenAI) |
| **Intelligent Agent** | LangChain with tool calling |
| **Auto-Updates** | Django signals → Celery tasks |
| **Persistence** | ChromaDB in Docker volume |
| **Framework-Based** | LlamaIndex + LangChain |

---

## 🛠️ Common Tasks

### Add New Category
```python
# Just add to database - NO code changes!
Category.objects.create(
    name="Kayaks",
    description="Water sports equipment"
)
# Index auto-updates via signals!
```

### Add Business Knowledge
```python
AIEmbeddedDocument.objects.create(
    document_type='faq',
    content="Free shipping on orders over $500",
    metadata={"topic": "shipping"}
)
# Rebuild index to include
```

### Add Custom Tool
```python
# In langchain_tools.py
class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"

    def _run(self, input: str) -> str:
        # Your logic
        return "result"

# Add to get_all_tools()
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Index not built" | `python manage.py build_ai_index` |
| "OPENAI_API_KEY not set" | Check `.env` file |
| Slow responses | Normal on first request (loads index) |
| Wrong products | Rebuild index with `--rebuild` |
| Out of memory | Reduce `top_k` in index_service.py |
| Permission errors | `chown -R www-data /app/chroma_db` |

---

## 📊 API Endpoints

### Chat
```bash
POST /api/ai-assistant/chat/
{
  "session_id": "session-123",
  "message": "I need a mountain bike",
  "context": {"currentPage": "/category/bikes"}
}
```

### Recommend Products
```bash
POST /api/ai-assistant/recommend-products/
{
  "query": "trail bike",
  "category_id": 1,
  "price_max": 2000
}
```

### Get Session
```bash
GET /api/ai-assistant/sessions/{session_id}/
```

---

## 🔄 Auto-Indexing Triggers

These model changes trigger automatic index updates:

- ✓ `PreConfiguredProduct` (save/delete)
- ✓ `Category` (save/delete)
- ✓ `PartOption` (save/delete)
- ✓ `IncompatibilityRule` (save/delete)
- ✓ `PriceAdjustmentRule` (save/delete)

**Delay:** 30 seconds (batches rapid changes)

---

## 🧪 Testing Examples

### Test Product Search
```python
from apps.ai_assistant.services.index_service import get_index_service

index = get_index_service()
index.build_index()

results = index.search_products("beginner bike")
print(f"Found {len(results)} products")
```

### Test Agent
```python
from apps.ai_assistant.services.agent_service import get_agent_service

agent = get_agent_service()
response = agent.generate_response("What's your cheapest bike?")

print(response['content'])
print(f"Tools used: {response['metadata']['tools_used']}")
```

### Test RAG
```python
from apps.ai_assistant.services.rag_service_new import get_rag_service

rag = get_rag_service()
context = rag.retrieve_context_for_query("mountain bike")

print(f"Intent: {context['intent']}")
print(f"Products: {len(context['products'])}")
```

---

## 📦 Dependencies

```
llama-index                    # Core indexing
llama-index-embeddings-openai  # OpenAI embeddings
llama-index-llms-openai        # OpenAI LLM
langchain                      # Agent framework
langchain-openai               # OpenAI integration
langchain-community            # Community tools
chromadb                       # Vector database
tiktoken                       # Token counting
```

---

## 🎓 Learning Resources

- **LlamaIndex:** https://docs.llamaindex.ai/
- **LangChain:** https://python.langchain.com/
- **ChromaDB:** https://docs.trychroma.com/
- **OpenAI API:** https://platform.openai.com/docs

---

## 💾 Docker Volumes

```bash
# List volumes
docker volume ls | grep marcus

# Inspect ChromaDB volume
docker volume inspect marcus-eccommerce-chromadb-data

# Remove ChromaDB volume (resets index)
docker volume rm marcus-eccommerce-chromadb-data

# Backup ChromaDB
docker run --rm -v marcus-eccommerce-chromadb-data:/data \
  -v $(pwd):/backup alpine tar czf /backup/chromadb-backup.tar.gz /data
```

---

## 🚦 Production Checklist

- [ ] Set `OPENAI_API_KEY` in production environment
- [ ] Use managed vector DB (Pinecone/Weaviate)
- [ ] Set up dedicated Celery worker
- [ ] Enable LangSmith monitoring
- [ ] Configure rate limiting
- [ ] Set up error alerting
- [ ] Schedule nightly index refresh
- [ ] Monitor ChromaDB disk usage
- [ ] Test failover scenarios
- [ ] Document API for frontend team

---

## 📈 Performance Tuning

```python
# Reduce retrieval time
Settings.top_k = 3  # Default: 5

# Use faster embedding model
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small"  # Faster than large
)

# Use faster LLM
self.llm = ChatOpenAI(
    model="gpt-3.5-turbo"  # Faster than gpt-4
)

# Enable caching
from langchain.cache import InMemoryCache
langchain.llm_cache = InMemoryCache()
```

---

## 🎉 Success Indicators

✅ Index builds without errors
✅ All tests pass
✅ Agent uses tools correctly
✅ Semantic search returns relevant results
✅ New products appear in search automatically
✅ Response time < 3 seconds
✅ No hallucinated products
✅ Celery tasks execute successfully

---

**Need help?** Check the full docs:
- [README.md](server/apps/ai_assistant/README.md)
- [SETUP.md](server/apps/ai_assistant/SETUP.md)
- [MIGRATION_GUIDE.md](server/apps/ai_assistant/MIGRATION_GUIDE.md)
