"""Environment configuration management for Supabase connections."""

import os
import requests
import textwrap
from dataclasses import dataclass
from typing import Optional
import dotenv


@dataclass
class EnvironmentConfig:
    """Configuration object that encapsulates all environment-related settings.

    Examples:
        Create configuration from environment variables:
        >>> config = EnvironmentConfig.from_environment()
        >>> print(config.environment)  # 'local' or 'production'

        Create configuration manually:
        >>> config = EnvironmentConfig(
        ...     environment="local",
        ...     url="http://127.0.0.1:54321",
        ...     anon_key="your-anon-key",
        ...     is_local=True
        ... )

        Validate configuration:
        >>> is_valid, message = config.validate()
        >>> if not is_valid:
        ...     print(f"Config error: {message}")

        Check if local Supabase is running:
        >>> if config.is_local:
        ...     print(config.get_console_message())
    """

    environment: str
    url: str
    anon_key: str
    is_local: bool

    @classmethod
    def from_environment(cls) -> "EnvironmentConfig":
        """Create configuration from environment variables."""
        # Load environment variables at runtime for dynamic configuration
        dotenv.load_dotenv()

        environment = (os.getenv("ENVIRONMENT") or "production").lower()
        url = os.getenv("SUPABASE_URL") or ""
        anon_key = os.getenv("SUPABASE_ANON_KEY") or ""
        is_local = environment == "local"

        return cls(
            environment=environment, url=url, anon_key=anon_key, is_local=is_local
        )

    def validate(self) -> tuple[bool, str]:
        """Validate that required configuration is available and services are running."""
        if not self.url or not self.anon_key:
            if self.is_local:
                return (
                    False,
                    textwrap.dedent(
                        """
                    Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.
                    For local development:
                    1. Run 'supabase start' to start local Supabase
                    2. Copy .env.local to .env to use local configuration
                """
                    ).strip(),
                )
            else:
                return (
                    False,
                    textwrap.dedent(
                        """
                    Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.
                    Please set these in your .env file for production use.
                """
                    ).strip(),
                )

        # For local environment, check if Supabase is actually running
        if self.is_local:
            if not self._is_local_supabase_running():
                return (
                    False,
                    textwrap.dedent(
                        f"""
                    Local Supabase appears to be offline.
                    Please run 'supabase start' to start the local Supabase services.
                    Expected Supabase API at: {self.url}
                """
                    ).strip(),
                )

        env_type = "local development" if self.is_local else "production"
        return True, f"Environment validated for {env_type}"

    def _is_local_supabase_running(self) -> bool:
        """Check if local Supabase is running by making a health check request."""
        if not self.is_local:
            return True  # Skip check for non-local environments

        try:
            # Try to reach the Supabase health endpoint (configurable)
            health_endpoint = os.getenv("SUPABASE_HEALTH_ENDPOINT", "/health")
            health_timeout = int(os.getenv("SUPABASE_HEALTH_TIMEOUT", "5"))
            health_url = f"{self.url}{health_endpoint}"
            response = requests.get(health_url, timeout=health_timeout)
            return response.status_code == 200
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            return False

    def get_display_name(self) -> str:
        """Get a human-readable display name for the environment."""
        return "local development" if self.is_local else "production"

    def get_console_message(self) -> str:
        """Get the console message to display when this configuration is active."""
        if self.is_local:
            return f"🔧 Using local Supabase environment at {self.url}"
        else:
            return "🌐 Using production Supabase environment"
