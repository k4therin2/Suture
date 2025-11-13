# System Design Interview: Web Scraping Multi-Agent Framework

**Interview Problem**: Design a self-healing, multi-agent web scraping system that can automatically adapt to website changes and integrate with other AI systems.

---

## Part 1: Clarifying Questions (5-10 minutes)

> **Key Skill**: Gather requirements before jumping to solutions. Show you understand business context and constraints.

### Questions to Ask the Interviewer

**Scope & Scale**:
- Q: "How many websites/platforms do we need to support? 10s, 100s, 1000s?"
  - A: Start with 10-20 major platforms (Slack, Reddit, etc.), grow to 100+
- Q: "What's the expected request volume? Scrapes per day?"
  - A: 1000-10K scrapes/day initially, potentially 100K+ as we scale
- Q: "Are scrapes one-off or recurring? Do we need scheduling?"
  - A: Both. Ad-hoc requests + scheduled refreshes every 1-24 hours

**Data & Integration**:
- Q: "Who are the consumers? Is this a library, API service, or both?"
  - A: Primary consumer is an AI assistant (Marvin), but should be reusable as library/API
- Q: "Do we store scraped data or just return it to callers?"
  - A: TBD - need to design for both options
- Q: "What data volumes per scrape? KB, MB, GB?"
  - A: Typically 1-10MB of structured data per scrape (100-1000 items)

**Reliability & Performance**:
- Q: "What's acceptable latency? Real-time or batch?"
  - A: Async is fine. 30s-5min per scrape is acceptable
- Q: "Availability requirements? Is this user-facing or backend?"
  - A: Backend service. 95% availability is fine initially
- Q: "What happens when websites change structure? How quickly must we adapt?"
  - A: This is the key feature - should auto-heal within 1-3 attempts

**Constraints**:
- Q: "Budget constraints? Can we use cloud LLMs or local only?"
  - A: Hybrid approach - prefer local models, use cloud for complex reasoning
- Q: "Legal/compliance requirements around web scraping?"
  - A: Assume user is responsible for ToS compliance. We provide tools, not guarantees

---

## Part 2: Requirements Definition (5 minutes)

### Functional Requirements

**Core Features** (P0):
1. **Multi-platform scraping**: Support 10-20 platforms out of the box
2. **Self-healing**: Automatically recover from website structure changes
3. **Data validation**: Ensure extracted data meets quality standards
4. **Conversational interface**: AI agents can request scrapes via natural language
5. **Authentication handling**: Support cookies, sessions, API tokens

**Extended Features** (P1):
6. **Platform extensibility**: Developers can add new platforms easily
7. **Human-in-the-loop**: Escalate to humans when confidence is low
8. **Scheduled refreshes**: Keep data fresh automatically
9. **Code repository management**: Store vetted scrapers in version control

**Nice-to-Have** (P2):
10. **Semantic search**: Index scraped data with embeddings
11. **Multi-tenancy**: Support multiple users/teams
12. **Rate limiting & throttling**: Respect website limits

### Non-Functional Requirements

| Requirement | Target | Measurement |
|------------|--------|-------------|
| **Latency (p95)** | < 5 minutes per scrape | End-to-end scraping time |
| **Availability** | 95% uptime | Service availability |
| **Success Rate** | 90% without human intervention | Scrapes succeeding after auto-recovery |
| **Self-Healing Rate** | 70% of failures auto-fixed | Recovery agent success rate |
| **Throughput** | 1000 scrapes/day initially | Concurrent scrape capacity |
| **Consistency** | Exactly-once data extraction | No duplicate items |
| **Observability** | 100% of operations traced | LangSmith coverage |

### Scale Estimates

**Initial Scale** (Year 1):
- 10 platforms
- 1,000 scrapes/day = ~40/hour = 0.01/sec
- ~1 GB/day scraped data
- 10 concurrent scrapes

**Growth Scale** (Year 2-3):
- 100+ platforms
- 100,000 scrapes/day = ~4,000/hour = ~1/sec
- ~100 GB/day scraped data
- 100 concurrent scrapes

---

