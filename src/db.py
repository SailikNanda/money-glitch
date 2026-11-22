"""Persistent SQLite Database layer for Viral Shorts Autopilot.
Stores candidates, clipping jobs, generated clips, upload queue, and published analytics.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from .config import DB_PATH, TOPIC_WEIGHTS

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Candidates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        video_id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        channel_title TEXT,
        category TEXT NOT NULL,
        view_count INTEGER DEFAULT 0,
        view_velocity REAL DEFAULT 0.0,
        duration_seconds REAL DEFAULT 0.0,
        published_at TEXT,
        discovered_at TEXT NOT NULL,
        rights_status TEXT NOT NULL DEFAULT 'PENDING_VERIFICATION',
        rights_notes TEXT,
        status TEXT NOT NULL DEFAULT 'discovered'
    );
    """)

    # 2. Clips table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_video_id TEXT,
        clip_file TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        hashtags TEXT,
        start_time REAL DEFAULT 0.0,
        end_time REAL DEFAULT 0.0,
        duration REAL DEFAULT 0.0,
        virality_score REAL DEFAULT 0.0,
        hook_quality REAL DEFAULT 0.0,
        humor_emotion_score REAL DEFAULT 0.0,
        retention_score REAL DEFAULT 0.0,
        gaming_layout_applied INTEGER DEFAULT 0,
        invideo_enhanced INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'ready',
        created_at TEXT NOT NULL,
        FOREIGN KEY (source_video_id) REFERENCES candidates (video_id)
    );
    """)

    # 3. Upload Queue table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS upload_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clip_id INTEGER NOT NULL,
        scheduled_time TEXT NOT NULL,
        privacy_status TEXT NOT NULL DEFAULT 'private',
        status TEXT NOT NULL DEFAULT 'scheduled',
        retry_count INTEGER DEFAULT 0,
        error_message TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (clip_id) REFERENCES clips (id)
    );
    """)

    # 4. Published Videos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS published_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clip_id INTEGER NOT NULL,
        youtube_video_id TEXT NOT NULL UNIQUE,
        youtube_url TEXT NOT NULL,
        title TEXT NOT NULL,
        published_at TEXT NOT NULL,
        views_24h INTEGER DEFAULT 0,
        views_72h INTEGER DEFAULT 0,
        views_7d INTEGER DEFAULT 0,
        retention_pct REAL DEFAULT 0.0,
        FOREIGN KEY (clip_id) REFERENCES clips (id)
    );
    """)

    # 5. System Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Set initial default settings if not exists
    defaults = {
        "auto_publish_enabled": "false",
        "emergency_stop": "false",
        "topic_weights": json.dumps(TOPIC_WEIGHTS),
        "daily_candidate_target": "8",
        "daily_upload_target": "3",
        "min_spacing_hours": "4",
        "total_cost_usd": "0.0"
    }
    for k, v in defaults.items():
        cursor.execute("""
        INSERT OR IGNORE INTO system_settings (key, value, updated_at)
        VALUES (?, ?, ?)
        """, (k, v, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()

def get_setting(key: str, default: Any = None) -> Any:
    conn = get_connection()
    row = conn.execute("SELECT value FROM system_settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row:
        val = row["value"]
        if val.lower() == "true":
            return True
        if val.lower() == "false":
            return False
        try:
            return json.loads(val)
        except Exception:
            return val
    return default

def set_setting(key: str, value: Any):
    conn = get_connection()
    val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
    conn.execute("""
    INSERT INTO system_settings (key, value, updated_at)
    VALUES (?, ?, ?)
    ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
    """, (key, val_str, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def add_candidate(candidate: Dict[str, Any]) -> bool:
    conn = get_connection()
    try:
        conn.execute("""
        INSERT OR IGNORE INTO candidates (
            video_id, url, title, channel_title, category,
            view_count, view_velocity, duration_seconds,
            published_at, discovered_at, rights_status, rights_notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate["video_id"],
            candidate["url"],
            candidate["title"],
            candidate.get("channel_title", ""),
            candidate.get("category", "gaming"),
            candidate.get("view_count", 0),
            candidate.get("view_velocity", 0.0),
            candidate.get("duration_seconds", 0.0),
            candidate.get("published_at", ""),
            datetime.utcnow().isoformat(),
            candidate.get("rights_status", "PENDING_VERIFICATION"),
            candidate.get("rights_notes", ""),
            candidate.get("status", "discovered")
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding candidate: {e}")
        return False
    finally:
        conn.close()

def update_candidate_rights(video_id: str, rights_status: str, notes: str = ""):
    conn = get_connection()
    conn.execute("""
    UPDATE candidates SET rights_status = ?, rights_notes = ? WHERE video_id = ?
    """, (rights_status, notes, video_id))
    conn.commit()
    conn.close()

def update_candidate_status(video_id: str, status: str):
    conn = get_connection()
    conn.execute("""
    UPDATE candidates SET status = ? WHERE video_id = ?
    """, (status, video_id))
    conn.commit()
    conn.close()

def list_candidates(limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if category:
        rows = conn.execute("SELECT * FROM candidates WHERE category = ? ORDER BY view_velocity DESC LIMIT ?", (category, limit)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM candidates ORDER BY view_velocity DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_clip(clip: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clips (
        source_video_id, clip_file, title, description, hashtags,
        start_time, end_time, duration, virality_score,
        hook_quality, humor_emotion_score, retention_score,
        gaming_layout_applied, invideo_enhanced, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        clip.get("source_video_id"),
        clip["clip_file"],
        clip["title"],
        clip.get("description", ""),
        clip.get("hashtags", "#Shorts #GTA6 #Gaming"),
        clip.get("start_time", 0.0),
        clip.get("end_time", 0.0),
        clip.get("duration", 0.0),
        clip.get("virality_score", 0.0),
        clip.get("hook_quality", 0.0),
        clip.get("humor_emotion_score", 0.0),
        clip.get("retention_score", 0.0),
        1 if clip.get("gaming_layout_applied") else 0,
        1 if clip.get("invideo_enhanced") else 0,
        clip.get("status", "ready"),
        datetime.utcnow().isoformat()
    ))
    clip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return clip_id

def list_clips(limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM clips WHERE status = ? ORDER BY virality_score DESC LIMIT ?", (status, limit)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clips ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def enqueue_upload(clip_id: int, scheduled_time: str, privacy: str = "private") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO upload_queue (clip_id, scheduled_time, privacy_status, status, updated_at)
    VALUES (?, ?, ?, 'scheduled', ?)
    """, (clip_id, scheduled_time, privacy, datetime.utcnow().isoformat()))
    queue_id = cursor.lastrowid
    cursor.execute("UPDATE clips SET status = 'queued' WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()
    return queue_id

def list_upload_queue() -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT q.*, c.title as clip_title, c.clip_file, c.virality_score, c.hashtags
    FROM upload_queue q
    JOIN clips c ON q.clip_id = c.id
    ORDER BY q.scheduled_time ASC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def record_published(clip_id: int, youtube_video_id: str, youtube_url: str, title: str):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    cursor.execute("""
    INSERT OR REPLACE INTO published_videos (clip_id, youtube_video_id, youtube_url, title, published_at)
    VALUES (?, ?, ?, ?, ?)
    """, (clip_id, youtube_video_id, youtube_url, title, now_str))
    cursor.execute("UPDATE upload_queue SET status = 'published', updated_at = ? WHERE clip_id = ?", (now_str, clip_id))
    cursor.execute("UPDATE clips SET status = 'published' WHERE id = ?", (clip_id,))
    conn.commit()
    conn.close()

def list_published(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
    SELECT 
        p.*, 
        cand.category,
        cand.channel_title
    FROM published_videos p
    LEFT JOIN clips c ON p.clip_id = c.id
    LEFT JOIN candidates cand ON c.source_video_id = cand.video_id
    ORDER BY p.published_at DESC LIMIT ?
    """
    rows = conn.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_all_data():
    """Wipes all candidates, clips, queue, and published records to start fresh from zero."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM upload_queue")
    cursor.execute("DELETE FROM clips")
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM published_videos")
    cursor.execute("UPDATE system_settings SET value = '0' WHERE key = 'consecutive_errors'")
    cursor.execute("UPDATE system_settings SET value = '0' WHERE key = 'auto_publish_enabled'")
    conn.commit()
    conn.close()

# Initialize tables upon module load
init_db()
