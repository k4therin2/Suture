"""
Command-line interface for Suture framework.
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from suture import Scraper, SutureConfig, __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Suture: Self-healing multi-agent framework for web data extraction."""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    required=True,
    help="Path to configuration YAML file",
)
@click.option("--url", "-u", required=True, help="URL to scrape")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (JSON)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def scrape(config: str, url: str, output: str | None, verbose: bool):
    """Scrape data from a URL using configured platform."""
    try:
        # Load configuration
        suture_config = SutureConfig.from_yaml(Path(config))

        if verbose:
            console.print(f"[bold]Platform:[/bold] {suture_config.platform.name}")
            console.print(f"[bold]LLM:[/bold] {suture_config.llm.provider}/{suture_config.llm.model}")
            console.print(f"[bold]Target URL:[/bold] {url}\n")

        # Run scraping
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scraping...", total=None)

            results = asyncio.run(_run_scrape(suture_config, url, output))

            progress.update(task, completed=True)

        console.print(f"\n[green]✓[/green] Successfully extracted {len(results)} items")

        if output:
            console.print(f"[green]✓[/green] Results saved to {output}")

    except Exception as e:
        console.print(f"[red]✗[/red] Scraping failed: {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


async def _run_scrape(config: SutureConfig, url: str, output_path: str | None):
    """Internal async function to run scraping."""
    scraper = Scraper(config)
    try:
        output = Path(output_path) if output_path else None
        return await scraper.scrape(url, output_path=output)
    finally:
        await scraper.close()


@cli.command()
@click.option(
    "--platform",
    "-p",
    required=True,
    help="Platform name (e.g., slack, nextdoor)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="config.yaml",
    help="Output config file path",
)
def init(platform: str, output: str):
    """Initialize a new configuration file for a platform."""
    try:
        output_path = Path(output)

        if output_path.exists():
            if not click.confirm(f"{output} already exists. Overwrite?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # TODO: Load platform template and create config
        console.print(f"[green]✓[/green] Created configuration file: {output}")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Edit the configuration file with your settings")
        console.print("2. Set up authentication (cookies, credentials, etc.)")
        console.print(f"3. Run: suture scrape -c {output} -u <URL>")

    except Exception as e:
        console.print(f"[red]✗[/red] Failed to create config: {e}")
        sys.exit(1)


@cli.command()
def list_platforms():
    """List available platform integrations."""
    console.print("[bold]Available Platforms:[/bold]\n")

    platforms = [
        ("slack", "Extract messages, threads, and reactions from Slack"),
        # Add more as they're implemented
    ]

    for name, description in platforms:
        console.print(f"  [cyan]{name}[/cyan]")
        console.print(f"    {description}\n")


if __name__ == "__main__":
    cli()
