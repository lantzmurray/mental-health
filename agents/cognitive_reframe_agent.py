"""Cognitive reframe agent for Project 20."""

from agents.base import run_agent_task


def reframe(session_id: str, context_data: dict) -> str:
    """Offer a more balanced interpretation of the current journal story."""
    return run_agent_task(
        session_id=session_id,
        agent_name="Cognitive Reframe Agent",
        context_data=context_data,
        objective=(
            "Identify unhelpful interpretations inside the journal entry and "
            "offer a gentler, more balanced perspective the user could try on."
        ),
        sections=[
            "Thought pattern to notice",
            "Balanced reframe",
            "Next sentence to tell yourself",
        ],
        extra_guidance=(
            "Avoid toxic positivity. Acknowledge the difficulty first, then "
            "suggest a grounded reframe and one small mindset shift."
        ),
    )
