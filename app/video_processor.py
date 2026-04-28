import os
import uuid
import shutil

import yt_dlp
import whisper

# Auto-detect FFmpeg for local + Render
# 1) Use env variable if provided
# 2) Use system ffmpeg if installed
# 3) Fallback to Windows path

DEFAULT_WINDOWS_FFMPEG = r"C:\Users\Oruganti Veerababu\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"

FFMPEG_PATH = os.getenv("FFMPEG_PATH")

if not FFMPEG_PATH:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        FFMPEG_PATH = os.path.dirname(system_ffmpeg)
    else:
        FFMPEG_PATH = DEFAULT_WINDOWS_FFMPEG

os.environ["PATH"] += os.pathsep + FFMPEG_PATH


def download_audio(video_url: str) -> str:
    """Download audio from any video URL"""
    output_path = f"temp_audio_{uuid.uuid4().hex}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path + ".%(ext)s",
        "ffmpeg_location": FFMPEG_PATH,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return f"{output_path}.mp3"


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio to text using Whisper"""
    print("🎙️ Transcribing audio... please wait")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass

    return result["text"]


def process_video(video_url: str) -> str:
    """Main function - download + transcribe"""
    print("⬇️ Downloading video audio...")
    audio_path = download_audio(video_url)

    print("🎙️ Transcribing...")
    transcript = transcribe_audio(audio_path)

    print("✅ Done!")
    return transcript
