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
        # Type assertion to access our custom server attribute
        server: OAuthServer = self.server  # type: ignore
        server.auth_result = {}

        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Check for OAuth callback parameters
        if "code" in query_params:
            # Success - we got an authorization code
            server.auth_result["success"] = True
            server.auth_result["code"] = query_params["code"][0]
            if "state" in query_params:
                server.auth_result["state"] = query_params["state"][0]

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
            server.auth_result["success"] = False
            server.auth_result["error"] = query_params["error"][0]
            server.auth_result["error_description"] = query_params.get(
                "error_description", ["Unknown error"]
            )[0]

            # Send error response to browser
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {server.auth_result['error']}</p>
                    <p>Description: {server.auth_result['error_description']}</p>
                    <p>You can close this browser window and return to your CLI application.</p>
                </body>
                </html>
            """.encode()
            )
        else:
            # Unknown callback
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

    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    return server


def perform_oauth_flow():
    """Perform the complete OAuth flow for Google authentication"""

    # Start local server for callback
    print("Starting local server for OAuth callback...")
    server = start_oauth_server(8080)
    redirect_uri = "http://localhost:8080"

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

        while server.auth_result is None:
            if time.time() - start_time > timeout:
                print("Timeout: No response received within 5 minutes")
                return None
            time.sleep(0.5)

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
