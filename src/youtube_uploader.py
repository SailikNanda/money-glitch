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
import uuid
import time
import logging
import threading
import wsgiref.simple_server
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
    _RedirectWSGIApp,
    _ExclusiveWSGIServer,
    _WSGIRequestHandler
)
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import (
    YOUTUBE_CLIENT_SECRETS_PATH,
    YOUTUBE_TOKEN_PATH,
    DEFAULT_PRIVACY_STATUS
)

# Allow HTTP for local desktop OAuth loopback redirect
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

logger = logging.getLogger("YouTubeUploader")
logging.basicConfig(level=logging.INFO)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def _atomic_write_token(creds: Credentials):
    temp_path = YOUTUBE_TOKEN_PATH.with_suffix(f".tmp.{uuid.uuid4().hex}")
    try:
        fd = os.open(temp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        temp_path.replace(YOUTUBE_TOKEN_PATH)
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise

class YouTubeUploader:
    def __init__(self):
        self._auth_lock = threading.Lock()
        self._auth_version = int(time.time() * 1000)
        self._login_attempt_id = 0
        self._active_uploads = 0
        self._publication_reservation_id: Optional[str] = None
        self._explicitly_disconnected = False
        self._thread_local = threading.local()
        self._oauth_flow_status: Dict[str, Any] = {
            "attempt_id": 0,
            "status": "idle",
            "message": ""
        }
        self.credentials = self._load_credentials()
        self.youtube = None
        if self.credentials:
            try:
                self.youtube = build("youtube", "v3", credentials=self.credentials)
            except Exception as e:
                logger.error(f"Failed to build YouTube client: {e}")

    def get_auth_version(self) -> int:
        with self._auth_lock:
            return self._auth_version

    def acquire_publication_reservation(self, op_id: Optional[str] = None) -> Optional[str]:
        with self._auth_lock:
            if self._active_uploads > 0 or self._publication_reservation_id is not None:
                return None
            reservation = op_id or str(uuid.uuid4())
            self._publication_reservation_id = reservation
            return reservation

    def release_publication_reservation(self, reservation_id: str):
        with self._auth_lock:
            if self._publication_reservation_id == reservation_id:
                self._publication_reservation_id = None

    def get_oauth_flow_status(self) -> Dict[str, Any]:
        with self._auth_lock:
            return dict(self._oauth_flow_status)

    def _load_credentials(self, expected_version: Optional[int] = None) -> Optional[Credentials]:
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
                with self._auth_lock:
                    if expected_version is not None and self._auth_version != expected_version:
                        logger.info("Discarding refreshed token due to concurrent auth transition.")
                        return None
                    _atomic_write_token(creds)
                logger.info("YouTube OAuth token refreshed successfully.")
            except Exception as e:
                logger.error(f"Error refreshing YouTube token: {e}")
                creds = None

        return creds

    def is_connected(self) -> bool:
        with self._auth_lock:
            if self._explicitly_disconnected:
                return False
            current_version = self._auth_version
            creds = self.credentials
            client = self.youtube

        if creds is None or not creds.valid or client is None:
            if YOUTUBE_TOKEN_PATH.exists():
                try:
                    new_creds = self._load_credentials(expected_version=current_version)
                    if new_creds and new_creds.valid:
                        new_client = build("youtube", "v3", credentials=new_creds)
                        with self._auth_lock:
                            if self._auth_version == current_version and not self._explicitly_disconnected:
                                self.credentials = new_creds
                                self.youtube = new_client
                                return True
                except Exception as e:
                    logger.warning(f"Error rebuilding YouTube client in is_connected: {e}")
        with self._auth_lock:
            return not self._explicitly_disconnected and self.credentials is not None and self.credentials.valid and self.youtube is not None

    def get_authenticated_client(self) -> Tuple[Optional[Any], int]:
        """
        Ensures valid connection and returns a thread-specific authenticated YouTube client
        together with the auth version captured in the same locked snapshot.
        Avoids sharing httplib2.Http transport across concurrent request threads.
        Rechecks auth version and credentials after build() before caching or returning.
        """
        while True:
            if not self.is_connected():
                return None, 0
            with self._auth_lock:
                if self._explicitly_disconnected or not self.credentials:
                    return None, 0
                creds = self.credentials
                ver = self._auth_version

            client = getattr(self._thread_local, "client", None)
            client_ver = getattr(self._thread_local, "version", None)
            client_creds = getattr(self._thread_local, "creds", None)
            if client is not None and client_ver == ver and client_creds is creds:
                return client, ver

            try:
                new_client = build("youtube", "v3", credentials=creds)
            except Exception as e:
                logger.error(f"Failed to build thread-local YouTube client: {e}")
                return None, 0

            with self._auth_lock:
                if self._explicitly_disconnected or not self.credentials:
                    return None, 0
                if self._auth_version == ver and self.credentials is creds:
                    self._thread_local.client = new_client
                    self._thread_local.version = ver
                    self._thread_local.creds = creds
                    return new_client, ver
                # Stale build: auth version or credentials changed while build() was running, loop and retry

    def start_oauth_flow(self, preferred_port: int = 8085) -> str:
        """
        Starts a local HTTP redirect listener and returns the Google OAuth authorization URL.
        Spawns a non-blocking background thread that handles the redirect callback, exchanges token,
        and connects the YouTube channel.
        """
        if not YOUTUBE_CLIENT_SECRETS_PATH.exists():
            raise FileNotFoundError(f"Missing OAuth client secrets at: {YOUTUBE_CLIENT_SECRETS_PATH}")

        flow = InstalledAppFlow.from_client_secrets_file(str(YOUTUBE_CLIENT_SECRETS_PATH), SCOPES)
        wsgi_app = _RedirectWSGIApp("Authorization Received! Finalizing connection in Money Glitch...")

        # Find an available port, avoiding 8080 (which is used by Java/system processes)
        server = None
        for p in [preferred_port, 8089, 8090, 8095, 0]:
            try:
                server = wsgiref.simple_server.make_server(
                    "localhost", p, wsgi_app,
                    server_class=_ExclusiveWSGIServer,
                    handler_class=_WSGIRequestHandler
                )
                break
            except Exception as e:
                logger.debug(f"Port {p} not available: {e}")
                continue

        if not server:
            raise RuntimeError("Failed to bind local OAuth redirect server.")

        with self._auth_lock:
            self._login_attempt_id += 1
            current_attempt = self._login_attempt_id
            self._oauth_flow_status = {
                "attempt_id": current_attempt,
                "status": "pending",
                "message": "Awaiting authorization in Google sign-in tab..."
            }

        actual_port = server.server_port
        flow.redirect_uri = f"http://localhost:{actual_port}/"

        def _worker():
            try:
                logger.info(f"OAuth redirect server listening on http://localhost:{actual_port}/")
                server.timeout = 300  # 5 minutes timeout
                server.handle_request()
                auth_resp = wsgi_app.last_request_uri
                try:
                    flow.fetch_token(authorization_response=auth_resp)
                except Exception:
                    # Fallback if library expects https scheme
                    flow.fetch_token(authorization_response=auth_resp.replace("http://", "https://"))
                creds = flow.credentials
                new_client = build("youtube", "v3", credentials=creds)
                with self._auth_lock:
                    if self._login_attempt_id != current_attempt:
                        logger.warning("Discarding superseded OAuth worker result without updating status.")
                        return

                    if self._active_uploads > 0 or self._publication_reservation_id is not None:
                        logger.warning("Rejecting OAuth login commit because an active upload or publication reservation is in progress.")
                        self._oauth_flow_status = {
                            "attempt_id": current_attempt,
                            "status": "failed",
                            "error_code": "upload_in_progress",
                            "message": "Authorization could not complete because an upload or publication reservation was in progress. Please start a fresh sign-in flow after publication finishes."
                        }
                        return

                    _atomic_write_token(creds)
                    self._auth_version += 1
                    self._explicitly_disconnected = False
                    self.credentials = creds
                    self.youtube = new_client
                    if hasattr(self, "_thread_local"):
                        self._thread_local.client = new_client
                        self._thread_local.version = self._auth_version
                        self._thread_local.creds = creds
                    self._oauth_flow_status = {
                        "attempt_id": current_attempt,
                        "status": "connected",
                        "message": "YouTube channel connected successfully."
                    }
                logger.info("Successfully completed YouTube OAuth flow and updated credentials.")
            except Exception as ex:
                logger.error(f"Error handling OAuth callback: {ex}")
                with self._auth_lock:
                    if self._login_attempt_id == current_attempt:
                        self._oauth_flow_status = {
                            "attempt_id": current_attempt,
                            "status": "failed",
                            "error_code": "callback_error",
                            "message": f"OAuth callback failed: {str(ex)}"
                        }
            finally:
                try:
                    server.server_close()
                except Exception:
                    pass

        try:
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            t = threading.Thread(target=_worker, daemon=True)
            t.start()
        except Exception as e:
            with self._auth_lock:
                if self._login_attempt_id == current_attempt:
                    self._oauth_flow_status = {
                        "attempt_id": current_attempt,
                        "status": "failed",
                        "error_code": "worker_start_error",
                        "message": f"Failed to initialize OAuth authorization: {str(e)}"
                    }
            try:
                server.server_close()
            except Exception:
                pass
            raise
        return auth_url

    def authenticate_interactive(self) -> bool:
        """
        Runs local server OAuth flow to connect user's YouTube channel.
        Requires client_secrets.json from Google Cloud Console.
        """
        if not YOUTUBE_CLIENT_SECRETS_PATH.exists():
            logger.error(f"Client secrets file missing: {YOUTUBE_CLIENT_SECRETS_PATH}")
            return False

        with self._auth_lock:
            self._login_attempt_id += 1
            current_attempt = self._login_attempt_id
            self._oauth_flow_status = {
                "attempt_id": current_attempt,
                "status": "pending",
                "message": "Awaiting interactive OAuth authentication..."
            }

        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(YOUTUBE_CLIENT_SECRETS_PATH), SCOPES)
            try:
                creds = flow.run_local_server(port=8080, open_browser=True)
            except Exception as e:
                logger.warning(f"Port 8080 unavailable ({e}), attempting dynamic port...")
                creds = flow.run_local_server(port=0, open_browser=True)
            new_client = build("youtube", "v3", credentials=creds)
            with self._auth_lock:
                if self._login_attempt_id != current_attempt:
                    logger.warning("Rejecting superseded interactive login commit.")
                    return False
                if self._active_uploads > 0 or self._publication_reservation_id is not None:
                    logger.warning("Rejecting interactive login commit while upload or publication reservation is in progress.")
                    self._oauth_flow_status = {
                        "attempt_id": current_attempt,
                        "status": "failed",
                        "error_code": "upload_in_progress",
                        "message": "Authorization could not complete because an upload or publication reservation was in progress. Please start a fresh sign-in flow after publication finishes."
                    }
                    return False
                _atomic_write_token(creds)
                self._auth_version += 1
                self._explicitly_disconnected = False
                self.credentials = creds
                self.youtube = new_client
                if hasattr(self, "_thread_local"):
                    self._thread_local.client = new_client
                    self._thread_local.version = self._auth_version
                    self._thread_local.creds = creds
                self._oauth_flow_status = {
                    "attempt_id": current_attempt,
                    "status": "connected",
                    "message": "YouTube channel connected successfully."
                }
            logger.info("Successfully connected YouTube channel via OAuth 2.0.")
            return True
        except Exception as e:
            logger.error(f"Error during interactive OAuth flow: {e}")
            with self._auth_lock:
                if self._login_attempt_id == current_attempt:
                    self._oauth_flow_status = {
                        "attempt_id": current_attempt,
                        "status": "failed",
                        "error_code": "interactive_error",
                        "message": f"Interactive authentication failed: {str(e)}"
                    }
            return False

    def logout(self) -> Dict[str, Any]:
        """Disconnects current YouTube channel and clears cached OAuth credentials."""
        with self._auth_lock:
            if self._active_uploads > 0 or self._publication_reservation_id is not None:
                logger.warning("Cannot logout while upload or publication reservation is in progress.")
                return {"cleared": False, "reason": "upload_in_progress", "token_unlinked": False}
            self._login_attempt_id += 1
            self._auth_version += 1
            self._explicitly_disconnected = True
            self.credentials = None
            self.youtube = None
            self._oauth_flow_status = {
                "attempt_id": self._login_attempt_id,
                "status": "idle",
                "message": ""
            }
            if hasattr(self, "_thread_local"):
                self._thread_local.client = None
                self._thread_local.version = None
                self._thread_local.creds = None
            deletion_success = True
            if YOUTUBE_TOKEN_PATH.exists():
                try:
                    YOUTUBE_TOKEN_PATH.unlink()
                    logger.info("Removed stored YouTube OAuth token.")
                except Exception as e:
                    logger.error(f"Error removing token file: {e}")
                    deletion_success = False
            return {"cleared": True, "token_unlinked": deletion_success}

    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """Confirm connected channel identity before publishing."""
        client, _ = self.get_authenticated_client()
        if not client:
            return None
        try:
            res = client.channels().list(part="snippet,statistics", mine=True).execute()
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
        scheduled_publish_time: Optional[str] = None,
        expected_auth_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Uploads a vertical video as a YouTube Short.
        """
        client, auth_version_at_start = self.get_authenticated_client()
        if not client:
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

        with self._auth_lock:
            if self._explicitly_disconnected or self._auth_version != auth_version_at_start:
                return {
                    "success": False,
                    "error": "Upload aborted: YouTube account was disconnected or changed before upload started."
                }
            if expected_auth_version is not None and self._auth_version != expected_auth_version:
                return {
                    "success": False,
                    "error": "Upload aborted: Reserved YouTube account version changed before upload slot acquisition."
                }
            self._active_uploads += 1

        logger.info(f"Uploading '{clean_title}' to YouTube...")
        try:
            request = client.videos().insert(
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
        finally:
            with self._auth_lock:
                self._active_uploads = max(0, self._active_uploads - 1)
