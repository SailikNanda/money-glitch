#!/usr/bin/env python3
"""Master CLI Entrypoint for Viral Shorts Autopilot.
Project: Viral Shorts Autopilot
Target Audience: United States (American English)
Primary Content Priority: GTA 6 (Grand Theft Auto VI)
"""

import sys
import argparse
import uvicorn
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.db import init_db, list_candidates, list_clips, list_upload_queue, list_published, get_setting
from src.trend_discovery import TrendDiscoveryEngine
from src.clipping_engine import ClippingEngine
from src.scheduler import AutonomousScheduler
from src.youtube_uploader import YouTubeUploader

def main():
    init_db()

    parser = argparse.ArgumentParser(description="Viral Shorts Autopilot CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: discover
    p_disc = subparsers.add_parser("discover", help="Run YouTube trend discovery")
    p_disc.add_argument("--limit", type=int, default=3, help="Max candidates per category")

    # Command: clip
    p_clip = subparsers.add_parser("clip", help="Run viral moment clipping on a video")
    p_clip.add_argument("--source", type=str, required=True, help="Path or URL to source video")
    p_clip.add_argument("--id", type=str, default="manual_test", help="Identifier for source")
    p_clip.add_argument("--topic", type=str, default="GTA 6", help="Topic name")
    p_clip.add_argument("--title", type=str, default="GTA 6 VIRAL CLIP", help="Clip hook title prefix")

    # Command: cycle
    p_cycle = subparsers.add_parser("cycle", help="Execute one full autonomous iteration")

    # Command: daemon (Continuous Autonomous Engine)
    p_daemon = subparsers.add_parser("daemon", help="Run continuous background autonomous loop whenever PC is on")
    p_daemon.add_argument("--interval", type=int, default=1800, help="Heartbeat check interval in seconds (default: 1800s)")

    # Command: dashboard
    p_dash = subparsers.add_parser("dashboard", help="Start the FastAPI web control center")
    p_dash.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    p_dash.add_argument("--port", type=int, default=8501, help="Port to listen on")
    p_dash.add_argument("--open", dest="open_browser", action="store_true", help="Automatically open dashboard in web browser")

    # Command: status
    p_status = subparsers.add_parser("status", help="Print system status and queue")

    # Command: auth-youtube
    p_auth = subparsers.add_parser("auth-youtube", help="Run Google OAuth 2.0 flow to connect YouTube channel")

    # Command: update
    p_upd = subparsers.add_parser("update", help="Check and apply GitHub updates for Money Glitch Studio")
    p_upd.add_argument("--check-only", action="store_true", help="Only check for updates without pulling")
    p_upd.add_argument("--force", action="store_true", help="Force check ignoring 7-day interval")

    args = parser.parse_args()

    if args.command == "discover":
        engine = TrendDiscoveryEngine()
        results = engine.run_discovery_cycle(max_per_category=args.limit)
        print(f"\n[OK] Trend discovery completed. Found {len(results)} candidate videos.\n")

    elif args.command == "clip":
        engine = ClippingEngine()
        clips = engine.process_video_to_shorts(
            source_path=args.source,
            source_video_id=args.id,
            topic=args.topic,
            clip_title_prefix=args.title
        )
        print(f"\n[OK] Clipping completed. Produced {len(clips)} vertical Shorts.\n")

    elif args.command == "cycle":
        scheduler = AutonomousScheduler()
        res = scheduler.run_full_pipeline_iteration()
        print("\n=======================================================")
        print("   VIRAL SHORTS AUTOPILOT - CYCLE EXECUTION REPORT")
        print("=======================================================")
        print(f"Timestamp:             {res.get('timestamp')}")
        print(f"Candidates Discovered: {res.get('discovered')}")
        print(f"Eligible Authorized:   {res.get('authorized_eligible')}")
        print(f"Clips Generated:       {res.get('clips_generated')}")
        for cl in res.get("generated_clips", []):
            print(f"  -> [{cl.get('virality_score')}/100] {cl.get('title')} ({cl.get('duration')}s) - {cl.get('file')}")
        print(f"Auto-Publish Enabled:  {res.get('auto_publish_enabled')}")
        pacing = res.get("pacing", {})
        print(f"Upload Pacing Window:  {'OPEN' if pacing.get('can_upload') else 'BLOCKED'}")
        print(f"Pacing Status:         {pacing.get('wait_reason')}")
        print(f"Daily Cap / Spacing:   Max {pacing.get('daily_max')}/day, min {pacing.get('min_spacing_hours')}h between uploads")
        print(f"Uploads Published:     {res.get('uploaded')}")
        if res.get("upload_error"):
            print(f"Upload Status Notice:  {res.get('upload_error')}")
        print("=======================================================\n")

    elif args.command == "daemon":
        scheduler = AutonomousScheduler()
        print(f"\n[STARTING] Money Glitch Continuous Autonomous Daemon (Heartbeat: {args.interval}s)")
        print("Autonomous Lifecycle: Runs whenever PC is ON. Halts cleanly when PC is OFF. Resumes on reboot.\n")
        scheduler.run_continuous_daemon(check_interval_seconds=args.interval)

    elif args.command == "status":
        auto_pub = get_setting("auto_publish_enabled", False)
        emergency_stop = get_setting("emergency_stop", False)
        candidates = list_candidates()
        clips = list_clips()
        queue = list_upload_queue()
        published = list_published()

        print("\n=== VIRAL SHORTS AUTOPILOT STATUS ===")
        print(f"Auto-Publish: {'ON' if auto_pub else 'OFF'}")
        print(f"Emergency Stop: {'ACTIVE' if emergency_stop else 'OFF'}")
        print(f"Total Discovered Candidates: {len(candidates)}")
        print(f"Generated Shorts: {len(clips)}")
        print(f"Publishing Queue: {len(queue)}")
        print(f"Published Shorts: {len(published)}\n")

    elif args.command == "auth-youtube":
        uploader = YouTubeUploader()
        success = uploader.authenticate_interactive()
        if success:
            info = uploader.get_channel_info()
            print(f"\n[OK] Connected to channel: {info.get('channel_title')} (ID: {info.get('channel_id')})\n")
        else:
            print("\n[ERROR] YouTube OAuth authentication failed or client_secrets.json is missing.\n")

    elif args.command == "update":
        from src.auto_updater import get_auto_updater
        updater = get_auto_updater()
        if args.check_only:
            res = updater.check_for_updates()
            print("\n=========================================")
            print("   MONEY GLITCH GITHUB UPDATE CHECK")
            print("=========================================")
            print(f"Status:          {res.get('status')}")
            print(f"Local Commit:    {res.get('local_commit')}")
            print(f"Remote Commit:   {res.get('remote_commit')}")
            print(f"Commits Behind:  {res.get('behind_count', 0)}")
            print(f"Update Ready:    {'YES' if res.get('update_available') else 'NO (Up to date)'}")
            if res.get("commits"):
                print("New Commits on GitHub:")
                for c in res.get("commits", []):
                    print(f"  * {c}")
            print("=========================================\n")
        else:
            res = updater.check_and_auto_update_if_due(interval_days=7, force=args.force)
            print("\n=========================================")
            print("   MONEY GLITCH 7-DAY AUTO-UPDATER")
            print("=========================================")
            print(f"Status:   {res.get('status')}")
            print(f"Message:  {res.get('message')}")
            if res.get("update_applied"):
                print(f"Updated from {res.get('previous_commit')} -> {res.get('new_commit')}")
                print(f"Latest Commit Message: {res.get('commit_message')}")
            elif res.get("remaining_days") is not None:
                print(f"Days until next scheduled check: {res.get('remaining_days')} days")
            print("=========================================\n")

    elif args.command == "dashboard":
        print(f"\n[STARTING] Viral Shorts Autopilot Dashboard on http://{args.host}:{args.port}\n")
        if getattr(args, "open_browser", False):
            import threading
            import webbrowser
            threading.Timer(1.0, lambda: webbrowser.open(f"http://{args.host}:{args.port}")).start()
        uvicorn.run("src.dashboard:app", host=args.host, port=args.port, reload=False)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
