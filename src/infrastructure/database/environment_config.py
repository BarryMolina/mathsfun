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

        Runtime environment switching:
        >>> # First create a local config
        >>> import os
        >>> os.environ["ENVIRONMENT"] = "local"
        >>> local_config = EnvironmentConfig.from_environment()
        >>> print(local_config.get_display_name())  # 'local development'
        >>>
        >>> # Then switch to production
        >>> os.environ["ENVIRONMENT"] = "production"
        >>> prod_config = EnvironmentConfig.from_environment()
        >>> print(prod_config.get_display_name())  # 'production'

        Configuring health checks:
        >>> import os
        >>> os.environ["SUPABASE_HEALTH_ENDPOINT"] = "/api/health"
        >>> os.environ["SUPABASE_HEALTH_TIMEOUT"] = "10"
        >>> config = EnvironmentConfig.from_environment()
        >>> # Health check will use custom endpoint and 10s timeout
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
            is_running, error_details = self._is_local_supabase_running()
            if not is_running:
                fallback_suggestions = self._get_fallback_suggestions(error_details)
                return (
                    False,
                    textwrap.dedent(
                        f"""
                    Local Supabase appears to be offline.
                    Error: {error_details}
                    
                    Troubleshooting steps:
                    {fallback_suggestions}
                    
                    Expected Supabase API at: {self.url}
                """
                    ).strip(),
                )

        env_type = "local development" if self.is_local else "production"
        return True, f"Environment validated for {env_type}"

    def _is_local_supabase_running(self) -> tuple[bool, str]:
        """Check if local Supabase is running by making a health check request.

        Returns:
            tuple: (is_running, error_details) where error_details explains any failure
        """
        if not self.is_local:
            return True, ""  # Skip check for non-local environments

        try:
            # Try to reach the Supabase health endpoint (configurable)
            health_endpoint = os.getenv("SUPABASE_HEALTH_ENDPOINT", "/health")
            health_timeout = int(os.getenv("SUPABASE_HEALTH_TIMEOUT", "5"))
            health_url = f"{self.url}{health_endpoint}"
            response = requests.get(health_url, timeout=health_timeout)
            if response.status_code == 200:
                return True, ""
            else:
                return False, f"Health check failed with HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - Supabase may not be started"
        except requests.exceptions.Timeout:
            return False, f"Health check timed out after {health_timeout}s"
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"

    def _get_fallback_suggestions(self, error_details: str) -> str:
        """Provide contextual fallback suggestions based on the type of error."""
        if "Connection refused" in error_details:
            return textwrap.dedent(
                """
                1. Run 'supabase start' to start local Supabase services
                2. Verify Docker Desktop is running
                3. Check if port 54321 is available
            """
            ).strip()
        elif "timed out" in error_details:
            return textwrap.dedent(
                """
                1. Increase health check timeout with SUPABASE_HEALTH_TIMEOUT=10
                2. Check your network connection
                3. Verify local Supabase services are responding: curl {self.url}/health
            """
            ).strip()
        elif "HTTP" in error_details:
            return textwrap.dedent(
                """
                1. Try a different health endpoint with SUPABASE_HEALTH_ENDPOINT=/status
                2. Check Supabase logs: supabase logs
                3. Restart Supabase: supabase stop && supabase start
            """
            ).strip()
        else:
            return textwrap.dedent(
                """
                1. Run 'supabase start' to start local Supabase services
                2. Switch to production environment: set ENVIRONMENT=production
                3. Check the error logs for more details
            """
            ).strip()

    def get_display_name(self) -> str:
        """Get a human-readable display name for the environment."""
        return "local development" if self.is_local else "production"

    def get_console_message(self) -> str:
        """Get the console message to display when this configuration is active."""
        if self.is_local:
            return f"🔧 Using local Supabase environment at {self.url}"
        else:
            return "🌐 Using production Supabase environment"
