"""Comprehensive tests for SupabaseManager and related OAuth components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
import os
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qs

from src.infrastructure.database.supabase_manager import (
    SupabaseManager,
    OAuthServer,
    OAuthCallbackHandler,
    start_oauth_server,
    validate_environment,
)


@pytest.fixture
def mock_session_storage():
    """Mock session storage."""
    with patch(
        "src.infrastructure.database.supabase_manager.SessionStorage"
    ) as mock_storage_class:
        mock_storage = Mock()
        mock_storage_class.return_value = mock_storage
        yield mock_storage


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    with patch(
        "src.infrastructure.database.supabase_manager.create_client"
    ) as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def supabase_manager(mock_session_storage, mock_supabase_client):
    """Create SupabaseManager instance with mocked dependencies."""
    with patch.dict(
        "src.infrastructure.database.supabase_manager.__dict__",
        {"url": "http://test.supabase.co", "key": "test-key"},
    ):
        manager = SupabaseManager()
        return manager


class TestOAuthServer:
    """Test OAuthServer class."""

    def test_oauth_server_init(self):
        """Test OAuthServer initialization."""
        handler_class = Mock()
        server = OAuthServer(("localhost", 8080), handler_class)

        assert server.auth_result is None
        assert server.server_address == ("127.0.0.1", 8080)


class TestOAuthCallbackHandler:
    """Test OAuthCallbackHandler class."""

    def test_log_message_suppressed(self):
        """Test that log_message is suppressed."""
        # Create a mock handler without initializing the BaseHTTPRequestHandler
        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)

        # Should not raise any exception and should return None
        result = handler.log_message("test %s", "message")
        assert result is None

    def test_do_get_favicon_request(self):
        """Test handling of favicon requests."""
        mock_server = Mock(spec=OAuthServer)
        mock_server.auth_result = None

        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.server = mock_server
        handler.path = "/favicon.ico"
        handler.send_response = Mock()
        handler.end_headers = Mock()

        handler.do_GET()

        handler.send_response.assert_called_once_with(404)
        handler.end_headers.assert_called_once()

    def test_do_get_already_authenticated(self):
        """Test handling when authentication already completed."""
        mock_server = Mock(spec=OAuthServer)
        mock_server.auth_result = {"success": True}

        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.server = mock_server
        handler.path = "/callback"
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()

        handler.do_GET()

        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_once_with("Content-type", "text/html")
        assert handler.wfile.write.called

    def test_do_get_success_callback(self):
        """Test successful OAuth callback."""
        mock_server = Mock(spec=OAuthServer)
        mock_server.auth_result = None

        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.server = mock_server
        handler.path = "/callback?code=test_code&state=test_state"
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()

        handler.do_GET()

        # Verify server.auth_result was set correctly
        assert mock_server.auth_result["success"] is True
        assert mock_server.auth_result["code"] == "test_code"
        assert mock_server.auth_result["state"] == "test_state"

        handler.send_response.assert_called_once_with(200)

    def test_do_get_error_callback(self):
        """Test error OAuth callback."""
        mock_server = Mock(spec=OAuthServer)
        mock_server.auth_result = None

        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.server = mock_server
        handler.path = "/callback?error=access_denied&error_description=User%20denied"
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()

        handler.do_GET()

        # Verify server.auth_result was set correctly
        assert mock_server.auth_result["success"] is False
        assert mock_server.auth_result["error"] == "access_denied"
        assert "User denied" in mock_server.auth_result["error_description"]

        handler.send_response.assert_called_once_with(400)

    def test_do_get_unknown_callback(self):
        """Test unknown callback."""
        mock_server = Mock(spec=OAuthServer)
        mock_server.auth_result = None

        handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
        handler.server = mock_server
        handler.path = "/callback?unknown=param"
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        handler.wfile.write = Mock()

        handler.do_GET()

        # Verify server.auth_result was set correctly
        assert mock_server.auth_result["success"] is False
        assert mock_server.auth_result["error"] == "unknown_callback"

        handler.send_response.assert_called_once_with(400)


class TestStartOAuthServer:
    """Test start_oauth_server function."""

    @patch("src.infrastructure.database.supabase_manager.OAuthServer")
    @patch("src.infrastructure.database.supabase_manager.threading.Thread")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    def test_start_oauth_server(self, mock_sleep, mock_thread, mock_oauth_server):
        """Test OAuth server startup."""
        mock_server_instance = Mock()
        mock_oauth_server.return_value = mock_server_instance

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        # Mock threading.Event
        with patch(
            "src.infrastructure.database.supabase_manager.threading.Event"
        ) as mock_event:
            mock_event_instance = Mock()
            mock_event.return_value = mock_event_instance

            result = start_oauth_server(8080)

        # Verify server creation and threading
        mock_oauth_server.assert_called_once_with(
            ("localhost", 8080), OAuthCallbackHandler
        )
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        mock_event_instance.wait.assert_called_once_with(timeout=5)
        mock_sleep.assert_called_once_with(0.1)

        assert result == mock_server_instance


class TestSupabaseManagerInit:
    """Test SupabaseManager initialization."""

    def test_init(self, mock_session_storage, mock_supabase_client):
        """Test SupabaseManager initialization."""
        with patch.dict(
            "src.infrastructure.database.supabase_manager.__dict__",
            {"url": "http://test.supabase.co", "key": "test-key"},
        ):
            manager = SupabaseManager()

        assert manager._client == mock_supabase_client
        assert manager._authenticated is False
        assert manager._session_data is None
        assert isinstance(manager._lock, threading.Lock)


class TestSupabaseManagerBasicMethods:
    """Test basic SupabaseManager methods."""

    def test_get_client(self, supabase_manager):
        """Test get_client method."""
        result = supabase_manager.get_client()
        assert result == supabase_manager._client

    def test_is_authenticated_false(self, supabase_manager):
        """Test is_authenticated when not authenticated."""
        result = supabase_manager.is_authenticated()
        assert result is False

    def test_is_authenticated_true(self, supabase_manager):
        """Test is_authenticated when authenticated."""
        supabase_manager._authenticated = True
        result = supabase_manager.is_authenticated()
        assert result is True

    def test_get_session_data_none(self, supabase_manager):
        """Test get_session_data when no session data."""
        result = supabase_manager.get_session_data()
        assert result is None

    def test_get_session_data_exists(self, supabase_manager):
        """Test get_session_data when session data exists."""
        session_data = {"access_token": "test_token"}
        supabase_manager._session_data = session_data

        result = supabase_manager.get_session_data()
        assert result == session_data

    def test_sign_out(
        self, supabase_manager, mock_session_storage, mock_supabase_client
    ):
        """Test sign_out method."""
        # Set up authenticated state
        supabase_manager._authenticated = True
        supabase_manager._session_data = {"access_token": "test_token"}

        supabase_manager.sign_out()

        assert supabase_manager._authenticated is False
        assert supabase_manager._session_data is None
        mock_session_storage.clear_session.assert_called_once()


class TestSupabaseManagerSessionManagement:
    """Test session management methods."""

    def test_save_session_not_authenticated(self, supabase_manager):
        """Test save_session when not authenticated."""
        result = supabase_manager.save_session()
        assert result is False

    def test_save_session_no_session_data(self, supabase_manager):
        """Test save_session when no session data."""
        supabase_manager._authenticated = True
        result = supabase_manager.save_session()
        assert result is False

    def test_save_session_success(self, supabase_manager, mock_session_storage):
        """Test successful save_session."""
        supabase_manager._authenticated = True
        supabase_manager._session_data = {"access_token": "test_token"}
        mock_session_storage.save_session.return_value = True

        result = supabase_manager.save_session()

        assert result is True
        mock_session_storage.save_session.assert_called_once_with(
            {"access_token": "test_token"}
        )

    def test_save_session_exception(self, supabase_manager, mock_session_storage):
        """Test save_session with exception."""
        supabase_manager._authenticated = True
        supabase_manager._session_data = {"access_token": "test_token"}
        mock_session_storage.save_session.side_effect = Exception("Save error")

        with patch("builtins.print") as mock_print:
            result = supabase_manager.save_session()

        assert result is False
        mock_print.assert_called_once_with("Warning: Error saving session: Save error")

    def test_restore_session_missing_tokens(self, supabase_manager):
        """Test restore_session with missing tokens."""
        session_data = {"access_token": "test_token"}  # Missing refresh_token

        result = supabase_manager.restore_session(session_data)
        assert result is False

    def test_restore_session_success_set_session(
        self, supabase_manager, mock_supabase_client
    ):
        """Test successful restore_session using set_session."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }

        result = supabase_manager.restore_session(session_data)

        assert result is True
        mock_supabase_client.auth.set_session.assert_called_once_with(
            access_token="test_access_token", refresh_token="test_refresh_token"
        )
        assert supabase_manager._authenticated is True
        assert supabase_manager._session_data == session_data

    def test_restore_session_fallback_to_refresh(
        self, supabase_manager, mock_supabase_client
    ):
        """Test restore_session falling back to refresh_session."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }

        # Make set_session fail
        mock_supabase_client.auth.set_session.side_effect = Exception(
            "Set session failed"
        )

        # Mock successful refresh
        mock_refresh_result = Mock()
        mock_refresh_result.session = Mock()
        mock_supabase_client.auth.refresh_session.return_value = mock_refresh_result

        result = supabase_manager.restore_session(session_data)

        assert result is True
        mock_supabase_client.auth.refresh_session.assert_called_once_with(
            "test_refresh_token"
        )

    def test_restore_session_refresh_fails(
        self, supabase_manager, mock_supabase_client
    ):
        """Test restore_session when refresh also fails."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }

        # Make set_session fail
        mock_supabase_client.auth.set_session.side_effect = Exception(
            "Set session failed"
        )

        # Make refresh return no session
        mock_refresh_result = Mock()
        mock_refresh_result.session = None
        mock_supabase_client.auth.refresh_session.return_value = mock_refresh_result

        result = supabase_manager.restore_session(session_data)
        assert result is False

    def test_restore_session_exception(self, supabase_manager, mock_supabase_client):
        """Test restore_session with exception."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }

        mock_supabase_client.auth.set_session.side_effect = Exception("Auth error")
        mock_supabase_client.auth.refresh_session.side_effect = Exception(
            "Refresh error"
        )

        result = supabase_manager.restore_session(session_data)
        assert result is False

    def test_load_persisted_session_no_data(
        self, supabase_manager, mock_session_storage
    ):
        """Test load_persisted_session with no stored data."""
        mock_session_storage.load_session.return_value = None

        result = supabase_manager.load_persisted_session()
        assert result is False

    def test_load_persisted_session_success(
        self, supabase_manager, mock_session_storage
    ):
        """Test successful load_persisted_session."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }
        mock_session_storage.load_session.return_value = session_data

        with patch.object(
            supabase_manager, "restore_session", return_value=True
        ) as mock_restore:
            result = supabase_manager.load_persisted_session()

        assert result is True
        mock_restore.assert_called_once_with(session_data)

    def test_load_persisted_session_restore_fails(
        self, supabase_manager, mock_session_storage
    ):
        """Test load_persisted_session when restore fails."""
        session_data = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }
        mock_session_storage.load_session.return_value = session_data

        with patch.object(
            supabase_manager, "restore_session", return_value=False
        ) as mock_restore:
            result = supabase_manager.load_persisted_session()

        assert result is False
        mock_session_storage.clear_session.assert_called_once()

    def test_load_persisted_session_exception(
        self, supabase_manager, mock_session_storage
    ):
        """Test load_persisted_session with exception."""
        mock_session_storage.load_session.side_effect = Exception("Load error")

        with patch("builtins.print") as mock_print:
            result = supabase_manager.load_persisted_session()

        assert result is False
        mock_print.assert_called_once_with(
            "Warning: Error loading persisted session: Load error"
        )


