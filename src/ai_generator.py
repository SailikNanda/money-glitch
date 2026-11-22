"""Gemini AI Viral Content Generator for Viral Shorts Autopilot.
Uses Google Gemini 2.5 Flash to generate high-CTR hook titles,
SEO descriptions, viral hashtags, and meme pacing cues.
"""

import os
import re
import json
import logging
import requests
from typing import Dict, Any, Optional

from .config import GOOGLE_API_KEY

logger = logging.getLogger("AIGenerator")
logging.basicConfig(level=logging.INFO)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

class ViralAIGenerator:
    def __init__(self):
        self.api_key = GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY", "")

    def analyze_stream_viral_climax(
        self,
        transcript_or_description: str,
        video_duration_seconds: float = 600.0,
        streamer_name: str = "Streamer",
        game_topic: str = "GTA 6"
    ) -> Dict[str, Any]:
        """
        Uses Gemini 2.5 Flash LLM reasoning to detect the viral climax, exact punchline/scream timestamp,
        and pattern interrupt editing cues.
        """
        fallback = {
            "start_time": max(0, int(video_duration_seconds * 0.25)),
            "duration": 30.0,
            "climax_second": 14.0,
            "hook_title": f"HE BROKE {game_topic.upper()}! 💀",
            "emphasis_keywords": ["BROKE", "INSANE", "NO WAY"],
            "meme_sfx": "vine_boom",
            "virality_score": 93.5
        }

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. Using fallback moment.")
            return fallback

        prompt = f"""You are the Antigravity AI Autonomous Video Director.
Analyze this livestream stream context and identify the single most viral 30-45 second Shorts clip:
Streamer: {streamer_name}
Topic: {game_topic}
Video Duration: {video_duration_seconds}s
Context/Transcript:
{transcript_or_description[:2000]}

Identify:
1. "start_time": Best second to start the clip (integer between 0 and {int(video_duration_seconds - 35)}).
2. "duration": Float between 25.0 and 40.0.
3. "climax_second": Exact second inside the clip (e.g. 14.0) where streamer screams or climax hits.
4. "hook_title": Punchy all-caps curiosity-gap hook title (max 45 chars, e.g. "HE BROKE GTA 6! 💀").
5. "emphasis_keywords": Array of 3-5 punchy words to highlight in bright neon on screen.
6. "meme_sfx": Sound effect cue ("vine_boom", "wasted", or "emotional_damage").
7. "virality_score": Predicted virality rating between 85.0 and 98.0.

Return ONLY a valid JSON object.
"""
        for attempt in range(3):
            try:
                url = f"{GEMINI_API_URL}?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7}
                }
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    match = re.search(r"\{.*\}", text, re.DOTALL)
                    if match:
                        result = json.loads(match.group(0))
                        logger.info(f"LLM Climax Detected: '{result.get('hook_title')}' @ {result.get('start_time')}s")
                        return result
            except Exception as e:
                logger.warning(f"LLM Climax Detection attempt {attempt+1} error: {e}")

        return fallback

    def generate_shorts_metadata(
        self,
        video_title: str,
        topic: str = "GTA 6",
        channel_name: str = ""
    ) -> Dict[str, Any]:
        """
        Generates click-worthy hook title, full YouTube Shorts description,
        and trending hashtags using Gemini 2.5 Flash.
        """
        fallback = {
            "hook_title": f"WAIT TILL THE END IN {topic.upper()}! 💀",
            "description": f"Most insane {topic} moment ever! Credit: {channel_name}\n\nSubscribe for daily viral gaming moments! #Shorts #{topic.replace(' ', '')} #Gaming #Viral",
            "hashtags": f"#Shorts #{topic.replace(' ', '')} #Gaming #Trending #ViralShorts",
            "meme_cue": "vine_boom"
        }

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. Using fallback metadata.")
            return fallback

        prompt = f"""You are an elite viral YouTube Shorts strategist and meme creator.
Target Audience: United States gaming & internet culture audience.
Primary Topic: {topic}
Source Video Title: "{video_title}"
Original Channel: "{channel_name}"

Generate high-CTR, algorithm-friendly YouTube Shorts metadata.
Output format: JSON object with the following fields:
- "hook_title": Punchy, high curiosity gap, maximum 45 characters, capital letters, with 1 emoji (e.g. "HE BROKE GTA 6! 💀").
- "description": 2 engaging sentences describing the crazy moment, giving credit to {channel_name}, and call to action.
- "hashtags": String of 5-7 viral hashtags separated by spaces (must include #Shorts #GTA6 #Gaming).
- "meme_cue": One chosen sound effect: "vine_boom", "wasted", or "emotional_damage".

Return ONLY the JSON. No conversational text.
"""

        for attempt in range(3):
            try:
                url = f"{GEMINI_API_URL}?key={self.api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7
                    }
                }
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Extract JSON if enclosed in markdown
                    match = re.search(r"\{.*\}", text, re.DOTALL)
                    if match:
                        json_str = match.group(0)
                        metadata = json.loads(json_str)
                        # Standardize hashtags if array
                        if isinstance(metadata.get("hashtags"), list):
                            metadata["hashtags"] = " ".join(metadata["hashtags"])
                        logger.info(f"Generated AI Viral Hook: {metadata.get('hook_title')}")
                        return metadata
                    else:
                        logger.warning("Could not find JSON pattern in response.")
                        return fallback
                else:
                    logger.warning(f"Gemini API returned status {res.status_code}: {res.text[:200]}")
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt+1} failed: {e}")
                import time
                time.sleep(1)

        logger.error("All Gemini API attempts failed. Using fallback metadata.")
        return fallback
