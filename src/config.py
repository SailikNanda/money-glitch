"""Configuration settings for Viral Shorts Autopilot.
Project: Viral Shorts Autopilot
Target Audience: United States (American English)
Primary Content Priority: GTA 6 / Grand Theft Auto VI (60%)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load workspace .env if present
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(WORKSPACE_DIR / ".env")

# Directory Layout
DATA_DIR = WORKSPACE_DIR / "data"
CLIPS_DIR = WORKSPACE_DIR / "clips"
EXPORTS_DIR = CLIPS_DIR / "exports"
ASSETS_DIR = WORKSPACE_DIR / "assets"
DB_PATH = DATA_DIR / "autopilot.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# YouTube & Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY", GOOGLE_API_KEY)
YOUTUBE_CLIENT_SECRETS_PATH = DATA_DIR / "client_secrets.json"
YOUTUBE_TOKEN_PATH = DATA_DIR / "youtube_token.json"

# SupoClip Configuration
SUPOCLIP_API_URL = os.getenv("SUPOCLIP_API_URL", "http://localhost:8000")
SUPOCLIP_API_KEY = os.getenv("SUPOCLIP_API_KEY", "")
SUPOCLIP_USER_ID = os.getenv("SUPOCLIP_USER_ID", "autopilot_user")
GAMING_LAYOUT_MODE = os.getenv("GAMING_LAYOUT", "auto")  # off | auto

# Scheduling & Queue Parameters
SCHEDULING_TIMEZONE = os.getenv("AUTOPILOT_TIMEZONE", "America/New_York")
DISCOVERY_INTERVAL_HOURS = 3
DAILY_MAX_CANDIDATE_CLIPS = 10
DAILY_MAX_PUBLISHED_SHORTS = 3   # Optimal safe limit for YouTube algorithm (avoids spam flag/shadowban)
MIN_UPLOAD_SPACING_HOURS = 4     # Required gap between uploads to protect channel health
AUTONOMOUS_MODE = True           # Auto-pipeline: Discover -> Clip -> Meme Edit -> AI Title -> Queue -> Upload

# Topic Priorities & Dynamic Multi-Genre Weights (Dynamic Trend Engine)
TOPIC_WEIGHTS = {
    "gaming": 0.40,      # Top viral streamer reactions, fails, clutches (Speed, Kai Cenat, GTA 6)
    "cinema": 0.35,      # Trending movie trailers, anime climaxes, blockbuster pop culture
    "trends": 0.25,      # Real-time breakout internet & entertainment trends
}

# Trend Discovery Queries by Topic Category (Focusing on completed streams & viral moments)
DISCOVERY_QUERIES = {
    "cinema": [
        "trending official movie trailer climax 2026",
        "blockbuster movie epic action scene clip",
        "anime viral fight scene 4k clip",
        "trending marvel cinema scene soundtrack"
    ],
    "gaming": [
        "IShowSpeed GTA 6 funny stream reaction",
        "Kai Cenat streamer rage hilarious moments",
        "crazy gaming clutch fail stream highlight",
        "GTA 6 insane streamer gameplay moments"
    ],
    "trends": [
        "viral entertainment trend moments US",
        "breakout pop culture internet moments 2026"
    ]
}

# Upload Defaults
DEFAULT_PRIVACY_STATUS = os.getenv("AUTOPILOT_PRIVACY", "public")  # 'public' for auto-publishing, 'unlisted' for staging
AUTO_PUBLISH_DEFAULT = True  # Fully autonomous publishing

# Video specs for vertical Shorts
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
MIN_CLIP_DURATION = 15.0
MAX_CLIP_DURATION = 45.0
ABSOLUTE_MAX_DURATION = 60.0
