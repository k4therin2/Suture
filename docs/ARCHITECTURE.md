# Suture Architecture

**Version:** 0.1.0
**Last Updated:** 2025-11-06

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Internal Architecture](#internal-architecture)
4. [Multi-Agent Workflow](#multi-agent-workflow)
5. [Integration with External Systems](#integration-with-external-systems)
6. [Data Flow](#data-flow)
7. [Component Details](#component-details)

---

## Overview

Suture is a **self-healing multi-agent framework** for web data extraction. It uses LangGraph to orchestrate specialized AI agents that collaboratively scrape, validate, and store structured data from difficult web sources.

**Key Design Principles:**
- **Observable by Default**: Every agent action is logged and traceable
- **Self-Healing**: Automatic recovery from website changes and failures
- **Platform-Agnostic**: Extensible template system for any web platform
- **LLM-Flexible**: Works with local (Ollama) or cloud (OpenAI, Anthropic) models

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUTURE FRAMEWORK                                 │
│                    (Autonomous Data Extraction)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
        │   MARVIN AI     │ │  External   │ │  Standalone │
        │   Assistant     │ │  Services   │ │  CLI Usage  │
        │                 │ │             │ │             │
        │  - Activity     │ │  - Data     │ │  - Manual   │
        │    Reports      │ │    Pipelines│ │    Scraping │
        │  - Query Agent  │ │  - ETL Jobs │ │  - Testing  │
        └─────────────────┘ └─────────────┘ └─────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       SUTURE INTERNAL ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                    PUBLIC API LAYER                          │
    ├──────────────────────────────────────────────────────────────┤
    │  • Scraper.scrape(url, config)                               │
    │  • Scraper.scrape_with_validation(url, schema)               │
    │  • Scraper.batch_scrape(urls[])                              │
    └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              LANGGRAPH ORCHESTRATION LAYER                   │
    │                 (State Machine)                              │
    └─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │Director│          │Scraper │          │Recovery│
    │ Agent  │──────────│Coding  │──────────│ Agent  │
    │        │          │ Agent  │          │        │
    └────────┘          └────────┘          └────────┘
         │                    │                    │
         │                    ▼                    │
         │              ┌────────┐                 │
         │              │Script  │                 │
         │              │Executor│                 │
         │              └────────┘                 │
         │                    │                    │
         │                    ▼                    │
         │              ┌────────┐                 │
         └─────────────▶│Validator◀───────────────┘
                        │ Agent  │
                        └────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │Schema  │          │Classify│          │Human   │
    │Manager │          │ Agent  │          │in-Loop │
    │        │          │        │          │ Agent  │
    └────────┘          └────────┘          └────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   PLATFORM LAYER                             │
    ├──────────────────────────────────────────────────────────────┤
    │  Healer Modules    │  Platform Configs  │  Tools             │
    │  • slack.healer    │  • slack.yaml      │  • Playwright      │
    │  • nextdoor.healer │  • nextdoor.yaml   │  • Screenshot      │
    │  • template.healer │  • template.yaml   │  • JavaScript Exec │
    └──────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                   STORAGE LAYER                              │
    ├──────────────────────────────────────────────────────────────┤
    │  • SQLite (embedded)                                         │
    │  • ChromaDB (vector embeddings - optional)                   │
    │  • LangSmith (tracing & monitoring)                          │
    └──────────────────────────────────────────────────────────────┘
```

---

## Internal Architecture

### Agent Responsibilities

```
┌────────────────────────────────────────────────────────────────┐
│                    AGENT ARCHITECTURE                           │
└────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 1. DIRECTOR AGENT                                                │
│    - Analyzes target URL and platform                            │
│    - Plans scraping strategy                                     │
│    - Decides which agents to invoke                              │
│    - Monitors overall workflow                                   │
│    LLM: Haiku (fast, cheap decisions)                            │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. SCRAPER CODING AGENT                                          │
│    - Writes Playwright scraping scripts                          │
│    - Adapts to platform structure (via YAML config + healer)     │
│    - Generates JavaScript extraction snippets                    │
│    - Handles pagination logic                                    │
│    LLM: Sonnet (code generation quality)                         │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. SCRIPT EXECUTOR (Non-Agent)                                   │
│    - Runs Playwright scripts in browser                          │
│    - Captures screenshots for debugging                          │
│    - Handles authentication flows                                │
│    - Returns raw extracted data                                  │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. VALIDATOR AGENT                                               │
│    - Checks data completeness (expected fields present?)         │
│    - Validates data quality (reasonable values?)                 │
│    - Compares against schema                                     │
│    - Returns confidence score (0-1)                              │
│    LLM: Haiku (fast validation)                                  │
└──────────────────────────────────────────────────────────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
            Confidence < 0.8    Confidence ≥ 0.8
                   │                 │
                   ▼                 ▼
┌──────────────────────────────────────┐  ┌────────────────────────┐
│ 5. RECOVERY AGENT                    │  │ 6. SCHEMA MANAGER      │
│    - Diagnoses failure cause         │  │    - Analyzes data     │
│    - Suggests fixes to scraper       │  │    - Designs schema    │
│    - Tries alternative selectors     │  │    - Evolves schema    │
│    - Invokes platform healer         │  │    - Deduplicates      │
│    LLM: Sonnet (complex reasoning)   │  │    LLM: Haiku          │
└──────────────────────────────────────┘  └────────────────────────┘
                   │                                 │
                   └─────────┬───────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 7. CLASSIFIER AGENT (Optional)                                   │
│    - Categorizes extracted content                               │
│    - Enriches with metadata                                      │
│    - Generates vector embeddings                                 │
│    LLM: Haiku + Embeddings Model                                 │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 8. HUMAN-IN-LOOP AGENT                                           │
│    - Requests manual validation when confidence < threshold      │
│    - Shows preview of extracted data                             │
│    - Accepts corrections                                         │
│    - Learns from human feedback                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              LANGGRAPH STATE MACHINE FLOW                        │
└─────────────────────────────────────────────────────────────────┘

                        START
                          │
                          ▼
                    ┌──────────┐
                    │ Director │
                    │  Agent   │──────┐ analyze URL
                    └──────────┘      │ load platform config
                          │           │ plan strategy
                          │           │
                          ▼           ▼
                    ┌──────────┐  [State]
                    │ Scraper  │  • url
                    │  Coding  │  • platform
                    │  Agent   │  • strategy
                    └──────────┘  • script
                          │       • data
                          │       • errors
                          ▼       • attempt_count
                    ┌──────────┐
                    │  Script  │
                    │ Executor │
                    └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │Validator │
                    │  Agent   │
                    └──────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
         confidence ≥ 0.8    confidence < 0.8
                │                   │
                ▼                   ▼
         ┌──────────┐        ┌──────────┐
         │  Schema  │        │ Recovery │
         │ Manager  │        │  Agent   │
         └──────────┘        └──────────┘
                │                   │
                │                   ▼
                │            ┌──────────┐
                │            │ Platform │
                │            │  Healer  │
                │            └──────────┘
                │                   │
                │            attempts < max?
                │                   │
                │              ┌────┴────┐
                │             YES       NO
                │              │         │
                │              ▼         ▼
                │         [Retry]   [Human-in-Loop]
                │              │         │
                └──────────────┴─────────┘
                          │
                          ▼
                    ┌──────────┐
                    │Classifier│  (optional)
                    │  Agent   │
                    └──────────┘
                          │
                          ▼
                    ┌──────────┐
                    │  Save to │
                    │ Database │
                    └──────────┘
                          │
                          ▼
                        END
```

---

## Integration with External Systems

### Pattern 1: Marvin Integration (Multi-Agent System)

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARVIN AI ASSISTANT                           │
│              (Multi-Agent Activity Tracking)                     │
└─────────────────────────────────────────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐  ┌──────────┐
    │ Director │   │  Query   │  │ Report   │
    │  Agent   │   │  Agent   │  │  Agent   │
    └──────────┘   └──────────┘  └──────────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ "Need Slack messages from │
            │  #engineering for report" │
            └───────────────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   ADAPTER LAYER           │
            │   (in Marvin)             │
            │                           │
            │   from suture import      │
            │       Scraper, Config     │
            │                           │
            │   async def get_messages()│
            └───────────────────────────┘
                          │
                          ▼
                    ═══════════════
                    ║   SUTURE   ║  <── External dependency
                    ║  FRAMEWORK ║
                    ═══════════════
                          │
                          ▼
            ┌───────────────────────────┐
            │  Extracted Messages       │
            │  (JSON/Dict)              │
            └───────────────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │  MARVIN DATABASE          │
            │  • Stores messages        │
            │  • Indexes for search     │
            │  • ChromaDB embeddings    │
            └───────────────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │  Marvin processes data    │
            │  • Generate reports       │
            │  • Answer queries         │
            │  • Analyze trends         │
            └───────────────────────────┘
```

**Integration Code Example:**

```python
# In Marvin's backend/scrapers/slack_adapter.py

from suture import Scraper, SutureConfig
from pathlib import Path

class MarvinSlackAdapter:
    """Adapter to use Suture for Slack scraping in Marvin."""

    def __init__(self):
        config_path = Path(__file__).parent / "suture_slack_config.yaml"
        self.config = SutureConfig.from_yaml(config_path)
        self.scraper = Scraper(self.config)

    async def scrape_channel(self, channel: str, after_timestamp: int):
        """Scrape Slack channel using Suture.

        Args:
            channel: Channel name (without #)
            after_timestamp: Unix timestamp

        Returns:
            List of message dicts compatible with Marvin's schema
        """
        # Build Slack search query
        url = f"https://app.slack.com/client/..."
        search_query = f"in:#{channel} after:{after_timestamp}"

        # Use Suture to scrape
        results = await self.scraper.scrape(
            url,
            search_query=search_query,
            limit=100
        )

        # Transform to Marvin's expected format
        messages = self._transform_to_marvin_format(results)

        return messages

    def _transform_to_marvin_format(self, suture_results):
        """Convert Suture output to Marvin's expected schema."""
        # Suture and Marvin use same schema, so just pass through
        return suture_results['messages']
```

### Pattern 2: Standalone API Service

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL APPLICATIONS                         │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   SUTURE API SERVER       │
            │   (FastAPI/Flask)         │
            ├───────────────────────────┤
            │ POST /scrape              │
            │ GET  /status/{job_id}     │
            │ GET  /platforms           │
            └───────────────────────────┘
                          │
                          ▼
                    ═══════════════
                    ║   SUTURE   ║
                    ║  FRAMEWORK ║
                    ═══════════════
                          │
                          ▼
            ┌───────────────────────────┐
            │  Results Queue            │
            │  • Redis/RabbitMQ         │
            │  • Async task processing  │
            └───────────────────────────┘
```

### Pattern 3: Library/SDK Usage

```python
# Direct usage as Python library

from suture import Scraper, SutureConfig

# Load configuration
config = SutureConfig.from_yaml("slack_config.yaml")

# Create scraper
scraper = Scraper(config)

# Scrape data
results = await scraper.scrape(
    url="https://app.slack.com/client/T123/C456",
    search_query="in:#engineering after:1730800000"
)

# Use results
for message in results:
    print(f"{message['author']}: {message['text']}")
```

---

## Data Flow

### Request → Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. REQUEST                                                       │
└─────────────────────────────────────────────────────────────────┘

{
  "url": "https://app.slack.com/client/T123/C456",
  "platform": "slack",
  "search_query": "in:#engineering after:1730800000",
  "limit": 100
}
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. DIRECTOR AGENT PLANNING                                       │
└─────────────────────────────────────────────────────────────────┘

LangGraph State = {
  "url": "...",
  "platform": "slack",
  "platform_config": <loaded from slack.yaml>,
  "healer": <loaded from slack.healer>,
  "strategy": "search_based",
  "script": null,
  "data": [],
  "errors": [],
  "confidence": null,
  "attempt_count": 0
}
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. SCRAPER CODING AGENT                                          │
└─────────────────────────────────────────────────────────────────┘

State.script = """
async function scrapeSlack(page) {
  await page.goto('https://app.slack.com/...');
  // ... Playwright code generated by LLM
  return messages;
}
"""
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. SCRIPT EXECUTOR                                               │
└─────────────────────────────────────────────────────────────────┘

State.data = [
  {
    "channel": "#engineering",
    "author": "Alice",
    "timestamp_iso": "2025-11-05T09:00:00",
    "timestamp_epoch": 1730800800,
    "text": "Found a critical bug...",
    "url": "https://slack.com/archives/..."
  },
  ...
]
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. VALIDATOR AGENT                                               │
└─────────────────────────────────────────────────────────────────┘

State.confidence = 0.95  # High confidence
State.validation_notes = "All expected fields present, timestamps valid"
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. SCHEMA MANAGER                                                │
└─────────────────────────────────────────────────────────────────┘

State.data = [<deduplicated and normalized>]
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. SAVE TO DATABASE                                              │
└─────────────────────────────────────────────────────────────────┘

SQLite INSERT INTO messages (id, channel, author, timestamp_iso, ...)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. RESPONSE                                                      │
└─────────────────────────────────────────────────────────────────┘

{
  "status": "success",
  "messages_extracted": 47,
  "confidence": 0.95,
  "execution_time_ms": 2341,
  "trace_url": "https://smith.langchain.com/..."
}
```

---

## Component Details

### 1. Configuration System

```yaml
# Platform configuration (slack.yaml)
version: "1.0"

platform:
  name: slack
  auth_type: cookies
  base_url: "https://app.slack.com"
  healer_module: "suture.platforms.slack.healer"

  schema:
    message:
      channel: string
      author: string
      timestamp_iso: string
      timestamp_epoch: integer
      text: string
      url: string

  selectors:
    message_container: ".c-virtual_list__item"
    message_text: ".p-rich_text_section"
    author: "[data-qa='message_sender_name']"
    timestamp: "a.c-timestamp[data-ts]"

llm:
  provider: ollama
  model: llama3.2:3b
  base_url: "http://localhost:11434"

database:
  type: sqlite
  path: "slack_messages.db"

max_recovery_attempts: 3
enable_human_loop: false
confidence_threshold: 0.8
```

### 2. Platform Healer Module

```python
# suture/platforms/slack/healer.py

from suture.healer.base import BaseHealer

class SlackHealer(BaseHealer):
    """Slack-specific recovery logic."""

    async def diagnose_failure(self, error, state):
        """Diagnose why scraping failed."""
        if "selector not found" in str(error):
            return {
                "cause": "ui_change",
                "suggestion": "Try alternative selectors from Slack DOM"
            }
        elif "authentication" in str(error):
            return {
                "cause": "auth_expired",
                "suggestion": "Re-authenticate with Slack"
            }
        return {"cause": "unknown", "suggestion": "retry"}

    async def heal(self, diagnosis, state):
        """Attempt to fix the issue."""
        if diagnosis["cause"] == "ui_change":
            # Use Anthropic Computer Use to visually identify elements
            alternative_script = await self._generate_visual_scraper(state)
            return {"script": alternative_script}

        return None
```

### 3. LangGraph State Definition

```python
# suture/graph/state.py

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class ScraperState(TypedDict):
    """LangGraph state for scraping workflow."""

    # Input
    url: str
    platform: str
    search_query: Optional[str]
    limit: int

    # Configuration
    platform_config: Dict[str, Any]
    healer: Any

    # Workflow
    strategy: str  # "search_based", "channel_nav", etc.
    script: Optional[str]
    screenshot_path: Optional[str]

    # Results
    data: List[Dict[str, Any]]
    confidence: Optional[float]
    validation_notes: str

    # Error handling
    errors: List[str]
    attempt_count: int
    max_attempts: int

    # Metadata
    execution_id: str
    started_at: str
    completed_at: Optional[str]
```

---

## Summary

**Suture provides:**

1. **Autonomous scraping** via multi-agent collaboration
2. **Self-healing** through specialized recovery agents
3. **Observable workflows** with LangGraph + LangSmith
4. **Flexible integration** as library, API, or CLI
5. **Platform extensibility** via YAML + Python healers

**Integration with Marvin:**

- Marvin imports Suture as a Python library
- Marvin's agents delegate scraping tasks to Suture
- Suture returns structured data to Marvin's database
- Both systems remain independent and composable

**Next Steps:**

1. Implement core LangGraph workflow
2. Port Slack scraper as first platform integration
3. Add integration tests with real Slack data
4. Create adapter layer for Marvin
