"""Tests for EnvironmentConfig class."""

import pytest
import os
from unittest.mock import patch, Mock
import requests
from src.infrastructure.database.environment_config import (
    EnvironmentConfig,
    ValidationLevel,
)


class TestEnvironmentConfig:
    """Test EnvironmentConfig class functionality."""

    def test_from_environment_local(self):
        """Test creating config from local environment variables."""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            # Mock dotenv.load_dotenv to prevent loading from .env.local file
            with patch(
                "src.infrastructure.database.environment_config.dotenv.load_dotenv"
            ):
                config = EnvironmentConfig.from_environment(use_local=True)

                assert config.environment == "local"
                assert config.url == "http://127.0.0.1:54321"
                assert config.anon_key == "local-key"
                assert config.is_local is True

    def test_from_environment_production(self):
        """Test creating config from production environment variables."""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            config = EnvironmentConfig.from_environment(use_local=False)

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

        is_valid, message, level = config.validate()

        assert is_valid is True
        assert "local development" in message
        assert level == ValidationLevel.INFO
        assert "validated" in message
        mock_get.assert_called_once_with("http://127.0.0.1:54321/rest/v1/", timeout=5)

    def test_validate_success_production(self):
        """Test validation with valid production configuration."""
        config = EnvironmentConfig(
            environment="production",
            url="https://test.supabase.co",
            anon_key="prod-key",
            is_local=False,
        )

        is_valid, message, level = config.validate()

        assert is_valid is True
        assert "production" in message
        assert level == ValidationLevel.INFO
        assert "validated" in message

    def test_validate_missing_url_local(self):
        """Test validation with missing URL in local environment."""
        config = EnvironmentConfig(
            environment="local", url="", anon_key="test-key", is_local=True
        )

        is_valid, message, level = config.validate()

        assert is_valid is False
        assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message
        assert "supabase start" in message
        assert ".env.local" in message
        assert level == ValidationLevel.CRITICAL

    def test_validate_missing_key_production(self):
        """Test validation with missing key in production environment."""
        config = EnvironmentConfig(
            environment="production",
            url="https://test.supabase.co",
            anon_key="",
            is_local=False,
        )

        is_valid, message, level = config.validate()

        assert is_valid is False
        assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message
        assert ".env file for production" in message
        assert level == ValidationLevel.CRITICAL

    def test_get_display_name(self):
        """Test get_display_name method."""
        local_config = EnvironmentConfig("local", "", "", True)
        prod_config = EnvironmentConfig("production", "", "", False)

        assert local_config.get_display_name() == "local development"
        assert prod_config.get_display_name() == "production"

    def test_validation_level_enum_values(self):
        """Test ValidationLevel enum has expected values."""
        assert ValidationLevel.CRITICAL.value == "critical"
        assert ValidationLevel.WARNING.value == "warning"
        assert ValidationLevel.INFO.value == "info"

    def test_validation_levels_for_different_scenarios(self):
        """Test that different validation scenarios return appropriate ValidationLevel."""
        # Test CRITICAL level for missing config
        critical_config = EnvironmentConfig(
            environment="production", url="", anon_key="", is_local=False
        )
        is_valid, message, level = critical_config.validate()
        assert not is_valid
        assert level == ValidationLevel.CRITICAL
        assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message

        # Test INFO level for successful validation
        info_config = EnvironmentConfig(
            environment="production",
            url="https://test.supabase.co",
            anon_key="test-key",
            is_local=False,
        )
        is_valid, message, level = info_config.validate()
        assert is_valid
        assert level == ValidationLevel.INFO
        assert "validated" in message.lower()

    @patch("requests.get")
    def test_validation_level_warning_for_health_check_failures(self, mock_get):
        """Test that health check failures return WARNING level."""
        # Test connection error returns WARNING
        mock_get.side_effect = requests.exceptions.ConnectionError()
        config = EnvironmentConfig(
            environment="local",
            url="http://127.0.0.1:54321",
            anon_key="test-key",
            is_local=True,
        )
        is_valid, message, level = config.validate()
        assert not is_valid
        assert level == ValidationLevel.WARNING
        assert "Local Supabase appears to be offline" in message

        # Test HTTP error returns WARNING
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        is_valid, message, level = config.validate()
        assert not is_valid
        assert level == ValidationLevel.WARNING
        assert "Local Supabase appears to be offline" in message

    def test_get_console_message(self):
        """Test get_console_message method."""
        local_config = EnvironmentConfig("local", "http://127.0.0.1:54321", "key", True)
        prod_config = EnvironmentConfig("production", "https://prod.co", "key", False)

        local_message = local_config.get_console_message()
        prod_message = prod_config.get_console_message()

        assert "🔧 Using local Supabase environment" in local_message
        assert "http://127.0.0.1:54321" in local_message
        assert "🌐 Using production Supabase environment" in prod_message

    def test_use_local_parameter_behavior(self):
        """Test that use_local parameter correctly sets environment."""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "key",
            },
            clear=False,
        ):
            # Test local configuration
            local_config = EnvironmentConfig.from_environment(use_local=True)
            assert local_config.environment == "local"
            assert local_config.is_local is True

            # Test production configuration
            prod_config = EnvironmentConfig.from_environment(use_local=False)
            assert prod_config.environment == "production"
            assert prod_config.is_local is False

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

        is_valid, message, level = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message
        assert "supabase start" in message
        assert "http://127.0.0.1:54321" in message
        assert level == ValidationLevel.WARNING

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

        is_valid, message, level = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message
        assert level == ValidationLevel.WARNING

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

        is_valid, message, level = config.validate()

        assert is_valid is False
        assert "Local Supabase appears to be offline" in message
        assert level == ValidationLevel.WARNING

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
        """Test that multiple config instances can have different environments using use_local parameter."""
        # Create config with production environment
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            prod_config = EnvironmentConfig.from_environment(use_local=False)
            assert prod_config.environment == "production"
            assert prod_config.is_local is False

        # Create config with local environment using same environment variables
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            local_config = EnvironmentConfig.from_environment(use_local=True)
            assert local_config.environment == "local"
            assert local_config.is_local is True
            assert local_config.url == "http://127.0.0.1:54321"

        # Verify both configs maintain their state
        assert prod_config.environment == "production"
        assert prod_config.is_local is False
        assert local_config.environment == "local"
        assert local_config.is_local is True
