# Suture Architecture - Visual Diagrams

**Detailed visual representations of Suture's architecture and integrations**

---

## Diagram 1: High-Level System Context

```
                    ╔════════════════════════════╗
                    ║   EXTERNAL CONSUMERS       ║
                    ╚════════════════════════════╝
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  ┌──────────┐         ┌──────────┐         ┌──────────┐
  │  MARVIN  │         │   ETL    │         │STANDALONE│
  │    AI    │         │ PIPELINE │         │   CLI    │
  │ SYSTEM   │         │ SERVICES │         │  USAGE   │
  └──────────┘         └──────────┘         └──────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                  ╔═══════════════════════╗
                  ║   SUTURE FRAMEWORK    ║
                  ║  (Data Extraction)    ║
                  ╚═══════════════════════╝
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  ┌──────────┐         ┌──────────┐         ┌──────────┐
  │  SLACK   │         │ NEXTDOOR │         │  CUSTOM  │
  │ PLATFORM │         │ PLATFORM │         │ PLATFORMS│
  └──────────┘         └──────────┘         └──────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ╔════════════════════╗
                    ║   TARGET WEBSITES  ║
                    ╚════════════════════╝
```

---

## Diagram 2: Marvin ↔ Suture Integration (Detailed)

```
┌───────────────────────────────────────────────────────────────────┐
│                         MARVIN SYSTEM                              │
│                    (Multi-Agent AI Assistant)                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │  Director    │    │   Report     │    │    Query     │        │
│  │   Agent      │    │   Agent      │    │    Agent     │        │
│  │              │    │              │    │              │        │
│  │ Coordinates  │    │ Generates    │    │ Answers      │        │
│  │ workflow     │    │ activity     │    │ natural      │        │
│  │              │    │ reports      │    │ language     │        │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘        │
│         │                   │                   │                 │
│         └───────────────────┼───────────────────┘                 │
│                             │                                     │
│                             ▼                                     │
│                  ┌─────────────────────┐                          │
│                  │ "Need fresh Slack   │                          │
│                  │  data from last     │                          │
│                  │  24 hours"          │                          │
│                  └─────────────────────┘                          │
│                             │                                     │
│                             ▼                                     │
│              ╔════════════════════════════╗                       │
│              ║  SLACK SCRAPER ADAPTER     ║                       │
│              ║  (Marvin component)        ║                       │
│              ╠════════════════════════════╣                       │
│              ║ • Translates Marvin needs  ║                       │
│              ║ • Calls Suture API         ║                       │
│              ║ • Transforms results       ║                       │
│              ╚════════════════════════════╝                       │
│                             │                                     │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                              │ import suture
                              │ scraper = Scraper(config)
                              │ results = await scraper.scrape(...)
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                      SUTURE FRAMEWORK                              │
│                  (Independent Python Package)                      │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              LANGGRAPH ORCHESTRATOR                         │   │
│  │                                                             │   │
│  │   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐       │   │
│  │   │Director│ → │Scraper │ → │Executor│ → │Validate│       │   │
│  │   │        │   │ Coding │   │        │   │        │       │   │
│  │   └────────┘   └────────┘   └────────┘   └────────┘       │   │
│  │                                    │                        │   │
│  │                           ┌────────┴────────┐              │   │
│  │                           │                 │              │   │
│  │                      Success          Failure              │   │
│  │                           │                 │              │   │
│  │                           ▼                 ▼              │   │
│  │                    ┌────────┐        ┌────────┐           │   │
│  │                    │ Schema │        │Recovery│           │   │
│  │                    │Manager │        │ Agent  │           │   │
│  │                    └────────┘        └────────┘           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              PLATFORM INTEGRATIONS                          │   │
│  │                                                             │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │   │ slack.yaml   │  │slack.healer  │  │  Playwright  │    │   │
│  │   │ (config)     │  │ (recovery)   │  │  (browser)   │    │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    STORAGE                                  │   │
│  │   SQLite | ChromaDB | LangSmith Tracing                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                             │                                      │
└─────────────────────────────┼──────────────────────────────────────┘
                              │
                              │ Returns:
                              │ [{channel, author, text, ...}, ...]
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                      BACK TO MARVIN                                │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  MARVIN DATABASE                                             │  │
│  │                                                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │  │
│  │  │ Messages │  │ ChromaDB │  │  Indices │                  │  │
│  │  │  SQLite  │  │Embeddings│  │  Search  │                  │  │
│  │  └──────────┘  └──────────┘  └──────────┘                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                             │                                      │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  MARVIN AGENTS USE DATA                                      │  │
│  │                                                              │  │
│  │  • Report Agent → "Alice fixed payment bug"                 │  │
│  │  • Query Agent  → "What did engineering discuss today?"     │  │
│  │  • Analysis     → "Team velocity increased 15%"             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Diagram 3: Suture Internal Agent Communication

```
┌─────────────────────────────────────────────────────────────────┐
│              SUTURE AGENT COMMUNICATION FLOW                     │
│                  (LangGraph State Machine)                       │
└─────────────────────────────────────────────────────────────────┘

    USER REQUEST
         │
         ▼
    ┌────────┐
    │ Input  │
    │ State  │  ← url: "https://slack.com/..."
    │        │  ← platform: "slack"
    │        │  ← search_query: "in:#eng after:123"
    └───┬────┘
        │
        ▼
