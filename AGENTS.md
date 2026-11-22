# Google Antigravity Agent Directive — Money Glitch Autonomous Studio

> **[IMPORTANT] Antigravity Exclusive Protocol:**
> This repository is exclusively engineered for **Google Antigravity**. When a user gives you this repository link (`https://github.com/SailikNanda/money-glitch.git`) and says **"Use this"**, **"Run this"**, or **"Start"**, execute the complete Turnkey Autopilot Runbook below. Do not ask redundant questions or request manual JSON configuration.

---

## Turnkey Autopilot Runbook (Zero-Touch Onboarding)

When triggered with `"Use this"` or `"Run this"`, Antigravity MUST execute these 4 phases sequentially:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 1: Environment & Dependency Auto-Setup                          │
│  - Install requirements.txt, ensure FFmpeg, init SQLite DB             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 2: Browser Autonomous Google Cloud & OAuth Credential Setup     │
│  - Control browser on Google Cloud Console                             │
│  - Enable YouTube Data API v3, create Desktop OAuth Client             │
│  - Save credentials directly to data/client_secrets.json               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 3: Launch Studio Dashboard & Channel Connection                 │
│  - Start FastAPI studio dashboard on http://127.0.0.1:8501             │
│  - Instruct user to click 'Connect Channel' once to link YouTube       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 4: Autonomous Production, Dynamic Copywriting & Publishing      │
│  - Trend research (GTA 6, IShowSpeed, Kai Cenat, viral gaming)         │
│  - Dynamic climax & scream detection (video-specific, not templates)   │
│  - 100% unique titles, tailored descriptions, non-repetitive hashtags  │
│  - Retention editing (3.5s zooms, kinetic subtitles, OLED saturation)  │
│  - Paced YouTube Shorts publishing (max 3/day, 4-hour spacing guard)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Environment & Dependency Auto-Setup
Run the following commands using `run_command`:
```powershell
pip install -r requirements.txt
python -c "from src.db import init_db; init_db(); print('Database Initialized')"
```
Verify that `ffmpeg` and `ffprobe` are available on PATH.

---

### Phase 2: Autonomous Google Cloud OAuth Setup (Browser Control)
If `data/client_secrets.json` does NOT already exist, invoke the Antigravity `browser` subagent to configure Google Cloud on the user's logged-in browser session:

1. **Navigate to Google Cloud Console**:
   - URL: `https://console.cloud.google.com/projectcreate`
   - If prompted, create project name: `Money Glitch Studio`. Click **Create**.
2. **Enable YouTube Data API v3**:
   - URL: `https://console.cloud.google.com/apis/library/youtube.googleapis.com`
   - Click the blue **ENABLE** button.
3. **Configure OAuth Consent Screen**:
   - URL: `https://console.cloud.google.com/apis/credentials/consent`
   - Select User Type: **External** -> Click **Create**.
   - App name: `Money Glitch Studio`.
   - User support email: Select current user email.
   - Developer contact email: Enter current user email.
   - Click **Save and Continue** through Scopes and Test Users (add user email to test users if in testing mode).
4. **Create OAuth Client ID**:
   - URL: `https://console.cloud.google.com/apis/credentials/oauthclient`
   - Application type: Select **Desktop app**.
   - Name: `Money Glitch Desktop Client`.
   - Click **Create**.
5. **Download Credentials**:
   - In the pop-up or credentials list, click **DOWNLOAD JSON**.
   - Save the downloaded file directly to: `data/client_secrets.json` in this workspace.

---

