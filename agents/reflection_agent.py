"""Reflection agent for Project 20.

This agent reuses the summarization habit from earlier projects, but applies it
to emotional journaling so the user gets a grounded read on what they are
experiencing before any coaching or habit tracking starts.
"""

from agents.base import run_agent_task


def reflect(session_id: str, context_data: dict) -> str:
    """Turn the current mood + journal entry into an empathetic reflection."""
    return run_agent_task(
        session_id=session_id,
        agent_name="Reflection Agent",
        context_data=context_data,
        objective=(
            "Summarize the user's mood and journal entry into a calm emotional "
            "snapshot that feels supportive, specific, and easy to act on."
        ),
        sections=[
            "Emotional snapshot",
            "Themes and triggers",
            "Supportive reflection",
        ],
        extra_guidance=(
            "Name likely feelings and patterns without sounding clinical or "
            "diagnostic. Keep the tone warm, grounded, and practical."
        ),
    )
