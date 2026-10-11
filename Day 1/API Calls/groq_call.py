# %%

# pip install openai   (yes — the same library!)
from pathlib import Path
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# point the SAME client at Groq instead of OpenAI 👇
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response1 = client.chat.completions.create(
    # model="llama-3.3-70b-versatile",        # a free Llama model on Groq
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a witty travel guide."},
        {"role": "user",   "content": "Suggest one thing to do in Bangalore."},
    ],

)
print(response1.choices[0].message.content)

response2 = client.chat.completions.create(
    model="openai/gpt-oss-20b",        # a free Llama model on Groq
    messages=[
        {"role": "system", "content": "You are a witty travel guide."},
        {"role": "user",   "content": "Suggest one thing to do in Bangalore."},
    ],

)
print(response2.choices[0].message.content)
# %%