## Part 3: High-Level Architecture (10 minutes)

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL CONSUMERS                        │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐            │
│  │ Marvin   │     │ Data     │     │ Direct   │            │
│  │ AI Agent │     │ Pipeline │     │ API      │            │
│  │          │     │          │     │ Clients  │            │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘            │
└───────┼────────────────┼────────────────┼──────────────────┘
        │                │                │
        └────────────────┴────────────────┘
                         │
                         ▼
        ╔════════════════════════════════════════╗
        ║          MCP/API GATEWAY               ║
        ║  - Authentication                      ║
        ║  - Rate limiting                       ║
        ║  - Request routing                     ║
        ╚════════════════════════════════════════╝
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Director    │ │  Scraper     │ │  Recovery    │
│  Agent       │→│  Agent       │→│  Agent       │
│  (Planning)  │ │  (Coding)    │ │  (Healing)   │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
        ╔════════════════════════════════════════╗
        ║       EXECUTION LAYER                  ║
        ║  ┌──────────────┐  ┌──────────────┐   ║
        ║  │ Playwright   │  │ Task Queue   │   ║
        ║  │ Browser Pool │  │ (Redis)      │   ║
        ║  └──────────────┘  └──────────────┘   ║
        ╚════════════════════════════════════════╝
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │   Redis      │ │  S3/Blob     │
│  (Metadata)  │ │  (Cache)     │ │  (Raw Data)  │
└──────────────┘ └──────────────┘ └──────────────┘
                         │
                         ▼
        ╔════════════════════════════════════════╗
        ║         OBSERVABILITY                  ║
        ║  LangSmith | Prometheus | Grafana     ║
        ╚════════════════════════════════════════╝
```

### Component Breakdown

| Component | Technology | Purpose | Scaling Strategy |
|-----------|-----------|---------|------------------|
| **API Gateway** | FastAPI + Nginx | Request routing, auth, rate limiting | Horizontal (stateless) |
| **Director Agent** | LangChain + Claude Haiku | Orchestration, planning | Horizontal (stateless) |
| **Scraper Agent** | LangChain + Claude Sonnet | Playwright code generation | Horizontal (stateless) |
| **Recovery Agent** | LangChain + Claude Sonnet | Self-healing logic | Horizontal (stateless) |
| **Browser Pool** | Playwright + Docker | Execute scraping scripts | Horizontal (containerized) |
| **Task Queue** | Redis + Celery | Async job processing | Horizontal (workers) |
| **Metadata DB** | PostgreSQL | Job status, configs, results index | Vertical → Read replicas |
| **Data Storage** | S3 / MinIO | Raw scraped data (JSON blobs) | Object storage (infinite) |
| **Cache** | Redis | Scripts, selectors, sessions | Horizontal (cluster) |
| **Tracing** | LangSmith | LLM call tracing | SaaS |
| **Metrics** | Prometheus + Grafana | System metrics, alerts | Vertical |

---

## Part 4: API Design (5 minutes)

### REST API

```python
# Async scraping (preferred)
POST /api/v1/scrape
{
  "platform": "slack",
  "url": "https://app.slack.com/client/T123/C456",
  "query": "in:#engineering after:1730800000",
  "priority": "normal",  // high | normal | low
  "options": {
    "limit": 100,
    "auth_method": "cookies_from_profile"
  }
}
→ Response: 202 Accepted
{
  "job_id": "scrape_abc123",
  "status": "queued",
  "estimated_time_sec": 45,
  "status_url": "/api/v1/jobs/scrape_abc123"
}

# Check job status
GET /api/v1/jobs/{job_id}
→ Response: 200 OK
{
  "job_id": "scrape_abc123",
  "status": "completed",  // queued | running | completed | failed
  "progress": {
    "current_step": "validation",
    "percent_complete": 90
  },
  "result": {
    "items_extracted": 47,
    "confidence": 0.95,
    "data_url": "/api/v1/jobs/scrape_abc123/data"
  },
  "metadata": {
    "started_at": "2025-11-13T10:00:00Z",
    "completed_at": "2025-11-13T10:00:42Z",
    "execution_time_ms": 42000,
    "attempts": 1,
    "trace_url": "https://smith.langchain.com/..."
  }
}

# Get scraped data
GET /api/v1/jobs/{job_id}/data
→ Response: 200 OK
{
  "items": [
    {
      "id": "slack_eng_alice_1730800800",
      "channel": "#engineering",
      "author": "Alice",
      "text": "Found a critical bug...",
      "timestamp": "2025-11-05T09:00:00Z",
      "url": "https://slack.com/archives/..."
    },
    // ... 46 more
  ],
  "metadata": {
    "total_items": 47,
    "schema_version": "1.0"
  }
}

# List supported platforms
GET /api/v1/platforms
→ Response: 200 OK
{
  "platforms": [
    {
      "name": "slack",
      "status": "stable",
      "auth_methods": ["cookies", "oauth"],
      "capabilities": ["search", "channel_scrape", "thread_scrape"],
      "schema": { /* ... */ }
    },
    // ...
  ]
}

# Health check
GET /api/v1/health
→ Response: 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "components": {
    "api": "healthy",
    "workers": "healthy (5 available)",
    "database": "healthy",
    "browser_pool": "healthy (3/5 browsers active)"
  }
}
```

### MCP Interface (for Marvin integration)

```python
# MCP Tools exposed to Marvin

@server.tool()
async def request_scrape(
    platform: str,
    url: str,
    query: Optional[str] = None
) -> Dict:
    """Request Suture to scrape data. Returns job_id."""

@server.tool()
async def get_scrape_status(job_id: str) -> Dict:
    """Check status of a scraping job."""