╔═══════════════════════════════════════════════════════════════╗
║  DIRECTOR AGENT                                                ║
║  LLM: Claude Haiku (fast, cheap)                              ║
╠═══════════════════════════════════════════════════════════════╣
║  Input:  State.url, State.platform                            ║
║  Thinks: "This is Slack. Load slack.yaml config.             ║
║          Use search-based strategy.                           ║
║          Need to check authentication first."                 ║
║  Output: State.strategy = "search_based"                      ║
║          State.platform_config = <slack.yaml>                 ║
║          State.next_agent = "scraper_coding"                  ║
╚═══════════════════════════════════════════════════════════════╝
        │
        ▼
╔═══════════════════════════════════════════════════════════════╗
║  SCRAPER CODING AGENT                                          ║
║  LLM: Claude Sonnet (code generation quality)                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Input:  State.platform_config.selectors                      ║
║          State.search_query                                   ║
║  Thinks: "I'll write Playwright script to:                    ║
║          1. Navigate to Slack                                 ║
║          2. Use Cmd+K to open search                          ║
║          3. Type search query                                 ║
║          4. Extract messages with JS injection"               ║
║  Output: State.script = <Playwright code>                     ║
║          State.next = "script_executor"                       ║
╚═══════════════════════════════════════════════════════════════╝
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  SCRIPT EXECUTOR (Non-Agent)                                  │
│  Tech: Playwright + JavaScript                                │
├───────────────────────────────────────────────────────────────┤
│  Input:  State.script                                         │
│  Does:   • Launch browser                                     │
│          • Execute scraping script                            │
│          • Capture screenshots                                │
│          • Handle errors                                      │
│  Output: State.data = [{msg1}, {msg2}, ...]                   │
│          OR State.errors = ["selector not found"]             │
└───────────────────────────────────────────────────────────────┘
        │
        ├──── Success? ────┐
        │                  │
       YES                NO
        │                  │
        ▼                  ▼
╔═══════════════════╗  ╔════════════════════════════════════════╗
║  VALIDATOR AGENT  ║  ║  RECOVERY AGENT                        ║
║  LLM: Haiku       ║  ║  LLM: Sonnet (complex reasoning)       ║
╠═══════════════════╣  ╠════════════════════════════════════════╣
║ Input: State.data ║  ║ Input: State.errors                    ║
║ Checks:           ║  ║ Analyzes:                              ║
║ • All fields?     ║  ║ • "selector not found" means UI change ║
║ • Valid types?    ║  ║ • Load slack.healer for alternatives   ║
║ • Reasonable?     ║  ║ Suggests:                              ║
║ Output:           ║  ║ • Try different selectors              ║
║ confidence = 0.95 ║  ║ • Use Computer Use for visual detect   ║
║ next = "schema"   ║  ║ Output: State.script = <new script>    ║
╚═══════════════════╝  ║         State.attempt_count++          ║
        │              ║         next = "script_executor" (retry)║
        │              ╚════════════════════════════════════════╝
        │                              │
        │              ┌───────────────┤
        │              │ attempts < 3? │
        │              ├───────────────┘
        │              │       │
        │             YES     NO
        │              │       │
        │              │       ▼
        │              │  ╔═══════════════════════╗
        │              │  ║ HUMAN-IN-LOOP AGENT   ║
        │              │  ║ Requests manual help  ║
        │              │  ╚═══════════════════════╝
        │              │       │
        │              └───────┘
        │                  │
        ▼                  ▼
