# AI Engineering · Class 2 — LangChain & Your First Agent (runnable code)

Every file here matches a code block from the Class 2 deck. They are
self-contained — run any one of them directly.

## One-time setup
```bash
# 1. create & activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. install everything
pip install -r requirements.txt

# 3. add your key
#    copy .env.example to a file named .env, then paste your OpenAI key inside
cp .env.example .env            # Windows: copy .env.example .env
```
Get a key at https://platform.openai.com/api-keys (add a little billing credit).

## What to run (in deck order)
| File | What it shows | Run |
|------|---------------|-----|
| `scraper.py` | Class 1 helper: URL -> page text | `python scraper.py` |
| `summarizer_langchain.py` | Block 10 — summarizer rebuilt in LangChain (prompt \| model \| parser) | `python summarizer_langchain.py` |
| `memory_demo.py` | Block 10 — memory with history typed by hand | `python memory_demo.py` |
| `memory_chat.py` | Block 10 — memory that builds itself in a chat loop | `python memory_chat.py` |
| `agent.py` | Block 11 — your first tool-using agent | `python agent.py` |
| `app.py` | Block 12 — the agent with a Gradio chat UI + public link | `python app.py` |

## Notes
- All files use the cheap `gpt-4o-mini` model.
- `summarizer_langchain.py` imports `fetch_website_contents` from `scraper.py`,
  so keep them in the same folder.
- `app.py` imports `agent` from `agent.py` — same folder.
- Never commit `.env`. A `.gitignore` is included that already ignores it.

## Stop a running app
Press `Ctrl + C` in the terminal.
