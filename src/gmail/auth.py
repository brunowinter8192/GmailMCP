# INFRASTRUCTURE
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CONFIG_DIR = Path.home() / ".gmail-mcp"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"


# FUNCTIONS

def get_gmail_service():
    """Build and return an authenticated Gmail API service."""
    from googleapiclient.discovery import build

    creds = load_credentials()
    return build("gmail", "v1", credentials=creds)


def load_credentials() -> Credentials:
    """Load OAuth credentials from ~/.gmail-mcp/credentials.json, refresh if expired."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"No credentials at {CREDENTIALS_PATH}. Run: python3 auth/setup.py"
        )

    creds = Credentials.from_authorized_user_info(
        json.loads(CREDENTIALS_PATH.read_text()), SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        CREDENTIALS_PATH.write_text(creds.to_json())

    return creds