@server.tool()
async def get_fresh_data(
    platform: str,
    query: str,
    max_age_hours: int = 24
) -> Dict:
    """Get data, refreshing if stale."""

@server.tool()
async def ask_director(question: str) -> str:
    """Ask Suture's Director Agent a question."""
```

---

## Part 5: Data Model (5 minutes)

### PostgreSQL Schema

```sql
-- Scraping jobs
CREATE TABLE scrape_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    query JSONB,  -- Platform-specific query parameters

    -- Status
    status VARCHAR(20) NOT NULL,  -- queued | running | completed | failed
    priority VARCHAR(10) DEFAULT 'normal',  -- high | normal | low

    -- Execution metadata
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_ms INTEGER,
    attempts INTEGER DEFAULT 0,

    -- Results
    items_extracted INTEGER,
    confidence DECIMAL(3,2),  -- 0.00 to 1.00
    data_location TEXT,  -- S3 URL or similar

    -- Tracing
    trace_url TEXT,
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_status (status),
    INDEX idx_platform_created (platform, created_at),
    INDEX idx_created (created_at DESC)
);

-- Platform configurations
CREATE TABLE platforms (
    platform_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'experimental',  -- stable | experimental | deprecated

    -- Config
    config JSONB NOT NULL,  -- YAML config as JSON
    schema JSONB NOT NULL,  -- Expected data schema

    -- Code references
    scraper_version VARCHAR(50),  -- Git commit hash
    healer_version VARCHAR(50),

    -- Metrics
    total_scrapes INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),  -- Last 100 scrapes
    avg_execution_time_ms INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cached scripts (working Playwright code)
CREATE TABLE script_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    url_pattern TEXT NOT NULL,  -- Regex or glob pattern

    script TEXT NOT NULL,  -- Playwright code
    selectors JSONB,  -- CSS selectors that work

    -- Validity tracking
    last_successful_use TIMESTAMP NOT NULL,
    total_uses INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- TTL, e.g., 7 days

    INDEX idx_platform_pattern (platform, url_pattern),
    INDEX idx_last_used (last_successful_use DESC)
);

-- Recovery attempts (learning from failures)
CREATE TABLE recovery_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES scrape_jobs(job_id),
    attempt_number INTEGER NOT NULL,

    -- Diagnosis
    error_type VARCHAR(50),  -- selector_not_found | auth_expired | timeout | ...
    diagnosis TEXT,

    -- Recovery strategy
    strategy VARCHAR(50),  -- alternative_selectors | computer_use | human_loop

    -- Outcome
    success BOOLEAN,
    execution_time_ms INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Human validations (for learning)
CREATE TABLE human_validations (
    validation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES scrape_jobs(job_id),

    -- What we showed to human
    proposed_data JSONB,
    confidence DECIMAL(3,2),

    -- Human feedback
    approved BOOLEAN,
    corrections JSONB,  -- What human changed
    feedback TEXT,

    validated_by VARCHAR(100),
    validated_at TIMESTAMP DEFAULT NOW()
);
```

### Data Storage Strategy

| Data Type | Storage | Retention | Rationale |
|-----------|---------|-----------|-----------|
| **Job metadata** | PostgreSQL | 90 days | Fast queries, relational |
| **Scraped data (JSON)** | S3/MinIO | 365 days | Cheap, scalable, append-only |
| **Scripts (code)** | Redis (hot) + Postgres (warm) | 7 days (Redis), 90 days (Postgres) | Fast retrieval, fallback |
| **Screenshots (debug)** | S3 | 30 days | Large files, rarely accessed |
| **Embeddings** | ChromaDB / Pinecone | Optional | Semantic search (if needed) |
| **Logs** | CloudWatch / Loki | 30 days | Operational debugging |
| **Traces** | LangSmith | 90 days | LLM call debugging |

---

## Part 6: Deep Dives (15-20 minutes)

### 6.1 Multi-Agent Orchestration with LangGraph

**Challenge**: How do we coordinate 7 specialized agents with complex branching logic?

**Solution**: LangGraph state machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class ScraperState(TypedDict):
    # Input
    job_id: str
    platform: str
    url: str
    query: Optional[str]

    # Workflow state
    current_step: str
    attempts: int
    max_attempts: int

    # Data
    script: Optional[str]
    raw_data: List[Dict]
    validated_data: List[Dict]

    # Quality
    confidence: Optional[float]
    errors: List[str]

# Define workflow
workflow = StateGraph(ScraperState)

# Add nodes (agents)
workflow.add_node("director", director_agent)
workflow.add_node("scraper_coding", scraper_coding_agent)
workflow.add_node("executor", script_executor)
workflow.add_node("validator", validator_agent)
workflow.add_node("recovery", recovery_agent)
workflow.add_node("schema_manager", schema_manager_agent)

# Define edges (transitions)
workflow.set_entry_point("director")
workflow.add_edge("director", "scraper_coding")
workflow.add_edge("scraper_coding", "executor")

# Conditional branching after validation
def should_recover(state):
    return state["confidence"] < 0.8 and state["attempts"] < state["max_attempts"]

workflow.add_conditional_edges(
    "validator",
    should_recover,
    {
        True: "recovery",
        False: "schema_manager"
    }
)

workflow.add_edge("recovery", "scraper_coding")  # Retry loop
workflow.add_edge("schema_manager", END)

app = workflow.compile()
```

