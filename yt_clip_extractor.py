import os
import subprocess
from yt_dlp import YoutubeDL


class YouTubeClipExtractor:
    def __init__(self, ffmpeg_path: str = "C:/ffmpeg/ffmpeg-2025-03-31-git-35c091f4b7-full_build/bin/ffmpeg.exe", clip_output_dir: str = "clips"):
        self.ffmpeg_path = ffmpeg_path
        self.ffmpeg_dir = os.path.dirname(ffmpeg_path)
        self.clip_output_dir = clip_output_dir
        os.makedirs(self.clip_output_dir, exist_ok=True)

    def download_video(self, url: str, output_filename: str = "downloaded_video.mp4") -> str:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_filename,
            'ffmpeg_location': self.ffmpeg_dir,
            'quiet': False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            print("📥 Downloading video...")
            ydl.download([url])

        print(f"✅ Downloaded to: {output_filename}")
        return output_filename

    def cut_clip(self, input_file: str, start: int, end: int, clip_index: int = 0) -> str:
        output_file = os.path.join(self.clip_output_dir, f"clip_{clip_index}_{start}-{end}.mp4")

        cmd = [
            self.ffmpeg_path,
            '-y',  # Overwrite
            '-i', input_file,
            '-ss', str(start),
            '-to', str(end),
            '-c', 'copy',
            output_file
        ]

        print(f"✂️ Cutting {start}s to {end}s -> {output_file}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"🎬 Clip saved: {output_file}")

        return output_file

    def extract_clips(self, video_path: str, timestamps: list[tuple[int, int]]) -> list[str]:
        clips = []
        for idx, (start, end) in enumerate(timestamps):
            clip = self.cut_clip(video_path, start, end, idx)
            clips.append(clip)
        return clips
