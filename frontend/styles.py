import streamlit as st


def load_css() -> None:
    st.markdown(
        """
        <style>

        /* --------------------------------------------------
           Global
        -------------------------------------------------- */

        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(99, 102, 241, 0.08),
                    transparent 30%
                ),
                #080b14;
            color: #e5e7eb;
        }

        .main .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* --------------------------------------------------
           Sidebar
        -------------------------------------------------- */

        section[data-testid="stSidebar"] {
            background: #0b0f19;
            border-right: 1px solid #1f2937;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.5rem;
        }

        /* --------------------------------------------------
           Typography
        -------------------------------------------------- */

        h1,
        h2,
        h3 {
            color: #f8fafc !important;
        }

        p,
        label,
        span {
            color: #cbd5e1;
        }

        /* --------------------------------------------------
           Cards
        -------------------------------------------------- */

        .metric-card {
            background: #111725;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 18px;
            min-height: 115px;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 30px;
            font-weight: 700;
        }

        .metric-description {
            color: #64748b;
            font-size: 12px;
            margin-top: 4px;
        }

        /* --------------------------------------------------
           Hero
        -------------------------------------------------- */

        .hero {
            background:
                linear-gradient(
                    135deg,
                    rgba(99, 102, 241, 0.16),
                    rgba(139, 92, 246, 0.06)
                );
            border: 1px solid #312e81;
            border-radius: 16px;
            padding: 26px;
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 34px;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 6px;
        }

        .hero-subtitle {
            font-size: 15px;
            color: #94a3b8;
        }

        /* --------------------------------------------------
           Status
        -------------------------------------------------- */

        .status-online {
            display: inline-block;
            background: #052e16;
            color: #4ade80;
            border: 1px solid #166534;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-offline {
            display: inline-block;
            background: #450a0a;
            color: #f87171;
            border: 1px solid #991b1b;
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: 600;
        }

        /* --------------------------------------------------
           Event rows
        -------------------------------------------------- */

        .event-row {
            background: #111725;
            border: 1px solid #1f2937;
            border-radius: 10px;
            padding: 13px 15px;
            margin-bottom: 8px;
        }

        .event-type {
            color: #a78bfa;
            font-weight: 600;
            font-size: 13px;
        }

        .event-detail {
            color: #94a3b8;
            font-size: 12px;
            margin-top: 3px;
        }

        /* --------------------------------------------------
           Alert
        -------------------------------------------------- */

        .alert-card {
            background: #1c1111;
            border: 1px solid #7f1d1d;
            border-left: 4px solid #ef4444;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        .alert-title {
            color: #fca5a5;
            font-weight: 700;
        }

        .alert-description {
            color: #cbd5e1;
            font-size: 13px;
            margin-top: 5px;
        }

        /* --------------------------------------------------
           Investigation
        -------------------------------------------------- */

        .investigation-card {
            background: #111725;
            border: 1px solid #1f2937;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 10px;
        }

        /* --------------------------------------------------
           Buttons
        -------------------------------------------------- */

        .stButton > button {
            border-radius: 8px;
            border: 1px solid #3730a3;
            background: #312e81;
            color: white;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: #6366f1;
            background: #4338ca;
            color: white;
        }

        /* --------------------------------------------------
           Tables
        -------------------------------------------------- */

        [data-testid="stDataFrame"] {
            border: 1px solid #1f2937;
            border-radius: 10px;
        }

        /* --------------------------------------------------
           Hide Streamlit branding
        -------------------------------------------------- */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )