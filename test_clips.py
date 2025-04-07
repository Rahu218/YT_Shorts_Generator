from yt_clip_extractor import YouTubeClipExtractor

def timestamp_to_seconds(ts: str) -> int:
    h, m, s = map(int, ts.split(":"))
    return h * 3600 + m * 60 + s


# Set your YouTube URL and desired timestamps here
yt_url = "https://www.youtube.com/watch?v=u4xvQnu535s"
timestamps = [
    (timestamp_to_seconds("00:05:00"), timestamp_to_seconds("00:05:55"))
]

# Initialize the extractor
extractor = YouTubeClipExtractor()

# Step 1: Download video
#downloaded_video = extractor.download_video(yt_url, output_filename="downloaded_video.mp4")

downloaded_video = "downloaded_video.mp4.webm"
# Step 2: Extract clips
clip_paths = extractor.extract_clips(downloaded_video, timestamps)

print("✅ All clips saved:")
for path in clip_paths:
    print(" -", path)