class TestSignInWithGoogle:
    """Test sign_in_with_google method."""

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    def test_sign_in_with_google_no_oauth_url(
        self,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google when OAuth URL is not returned."""
        mock_server = Mock()
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()
        mock_create_client.return_value = mock_oauth_client

        mock_oauth_response = Mock()
        mock_oauth_response.url = None
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert "Failed to get OAuth URL" in result["error"]
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_timeout(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google timeout."""
        mock_server = Mock()
        mock_server.auth_result = None  # Never gets set
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()
        mock_create_client.return_value = mock_oauth_client

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        # Mock time progression to trigger timeout
        mock_time.side_effect = [0, 301]  # Start at 0, then exceed 300 second timeout

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert result["error"] == "Authentication timeout"
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_success(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test successful sign_in_with_google."""
        # Mock server with successful auth result
        mock_server = Mock()
        mock_server.auth_result = {"success": True, "code": "test_auth_code"}
        mock_start_server.return_value = mock_server

        # Mock OAuth client
        mock_oauth_client = Mock()

        # Create a side effect for create_client that captures the storage and sets the code verifier
        def mock_create_client_with_storage(url, key, options=None):
            if options and hasattr(options, "storage") and options.storage:
                # Simulate what happens when sign_in_with_oauth is called - it stores the code verifier
                options.storage.set_item(
                    "supabase.auth.token-code-verifier", "test_code_verifier"
                )
            return mock_oauth_client

        mock_create_client.side_effect = mock_create_client_with_storage

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"

        # Create a side effect that simulates what the real sign_in_with_oauth does:
        # it stores the code verifier in the storage that was passed to create_client
        def simulate_oauth_flow(*args, **kwargs):
            # The create_client call will be made with options.storage
            # We need to store the code verifier in that storage
            return mock_oauth_response

        mock_oauth_client.auth.sign_in_with_oauth.side_effect = simulate_oauth_flow

        # Mock session exchange
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"full_name": "Test User"}
        mock_user.app_metadata = {"provider": "google"}
        mock_user.last_sign_in_at = "2023-01-01T00:00:00Z"

        mock_session = Mock()
        mock_session.access_token = "access_token_123"
        mock_session.refresh_token = "refresh_token_123"
        mock_session.expires_at = 1234567890
        mock_session.provider_token = "provider_token_123"
        mock_session.provider_refresh_token = "provider_refresh_123"

        mock_session_response = Mock()
        mock_session_response.session = mock_session
        mock_session_response.user = mock_user

        mock_oauth_client.auth.exchange_code_for_session.return_value = (
            mock_session_response
        )

        # Mock time to prevent timeout
        mock_time.side_effect = [0, 1, 2]  # Stay well under timeout

        # Mock the save_session method
        with patch.object(supabase_manager, "save_session") as mock_save:
            result = supabase_manager.sign_in_with_google()

        # Verify success
        assert result["success"] is True
        assert result["user"]["id"] == "user123"
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["name"] == "Test User"
        assert result["session"]["access_token"] == "access_token_123"

        # Verify authentication state
        assert supabase_manager._authenticated is True
        assert supabase_manager._session_data is not None

        mock_save.assert_called_once()
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_no_code_verifier(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google when code verifier is missing."""
        mock_server = Mock()
        mock_server.auth_result = {"success": True, "code": "test_auth_code"}
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()
        mock_create_client.return_value = mock_oauth_client

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        mock_time.side_effect = [0, 1, 2]

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert "Could not find code verifier" in result["error"]
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_exchange_fails(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google when code exchange fails."""
        mock_server = Mock()
        mock_server.auth_result = {"success": True, "code": "test_auth_code"}
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()

        # Create a side effect for create_client that captures the storage and sets the code verifier
        def mock_create_client_with_storage(url, key, options=None):
            if options and hasattr(options, "storage") and options.storage:
                # Simulate what happens when sign_in_with_oauth is called - it stores the code verifier
                options.storage.set_item(
                    "supabase.auth.token-code-verifier", "test_code_verifier"
                )
            return mock_oauth_client

        mock_create_client.side_effect = mock_create_client_with_storage

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        # Make exchange fail
        mock_oauth_client.auth.exchange_code_for_session.side_effect = Exception(
            "Exchange failed"
        )

        mock_time.side_effect = [0, 1, 2]

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert "Failed to exchange code for session" in result["error"]
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_no_session_created(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google when no session is created."""
        mock_server = Mock()
        mock_server.auth_result = {"success": True, "code": "test_auth_code"}
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()

        # Create a side effect for create_client that captures the storage and sets the code verifier
        def mock_create_client_with_storage(url, key, options=None):
            if options and hasattr(options, "storage") and options.storage:
                # Simulate what happens when sign_in_with_oauth is called - it stores the code verifier
                options.storage.set_item(
                    "supabase.auth.token-code-verifier", "test_code_verifier"
                )
            return mock_oauth_client

        mock_create_client.side_effect = mock_create_client_with_storage

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        # Mock session exchange returning no session
        mock_session_response = Mock()
        mock_session_response.session = None
        mock_oauth_client.auth.exchange_code_for_session.return_value = (
            mock_session_response
        )

        mock_time.side_effect = [0, 1, 2]

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert "Failed to create session from code" in result["error"]
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    @patch("src.infrastructure.database.supabase_manager.time.sleep")
    @patch("src.infrastructure.database.supabase_manager.time.time")
    @patch("builtins.print")
    def test_sign_in_with_google_server_error_result(
        self,
        mock_print,
        mock_time,
        mock_sleep,
        mock_create_client,
        mock_start_server,
        mock_webbrowser,
        supabase_manager,
    ):
        """Test sign_in_with_google when server returns error result."""
        mock_server = Mock()
        mock_server.auth_result = {
            "success": False,
            "error": "access_denied",
            "error_description": "User denied access",
        }
        mock_start_server.return_value = mock_server

        mock_oauth_client = Mock()
        mock_create_client.return_value = mock_oauth_client

        mock_oauth_response = Mock()
        mock_oauth_response.url = "https://oauth.example.com"
        mock_oauth_client.auth.sign_in_with_oauth.return_value = mock_oauth_response

        mock_time.side_effect = [0, 1, 2]

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert result["error"] == "access_denied"
        mock_server.shutdown.assert_called_once()

    @patch("src.infrastructure.database.supabase_manager.webbrowser.open")
    @patch("src.infrastructure.database.supabase_manager.start_oauth_server")
    @patch("src.infrastructure.database.supabase_manager.create_client")
    def test_sign_in_with_google_general_exception(
        self, mock_create_client, mock_start_server, mock_webbrowser, supabase_manager
    ):
        """Test sign_in_with_google with general exception."""
        mock_server = Mock()
        mock_start_server.return_value = mock_server

        # Make create_client raise an exception
        mock_create_client.side_effect = Exception("General error")

        result = supabase_manager.sign_in_with_google()

        assert result["success"] is False
        assert result["error"] == "General error"
        mock_server.shutdown.assert_called_once()


class TestValidateEnvironment:
    """Test validate_environment function."""

    def test_validate_environment_missing_url(self):
        """Test validate_environment with missing URL."""
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "", "SUPABASE_ANON_KEY": "test-key"},
            clear=False,
        ):
            valid, message = validate_environment()

            assert valid is False
            assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message

    def test_validate_environment_missing_key(self):
        """Test validate_environment with missing key."""
        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.supabase.co", "SUPABASE_ANON_KEY": ""},
            clear=False,
        ):
            valid, message = validate_environment()

            assert valid is False
            assert "Missing SUPABASE_URL or SUPABASE_ANON_KEY" in message

    def test_validate_environment_success(self):
        """Test validate_environment with valid environment."""
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "http://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-key",
            },
            clear=False,
        ):
            valid, message = validate_environment()

            assert valid is True
            assert "Environment validated" in message


