# Future — AI Agents on AWS

Hands-on masterclass code. Build agents with the AWS Strands SDK on Amazon Bedrock.

**Open `GUIDE.html` in your browser first** — that's the full teaching companion, with diagrams, explanations, and a copy-paste run command after every concept.

---

## Quick start

### 1. Install

```bash
./setup.sh          # macOS / Linux
setup.bat           # Windows
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. AWS credentials

**Option A — temporary SSO credentials (easiest).** In the AWS access portal → your account → _Command line or programmatic access_ → copy the block and paste into your terminal:

```bash
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION=us-east-1
```

These expire after a few hours — paste a fresh block when they do. They also apply only to the terminal you paste them into.

**Option B — permanent IAM key.** Run `aws configure`.

### 3. Enable the models

AWS console → **Bedrock** → **Model access** (region **us-east-1**) → enable:

- Claude Haiku 4.5
- Amazon Nova Lite
- Claude Sonnet 4.5 _(optional)_

### 4. Verify

```bash
python 00_check_setup.py
```

Checks Python, packages, credentials, region, Bedrock — **and makes a real model call**. If it passes, every lesson will run. If not, it prints the exact fix.

---

## Running the lessons

Run everything **from this folder** (the one with `config.py`), not from inside `getting_started_examples/`.

### Module 1 — first agents

```bash
python getting_started_examples/01_hello_world_agent.py        # simplest agent, no tools
python getting_started_examples/02_hello_world_langgraph.py    # with a tool — watch the loop
```

### Module 2 — tools

```bash
python strands_tool_examples/01_function_to_tool.py         # THE core idea: @tool
python strands_tool_examples/02_tip_calculator.py           # first useful tool agent
python strands_tool_examples/03_multi_tool_sales.py         # 3 tools, agent picks the order
python strands_tool_examples/04_custom_tool_inventory.py    # build your own tool
python strands_tool_examples/05_prebuilt_tools.py           # community tools + system prompt
python strands_tool_examples/06_multi_prebuilt_tools.py     # combining several tools
python strands_tool_examples/07_use_aws.py                  # one tool, many AWS services
python strands_tool_examples/08_class_based_tools.py        # shared-resource pattern
python strands_tool_examples/09_async_tools.py              # parallel tools: 2s not 6s
```

### Module 3 — capstone

```bash
python travel_assitant_capstone_project/travel_assistant.py

# or ask your own question:
python travel_assitant_capstone_project/travel_assistant.py "I'm going to Manali for 4 days, budget 15000"
```

---

## Two experiments worth doing in class

**1. Break a docstring.** In `strands_tool_examples/01_function_to_tool.py`, change the tool's docstring to just `"""Does a thing."""` and re-run. The agent often stops calling the tool. The docstring isn't a comment — it's the manual the _model_ reads to decide if your tool is relevant.

**2. Watch the loop.** Run `getting_started_examples/02_hello_world_langgraph.py` and look at the empty `ai:` line. That's the model choosing to _use a tool_ instead of answering. That is the agentic loop.

---

## Changing the model

All lessons import from `config.py`. Change it once there:

```python
MODEL_ID = os.environ.get("MODEL_ID", HAIKU)   # swap HAIKU → SONNET or NOVA_LITE
```

Or per-run:

```bash
export MODEL_ID="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
```

---

## Troubleshooting

| Error                                                                            | Fix                                                                                    |
| -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `ResourceNotFoundException ... end of its life` / `marked by provider as Legacy` | Model retired. Run `python 01_list_models.py`, pick a live one, set it in `config.py`. |
| `AccessDeniedException`                                                          | Model not enabled in Bedrock → Model access, or wrong region.                          |
| `ExpiredToken` / `InvalidClientTokenId`                                          | Credentials expired. Paste a fresh SSO block, or re-run `aws configure`.               |
| `ModuleNotFoundError: No module named 'strands'`                                 | Virtual env not active: `source .venv/bin/activate`.                                   |
| `ModuleNotFoundError: No module named 'config'`                                  | You ran from inside a subfolder. Run from this folder instead.                         |
| Script seems to hang                                                             | A tool is waiting for consent — type `y` and press Enter.                              |
| Works in one terminal, not another                                               | Credentials are per-terminal. Paste them again.                                        |
| Worked yesterday, fails today                                                    | Almost always expired credentials. Run `python 00_check_setup.py`.                     |

**Note:** if `AWS_ACCESS_KEY_ID` etc. are set as environment variables, they _override_ anything saved by `aws configure`. Diagnose with:

```bash
env | grep AWS
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
```

---

## Cost

Everything runs on your laptop and calls Bedrock per request. All lessons together cost **a fraction of a cent**. Nothing runs in the background — nothing to shut down.

---

## Files

```
.
├── GUIDE.html            ← open this first
├── README.md
├── config.py             ← model IDs — change once, applies everywhere
├── requirements.txt
├── setup.sh / setup.bat
├── 00_check_setup.py     ← run this first
├── 01_list_models.py     ← when a model is retired
├── getting_started_examples/             ← Module 1 · 2 lessons
├── strands_tool_examples/             ← Module 2 · 9 lessons
└── travel_assitant_capstone_project/             ← Module 3 · capstone
```
