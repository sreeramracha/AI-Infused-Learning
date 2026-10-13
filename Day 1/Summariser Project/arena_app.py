# pip install openai gradio python-dotenv
import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

groq_client = OpenAI(api_key=os.getenv("GROQ_API_KEY"),
                     base_url="https://api.groq.com/openai/v1")


def ask(client, model, prompt):
    r = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content


def battle(prompt):
    a = ask(groq_client, "llama-3.3-70b-versatile", prompt)
    b = ask(groq_client, "llama-3.1-8b-instant", prompt)
    return a, b


def vote(label):
    # in real apps, save this to a file/DB
    return f"🗳️ Thanks! You voted: **{label}**"


with gr.Blocks(title="LLM Arena") as demo:
    gr.Markdown("# 🥊 LLM Arena — one prompt, two models")
    prompt = gr.Textbox(label="Ask both models the same thing")
    go = gr.Button("⚔️ Battle!", variant="primary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🤖 Model A")
            out_a = gr.Markdown()
            with gr.Row():
                up_a = gr.Button("👍")
                down_a = gr.Button("👎")
        with gr.Column():
            gr.Markdown("### 🤖 Model B")
            out_b = gr.Markdown()
            with gr.Row():
                up_b = gr.Button("👍")
                down_b = gr.Button("👎")

    verdict = gr.Markdown()

    go.click(battle, inputs=prompt, outputs=[out_a, out_b])
    up_a.click(lambda: vote("👍 Model A"), outputs=verdict)
    down_a.click(lambda: vote("👎 Model A"), outputs=verdict)
    up_b.click(lambda: vote("👍 Model B"), outputs=verdict)
    down_b.click(lambda: vote("👎 Model B"), outputs=verdict)

# demo.launch(share=True)   # → local + public link 🎉
demo.launch()  # → local only
