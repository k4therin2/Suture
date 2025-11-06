"""
Basic usage example for Suture framework.

This example shows how to use Suture to scrape Slack messages.
"""

import asyncio
from pathlib import Path

from suture import Scraper, SutureConfig


async def main():
    """Run basic Suture scraping example."""

    # Load configuration from YAML file
    config_path = Path(__file__).parent / "slack_config.yaml"
    config = SutureConfig.from_yaml(config_path)

    print(f"Platform: {config.platform.name}")
    print(f"LLM: {config.llm.provider}/{config.llm.model}")
    print()

    # Create scraper instance
    scraper = Scraper(config)

    try:
        # Scrape a Slack channel or thread URL
        url = "https://app.slack.com/client/T123/C456"

        print(f"Scraping: {url}")
        print("This will:")
        print("  1. Launch browser and navigate to URL")
        print("  2. LLM agents analyze the page structure")
        print("  3. Write and execute Playwright script")
        print("  4. Extract and validate messages")
        print("  5. Save to database")
        print()

        results = await scraper.scrape(url)

        print(f"✓ Successfully extracted {len(results)} messages")
        print()

        # Display first few results
        for i, msg in enumerate(results[:3], 1):
            print(f"Message {i}:")
            print(f"  Author: {msg.get('author')}")
            print(f"  Text: {msg.get('text')[:60]}...")
            print()

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
