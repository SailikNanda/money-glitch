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

# Real-Time Freshness Window (Strict 5-day ceiling: Max 120 hours)
FRESHNESS_WINDOW_DAYS = 5
FRESHNESS_WINDOW_HOURS = 120.0

# Optimal YouTube Shorts Viral Publishing Windows (America/New_York Time)
# Targets maximum online audience engagement waves & avoids dead zones (1 AM - 10 AM).
OPTIMAL_VIRAL_WINDOWS = [
    {"slot": 1, "name": "Midday Lunch Surge", "start_hour": 11.5, "end_hour": 14.5, "target": "12:00 PM"},
    {"slot": 2, "name": "Afternoon Commute Peak", "start_hour": 16.5, "end_hour": 19.0, "target": "05:00 PM"},
    {"slot": 3, "name": "Prime Evening Scroll", "start_hour": 20.0, "end_hour": 23.0, "target": "08:30 PM"}
]
ENFORCE_VIRAL_HOURS = os.getenv("ENFORCE_VIRAL_HOURS", "true").lower() == "true"

# Topic Priorities & Dynamic Multi-Genre Weights (Dynamic Real-Time Trend Engine)
TOPIC_WEIGHTS = {
    "gaming": 0.35,      # Viral streamers (Speed, Kai, Jynxzi, Fanum, Sketch) & trending games (GTA 6, etc.)
    "cinema": 0.25,      # Trending official movie trailers, anime climaxes, blockbuster pop culture
    "sports": 0.20,      # NBA buzzer beaters, UFC knockouts, crazy athletic highlights
    "trends": 0.20,      # Real-time breakout internet news, viral debates & pop-culture moments
}

