"""Storage Manager for Money Glitch Autopilot.
Automatically purges temporary stream chunks, intermediate ffmpeg renders,
sample video files, and resets storage cleanly to 0.00 MB.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List

from .config import CLIPS_DIR, EXPORTS_DIR, WORKSPACE_DIR
from .db import list_published, clear_all_data

logger = logging.getLogger("StorageManager")

def purge_temporary_stream_files(hard_purge: bool = True) -> Dict[str, Any]:
    """Deletes ALL generated clips, sample videos, stream downloads (*.webm),
    temporary exports, and scratch frames recursively so storage becomes 0.00 MB.
    """
    freed_bytes = 0
    deleted_files: List[str] = []
    failed_files: List[str] = []

    # Patterns to delete
    patterns = [
        "*.mp4",
        "*.webm",
        "*.mkv",
        "*.avi",
        "*.mov",
        "*.tmp",
        "temp_*",
        "*_temp.*",
        "raw_*.*",
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
        WORKSPACE_DIR / "scratch"
    ]

    for d in search_dirs:
        if not d.exists():
            continue
        for pat in patterns:
            # Recursive traversal to catch nested job folders
            for f in list(d.rglob(pat)):
                if f.is_file():
                    try:
                        sz = f.stat().st_size
                        f.unlink()
                        freed_bytes += sz
                        deleted_files.append(f.name)
                        logger.info(f"Purged file: {f.name} ({sz / (1024*1024):.2f} MB)")
                    except Exception as e:
                        failed_files.append(f.name)
                        logger.warning(f"Could not delete {f.name}: {e}")

    # Also clean up any lingering test mp4s in root workspace directory
    for root_file in WORKSPACE_DIR.glob("*.mp4"):
        if root_file.is_file():
            try:
                sz = root_file.stat().st_size
                root_file.unlink()
                freed_bytes += sz
                deleted_files.append(root_file.name)
                logger.info(f"Purged root test video: {root_file.name} ({sz / (1024*1024):.2f} MB)")
            except Exception as e:
                failed_files.append(root_file.name)
                logger.warning(f"Could not delete {root_file.name}: {e}")

    # Ensure empty directory structure exists
    for d in [CLIPS_DIR, EXPORTS_DIR, CLIPS_DIR / "exports", CLIPS_DIR / "downloads"]:
        d.mkdir(parents=True, exist_ok=True)

    freed_mb = freed_bytes / (1024 * 1024)
    logger.info(f"Complete Storage Cleanup finished. Freed {freed_mb:.2f} MB across {len(deleted_files)} files.")
    return {
        "status": "success" if not failed_files else "partial",
        "freed_mb": round(freed_mb, 2),
        "deleted_count": len(deleted_files),
        "deleted_files": deleted_files,
        "failed_files": failed_files
    }

def cleanup_published_files(keep_latest_exports: int = 2) -> Dict[str, Any]:
    """Cleans up older heavy export files only for videos that are already safely published,
    preserving queued and unpublished clips.
    """
    freed_bytes = 0
    deleted_files: List[str] = []
    
    published = list_published()
    published_titles = {p.get("title", "") for p in published}
    published_video_ids = {p.get("youtube_video_id", "") for p in published}

    if not EXPORTS_DIR.exists():
        return {"status": "success", "freed_mb": 0.0, "deleted_count": 0, "deleted_files": []}

    all_exports = sorted(list(EXPORTS_DIR.rglob("*.mp4")), key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Identify which exports belong to published records
    published_exports = []
    for exp in all_exports:
        for p_id in published_video_ids:
            if p_id and p_id in exp.name:
                published_exports.append(exp)
                break

    to_delete = published_exports[keep_latest_exports:]
    for f in to_delete:
        try:
            sz = f.stat().st_size
            f.unlink()
            freed_bytes += sz
            deleted_files.append(f.name)
            logger.info(f"Purged published export: {f.name} ({sz / (1024*1024):.2f} MB)")
        except Exception as e:
            logger.warning(f"Could not delete published export {f.name}: {e}")

    freed_mb = freed_bytes / (1024 * 1024)
    return {
        "status": "success",
        "freed_mb": round(freed_mb, 2),
        "deleted_count": len(deleted_files),
        "deleted_files": deleted_files
    }

def reset_all_data() -> Dict[str, Any]:
    """Performs a 100% hard reset: wipes all media storage and database history,
    then verifies actual measured storage.
    """
    storage_res = purge_temporary_stream_files(hard_purge=True)
    clear_all_data()
    
    # Measure actual remaining storage to verify completion
    stats = get_storage_stats()
    measured_mb = stats["clips_storage_mb"]
    success = (measured_mb == 0.0)

    logger.info(f"Hard Reset completed: {measured_mb} MB measured remaining. Database tables wiped to zero.")
    return {
        "status": "success" if success else "partial",
        "freed_mb": storage_res["freed_mb"],
        "deleted_count": storage_res["deleted_count"],
        "current_storage_mb": measured_mb,
        "message": "All media and database records cleared to 0.00 MB. Ready for fresh start." if success else f"Reset partially completed ({measured_mb} MB remaining)."
    }

def get_storage_stats() -> Dict[str, Any]:
    """Calculates current video clips and exports disk usage in workspace directories."""
    total_bytes = 0
    for d in [CLIPS_DIR, EXPORTS_DIR]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file():
                    total_bytes += f.stat().st_size

    total_mb = round(total_bytes / (1024 * 1024), 2)
    return {
        "clips_storage_mb": total_mb,
        "is_lean": total_mb == 0.0,
        "storage_health": "OPTIMAL (0.00 MB)" if total_mb == 0.0 else f"ACTIVE ({total_mb} MB)"
    }
