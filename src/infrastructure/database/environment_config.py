"""Environment configuration management for Supabase connections."""

import os
import requests
import textwrap
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import dotenv


class ValidationLevel(Enum):
    """Validation levels for configuration errors."""

    CRITICAL = "critical"  # Missing essential config that prevents operation
    WARNING = "warning"  # Service availability issues but can continue with degradation
    INFO = "info"  # Informational messages about configuration state


@dataclass
class EnvironmentConfig:
    """Configuration object that encapsulates all environment-related settings.

    This class manages Supabase environment configuration including URL, authentication keys,
    environment detection, and health checks for local development environments. It provides
    runtime configuration loading, validation with different severity levels, and resilient
    health checking with detailed error diagnostics.

    Attributes:
        environment: The current environment ('local' or 'production')
        url: Supabase API URL
        anon_key: Supabase anonymous API key
        is_local: Boolean indicating if running in local development mode

    Environment Variables:
        SUPABASE_URL: Supabase API URL
        SUPABASE_ANON_KEY: Supabase anonymous API key

    Examples:
        Basic usage:
        >>> config = EnvironmentConfig.from_environment()
        >>> print(config.environment)  # 'local' or 'production'

        Manual configuration:
        >>> config = EnvironmentConfig(
        ...     environment="local",
        ...     url="http://127.0.0.1:54321",
        ...     anon_key="your-anon-key",
        ...     is_local=True
        ... )

        Validation with error levels:
        >>> is_valid, message, level = config.validate()
        >>> if not is_valid:
        ...     if level == ValidationLevel.CRITICAL:
        ...         raise RuntimeError(f"Critical error: {message}")
        ...     elif level == ValidationLevel.WARNING:
        ...         print(f"Warning: {message}")

        Runtime environment switching:
        >>> import os
        >>> os.environ["ENVIRONMENT"] = "local"
        >>> local_config = EnvironmentConfig.from_environment()
        >>> print(local_config.get_display_name())  # 'local development'
        >>>
        >>> os.environ["ENVIRONMENT"] = "production"
        >>> prod_config = EnvironmentConfig.from_environment()
        >>> print(prod_config.get_display_name())  # 'production'

        Health check for local environments:
        >>> config = EnvironmentConfig.from_environment(use_local=True)
        >>> is_valid, message, level = config.validate()
        >>> # Health check will use the standard /rest/v1/ endpoint

    Health Check Behavior:
        - Only performed for local environments (is_local=True)
        - Uses the standard Supabase /rest/v1/ endpoint for validation
        - Differentiates between connection, timeout, and HTTP response errors
        - Provides contextual troubleshooting suggestions based on error type
        - Returns ValidationLevel.WARNING for health check failures (allows graceful degradation)
    """

    environment: str
    url: str
    anon_key: str
    is_local: bool

    @classmethod
    def from_environment(cls, use_local: bool = False) -> "EnvironmentConfig":
        """Create configuration from environment variables.

        Args:
            use_local: If True, load .env.local for local development.
                      If False, load .env for production.
        """
        # Load the appropriate environment file based on use_local flag
        if use_local:
            # Load .env.local for local development
            dotenv.load_dotenv(".env.local")
            environment = "local"
            is_local = True
        else:
            # Load .env for production (default behavior)
            dotenv.load_dotenv()
            environment = "production"
            is_local = False

        url = os.getenv("SUPABASE_URL") or ""
        anon_key = os.getenv("SUPABASE_ANON_KEY") or ""

        return cls(
            environment=environment, url=url, anon_key=anon_key, is_local=is_local
        )

    def validate(self) -> tuple[bool, str, ValidationLevel]:
        """Validate that required configuration is available and services are running.

        Returns:
            tuple: (is_valid, message, validation_level) where validation_level indicates
                   the severity of any validation failure
        """
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
                    ValidationLevel.CRITICAL,
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
                    ValidationLevel.CRITICAL,
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
                    ValidationLevel.WARNING,
                )

        env_type = "local development" if self.is_local else "production"
        return True, f"Environment validated for {env_type}", ValidationLevel.INFO

    def _is_local_supabase_running(self) -> tuple[bool, str]:
        """Check if local Supabase is running by making a health check request.

        This method attempts to connect to the local Supabase health endpoint to verify
        that the service is running and responding. It differentiates between various
        types of connection and HTTP errors to provide better diagnostic information.

        Returns:
            tuple: (is_running, error_details) where error_details explains any failure
                   with specific categorization of the error type for better troubleshooting
        """
        if not self.is_local:
            return True, ""  # Skip check for non-local environments

        try:
            # Use the standard Supabase REST API endpoint for health checking
            health_url = f"{self.url}/rest/v1/"
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return True, ""
            elif response.status_code == 404:
                return (
                    False,
                    "REST API endpoint not found (HTTP 404). Supabase may not be fully initialized",
                )
            elif response.status_code == 503:
                return (
                    False,
                    f"Service unavailable (HTTP 503). Supabase services may be starting up or experiencing issues",
                )
            elif response.status_code >= 500:
                return (
                    False,
                    f"Server error (HTTP {response.status_code}). Supabase may be experiencing internal issues",
                )
            elif response.status_code >= 400:
                return (
                    False,
                    f"Client error (HTTP {response.status_code}). Supabase API may have issues",
                )
            else:
                return (
                    False,
                    f"Unexpected HTTP response {response.status_code} from health check",
                )
        except requests.exceptions.ConnectionError as e:
            if "Connection refused" in str(e):
                return (
                    False,
                    "Connection refused - Supabase services are not running or not accessible on the configured port",
                )
            elif "Name resolution" in str(e) or "Name or service not known" in str(e):
                return (
                    False,
                    "DNS resolution failed - Check if the Supabase URL is correct",
                )
            else:
                return False, f"Connection error - {str(e)}"
        except requests.exceptions.Timeout:
            return (
                False,
                "Health check timed out after 5s - Service may be slow to respond or unreachable",
            )
        except requests.exceptions.RequestException as e:
            return False, f"Network request failed: {str(e)}"

    def _get_fallback_suggestions(self, error_details: str) -> str:
        """Provide contextual fallback suggestions based on the specific type of error.

        This method analyzes the error details to provide targeted troubleshooting
        steps, with fallback strategies for when health checks fail.
        """
        if "Connection refused" in error_details:
            return textwrap.dedent(
                """
                1. Run 'supabase start' to start local Supabase services
                2. Verify Docker Desktop is running and containers are healthy
                3. Check if port 54321 is available: lsof -i :54321
                4. Fallback: Use production environment with ENVIRONMENT=production
            """
            ).strip()
        elif "DNS resolution failed" in error_details:
            return textwrap.dedent(
                """
                1. Verify SUPABASE_URL is correct (should be http://127.0.0.1:54321 for local)
                2. Check network connectivity
                3. Try alternative localhost: http://localhost:54321
                4. Fallback: Use production environment with valid URL
            """
            ).strip()
        elif "timed out" in error_details:
            return textwrap.dedent(
                f"""
                1. Check system resources (CPU/Memory usage)
                2. Verify services are starting: curl -v {self.url}/rest/v1/
                3. Wait for services to fully initialize
                4. Fallback: Skip health check by switching to production environment
            """
            ).strip()
        elif "404" in error_details:
            return textwrap.dedent(
                """
                1. Check if Supabase is fully initialized
                2. Verify all services are running: supabase status
                3. Check Supabase version compatibility
                4. Fallback: Use production environment
            """
            ).strip()
        elif "503" in error_details or "Server error" in error_details:
            return textwrap.dedent(
                """
                1. Wait for services to fully initialize (may take 1-2 minutes)
                2. Check Supabase logs: supabase logs
                3. Restart services: supabase stop && supabase start
                4. Fallback: Use production environment if local issues persist
            """
            ).strip()
        elif "HTTP" in error_details:
            return textwrap.dedent(
                """
                1. Check Supabase service logs: supabase logs
                2. Restart Supabase: supabase stop && supabase start
                3. Verify all services are healthy: supabase status
                4. Fallback: Continue with production environment
            """
            ).strip()
        else:
            return textwrap.dedent(
                """
                1. Run 'supabase start' to start local Supabase services
                2. Verify Docker and all dependencies are installed
                3. Check system logs for additional error details
                4. Fallback: Switch to production environment
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
