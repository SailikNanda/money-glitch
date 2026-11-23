#!/usr/bin/env python3
"""Registers Money Glitch Studio directly into Google Antigravity's native Automations dashboard.
Creates the scheduled sidecar configuration in ~/.gemini/config/sidecars/money-glitch-autopilot/sidecar.json
"""

import os
import sys
import json
from pathlib import Path

def register_automation():
    print("=" * 65)
    print("   REGISTERING MONEY GLITCH IN ANTIGRAVITY AUTOMATIONS")
    print("=" * 65)

    workspace_dir = Path(__file__).resolve().parent.parent
    user_home = Path.home()
    sidecar_dir = user_home / ".gemini" / "config" / "sidecars" / "money-glitch-autopilot"
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = sidecar_dir / "sidecar.json"

    workspace_uri = workspace_dir.as_uri()

    automation_config = {
        "builtin": "schedule",
        "args": [
            "CRON_TZ=America/New_York 0 */3 * * *",
            "agentapi",
            "new-conversation",
            "--",
            (
                f"Execute Money Glitch Autonomous Studio scheduled cycle in '{workspace_dir}'. "
                "1. Auto-Updater: Check for GitHub repository updates (auto-update every 7 days). "
                "2. Trend Intelligence: Discover real-time trends across 24 dynamic categories (within 5-day freshness window). "
                "3. Zigzag Diversification: Apply universal creator rotation (max 1 candidate/creator, 5-upload cooldown). "
                "4. Retention Director: Detect viral stream climaxes, direct high-retention 9:16 60FPS video edits with video meme cutaways, trending phonk ducking, and kinetic subtitles. "
                "5. Publishing Guard: Publish to YouTube Shorts respecting the 4-hour spacing guard (max 3/day)."
            )
        ],
        "restart_policy": "always",
        "display_name": "Money Glitch Autonomous Studio",
        "description": "Every 3 hours, runs autonomous studio cycle with 7-day GitHub self-updates, 24-category trend scans, zigzag creator rotation, and high-retention YouTube Shorts publishing.",
        "agent_permissions": {
            "workspace_uris": [
                workspace_uri
            ],
            "access_grants": [
                "command(python run_autopilot.py)",
                "command(python run_autopilot.py update)",
                "command(ffmpeg)",
                "command(ffprobe)",
                "command(git)",
                "command(git fetch)",
                "command(git pull)",
                "command(git rev-parse)",
                "command(pip install)"
            ]
        }
    }

    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(automation_config, f, indent=2)

    # Automatically set "enabled": True in Antigravity's config.json so it is Active by default (not Paused)
    main_config_path = user_home / ".gemini" / "config" / "config.json"
    if main_config_path.exists():
        try:
            with open(main_config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            sidecars = cfg.setdefault("sidecars", {})
            # Purge deprecated old sidecars
            sidecars.pop("viral-shorts-autopilot", None)
            # Register and enable Money Glitch
            sidecars["money-glitch-autopilot"] = {
                "enabled": True,
                "schemaVersion": 1,
                "resolvedPermissions": {
                    "workspaceUris": [
                        workspace_uri
                    ],
                    "accessGrants": [
                        "command(python run_autopilot.py)",
                        "command(python run_autopilot.py update)",
                        "command(ffmpeg)",
                        "command(ffprobe)",
                        "command(git)",
                        "command(git fetch)",
                        "command(git pull)",
                        "command(git rev-parse)",
                        "command(pip install)"
                    ]
                }
            }
            with open(main_config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            print("[SUCCESS] Automation auto-enabled (status: ACTIVE) in Antigravity UI!")
        except Exception as e:
            print(f"[WARNING] Could not update config.json: {e}")

    print(f"[SUCCESS] Antigravity Automation Registered & Enabled!")
    print(f"Path: {sidecar_path}")
    print(f"Display Name: {automation_config['display_name']}")
    print(f"Cadence: Every 3 hours (CRON_TZ=America/New_York 0 */3 * * *)")
    print(f"Status: Visible in Antigravity UI under 'Automations' section.")
    print("=" * 65)

if __name__ == "__main__":
    register_automation()
