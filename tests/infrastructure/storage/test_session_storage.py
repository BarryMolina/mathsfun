"""Comprehensive tests for SessionStorage class."""

import pytest
import json
import os
import stat
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.infrastructure.storage.session_storage import SessionStorage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def session_storage(temp_dir):
    """Create SessionStorage instance with temporary directory."""
    with patch.object(
        SessionStorage, "_get_config_directory", return_value=temp_dir / "mathsfun"
    ):
        storage = SessionStorage("test_app")
        return storage


@pytest.fixture
def sample_session_data():
    """Create sample session data for testing."""
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_at": time.time() + 3600,  # 1 hour from now
    }


@pytest.fixture
def expired_session_data():
    """Create expired session data for testing."""
    return {
        "access_token": "expired_access_token",
        "refresh_token": "expired_refresh_token",
        "expires_at": time.time() - 3600,  # 1 hour ago
    }


class TestSessionStorageInit:
    """Test SessionStorage initialization."""

    def test_init_default_app_name(self, temp_dir):
        """Test initialization with default app name."""
        with patch.object(
            SessionStorage, "_get_config_directory", return_value=temp_dir / "mathsfun"
        ):
            storage = SessionStorage()
            assert storage.app_name == "mathsfun"

    def test_init_custom_app_name(self, temp_dir):
        """Test initialization with custom app name."""
        with patch.object(
            SessionStorage,
            "_get_config_directory",
            return_value=temp_dir / "custom_app",
        ):
            storage = SessionStorage("custom_app")
            assert storage.app_name == "custom_app"

    def test_init_creates_config_directory(self, temp_dir):
        """Test that initialization creates config directory."""
        config_dir = temp_dir / "test_mathsfun"
        with patch.object(
            SessionStorage, "_get_config_directory", return_value=config_dir
        ):
            storage = SessionStorage("test_mathsfun")
            assert config_dir.exists()


class TestGetConfigDirectory:
    """Test _get_config_directory method."""

    @patch("os.name", "nt")
    @patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    @patch("src.infrastructure.storage.session_storage.Path")
    def test_get_config_directory_windows(self, mock_path):
        """Test config directory on Windows."""
        # Mock the Path behavior
        mock_path_instance = Mock()
        mock_path_instance.__truediv__ = Mock(return_value=mock_path_instance)
        mock_path.return_value = mock_path_instance

        storage = SessionStorage("testapp")
        config_dir = storage._get_config_directory()

        # Verify Path was called with APPDATA
        mock_path.assert_called_with("C:\\Users\\Test\\AppData\\Roaming")
        # Verify the path division was called with app name
        mock_path_instance.__truediv__.assert_called_with("testapp")

    @patch("os.name", "posix")
    @patch.dict(os.environ, {"XDG_CONFIG_HOME": "/home/test/.config"})
    def test_get_config_directory_linux_with_xdg(self):
        """Test config directory on Linux with XDG_CONFIG_HOME."""
        storage = SessionStorage("testapp")
        config_dir = storage._get_config_directory()
        assert str(config_dir) == "/home/test/.config/testapp"

    @patch("os.name", "posix")
    @patch.dict(os.environ, {}, clear=True)
    @patch("os.path.expanduser")
    def test_get_config_directory_linux_without_xdg(self, mock_expanduser):
        """Test config directory on Linux without XDG_CONFIG_HOME."""
        mock_expanduser.return_value = "/home/test/.config"
        storage = SessionStorage("testapp")
        config_dir = storage._get_config_directory()
        assert str(config_dir) == "/home/test/.config/testapp"


