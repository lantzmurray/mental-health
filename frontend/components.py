"""Streamlit UI Components - Reusable across all projects."""

import html
import threading
import time
from typing import Any, Callable, Dict, Optional, Sequence, TypeVar

import streamlit as st

T = TypeVar("T")

DEFAULT_HEARTBEAT_MESSAGES = (
    "Still working...",
    "Still updating...",
)

DEFAULT_APP_FOOTER_TEXT = "Built by Lantz Murray."

def create_input_section(
    title: str,
    input_type: str,
    placeholder: str = "",
    height: int = 200,
    help_text: Optional[str] = None
) -> Any:
    """Create standardized input section"""
    st.subheader(title)
    
    if input_type == "text_area":
        return st.text_area(
            placeholder=placeholder,
            height=height,
            help=help_text
        )
    elif input_type == "text_input":
        return st.text_input(
            placeholder=placeholder,
            help=help_text
        )
    elif input_type == "file_uploader":
        return st.file_uploader(
            label=placeholder,
            help=help_text
        )
    else:
        raise ValueError(f"Unknown input type: {input_type}")

def create_output_section(
    title: str,
    content: str,
    show_raw: bool = False
) -> None:
    """Create standardized output section"""
    st.subheader(title)
    
    if show_raw:
        with st.expander("Show Raw Output"):
            st.code(content)
    else:
        st.markdown(content)

def create_processing_indicator(message: str = "Processing...") -> None:
    """Create standardized processing indicator"""
    with st.spinner(message):
        yield

def create_error_message(error: str) -> None:
    """Create standardized error message"""
    st.error(f"Error: {error}")

def create_success_message(message: str) -> None:
    """Create standardized success message"""
    st.success(message)

def create_info_message(message: str) -> None:
    """Create standardized info message"""
    st.info(message)

def create_warning_message(message: str) -> None:
    """Create standardized warning message"""
    st.warning(message)

def create_button(
    label: str,
    on_click: Callable,
    disabled: bool = False,
    key: Optional[str] = None
) -> bool:
    """Create standardized button"""
    return st.button(
        label=label,
        on_click=on_click,
        disabled=disabled,
        key=key
    )

def create_screenshot_placeholder(
    project_id: str,
    description: str = "Application screenshot"
) -> None:
    """Create placeholder for screenshot"""
    st.info(f"📸 {description}")
    st.markdown(f"*Screenshot will be added: `screenshots/{project_id}-*.png`*")

def create_metrics_display(
    metrics: Dict[str, Any]
) -> None:
    """Create standardized metrics display"""
    st.subheader("Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Calls",
            metrics.get("total_calls", 0)
        )
    
    with col2:
        st.metric(
            "Avg Time",
            f"{metrics.get('average_time', 0):.2f}s"
        )
    
    with col3:
        st.metric(
            "Success Rate",
            f"{metrics.get('success_rate', 0):.1%}"
        )


def render_app_footer(text: str = DEFAULT_APP_FOOTER_TEXT) -> None:
    """Render a consistent project footer near the bottom of the page."""
    st.markdown(
        f"""
        <div style="padding: 2rem 0 1rem; text-align: center; color: #6b7280; font-size: 0.9rem;">
            {html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_with_status_updates(
    task: Callable[[], T],
    start_message: str = "Working on your request...",
    heartbeat_messages: Optional[Sequence[str]] = None,
    heartbeat_interval_seconds: float = 1.5,
) -> T:
    """Run a long task in the background while the UI posts keep-alive updates.

    Streamlit can look frozen during long local-model calls on older Macs.
    This helper keeps a visible status box on-screen so users can tell the
    app is still alive while the real work continues in a background thread.
    """
    messages = tuple(heartbeat_messages or DEFAULT_HEARTBEAT_MESSAGES)
    status_placeholder = st.empty()
    started_at = time.monotonic()
    result: Dict[str, T] = {}
    error: Dict[str, Exception] = {}

    def worker() -> None:
        """Run the real task without blocking the status-update loop."""
        try:
            result["value"] = task()
        except Exception as exc:  # pragma: no cover - UI helper safety guard
            error["value"] = exc

    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()

    status_index = 0
    while worker_thread.is_alive():
        elapsed_seconds = int(time.monotonic() - started_at)
        heartbeat = messages[status_index % len(messages)]
        status_placeholder.info(
            f"{start_message}\n\n{heartbeat} {elapsed_seconds}s elapsed."
        )
        worker_thread.join(timeout=heartbeat_interval_seconds)
        status_index += 1

    elapsed_seconds = int(time.monotonic() - started_at)
    if "value" in error:
        status_placeholder.error(
            f"{start_message}\n\nStopped after {elapsed_seconds}s because an error occurred."
        )
        raise error["value"]

    status_placeholder.success(
        f"{start_message}\n\nFinished after {elapsed_seconds}s."
    )
    return result["value"]
