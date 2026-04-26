"""Reusable runtime for the later School of AI multi-agent projects.

This module packages the patterns introduced in projects 11-13:
- simple prompt-driven agent execution
- shared TinyDB session logs so agents can collaborate
- predictable session ids that the frontend can display and the game can reuse

Projects 20-25 can import this runtime and keep their own prompts, comments,
and UI logic without copy-pasting the low-level plumbing over and over.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from tinydb import Query, TinyDB

from .config import Config
from .llm_client import LLMClient


class ProjectRuntime:
    """Shared LLM + memory runtime for standalone School of AI projects."""

    def __init__(
        self,
        project_name: str,
        memory_path: Path,
        default_model: str = "llama2",
    ) -> None:
        self.project_name = project_name
        self.default_model = default_model
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(str(self.memory_path))
        self.session_query = Query()

    def generate_session_id(self) -> str:
        """Create a short session id that is easy to show in demos."""
        return uuid.uuid4().hex[:8]

    def _build_client(self, model: Optional[str] = None) -> LLMClient:
        """Build an LLM client from shared School of AI configuration."""
        llm_config = Config.get_llm_config()
        provider = llm_config.get("provider", "ollama")
        resolved_model = model or llm_config.get("model", self.default_model)

        credentials = llm_config.get("credentials") or {}
        if llm_config.get("api_key"):
            credentials = {**credentials, "api_key": llm_config["api_key"]}

        return LLMClient(
            provider=provider,
            model=resolved_model,
            region=llm_config.get("region"),
            credentials=credentials or None,
            endpoint=llm_config.get("endpoint"),
            timeout_seconds=llm_config.get("timeout_seconds", 1800),
        )

    def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        """Call the configured LLM with sensible defaults for portfolio demos."""
        try:
            client = self._build_client(model)
            if client.provider == "ollama":
                return client.query(
                    prompt,
                    system_prompt=system_prompt,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                )

            return client.query(
                prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            return f"LLM error for {self.project_name}: {exc}"

    def log_agent_response(
        self,
        session_id: str,
        agent: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a new collaboration entry to the session memory log."""
        timestamp = datetime.now().isoformat(timespec="seconds")
        entry = {
            "agent": agent,
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        existing = self.db.get(self.session_query.session_id == session_id)
        if existing:
            updated_log = existing.get("log", []) + [entry]
            self.db.update(
                {
                    "log": updated_log,
                    "updated_at": timestamp,
                },
                self.session_query.session_id == session_id,
            )
            return

        self.db.insert(
            {
                "session_id": session_id,
                "project": self.project_name,
                "created_at": timestamp,
                "updated_at": timestamp,
                "log": [entry],
            }
        )

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Return the full collaboration log for the given session."""
        record = self.db.get(self.session_query.session_id == session_id)
        if not record:
            return []
        return record.get("log", [])

    def _stringify_value(self, value: Any) -> str:
        """Normalize values before they are embedded into prompts or logs."""
        if value is None:
            return "Not provided"
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned if cleaned else "Not provided"
        if isinstance(value, (list, dict, tuple)):
            return json.dumps(value, indent=2, ensure_ascii=True)
        return str(value)

    def _format_context(self, context_data: Dict[str, Any]) -> str:
        """Render user input as a stable, readable prompt block."""
        if not context_data:
            return "- No input context was supplied."

        lines = []
        for key, value in context_data.items():
            label = key.replace("_", " ").title()
            lines.append(f"- {label}: {self._stringify_value(value)}")
        return "\n".join(lines)

    def _format_history(self, session_id: str) -> str:
        """Summarize the recent collaboration log for the next agent."""
        history = self.get_session_history(session_id)
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
        self,
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
        prompt = f"""You are {agent_name} for the School of AI project "{self.project_name}".

Objective:
{objective}

Current user context:
{self._format_context(context_data)}

Recent collaboration history:
{self._format_history(session_id)}

Response requirements:
- Write polished markdown that is good enough for a portfolio walkthrough.
- Keep the response grounded in the supplied inputs.
- If a detail is missing, make a reasonable assumption and label it clearly.
- Be concrete and teachable because this output may later be adapted into Signal City gameplay content.
- Do not present external bookings, citations, approvals, or live facts as confirmed unless they were explicitly provided.

Required sections:
{chr(10).join(f"- {section}" for section in section_list)}

Additional guidance:
{extra_guidance or "Keep it concise, practical, and well structured."}
"""

        response = self.call_llm(
            prompt=prompt,
            model=model,
            system_prompt=(
                "You are a careful AI teammate who writes helpful, structured, "
                "portfolio-ready outputs."
            ),
        )
        self.log_agent_response(
            session_id,
            agent_name,
            response,
            metadata={
                "objective": objective,
                "sections": section_list,
            },
        )
        return response
