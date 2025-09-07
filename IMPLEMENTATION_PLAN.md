# CRM + LLM Chatbot Integration - Complete Implementation Plan

## Project Restructure + LLM Integration

### Phase 1: Code Reorganization
**Objective**: Restructure codebase from `app/` to `crm/` + `chatbot/` for clear service separation

**Key Changes**:
- [ ] Rename `app/` directory to `crm/`
- [ ] Update all imports from `from app.*` to `from crm.*`
- [ ] Update Flask configuration paths (templates, static)
- [ ] Test that existing CRM functionality works after restructure

**Files to Modify**:
- `main.py` - Update all import statements
- All files in `crm/` directory - Update relative imports
- Templates if they reference static paths

**Implementation Order**:
1. Create new `crm/` directory structure
2. Move all `app/` contents to `crm/`
3. Update import statements throughout codebase
4. Test Flask app startup and basic functionality
5. Commit restructure before adding LLM features

**Risks**: Import errors, template path issues

### Phase 2: Database Schema Extensions
**Objective**: Add LLM-specific tables while maintaining existing CRM functionality

**Key Changes**:
- [ ] Create new SQLAlchemy models for LLM features
- [ ] Add database migration scripts
- [ ] Implement hybrid structured + JSON schema approach

**Files to Create**:
- `crm/models/meeting.py` - Meeting transcripts and metadata
- `crm/models/extracted_insight.py` - LLM extraction results (JSON data)
- `crm/models/chat_history.py` - Chatbot conversation storage
- `crm/models/embedding.py` - Vector embeddings for semantic search
- `shared/database_config.py` - Shared DB configuration

**Implementation Order**:
1. Design schema with hybrid structured + JSON approach
2. Create new model files with SQLAlchemy definitions
3. Add database migration capability
4. Test schema creation and basic CRUD operations
5. Populate test data for development

**Risks**: Database migration complexity, JSON field queries

### Phase 3: FastAPI Chatbot Service Foundation
**Objective**: Create separate FastAPI service with direct database access

**Key Changes**:
- [ ] Set up FastAPI application structure
- [ ] Configure shared database access with CRM
- [ ] Implement WebSocket for real-time chat
- [ ] Create basic chat interface

**Files to Create**:
- `chatbot/main.py` - FastAPI application entry point
- `chatbot/database.py` - Database connection and session management
- `chatbot/models/` - Mirror CRM models for shared access
- `chatbot/services/chat_handler.py` - WebSocket chat logic
- `chatbot/templates/chat_widget.html` - Floating chat interface
- `chatbot/static/js/chat.js` - WebSocket client
- `chatbot/requirements.txt` - FastAPI, WebSocket, async dependencies

**Implementation Order**:
1. Create FastAPI app with basic health check
2. Configure shared SQLite database access
3. Implement WebSocket endpoint for chat
4. Create basic chat widget UI
5. Test real-time communication between CRM and chatbot

**Risks**: Database concurrency, WebSocket connection stability

### Phase 4: Ollama Integration & LLM Pipeline
**Objective**: Integrate dual Ollama models for extraction and conversation

**Key Changes**:
- [ ] Set up Ollama client for model management
- [ ] Implement dual-model architecture (8B extraction, 70B chat)
- [ ] Create meeting analysis pipeline
- [ ] Add confidence scoring for extractions

**Files to Create**:
- `chatbot/services/ollama_client.py` - Ollama API integration
- `chatbot/services/meeting_analyzer.py` - LLM extraction pipeline
- `chatbot/services/extraction_schemas.py` - JSON schemas for structured output
- `chatbot/services/background_worker.py` - Async processing queue

**Implementation Order**:
1. Install and configure Ollama with required models
2. Create Ollama client with model switching capability
3. Implement structured extraction pipeline
4. Add background processing for meeting analysis
5. Test extraction accuracy with sample meeting data

**Risks**: Model performance, structured output reliability

### Phase 5: Advanced RAG System
**Objective**: Implement semantic search and intelligent context retrieval

**Key Changes**:
- [ ] Add sentence transformers for embeddings
- [ ] Implement vector similarity search
- [ ] Create smart query routing system
- [ ] Build context ranking and relevance scoring

**Files to Create**:
- `chatbot/services/rag_engine.py` - RAG pipeline and context building
- `chatbot/services/embedding_service.py` - Sentence transformer integration
- `chatbot/services/query_router.py` - Simple vs complex query routing
- `chatbot/services/context_builder.py` - Multi-source context assembly

**Implementation Order**:
1. Set up sentence transformers for embeddings
2. Implement vector storage and similarity search
3. Create query routing logic
4. Build context ranking system
5. Test context quality and relevance

**Risks**: Embedding performance, context relevance quality

### Phase 6: CRM Integration & UI Enhancement
**Objective**: Seamlessly integrate chatbot into existing CRM interface

**Key Changes**:
- [ ] Add chat widget to CRM base template
- [ ] Create meeting upload interface
- [ ] Display extracted insights in CRM entities
- [ ] Add meeting management views

**Files to Modify**:
- `crm/templates/base/layout.html` - Add chat widget
- `crm/routes/meetings.py` - Meeting management endpoints
- `crm/templates/meetings/` - Meeting management interface

**Files to Create**:
- `crm/static/js/chatbot_integration.js` - CRM-chatbot communication
- `crm/templates/components/chat_integration.html` - Chat widget component

**Implementation Order**:
1. Add floating chat widget to CRM interface
2. Implement meeting upload and management UI
3. Create extracted insights display in CRM entities
4. Test end-to-end user experience
5. Polish UI/UX and error handling

**Risks**: UI integration complexity, user experience flow

## Final Project Structure
```
/home/will/code/crm/.worktrees/llm/
├── crm/                           # Renamed Flask CRM
│   ├── models/                    # Extended with LLM tables
│   ├── routes/                    # Existing + meeting management
│   ├── templates/                 # Enhanced with chat integration
│   └── static/                    # Chat widget integration
├── chatbot/                       # New FastAPI service
│   ├── main.py                    # FastAPI app
│   ├── services/                  # LLM, RAG, chat services
│   ├── models/                    # Shared model definitions
│   └── templates/                 # Chat widget UI
├── shared/                        # Common utilities
│   ├── database_config.py
│   └── schemas.py
├── main.py                        # CRM entry point
├── chatbot_main.py                # Chatbot entry point
├── requirements.txt               # Updated dependencies
└── IMPLEMENTATION_PLAN.md         # This plan
```

## Success Criteria
- [ ] Meeting transcripts automatically extract structured CRM data
- [ ] Chatbot accurately answers questions using CRM database context
- [ ] Real-time chat integration feels native in CRM interface
- [ ] System operates completely offline with good performance
- [ ] Clean separation allows independent service development/deployment
- [ ] Extraction confidence scoring enables manual review workflow