class TestEnsureConfigDirectory:
    """Test _ensure_config_directory method."""

    def test_ensure_config_directory_creates_directory(self, temp_dir):
        """Test that config directory is created."""
        config_dir = temp_dir / "new_app"
        with patch.object(
            SessionStorage, "_get_config_directory", return_value=config_dir
        ):
            storage = SessionStorage("new_app")
            assert config_dir.exists()

    @patch("os.name", "posix")
    @patch("os.chmod")
    def test_ensure_config_directory_sets_permissions_unix(self, mock_chmod, temp_dir):
        """Test that permissions are set on Unix systems."""
        config_dir = temp_dir / "secure_app"
        with patch.object(
            SessionStorage, "_get_config_directory", return_value=config_dir
        ):
            storage = SessionStorage("secure_app")
            mock_chmod.assert_called_with(config_dir, stat.S_IRWXU)

    @patch("os.name", "nt")
    @patch("os.chmod")
    def test_ensure_config_directory_no_permissions_windows(self, mock_chmod, temp_dir):
        """Test that permissions are not set on Windows."""
        config_dir = temp_dir / "windows_app"
        with patch.object(
            SessionStorage, "_get_config_directory", return_value=config_dir
        ):
            storage = SessionStorage("windows_app")
            mock_chmod.assert_not_called()

    def test_ensure_config_directory_exception_handling(self, temp_dir):
        """Test exception handling in config directory creation."""
        config_dir = temp_dir / "error_app"

        with patch.object(
            SessionStorage, "_get_config_directory", return_value=config_dir
        ):
            with patch.object(
                Path, "mkdir", side_effect=PermissionError("Access denied")
            ):
                with patch("builtins.print") as mock_print:
                    storage = SessionStorage("error_app")
                    mock_print.assert_called_with(
                        "Warning: Could not create config directory: Access denied"
                    )


class TestSaveSession:
    """Test save_session method."""

    def test_save_session_success(self, session_storage, sample_session_data):
        """Test successful session saving."""
        result = session_storage.save_session(sample_session_data)

        assert result is True
        assert session_storage._session_file.exists()

        # Verify file contents
        with open(session_storage._session_file, "r") as f:
            stored_data = json.load(f)

        assert "session" in stored_data
        assert "stored_at" in stored_data
        assert stored_data["session"] == sample_session_data

    @patch("os.name", "posix")
    @patch("os.chmod")
    def test_save_session_sets_file_permissions_unix(
        self, mock_chmod, session_storage, sample_session_data
    ):
        """Test that file permissions are set on Unix systems."""
        session_storage.save_session(sample_session_data)

        # Should be called for both directory and file
        expected_calls = [
            unittest.mock.call(session_storage._config_dir, stat.S_IRWXU),
            unittest.mock.call(
                session_storage._session_file.with_suffix(".tmp"),
                stat.S_IRUSR | stat.S_IWUSR,
            ),
        ]
        # Check that chmod was called for the temp file with correct permissions
        mock_chmod.assert_any_call(
            session_storage._session_file.with_suffix(".tmp"),
            stat.S_IRUSR | stat.S_IWUSR,
        )

    @patch("os.name", "nt")
    @patch("os.chmod")
    def test_save_session_no_file_permissions_windows(
        self, mock_chmod, session_storage, sample_session_data
    ):
        """Test that file permissions are not set on Windows."""
        session_storage.save_session(sample_session_data)

        # chmod should only be called once for directory creation, not for file permissions
        assert mock_chmod.call_count <= 1

    def test_save_session_atomic_operation(self, session_storage, sample_session_data):
        """Test that save operation is atomic using temporary file."""
        # Create existing session file
        session_storage._session_file.write_text('{"old": "data"}')

        with patch("pathlib.Path.rename") as mock_rename:
            mock_rename.side_effect = Exception("Rename failed")

            with patch("builtins.print") as mock_print:
                result = session_storage.save_session(sample_session_data)

            assert result is False
            # Original file should still exist with old data
            assert session_storage._session_file.exists()
            mock_print.assert_called_with(
                "Warning: Could not save session: Rename failed"
            )

    def test_save_session_cleanup_on_failure(
        self, session_storage, sample_session_data
    ):
        """Test that temporary file is cleaned up on failure."""
        with patch("builtins.open", side_effect=PermissionError("Write failed")):
            with patch("builtins.print") as mock_print:
                result = session_storage.save_session(sample_session_data)

        assert result is False
        # Temp file should not exist
        temp_file = session_storage._session_file.with_suffix(".tmp")
        assert not temp_file.exists()
        mock_print.assert_called_with("Warning: Could not save session: Write failed")

    def test_save_session_cleanup_exception_handling(
        self, session_storage, sample_session_data
    ):
        """Test exception handling during temp file cleanup."""
        with patch("builtins.open", side_effect=PermissionError("Write failed")):
            with patch.object(Path, "exists", return_value=True):
                with patch.object(
                    Path, "unlink", side_effect=PermissionError("Cannot delete")
                ):
                    with patch("builtins.print") as mock_print:
                        result = session_storage.save_session(sample_session_data)

        assert result is False
        # Should not raise exception even if cleanup fails