╔═══════════════════════════════════════════════════════════════╗
║  SCHEMA MANAGER AGENT                                          ║
║  LLM: Haiku (fast analysis)                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Input:  State.data (validated or human-approved)             ║
║  Does:   • Normalize field names                              ║
║          • Deduplicate messages                               ║
║          • Generate unique IDs                                ║
║          • Match expected schema                              ║
║  Output: State.data = <normalized messages>                   ║
║          State.next = "classifier" (optional)                 ║
╚═══════════════════════════════════════════════════════════════╝
        │
        ▼ (optional)
╔═══════════════════════════════════════════════════════════════╗
║  CLASSIFIER AGENT                                              ║
║  LLM: Haiku + Embeddings                                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Input:  State.data                                           ║
║  Does:   • Categorize messages (bug, feature, question)       ║
║          • Generate embeddings for semantic search            ║
║          • Add metadata tags                                  ║
║  Output: State.data = <enriched messages>                     ║
╚═══════════════════════════════════════════════════════════════╝
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│  SAVE TO DATABASE                                             │
│  SQLite + ChromaDB                                            │
├───────────────────────────────────────────────────────────────┤
│  INSERT INTO messages (id, channel, author, text, ...)        │
│  INSERT INTO embeddings (message_id, vector)                  │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
    ┌────────┐
    │ Return │  → {status: "success", count: 47}
    │ Result │
    └────────┘
```

---

## Diagram 4: Data Flow with Real Example

```
INPUT REQUEST:
{
  "url": "https://app.slack.com/client/T123/C456",
  "search_query": "in:#engineering after:1730800000",
  "limit": 100
}

                  ↓

╔═══════════════════════════════════════════════════════════════╗
║ DIRECTOR AGENT DECISION                                        ║
╠═══════════════════════════════════════════════════════════════╣
║ Loads: slack.yaml config                                      ║
║ {                                                             ║
║   "platform": "slack",                                        ║
║   "auth_type": "cookies",                                     ║
║   "selectors": {                                              ║
║     "message_container": ".c-virtual_list__item",            ║
║     "message_text": ".p-rich_text_section"                   ║
║   }                                                           ║
║ }                                                             ║
║ Strategy: "search_based"                                      ║
╚═══════════════════════════════════════════════════════════════╝

                  ↓

╔═══════════════════════════════════════════════════════════════╗
║ SCRAPER CODING AGENT GENERATES CODE                           ║
╠═══════════════════════════════════════════════════════════════╣
║ async function scrapeSlack(page, config) {                   ║
║   await page.goto('https://app.slack.com/...');              ║
║   await page.keyboard.press('Meta+k'); // Open search        ║
║   await page.fill('input[type="search"]', query);            ║
║   await page.keyboard.press('Enter');                        ║
║   await page.waitForTimeout(2000);                           ║
║                                                               ║
║   // Fast JS extraction                                      ║
║   const messages = await page.evaluate(() => {               ║
║     return Array.from(                                       ║
║       document.querySelectorAll('.c-virtual_list__item')     ║
║     ).map(el => ({                                           ║
║       text: el.querySelector('.p-rich_text_section')         ║
║                .innerText,                                   ║
║       author: el.querySelector('[data-qa="..."]')            ║
║                  .innerText,                                 ║
║       // ...                                                 ║
║     }));                                                     ║
║   });                                                        ║
║   return messages;                                           ║
║ }                                                            ║
╚═══════════════════════════════════════════════════════════════╝

                  ↓

┌───────────────────────────────────────────────────────────────┐
│ SCRIPT EXECUTOR RUNS CODE                                     │
├───────────────────────────────────────────────────────────────┤
│ • Launches Chrome with Marvin profile                         │
│ • Executes Playwright script                                  │
│ • Returns raw data in ~2 seconds                              │
└───────────────────────────────────────────────────────────────┘

                  ↓

