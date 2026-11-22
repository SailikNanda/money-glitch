#!/usr/bin/env python3
"""Google Cloud Console & YouTube OAuth Credential Validator and Helper.
Used by Antigravity AI to verify and guide the setup of data/client_secrets.json.
"""

import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CLIENT_SECRETS_FILE = ROOT_DIR / "data" / "client_secrets.json"
TOKEN_FILE = ROOT_DIR / "data" / "youtube_token.json"

CONSOLE_URLS = {
    "project_create": "https://console.cloud.google.com/projectcreate",
    "enable_youtube_api": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
    "oauth_consent": "https://console.cloud.google.com/apis/credentials/consent",
    "create_credentials": "https://console.cloud.google.com/apis/credentials/oauthclient"
}

def check_status():
    print("=" * 60)
    print("   ANTIGRAVITY GOOGLE OAUTH & YOUTUBE CREDENTIAL STATUS")
    print("=" * 60)
    
    secrets_ok = CLIENT_SECRETS_FILE.exists()
    print(f"1. client_secrets.json: {'[FOUND]' if secrets_ok else '[MISSING]'}")
    if secrets_ok:
        try:
            with open(CLIENT_SECRETS_FILE, "r") as f:
                data = json.load(f)
                client_id = data.get("installed", {}).get("client_id") or data.get("web", {}).get("client_id")
                print(f"   -> Client ID: {client_id[:20]}..." if client_id else "   -> Warning: Malformed JSON")
        except Exception as e:
            print(f"   -> Error reading client_secrets: {e}")
    else:
        print(f"   -> Required path: {CLIENT_SECRETS_FILE}")
        print("   -> Antigravity Browser Directive:")
        print(f"      1. Create Project:        {CONSOLE_URLS['project_create']}")
        print(f"      2. Enable YouTube API:    {CONSOLE_URLS['enable_youtube_api']}")
        print(f"      3. Configure Consent:     {CONSOLE_URLS['oauth_consent']}")
        print(f"      4. Create Desktop Client: {CONSOLE_URLS['create_credentials']}")

    token_ok = TOKEN_FILE.exists()
    print(f"\n2. youtube_token.json:  {'[CONNECTED]' if token_ok else '[NOT AUTHENTICATED]'}")
    if token_ok:
        try:
            with open(TOKEN_FILE, "r") as f:
                tdata = json.load(f)
                print(f"   -> Token Expiry: {tdata.get('expiry', 'Active')}")
        except Exception as e:
            print(f"   -> Error reading token: {e}")
    else:
        print("   -> Action: Launch dashboard and click [Connect Channel] once.")

    print("=" * 60)
    return secrets_ok and token_ok

if __name__ == "__main__":
    ready = check_status()
    sys.exit(0 if ready else 1)
