"""Runtime bridge for Project 20.

This project uses a self-contained runtime - no external dependencies.
"""

from pathlib import Path
import sys

# Add project root to path for local imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from runtime import ProjectRuntime

runtime = ProjectRuntime(
    project_name="Mental Health Companion Agents",
    memory_path=PROJECT_ROOT / "memory" / "memory_store.json",
    default_model="llama2",
)

call_llm = runtime.call_llm
generate_session_id = runtime.generate_session_id
get_session_history = runtime.get_session_history
log_agent_response = runtime.log_agent_response
run_agent_task = runtime.run_agent_task