RAW DATA:
[
  {
    "text": "Found a critical bug in payment processing",
    "author": "Alice",
    "timestamp_epoch": 1730800800,
    "channel": "#engineering"
  },
  {
    "text": "I can help with that Alice",
    "author": "Bob",
    "timestamp_epoch": 1730801700,
    "channel": "#engineering"
  },
  // ... 45 more messages
]

                  ↓

╔═══════════════════════════════════════════════════════════════╗
║ VALIDATOR AGENT CHECKS                                         ║
╠═══════════════════════════════════════════════════════════════╣
║ ✓ All 47 messages have: text, author, timestamp, channel     ║
║ ✓ Timestamps are valid Unix epochs                           ║
║ ✓ Channel names match expected format                        ║
║ ✓ No obvious scraping artifacts                              ║
║                                                               ║
║ Confidence: 0.95 (High)                                       ║
║ Validation: PASS → Continue to Schema Manager                ║
╚═══════════════════════════════════════════════════════════════╝

                  ↓

╔═══════════════════════════════════════════════════════════════╗
║ SCHEMA MANAGER NORMALIZES                                      ║
╠═══════════════════════════════════════════════════════════════╣
║ • Generates unique IDs: hash(channel+author+timestamp)       ║
║ • Converts epochs to ISO: "2025-11-05T09:00:00Z"             ║
║ • Deduplicates (0 dupes found)                               ║
║ • Adds URL field: "https://slack.com/archives/C123/p..."     ║
╚═══════════════════════════════════════════════════════════════╝

                  ↓

NORMALIZED DATA:
[
  {
    "id": "slack_engineering_alice_1730800800",
    "channel": "#engineering",
    "author": "Alice",
    "timestamp_iso": "2025-11-05T09:00:00Z",
    "timestamp_epoch": 1730800800,
    "text": "Found a critical bug in payment processing",
    "url": "https://slack.com/archives/C123/p1730800800"
  },
  // ... 46 more
]

                  ↓

┌───────────────────────────────────────────────────────────────┐
│ SAVE TO DATABASE                                              │
├───────────────────────────────────────────────────────────────┤
│ SQLite: INSERT 47 messages                                    │
│ ChromaDB: INSERT 47 embeddings (optional)                     │
└───────────────────────────────────────────────────────────────┘

                  ↓

RESPONSE:
{
  "status": "success",
  "messages_extracted": 47,
  "messages_new": 47,
  "messages_duplicate": 0,
  "confidence": 0.95,
  "execution_time_ms": 2341,
  "attempts": 1,
  "trace_url": "https://smith.langchain.com/public/abc123"
}
```

---

## Diagram 5: Error Recovery Flow

```
SCENARIO: Slack UI changed, selectors no longer work

┌───────────────────────────────────────────────────────────────┐
│ SCRAPER CODING AGENT                                          │
│ Generates script with selector: ".c-virtual_list__item"      │
└───────────────────────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────┐
│ SCRIPT EXECUTOR                                               │
│ ❌ Error: "Selector not found: .c-virtual_list__item"        │
└───────────────────────────────────────────────────────────────┘
                  ↓
╔═══════════════════════════════════════════════════════════════╗
║ RECOVERY AGENT (Attempt 1/3)                                  ║
╠═══════════════════════════════════════════════════════════════╣
║ Diagnosis: "UI Change - selector renamed"                    ║
║ Consults: slack.healer module                                ║
║                                                               ║
║ slack.healer suggests:                                       ║
║ Alternative selectors to try:                                ║
║ - "[data-qa='virtual-list-item']"                           ║
║ - ".c-message-container"                                     ║
║ - "[role='listitem']"                                        ║
╚═══════════════════════════════════════════════════════════════╝
                  ↓
╔═══════════════════════════════════════════════════════════════╗
║ SCRAPER CODING AGENT (Retry)                                  ║
║ Generates new script with alternative selector               ║
╚═══════════════════════════════════════════════════════════════╝
                  ↓
┌───────────────────────────────────────────────────────────────┐
│ SCRIPT EXECUTOR (Retry)                                       │
│ ❌ Still failing with all alternatives                        │
└───────────────────────────────────────────────────────────────┘
                  ↓
