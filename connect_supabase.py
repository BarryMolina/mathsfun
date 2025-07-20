import dotenv
import os
import webbrowser
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from supabase import create_client, Client
from typing import Optional, Dict, Any

dotenv.load_dotenv()

url = os.getenv("SUPABASE_URL") or ""
key = os.getenv("SUPABASE_KEY") or ""

print(f"Supabase URL: {url}")
print(f"Supabase Key: {key[:20]}...")


class OAuthServer(HTTPServer):
    """Custom HTTP server that stores OAuth callback results"""

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.auth_result: Optional[Dict[str, Any]] = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""

    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        print(f"Received callback request: {self.path}")

        # Type assertion to access our custom server attribute
        server: OAuthServer = self.server  # type: ignore

        # Ignore favicon and other non-OAuth requests
        if self.path == "/favicon.ico" or self.path.startswith("/favicon"):
            print("Ignoring favicon request")
            self.send_response(404)
            self.end_headers()
            return

        # Don't overwrite existing successful results
        if server.auth_result and server.auth_result.get("success"):
            print("Already have successful auth result, ignoring additional requests")
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
        print(f"Query parameters: {query_params}")

        # Initialize auth_result as empty dict
        result = {}

        # Check for OAuth callback parameters
        if "code" in query_params:
            print("✅ Found authorization code in callback")
            # Success - we got an authorization code
            result["success"] = True
            result["code"] = query_params["code"][0]
            if "state" in query_params:
                result["state"] = query_params["state"][0]

            # Set the result atomically
            server.auth_result = result
            print(f"Server auth_result set to: {server.auth_result}")

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
            print("❌ Found error in callback")
            # Error during OAuth flow
            result["success"] = False
            result["error"] = query_params["error"][0]
            result["error_description"] = query_params.get(
                "error_description", ["Unknown error"]
            )[0]

            # Set the result atomically
            server.auth_result = result
            print(f"Server auth_result set to: {server.auth_result}")

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
            print("⚠️  Unknown callback - no code or error found")
            # Unknown callback - but still set a result to unblock waiting
            result["success"] = False
            result["error"] = "unknown_callback"
            result["error_description"] = (
                "No authorization code or error found in callback"
            )

            # Set the result atomically
            server.auth_result = result
            print(f"Server auth_result set to: {server.auth_result}")

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

    def log_message(self, format, *args):
        """Override to suppress HTTP server logs"""
        pass


def start_oauth_server(port=8080):
    """Start local HTTP server for OAuth callback"""
    server = OAuthServer(("localhost", port), OAuthCallbackHandler)

    # Use an event to signal when server is ready
    server_ready = threading.Event()

    def server_runner():
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


def perform_oauth_flow():
    """Perform the complete OAuth flow for Google authentication"""

    # Start local server for callback
    print("Starting local server for OAuth callback...")
    server = start_oauth_server(8080)
    redirect_uri = "http://localhost:8080"

    # Test server is ready
    print(f"Server started, listening on {redirect_uri}")
    print(f"Server auth_result initialized as: {server.auth_result}")

    try:
        # Create Supabase client
        supabase: Client = create_client(url, key)

        # Initiate OAuth flow
        print("Initiating Google OAuth flow...")
        res = supabase.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": redirect_uri}}
        )

        if not res.url:
            print("Error: Failed to get OAuth URL from Supabase")
            return None

        print(f"Opening browser for authentication: {res.url}")

        # Open OAuth URL in user's default browser
        webbrowser.open(res.url)

        print("Waiting for authentication...")
        print("Please complete the authentication in your browser.")
        print("This window will close automatically after authentication.")

        # Wait for callback (with timeout)
        timeout = 300  # 5 minutes
        start_time = time.time()

        print("Starting callback wait loop...")
        check_count = 0

        while server.auth_result is None:
            check_count += 1
            elapsed = time.time() - start_time

            if check_count % 10 == 0:  # Log every 5 seconds
                print(f"Still waiting for callback... ({elapsed:.1f}s elapsed)")

            if elapsed > timeout:
                print("Timeout: No response received within 5 minutes")
                return None
            time.sleep(0.5)

        print(f"✅ Callback received after {time.time() - start_time:.1f}s")
        print(f"Final auth_result: {server.auth_result}")

        # Process the result
        if server.auth_result["success"]:
            print("✅ Authentication successful!")
            print(f"Authorization code received: {server.auth_result['code'][:20]}...")
            return server.auth_result
        else:
            print("❌ Authentication failed!")
            print(f"Error: {server.auth_result['error']}")
            print(f"Description: {server.auth_result['error_description']}")
            return None

    except Exception as e:
        print(f"Error during OAuth flow: {e}")
        return None
    finally:
        # Clean up server
        server.shutdown()
        print("Local server stopped.")


if __name__ == "__main__":
    result = perform_oauth_flow()
    if result:
        print("\n🎉 OAuth flow completed successfully!")
        print("You can now use this authentication in your application.")
    else:
        print("\n💥 OAuth flow failed. Please try again.")
