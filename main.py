"""
Production entry point for the Code Review Crew Cloud Run service.

We use `get_fast_api_app()` directly instead of `adk deploy cloud_run` because
the latter has no `--allow_origins` flag (see
https://github.com/google/adk-python/issues/1444). The custom UI in `ui/` runs
on a different origin (localhost during the workshop, or any static host in
production), so CORS must be enabled here.
"""

import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Directory that contains the `agent/` subfolder (which has agent.py +
# __init__.py exposing `root_agent`). For this project that's the repo root.
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Allow any origin. Fine for the workshop / a public demo. In production,
# replace with a concrete list of your frontend origins.
ALLOW_ORIGINS = ["*"]

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=ALLOW_ORIGINS,
    web=True,  # also mount the ADK dev UI at /dev-ui — handy for debugging.
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