class TestLoadSession:
    """Test load_session method."""

    def test_load_session_success(self, session_storage, sample_session_data):
        """Test successful session loading."""
        # Save session first
        session_storage.save_session(sample_session_data)

        # Load session
        loaded_data = session_storage.load_session()

        assert loaded_data == sample_session_data

    def test_load_session_file_not_exists(self, session_storage):
        """Test loading when session file doesn't exist."""
        result = session_storage.load_session()
        assert result is None

    @patch("os.name", "posix")
    def test_load_session_insecure_permissions(
        self, session_storage, sample_session_data
    ):
        """Test loading with insecure file permissions."""
        # Save session first
        session_storage.save_session(sample_session_data)

        # Mock file stat to return insecure permissions
        with patch.object(Path, "stat") as mock_stat:
            mock_file_stat = Mock()
            mock_file_stat.st_mode = 0o644  # Group and others can read
            mock_stat.return_value = mock_file_stat

            with patch.object(session_storage, "_clear_session") as mock_clear:
                with patch("builtins.print") as mock_print:
                    result = session_storage.load_session()

            assert result is None
            mock_clear.assert_called_once()
            mock_print.assert_called_with(
                "Warning: Session file has insecure permissions, removing it"
            )

    @patch("os.name", "nt")
    def test_load_session_skip_permissions_check_windows(
        self, session_storage, sample_session_data
    ):
        """Test that permission checks are skipped on Windows."""
        # Save session first
        session_storage.save_session(sample_session_data)

        # Load session - should work regardless of permissions on Windows
        result = session_storage.load_session()
        assert result == sample_session_data

    def test_load_session_invalid_json(self, session_storage):
        """Test loading with invalid JSON."""
        # Write invalid JSON
        session_storage._session_file.write_text('{"invalid": json}')

        with patch.object(session_storage, "_clear_session") as mock_clear:
            with patch("builtins.print") as mock_print:
                result = session_storage.load_session()

        assert result is None
        mock_clear.assert_called_once()

    def test_load_session_missing_session_key(self, session_storage):
        """Test loading with missing session key."""
        # Write data without session key
        storage_data = {"stored_at": time.time()}
        session_storage._session_file.write_text(json.dumps(storage_data))

        result = session_storage.load_session()
        assert result is None

    def test_load_session_invalid_structure(self, session_storage):
        """Test loading with invalid session structure."""
        # Write session data missing required fields
        storage_data = {
            "session": {"access_token": "test"},  # Missing refresh_token
            "stored_at": time.time(),
        }
        session_storage._session_file.write_text(json.dumps(storage_data))
        # Set secure permissions to avoid permission check failure
        if os.name != "nt":
            session_storage._session_file.chmod(0o600)

        with patch.object(session_storage, "_clear_session") as mock_clear:
            with patch("builtins.print") as mock_print:
                result = session_storage.load_session()

        assert result is None
        mock_clear.assert_called_once()
        mock_print.assert_called_with(
            "Warning: Invalid session data structure, clearing session"
        )

    def test_load_session_expired(self, session_storage, expired_session_data):
        """Test loading expired session."""
        # Save expired session
        session_storage.save_session(expired_session_data)

        with patch.object(session_storage, "_clear_session") as mock_clear:
            with patch("builtins.print") as mock_print:
                result = session_storage.load_session()

        assert result is None
        mock_clear.assert_called_once()
        mock_print.assert_called_with("Session has expired, clearing stored session")

    def test_load_session_file_not_found_exception(self, session_storage):
        """Test handling of FileNotFoundError."""
        # The file should exist first for open() to be called, then the FileNotFoundError will be caught
        session_storage._session_file.touch()  # Create the file
        if os.name != "nt":
            session_storage._session_file.chmod(0o600)  # Set secure permissions

        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with patch.object(session_storage, "_clear_session") as mock_clear:
                with patch("builtins.print") as mock_print:
                    result = session_storage.load_session()

        assert result is None
        mock_clear.assert_called_once()

    def test_load_session_unexpected_exception(self, session_storage):
        """Test handling of unexpected exceptions."""
        session_storage._session_file.write_text(
            '{"session": {"access_token": "test", "refresh_token": "test"}}'
        )
        # Set secure permissions to avoid permission check failure
        if os.name != "nt":
            session_storage._session_file.chmod(0o600)

        with patch("builtins.open", side_effect=PermissionError("Unexpected error")):
            with patch("builtins.print") as mock_print:
                result = session_storage.load_session()

        assert result is None
        mock_print.assert_called_with(
            "Warning: Unexpected error loading session: Unexpected error"
        )


