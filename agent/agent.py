"""
Code Review Crew — a multi-agent code reviewer built with Google ADK.

This file is structured as four layers that build on each other. When teaching,
you can start with only STAGE 1 uncommented, demo it, then peel back each
`# --- STAGE N ---` block in turn. Attendees can follow along by copy-pasting
each stage into their own file.

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
# One agent, one prompt, tries to do everything. This is our baseline.
# On stage: deploy this, paste the vulnerable login() function, show the output.
# It will usually miss at least one of the three bugs, or flag them too briefly.
# That's the setup: "one agent isn't enough. Let's fix that."

naive_reviewer = LlmAgent(
    name="NaiveReviewer",
    model=MODEL,
    instruction=NAIVE_REVIEWER_INSTRUCTION,
    description="A single generalist reviewer. Our baseline.",
    output_key="naive_review",
)


# --- STAGE 2: Three specialists with sharp personas ---------------------------
# Each agent has ONE job and a distinct personality. Run in parallel because
# they don't depend on each other's output. Key teaching point: the specialists
# share session state but write to DIFFERENT output_keys — no race conditions.

security_reviewer = LlmAgent(
    name="SecurityReviewer",
    model=MODEL,
    instruction=SECURITY_REVIEWER_INSTRUCTION,
    description="Paranoid security specialist. Thinks about auth, injection, secrets.",
    output_key="security_findings",
)

performance_reviewer = LlmAgent(
    name="PerformanceReviewer",
    model=MODEL,
    instruction=PERFORMANCE_REVIEWER_INSTRUCTION,
    description="Performance hawk. Thinks about complexity, N+1, memory.",
    output_key="performance_findings",
)

style_reviewer = LlmAgent(
    name="StyleReviewer",
    model=MODEL,
    instruction=STYLE_REVIEWER_INSTRUCTION,
    description="Style pedant. Thinks about naming, structure, docstrings.",
    output_key="style_findings",
)

specialist_panel = ParallelAgent(
    name="SpecialistPanel",
    description="Runs all three specialist reviewers simultaneously.",
    sub_agents=[security_reviewer, performance_reviewer, style_reviewer],
)


# --- STAGE 3: Synthesizer merges findings into one prioritized review ---------
# This agent reads from session.state via {placeholder} templating — no
# manual passing of data. The synthesizer is where the "team" becomes a
# "report." It's the first time the audience sees agents truly collaborate.

synthesizer = LlmAgent(
    name="Synthesizer",
    model=MODEL,
    instruction=SYNTHESIZER_INSTRUCTION,
    description="Merges the three specialist reviews into a prioritized report.",
    output_key="draft_review",
)


# --- STAGE 4: The critic loop — the crescendo --------------------------------
# The critic reads the synthesized review and either approves it or rejects it
# with specific objections. If rejected, the reviser rewrites. If approved, the
# critic calls the built-in `exit_loop` tool to bail out of the LoopAgent.
#
# This is THE pattern that justifies ADK over a vanilla chain of Gemini calls.
# Agents genuinely iterate on each other's output. Audience should feel this click.

critic = LlmAgent(
    name="Critic",
    model=MODEL,
    instruction=CRITIC_INSTRUCTION,
    description="Stress-tests the draft review. Approves or sends back for revision.",
    tools=[exit_loop],  # so the critic can end the loop early when satisfied
    output_key="critique",
)

reviser = LlmAgent(
    name="Reviser",
    model=MODEL,
    instruction=REVISER_INSTRUCTION,
    description="Rewrites the review based on the critic's objections.",
    output_key="draft_review",  # overwrites the draft each iteration
)

refinement_loop = LoopAgent(
    name="RefinementLoop",
    description="Critic ↔ Reviser. Iterates until critic approves or 3 rounds pass.",
    sub_agents=[critic, reviser],
    max_iterations=3,
)


# --- ROOT AGENT: what ADK deploys --------------------------------------------
# The full pipeline: specialists in parallel → synthesizer → critic/reviser loop.
# This is `root_agent` because that's the name ADK looks for when deploying.

root_agent = SequentialAgent(
    name="CodeReviewCrew",
    description=(
        "A multi-agent code reviewer. Three specialists review in parallel, "
        "a synthesizer merges their findings, and a critic/reviser loop "
        "polishes the final review."
    ),
    sub_agents=[specialist_panel, synthesizer, refinement_loop],
)
