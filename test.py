import os
from dotenv import load_dotenv
import openai
from openai import OpenAI

load_dotenv("YT_Shorts_Generator/.env")

# print(os.getenv("openai_key"))

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define a function to chat with an OpenAI model
def get_response_from_openai(prompt: str) -> str:

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a helpful assistant.",
        input=prompt,
        max_output_tokens=9000,
    )

    return response.output_text

prompt = "Generate a script for a YouTube short about the benefits of meditation."

res1 = get_response_from_openai(prompt=prompt)
print(res1)
