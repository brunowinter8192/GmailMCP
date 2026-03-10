"""One-time OAuth setup for Gmail MCP server.

Usage:
    1. Download OAuth client JSON from Google Cloud Console
    2. mv ~/Downloads/client_secret_xxx.json ~/.gmail-mcp/gcp-oauth.keys.json
    3. python3 auth/setup.py
"""
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CONFIG_DIR = Path.home() / ".gmail-mcp"
OAUTH_KEYS = CONFIG_DIR / "gcp-oauth.keys.json"
CREDENTIALS = CONFIG_DIR / "credentials.json"


def main():
    if not OAUTH_KEYS.exists():
        print(f"ERROR: OAuth keys not found at {OAUTH_KEYS}")
        print()
        print("Setup:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create project -> Enable Gmail API")
        print("  3. APIs & Services -> Credentials -> Create OAuth client ID -> Desktop app")
        print("  4. Download JSON and run:")
        print(f"     mkdir -p {CONFIG_DIR}")
        print(f"     mv ~/Downloads/client_secret_xxx.json {OAUTH_KEYS}")
        print("  5. Re-run this script")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(OAUTH_KEYS), SCOPES)
    creds = flow.run_local_server(port=3000)

    CREDENTIALS.write_text(creds.to_json())
    print(f"Credentials saved to {CREDENTIALS}")
    print("Gmail MCP server is ready to use.")


if __name__ == "__main__":
    main()