**Why LangGraph**?
- ✅ Built-in state persistence (checkpointing)
- ✅ Automatic tracing to LangSmith
- ✅ Handles agent failures gracefully
- ✅ Easy to visualize workflow
- ❌ Learning curve for team
- ❌ Vendor lock-in to LangChain ecosystem

**Alternative Considered**: Temporal.io
- ✅ Better for long-running workflows
- ✅ Industry-standard durable execution
- ❌ Doesn't integrate with LLM tracing
- ❌ More operational overhead

**Decision**: LangGraph for MVP, consider Temporal if workflows become very long-running (hours/days).

---

### 6.2 Self-Healing: Recovery Agent Design

**Challenge**: Websites change their HTML structure unpredictably. How do we auto-recover?

**Recovery Strategy Chain**:

```python
class RecoveryAgent:
    """Attempts to fix scraping failures."""

    async def recover(self, error: Exception, state: ScraperState) -> RecoveryResult:
        """Try recovery strategies in order of cost/speed."""

        strategies = [
            AlternativeSelectorStrategy(),      # Fast, cheap
            VisualDetectionStrategy(),          # Slow, expensive
            HumanInLoopStrategy(),              # Slowest, most reliable
        ]

        for strategy in strategies:
            if await strategy.can_handle(error):
                result = await strategy.recover(error, state)

                if result.success:
                    # Cache the working solution
                    await self.cache_successful_recovery(state.platform, result)
                    return result

        # All strategies failed
        return RecoveryResult(success=False, escalate_to_human=True)

class AlternativeSelectorStrategy:
    """Try alternative CSS selectors from platform healer."""

    async def recover(self, error, state):
        # Load platform-specific healer
        healer = await load_healer(state.platform)

        # Get alternative selectors
        alternatives = healer.suggest_alternatives(
            failed_selector=self.extract_failed_selector(error),
            context=state
        )

        # Generate new script with alternatives
        new_script = await scraper_agent.generate_script(
            platform=state.platform,
            url=state.url,
            selectors=alternatives
        )

        return RecoveryResult(
            success=True,
            new_script=new_script,
            confidence=0.7,  # Medium confidence
            cost_usd=0.001   # Cheap LLM call
        )

class VisualDetectionStrategy:
    """Use Claude Computer Use to visually identify elements."""

    async def recover(self, error, state):
        # Take screenshot
        screenshot = await self.capture_screenshot(state.url)

        # Ask Claude Computer Use to identify elements
        prompt = f"""
        The webpage has changed. These selectors no longer work:
        {self.extract_failed_selector(error)}

        Looking at this screenshot, identify where the messages/data are located.
        Suggest new CSS selectors or XPath expressions.
        """

        response = await anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": screenshot},
                    {"type": "text", "text": prompt}
                ]
            }],
            tools=[computer_use_tool]
        )

        # Extract suggested selectors from response
        new_selectors = self.parse_selector_suggestions(response)

        return RecoveryResult(
            success=True,
            new_selectors=new_selectors,
            confidence=0.85,
            cost_usd=0.50  # Expensive
        )
```

**Caching Strategy**:
When a recovery succeeds, cache it:

```python
await redis.setex(
    key=f"script:{platform}:{url_pattern}",
    value=working_script,
    expiry=7 * 24 * 60 * 60  # 7 days
)
```

Next scrape checks cache first before generating new code.

**Metrics to Track**:
- Recovery success rate by strategy
- Time to recover (p50, p95, p99)
- Cost per recovery attempt
- Cache hit rate

---

### 6.3 Scalability: Browser Pool Management

**Challenge**: Playwright browsers are resource-intensive (500MB+ RAM each). How do we scale to 100 concurrent scrapes?

**Solution**: Pooled browser management with containerization

