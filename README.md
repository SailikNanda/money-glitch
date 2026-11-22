# Viral Shorts Autopilot 🎬🚀

Autonomous YouTube Shorts Clipping, Invideo Polish & Scheduled Publishing System built on **Google Antigravity**.

- **Focus**: GTA 6 (Grand Theft Auto VI) at 60% priority, Gaming & Streamers (25%), US Internet Trends (15%).
- **Language & Region**: American English, targeting United States YouTube audience.
- **Cadence**: Every 3 hours (`CRON_TZ=America/New_York 0 */3 * * *`).
- **Pacing**: Up to 5–10 eligible candidate clips daily, ~3 published Shorts daily with a minimum 4-hour gap.

---

## Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │   Antigravity Scheduled Automation     │
                      │  (Every 3 Hours - America/New_York)    │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │        YouTube Trend Discovery         │
                      │ (GTA 6 60%, Gaming 25%, Viral US 15%)  │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │       Rights & Source Validation       │
                      │ (CC-BY, Whitelist, Manual Verification)│
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │  SupoClip Viral Moment & Gaming Layout │
                      │  (Facecam Top, Gameplay, HUD Preserve) │
                      │       1080x1920 9:16 60FPS MP4         │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │        Invideo Advanced Polish         │
                      │ (Color Grading, Transitions, Audio)    │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │     Publishing Queue & Upload Guard    │
                      │  (Pacing: 4h Gap, Max 3/Day, Safety)   │
                      └──────────────────┬─────────────────────┘
                                         │
                                         ▼
                      ┌────────────────────────────────────────┐
                      │   Official YouTube Data API v3 Upload  │
                      │    (OAuth 2.0, Hook Frame, Attribution)│
                      └────────────────────────────────────────┘
```

---

## 1. Directory Structure

- `src/`
  - `config.py`: Core configuration, topic weights, quotas, and environment paths.
  - `db.py`: SQLite persistence (`data/autopilot.db`) for candidates, clips, queue, and published history.
  - `rights_validator.py`: Gatekeeper ensuring no media is republished without verified permissions.
  - `trend_discovery.py`: High-velocity trend scanner across YouTube Data API v3 and public sources.
  - `clipping_engine.py`: SupoClip-powered viral moment analysis and 9:16 gaming layout rendering.
  - `invideo_enhancer.py`: Invideo CLI integration and video spec verification.
  - `youtube_uploader.py`: Official Google OAuth 2.0 uploader with channel confirmation.
  - `scheduler.py`: Autonomous orchestrator with America/New_York timezone pacing.
  - `dashboard.py`: FastAPI real-time web control center.
- `templates/dashboard.html`: Tailwind CSS responsive operator dashboard.
- `clips/exports/`: Rendered 1080x1920 vertical Shorts.
- `run_autopilot.py`: Master CLI entrypoint.

---

## 2. CLI Usage

```bash
# 1. Start the Web Dashboard (Control Center)
python run_autopilot.py dashboard --port 8501

# 2. Check System Status & Queue
python run_autopilot.py status

# 3. Run Trend Discovery
python run_autopilot.py discover --limit 3

# 4. Generate Shorts from a Source Video
python run_autopilot.py clip --source "s:/Money Glitch/clips/raw_clip_3.webm" --id "gta6_rage" --topic "GTA 6"

# 5. Execute One Autonomous Pipeline Iteration
python run_autopilot.py cycle

# 6. Authenticate YouTube Channel (One-time Google OAuth)
python run_autopilot.py auth-youtube
```

---

## High-Retention AI Video Editing Suite ⚡

The system features an autonomous retention psychology engine (`src/retention_editor.py` & `skills/viral-shorts-editor/`):
- **Pattern Interrupt Micro-Zooms**: Alternates between 1.0x and 1.15x dynamic punch-ins every 3.5 seconds via FFmpeg mathematical zoom graphs to eliminate viewer drop-off.
- **Mobile OLED Vibrancy Tuning**: Automatically boosts saturation (+25%) and micro-contrast for smartphone displays with subtle unsharp masking.
- **Kinetic Typography (SubStation Alpha .ass)**: Word-level active highlighted subtitles positioned strictly in the YouTube Shorts safe zone (`MarginV=320px`).
- **Smart Sidechain Audio Ducking**: Dips background phonk/music tracks by -40% (-6dB) under voice dialogue and restores volume during hype gameplay climaxes.
- **Auto-Silence Jump Cuts**: Strips dead air longer than 350ms to sustain rapid-fire storytelling pacing.

---

## 3. Web Dashboard

Launch on `http://127.0.0.1:8501`:
- **Live Status Bar**: Channel identity, daily upload pacing (e.g. `0 / 3 Shorts`), and total AI cost ($0.00).
- **Controls**:
  - `Run Discovery & Clipping`: Instant manual trigger.
  - `Auto-Publish ON/OFF`: Safety toggle. Default is OFF until explicitly enabled.
  - `Emergency Stop`: Immediate pipeline freeze.
  - `Submit Authorized Source`: Direct video ingest for instant clipping.
- **Candidate Rights Gate**: Authorize trending clips with 1 click.
- **Published Shorts Table**: Direct links to published YouTube Shorts.

---

## 4. Connecting Your YouTube Channel

1. Place your Google Cloud OAuth Client credentials JSON file at:
   `s:\Money Glitch\data\client_secrets.json`
2. Run:
   ```bash
   python run_autopilot.py auth-youtube
   ```
3. A local browser tab will open for official Google consent. The token is safely saved in `data/youtube_token.json` (no passwords stored).
