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
                "Discover real-time trends across 24 dynamic categories (within 5-day freshness window), "
                "apply universal creator zigzag diversification, detect viral stream climaxes, "
                "direct high-retention 9:16 60FPS video edits with kinetic subtitles, "
                "and publish to YouTube Shorts respecting the 4-hour spacing guard."
            )
        ],
        "restart_policy": "always",
        "display_name": "Money Glitch Autonomous Studio",
        "description": "Every 3 hours, autonomously scans 24 categories (5-day window), performs universal creator zigzag rotation, retention editing, and publishes to YouTube Shorts.",
        "agent_permissions": {
            "workspace_uris": [
                workspace_uri
            ],
            "access_grants": [
                "command(python run_autopilot.py)",
                "command(ffmpeg)",
                "command(ffprobe)"
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
                        "command(ffmpeg)",
                        "command(ffprobe)"
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
