# AI Assistant Integration - Implementation Guide

## Overview

This document describes the AI-powered assistant integration for Marcus Custom Bikes e-commerce platform. The AI assistant helps shorten the customer journey by providing intelligent product recommendations, configuration guidance, and real-time support throughout the shopping experience.

## What Has Been Implemented

### Phase 1: Foundation (COMPLETED)

#### Frontend Components
**Location**: `web/client/components/ai-assistant/`

1. **AIAssistant** - Main component that renders both button and panel
2. **AIAssistantButton** - Floating button in bottom-right corner
   - Purple-pink gradient styling
   - Toggles panel visibility
   - Shows unread message count (ready for future enhancement)

3. **AIAssistantPanel** - Chat interface
   - Collapsible panel with message history
   - Quick action buttons for common queries
   - Auto-scroll to latest messages
   - Loading states with animated indicators

4. **AIChatMessage** - Individual message component
   - Different styling for user vs assistant messages
   - Timestamp display
   - Avatar icons (User/Bot)

#### Context Provider
**Location**: `web/client/context/ai-assistant-context.tsx`

- **AIAssistantProvider**: Global state management for AI chat
- **useAIAssistant**: Hook to access AI assistant functionality
- Features:
  - Session management with localStorage persistence
  - Message history persistence
  - Session context tracking (page, cart, configuration state)
  - Real-time API integration

#### Integration Points

1. **App Integration** ([web/client/App.jsx](web/client/App.jsx))
   - AI Assistant component added to main app
   - Available on all pages globally

2. **Provider Setup** ([web/client/main.jsx](web/client/main.jsx))
   - AIAssistantProvider wraps the entire app
   - Provides AI state to all components

### Phase 2: Backend API (COMPLETED)

#### Django App
**Location**: `server/apps/ai_assistant/`

#### Models ([models.py](server/apps/ai_assistant/models.py))

1. **AIChatSession**
   - Tracks conversation sessions
   - Links to Customer (or anonymous)
   - Stores context (page, cart, configuration)
   - Timestamps for analytics

2. **AIChatMessage**
   - Individual messages in conversations
   - Role: user, assistant, or system
   - Metadata for product IDs, suggestions, etc.
   - Ordered by creation time

3. **AIEmbeddedDocument** (Ready for RAG)
   - Stores document embeddings for search
   - Types: product, part_option, category, compatibility_rule, faq
   - Metadata for filtering and retrieval
   - Vector field (commented out, pending pgvector setup)

4. **AIRecommendation**
   - Tracks recommendations made to users
   - Records user actions (viewed, added_to_cart, ignored)
   - For analytics and improvement

#### API Endpoints ([views.py](server/apps/ai_assistant/views.py))

**Base URL**: `/api/ai-assistant/`