class TestIsSessionExpired:
    """Test _is_session_expired method."""

    def test_is_session_expired_no_expires_at(self, session_storage):
        """Test expiry check with no expires_at field."""
        session_data = {"access_token": "test"}
        result = session_storage._is_session_expired(session_data)
        assert result is True

    def test_is_session_expired_valid_session(self, session_storage):
        """Test expiry check with valid (non-expired) session."""
        session_data = {"expires_at": time.time() + 3600}  # 1 hour from now
        result = session_storage._is_session_expired(session_data)
        assert result is False

    def test_is_session_expired_expired_session(self, session_storage):
        """Test expiry check with expired session."""
        session_data = {"expires_at": time.time() - 3600}  # 1 hour ago
        result = session_storage._is_session_expired(session_data)
        assert result is True

    def test_is_session_expired_with_buffer(self, session_storage):
        """Test expiry check with 5-minute buffer."""
        # Session expires in 3 minutes - should be considered expired due to 5-minute buffer
        session_data = {"expires_at": time.time() + 180}
        result = session_storage._is_session_expired(session_data)
        assert result is True

    def test_is_session_expired_exception_handling(self, session_storage):
        """Test expiry check exception handling."""
        session_data = {"expires_at": "invalid_timestamp"}
        result = session_storage._is_session_expired(session_data)
        assert result is True


class TestClearSession:
    """Test session clearing methods."""

    def test_clear_session_public_method(self, session_storage, sample_session_data):
        """Test public clear_session method."""
        # Save session first
        session_storage.save_session(sample_session_data)
        assert session_storage._session_file.exists()

        # Clear session
        result = session_storage.clear_session()

        assert result is True
        assert not session_storage._session_file.exists()

    def test_clear_session_private_method(self, session_storage, sample_session_data):
        """Test private _clear_session method."""
        # Save session first
        session_storage.save_session(sample_session_data)
        assert session_storage._session_file.exists()

        # Clear session
        result = session_storage._clear_session()

        assert result is True
        assert not session_storage._session_file.exists()

    def test_clear_session_file_not_exists(self, session_storage):
        """Test clearing when file doesn't exist."""
        result = session_storage._clear_session()
        assert result is True

    def test_clear_session_exception_handling(
        self, session_storage, sample_session_data
    ):
        """Test clear_session exception handling."""
        # Save session first
        session_storage.save_session(sample_session_data)

        with patch.object(Path, "unlink", side_effect=PermissionError("Cannot delete")):
            with patch("builtins.print") as mock_print:
                result = session_storage._clear_session()

        assert result is False
        mock_print.assert_called_with(
            "Warning: Could not clear session file: Cannot delete"
        )


