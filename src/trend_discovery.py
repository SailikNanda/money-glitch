"""Automated YouTube Trend Discovery Engine for Viral Shorts Autopilot.
Queries YouTube Data API v3 and public video feeds for:
- GTA 6 updates, reactions, and discussions (60% weight)
- Gaming livestream highlights and funny moments (25% weight)
- US viral internet trends (15% weight)
Calculates view velocity, freshness, and tags initial rights validation.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import yt_dlp
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import (
    GOOGLE_API_KEY,
    YOUTUBE_DATA_API_KEY,
    TOPIC_WEIGHTS,
    CATEGORIES_CATALOG,
    DISCOVERY_QUERIES
)
from .db import add_candidate, get_setting
from .rights_validator import RightsValidator

logger = logging.getLogger("TrendDiscovery")
logging.basicConfig(level=logging.INFO)

class TrendDiscoveryEngine:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_DATA_API_KEY", "")
        self.youtube = None
        if self.api_key:
            try:
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize YouTube API client: {e}. Falling back to yt-dlp.")
        self.rights_validator = RightsValidator()

    def run_discovery_cycle(self, max_per_category: int = 3, categories_per_cycle: int = 6) -> List[Dict[str, Any]]:
        """
        Executes a balanced trend discovery cycle across 24 dynamic categories.
        Rotates across Gaming, Cinema, Sports, and Viral Culture.
        Samples from any creator on YouTube with balanced velocity + exploration scoring.
        """
        import random
        logger.info("Starting Multi-Genre Balanced Trend Discovery Cycle...")
        discovered_candidates = []

        # Group categories by vertical
        verticals = {"gaming": [], "cinema": [], "sports": [], "viral": []}
        for cat_id, cat_info in CATEGORIES_CATALOG.items():
            vert = cat_info.get("vertical", "gaming")
            verticals.setdefault(vert, []).append((cat_id, cat_info))

        # Sample categories across all verticals for guaranteed diversity in every cycle
        sampled_categories = []
        for vert, cat_list in verticals.items():
            k = 2 if vert in ("gaming", "cinema") else 1
            sampled_categories.extend(random.sample(cat_list, min(k, len(cat_list))))

        random.shuffle(sampled_categories)
        logger.info(f"Selected {len(sampled_categories)} categories for this discovery cycle: {[c[0] for c in sampled_categories]}")

        seen_channels = set()

        for category_id, cat_info in sampled_categories:
            queries = cat_info.get("queries", [])
            query = random.choice(queries) if queries else f"trending {category_id}"
            logger.info(f"Discovering [{cat_info.get('label', category_id)}]: '{query}'")

            batch_results = []
            if self.youtube:
                try:
                    batch_results = self._search_via_api(query, category_id, limit=max_per_category * 2)
                except HttpError as err:
                    logger.warning(f"YouTube API error: {err}. Falling back to yt-dlp search.")
                    self.youtube = None
                    batch_results = self._search_via_ytdlp(query, category_id, limit=max_per_category * 2)
            else:
                batch_results = self._search_via_ytdlp(query, category_id, limit=max_per_category * 2)

            # Balanced Creator Sampling: Favor high-velocity/famous clips while avoiding channel repetition
            for cand in batch_results:
                channel = (cand.get("channel_title") or "").strip().lower()
                if channel and channel in seen_channels:
                    continue  # Strict 1 candidate per channel per cycle to avoid channel dominance

                # Calculate Exploration & Virality Score
                base_velocity = float(cand.get("view_velocity", 0.0))
                # Add exploration jitter (+0 to +15 pts) so new/smaller creators also get featured
                exploration_jitter = random.uniform(0.0, 15.0)
                cand["virality_score"] = round(min(98.0, max(85.0, 88.0 + (base_velocity / 500.0) + exploration_jitter)), 1)

                if channel:
                    seen_channels.add(channel)
                discovered_candidates.append(cand)
                if len([c for c in discovered_candidates if c.get("category") == category_id]) >= max_per_category:
                    break

        # Ingest and validate rights for each candidate
        new_count = 0
        for cand in discovered_candidates:
            eligible, rights_status, attribution = self.rights_validator.validate_candidate(cand)
            cand["rights_status"] = rights_status
            cand["rights_notes"] = attribution

            if add_candidate(cand):
                new_count += 1

        logger.info(f"Trend Discovery completed. {len(discovered_candidates)} candidates across {len(seen_channels)} creators, {new_count} new entries saved.")
        return discovered_candidates

    def _search_via_api(self, query: str, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube Data API v3 and get detailed video metrics."""
        candidates = []
        search_res = self.youtube.search().list(
            q=query,
            part="id,snippet",
            maxResults=limit,
            type="video",
            videoDuration="medium",  # 4-20 minutes
            relevanceLanguage="en",
            regionCode="US"
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_res.get("items", []) if "videoId" in item.get("id", {})]
        if not video_ids:
            return []

        # Get detailed statistics and content details
        videos_res = self.youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,statistics,contentDetails"
        ).execute()

        for item in videos_res.get("items", []):
            vid = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})

            view_count = int(stats.get("viewCount", 0))
            published_str = snippet.get("publishedAt", "")
            velocity = self._calculate_velocity(view_count, published_str)

            candidates.append({
                "video_id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "category": category,
                "view_count": view_count,
                "view_velocity": velocity,
                "published_at": published_str,
                "duration_seconds": 0.0  # Parsed as needed
            })

        return candidates

    def _search_via_ytdlp(self, query: str, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback search using yt-dlp ytsearch."""
        candidates = []
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "socket_timeout": 8,
            "retries": 1,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
                for entry in info.get("entries", []):
                    if not entry:
                        continue
                    vid = entry.get("id")
                    if not vid:
                        continue
                    view_count = entry.get("view_count") or 0
                    timestamp = entry.get("upload_date") or ""
                    velocity = float(view_count) / 24.0 if view_count else 0.0

                    candidates.append({
                        "video_id": vid,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "title": entry.get("title", ""),
                        "channel_title": entry.get("uploader", ""),
                        "channel_id": entry.get("channel_id", ""),
                        "category": category,
                        "view_count": view_count,
                        "view_velocity": round(velocity, 2),
                        "published_at": timestamp,
                        "duration_seconds": float(entry.get("duration") or 0.0)
                    })
        except Exception as e:
            logger.error(f"yt-dlp search error for '{query}': {e}")
        return candidates

    def _calculate_velocity(self, view_count: int, published_at_str: str) -> float:
        """Calculate views per hour since publication."""
        try:
            pub_dt = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            hours = (now_dt - pub_dt).total_seconds() / 3600.0
            hours = max(hours, 0.5)
            return round(view_count / hours, 2)
        except Exception:
            return round(float(view_count) / 24.0, 2)
