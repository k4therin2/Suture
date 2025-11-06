"""
Configuration management for Suture framework.

Handles loading and validation of YAML config files for scraping platforms.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
import yaml


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(..., description="LLM provider (ollama, openai, anthropic)")
    model: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key for cloud providers")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: int = Field(4096, description="Max tokens for generation")


class DatabaseConfig(BaseModel):
    """Database configuration."""

    type: str = Field("sqlite", description="Database type")
    path: str = Field("suture.db", description="Database file path")


class PlatformConfig(BaseModel):
    """Platform-specific configuration."""

    name: str = Field(..., description="Platform name (e.g., slack)")
    auth_type: str = Field(..., description="Authentication type (cookies, credentials, token)")
    base_url: str = Field(..., description="Base URL for the platform")
    healer_module: Optional[str] = Field(None, description="Python module for healer logic")
    schema: Dict[str, Any] = Field(default_factory=dict, description="Data schema definition")
    selectors: Dict[str, str] = Field(default_factory=dict, description="CSS selectors")


class SutureConfig(BaseModel):
    """Main Suture configuration."""

    version: str = Field("1.0", description="Config version")
    platform: PlatformConfig
    llm: LLMConfig
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # Agent settings
    max_recovery_attempts: int = Field(3, description="Max recovery attempts per failure")
    enable_human_loop: bool = Field(False, description="Enable human-in-the-loop validation")
    confidence_threshold: float = Field(0.8, description="Confidence threshold for auto-approval")

    # Browser settings
    browser_headless: bool = Field(True, description="Run browser in headless mode")
    browser_timeout: int = Field(30000, description="Browser timeout in milliseconds")

    @classmethod
    def from_yaml(cls, path: Path) -> "SutureConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            SutureConfig instance
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            path: Path to save YAML configuration
        """
        with open(path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


def load_config(config_path: str = "config.yaml") -> SutureConfig:
    """Load Suture configuration from file.

    Args:
        config_path: Path to configuration file

    Returns:
        SutureConfig instance
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    return SutureConfig.from_yaml(path)