# -------------------------------------------------------------------------
# 24 Dynamic Multi-Genre Categories (Gaming, Cinema, Sports, Viral Culture)
# No single creator or niche hardcoded. Explores all creators dynamically.
# -------------------------------------------------------------------------
CATEGORIES_CATALOG = {
    # === 1. GAMING VERTICAL (8 Diverse Categories) ===
    "gaming_open_world": {
        "label": "Open World & Sandbox Chaos",
        "vertical": "gaming",
        "queries": ["trending open world gameplay funny moments", "GTA 6 open world crazy gameplay", "RDR2 open world hilarious encounters"]
    },
    "gaming_fps_esports": {
        "label": "FPS & Esports Clutches",
        "vertical": "gaming",
        "queries": ["1v5 impossible esports clutch 60fps", "Valorant insane ace stream reaction", "Warzone craziest sniper play"]
    },
    "gaming_survival_sandbox": {
        "label": "Survival & Sandbox Traps",
        "vertical": "gaming",
        "queries": ["Minecraft insane redstone trap reaction", "Rust craziest base raid clutch", "survival game impossible escape"]
    },
    "gaming_horror_jumpscare": {
        "label": "Horror & Jumpscare Reactions",
        "vertical": "gaming",
        "queries": ["funniest gamer horror game jumpscare screams", "lethal company hilarious stream moments", "scariest horror game reaction stream"]
    },
    "gaming_physics_destruction": {
        "label": "Physics Destruction & Simulators",
        "vertical": "gaming",
        "queries": ["BeamNG drive most satisfying crash physics", "Teardown insane destruction physics", "simulator game broken physics moments"]
    },
    "gaming_rage_fails": {
        "label": "Gamer Rage & Instant Karma",
        "vertical": "gaming",
        "queries": ["streamer rage quit broken controller funny", "gamer instant karma funny moments", "unluckiest gamer moments stream"]
    },
    "gaming_souls_bossfights": {
        "label": "Souls-like & Impossible Boss Fights",
        "vertical": "gaming",
        "queries": ["no hit boss fight insane reaction", "Elden Ring impossible boss clutch", "hardest game boss defeated scream"]
    },
    "gaming_indie_viral": {
        "label": "Breakout Viral Indie Games",
        "vertical": "gaming",
        "queries": ["viral new indie game crazy gameplay", "trending steam game everyone is playing", "hidden gem indie game insane moment"]
    },

    # === 2. MOVIES & CINEMA VERTICAL (5 Diverse Categories) ===
    "cinema_blockbuster_trailers": {
        "label": "Official Blockbuster Movie Trailers",
        "vertical": "cinema",
        "queries": ["official movie trailer 2026 4K", "blockbuster movie teaser climax reaction", "new superhero movie trailer climax"]
    },
    "cinema_epic_action": {
        "label": "Cinematic Action & Chase Sequences",
        "vertical": "cinema",
        "queries": ["greatest movie car chase scene 4K", "epic movie battle sequence climax", "best movie stunt ever performed"]
    },
    "cinema_anime_battles": {
        "label": "Viral Anime Fight Climaxes",
        "vertical": "cinema",
        "queries": ["anime fight scene 4K 60fps", "most hyped anime battle climax", "legendary anime transformation scene"]
    },
    "cinema_plot_twists": {
        "label": "Mind-Bending Movie Plot Twists",
        "vertical": "cinema",
        "queries": ["craziest movie plot twist nobody saw coming", "thriller movie ending mind blown", "most shocking cinema revelations"]
    },
    "cinema_soundtrack_drops": {
        "label": "Cinematic Music & Visual Drops",
        "vertical": "cinema",
        "queries": ["epic movie soundtrack visual drop", "Hans Zimmer epic cinema score moment", "chill-inducing movie sequence soundtrack"]
    },

    # === 3. SPORTS & ATHLETICS VERTICAL (6 Diverse Categories) ===
    "sports_nba_basketball": {
        "label": "NBA Buzzer Beaters & Dunk Climaxes",
        "vertical": "sports",
        "queries": ["NBA game winner buzzer beater highlights", "coldest basketball ankle breaker dunk", "insane basketball clutch moment"]
    },
    "sports_combat_ufc_boxing": {
        "label": "UFC & Boxing Knockout Finishes",
        "vertical": "sports",
        "queries": ["UFC brutal knockout finish slow motion", "boxing walk off knockout counter punch", "most shocking MMA comeback knockout"]
    },
    "sports_soccer_golazos": {
        "label": "Football / Soccer Screamer Goals",
        "vertical": "sports",
        "queries": ["Champions League impossible goal of the month", "Premier League 90th minute bicycle kick", "craziest goalkeeper save in history"]
    },
    "sports_extreme_stunts": {
        "label": "Extreme Sports & Stunt Feats",
        "vertical": "sports",
        "queries": ["Red Bull extreme stunt viral clip", "insane skateboard ramp trick 4K", "parkour impossible roof jump save"]
    },
    "sports_nfl_clutches": {
        "label": "Football / NFL Impossible Catches",
        "vertical": "sports",
        "queries": ["NFL craziest one handed touchdown catch", "hail mary 4th quarter clutch play", "unbelievable football tackle return"]
    },
    "sports_motorsport_drifts": {
        "label": "Motorsports & Supercar Drifts",
        "vertical": "sports",
        "queries": ["Formula 1 insane overtake 60fps", "supercar drift near miss save", "rally car impossible corner slide"]
    },

    # === 4. VIRAL INTERNET & CULTURE (5 Diverse Categories) ===
    "viral_unbelievable_odds": {
        "label": "1 in a Million Odds & Lucky Saves",
        "vertical": "viral",
        "queries": ["one in a million caught on camera", "craziest lucky save ever recorded", "unbelievable coincidence real life"]
    },
    "viral_tech_robotics": {
        "label": "Futuristic Tech & Robotics Leaks",
        "vertical": "viral",
        "queries": ["insane futuristic humanoid robot demo", "new futuristic tech gadget reveal", "flying car technology real demo"]
    },
    "viral_wholesome_animals": {
        "label": "Clever Pets & Wild Animal Feats",
        "vertical": "viral",
        "queries": ["smartest dog saves owner caught on camera", "wild animal encounters incredible moments", "funniest cat reflexes viral clip"]
    },
    "viral_satisfying_craft": {
        "label": "Satisfying Restorations & Visual ASMR",
        "vertical": "viral",
        "queries": ["hydraulic press vs titanium satisfying", "ancient rusty tool restoration 4K", "satisfying optical illusion craft"]
    },
    "viral_street_trivia": {
        "label": "Public Street Interviews & Challenges",
        "vertical": "viral",
        "queries": ["funniest street interview public questions", "cash trivia challenge unexpected answer", "IQ test on the street hilarious"]
    }
}

# Dynamic Category Queries Extracted from Catalog
DISCOVERY_QUERIES = {k: v["queries"] for k, v in CATEGORIES_CATALOG.items()}

# Upload Defaults
DEFAULT_PRIVACY_STATUS = os.getenv("AUTOPILOT_PRIVACY", "public")  # 'public' for auto-publishing, 'unlisted' for staging
AUTO_PUBLISH_DEFAULT = True  # Fully autonomous publishing

# Video specs for vertical Shorts
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
MIN_CLIP_DURATION = 15.0
MAX_CLIP_DURATION = 45.0
ABSOLUTE_MAX_DURATION = 60.0
