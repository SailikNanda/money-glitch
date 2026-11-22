---
name: viral-trend-research-intelligence
description: Autonomous real-time trend discovery, view-velocity scoring, 24-category diversification, creator anti-monotony jitter, and zigzag rotation for YouTube Shorts.
version: 1.0.0
author: Antigravity AI
---

# Viral Trend Research & Intelligence Skill

This skill governs the autonomous research, evaluation, and selection of raw video content across YouTube, ensuring high viral probability and channel growth while preventing creator monotony.

---

## 1. 24 Dynamic Category Taxonomy

Never hardcode single creators or repetitive queries. Content is rotated through **24 distinct high-velocity categories**:

### Gaming (8 Categories)
1. **Open-World Chaos**: GTA 6, GTA 5, Red Dead Redemption 2, Cyberpunk.
2. **FPS & Esports Clutches**: Valorant, Warzone, Apex Legends, CS2.
3. **Survival Traps**: Minecraft hardcore, Rust base raids, DayZ.
4. **Horror Jumpscares**: Lethal Company, Five Nights at Freddy's, Phasmophobia.
5. **Physics Destruction**: BeamNG.drive crash physics, Teardown, Garry's Mod.
6. **Gamer Rage & Karma**: Streamer desk smashes, instant karma moments.
7. **Souls-Like Boss Battles**: Elden Ring, Dark Souls, Black Myth: Wukong.
8. **Breakout Indie Viral Games**: Lethal Company, Content Warning, Palworld.

### Movies & Cinema (5 Categories)
9. **Blockbuster Trailers**: Marvel, DC, Nolan films, IMAX teasers.
10. **Epic Action & Car Chases**: John Wick, Fast & Furious, Mission Impossible.
11. **Anime Fight Climaxes (4K 60fps)**: Jujutsu Kaisen, Demon Slayer, Attack on Titan.
12. **Mind-Bending Plot Twists**: Interstellar, Fight Club, Inception.
13. **Soundtrack Visual Drops**: Epic Hans Zimmer & Ludwig Göransson bass drops.

### Sports & Athletics (6 Categories)
14. **NBA Buzzer Beaters & Dunks**: Ankle breakers, half-court game winners.
15. **UFC & Boxing Knockout Finishes**: Highlight reel KOs, spinning back kicks.
16. **Champions League & Premier League Golazos**: Screamer goals, solo runs.
17. **Extreme Red Bull Stunts**: Wingsuit proximity flying, cliff diving.
18. **NFL Impossible Catches**: One-handed sideline catches, touchdown scrambles.
19. **Supercar Drifts & Touge**: Mountain passes, track records.

### Viral Internet & Culture (5 Categories)
20. **1-in-a-Million Lucky Saves**: Dashcam close calls, unbelievable luck.
21. **Futuristic Robotics & Tech Leaks**: Boston Dynamics, humanoid robotics.
22. **Clever Pets & Wild Animals**: High IQ pets, funny animal interactions.
23. **Satisfying Restorations (ASMR)**: Deep cleaning, vintage watch restorations.
24. **Public Street Trivia**: High-energy cash trivia challenges.

---

## 2. Real-Time Freshness & View Velocity Scoring

The discovery engine filters out stale content:
- **Freshness Window**: Published within the last 5 days.
- **View Velocity Equation**:
  $$\text{Velocity} = \frac{\text{View Count}}{\max(\text{Hours Since Published}, 1)}$$
- **High-Velocity Threshold**: Priority is awarded to clips exceeding 5,000 views/hour.

---

## 3. Anti-Monotony Exploration Protocol

To ensure small and medium breakout creators compete fairly with mega-channels:
- **Random Sampling Jitter**: `+0` to `+15` points is added to velocity scores across the candidate pool.
- **Max 1 Candidate Per Channel Per Batch**: Prevents any single channel from dominating discovery results.

---

## 4. Universal Zigzag Creator & Topic Rotation

- **Strict Alternation**: Never publish the same creator or the same category consecutively.
- **5-Upload Cooldown**: If a channel was featured in any of the last 5 uploads in the SQLite database (`data/money_glitch.db`), a -50 point penalty is applied.
- **Category Balancing**: Rotates Gaming $\to$ Cinema $\to$ Sports $\to$ Viral Culture sequentially.