```python
class BrowserPool:
    """Manages a pool of Playwright browser instances."""

    def __init__(self, max_browsers: int = 10):
        self.max_browsers = max_browsers
        self.available = asyncio.Queue()
        self.in_use = set()
        self.metrics = BrowserPoolMetrics()

    async def acquire(self, timeout: int = 30) -> Browser:
        """Get an available browser or wait."""
        try:
            browser = await asyncio.wait_for(
                self.available.get(),
                timeout=timeout
            )
            self.in_use.add(browser)
            self.metrics.browsers_in_use.inc()
            return browser

        except asyncio.TimeoutError:
            # Pool exhausted, scale up if under limit
            if len(self.in_use) < self.max_browsers:
                browser = await self._create_browser()
                self.in_use.add(browser)
                return browser
            else:
                raise PoolExhaustedError("No browsers available")

    async def release(self, browser: Browser):
        """Return browser to pool."""
        # Reset browser state
        await self._cleanup_browser(browser)

        self.in_use.remove(browser)
        await self.available.put(browser)
        self.metrics.browsers_in_use.dec()

    async def _create_browser(self) -> Browser:
        """Launch a new browser instance."""
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        self.metrics.total_browsers_created.inc()
        return browser

    async def _cleanup_browser(self, browser: Browser):
        """Clear cookies, cache, sessions."""
        # Close all pages except one blank page
        pages = browser.contexts[0].pages
        for page in pages[1:]:
            await page.close()

        # Clear cookies
        await browser.contexts[0].clear_cookies()
```

**Deployment Strategy**:

```yaml
# docker-compose.yml
services:
  suture-api:
    image: suture-api:latest
    replicas: 3
    resources:
      limits:
        memory: 1GB
        cpus: '0.5'

  suture-worker:
    image: suture-worker:latest
    replicas: 5  # Scale based on load
    environment:
      - MAX_BROWSERS_PER_WORKER=2
    resources:
      limits:
        memory: 2GB  # 500MB per browser × 2 + overhead
        cpus: '1.0'

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

**Auto-scaling Rules**:
- Scale up workers if queue depth > 50 jobs
- Scale down if queue depth < 10 for 5 minutes
- Max workers: 20 (cost limit)

**Resource Estimates**:
- 1 browser instance: ~500MB RAM, 0.1 CPU
- 1 worker (2 browsers): 2GB RAM, 1 CPU
- 10 workers (100 concurrent): 20GB RAM, 10 CPUs
- Cost: ~$100-200/month (AWS EC2 c5.2xlarge × 2)

---

### 6.4 Observability & Debugging

**Challenge**: LLM-based systems are non-deterministic. How do we debug when things go wrong?

**Observability Stack**:

```
┌─────────────────────────────────────────────────────────┐
│                 OBSERVABILITY LAYERS                     │
├─────────────────────────────────────────────────────────┤
│ 1. LLM Tracing      → LangSmith                         │
│ 2. Application Logs → CloudWatch / Loki                 │
│ 3. Metrics          → Prometheus + Grafana              │
│ 4. APM              → DataDog / New Relic               │
│ 5. Alerting         → PagerDuty                         │
└─────────────────────────────────────────────────────────┘
```

**Key Metrics**:

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Scraping metrics
scrapes_total = Counter(
    'suture_scrapes_total',
    'Total scrapes attempted',
    ['platform', 'status']  # labels
)

scrape_duration = Histogram(
    'suture_scrape_duration_seconds',
    'Time to complete scrape',
    ['platform'],
    buckets=[1, 5, 10, 30, 60, 120, 300]  # seconds
)

# Self-healing metrics
recovery_attempts = Counter(
    'suture_recovery_attempts_total',
    'Recovery attempts',
    ['platform', 'strategy', 'success']
)

recovery_cost = Histogram(
    'suture_recovery_cost_usd',
    'Cost of recovery attempts',
    ['strategy'],
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
)

# Resource metrics
browser_pool_size = Gauge(
    'suture_browser_pool_available',
    'Available browsers in pool'
)

queue_depth = Gauge(
    'suture_queue_depth',
    'Jobs waiting in queue',
    ['priority']
)

# Business metrics
data_freshness = Gauge(
    'suture_data_age_hours',
    'Age of data since last scrape',
    ['platform', 'dataset']
)
```

**Structured Logging**:

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "scrape_started",
    job_id=job_id,
    platform=platform,
    url=url,
    trace_url=trace_url
)

logger.warning(
    "recovery_triggered",
    job_id=job_id,
    error_type="selector_not_found",
    attempt=2,
    strategy="visual_detection"
)

logger.error(
    "scrape_failed",
    job_id=job_id,
    error=str(error),
    attempts=3,
    escalated_to_human=True
)
```

**Dashboards** (Grafana):
1. **Executive Dashboard**: Success rate, throughput, cost/scrape
2. **Ops Dashboard**: Queue depth, worker health, error rates
3. **Self-Healing Dashboard**: Recovery success by strategy, cost trends
4. **Platform Dashboard**: Per-platform metrics, selector health

**Alerts**:
```yaml
alerts:
  - name: HighFailureRate
    expr: rate(suture_scrapes_total{status="failed"}[5m]) > 0.2
    severity: warning
    message: "Scrape failure rate > 20% for 5 minutes"

  - name: RecoveryNotWorking
    expr: rate(suture_recovery_attempts_total{success="false"}[10m]) > 0.5
    severity: critical
    message: "Recovery failing for > 50% of attempts"

  - name: QueueBacklog
    expr: suture_queue_depth > 100
    severity: warning
    message: "Queue depth > 100 jobs, consider scaling workers"
