# %%
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


def battle(prompt):
    msgs = [{"role": "user", "content": prompt}]

    a = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=msgs)

    b = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant", messages=msgs)

    return a.choices[0].message.content, b.choices[0].message.content
# …now we wrap this in Gradio with two columns + thumbs up/down 👇
