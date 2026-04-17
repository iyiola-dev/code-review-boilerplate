# Code Review Crew

> A multi-agent code reviewer built with **Google ADK** and **Gemini 2.5**.
> Built live at **Build with AI Abuja · 18 April 2026**.

Three specialist agents review your code in parallel. A synthesizer merges
their findings. A critic sends it back for revision until it's ready to ship.

```
    [ Security ]
    [Performance] ──► [Synthesizer] ⇄ [Critic / Reviser loop] ──► Final review
    [   Style  ]
```

---

## What you'll build

By the end of the workshop you will have:

1. A multi-agent pipeline running locally in Cloud Shell
2. The same pipeline deployed to **Cloud Run** as a live HTTPS endpoint
3. A custom UI that streams each agent's output into its own panel

---

## Quick start (Cloud Shell)

Open Cloud Shell. Make sure a GCP project is selected (`gcloud config get-value project`).

```bash
# 1. Clone
git clone https://github.com/iyiola-dev/code-review-boilerplate.git
cd code-review-boilerplate

# 2. Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 3. Sync dependencies (reads pyproject.toml, creates .venv)
uv sync

# 4. Configure Vertex AI credentials (persistent — ADK auto-loads agent/.env)
cat > agent/.env <<EOF
GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
EOF

# 5. Try the agent locally
uv run adk web --port 8080 --allow_origins="*"
# Then click Cloud Shell's Web Preview → port 8080

# 6. Deploy to Cloud Run
./deploy.sh
```

After `./deploy.sh` finishes you'll get a URL. Open it — you'll see the
**ADK dev UI** with a chat window connected to your crew.

To use the **custom UI** instead:

```bash
# Edit ui/app.js and paste your Cloud Run URL into AGENT_URL
# Then serve the ui/ folder. From Cloud Shell Editor, right-click ui/index.html
# and pick "Preview on Port 8080", or use:
cd ui && python3 -m http.server 8080
```

---

## Repository layout

```
code-review-boilerplate/
├── agent/                      # the multi-agent system
│   ├── agent.py                # root_agent — what ADK deploys
│   ├── prompts.py              # agent personas
│   └── __init__.py
├── ui/                         # single-file frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── pyproject.toml              # uv dependencies
├── deploy.sh                   # one-shot Cloud Run deploy
└── README.md
```

---

## The four ADK patterns you'll see

This project is deliberately built to showcase every core ADK workflow primitive:

| Pattern           | Where it shows up                      | What it teaches |
|-------------------|----------------------------------------|-----------------|
| `LlmAgent`        | `naive_reviewer`, each specialist       | Single-agent baseline |
| `ParallelAgent`   | `specialist_panel`                      | Fan-out concurrent sub-agents |
| `SequentialAgent` | `root_agent`                            | Ordered pipeline with shared state |
| `LoopAgent`       | `refinement_loop` (critic ⇄ reviser)    | Iterative refinement with early exit |

---

## Cost

Cloud Run scales to zero. A full workshop demo run (~50 requests across
all attendees) typically costs **well under $1** in Vertex AI credits.
New GCP accounts get $300 in free credits.

---

## License

Apache 2.0 — use this however you like. If you give a talk based on it,
say hi to GDG Abuja.
