"""Shared agent utilities for Project 20."""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import requests
from tinydb import Query, TinyDB

PROJECT_NAME = "Mental Health Companion Agents"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TIMEOUT_SECONDS = 1800

memory_dir = os.path.join(os.path.dirname(__file__), "..", "memory")
os.makedirs(memory_dir, exist_ok=True)
db = TinyDB(os.path.join(memory_dir, "memory_store.json"))
Session = Query()


def _read_ollama_stream(response: requests.Response) -> str:
    """Read Ollama's streamed NDJSON chunks into one response string."""
    chunks = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        data = json.loads(line)
        chunks.append(data.get("response", ""))
        if data.get("done"):
            break
    return "".join(chunks).strip()


def generate_session_id() -> str:
    """Create a short session id that is easy to surface in demos."""
    return uuid.uuid4().hex[:8]


def call_llm(
    prompt: str,
    model: str = "llama2",
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> str:
    """Call the local Ollama model with project-friendly defaults."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        with requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=(10, OLLAMA_TIMEOUT_SECONDS),
            stream=True,
        ) as response:
            response.raise_for_status()
            return _read_ollama_stream(response)
    except requests.RequestException as exc:
        return f"LLM error for {PROJECT_NAME}: {exc}"


def log_agent_response(
    session_id: str,
    agent: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Append a new collaboration entry to the shared session log."""
    timestamp = datetime.now().isoformat(timespec="seconds")
    entry = {
        "agent": agent,
        "content": content,
        "timestamp": timestamp,
        "metadata": metadata or {},
    }

    existing = db.get(Session.session_id == session_id)
    if existing:
        updated_log = existing.get("log", []) + [entry]
        db.update(
            {
                "log": updated_log,
                "updated_at": timestamp,
            },
            Session.session_id == session_id,
        )
        return

    db.insert(
        {
            "session_id": session_id,
            "project": PROJECT_NAME,
            "created_at": timestamp,
            "updated_at": timestamp,
            "log": [entry],
        }
    )


def get_session_history(session_id: str) -> List[Dict[str, Any]]:
    """Return the collaboration log for a prior workflow run."""
    record = db.get(Session.session_id == session_id)
    if not record:
        return []
    return record.get("log", [])


def _stringify_value(value: Any) -> str:
    """Normalize values before they are embedded into prompts or logs."""
    if value is None:
        return "Not provided"
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else "Not provided"
    if isinstance(value, (list, dict, tuple)):
        return json.dumps(value, indent=2, ensure_ascii=True)
    return str(value)


def _format_context(context_data: Dict[str, Any]) -> str:
    """Render user input as a stable, readable prompt block."""
    if not context_data:
        return "- No input context was supplied."

    lines = []
    for key, value in context_data.items():
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: {_stringify_value(value)}")
    return "\n".join(lines)


def _format_history(session_id: str) -> str:
    """Summarize recent agent output for the next specialist in the chain."""
    history = get_session_history(session_id)
    if not history:
        return "- No earlier agent output yet."

    recent_entries = history[-4:]
    formatted_entries = []
    for entry in recent_entries:
        formatted_entries.append(
            f"### {entry['agent']} ({entry['timestamp']})\n{entry['content']}"
        )
    return "\n\n".join(formatted_entries)


def run_agent_task(
    session_id: str,
    agent_name: str,
    context_data: Dict[str, Any],
    objective: str,
    sections: Iterable[str],
    extra_guidance: str = "",
    model: Optional[str] = None,
) -> str:
    """Run a prompt-driven specialist agent and store the result."""
    section_list = list(sections)
    prompt = f"""You are {agent_name} for the School of AI project "{PROJECT_NAME}".

Objective:
{objective}

Current user context:
{_format_context(context_data)}

Recent collaboration history:
{_format_history(session_id)}

Response requirements:
- Write polished markdown that is good enough for a portfolio walkthrough.
- Keep the response grounded in the supplied inputs.
- If a detail is missing, make a reasonable assumption and label it clearly.
- Be concrete and teachable because this output may later be adapted into future coursework.
- Do not present live facts, reservations, approvals, or citations as confirmed unless they were explicitly provided.

Required sections:
{chr(10).join(f"- {section}" for section in section_list)}

Additional guidance:
{extra_guidance or "Keep it concise, practical, and well structured."}
"""

    response = call_llm(
        prompt=prompt,
        model=model or "llama2",
        system_prompt=(
            "You are a careful AI teammate who writes helpful, structured, "
            "portfolio-ready outputs."
        ),
    )
    log_agent_response(
        session_id,
        agent_name,
        response,
        metadata={
            "objective": objective,
            "sections": section_list,
        },
    )
    return response
