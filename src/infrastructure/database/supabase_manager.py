import dotenv
import os
import webbrowser
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from supabase import create_client, Client, ClientOptions
from typing import Optional, Dict, Any
from ..storage.session_storage import SessionStorage
from .environment_config import EnvironmentConfig, ValidationLevel


class OAuthServer(HTTPServer):
    """Custom HTTP server that stores OAuth callback results"""

    def __init__(
        self, server_address: tuple[str, int], RequestHandlerClass: type
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.auth_result: Optional[Dict[str, Any]] = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""

    def do_GET(self) -> None:
        """Handle GET request from OAuth redirect"""

        # Type assertion to access our custom server attribute
        server: OAuthServer = self.server  # type: ignore

        # Ignore favicon and other non-OAuth requests
        if self.path == "/favicon.ico" or self.path.startswith("/favicon"):
            self.send_response(404)
            self.end_headers()
            return

        # Don't overwrite existing successful results
        if server.auth_result and server.auth_result.get("success"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><p>Authentication already completed.</p></body></html>"
            )
            return

        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Initialize auth_result as empty dict
        result: Dict[str, Any] = {}

        # Check for OAuth callback parameters
        if "code" in query_params:
            # Success - we got an authorization code
            result["success"] = True
            result["code"] = query_params["code"][0]
            if "state" in query_params:
                result["state"] = query_params["state"][0]

            # Set the result atomically
            server.auth_result = result

            # Send success response to browser
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can now close this browser window and return to your CLI application.</p>
                    <script>window.close();</script>
                </body>
                </html>
            """
            )

        elif "error" in query_params:
            # Error during OAuth flow
            result["success"] = False
            result["error"] = query_params["error"][0]
            result["error_description"] = query_params.get(
                "error_description", ["Unknown error"]
            )[0]

            # Set the result atomically
            server.auth_result = result

            # Send error response to browser
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {result['error']}</p>
                    <p>Description: {result['error_description']}</p>
                    <p>You can close this browser window and return to your CLI application.</p>
                </body>
                </html>
            """.encode()
            )
        else:
            # Unknown callback - but still set a result to unblock waiting
            result["success"] = False
            result["error"] = "unknown_callback"
            result["error_description"] = (
                "No authorization code or error found in callback"
            )

            # Set the result atomically
            server.auth_result = result

            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                <body>
                    <h1>Invalid Callback</h1>
                    <p>This doesn't appear to be a valid OAuth callback.</p>
                </body>
                </html>
            """
            )

    def log_message(self, format: str, *args: Any) -> None:
        """Override to suppress HTTP server logs"""
        return


def start_oauth_server(port: int = 8080) -> OAuthServer:
    """Start local HTTP server for OAuth callback"""
    server = OAuthServer(("localhost", port), OAuthCallbackHandler)

    # Use an event to signal when server is ready
    server_ready = threading.Event()

    def server_runner() -> None:
        server_ready.set()  # Signal that server is ready
        server.serve_forever()

    # Start server in a separate thread
    server_thread = threading.Thread(target=server_runner)
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to be ready before returning
    server_ready.wait(timeout=5)  # Wait up to 5 seconds

    # Small additional delay to ensure socket is bound
    time.sleep(0.1)

    return server


class SupabaseManager:
    """Manages Supabase authentication and client access"""

    def __init__(self, use_local: bool = False) -> None:
        # Use configuration object for environment settings
        self.config = EnvironmentConfig.from_environment(use_local=use_local)

        # Validate configuration and handle validation failures based on severity
        is_valid, message, level = self.config.validate()
        if not is_valid:
            if level == ValidationLevel.CRITICAL:
                # Critical errors prevent application startup
                raise ValueError(f"Critical configuration error: {message}")
            elif level == ValidationLevel.WARNING:
                # Warnings allow continuation with graceful degradation
                print(f"⚠️  Configuration warning: {message}")
            # INFO level messages are handled in successful validation path

        # Log environment information for development visibility
        print(self.config.get_console_message())

        self._client: Client = create_client(self.config.url, self.config.anon_key)
        self._authenticated = False
        self._lock = threading.Lock()
        self._session_data: Optional[Dict[str, Any]] = None
        self._session_storage = SessionStorage()

    def sign_in_with_google(self) -> Dict[str, Any]:
        """Authenticate user with Google OAuth and store client"""

        # In local development, warn about OAuth limitations
        if self.config.is_local:
            print(
                "⚠️  Note: OAuth may not work in local development without proper provider configuration"
            )
            print(
                "   For testing, consider using email/password auth or skip authentication features"
            )

        server = start_oauth_server(8080)
        redirect_uri = "http://localhost:8080"

        # Custom storage to handle PKCE code verifier
        class PKCEStorage:
            def __init__(self) -> None:
                self.storage: Dict[str, str] = {}

            def get_item(self, key: str) -> Optional[str]:
                return self.storage.get(key)

            def set_item(self, key: str, value: str) -> None:
                self.storage[key] = value

            def remove_item(self, key: str) -> None:
                self.storage.pop(key, None)

        try:
            # Create storage instance and configure existing client for PKCE
            storage = PKCEStorage()

            # Reconfigure the existing client for PKCE flow
            supabase: Client = create_client(
                self.config.url,
                self.config.anon_key,
                options=ClientOptions(
                    flow_type="pkce", storage=storage  # type: ignore
                ),
            )

            res = supabase.auth.sign_in_with_oauth(
                {"provider": "google", "options": {"redirect_to": redirect_uri}}
            )

            if not res.url:
                return {
                    "success": False,
                    "error": "Failed to get OAuth URL from Supabase",
                }

            print("✅ Opening browser for Google authentication...")
            print("\\nPlease complete the authentication in your browser.")
            print("This window will close automatically after authentication.")

            webbrowser.open(res.url)

            timeout = 300  # 5 minutes
            start_time = time.time()

            while server.auth_result is None:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    return {"success": False, "error": "Authentication timeout"}
                time.sleep(0.5)

            # If we got an authorization code, exchange it for a session
            if (
                server.auth_result
                and server.auth_result.get("success")
                and server.auth_result.get("code")
            ):
                try:
                    # Get the code verifier from storage
                    code_verifier = storage.get_item(
                        "supabase.auth.token-code-verifier"
                    )

                    if not code_verifier:
                        return {
                            "success": False,
                            "error": "Could not find code verifier for PKCE exchange",
                        }

                    # Exchange the authorization code for a session
                    session_response = supabase.auth.exchange_code_for_session(
                        {
                            "auth_code": server.auth_result["code"],
                            "code_verifier": code_verifier,
                            "redirect_to": redirect_uri,
                        }
                    )

                    if session_response.session:
                        # Get user information
                        user = session_response.user
                        session = session_response.session

                        # Extract user data safely
                        user_data = {
                            "id": user.id if user else None,
                            "email": user.email if user else None,
                            "name": (
                                user.user_metadata.get("full_name")
                                if user and user.user_metadata
                                else (
                                    user.user_metadata.get("name", "Unknown")
                                    if user and user.user_metadata
                                    else "Unknown"
                                )
                            ),
                            "avatar_url": (
                                user.user_metadata.get("avatar_url")
                                if user and user.user_metadata
                                else None
                            ),
                            "provider": (
                                user.app_metadata.get("provider", "google")
                                if user and user.app_metadata
                                else "google"
                            ),
                            "last_sign_in": user.last_sign_in_at if user else None,
                        }

                        # Extract provider tokens if available
                        provider_token = None
                        provider_refresh_token = None
                        if hasattr(session, "provider_token"):
                            provider_token = session.provider_token
                        if hasattr(session, "provider_refresh_token"):
                            provider_refresh_token = session.provider_refresh_token

                        session_data = {
                            "access_token": session.access_token,
                            "refresh_token": session.refresh_token,
                            "expires_at": session.expires_at,
                            "provider_token": provider_token,
                            "provider_refresh_token": provider_refresh_token,
                        }

                        # Store session data and mark as authenticated
                        with self._lock:
                            self._client = supabase  # Update with authenticated client
                            self._authenticated = True
                            self._session_data = session_data

                        # Save session to persistent storage
                        self.save_session()

                        return {
                            "success": True,
                            "user": user_data,
                            "session": session_data,
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Failed to create session from code",
                        }

                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to exchange code for session: {str(e)}",
                    }
            else:
                return server.auth_result or {
                    "success": False,
                    "error": "No auth result received",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            server.shutdown()

    def sign_up_with_email_password(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user with email and password"""
        try:
            response = self._client.auth.sign_up({"email": email, "password": password})

            if response.user and response.session:
                user = response.user
                session = response.session

                # Extract user data for email/password auth
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "name": (
                        user.email.split("@")[0] if user.email else "User"
                    ),  # Use email prefix as default name
                    "avatar_url": None,  # Not available for email auth
                    "provider": "email",
                    "last_sign_in": user.last_sign_in_at,
                }

                session_data = {
                    "access_token": session.access_token,
                    "refresh_token": session.refresh_token,
                    "expires_at": session.expires_at,
                    "provider_token": None,  # Not available for email auth
                    "provider_refresh_token": None,  # Not available for email auth
                }

                # Store session data and mark as authenticated
                with self._lock:
                    self._authenticated = True
                    self._session_data = session_data

                # Save session to persistent storage
                self.save_session()

                return {
                    "success": True,
                    "user": user_data,
                    "session": session_data,
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create user account",
                }

        except Exception as e:
            error_msg = str(e)
            # Provide user-friendly error messages
            if "email" in error_msg.lower() and "already" in error_msg.lower():
                return {
                    "success": False,
                    "error": "An account with this email already exists. Please try signing in instead.",
                }
            elif "password" in error_msg.lower():
                return {
                    "success": False,
                    "error": "Password does not meet requirements. Please use at least 6 characters.",
                }
            else:
                return {
                    "success": False,
                    "error": "Unable to create account. Please try again.",
                }

    def sign_in_with_email_password(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user with email and password"""
        try:
            response = self._client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user and response.session:
                user = response.user
                session = response.session

                # Extract user data for email/password auth
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "name": (
                        user.email.split("@")[0] if user.email else "User"
                    ),  # Use email prefix as default name
                    "avatar_url": None,  # Not available for email auth
                    "provider": "email",
                    "last_sign_in": user.last_sign_in_at,
                }

                session_data = {
                    "access_token": session.access_token,
                    "refresh_token": session.refresh_token,
                    "expires_at": session.expires_at,
                    "provider_token": None,  # Not available for email auth
                    "provider_refresh_token": None,  # Not available for email auth
                }

                # Store session data and mark as authenticated
                with self._lock:
                    self._authenticated = True
                    self._session_data = session_data

                # Save session to persistent storage
                self.save_session()

                return {
                    "success": True,
                    "user": user_data,
                    "session": session_data,
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid email or password",
                }

        except Exception as e:
            error_msg = str(e)
            # Provide user-friendly error messages without revealing user existence
            if "invalid" in error_msg.lower() or "not found" in error_msg.lower():
                return {
                    "success": False,
                    "error": "Invalid email or password",
                }
            else:
                return {
                    "success": False,
                    "error": "Unable to sign in. Please try again.",
                }

    def get_client(self) -> Client:
        """Get the Supabase client (always available)"""
        with self._lock:
            return self._client

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated"""
        with self._lock:
            return self._authenticated

    def sign_out(self) -> None:
        """Sign out and clear authentication state"""
        with self._lock:
            self._authenticated = False
            self._session_data = None
            # Clear stored session
            self._session_storage.clear_session()
            # Recreate client to clear session
            self._client = create_client(self.config.url, self.config.anon_key)

    def get_session_data(self) -> Optional[Dict[str, Any]]:
        """Get current session data for persistence"""
        with self._lock:
            return self._session_data

    def restore_session(self, session_data: Dict[str, Any]) -> bool:
        """Restore authentication state from stored session data"""
        try:
            if not session_data.get("access_token") or not session_data.get(
                "refresh_token"
            ):
                return False

            # Try to set session using the auth API on existing client
            try:
                self._client.auth.set_session(
                    access_token=session_data["access_token"],
                    refresh_token=session_data["refresh_token"],
                )
            except Exception:
                # If set_session doesn't work, try refresh
                refresh_result = self._client.auth.refresh_session(
                    session_data["refresh_token"]
                )
                if not refresh_result.session:
                    return False

            # Store session data and mark as authenticated
            with self._lock:
                self._authenticated = True
                self._session_data = session_data

            return True

        except Exception:
            return False

    def load_persisted_session(self) -> bool:
        """Attempt to restore authentication from persisted session"""
        try:
            session_data = self._session_storage.load_session()
            if not session_data:
                return False

            # Try to restore the session
            if self.restore_session(session_data):
                return True
            else:
                # If restore failed, clear the invalid session
                self._session_storage.clear_session()
                return False

        except Exception as e:
            print(f"Warning: Error loading persisted session: {e}")
            return False

    def save_session(self) -> bool:
        """Save current session to persistent storage"""
        try:
            with self._lock:
                if not self._authenticated or not self._session_data:
                    return False

                return self._session_storage.save_session(self._session_data)

        except Exception as e:
            print(f"Warning: Error saving session: {e}")
            return False


def validate_environment(use_local: bool = False) -> tuple[bool, str]:
    """Validate that required environment variables are set"""
    config = EnvironmentConfig.from_environment(use_local=use_local)
    is_valid, message, level = config.validate()
    return is_valid, message


def create_supabase_manager(use_local: bool = False) -> SupabaseManager:
    """Create a SupabaseManager instance with the specified configuration.

    Args:
        use_local: If True, configure for local development (.env.local).
                  If False, configure for production (.env).

    Returns:
        Configured SupabaseManager instance
    """
    return SupabaseManager(use_local=use_local)


# TODO: Singleton removed - all code should use create_supabase_manager()
# supabase_manager = SupabaseManager()