```

---

## Part 7: Trade-offs & Alternatives (5 minutes)

### Key Design Decisions

| Decision | Choice | Alternative | Trade-off Rationale |
|----------|--------|-------------|---------------------|
| **Orchestration** | LangGraph | Temporal.io, Airflow | LangGraph integrates with LLM tracing, simpler for short workflows |
| **LLM Provider** | Hybrid (local + cloud) | All cloud, all local | Balance cost vs quality; use cheap models for simple tasks |
| **Data Storage** | PostgreSQL + S3 | All in Postgres, MongoDB | Relational for metadata, object storage for blobs |
| **Browser Automation** | Playwright | Selenium, Puppeteer | Modern, supports multiple browsers, good Python support |
| **Task Queue** | Redis + Celery | RabbitMQ, SQS | Simplicity, already using Redis for cache |
| **API Style** | REST (async) | GraphQL, gRPC | REST is simple, widely understood; async for long-running jobs |
| **Deployment** | Docker Compose → K8s | Serverless (Lambda) | Need stateful browser instances, hard to do serverless |

### Scaling Strategy

**Vertical Scaling Limits**:
- Single worker: 2 browsers, ~2GB RAM
- Single machine: 20 browsers, ~20GB RAM, ~$100/mo

**Horizontal Scaling Approach**:
```
Phase 1 (0-1K scrapes/day):    1 API server, 2 workers, 1 Redis, 1 Postgres
Phase 2 (1-10K scrapes/day):   3 API servers, 5 workers, Redis cluster, Postgres replicas
Phase 3 (10-100K scrapes/day): 5+ API servers, 20+ workers, Kubernetes, managed Redis/Postgres
```

**Bottlenecks to Watch**:
1. **Browser pool exhaustion**: Scale workers horizontally
2. **PostgreSQL writes**: Add read replicas, partition by platform
3. **LLM rate limits**: Implement backoff, queue management
4. **Network I/O**: Use CDN for static assets, compress responses

---

## Part 8: Reliability & Failure Modes (5 minutes)

### Failure Scenarios

| Failure | Impact | Mitigation | Detection |
|---------|--------|------------|-----------|
| **Browser crashes** | Scrape fails | Pool recreates browser, retry job | Health checks, monitor browser exit codes |
| **Website down** | Scrape fails | Exponential backoff, retry later | HTTP status codes |
| **Selector changed** | Data extraction fails | Recovery agent auto-heals | Validation confidence < threshold |
| **Auth expired** | Scrape fails | Detect auth error, request re-auth | Error pattern matching |
| **LLM API down** | Can't generate scripts | Fallback to cached scripts | API health check, circuit breaker |
| **Database down** | Can't save results | Queue in memory, flush when DB recovers | Connection pool monitoring |
| **Worker OOM** | Worker crashes | Set memory limits, restart worker | Container OOM events |
| **Infinite loop** | Worker hangs | Timeout on all operations | Job timeout alerts |

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    reraise=True
)
async def execute_scrape(job_id: str):
    """Execute scrape with exponential backoff retry."""
    # Attempt 1: immediate
    # Attempt 2: wait 4-8 seconds
    # Attempt 3: wait 16-32 seconds
    pass
```

### Circuit Breaker (for external LLM APIs)

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_llm(prompt: str):
    """Call LLM with circuit breaker protection.

    If 5 consecutive failures, circuit opens for 60 seconds.
    During open circuit, return cached response or fail fast.
    """
    pass
```

### Data Consistency

**Problem**: Scrape succeeds, but saving to database fails.

**Solution**: Write-ahead log pattern
```python
async def save_results(job_id: str, data: List[Dict]):
    # 1. Write to S3 first (durable)
    s3_url = await s3.put_object(f"scrapes/{job_id}.json", data)

    # 2. Update database with S3 reference
    try:
        await db.execute(
            "UPDATE scrape_jobs SET data_location = $1, status = 'completed' WHERE job_id = $2",
            s3_url, job_id
        )
    except Exception as e:
        # Data is safe in S3, can reconcile later
        logger.error("db_update_failed", job_id=job_id, s3_url=s3_url, error=e)
        # Async worker will retry DB update
        await queue.enqueue_retry(job_id)
```

---

## Part 9: Security & Compliance (5 minutes)

### Security Considerations

**1. Authentication & Authorization**:
```python
# API requires API key or OAuth token
@app.post("/api/v1/scrape")
async def scrape(request: ScrapeRequest, api_key: str = Header(...)):
    user = await authenticate(api_key)

    # Check if user has permission for this platform
    if not await authorize(user, request.platform):
        raise HTTPException(403, "Not authorized for this platform")
