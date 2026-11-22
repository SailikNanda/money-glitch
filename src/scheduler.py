"""Autonomous Upload Scheduler & Pipeline Orchestrator for Viral Shorts Autopilot.
Enforces:
- 3-hour trend discovery interval
- Production of 5-10 candidate clips daily
- Publication of ~3 high-quality Shorts daily with >= 4-hour spacing
- America/New_York timezone alignment
- Strict rights verification gate before any upload
- Safe recovery and idempotent duplicate prevention
"""

import time
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional

from .config import (
    WORKSPACE_DIR,
    SCHEDULING_TIMEZONE,
    DAILY_MAX_CANDIDATE_CLIPS,
    DAILY_MAX_PUBLISHED_SHORTS,
    MIN_UPLOAD_SPACING_HOURS,
    DISCOVERY_INTERVAL_HOURS,
    DEFAULT_PRIVACY_STATUS,
    AUTO_PUBLISH_DEFAULT
)
from .storage_manager import purge_temporary_stream_files
from .db import (
    get_setting,
    set_setting,
    list_candidates,
    list_clips,
    list_upload_queue,
    enqueue_upload,
    record_published,
    list_published,
    update_candidate_status
)
from .trend_discovery import TrendDiscoveryEngine
from .clipping_engine import ClippingEngine
from .invideo_enhancer import InvideoEnhancer
from .youtube_uploader import YouTubeUploader

logger = logging.getLogger("Scheduler")
logging.basicConfig(level=logging.INFO)

