# Architecture Decision Record (ADR)

## ADR-007: Microservices Architecture with Auto-Port Discovery

**Status:** Accepted  
**Date:** 13-09-25-10h-00m-00s  
**Session:** Current comprehensive ADR review  
**Todo:** Complete architectural documentation  
**Deciders:** Will Robinson, Development Team

### Context

The CRM application evolved from a monolithic Flask app to require additional services (chatbot with AI capabilities). This created several architectural challenges:

- **Service Orchestration**: Need to coordinate multiple services (CRM + Chatbot) in development
- **Port Management**: Multiple services competing for development ports across worktrees
- **Service Discovery**: Services need to find and communicate with each other
- **Development Friction**: Manual port configuration creates developer productivity issues
- **Deployment Complexity**: Different environments require different port strategies
- **AI Service Integration**: Chatbot requires FastAPI, WebSocket support, and AI service connections

The monolithic Flask approach was insufficient for the expanded requirements including real-time chat and AI integration.

### Decision

**We will implement a microservices architecture with intelligent auto-port discovery:**

1. **Core CRM Service**: Flask application with SQLAlchemy ORM and web UI (port range: 5050-5060)
2. **Chatbot Service**: FastAPI application with WebSocket, AI integration (port range: 8020-8070)  
3. **Shared Database**: Single SQLite database shared between services
4. **Auto-Port Discovery**: Services automatically find free ports in designated ranges
5. **Service Orchestration**: `run.sh` script coordinates service startup and health checks
6. **Development Mode**: All services run locally with auto-configuration

**Service Communication Pattern:**
```
CRM Service (Flask) ←→ Shared Database ←→ Chatbot Service (FastAPI)
     ↑                                            ↑
Web Interface                              WebSocket + AI APIs
```

### Rationale

**Primary drivers:**

- **Separation of Concerns**: CRM logic separate from AI/chat capabilities  
- **Technology Fit**: Flask for web UI, FastAPI for real-time chat and AI APIs
- **Development Velocity**: Auto-port discovery eliminates configuration friction
- **Scalability**: Services can scale independently based on load patterns
- **AI Integration**: FastAPI provides better async support for AI service calls
- **Real-time Requirements**: WebSocket support for chat requires different server architecture

**Technical benefits:**

- Clean separation between traditional CRUD operations and AI capabilities
- Independent deployment and scaling of services
- Technology selection optimized per service requirements
- Automatic conflict resolution for development environments
- Easy integration testing with coordinated service startup

### Alternatives Considered

- **Option A: Monolithic Flask with extensions** - Rejected due to WebSocket limitations and AI service integration complexity
- **Option B: Single FastAPI application** - Rejected due to mature Flask codebase and team familiarity
- **Option C: Docker-based services** - Rejected as over-complex for development workflow
- **Option D: Manual port configuration** - Rejected due to development friction and error-proneness

### Consequences

**Positive:**

- ✅ **Technology Optimization**: Each service uses optimal technology stack
- ✅ **Development Productivity**: Auto-port discovery eliminates configuration issues  
- ✅ **Independent Scaling**: Services can be scaled based on specific load patterns
- ✅ **Clear Boundaries**: Well-defined service responsibilities and interfaces
- ✅ **AI Integration**: FastAPI provides superior async support for AI service calls
- ✅ **Real-time Capabilities**: WebSocket support enables rich chat experiences

**Negative:**

- ➖ **Complexity**: Multiple services increase operational and debugging complexity
- ➖ **Resource Usage**: More memory and CPU required for multiple service processes
- ➖ **Service Coordination**: Startup dependencies and health check requirements
- ➖ **Network Latency**: Inter-service communication adds minimal latency

**Neutral:**

- 🔄 **Development Workflow**: Requires orchestrated startup but automated via scripts
- 🔄 **Deployment Strategy**: Need to coordinate deployment of multiple services  
- 🔄 **Monitoring**: Each service requires separate logging and monitoring

### Implementation Notes

**Auto-Port Discovery Algorithm:**
```bash
find_free_port() {
    local start_port=$1
    local max_attempts=${2:-10}
    
    for ((port=start_port; port<start_port+max_attempts; port++)); do
        if ! timeout 1 nc -z localhost $port 2>/dev/null; then
            echo $port
            return 0
        fi
    done
    
    echo "Error: No free port found in range"
    exit 1
}
```

**Service Architecture:**

1. **CRM Service** (`services/crm/main.py`):
   - Flask application with Jinja2 templates
   - SQLAlchemy ORM for database operations
   - Web UI for CRUD operations
   - REST API endpoints for frontend interactions
   - Auto-detects database path (worktree-aware)

2. **Chatbot Service** (`services/chatbot/main.py`):
   - FastAPI application with async support
   - WebSocket endpoints for real-time chat
   - Integration with Ollama LLM service
   - Vector search with Qdrant database
   - RAG (Retrieval Augmented Generation) engine

**Service Startup Coordination:**
```bash
# run.sh orchestration pattern
CRM_PORT=$(find_free_port 5050)
CHATBOT_PORT=$(find_free_port 8020 50)

# Start chatbot service in background
python3 services/chatbot/main.py --port "$CHATBOT_PORT" &
CHATBOT_PID=$!

# Health check chatbot startup
sleep 2
if ! kill -0 $CHATBOT_PID; then
    echo "Failed to start chatbot service"
    exit 1
fi

# Start CRM service (foreground)
python3 services/crm/main.py --port "$CRM_PORT"
```

**Shared Database Strategy:**
- Single SQLite database in `/instance/crm.db`
- Both services connect to same database instance
- CRM service handles schema migrations
- Chatbot service reads entity data for context

**Configuration Management:**
- Environment-based configuration in `services/chatbot/config.py`
- Auto-detection of AI service endpoints (Ollama, Qdrant)
- Graceful fallback when AI services unavailable
- Development vs production configuration profiles

### Version History

| Date | Session | Todo | Commit | Changes | Rationale |
|------|---------|------|--------|---------|-----------|
| 13-09-25-10h-00m-00s | Current | ADR review | Initial creation | Document microservices architecture | Establish service coordination standards |

---

**Impact Assessment:** High - This is a foundational architectural decision affecting deployment, development, and scaling strategies.

**Review Required:** Yes - Team must understand service coordination, port management, and inter-service communication patterns.

**Next Steps:**
1. Create service health check and monitoring strategy
2. Implement service discovery for production environments  
3. Add graceful degradation when optional services (chatbot) unavailable
4. Consider container orchestration for production deployment