╔═══════════════════════════════════════════════════════════════╗
║ RECOVERY AGENT (Attempt 2/3)                                  ║
╠═══════════════════════════════════════════════════════════════╣
║ Escalates: "Need visual inspection"                          ║
║ Uses: Anthropic Computer Use API                             ║
║                                                               ║
║ Claude with Computer Use:                                    ║
║ 1. Takes screenshot of Slack page                            ║
║ 2. Visually identifies message elements                      ║
║ 3. Suggests: "Messages now use '.p-message_wrapper'"         ║
╚═══════════════════════════════════════════════════════════════╝
                  ↓
╔═══════════════════════════════════════════════════════════════╗
║ SCRAPER CODING AGENT (Retry 2)                                ║
║ Generates script with visually-identified selector           ║
╚═══════════════════════════════════════════════════════════════╝
                  ↓
┌───────────────────────────────────────────────────────────────┐
│ SCRIPT EXECUTOR (Retry 2)                                     │
│ ✓ Success! Extracted 47 messages                             │
└───────────────────────────────────────────────────────────────┘
                  ↓
╔═══════════════════════════════════════════════════════════════╗
║ SCHEMA MANAGER UPDATES CONFIG                                 ║
╠═══════════════════════════════════════════════════════════════╣
║ Suggests: Update slack.yaml with new selector:               ║
║ "message_container": ".p-message_wrapper"                    ║
║                                                               ║
║ (Human can approve this config update)                       ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Diagram 6: LLM Model Assignment by Agent

```
┌────────────────────────────────────────────────────────────┐
│                  LLM MODEL STRATEGY                         │
│             (Optimize Cost vs Performance)                  │
└────────────────────────────────────────────────────────────┘

    CHEAP & FAST              EXPENSIVE & SMART
    (Ollama Local)            (Cloud APIs)
         │                           │
    ┌────┴────┐                 ┌───┴────┐
    │         │                 │        │
    ▼         ▼                 ▼        ▼

┌─────────┐ ┌─────────┐  ┌─────────┐ ┌─────────┐
│Director │ │Validator│  │ Scraper │ │Recovery │
│ Agent   │ │ Agent   │  │ Coding  │ │ Agent   │
├─────────┤ ├─────────┤  ├─────────┤ ├─────────┤
│ Haiku   │ │ Haiku   │  │ Sonnet  │ │ Sonnet  │
│ (fast)  │ │ (fast)  │  │(quality)│ │(complex)│
└─────────┘ └─────────┘  └─────────┘ └─────────┘

Simple         Quick        Code         Complex
decisions   validation   generation    reasoning


CONFIGURATION OPTIONS:

Option 1: All Local (Ollama)
├─ Director:  llama3.2:3b  (fast decisions)
├─ Validator: llama3.2:3b  (simple checks)
├─ Scraper:   llama3.1:70b (code quality)
└─ Recovery:  llama3.1:70b (debugging)
   Cost: $0  |  Speed: Fast  |  Quality: Good

Option 2: Hybrid (Recommended)
├─ Director:  llama3.2:3b      (Ollama - fast)
├─ Validator: llama3.2:3b      (Ollama - fast)
├─ Scraper:   claude-sonnet    (Anthropic - best)
└─ Recovery:  claude-sonnet    (Anthropic - best)
   Cost: ~$0.50/run  |  Speed: Fast  |  Quality: Excellent

Option 3: All Cloud
├─ Director:  claude-haiku     (cheap, fast)
├─ Validator: claude-haiku     (cheap, fast)
├─ Scraper:   claude-sonnet    (powerful)
└─ Recovery:  claude-sonnet    (powerful)
   Cost: ~$0.80/run  |  Speed: Fast  |  Quality: Excellent
```

---

## Summary

These diagrams show:

1. **System Context**: How Suture fits in the broader ecosystem
2. **Marvin Integration**: Detailed view of how Marvin uses Suture as a library
3. **Agent Communication**: LangGraph state machine flow between agents
4. **Real Example**: Concrete data transformation through the pipeline
5. **Error Recovery**: Self-healing workflow when things go wrong
6. **LLM Strategy**: Cost/performance optimization through model selection

**Key Takeaways:**

- **Suture is autonomous**: Marvin just calls `scraper.scrape()` and gets results
- **Multi-agent collaboration**: 7 specialized agents work together via LangGraph
- **Self-healing**: Automatic recovery from website changes using healer modules
- **Observable**: Every step is traced via LangSmith
- **Flexible**: Can be used as library, API service, or CLI tool
