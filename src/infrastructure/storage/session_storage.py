#!/usr/bin/env python3
import json
import os
import stat
import time
from pathlib import Path
from typing import Optional, Dict, Any


class SessionStorage:
    """Handles secure persistence of authentication sessions"""

    def __init__(self, app_name: str = "mathsfun"):
        self.app_name = app_name
        self._config_dir = self._get_config_directory()
        self._session_file = self._config_dir / "session.json"

        # Ensure config directory exists with secure permissions
        self._ensure_config_directory()

    def _get_config_directory(self) -> Path:
        """Get platform-appropriate config directory"""
        if os.name == "nt":  # Windows
            config_base = Path(os.getenv("APPDATA", os.path.expanduser("~")))
        else:  # Unix-like (macOS, Linux)
            config_base = Path(
                os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            )

        return config_base / self.app_name

    def _ensure_config_directory(self) -> None:
        """Create config directory with secure permissions if it doesn't exist"""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)

            # Set secure permissions (owner read/write/execute only)
            if os.name != "nt":  # Unix-like systems
                os.chmod(self._config_dir, stat.S_IRWXU)  # 700

        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")

    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save session data to secure storage"""
        try:
            # Add timestamp for tracking
            storage_data = {"session": session_data, "stored_at": time.time()}

            # Write to temporary file first, then rename (atomic operation)
            temp_file = self._session_file.with_suffix(".tmp")

            with open(temp_file, "w") as f:
                json.dump(storage_data, f, indent=2)

            # Set secure permissions before moving
            if os.name != "nt":  # Unix-like systems
                os.chmod(temp_file, stat.S_IRUSR | stat.S_IWUSR)  # 600

            # Atomic rename
            temp_file.rename(self._session_file)

            return True

        except Exception as e:
            print(f"Warning: Could not save session: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
            return False

    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load and validate session data from storage"""
        try:
            if not self._session_file.exists():
                return None

            # Check file permissions for security
            if os.name != "nt":  # Unix-like systems
                file_stat = self._session_file.stat()
                if (
                    file_stat.st_mode & 0o077
                ):  # Check if group/other have any permissions
                    print("Warning: Session file has insecure permissions, removing it")
                    self._clear_session()
                    return None

            with open(self._session_file, "r") as f:
                storage_data = json.load(f)

            session_data = storage_data.get("session")
            if not session_data:
                return None

            # Validate session data structure
            required_fields = ["access_token", "refresh_token"]
            if not all(field in session_data for field in required_fields):
                print("Warning: Invalid session data structure, clearing session")
                self._clear_session()
                return None

            # Check if tokens are expired
            if self._is_session_expired(session_data):
                print("Session has expired, clearing stored session")
                self._clear_session()
                return None

            return session_data

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Warning: Could not load session data: {e}")
            self._clear_session()
            return None
        except Exception as e:
            print(f"Warning: Unexpected error loading session: {e}")
            return None

    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """Check if session tokens are expired"""
        try:
            expires_at = session_data.get("expires_at")
            if not expires_at:
                return True

            # Add 5 minute buffer to account for clock skew and processing time
            buffer_seconds = 5 * 60
            return expires_at <= (time.time() + buffer_seconds)

        except Exception:
            return True

    def clear_session(self) -> bool:
        """Public method to clear stored session"""
        return self._clear_session()

    def _clear_session(self) -> bool:
        """Clear stored session data"""
        try:
            if self._session_file.exists():
                self._session_file.unlink()
            return True
        except Exception as e:
            print(f"Warning: Could not clear session file: {e}")
            return False

    def has_stored_session(self) -> bool:
        """Check if a session file exists (doesn't validate contents)"""
        return self._session_file.exists()

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get metadata about stored session without loading sensitive data"""
        try:
            if not self._session_file.exists():
                return None

            with open(self._session_file, "r") as f:
                storage_data = json.load(f)

            stored_at = storage_data.get("stored_at")
            session = storage_data.get("session", {})
            expires_at = session.get("expires_at")

            return {
                "stored_at": stored_at,
                "expires_at": expires_at,
                "is_expired": self._is_session_expired(session) if session else True,
                "file_path": str(self._session_file),
            }

        except Exception:
            return None
