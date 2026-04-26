"""Wellness tracker agent for Project 20."""

from agents.base import run_agent_task


def track_wellness(session_id: str, context_data: dict) -> str:
    """Translate the journal entry into practical habits and trend signals."""
    return run_agent_task(
        session_id=session_id,
        agent_name="Wellness Tracker Agent",
        context_data=context_data,
        objective=(
            "Highlight the habit or pattern worth tracking next and suggest "
            "small wellness actions the user can realistically try."
        ),
        sections=[
            "Pattern to track",
            "Supportive habits for today",
            "Tomorrow check-in prompt",
        ],
        extra_guidance=(
            "Favor lightweight actions like sleep, movement, hydration, social "
            "support, or boundaries. Do not position the output as medical care."
        ),
    )