class AutonomousScheduler:
    def __init__(self):
        self.tz = ZoneInfo(SCHEDULING_TIMEZONE)
        self.discovery_engine = TrendDiscoveryEngine()
        self.clipping_engine = ClippingEngine()
        self.invideo_enhancer = InvideoEnhancer()
        self.youtube_uploader = YouTubeUploader()

    def run_full_pipeline_iteration(self) -> Dict[str, Any]:
        """
        Executes one full iteration of the autonomous cycle:
        1. Checks safety flags (Emergency Stop)
        2. Discovers trending topics
        3. Clips top authorized candidate moments
        4. Validates pacing (max 3/day, 4h gap) and uploads if authorized
        """
        if get_setting("emergency_stop", False):
            logger.warning("Emergency Stop is ACTIVE. Halting scheduler pipeline.")
            return {"status": "halted", "reason": "emergency_stop"}

        logger.info(f"Running autonomous pipeline cycle in timezone: {SCHEDULING_TIMEZONE}")
        results = {
            "timestamp": datetime.now(self.tz).isoformat(),
            "discovered": 0,
            "authorized_eligible": 0,
            "clips_generated": 0,
            "generated_clips": [],
            "uploaded": 0,
            "auto_publish_enabled": False,
            "pacing": {}
        }

        # Step 1: Trend Discovery
        try:
            candidates = self.discovery_engine.run_discovery_cycle(max_per_category=3)
            results["discovered"] = len(candidates)
        except Exception as e:
            logger.error(f"Error during trend discovery: {e}")

        # Step 2: Check eligible authorized candidates for clipping
        all_candidates = list_candidates(limit=100)
        authorized_candidates = [
            c for c in all_candidates
            if c.get("rights_status") in ("AUTHORIZED", "CREATIVE_COMMONS")
            and c.get("status") == "discovered"
        ]
        # Prioritize candidates with local files ready for immediate processing
        def _has_local_file(cand):
            u = cand.get("url", "")
            if Path(u).exists() or (WORKSPACE_DIR / "clips" / u).exists():
                return 0
            return 1
        authorized_candidates.sort(key=_has_local_file)
        results["authorized_eligible"] = len(authorized_candidates)

        # Step 3: Clipping Generation (enforce daily candidate target 5-10 with Zigzag Diversification)
        today_clips = [c for c in list_clips(limit=50) if c.get("created_at", "").startswith(datetime.now(timezone.utc).strftime("%Y-%m-%d"))]
        if len(today_clips) < DAILY_MAX_CANDIDATE_CLIPS and authorized_candidates:
            cand = self._select_zigzag_candidate(authorized_candidates)
            if cand:
                logger.info(f"Generating Shorts for Zigzag candidate: {cand['title']}")
                clips = self.clipping_engine.process_video_to_shorts(
                    source_path=cand.get("url"), # or local source
                    source_video_id=cand["video_id"],
                    topic=cand.get("category", "Trending"),
                    clip_title_prefix=cand["title"][:40]
                )
                if clips:
                    update_candidate_status(cand["video_id"], "clipped")
                    results["clips_generated"] += len(clips)
                    for cl in clips:
                        results["generated_clips"].append({
                            "id": cl.get("id"),
                            "title": cl.get("title"),
                            "file": Path(cl.get("clip_file", "")).name,
                            "virality_score": cl.get("virality_score"),
                            "duration": cl.get("duration"),
                            "gaming_layout": cl.get("gaming_layout_applied")
                        })

        # Step 4: Autonomous Upload Evaluation & Pacing Verification
        can_upload, wait_reason = self._check_upload_pacing()
        results["pacing"] = {
            "can_upload": can_upload,
            "wait_reason": wait_reason,
            "daily_max": DAILY_MAX_PUBLISHED_SHORTS,
            "min_spacing_hours": MIN_UPLOAD_SPACING_HOURS
        }

        # Stage unallocated ready clips into upload_queue with 4h spacing slots
        existing_queue = list_upload_queue()
        queued_clip_ids = {q["clip_id"] for q in existing_queue}
        unallocated_clips = [c for c in list_clips(limit=20, status="ready") if c["id"] not in queued_clip_ids]
        
        if unallocated_clips:
            if existing_queue:
                last_slot_str = max(q["scheduled_time"] for q in existing_queue)
                try:
                    last_slot = datetime.fromisoformat(last_slot_str)
                except Exception:
                    last_slot = datetime.now(timezone.utc)
            else:
                last_slot = datetime.now(timezone.utc)
                
            for clip in unallocated_clips:
                next_slot = last_slot + timedelta(hours=MIN_UPLOAD_SPACING_HOURS)
                enqueue_upload(clip["id"], next_slot.isoformat(), privacy=DEFAULT_PRIVACY_STATUS)
                last_slot = next_slot
                logger.info(f"Clip {clip['id']} enqueued for scheduled release at: {next_slot.isoformat()}")

        auto_publish = get_setting("auto_publish_enabled", AUTO_PUBLISH_DEFAULT)
        results["auto_publish_enabled"] = auto_publish
        if not auto_publish:
            logger.info("Auto-publishing is DISABLED in settings. Clips staged in ready queue.")
            purge_temporary_stream_files()
            return results

        # Check daily upload limit & spacing
        if not can_upload:
            logger.info(f"Upload pacing check: {wait_reason}")
            purge_temporary_stream_files()
            return results

        # Get highest scoring ready or queued clip using Zigzag Diversification
        ready_clips = [c for c in list_clips(limit=20) if c.get("status") in ("ready", "queued")]
        if not ready_clips:
            logger.info("No ready clips in queue for publication.")
            purge_temporary_stream_files()
            return results

        top_clip = self._select_zigzag_clip_to_upload(ready_clips)
        if not top_clip:
            logger.info("Could not resolve eligible zigzag clip for publication.")
            purge_temporary_stream_files()
            return results

        logger.info(f"Selected Zigzag clip for publication: ID {top_clip['id']} - {top_clip['title']} (Virality: {top_clip['virality_score']})")

        # Optional Invideo polish & spec verification
        enhanced = self.invideo_enhancer.enhance_clip(top_clip["clip_file"])
        final_video_path = enhanced.get("file_path", top_clip["clip_file"])

        # Execute YouTube upload
        upload_res = self.youtube_uploader.upload_short(
            video_path=final_video_path,
            title=top_clip["title"],
            description=top_clip["description"],
            tags=top_clip["hashtags"].split()
        )

        if upload_res.get("success"):
            record_published(
                clip_id=top_clip["id"],
                youtube_video_id=upload_res["video_id"],
                youtube_url=upload_res["youtube_url"],
                title=top_clip["title"]
            )
            results["uploaded"] += 1
            logger.info(f"Autonomous upload succeeded: {upload_res['youtube_url']}")
        else:
            logger.error(f"Upload failed: {upload_res.get('error')}")
            results["upload_error"] = upload_res.get("error")

        # Step 5: Automatic Storage Cleanup (Auto-delete raw stream downloads & temp renders)
        try:
            purge_res = purge_temporary_stream_files()
            results["storage_purged_mb"] = purge_res.get("freed_mb", 0)
        except Exception as e:
            logger.warning(f"Storage purge exception: {e}")

        return results

    def _check_upload_pacing(self) -> tuple[bool, str]:
        """
        Ensures:
        1. Published today < DAILY_MAX_PUBLISHED_SHORTS (3)
        2. Hours since last upload >= MIN_UPLOAD_SPACING_HOURS (4)
        """
        now = datetime.now(timezone.utc)
        published_list = list_published(limit=20)

        # 1. Check today's published count
        today_str = now.strftime("%Y-%m-%d")
        published_today = [p for p in published_list if p.get("published_at", "").startswith(today_str)]
        if len(published_today) >= DAILY_MAX_PUBLISHED_SHORTS:
            return False, f"Daily limit reached ({len(published_today)}/{DAILY_MAX_PUBLISHED_SHORTS} uploaded today)."

        # 2. Check spacing from last upload
        if published_list:
            last_pub_time_str = published_list[0].get("published_at", "")
            try:
                last_dt = datetime.fromisoformat(last_pub_time_str)
                gap_hours = (now - last_dt).total_seconds() / 3600.0
                if gap_hours < MIN_UPLOAD_SPACING_HOURS:
                    remaining = round(MIN_UPLOAD_SPACING_HOURS - gap_hours, 1)
                    return False, f"Upload spacing active: {remaining} hours remaining before next upload."
            except Exception:
                pass

        return True, "Upload window open."

    def _select_zigzag_candidate(self, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Zigzag Creator & Topic Diversification Selection:
        Rotates between distinct creators and categories.
        Avoids posting from the same creator or same sub-niche consecutively.
        """
        if not candidates:
            return None

        # Fetch recent uploads to inspect recently published creators and categories
        recent_published = list_published(limit=10)
        recent_titles_lower = [p.get("title", "").lower() for p in recent_published]

        # Prioritize candidates from creators that do NOT appear in the most recent uploads
        def _zigzag_penalty(cand):
            title = cand.get("title", "").lower()
            category = cand.get("category", "gaming").lower()

            penalty = 0
            for idx, rtitle in enumerate(recent_titles_lower[:4]):
                for creator in ["speed", "kai", "jynxzi", "fanum", "sketch", "gta", "cinema", "sports"]:
                    if creator in title and creator in rtitle:
                        penalty += (4 - idx) * 15

            # Local file bonus (ready for immediate processing)
            has_file = Path(cand.get("url", "")).exists() or (WORKSPACE_DIR / "clips" / cand.get("url", "")).exists()
            file_bonus = -10 if has_file else 0

            return penalty + file_bonus

        sorted_candidates = sorted(candidates, key=_zigzag_penalty)
        chosen = sorted_candidates[0]
        logger.info(f"[Zigzag Engine] Selected candidate: '{chosen.get('title')}' (Category: {chosen.get('category')})")
        return chosen

    def _select_zigzag_clip_to_upload(self, ready_clips: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Selects next clip to publish ensuring creator & genre zigzag rotation.
        """
        if not ready_clips:
            return None

        recent_published = list_published(limit=10)
        recent_titles_lower = [p.get("title", "").lower() for p in recent_published]

        def _clip_penalty(clip):
            title = clip.get("title", "").lower()
            penalty = 0
            for idx, rtitle in enumerate(recent_titles_lower[:4]):
                for creator in ["speed", "kai", "jynxzi", "fanum", "sketch", "gta", "cinema", "sports"]:
                    if creator in title and creator in rtitle:
                        penalty += (4 - idx) * 15

            virality = float(clip.get("virality_score", 90.0))
            return penalty - virality

        sorted_clips = sorted(ready_clips, key=_clip_penalty)
        return sorted_clips[0]

    def run_continuous_daemon(self, check_interval_seconds: int = 1800):
        """
        Continuous Autonomous Studio Daemon.
        Runs as long as the computer is turned ON.
        When the computer is shut down, execution halts cleanly.
        When restarted, it resumes from SQLite state seamlessly without lost pacing.
        """
        logger.info(f"[Lifecycle] Starting Continuous Autonomous Daemon (Interval: {check_interval_seconds}s)")
        while True:
            try:
                logger.info(f"[Lifecycle Heartbeat] Running autonomous cycle @ {datetime.now(self.tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
                res = self.run_full_pipeline_iteration()
                logger.info(f"[Lifecycle Cycle Complete] Uploaded: {res.get('uploaded', 0)} | Clips: {res.get('clips_generated', 0)}")
            except Exception as e:
                logger.error(f"[Lifecycle Error] Daemon cycle error: {e}")

            logger.info(f"[Lifecycle Sleeping] Next heartbeat in {check_interval_seconds}s (Will resume instantly if machine restarts)...")
            time.sleep(check_interval_seconds)