```

**2. Secrets Management**:
- Store cookies/tokens in encrypted vault (AWS Secrets Manager, HashiCorp Vault)
- Never log sensitive data (cookies, passwords, API keys)
- Rotate credentials regularly

**3. Network Security**:
```yaml
# Browsers run in isolated network
services:
  suture-worker:
    networks:
      - browser-network  # Isolated, no internet access for workers

  proxy:
    image: squid-proxy  # Workers access web through proxy
    networks:
      - browser-network
      - internet
```

**4. Rate Limiting**:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_api_key)

@app.post("/api/v1/scrape")
@limiter.limit("100/hour")  # 100 scrapes per hour per API key
async def scrape():
    pass
```

**5. Data Privacy**:
- Encrypt data at rest (S3 encryption)
- Encrypt data in transit (TLS)
- PII detection and masking
- GDPR compliance (right to deletion)

### Legal & Compliance

**robots.txt Compliance**:
```python
from urllib.robotparser import RobotFileParser

async def check_robots_txt(url: str) -> bool:
    """Check if scraping is allowed by robots.txt."""
    parser = RobotFileParser()
    parser.set_url(f"{get_domain(url)}/robots.txt")
    parser.read()

    if not parser.can_fetch("SutureBot", url):
        raise RobotsDisallowedError(f"robots.txt disallows scraping {url}")
```

**Rate Limiting (Respectful Scraping)**:
- Default: 1 request per 2 seconds per domain
- Configurable per platform
- Exponential backoff on 429 (Too Many Requests)

**Terms of Service**:
- User responsible for compliance
- Suture provides tools, not guarantees
- Log user acknowledgment of ToS

---

## Part 10: Testing Strategy (5 minutes)

### Testing Pyramid

```
         ┌─────────────┐
         │     E2E     │  ← 5% (expensive, slow)
         │   Tests     │     Real websites, full workflow
         └─────────────┘
       ┌──────────────────┐
       │   Integration    │  ← 25% (moderate cost/speed)
       │      Tests       │     Mock LLMs, real browsers
       └──────────────────┘
    ┌──────────────────────────┐
    │      Unit Tests          │  ← 70% (cheap, fast)
    │                          │     Pure functions, mocked dependencies
    └──────────────────────────┘
```

### Test Types

**1. Unit Tests** (70%):
```python
def test_selector_extraction():
    """Test that we correctly extract failed selectors from errors."""
    error = "Error: Selector '.c-virtual_list__item' not found"
    selector = extract_failed_selector(error)
    assert selector == ".c-virtual_list__item"

def test_recovery_strategy_selection():
    """Test that we select the right recovery strategy."""
    error = SelectorNotFoundError("...")
    strategy = select_recovery_strategy(error, attempts=1)
    assert isinstance(strategy, AlternativeSelectorStrategy)
```

**2. Integration Tests** (25%):
```python
@pytest.mark.integration
async def test_slack_scraping_with_mock_llm():
    """Test Slack scraping with mocked LLM responses."""
    # Mock LLM to return predictable script
    with mock_llm_response(script=SAMPLE_PLAYWRIGHT_SCRIPT):
        scraper = Scraper(slack_config)
        results = await scraper.scrape(url=SLACK_TEST_URL)

        assert len(results) > 0
        assert all('text' in r for r in results)

@pytest.mark.integration
async def test_recovery_agent_with_real_llm():
    """Test recovery agent with real LLM (uses quota)."""
    # Use a page with intentionally broken selectors
    scraper = Scraper(test_config)
    results = await scraper.scrape(url=BROKEN_SELECTOR_PAGE)

    # Should auto-recover
    assert results.recovered == True
    assert results.attempts > 1
```

**3. E2E Tests** (5%):
```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_full_slack_workflow():
    """Test complete workflow against real Slack (requires auth)."""
    config = SutureConfig.from_yaml("platforms/slack/config.yaml")
    scraper = Scraper(config)

    results = await scraper.scrape(
        url=os.getenv("SLACK_TEST_URL"),
        query="in:#test-channel after:yesterday"
    )

    assert len(results) > 0
    assert results.confidence > 0.8
```

**4. Chaos Testing**:
```python
@pytest.mark.chaos
async def test_browser_crash_recovery():
    """Simulate browser crash during scrape."""
    scraper = Scraper(config)

    # Inject fault: kill browser mid-scrape
    async def inject_crash():
        await asyncio.sleep(5)
        await scraper.browser.close()

    asyncio.create_task(inject_crash())

    # Should detect crash and retry
    results = await scraper.scrape(url=TEST_URL)
    assert results is not None  # Should eventually succeed
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Run unit tests
        run: pytest -m "not integration and not e2e" --cov

      - name: Run integration tests
        run: pytest -m integration
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      # E2E tests only on main branch (expensive)
      - name: Run E2E tests
        if: github.ref == 'refs/heads/main'
        run: pytest -m e2e
        env:
          SLACK_TEST_URL: ${{ secrets.SLACK_TEST_URL }}
          SLACK_COOKIES: ${{ secrets.SLACK_COOKIES }}
```