### Phase 3: Launch Studio Dashboard & Register Antigravity Automation
1. Launch the background daemon server and auto-open the dashboard UI:
   ```powershell
   python run_autopilot.py dashboard --port 8501 --open
   ```
   *(This launches the FastAPI studio and automatically opens `http://127.0.0.1:8501` in the user's default browser so they immediately see the live Studio UI).*
2. Automatically register this studio in Antigravity's native Automations section:
   ```powershell
   python scripts/register_antigravity_automation.py
   ```
   *(Creates `~/.gemini/config/sidecars/money-glitch-autopilot/sidecar.json` so it appears in the Antigravity UI sidebar under 'Automations').*
3. Notify the user:
   > "Studio Dashboard is live at `http://127.0.0.1:8501` (opened in your browser) and registered in your Antigravity **Automations** tab. Please click **[Connect Channel]** in the header once to link your YouTube channel (or approve the Google Sign-In tab). Everything else will run on complete autopilot!"
4. Once the user completes the Google Sign-In, `data/youtube_token.json` is generated.

---

### Phase 4: Autonomous Production, Zigzag Diversification & Publishing
Antigravity acts as the Supreme Content Director and Executive Producer:

1. **Universal 24-Category Real-Time Discovery (Zero Hardcoded Channels)**:
   - **Never hardcode just one creator, one game, or a fixed list of channels.** There are millions of creators on YouTube; all gameplay and content are judged on their own virality and entertainment value.
   - Dynamically discover real-time trends across **24 distinct categories**:
     - **Gaming (8 Categories)**: Open-world chaos (GTA 6/RDR2), FPS/Esports clutches (Valorant/Warzone), survival traps (Minecraft/Rust), horror jumpscares (Lethal Company/FNAF), physics destruction (BeamNG/Teardown), gamer rage & instant karma, souls-like boss fights (Elden Ring), and breakout viral indie games.
     - **Movies & Cinema (5 Categories)**: Blockbuster trailers, epic action & car chases, anime fight climaxes (4K 60fps), mind-bending plot twists, and chilling soundtrack visual drops.
     - **Sports & Athletics (6 Categories)**: NBA buzzer beaters & ankle breaker dunks, UFC/boxing knockout finishes, Champions League/Premier League golazos, extreme Red Bull stunts, NFL impossible catches, and supercar drifts.
     - **Viral Internet & Culture (5 Categories)**: 1-in-a-million lucky saves, futuristic robotics/tech leaks, clever pets & wild animal feats, satisfying restorations (ASMR), and public street trivia.
2. **Balanced Creator Sampling & Anti-Monotony Protocol**:
   - **Famous & Trending Priority**: Higher view-velocity trending videos receive primary priority weight.
   - **Anti-Monotony Exploration**: Random sampling jitter (+0 to +15 pts) is applied across search results so breakout clips from small/medium creators compete fairly with mega-channels.
   - **Max 1 Candidate Per Channel Per Batch**: Prevents any single channel from dominating discovery results.
3. **Zigzag Creator & Topic Rotation Protocol**:
   - **Strict Rule:** Never publish the same creator or the same category consecutively.
   - The engine checks recent uploads and enforces a heavy penalty if a channel was featured in the last 5 uploads.
   - Cycles across categories and creators in a dynamic zigzag rotation to keep channel engagement at peak levels.
4. **Dynamic Climax Reasoning (No Generic Presets)**:
   - Analyze each video individually: audio pitch, streamer scream timestamps, crowd reactions, and action peaks.
   - Set optimal 25–35s duration with climax placed at 55%–65% through the clip for maximum retention.
5. **100% Unique Copywriting & Dynamic Hashtags**:
   - **Never copy-paste identical hashtags across videos.**
   - Tailor tags to specific creator, specific sport/movie/game, and specific action (`#PoliceEscape`, `#BuzzerBeater`, `#GamingRage`, `#MovieClips`, `#Shorts`).
   - Create curiosity-gap hook titles matching the exact scene event.
6. **Retention Engine Execution**:
   - 3.5s pattern interrupt cadence (Punch-In 1.18x zooms + voice peak camera shakes).
   - Kinetic `.ass` subtitles in 9:16 safe zone with Neon Yellow (`#FACC15`) active word highlights.
   - Mobile OLED saturation boost (`eq=saturation=1.28:contrast=1.06`).
   - Smart audio sidechain ducking (-40% under speech, swelling on climax drops).
7. **Publishing Guard & Continuous Lifecycle**:
   - Upload through `src/youtube_uploader.py` honoring the 4-hour spacing window and maximum 3 uploads/day limit.
   - **Lifecycle Management:** Runs continuously (`python run_autopilot.py daemon`) as long as the PC is turned ON. When the PC shuts down, execution halts safely with SQLite persistence. When the PC turns on, it seamlessly resumes from where it left off!
