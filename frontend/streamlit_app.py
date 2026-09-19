from __future__ import annotations

import streamlit as st

from api_client import AgentTraceAPI
from components import (
    alert_card,
    empty_state,
    event_card,
    investigation_card,
    metric_card,
    page_header,
    risk_badge,
    status_badge,
)
from config import API_BASE_URL, EVENT_TYPES
from styles import load_css


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AgentTrace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


# ============================================================
# API CLIENT
# ============================================================

@st.cache_resource
def get_api() -> AgentTraceAPI:
    return AgentTraceAPI()


api = get_api()


# ============================================================
# SESSION STATE
# ============================================================

if "selected_investigation" not in st.session_state:
    st.session_state.selected_investigation = None

if "hero_result" not in st.session_state:
    st.session_state.hero_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:26px;
            font-weight:800;
            color:#f8fafc;
            margin-bottom:4px;
        ">
            🛡️ AgentTrace
        </div>

        <div style="
            color:#64748b;
            font-size:12px;
            margin-bottom:24px;
        ">
            AI Agent Security Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Live Events",
            "Alerts",
            "Investigations",
            "Demo Mode",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("Backend")

    status_placeholder = st.empty()

    try:
        health = api.health()

        if health.get("status") == "ok":
            status_badge(True)

            environment = health.get(
                "environment",
                "unknown",
            )

            st.caption(
                f"Environment: `{environment}`"
            )
        else:
            status_badge(False)

    except Exception:
        status_badge(False)

    st.divider()

    st.caption("API")

    st.code(
        API_BASE_URL,
        language="text",
    )

    if st.button(
        "↻ Refresh",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    page_header(
        "Security Dashboard",
        "Monitor AI-agent activity, threats, policy violations and investigations.",
    )

    # Hero section

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                AgentTrace
            </div>

            <div class="hero-subtitle">
                Security telemetry and forensic visibility
                for autonomous AI agents.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # Dashboard API

    try:
        overview = api.dashboard_overview()

    except Exception as exc:
        overview = {}
        st.warning(
            f"Dashboard endpoint unavailable: {exc}"
        )

    # Attempt to support multiple possible API response shapes.

    agents_count = (
        overview.get("agents")
        or overview.get("agent_count")
        or overview.get("total_agents")
        or 0
    )

    events_count = (
        overview.get("events")
        or overview.get("event_count")
        or overview.get("total_events")
        or 0
    )

    alerts_count = (
        overview.get("alerts")
        or overview.get("alert_count")
        or overview.get("total_alerts")
        or 0
    )

    investigations_count = (
        overview.get("investigations")
        or overview.get("investigation_count")
        or overview.get("total_investigations")
        or 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Agents",
            agents_count,
            "Registered AI agents",
        )

    with col2:
        metric_card(
            "Events",
            events_count,
            "Telemetry events",
        )

    with col3:
        metric_card(
            "Alerts",
            alerts_count,
            "Security alerts",
        )

    with col4:
        metric_card(
            "Investigations",
            investigations_count,
            "Active investigations",
        )

    st.divider()

    # Recent activity

    col_left, col_right = st.columns(
        [1.5, 1]
    )

    with col_left:

        st.subheader("Recent Agent Activity")

        try:
            events = api.get_events(
                limit=10
            )

            if events:
                for event in events:
                    event_card(event)
            else:
                empty_state(
                    "No telemetry events recorded yet."
                )

        except Exception as exc:
            st.error(
                f"Could not load events: {exc}"
            )

    with col_right:

        st.subheader("Security Alerts")

        try:
            alerts = api.get_alerts(
                limit=5
            )

            if alerts:
                for alert in alerts:
                    alert_card(alert)
            else:
                empty_state(
                    "No security alerts."
                )

        except Exception as exc:
            st.error(
                f"Could not load alerts: {exc}"
            )


# ============================================================
# LIVE EVENTS
# ============================================================

elif page == "Live Events":

    page_header(
        "Live Agent Activity",
        "Inspect telemetry generated by AI agents.",
    )

    col1, col2 = st.columns(
        [1, 4]
    )

    with col1:

        limit = st.number_input(
            "Events",
            min_value=5,
            max_value=200,
            value=50,
            step=5,
        )

    with col2:

        event_filter = st.selectbox(
            "Event Type",
            EVENT_TYPES,
        )

    try:
        events = api.get_events(
            limit=int(limit)
        )

        if event_filter != "all":

            events = [
                event
                for event in events
                if (
                    event.get("event_type")
                    or event.get("type")
                    or event.get("event")
                )
                == event_filter
            ]

        st.caption(
            f"{len(events)} event(s)"
        )

        if events:

            for event in events:
                event_card(event)

        else:

            empty_state(
                "No events match the current filter."
            )

    except Exception as exc:

        st.error(
            f"Could not load telemetry: {exc}"
        )


# ============================================================
# ALERTS
# ============================================================

elif page == "Alerts":

    page_header(
        "Security Alerts",
        "Threat detections and policy violations generated by AgentTrace.",
    )

    try:

        alerts = api.get_alerts(
            limit=100
        )

        if not alerts:

            empty_state(
                "No security alerts detected."
            )

        else:

            st.metric(
                "Total Alerts",
                len(alerts),
            )

            st.divider()

            for alert in alerts:

                alert_card(alert)

                with st.expander(
                    "View alert details"
                ):
                    st.json(alert)

    except Exception as exc:

        st.error(
            f"Could not load alerts: {exc}"
        )


# ============================================================
# INVESTIGATIONS
# ============================================================

elif page == "Investigations":

    page_header(
        "Investigations",
        "Trace security incidents from detection to forensic analysis.",
    )

    try:

        investigations = api.get_investigations(
            limit=100
        )

        if not investigations:

            empty_state(
                "No investigations have been created."
            )

        else:

            for investigation in investigations:

                investigation_card(
                    investigation
                )

                investigation_id = investigation.get(
                    "investigation_id",
                    investigation.get(
                        "id",
                        "",
                    ),
                )

                if st.button(
                    "Open Investigation",
                    key=f"open_{investigation_id}",
                ):

                    st.session_state.selected_investigation = (
                        investigation_id
                    )

                    st.rerun()

    except Exception as exc:

        st.error(
            f"Could not load investigations: {exc}"
        )

    # Selected investigation

    selected_id = (
        st.session_state.selected_investigation
    )

    if selected_id:

        st.divider()

        st.subheader(
            f"Investigation: {selected_id}"
        )

        try:

            investigation = api.get_investigation(
                selected_id
            )

            st.json(investigation)

            st.subheader("Evidence")

            evidence = (
                api.get_investigation_evidence(
                    selected_id
                )
            )

            if evidence:

                for item in evidence:

                    with st.expander(
                        str(
                            item.get(
                                "title",
                                item.get(
                                    "evidence_id",
                                    "Evidence",
                                ),
                            )
                        )
                    ):

                        st.json(item)

            else:

                empty_state(
                    "No evidence linked to this investigation."
                )

            st.subheader(
                "Forensic Analysis"
            )

            if st.button(
                "Run Forensic Analysis",
                key=f"forensics_{selected_id}",
            ):

                with st.spinner(
                    "Analyzing investigation..."
                ):

                    try:

                        result = (
                            api.analyze_investigation(
                                selected_id
                            )
                        )

                        st.success(
                            "Forensic analysis completed."
                        )

                        st.json(result)

                    except Exception as exc:

                        st.error(
                            f"Forensic analysis failed: {exc}"
                        )

        except Exception as exc:

            st.error(
                f"Could not load investigation: {exc}"
            )


# ============================================================
# DEMO MODE
# ============================================================

elif page == "Demo Mode":

    page_header(
        "Security Demo",
        "Run the AgentTrace hero scenario for the hackathon demonstration.",
    )

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                🔥 Agent Security Incident
            </div>

            <div class="hero-subtitle">
                Research Agent → Untrusted Content →
                Prompt Injection → Sensitive Action →
                Policy DENY → Alert → Investigation
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### Demo Scenario

        The demo represents a realistic AI-agent attack chain:

        ```text
        Research Agent
              ↓
        Untrusted Content
              ↓
        Prompt Injection
              ↓
        Sensitive Action Attempt
              ↓
        Policy DENY
              ↓
        Tool Blocked
              ↓
        Security Alert
              ↓
        Investigation
              ↓
        Risk Analysis
        ```
        """
    )

    if st.button(
        "▶ Run Security Demo",
        use_container_width=True,
    ):

        with st.spinner(
            "Running AgentTrace security scenario..."
        ):

            try:

                result = api.run_hero_demo()

                st.session_state.hero_result = result

                st.success(
                    "Security scenario completed."
                )

            except Exception as exc:

                st.error(
                    f"Demo failed: {exc}"
                )

    result = st.session_state.hero_result

    if result:

        st.divider()

        st.subheader(
            "Incident Summary"
        )

        # ----------------------------------------------------
        # Core risk information
        # ----------------------------------------------------

        risk_score = result.get(
            "risk_score",
            0,
        )

        risk_level = result.get(
            "risk_level",
            "UNKNOWN",
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            metric_card(
                "Risk Score",
                risk_score,
                "Calculated incident risk",
            )

        with col2:

            st.markdown(
                "### Risk Level"
            )

            risk_badge(
                risk_level
            )

        with col3:

            metric_card(
                "Agent",
                result.get(
                    "agent_id",
                    "unknown",
                ),
                "Affected agent",
            )

        with col4:

            metric_card(
                "Session",
                result.get(
                    "session_id",
                    "unknown",
                ),
                "Incident session",
            )

        st.divider()

        # ----------------------------------------------------
        # Attack details
        # ----------------------------------------------------

        st.subheader(
            "Attack Details"
        )

        details = {
            "Attack Vector": result.get(
                "attack_vector",
                "Unknown",
            ),
            "Policy Decision": result.get(
                "policy_decision",
                "Unknown",
            ),
            "Sensitive Action Attempted": result.get(
                "sensitive_action_attempted",
                False,
            ),
            "Sensitive Action Executed": result.get(
                "sensitive_action_executed",
                False,
            ),
            "Action Blocked": result.get(
                "action_blocked",
                False,
            ),
            "External Transmission": result.get(
                "external_transmission",
                False,
            ),
            "Events Persisted": result.get(
                "events_persisted",
                0,
            ),
        }

        st.json(details)

        # ----------------------------------------------------
        # Detections
        # ----------------------------------------------------

        st.subheader(
            "Security Detections"
        )

        detections = result.get(
            "detections",
            [],
        )

        if detections:

            for detection in detections:

                if isinstance(
                    detection,
                    dict,
                ):

                    title = (
                        detection.get(
                            "name"
                        )
                        or detection.get(
                            "type"
                        )
                        or "Detection"
                    )

                    st.warning(
                        title
                    )

                    with st.expander(
                        "Detection details"
                    ):

                        st.json(
                            detection
                        )

                else:

                    st.warning(
                        str(detection)
                    )

        else:

            empty_state(
                "No detection details returned."
            )

        # ----------------------------------------------------
        # Investigation
        # ----------------------------------------------------

        investigation_id = result.get(
            "investigation_id"
        )

        if investigation_id:

            st.divider()

            st.subheader(
                "Investigation Created"
            )

            st.code(
                investigation_id
            )

            forensic_result = result.get(
                "forensics"
            )

            if forensic_result:

                st.subheader(
                    "Forensic Findings"
                )

                st.json(
                    forensic_result
                )

        # ----------------------------------------------------
        # Raw response
        # ----------------------------------------------------

        with st.expander(
            "View complete API response"
        ):

            st.json(result)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AgentTrace • AI Agent Security Telemetry & Forensics"
)