class TestHasStoredSession:
    """Test has_stored_session method."""

    def test_has_stored_session_true(self, session_storage, sample_session_data):
        """Test has_stored_session when file exists."""
        session_storage.save_session(sample_session_data)
        result = session_storage.has_stored_session()
        assert result is True

    def test_has_stored_session_false(self, session_storage):
        """Test has_stored_session when file doesn't exist."""
        result = session_storage.has_stored_session()
        assert result is False


class TestGetSessionInfo:
    """Test get_session_info method."""

    def test_get_session_info_success(self, session_storage, sample_session_data):
        """Test successful session info retrieval."""
        session_storage.save_session(sample_session_data)

        info = session_storage.get_session_info()

        assert info is not None
        assert "stored_at" in info
        assert "expires_at" in info
        assert "is_expired" in info
        assert "file_path" in info
        assert info["expires_at"] == sample_session_data["expires_at"]
        assert info["is_expired"] is False
        assert str(session_storage._session_file) == info["file_path"]

    def test_get_session_info_file_not_exists(self, session_storage):
        """Test get_session_info when file doesn't exist."""
        info = session_storage.get_session_info()
        assert info is None

    def test_get_session_info_expired_session(
        self, session_storage, expired_session_data
    ):
        """Test get_session_info with expired session."""
        session_storage.save_session(expired_session_data)

        info = session_storage.get_session_info()

        assert info is not None
        assert info["is_expired"] is True

    def test_get_session_info_no_session_data(self, session_storage):
        """Test get_session_info with storage data but no session."""
        storage_data = {"stored_at": time.time()}
        session_storage._session_file.write_text(json.dumps(storage_data))

        info = session_storage.get_session_info()

        assert info is not None
        assert info["is_expired"] is True

    def test_get_session_info_exception_handling(self, session_storage):
        """Test get_session_info exception handling."""
        # Write invalid JSON
        session_storage._session_file.write_text('{"invalid": json}')

        info = session_storage.get_session_info()
        assert info is None


@pytest.mark.storage
class TestSessionStorageIntegration:
    """Integration tests for SessionStorage."""

    def test_full_session_lifecycle(self, session_storage, sample_session_data):
        """Test complete session storage lifecycle."""
        # Initially no session
        assert not session_storage.has_stored_session()
        assert session_storage.load_session() is None
        assert session_storage.get_session_info() is None

        # Save session
        assert session_storage.save_session(sample_session_data) is True
        assert session_storage.has_stored_session() is True

        # Load session
        loaded_data = session_storage.load_session()
        assert loaded_data == sample_session_data

        # Get session info
        info = session_storage.get_session_info()
        assert info is not None
        assert not info["is_expired"]

        # Clear session
        assert session_storage.clear_session() is True
        assert not session_storage.has_stored_session()
        assert session_storage.load_session() is None

    def test_session_data_integrity(self, session_storage):
        """Test that session data maintains integrity through save/load cycle."""
        complex_session_data = {
            "access_token": "complex_token_123",
            "refresh_token": "refresh_token_456",
            "expires_at": int(time.time()) + 3600,  # 1 hour from now
            "user_data": {
                "id": "user123",
                "email": "test@example.com",
                "metadata": {"custom_field": "custom_value"},
            },
            "provider_tokens": ["token1", "token2"],
        }

        # Save and load
        session_storage.save_session(complex_session_data)
        loaded_data = session_storage.load_session()

        # Verify exact match
        assert loaded_data == complex_session_data

    def test_concurrent_access_simulation(self, session_storage, sample_session_data):
        """Test behavior under simulated concurrent access."""
        # Save session
        session_storage.save_session(sample_session_data)

        # Simulate concurrent read/write by manually manipulating file
        # This tests the atomic write behavior
        original_content = session_storage._session_file.read_text()

        # Attempt to save while simulating interruption
        with patch.object(Path, "rename", side_effect=[None]) as mock_rename:
            session_storage.save_session({"new": "data"})

        # Original session should still be loadable
        loaded_data = session_storage.load_session()
        assert (
            "new" in str(loaded_data) or loaded_data == sample_session_data
        )  # Either new data succeeded or old data preserved


# Import required for the mock patch
import unittest.mock