---

## Part 11: Future Enhancements (3 minutes)

### Phase 2 Features (3-6 months)

1. **Multi-tenancy**:
   - Separate workspaces for different teams
   - Per-tenant resource quotas
   - Billing and usage tracking

2. **Streaming Results**:
   - WebSocket API for real-time progress updates
   - Stream partial results as they're extracted

3. **Smarter Scheduling**:
   - Auto-detect data update frequency
   - Intelligent refresh scheduling
   - Batch similar scrapes

4. **Advanced Recovery**:
   - Learn from human corrections
   - Fine-tune recovery prompts per platform
   - Community-contributed healers

### Phase 3 Features (6-12 months)

5. **Federated Scraping**:
   - Distribute scrapes across regions
   - Rotate IP addresses
   - Handle geo-restrictions

6. **Data Pipelines**:
   - Built-in ETL transformations
   - Webhooks on data updates
   - Integration with data warehouses

7. **ML-Powered Optimization**:
   - Predict scrape success probability
   - Optimize selector generation with fine-tuned model
   - Anomaly detection on scraped data

---

## Summary: Interviewer Takeaways

**What We Covered**:
1. ✅ **Requirements gathering** - Functional, non-functional, scale estimates
2. ✅ **High-level architecture** - 7 agents, LangGraph orchestration, hybrid storage
3. ✅ **API design** - REST + MCP interface, async job pattern
4. ✅ **Data model** - PostgreSQL for metadata, S3 for data
5. ✅ **Deep dives**:
   - Multi-agent orchestration with LangGraph
   - Self-healing recovery strategies
   - Browser pool scalability
   - Observability stack
6. ✅ **Trade-offs** - Evaluated alternatives, justified decisions
7. ✅ **Reliability** - Failure modes, retry strategies, circuit breakers
8. ✅ **Security** - Auth, secrets, rate limiting, compliance
9. ✅ **Testing** - Unit/integration/E2E pyramid, CI/CD

**Key Design Highlights**:
- **Multi-agent self-healing** as core differentiator
- **Hybrid LLM strategy** (local + cloud) for cost optimization
- **Separation of concerns** (API ↔ Workers ↔ Browsers)
- **Observability-first** with LangSmith, Prometheus, structured logs
- **Scalable from day 1** (10 scrapes → 100K scrapes with same architecture)

**Risks & Mitigations**:
- Risk: LLM non-determinism → Mitigation: Extensive tracing, caching working solutions
- Risk: Browser resource limits → Mitigation: Pooling, containerization, auto-scaling
- Risk: Website changes break scrapers → Mitigation: Multi-tier recovery strategies

**Estimated Development Timeline**:
- MVP (single platform, no self-healing): 4 weeks
- Self-healing + 3 platforms: 8 weeks
- Production-ready (monitoring, auth, scaling): 12 weeks

---

## Interview Performance Tips

### What Interviewers Look For (EM Level)

1. **Structured Thinking**:
   - ✅ Asked clarifying questions before designing
   - ✅ Defined requirements clearly
   - ✅ Broke problem into manageable pieces

2. **Technical Depth**:
   - ✅ Understood trade-offs (LangGraph vs Temporal)
   - ✅ Justified technology choices
   - ✅ Identified bottlenecks and scaling strategies

3. **Production Mindset**:
   - ✅ Considered observability from the start
   - ✅ Thought about failure modes
   - ✅ Included security and compliance

4. **Communication**:
   - ✅ Used diagrams and examples
   - ✅ Explained reasoning, not just solutions
   - ✅ Engaged interviewer ("Does this make sense?")

5. **EM-Specific**:
   - ✅ Thought about team structure (who builds what)
   - ✅ Phased rollout strategy
   - ✅ Operational concerns (on-call, debugging)

### Common Pitfalls to Avoid

- ❌ Jumping to code without requirements
- ❌ Over-engineering for current scale
- ❌ Ignoring operational concerns (monitoring, alerts)
- ❌ Not considering costs
- ❌ Forgetting about authentication/security
- ❌ No discussion of testing strategy

### Follow-up Questions to Expect

1. "How would you handle scraping websites with JavaScript-heavy SPAs?"
   → Playwright waits for network idle, JS execution

2. "What if a platform rate-limits us aggressively?"
   → Exponential backoff, distributed scraping across IPs

3. "How do you prevent duplicate data?"
   → Unique ID generation (hash of key fields), database unique constraints

4. "What's your deployment strategy?"
   → Blue-green for API servers, rolling for workers, canary for new platforms

5. "How would you debug a failing scrape in production?"
   → LangSmith trace → Logs → Screenshots → Replay in staging

---

**Good luck with your Affirm interview! 🚀**

*Remember: It's okay to say "I don't know, but here's how I'd figure it out." Shows humility and problem-solving.*
