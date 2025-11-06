# Suture 🧵

**Self-healing multi-agent framework for web data extraction**

Suture is a LangGraph-based framework that orchestrates specialized AI agents to reliably extract structured data from difficult web sources. It automatically adapts to website changes, handles authentication flows, and provides human-in-the-loop validation when needed.

## Features

- **Self-Healing Architecture**: Agents automatically detect and adapt to website changes
- **Multi-Agent Orchestration**: Director coordinates specialized agents (Scraper, Validator, Recovery, Schema Manager)
- **Platform-Agnostic**: Extensible template system for any web platform
- **LLM Flexibility**: Use local models (Ollama), cloud models (OpenAI, Anthropic), or hybrid
- **Human-in-the-Loop**: Optional manual validation for critical data
- **Observable by Default**: LangSmith integration for debugging and monitoring

## Quick Start

```bash
# Install
pip install suture

# Configure
suture init --platform slack

# Run
suture scrape --config config.yaml
```

## Architecture

Suture uses LangGraph to coordinate 7 specialized agents:

1. **Director Agent**: Orchestrates workflow and makes high-level decisions
2. **Scraper Coding Agent**: Writes and executes Playwright scraping scripts
3. **Validator Agent**: Verifies extracted data quality and completeness
4. **Recovery Agent**: Diagnoses and fixes scraping failures
5. **Schema Manager Agent**: Designs and evolves database schema
6. **Classifier Agent**: Categorizes and enriches extracted data
7. **Human-in-Loop Agent**: Requests manual validation when confidence is low

## Platform Support

### Built-in Integrations

- **Slack** - Extract messages, threads, reactions
- _More coming soon..._

### Extending Suture

Add new platforms with:
1. YAML config defining the platform structure
2. Python healer module for platform-specific recovery logic

See [docs/EXTENDING.md](docs/EXTENDING.md) for details.

## LLM Configuration

Suture supports multiple LLM providers:

```yaml
# Local (free, private)
llm:
  provider: ollama
  model: llama3.2:3b
  reasoning_model: llama3.1:70b

# Cloud (powerful, reliable)
llm:
  provider: anthropic
  model: claude-3-5-haiku-20250101
  reasoning_model: claude-3-5-sonnet-20250128

# Hybrid (optimize cost/performance)
llm:
  validator:
    provider: ollama
    model: llama3.2:3b
  recovery:
    provider: anthropic
    model: claude-3-5-sonnet-20250128
```

## Use Cases

- **Team Communication Analysis**: Extract Slack messages for activity reports
- **Community Monitoring**: Scrape NextDoor or town hall websites
- **Market Research**: Gather data from forums and discussion boards
- **Competitive Intelligence**: Monitor competitor websites and social media
- **Research Data Collection**: Extract structured data from academic sites

## Development Status

**Current Version**: 0.1.0-alpha
**Status**: Initial development

This is an early-stage project extracted from the [Marvin](https://github.com/k4therin2/marvin) AI assistant system.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [Platform Integration Guide](docs/EXTENDING.md)
- [Architecture Deep Dive](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

We're especially interested in:
- New platform integrations
- Healer patterns for common website types
- Performance optimizations
- Documentation improvements

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Built with:
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [LangChain](https://python.langchain.com/) - LLM framework
- [Playwright](https://playwright.dev/python/) - Browser automation
- [Anthropic Claude](https://anthropic.com) - LLM reasoning
- [Ollama](https://ollama.ai) - Local LLM inference

Inspired by the [Marvin](https://github.com/k4therin2/marvin) project.

## Support

- **Issues**: [GitHub Issues](https://github.com/k4therin2/suture/issues)
- **Discussions**: [GitHub Discussions](https://github.com/k4therin2/suture/discussions)
- **Documentation**: [docs/](docs/)

---

**"Suture: Stitching together reliable data extraction from the chaotic web"** 🧵