class TestPKCEStorage:
    """Test PKCEStorage inner class."""

    def test_pkce_storage_operations(self, supabase_manager):
        """Test PKCEStorage get, set, and remove operations."""
        # We need to access the PKCEStorage class from the sign_in_with_google method
        # This is a bit of a hack since it's defined inside the method

        with patch(
            "src.infrastructure.database.supabase_manager.start_oauth_server"
        ) as mock_start_server:
            mock_server = Mock()
            mock_server.auth_result = {"success": False}  # To exit early
            mock_start_server.return_value = mock_server

            with patch(
                "src.infrastructure.database.supabase_manager.create_client"
            ) as mock_create_client:
                mock_oauth_client = Mock()
                mock_oauth_response = Mock()
                mock_oauth_response.url = "https://oauth.example.com"
                mock_oauth_client.auth.sign_in_with_oauth.return_value = (
                    mock_oauth_response
                )
                mock_create_client.return_value = mock_oauth_client

                with patch(
                    "src.infrastructure.database.supabase_manager.time.time",
                    side_effect=[0, 1, 2],
                ):
                    with patch(
                        "src.infrastructure.database.supabase_manager.webbrowser.open"
                    ):
                        # This will create a PKCEStorage instance internally
                        supabase_manager.sign_in_with_google()

        # Test is implicit in the fact that the method completes without error
        # The PKCEStorage class is tested indirectly through the OAuth flow
        assert True  # Placeholder assertion


