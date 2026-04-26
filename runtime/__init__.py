"""Backend shared components initialization.

This module provides the runtime components needed for the project.
All components are self-contained within this project.
"""

from .llm_client import LLMClient
from .config import Config
from .project_runtime import ProjectRuntime

__all__ = [
    "LLMClient",
    "Config",
    "ProjectRuntime",
]
