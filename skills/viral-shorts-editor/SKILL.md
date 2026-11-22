---
name: viral-shorts-editor
description: Autonomous high-retention video editing framework for viral YouTube Shorts, TikTok, and Instagram Reels. Uses FFmpeg, OpenCV, and kinetic typography.
version: 1.0.0
author: Antigravity AI
---

# Viral Shorts High-Retention Video Editor Skill

This skill provides the autonomous AI agent with programmatic blueprints, FFmpeg filtergraphs, and retention algorithms for producing top 1% viral vertical short-form videos (1080x1920 @ 60 FPS).

---

## 1. The Core Retention Laws (Viewer Psychology)

1. **The 3-Second Hook Rule:**
   - 65% of viewers swipe away within the first 1.8 seconds if the visual or auditory state is static.
   - *Implementation:* The first frame MUST start immediately on high energy (no silence, no intros). An eye-catching kinetic headline must be present on Frame 0.

2. **Pattern Interrupt Cadence (Every 2.5–3.5 Seconds):**
   - The human brain habituates to fixed framing after ~3 seconds.
   - *Implementation:* Alternate between Wide (1.0x), Punch-In Zoom (1.15x–1.25x), and subtle camera shakes on voice inflection peaks.

3. **Safe Zone Layout for 9:16 Shorts:**
   - **Top 15% (0–280px):** Safe for Facecam top panel, scoreboards, or streamer reactions.
   - **Center 60% (280–1450px):** Main action focus (gameplay, scene, face focus).
   - **Bottom 25% (1450–1920px):** Danger zone! YouTube Shorts UI overlays (Channel avatar, title, sound name, Like/Comment/Share buttons) cover this area.
   - *Rule:* Subtitles must be centered at `MarginV=300px` from the bottom to remain 100% visible and unblocked.

4. **Audio Mastering & Sidechain Ducking:**
   - Voice is King: Streamer/voice clarity must dominate.
   - Background Music (Phonk/Hype): Sidechain compressed by -40% (-6dB) under voice, swelling during gameplay climaxes.
   - Loudness Target: -14.0 LUFS integrated, -1.0 dB true peak.

---

## 2. Advanced FFmpeg Filtergraphs

### A. Dynamic Punch-In Zoom (Pattern Interrupt)
```bash
ffmpeg -i input.mp4 -vf "scale=8000:-2,zoompan=z='if(between(it,2.5,4.0)+between(it,7.5,9.0),1.18,1.0)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=60" -c:v libx264 -preset fast -crf 18 output.mp4
```

### B. Mobile OLED Vibrancy & Edge Sharpening
```bash
ffmpeg -i input.mp4 -vf "eq=saturation=1.28:contrast=1.06:brightness=0.01,unsharp=5:5:0.7:5:5:0.3" -c:v libx264 -c:a copy output.mp4
```

### C. Sidechain Audio Compression (Automatic Phonk Ducking)
```bash
ffmpeg -i voice.wav -i music.mp3 -filter_complex "[1:a]asplit=2[sc][mus];[0:a][sc]sidechaincompress=threshold=0.08:ratio=4:attack=20:release=250[ducked];[0:a][ducked]amix=inputs=2:duration=first" -c:a aac -b:a 192k output.m4a
```

---

## 3. Kinetic Subtitle Specs (Hormozi / MrBeast Style)

- **Font:** Impact or Montserrat Black (Heavy, readable at 0.5x speed).
- **Style:** Uppercase, 2–3 words per line max.
- **Coloring:** Primary White (`#FFFFFF`), Active Spoken Word highlighted in Neon Yellow (`#FACC15`) or Electric Cyan (`#06B6D4`).
- **Stroke & Shadow:** 4.5px Black Outline (`#000000`) with 2px soft shadow for high contrast on any background.

---

## 4. Automation Checklist for AI Agent

- [x] Auto-detect silences > 350ms and jump-cut dead air.
- [x] Split landscape gameplay and facecam into 9:16 dual-panel layout.
- [x] Insert Vine Boom bass drops and camera shakes on climactic events.
- [x] Burn kinetic subtitles in safe zone.
- [x] Export H.264 High Profile @ 60 FPS 1080x1920.