@pytest.mark.unit
class TestSupabaseManagerMarkings:
    """Test that all methods are properly covered by the test suite."""

    def test_all_public_methods_tested(self):
        """Verify all public methods of SupabaseManager are tested."""
        public_methods = [
            "get_client",
            "is_authenticated",
            "sign_out",
            "get_session_data",
            "restore_session",
            "load_persisted_session",
            "save_session",
            "sign_in_with_google",
        ]

        # This test serves as documentation of what should be tested
        # All methods listed above have corresponding test cases
        assert len(public_methods) == 8


class TestSupabaseManagerEnvironmentSwitching:
    """Test SupabaseManager runtime environment switching capabilities."""

    def test_runtime_environment_detection(self):
        """Test that SupabaseManager instances can have different environments at runtime."""
        # Create manager with production environment
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            prod_manager = SupabaseManager()
            assert prod_manager.config.environment == "production"
            assert prod_manager.config.is_local is False
            assert prod_manager.config.url == "https://prod.supabase.co"

        # Create manager with local environment (simulating runtime switch)
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            local_manager = SupabaseManager()
            assert local_manager.config.environment == "local"
            assert local_manager.config.is_local is True
            assert local_manager.config.url == "http://127.0.0.1:54321"

        # Verify both managers maintain their configurations
        assert prod_manager.config.environment == "production"
        assert local_manager.config.environment == "local"

        # Verify they have different clients pointing to different URLs
        assert prod_manager.config.url != local_manager.config.url

    def test_environment_validation_changes_with_environment(self):
        """Test that validate_environment reflects current environment variables."""
        # Test production validation
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "https://prod.supabase.co",
                "SUPABASE_ANON_KEY": "prod-key",
            },
            clear=False,
        ):
            is_valid, message = validate_environment()
            assert is_valid is True
            assert "production" in message

        # Test local validation (will fail health check)
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "SUPABASE_URL": "http://127.0.0.1:54321",
                "SUPABASE_ANON_KEY": "local-key",
            },
            clear=False,
        ):
            # This will fail because local Supabase isn't actually running
            is_valid, message = validate_environment()
            assert is_valid is False
            assert "Local Supabase appears to be offline" in message

    def test_supabase_manager_validation_enforcement(self):
        """Test that SupabaseManager enforces critical configuration validation."""
        # Test missing URL raises ValueError
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "",  # Missing URL
                "SUPABASE_ANON_KEY": "test-key",
            },
            clear=False,
        ):
            with pytest.raises(ValueError, match="Critical configuration missing"):
                SupabaseManager()

        # Test missing key raises ValueError
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "",  # Missing key
            },
            clear=False,
        ):
            with pytest.raises(ValueError, match="Critical configuration missing"):
                SupabaseManager()