1. **POST /chat/**
   - Main chat endpoint
   - Receives user message + context
   - Returns AI response
   - Creates/updates session automatically

2. **GET /session/{session_id}/**
   - Retrieve full chat history
   - Includes all messages in chronological order

3. **DELETE /session/{session_id}/clear/**
   - Clear message history
   - Keeps session for future conversations

4. **POST /recommend/** (Placeholder)
   - Product recommendation endpoint
   - Ready for RAG implementation

5. **POST /validate-config/** (Placeholder)
   - Configuration validation endpoint
   - Ready for AI-powered suggestions

#### Current AI Logic

**Simple Keyword-Based Responses** ([views.py](server/apps/ai_assistant/views.py:152))

The system currently uses keyword matching to provide helpful responses:
- Mountain/trail/off-road → Mountain bike information
- Road/racing/speed → Road bike recommendations
- Beginner/first/start → Beginner guidance
- Price/cost/cheap → Budget assistance
- Customize/custom/build → Configuration help
- Default → General assistance message

#### Admin Interface ([admin.py](server/apps/ai_assistant/admin.py))

- Full CRUD operations for all models
- Inline message display in sessions
- Content previews for long messages
- Filtering and search capabilities

### Phase 3: API Integration (COMPLETED)

#### Frontend API Client ([web/client/services/api.ts](web/client/services/api.ts))

```typescript
// AI Assistant API functions
sendAIChatMessage(sessionId, message, context)
getAIChatSession(sessionId)
clearAIChatSession(sessionId)
```

#### Real-time Communication
- Chat messages sent to Django backend
- Responses rendered immediately in UI
- Error handling with user-friendly messages
- Loading states during API calls

## Current Features

### User Experience

1. **Global Accessibility**
   - Floating button visible on all pages
   - Click to open/close chat panel
   - Maintains conversation across page navigation

2. **Conversation Persistence**
   - Messages saved to localStorage
   - Session ID tracked across browser sessions
   - Full history available in backend database

3. **Contextual Awareness**
   - System tracks current page
   - Can access cart contents
   - Aware of product configurations
   - Future: Context-aware responses

4. **Quick Actions**
   - Pre-defined queries for common needs:
     * "Recommend a bike for beginners"
     * "Show me mountain bikes"
     * "What's on sale?"
     * "Help me customize"

5. **Smart Responses**
   - Keyword-based matching (temporary)
   - Helpful guidance for different bike types
   - Budget assistance
   - Customization guidance

## What's Next (Pending Implementation)

### Phase 4: RAG System

1. **Setup pgvector Extension**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Generate Embeddings**
   - Create embeddings for all products
   - Embed part descriptions
   - Index category information
   - Store compatibility rules

3. **Vector Search Service**
   - Similarity search for user queries
   - Retrieve relevant products/parts
   - Context-aware filtering

### Phase 5: LLM Integration

1. **Choose LLM Provider**
   - OpenAI GPT-4
   - Anthropic Claude
   - Open-source alternative

2. **Implement LLM Service**
   - Prompt engineering
   - Context injection from RAG
   - Function calling for actions

3. **Streaming Responses**
   - Server-Sent Events (SSE)
   - Real-time response generation
   - Better user experience

### Phase 6: Advanced Features

1. **Product Recommendations**
   - AI-powered suggestions based on preferences
   - Similar product discovery
   - Complementary items

2. **Configuration Auto-complete**
   - Smart part selection
   - Compatibility validation
   - Price optimization

3. **Integration with BikeCustomizer**
   - Direct configuration updates
   - "Apply suggestion" buttons
   - Visual previews in chat

4. **Analytics & Learning**
   - Track recommendation effectiveness
   - A/B testing
   - Continuous improvement

## Technical Architecture

### Frontend Flow
```
User Input
  ↓
AIAssistantPanel (UI)
  ↓
useAIAssistant (Context)
  ↓
sendMessage()
  ↓
api.ts (API Client)
  ↓
Backend /api/ai-assistant/chat/
```

### Backend Flow
```
API Request
  ↓
views.chat()
  ↓
Get/Create Session
  ↓
Save User Message
  ↓
Generate AI Response (keyword matching)
  ↓
Save AI Message
  ↓
Return Response
```

### Future RAG Flow
```
User Query
  ↓
Generate Query Embedding
  ↓
Vector Similarity Search
  ↓
Retrieve Relevant Documents
  ↓
Build Context
  ↓
LLM with Context
  ↓
Structured Response
  ↓
Frontend Rendering
```

## Database Schema

### Current Tables

```sql
-- Chat sessions
ai_chat_session (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    customer_id INT REFERENCES customer,
    context JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Chat messages
ai_chat_message (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES ai_chat_session,
    role VARCHAR(20),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP
)

-- Embeddings (for RAG)
ai_embedded_document (
    id SERIAL PRIMARY KEY,
    document_type VARCHAR(50),
    document_id INT,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Recommendations tracking
ai_recommendation (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES ai_chat_session,
    recommended_product_ids INT[],
    context JSONB,
    user_action VARCHAR(50),
    created_at TIMESTAMP
)
```

## Configuration

### Frontend Environment
**File**: `web/.env.local`
```env
VITE_API_BASE_URL=http://localhost:8000/
```

### Backend Settings
**File**: `server/ecommerce_backend/settings.py`
```python
INSTALLED_APPS = [
    ...
    'apps.ai_assistant',
]
```

### URL Configuration
**File**: `server/ecommerce_backend/urls.py`
```python
api_patterns = [
    ...
    path('ai-assistant/', include('apps.ai_assistant.urls')),
]
```

## Testing the Integration

### 1. Start Backend
```bash
cd server
docker compose up
```

### 2. Run Migrations
```bash
docker compose exec web python manage.py migrate
```

### 3. Start Frontend
```bash
cd web
npm run dev:client
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

### 5. Test AI Assistant
1. Look for floating button in bottom-right corner
2. Click to open chat panel
3. Try quick actions or type a message
4. Messages should appear with ~1 second delay (simulating AI thinking)
5. Check Django admin to see stored sessions and messages

## Example Interactions

### Product Discovery
```
User: "I need a mountain bike for rough terrain"
AI: "Great! I can help you find the perfect mountain bike. Mountain bikes
     are designed for rugged terrain with features like durable frames and
     all-terrain tires. Would you like me to show you our top mountain bike models?"
```

### Budget Assistance
```
User: "What's affordable?"
AI: "I understand budget is important! I can help you find bikes within your
     price range. Could you tell me what your budget is, and I'll recommend
     the best options?"
```

### Customization Help
```
User: "Help me customize a bike"
AI: "I'd love to help you build your custom bike! You can customize various
     components like the frame, wheels, handlebars, and more. Each choice
     affects both performance and price. Shall we start with selecting a
     frame type?"
```

## Key Files Reference

### Frontend
- `web/client/context/ai-assistant-context.tsx` - State management
- `web/client/components/ai-assistant/` - UI components
- `web/client/services/api.ts` - API functions
- `web/client/App.jsx` - AI assistant integration
- `web/client/main.jsx` - Provider setup

### Backend
- `server/apps/ai_assistant/models.py` - Database models
- `server/apps/ai_assistant/views.py` - API endpoints
- `server/apps/ai_assistant/serializers.py` - Data serialization
- `server/apps/ai_assistant/urls.py` - URL routing
- `server/apps/ai_assistant/admin.py` - Admin interface
- `server/ecommerce_backend/settings.py` - App configuration
- `server/ecommerce_backend/urls.py` - Main URL config

## Next Steps

1. **Test the Current Implementation**
   - Verify all endpoints work
   - Test session persistence
   - Check admin interface

2. **Install pgvector**
   ```bash
   docker compose exec db psql -U ecommerce_user -d ecommerce_db
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Generate Embeddings**
   - Create management command to embed products
   - Store embeddings in AIEmbeddedDocument

4. **Integrate LLM API**
   - Add OpenAI or Claude API key to environment
   - Update views.py to use real LLM
   - Implement streaming responses

5. **Build RAG Service**
   - Implement vector search
   - Create context builder
   - Connect to LLM with retrieved context

6. **Connect to BikeCustomizer**
   - Update session context on configuration changes
   - Add "Apply suggestion" functionality
   - Show product previews in chat

## Success Metrics

Track these metrics to measure AI assistant effectiveness:

1. **Engagement**
   - % of users who open AI assistant
   - Average messages per session
   - Session duration

2. **Conversion**
   - Products added to cart via AI recommendations
   - Completed purchases with AI interaction
   - Average order value comparison

3. **Customer Satisfaction**
   - Response helpfulness ratings
   - Task completion rate
   - Return user percentage

4. **Performance**
   - Response time
   - Error rate
   - Successful recommendations

## Troubleshooting

### AI Button Not Showing
- Check that AIAssistantProvider is in main.jsx
- Verify AIAssistant component in App.jsx
- Check browser console for errors

### Messages Not Sending
- Verify backend is running (http://localhost:8000)
- Check CORS settings in Django
- Inspect network tab for API errors

### Session Not Persisting
- Check browser localStorage
- Verify session_id is being generated
- Check backend database for sessions

## Contributing

When adding new features to the AI assistant:

1. Update models.py if new data structures needed
2. Add API endpoints in views.py
3. Create/update serializers in serializers.py
4. Add frontend API functions in api.ts
5. Update context if new state needed
6. Add UI components as needed
7. Update this documentation

## License

This AI assistant integration is part of Marcus Custom Bikes e-commerce platform.
