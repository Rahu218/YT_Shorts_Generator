import whisper
import yt_dlp
import os

class Main:
    def download_youtube_audio(self, url, output_file="podcast_audio.mp3"):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio...")
            ydl.download([url])
        
        return output_file

    def transcribe_audio_with_timestamps(self, audio_file, model_size="base"):
        model = whisper.load_model(model_size)
        print("Transcribing...")
        result = model.transcribe(audio_file)

        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        return segments

    def save_transcript_to_file(self, transcript_segments, output_file="transcript_with_timestamps.txt"):
        with open(output_file, "w", encoding="utf-8") as f:
            for seg in transcript_segments:
                start = self.format_timestamp(seg['start'])
                end = self.format_timestamp(seg['end'])
                f.write(f"[{start} --> {end}] {seg['text']}\n")
        print(f"Transcript saved to {output_file}")

    def format_timestamp(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

# --------- MAIN EXECUTION ---------

if __name__ == "__main__":
    #yt_url = input("Enter YouTube podcast video URL: ")
    audio_file = "podcast_audio.mp3"

    main = Main()

    #audio_path = main.download_youtube_audio(yt_url, output_file=audio_file)
    audio_path = "podcast_audio.mp3"
    transcript_segments = main.transcribe_audio_with_timestamps(audio_path)
    main.save_transcript_to_file(transcript_segments)
