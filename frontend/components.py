from __future__ import annotations

from typing import Any

import streamlit as st


def metric_card(
    label: str,
    value: str | int | float,
    description: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-description">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(
    online: bool,
) -> None:
    if online:
        st.markdown(
            '<span class="status-online">● API ONLINE</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-offline">● API OFFLINE</span>',
            unsafe_allow_html=True,
        )


def risk_badge(
    level: str,
) -> None:
    level = str(level).upper()

    colors = {
        "LOW": ("#4ade80", "#052e16"),
        "MEDIUM": ("#facc15", "#422006"),
        "HIGH": ("#fb923c", "#431407"),
        "CRITICAL": ("#f87171", "#450a0a"),
    }

    foreground, background = colors.get(
        level,
        ("#cbd5e1", "#1e293b"),
    )

    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:5px 12px;
            border-radius:999px;
            background:{background};
            color:{foreground};
            border:1px solid {foreground};
            font-size:12px;
            font-weight:700;
        ">
            {level}
        </span>
        """,
        unsafe_allow_html=True,
    )


def event_card(
    event: dict[str, Any],
) -> None:
    event_type = (
        event.get("event_type")
        or event.get("type")
        or event.get("event")
        or "unknown.event"
    )

    event_id = event.get(
        "event_id",
        event.get("id", "unknown"),
    )

    agent_id = event.get(
        "agent_id",
        "unknown",
    )

    timestamp = event.get(
        "timestamp",
        event.get("created_at", ""),
    )

    st.markdown(
        f"""
        <div class="event-row">
            <div class="event-type">
                {event_type}
            </div>
            <div class="event-detail">
                Agent: {agent_id}
                &nbsp; | &nbsp;
                Event: {event_id}
                &nbsp; | &nbsp;
                {timestamp}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(
    alert: dict[str, Any],
) -> None:
    title = (
        alert.get("title")
        or alert.get("name")
        or alert.get("alert_type")
        or "Security Alert"
    )

    description = (
        alert.get("description")
        or alert.get("message")
        or alert.get("reason")
        or "Security event detected."
    )

    severity = (
        alert.get("severity")
        or alert.get("risk_level")
        or "HIGH"
    )

    st.markdown(
        f"""
        <div class="alert-card">
            <div class="alert-title">
                [{severity}] {title}
            </div>
            <div class="alert-description">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def investigation_card(
    investigation: dict[str, Any],
) -> None:
    investigation_id = investigation.get(
        "investigation_id",
        investigation.get("id", "unknown"),
    )

    title = investigation.get(
        "title",
        investigation.get(
            "name",
            "Investigation",
        ),
    )

    status = investigation.get(
        "status",
        "unknown",
    )

    risk = investigation.get(
        "risk_score",
        investigation.get(
            "risk",
            "N/A",
        ),
    )

    st.markdown(
        f"""
        <div class="investigation-card">
            <strong>{title}</strong>
            <br>
            <small>
                ID: {investigation_id}
                &nbsp; | &nbsp;
                Status: {status}
                &nbsp; | &nbsp;
                Risk: {risk}
            </small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(
    title: str,
    description: str = "",
) -> None:
    st.title(title)

    if description:
        st.caption(description)


def empty_state(
    message: str,
) -> None:
    st.info(message)