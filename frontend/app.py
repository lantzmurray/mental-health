import streamlit as st
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_ROOT = os.path.dirname(os.path.dirname(PROJECT_ROOT))
sys.path.insert(0, PROJECT_ROOT)
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from agents.base import get_session_history
from orchestrator import Orchestrator
from components import render_app_footer, run_with_status_updates

st.set_page_config(page_title="Mental Health Companion Agents", layout="wide")


def render_session_log(session_id: str) -> None:
    """Show the collaboration history so the workflow is teachable in demos."""
    history = get_session_history(session_id)
    if not history:
        return

    st.subheader("Collaboration Log")
    for entry in history:
        timestamp = entry["timestamp"].replace("T", " ")
        with st.expander(f"{entry['agent']} · {timestamp}", expanded=False):
            st.markdown(entry["content"])


def main():
    st.title("Mental Health Companion Agents")
    st.caption(
        "Create a journaling + coaching assistant for emotional well-being."
    )

    st.sidebar.title("Check-In")
    daily_mood = st.sidebar.text_input(
        "Daily Mood",
        placeholder="Anxious but still motivated",
    )
    journal_entry = st.text_area(
        "Journal Entry",
        height=220,
        placeholder="Write a few sentences about what happened today and how it felt.",
    )

    if st.button("Run Support Team", type="primary"):
        if not journal_entry.strip():
            st.warning("Add a journal entry so the agents have something to work with.")
            return

        inputs = {
            "daily_mood": daily_mood.strip(),
            "journal_entry": journal_entry.strip(),
        }
        orch = Orchestrator()
        output = run_with_status_updates(
            lambda: orch.run_workflow(inputs),
            start_message="Agents are collaborating on your support plan..."
        )

        st.success(f"Workflow Complete! Session ID: {output['session_id']}")

        for agent, response in output["results"].items():
            with st.expander(f"{agent} Response", expanded=True):
                st.markdown(response)

        render_session_log(output["session_id"])


    render_app_footer()

if __name__ == "__main__":
    main()
