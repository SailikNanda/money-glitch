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

### Phase 3: Launch Studio Dashboard & Connect Channel
1. Launch the background daemon server:
   ```powershell
   python run_autopilot.py dashboard --port 8501
   ```
2. Notify the user:
   > "Studio Dashboard is live at `http://127.0.0.1:8501`. Please click **[Connect Channel]** in the header once to link your YouTube channel (or approve the Google Sign-In tab). Everything else will run on complete autopilot!"
3. Once the user completes the Google Sign-In, `data/youtube_token.json` is generated.

---

### Phase 4: Autonomous Production, Zigzag Diversification & Publishing
Antigravity acts as the Supreme Content Director and Executive Producer:

1. **Universal Real-Time Trend Discovery (No Hardcoded Niches/Streamers)**:
   - **Never hardcode just one game or one creator.**
   - Dynamically scan whatever is truly trending in real time across 4 core verticals:
     - **Gaming**: Top viral streamers (IShowSpeed, Kai Cenat, Jynxzi, Fanum, Sketch, xQc, etc.) and trending titles (GTA 6, Fortnite, Valorant, Call of Duty, Minecraft).
     - **Movies & Cinema**: Trending official movie trailers, box office hype, anime battle climaxes, blockbuster pop culture.
     - **Sports & Athletics**: Viral NBA buzzer beaters, UFC knockouts, Champions League / Premier League goals, crazy athletic moments.
     - **Viral Internet News & Culture**: Real-time breaking internet debates, viral memes, and high-velocity social phenomena.
2. **Zigzag Creator & Topic Rotation Protocol (Creator Diversity)**:
   - **Strict Rule:** Never publish the same streamer or sub-topic consecutively.
   - Execute a smart **Zigzag Rotation**:
     - Day 1: IShowSpeed (Gaming)
     - Day 2: Kai Cenat (Gaming) or Trending Movie Trailer Climax (Cinema)
     - Day 3: Jynxzi (Gaming) or Viral NBA/UFC KO (Sports)
     - Day 4: Fanum / Sketch (Gaming) or Viral Internet Phenomenon (Trends)
     - Day 5: Return to IShowSpeed after full diverse rotation!
   - This keeps the channel's audience engaged, broadens algorithmic reach, and prevents creator fatigue.
3. **Dynamic Climax Reasoning (No Generic Presets)**:
   - Analyze each video individually: audio pitch, streamer scream timestamps, crowd reactions, and action peaks.
   - Set optimal 25–35s duration with climax placed at 55%–65% through the clip for maximum retention.
4. **100% Unique Copywriting & Dynamic Hashtags**:
   - **Never copy-paste identical hashtags across videos.**
   - Tailor tags to specific creator, specific sport/movie/game, and specific action (`#PoliceEscape`, `#BuzzerBeater`, `#GamingRage`, `#MovieClips`, `#Shorts`).
   - Create curiosity-gap hook titles matching the exact scene event.
5. **Retention Engine Execution**:
   - 3.5s pattern interrupt cadence (Punch-In 1.18x zooms + voice peak camera shakes).
   - Kinetic `.ass` subtitles in 9:16 safe zone with Neon Yellow (`#FACC15`) active word highlights.
   - Mobile OLED saturation boost (`eq=saturation=1.28:contrast=1.06`).
   - Smart audio sidechain ducking (-40% under speech, swelling on climax drops).
6. **Publishing Guard & Continuous Lifecycle**:
   - Upload through `src/youtube_uploader.py` honoring the 4-hour spacing window and maximum 3 uploads/day limit.
   - **Lifecycle Management:** Runs continuously (`python run_autopilot.py daemon`) as long as the PC is turned ON. When the PC shuts down, execution halts safely with SQLite persistence. When the PC turns on, it seamlessly resumes from where it left off!
