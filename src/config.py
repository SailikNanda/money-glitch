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

# Topic Priorities & Dynamic Multi-Genre Weights (Dynamic Real-Time Trend Engine)
TOPIC_WEIGHTS = {
    "gaming": 0.35,      # Viral streamers (Speed, Kai, Jynxzi, Fanum, Sketch) & trending games (GTA 6, etc.)
    "cinema": 0.25,      # Trending official movie trailers, anime climaxes, blockbuster pop culture
    "sports": 0.20,      # NBA buzzer beaters, UFC knockouts, crazy athletic highlights
    "trends": 0.20,      # Real-time breakout internet news, viral debates & pop-culture moments
}

# Diverse Streamer & Creator Roster for Zigzag Publishing Pattern
CREATOR_ROSTER = [
    "IShowSpeed",
    "Kai Cenat",
    "Jynxzi",
    "Fanum",
    "Sketch",
    "xQc",
    "Tfue",
    "Pokimane",
    "Shroud"
]

# Trend Discovery Queries by Topic Category (Rotated Dynamically)
DISCOVERY_QUERIES = {
    "gaming": [
        "trending gaming stream funny moments US",
        "IShowSpeed hilarious stream moments",
        "Kai Cenat stream rage moments",
        "Jynxzi best stream reactions clips",
        "GTA 6 insane gameplay moments",
        "crazy gaming clutch fail stream highlight",
        "Sketch streamer funniest clips"
    ],
    "cinema": [
        "trending official movie trailer climax 2026",
        "blockbuster movie epic action scene clip",
        "anime viral fight scene 4k clip",
        "trending marvel cinema scene soundtrack"
    ],
    "sports": [
        "NBA craziest buzzer beater highlights 2026",
        "UFC viral knockout finish reaction",
        "Premier League incredible goal of the week",
        "insane athletic play sports highlights"
    ],
    "trends": [
        "real time viral internet trend moments US",
        "breakout pop culture internet news 2026",
        "funniest viral video of the week US"
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
