import whisper
import yt_dlp
import os
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("YT_Shorts_Generator/.env")

class Main:
    def __init__(self):
        # Load environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.encoding = tiktoken.get_encoding("cl100k_base")

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
    
    def transcribe_audio_with_timestamps(self, audio_file, model_size="medium"):
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
            model="gpt-4o",
            instructions="You are a helpful assistant.",
            input=prompt,
            max_output_tokens=2000,
        )

        return response.output_text
    
    def get_timestampes_of_clips(self, transcript: str) -> str:

        prompt = f"""
        You are a YouTube Shorts Creator expert, and you are provided with a transcript of a podcast episode.
        Your task is to extract the most interesting parts of the podcast and provide timestamps for each clip.
        Note:
            - Each clip can be at max 60 seconds long.
            - Search for any Main Introduction or Hook or a Joke or a Story or a sequence of Jokes or events that can be used as a clip.
            - Note the clip should be interesting, engaging and self-contained.
            - The clips should be suitable for a YouTube Shorts video / TikTok / Instagram Reels.
            - Provide the timestamps in the format: [start_time, end_time].
        The output should be in JSON format.
        Timestamps , Small description of the clip and Title of the clip.
        
        Here is the transcript:{transcript}
        """
        
        prompt1 = f"""
        You are an expert YouTube Shorts creator and video content editor. You have been given the transcript of a podcast episode. 
        Your job is to extract multiple short, high-impact, and engaging clips that are suitable for YouTube Shorts, TikTok, or Instagram Reels.

        Guidelines:
        - Each clip must be **between 40 and 60 seconds**.
        - Focus on capturing moments that are:
            - **Attention-grabbing** (e.g., hooks, bold statements, punchlines)
            - **Emotionally engaging** (e.g., inspiring, funny, surprising, controversial)
            - **Self-contained** (should make sense even without full podcast context)
            - **Viral-worthy** (likely to resonate with short-form content audiences)
        - Look for:
            - A powerful **introduction or hook**
            - **Jokes**, **stories**, **insightful tips**, or **sequences of interesting events**
            - Clips that either entertain, educate, or intrigue

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
        Now, based on the following transcript, extract as many engaging clips as possible:

        Transcript: {transcript} 
        """
        response = self.get_response_from_openai(prompt=prompt1)
        print("Response from OpenAI:", response)
        return response


# --------- MAIN EXECUTION ---------

if __name__ == "__main__":
    #yt_url = input("Enter YouTube podcast video URL: ")
    yt_url = "https://www.youtube.com/watch?v=u4xvQnu535s"
    audio_file = "podcast_audio"

    main = Main()

    audio_path = main.download_youtube_audio(yt_url, output_file=audio_file)
    transcript_segments = main.transcribe_audio_with_timestamps("podcast_audio.mp3")
    main.save_transcript_to_file(transcript_segments)

    # # Read the transcript from the file
    # with open("t1.txt", "r", encoding="utf-8") as f:
    #     transcript = f.read()

    # num_tokens = main.count_tokens(transcript)
    # print(f"Number of tokens in the transcript: {num_tokens}")

    # main.get_timestampes_of_clips(transcript=transcript)

    #Get high quality transcript
    # Automate to cut the clips from the video