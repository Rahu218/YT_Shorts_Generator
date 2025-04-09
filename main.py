import whisper
import yt_dlp
from yt_dlp import YoutubeDL

import os
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
import json
from yt_clip_extractor import YouTubeClipExtractor

load_dotenv("YT_Shorts_Generator/.env")

class Main:
    def __init__(self, yt_url):
        # Load environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.yt_url = yt_url
        self.description = ""

        # Downloaf the video
        extractor1 = YouTubeClipExtractor()
        downloaded_video = extractor1.download_video(yt_url, output_filename="downloaded_video.mp4")
        
        self.downloaded_video_path = downloaded_video +".webm"

    # --------- Video download and Transcription Function ---------
    # Video download and Transcription
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
        # Load the Whisper model
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

    def get_video_description(self) -> str:
        url = self.yt_url

        ydl_opts = {
            'quiet': True,
            'skip_download': True,  # No need to download video
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            description = info_dict.get('description', '')
        
        # print(f"Video description: {description}")

        # token_count = self.count_tokens(description)
        # print(f"Number of tokens in video description: {token_count}")
        self.description = description

        return description

    # --------- Extracting Content With Time Stamps for Storts video ---------
    def count_tokens(self, text):
        # Encode text to get token IDs
        tokens = self.encoding.encode(text)
        return len(tokens)
    
    def get_response_from_openai(self, prompt: str) -> str:

        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        response = client.responses.create(
            model="gpt-4",
            instructions="You are a helpful assistant.",
            input=prompt,
            max_output_tokens=2000,
        )

        return response.output_text
    
    def get_timestampes_of_clips(self, transcript: str) -> str:

        prompt1 = f"""
        You are an expert YouTube Shorts creator and video content editor. You have been given the transcript of a podcast episode along with its description.
        Your job is to extract multiple short, hilarious, high-impact, and engaging clips that are suitable for YouTube Shorts, TikTok, or Instagram Reels.
        
        **Guidelines**:
        - Each clip must be **between 40 and 70 seconds**.
        - Each clip should start at a **natural conversational transition**, not mid-sentence or mid-thought.
        - Prioritize including the **setup** (especially for jokes or stories) and the **punchline** or reaction (laughter, shock, etc.) — even if that means adding a few extra seconds.
        - Favor starting a few seconds *before* the exciting moment and ending a few seconds *after* for better flow.
        - Focus on capturing moments/seqences of events that are:
            - **Funny** (e.g., jokes, humorous anecdotes, funny stories)
            - **Attention-grabbing** (e.g., hooks, bold statements, punchlines)
            - **Emotionally engaging** (e.g., funny, surprising, controversial)
            - **Self-contained** (should make sense even without full podcast context)
            - **Viral-worthy** (likely to resonate with short-form content audiences)
        - Look for:
            - A powerful **introduction or hook**
            - **Jokes**,**Unexpected Statemnets**, **Mockery** or **sequences of interesting events**

            
        Output Format:
        Return the output as a **JSON array**, where each object contains:
        - `"title"`: A catchy, clickable title for the clip (max 10 words)
        - `"description"`: 1-2 sentence summary of the clip’s content
        - `"timestamps"`: A list in the format `[start_time, end_time]` (e.g., `["00:02:13", "00:02:59"]`)

        Example:
        ```json
        [
        {{
            "title": "Why Most People Fail at Habits",
            "description": "The guest explains a powerful mindset shift about habit formation.",
            "timestamps": ["00:04:21", "00:05:15"]
        }},
        ...
        ]
        '''
        **Important**: The duration of each clip should be more than 40 seconds and less than 70 seconds. Each clip should be self-contained and engaging.

        Now, based on the following transcript, extract as many engaging clips as possible:

        **Description**: {self.description}

        **Transcript**: {transcript} 
        """
        response = self.get_response_from_openai(prompt=prompt1)
        
        with open("res1.txt", "w", encoding="utf-8") as f:
            f.write(response)
        
        list1 = self.convert_to_dist(response)

        return list1

    def convert_to_dist(self, response: str) -> list:

        lines = response.split("\n")
        json_lines = []

        hit = False
        for line in lines:
            if line.strip() == "[":
                hit = True
                json_lines.append(line)
                continue
            if hit:
                json_lines.append(line)
                if line.strip() == "]":
                    break

        # Convert the json_lines to a list of dictionaries
        json_string = '\n'.join(json_lines)
        try:
            clips = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            clips = []

        return clips
    
    def timestamp_to_seconds(self, ts: str) -> int:
        h, m, s = map(int, ts.split(":"))
        return h * 3600 + m * 60 + s

    def get_clips(self, clips: list):
        
        # create the output directory if it doesn't exist
        if not os.path.exists('clips'):
            os.makedirs('clips')

        self.get_video_description()

        # # Initialize the extractor
        extractor = YouTubeClipExtractor()

        # # Step 1: Download video
        # downloaded_video = extractor.download_video(yt_url, output_filename="downloaded_video.mp4")
        # print(downloaded_video)

        timestamps = []
        for dist1 in clips:
            timestamps.append((self.timestamp_to_seconds(dist1["timestamps"][0]), self.timestamp_to_seconds(dist1["timestamps"][1])))

        print(timestamps)
        
        clip_paths = extractor.extract_clips(self.downloaded_video_path, timestamps)

        print("✅ All clips saved:")
        for path in clip_paths:
            print(" -", path)
            
        return None 




# --------- MAIN EXECUTION ---------

if __name__ == "__main__":
    #yt_url = input("Enter YouTube podcast video URL: ")
    yt_url = "https://www.youtube.com/watch?v=u4xvQnu535s"
    audio_file = "podcast_audio"

    main = Main(yt_url)

    # audio_path = main.download_youtube_audio(yt_url, output_file=audio_file)
    # transcript_segments = main.transcribe_audio_with_timestamps("podcast_audio.mp3")
    # main.save_transcript_to_file(transcript_segments)

    # Read the transcript from the file
    with open("t1.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    num_tokens = main.count_tokens(transcript)
    print(f"Number of tokens in the transcript: {num_tokens}")

    list1 = main.get_timestampes_of_clips(transcript=transcript)

    main.get_clips(list1)

    