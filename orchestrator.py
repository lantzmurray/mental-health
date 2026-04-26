"""Orchestrator for Project 20.

The later School of AI projects should feel like intentional extensions of the
multi-agent work from projects 11-13. This orchestrator keeps that shape:
capture the input once, run focused agents in sequence, and preserve a readable
collaboration log for demos and future Signal City use.
"""

import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.base import generate_session_id, log_agent_response
from agents.reflection_agent import reflect
from agents.cognitive_reframe_agent import reframe
from agents.wellness_tracker_agent import track_wellness

AGENT_SEQUENCE = (
    ("Reflection Agent", reflect),
    ("Cognitive Reframe Agent", reframe),
    ("Wellness Tracker Agent", track_wellness),
)


class Orchestrator:
    """Run the mental-health support workflow in a predictable order."""

    def generate_session_id(self) -> str:
        """Expose short ids for the frontend and game-facing tooling."""
        return generate_session_id()

    def run_workflow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run every specialist agent and return both outputs and session id."""
        session_id = self.generate_session_id()
        results = {}

        # Log the user input once so the collaboration history tells a complete story.
        input_snapshot = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value or 'Not provided'}"
            for key, value in inputs.items()
        )
        log_agent_response(
            session_id,
            "Workflow Input",
            input_snapshot,
            {"kind": "input"},
        )

        for agent_name, agent_runner in AGENT_SEQUENCE:
            results[agent_name] = agent_runner(session_id, inputs)

        return {"session_id": session_id, "results": results}
