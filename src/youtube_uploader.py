"""YouTube Channel Connection & Upload Engine for Viral Shorts Autopilot.
Uses official Google OAuth 2.0 and YouTube Data API v3.
Features:
- Official Google OAuth flow without storing passwords
- Channel confirmation before upload
- American English title & description generation with source attribution
- Opening frame hook optimization (no custom thumbnail)
- Resumable video upload with verification
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import (
    YOUTUBE_CLIENT_SECRETS_PATH,
    YOUTUBE_TOKEN_PATH,
    DEFAULT_PRIVACY_STATUS
)

logger = logging.getLogger("YouTubeUploader")
logging.basicConfig(level=logging.INFO)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeUploader:
    def __init__(self):
        self.credentials = self._load_credentials()
        self.youtube = None
        if self.credentials:
            try:
                self.youtube = build("youtube", "v3", credentials=self.credentials)
            except Exception as e:
                logger.error(f"Failed to build YouTube client: {e}")

    def _load_credentials(self) -> Optional[Credentials]:
        """Loads existing token or attempts token refresh."""
        creds = None
        if YOUTUBE_TOKEN_PATH.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN_PATH), SCOPES)
            except Exception as e:
                logger.warning(f"Error loading stored token: {e}")

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(YOUTUBE_TOKEN_PATH, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                logger.info("YouTube OAuth token refreshed successfully.")
            except Exception as e:
                logger.error(f"Error refreshing YouTube token: {e}")
                creds = None

        return creds

    def is_connected(self) -> bool:
        return self.credentials is not None and self.credentials.valid

    def authenticate_interactive(self) -> bool:
        """
        Runs local server OAuth flow to connect user's YouTube channel.
        Requires client_secrets.json from Google Cloud Console.
        """
        if not YOUTUBE_CLIENT_SECRETS_PATH.exists():
            logger.error(f"Client secrets file missing: {YOUTUBE_CLIENT_SECRETS_PATH}")
            return False

        flow = InstalledAppFlow.from_client_secrets_file(str(YOUTUBE_CLIENT_SECRETS_PATH), SCOPES)
        try:
            creds = flow.run_local_server(port=8080, open_browser=True)
        except Exception as e:
            logger.warning(f"Port 8080 unavailable ({e}), attempting dynamic port...")
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(YOUTUBE_TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

        self.credentials = creds
        self.youtube = build("youtube", "v3", credentials=creds)
        logger.info("Successfully connected YouTube channel via OAuth 2.0.")
        return True

    def logout(self) -> bool:
        """Disconnects current YouTube channel and clears cached OAuth credentials."""
        self.credentials = None
        self.youtube = None
        if YOUTUBE_TOKEN_PATH.exists():
            try:
                YOUTUBE_TOKEN_PATH.unlink()
                logger.info("Removed stored YouTube OAuth token.")
                return True
            except Exception as e:
                logger.error(f"Error removing token file: {e}")
                return False
        return True

    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Confirm connected channel identity before publishing."""
        if not self.is_connected() or not self.youtube:
            return None
        try:
            res = self.youtube.channels().list(part="snippet,statistics", mine=True).execute()
            items = res.get("items", [])
            if not items:
                return None
            channel = items[0]
            snippet = channel.get("snippet", {})
            stats = channel.get("statistics", {})
            return {
                "channel_id": channel.get("id"),
                "channel_title": snippet.get("title"),
                "custom_url": snippet.get("customUrl"),
                "subscriber_count": stats.get("subscriberCount"),
                "video_count": stats.get("videoCount")
            }
        except Exception as e:
            logger.error(f"Failed to fetch channel info: {e}")
            return None

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy_status: str = DEFAULT_PRIVACY_STATUS,
        scheduled_publish_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads a vertical video as a YouTube Short.
        """
        if not self.is_connected() or not self.youtube:
            return {
                "success": False,
                "error": "YouTube channel not connected. OAuth token required."
            }

        file_path = Path(video_path)
        if not file_path.exists():
            return {"success": False, "error": f"Video file not found: {video_path}"}

        # Ensure #Shorts is included in title or description
        clean_title = title if "#Shorts" in title else f"{title} #Shorts"
        clean_tags = tags or ["Shorts", "GTA6", "Gaming", "Viral"]

        body = {
            "snippet": {
                "title": clean_title[:100],
                "description": description,
                "tags": clean_tags,
                "categoryId": "20",  # Gaming
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        # If scheduled publication time is provided (ISO 8601 UTC)
        if scheduled_publish_time:
            body["status"]["privacyStatus"] = "private"
            body["status"]["publishAt"] = scheduled_publish_time

        media = MediaFileUpload(
            str(file_path),
            mimetype="video/mp4",
            chunksize=1024 * 1024 * 2,  # 2MB chunks
            resumable=True
        )

        logger.info(f"Uploading '{clean_title}' to YouTube...")
        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")

            video_id = response.get("id")
            youtube_url = f"https://www.youtube.com/shorts/{video_id}"
            logger.info(f"Upload complete! Published at: {youtube_url}")

            return {
                "success": True,
                "video_id": video_id,
                "youtube_url": youtube_url,
                "title": clean_title
            }
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return {"success": False, "error": str(e)}
