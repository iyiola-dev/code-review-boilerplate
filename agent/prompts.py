"""
Agent personas, separated so agent.py stays readable.

Each specialist has a DISTINCT voice. This matters: if all three agents
read like the same prompt, the audience will wonder why we didn't just
use one agent with a bigger prompt. The voices should feel different.

Follow the codelab — you'll fill in each prompt as you go.
"""

# --- STAGE 1: Naive reviewer (already done — deliberately vague) ---------------

NAIVE_REVIEWER_INSTRUCTION = """
You are a code reviewer. Review the code the user provides and give feedback.
Cover whatever you think is important.
"""
# Deliberately vague. This is the baseline we want to improve on.


# --- STAGE 2: Specialist prompts -----------------------------------------------
# TODO: Write a SECURITY_REVIEWER_INSTRUCTION
# Give it a paranoid personality. Focus ONLY on security issues.
# Output format: SEVERITY / ISSUE / FIX

SECURITY_REVIEWER_INSTRUCTION = ""


# TODO: Write a PERFORMANCE_REVIEWER_INSTRUCTION
# Give it a Big-O obsessed personality. Focus ONLY on performance.
# Output format: IMPACT / ISSUE / FIX

PERFORMANCE_REVIEWER_INSTRUCTION = ""


# TODO: Write a STYLE_REVIEWER_INSTRUCTION
# Give it a clean-code craftsperson personality. Focus ONLY on style.
# Output format: PRIORITY / ISSUE / FIX

STYLE_REVIEWER_INSTRUCTION = ""


# --- STAGE 3: Synthesizer prompt -----------------------------------------------
# TODO: Write a SYNTHESIZER_INSTRUCTION
# This agent reads {security_findings}, {performance_findings}, {style_findings}
# from session state and merges them into one prioritized review.

SYNTHESIZER_INSTRUCTION = ""


# --- STAGE 4: Critic + Reviser prompts -----------------------------------------
# TODO: Write a CRITIC_INSTRUCTION
# This agent reads {draft_review} and either approves or sends back with objections.
# If approved, it should say "APPROVED" and call the exit_loop tool.

CRITIC_INSTRUCTION = ""


# TODO: Write a REVISER_INSTRUCTION
# This agent reads {draft_review} and {critique}, then rewrites the review.

REVISER_INSTRUCTION = ""
