# Architecture Decision Record (ADR)

## ADR-009: AI-Powered Chatbot Integration Architecture

**Status:** Accepted  
**Date:** 13-09-25-11h-00m-00s  
**Session:** Current comprehensive ADR review  
**Todo:** Complete architectural documentation  
**Deciders:** Will Robinson, Development Team

### Context

The CRM application required intelligent conversational capabilities to:

- **Query CRM Data**: Natural language queries about companies, contacts, opportunities, and tasks
- **Provide Context**: Leverage existing CRM data to answer business questions
- **Real-time Interaction**: WebSocket-based chat interface with immediate responses
- **AI Integration**: Connect with Large Language Models for intelligent responses
- **Vector Search**: Implement semantic search across CRM entities
- **Privacy Considerations**: Keep sensitive CRM data on-premises

Key challenges included:
- **Architecture Complexity**: Adding AI capabilities without disrupting core CRM functionality
- **Technology Integration**: Combining traditional web UI with real-time chat and AI services
- **Data Access**: Enabling AI to query CRM database while maintaining data integrity
- **Performance**: Real-time response requirements for chat interface
- **Scalability**: AI service resource requirements and scaling considerations

### Decision

**We will implement an embedded AI-powered chatbot with RAG (Retrieval Augmented Generation) architecture:**

1. **Separate FastAPI Service**: Dedicated microservice for chat and AI capabilities
2. **RAG Architecture**: Combine vector search with CRM database queries for context
3. **Local AI Stack**: Ollama for LLM, Qdrant for vector database, on-premises deployment
4. **WebSocket Integration**: Real-time chat interface embedded in CRM web UI
5. **Shared Database Access**: Chatbot reads from same SQLite database as CRM service
6. **Embedding Pipeline**: Automatic vectorization of CRM entities for semantic search

**Architecture Components:**
```
CRM Web UI → WebSocket → Chatbot Service → Ollama LLM
     ↓                        ↓              ↑
Shared SQLite Database → Embedding Service → Qdrant Vector DB
```

### Rationale

**Primary drivers:**

- **Intelligence Augmentation**: AI-powered insights from existing CRM data
- **User Experience**: Natural language interface for complex CRM queries
- **Privacy**: On-premises AI stack keeps sensitive data internal
- **Integration**: Embedded chat widget maintains CRM workflow context
- **Scalability**: Separate service allows independent scaling of AI capabilities
- **Technology Fit**: FastAPI + WebSocket optimal for real-time AI interactions

**Technical benefits:**

- RAG architecture provides accurate, context-aware responses using CRM data
- Vector search enables semantic similarity queries across entities
- WebSocket integration provides immediate response experience
- Separate service isolation prevents AI resource usage from affecting core CRM
- Local AI deployment ensures data privacy and reduces external dependencies

### Alternatives Considered

- **Option A: Third-party AI API integration** - Rejected due to data privacy concerns and external dependencies
- **Option B: Embedded chatbot in Flask** - Rejected due to WebSocket limitations and AI service resource requirements
- **Option C: Rule-based chatbot** - Rejected due to limited intelligence and inflexibility
- **Option D: External AI service** - Rejected due to network latency and data security requirements

### Consequences

**Positive:**

- ✅ **Enhanced User Experience**: Natural language queries for complex CRM operations
- ✅ **Data Privacy**: On-premises AI stack keeps sensitive business data internal
- ✅ **Contextual Intelligence**: RAG architecture provides accurate, CRM-data-informed responses
- ✅ **Real-time Interaction**: WebSocket interface enables immediate chat experience
- ✅ **Semantic Search**: Vector search discovers relevant entities beyond keyword matching
- ✅ **Independent Scaling**: AI service resources can scale without affecting CRM performance

**Negative:**

- ➖ **Infrastructure Complexity**: Additional services (Ollama, Qdrant) increase operational overhead
- ➖ **Resource Requirements**: AI models and vector databases consume significant memory and CPU
- ➖ **Development Complexity**: AI integration requires specialized knowledge and debugging
- ➖ **Response Latency**: AI inference adds processing time compared to traditional queries

**Neutral:**

- 🔄 **Embedding Pipeline**: Requires batch processing to vectorize CRM entities
- 🔄 **Model Management**: Need to manage AI model updates and versions
- 🔄 **Query Design**: Balancing AI responses with traditional database queries

### Implementation Notes

**Chatbot Service Architecture:**
```python
# FastAPI service with WebSocket support
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async for message in websocket.iter_text():
        # Process message through RAG engine
        response = await rag_engine.process_query(message)
        await websocket.send_text(response)
```

**RAG Engine Implementation:**
1. **Query Analysis**: Parse natural language query intent
2. **Vector Search**: Find semantically similar CRM entities in Qdrant
3. **Database Query**: Execute specific queries against CRM database
4. **Context Assembly**: Combine vector search results with database data
5. **LLM Generation**: Send context to Ollama for intelligent response generation
6. **Response Formatting**: Structure response for chat interface display

**Service Integration Pattern:**
```javascript
// Embedded chat widget in CRM UI
const chatSocket = new WebSocket('ws://localhost:8020/ws/chat');
chatSocket.onmessage = (event) => {
    displayChatMessage(JSON.parse(event.data));
};
```

**AI Stack Configuration:**
- **Ollama**: Local LLM service with configurable models (llama2, codellama, etc.)
- **Qdrant**: Vector database for entity embeddings and semantic search
- **Embedding Service**: Automatic vectorization of companies, contacts, opportunities, tasks
- **Configuration**: Environment-based AI service endpoints with fallback handling

**Data Flow:**
1. **Entity Creation/Update**: CRM service triggers embedding generation
2. **Vector Storage**: Embeddings stored in Qdrant with entity metadata
3. **Chat Query**: User sends natural language query via WebSocket
4. **Semantic Search**: Query vectorized and matched against entity embeddings
5. **Context Retrieval**: Relevant entities fetched from CRM database
6. **AI Response**: Context sent to LLM for intelligent response generation
7. **Response Display**: Formatted response shown in chat interface

**Privacy and Security:**
- All AI processing occurs on-premises (no external API calls)
- CRM database access read-only for chatbot service
- WebSocket connections use same authentication as web UI
- Entity embeddings contain no sensitive content (only metadata)

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-11h-00m-00s | Current | ADR review | Initial creation | Document AI chatbot architecture | Establish AI integration and privacy standards |

---

**Impact Assessment:** High - This introduces AI capabilities and significantly enhances user interaction patterns.

**Review Required:** Yes - Team must understand AI service integration, privacy implications, and troubleshooting approaches.

**Next Steps:**
1. Implement chatbot service health monitoring and graceful degradation
2. Create embedding pipeline automation for new CRM entities
3. Develop AI response quality metrics and improvement processes
4. Consider advanced RAG techniques (query expansion, re-ranking) for improved accuracy
5. Plan AI model update and management procedures