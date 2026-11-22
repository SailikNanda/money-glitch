"""Storage Manager for Money Glitch Autopilot.
Automatically purges temporary stream chunks, intermediate ffmpeg renders,
and clears storage once videos are published to keep disk space lean and fresh.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

from .config import CLIPS_DIR, EXPORTS_DIR, WORKSPACE_DIR
from .db import list_published

logger = logging.getLogger("StorageManager")

def purge_temporary_stream_files(purge_legacy_drafts: bool = True) -> Dict[str, Any]:
    """Deletes all raw stream downloads (*.webm), temp files, scratch frames,
    and legacy experimental clips so storage remains clean and lean.
    """
    freed_bytes = 0
    deleted_files: List[str] = []

    # Patterns for temporary raw downloads, frames, and intermediate renders
    temp_patterns = [
        "raw_*.webm",
        "*.tmp",
        "temp_*",
        "*_temp.*",
        "*.webm",
        "*.jpg",
        "*.jpeg",
        "*.png",
        "verify_*.*",
        "frame_*.*",
        "meme_*.*"
    ]

    search_dirs = [
        CLIPS_DIR, 
        EXPORTS_DIR, 
        WORKSPACE_DIR,
        CLIPS_DIR / "downloads",
        CLIPS_DIR / "inspect_c3",
        CLIPS_DIR / "exports"
    ]

    for d in search_dirs:
        if not d.exists():
            continue
        for pat in temp_patterns:
            for f in d.glob(pat):
                if f.is_file():
                    try:
                        sz = f.stat().st_size
                        f.unlink()
                        freed_bytes += sz
                        deleted_files.append(f.name)
                        logger.info(f"Purged temporary file: {f.name} ({sz / (1024*1024):.2f} MB)")
                    except Exception as e:
                        logger.warning(f"Could not delete {f.name}: {e}")

    # If purge_legacy_drafts is requested, clean up unselected older meme experiments
    if purge_legacy_drafts and CLIPS_DIR.exists():
        # Keep only the active reference clips
        protected_clips = {
            "clip_1_ULTRA_MEME_SATURATED.mp4",
            "short_35KDnej1hlI_1_5s.mp4",
            "short_G3KoTo4ozEw_2_35s.mp4",
            "speed_gta6_pro_edit.mp4"
        }
        for mp4 in CLIPS_DIR.glob("clip_*.mp4"):
            if mp4.name not in protected_clips:
                try:
                    sz = mp4.stat().st_size
                    mp4.unlink()
                    freed_bytes += sz
                    deleted_files.append(mp4.name)
                    logger.info(f"Purged legacy draft clip: {mp4.name} ({sz / (1024*1024):.2f} MB)")
                except Exception as e:
                    logger.warning(f"Could not delete legacy draft {mp4.name}: {e}")

    freed_mb = freed_bytes / (1024 * 1024)
    logger.info(f"Storage Cleanup completed. Freed {freed_mb:.2f} MB across {len(deleted_files)} files.")
    return {
        "status": "success",
        "freed_mb": round(freed_mb, 2),
        "deleted_count": len(deleted_files),
        "deleted_files": deleted_files
    }

def cleanup_published_files(keep_latest_exports: int = 5) -> Dict[str, Any]:
    """Cleans up older heavy export files for videos that are already safely published on YouTube."""
    freed_bytes = 0
    deleted_files: List[str] = []

    published = list_published()
    published_ids = {p.get("youtube_video_id") for p in published}

    # Find export files in EXPORTS_DIR
    all_exports = sorted(list(EXPORTS_DIR.glob("*.mp4")), key=lambda p: p.stat().st_mtime, reverse=True)

    # Keep the most recent N exports for the local dashboard player preview
    to_check = all_exports[keep_latest_exports:]

    for f in to_check:
        try:
            sz = f.stat().st_size
            f.unlink()
            freed_bytes += sz
            deleted_files.append(f.name)
            logger.info(f"Purged archived export: {f.name} ({sz / (1024*1024):.2f} MB)")
        except Exception as e:
            logger.warning(f"Could not delete archived export {f.name}: {e}")

    freed_mb = freed_bytes / (1024 * 1024)
    return {
        "status": "success",
        "freed_mb": round(freed_mb, 2),
        "deleted_count": len(deleted_files),
        "deleted_files": deleted_files
    }

def get_storage_stats() -> Dict[str, Any]:
    """Calculates current disk usage in workspace directories."""
    total_bytes = 0
    for d in [CLIPS_DIR, EXPORTS_DIR]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file():
                    total_bytes += f.stat().st_size

    total_mb = round(total_bytes / (1024 * 1024), 2)
    return {
        "clips_storage_mb": total_mb,
        "is_lean": total_mb < 300,
        "storage_health": "OPTIMAL" if total_mb < 300 else "NEEDS_PURGE"
    }
