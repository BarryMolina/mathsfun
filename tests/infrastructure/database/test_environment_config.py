"""Tests for EnvironmentConfig class."""

import pytest
import os
from unittest.mock import patch, Mock
import requests
from src.infrastructure.database.environment_config import EnvironmentConfig


class TestEnvironmentConfig:
    """Test EnvironmentConfig class functionality."""

    def test_from_environment_local(self):
        """Test creating config from local environment variables."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            config = EnvironmentConfig.from_environment()

            assert config.environment == "local"
            assert config.url == "http://127.0.0.1:54321"
            assert config.anon_key == "local-key"
            assert config.is_local is True

    def test_from_environment_production(self):
        """Test creating config from production environment variables."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            config = EnvironmentConfig.from_environment()

            assert config.environment == "production"
            assert config.url == "https://prod.supabase.co"
            assert config.anon_key == "prod-key"
            assert config.is_local is False

    def test_from_environment_defaults(self):
        """Test creating config with default values."""
        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "", "SUPABASE_URL": "", "SUPABASE_ANON_KEY": ""},
            clear=True,
        ):
            config = EnvironmentConfig.from_environment()

            assert config.environment == "production"  # Default
            assert config.url == ""  # Missing
            assert config.anon_key == ""  # Missing
            assert config.is_local is False

    @patch("requests.get")
    def test_validate_success_local(self, mock_get):
        """Test validation with valid local configuration and running Supabase."""
        # Mock successful health check
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        config = EnvironmentConfig(
            environment="local",
            url="http://127.0.0.1:54321",
            anon_key="test-key",
            is_local=True,
        )

        is_valid, message = config.validate()

        assert is_valid is True
        assert "local development" in message
        assert "validated" in message
        mock_get.assert_called_once_with("http://127.0.0.1:54321/health", timeout=5)

    def test_validate_success_production(self):
        """Test validation with valid production configuration."""
        config = EnvironmentConfig(
            environment="production",
            url="https://test.supabase.co",
            anon_key="prod-key",
            is_local=False,
        )

        is_valid, message = config.validate()

        assert is_valid is True
        assert "production" in message
        assert "validated" in message

    def test_validate_missing_url_local(self):
        """Test validation with missing URL in local environment."""
        config = EnvironmentConfig(
            environment="local", url="", anon_key="test-key", is_local=True
        )

        is_valid, message = config.validate()

        assert is_valid is False
        assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message
        assert "supabase start" in message
        assert ".env.local" in message

    def test_validate_missing_key_production(self):
        """Test validation with missing key in production environment."""
        config = EnvironmentConfig(
            environment="production",
            url="https://test.supabase.co",
            anon_key="",
            is_local=False,
        )

        is_valid, message = config.validate()

        assert is_valid is False
        assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message
        assert ".env file for production" in message

    def test_get_display_name(self):
        """Test get_display_name method."""
        local_config = EnvironmentConfig("local", "", "", True)
        prod_config = EnvironmentConfig("production", "", "", False)

        assert local_config.get_display_name() == "local development"
        assert prod_config.get_display_name() == "production"

    def test_get_console_message(self):
        """Test get_console_message method."""
        local_config = EnvironmentConfig("local", "http://127.0.0.1:54321", "key", True)
        prod_config = EnvironmentConfig("production", "https://prod.co", "key", False)

        local_message = local_config.get_console_message()
        prod_message = prod_config.get_console_message()

        assert "🔧 Using local Supabase environment" in local_message
        assert "http://127.0.0.1:54321" in local_message
        assert "🌐 Using production Supabase environment" in prod_message

    def test_case_insensitive_environment(self):
        """Test that environment variable is case insensitive."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "LOCAL",  # Uppercase
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "key",
            },
            clear=False,
        ):
            config = EnvironmentConfig.from_environment()

            assert config.environment == "local"  # Should be lowercase
            assert config.is_local is True

    @patch("requests.get")
    def test_validate_local_supabase_not_running(self, mock_get):
        """Test validation when local Supabase is not running."""
        # Mock failed health check
        mock_get.side_effect = requests.exceptions.ConnectionError()

        config = EnvironmentConfig(
            environment="local",
            url="http://127.0.0.1:54321",
            anon_key="test-key",
            is_local=True,
        )

        is_valid, message = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message
        assert "supabase start" in message
        assert "http://127.0.0.1:54321" in message

    @patch("requests.get")
    def test_validate_local_supabase_timeout(self, mock_get):
        """Test validation when local Supabase health check times out."""
        # Mock timeout
        mock_get.side_effect = requests.exceptions.Timeout()

        config = EnvironmentConfig(
            environment="local",
            url="http://127.0.0.1:54321",
            anon_key="test-key",
            is_local=True,
        )

        is_valid, message = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message

    @patch("requests.get")
    def test_validate_local_supabase_error_response(self, mock_get):
        """Test validation when local Supabase returns an error response."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        config = EnvironmentConfig(
            environment="local",
            url="http://127.0.0.1:54321",
            anon_key="test-key",
            is_local=True,
        )

        is_valid, message = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message

    def test_is_local_supabase_running_production_skip(self):
        """Test that local Supabase check is skipped for production environment."""
        config = EnvironmentConfig(
            environment="production",
            url="https://prod.supabase.co",
            anon_key="prod-key",
            is_local=False,
        )

        # Should return (True, "") without making any requests
        is_running, error_details = config._is_local_supabase_running()
        assert is_running is True
        assert error_details == ""

    def test_runtime_environment_switching(self):
        """Test that multiple config instances can have different environments."""
        # Create config with production environment
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            prod_config = EnvironmentConfig.from_environment()
            assert prod_config.environment == "production"
            assert prod_config.is_local is False

        # Switch environment variables and create new config
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            local_config = EnvironmentConfig.from_environment()
            assert local_config.environment == "local"
            assert local_config.is_local is True
            assert local_config.url == "http://127.0.0.1:54321"

        # Verify both configs maintain their state
        assert prod_config.environment == "production"
        assert prod_config.is_local is False
        assert local_config.environment == "local"
        assert local_config.is_local is True
