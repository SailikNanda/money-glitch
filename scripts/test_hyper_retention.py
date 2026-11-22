import subprocess
import os

test_in = "clips/exports/short_eHqRX-qBdL4_1_0s.mp4"
test_out = "clips/exports/test_hyper_retention.mp4"
meme_video = "assets/memes/walter_fall.mp4"
sfx = "assets/vine_boom.mp3"
phonk = "assets/audio/trending_phonk.mp3"

climax_t = 14.0
meme_dur = 2.0
climax_ms = int(climax_t * 1000)

filter_complex = (
    "[0:v]eq=saturation=1.45:contrast=1.15:brightness=0.01[v_col];"
    "[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black[meme_v];"
    f"[v_col][meme_v]overlay=0:0:enable='between(t,{climax_t},{climax_t + meme_dur})'[v_meme];"
    f"[v_meme]drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':text='WHAT JUST HAPPENED?!':fontsize=64:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-text_w)/2:y=1600:enable='between(t,{climax_t},{climax_t + meme_dur})'[vout];"
    "[2:a]aloop=loop=-1:size=2e+09,volume=0.22,atrim=0:22[bg_m];"
    f"[1:a]adelay={climax_ms}|{climax_ms},volume=2.2[m_a];"
    f"[3:a]adelay={climax_ms}|{climax_ms},volume=2.0[sfx_a];"
    "[0:a][bg_m][m_a][sfx_a]amix=inputs=4:duration=first:dropout_transition=2,aformat=sample_rates=48000:channel_layouts=stereo[aout]"
)

cmd = [
    "ffmpeg", "-y",
    "-t", "22",
    "-i", test_in,
    "-i", meme_video,
    "-i", phonk,
    "-i", sfx,
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    test_out
]

print("Executing test rendering...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"SUCCESS! Output size: {os.path.getsize(test_out)} bytes")
else:
    print(f"FFmpeg error:\n{res.stderr[-600:]}")
