"""
Code Review Crew — a multi-agent code reviewer built with Google ADK.

This file is structured as four layers that build on each other.
Follow the codelab step by step: each STAGE section tells you what to add.

The exported `root_agent` at the bottom is what ADK deploys to Cloud Run.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent, LoopAgent
from google.adk.tools import exit_loop

from .prompts import (
    NAIVE_REVIEWER_INSTRUCTION,
    SECURITY_REVIEWER_INSTRUCTION,
    PERFORMANCE_REVIEWER_INSTRUCTION,
    STYLE_REVIEWER_INSTRUCTION,
    SYNTHESIZER_INSTRUCTION,
    CRITIC_INSTRUCTION,
    REVISER_INSTRUCTION,
)

MODEL = "gemini-2.5-flash"


# --- STAGE 1: The naive single reviewer ---------------------------------------
# TODO: Create a single LlmAgent called naive_reviewer
# Hint: use NAIVE_REVIEWER_INSTRUCTION, output_key="naive_review"


# --- STAGE 2: Three specialists with sharp personas ---------------------------
# TODO: Create security_reviewer, performance_reviewer, style_reviewer
# TODO: Wrap them in a ParallelAgent called specialist_panel


# --- STAGE 3: Synthesizer ----------------------------------------------------
# TODO: Create a synthesizer LlmAgent
# Hint: use SYNTHESIZER_INSTRUCTION, output_key="draft_review"


# --- STAGE 4: The critic loop ------------------------------------------------
# TODO: Create a critic LlmAgent (with tools=[exit_loop])
# TODO: Create a reviser LlmAgent
# TODO: Wrap them in a LoopAgent called refinement_loop (max_iterations=3)


# --- ROOT AGENT ---------------------------------------------------------------
# TODO: Wire up the full pipeline as root_agent
# This is the name ADK looks for when deploying.

root_agent = None  # Replace this as you work through each stage
