import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

    /* ── Global background ─────────────────────────────────── */
    [data-testid="stApp"] { background: #050b17; }

    /* Hide Streamlit chrome */
    header[data-testid="stHeader"],
    footer, #MainMenu { display: none !important; }

    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── Typography ─────────────────────────────────────────── */
    h1 { color: #f8fafc !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }
    h2 { color: #e2e8f0 !important; font-weight: 700 !important; }
    h3 { color: #cbd5e1 !important; font-weight: 600 !important; }
    p  { color: #94a3b8 !important; }

    /* ── Text inputs ────────────────────────────────────────── */
    .stTextInput > div > div > input {
        background: #0a1628 !important;
        border: 1.5px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.18) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: #334155 !important; }

    /* Input labels */
    .stTextInput label, .stSelectbox label {
        color: #475569 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* ── Select box ─────────────────────────────────────────── */
    [data-testid="stSelectbox"] > div > div {
        background: #0a1628 !important;
        border: 1.5px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    [data-baseweb="select"] [data-baseweb="popover"] ul {
        background: #0d1f3c !important;
        border: 1px solid #1e3a5f !important;
        border-radius: 10px !important;
    }
    [data-baseweb="option"] { color: #cbd5e1 !important; background: transparent !important; }
    [data-baseweb="option"]:hover { background: rgba(37,99,235,0.12) !important; }

    /* ── Buttons ────────────────────────────────────────────── */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
        border: none !important;
        cursor: pointer !important;
        width: 100%;
    }
    /* Primary */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 28px rgba(37,99,235,0.45) !important;
    }
    /* Secondary */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1.5px solid #1e3a5f !important;
        color: #64748b !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #3b82f6 !important;
        color: #93c5fd !important;
        background: rgba(59,130,246,0.07) !important;
    }
    /* Disabled */
    .stButton > button:disabled {
        opacity: 0.35 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ── Download button ────────────────────────────────────── */
    [data-testid="stDownloadButton"] > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #0f4c9c, #0c3d7a) !important;
        color: #bfdbfe !important;
        border: 1.5px solid #1e3a5f !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37,99,235,0.35) !important;
    }

    /* ── Progress bar ───────────────────────────────────────── */
    .stProgress > div > div {
        background: #0f172a !important;
        border-radius: 6px !important;
        height: 6px !important;
    }
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2563eb, #06b6d4) !important;
        border-radius: 6px !important;
    }

    /* ── Alerts ─────────────────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left-width: 3px !important;
    }

    /* ── Image border radius ────────────────────────────────── */
    [data-testid="stImage"] img { border-radius: 10px; }

    /* ── Scrollbar ──────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2563eb; }

    /* ── Column gap fix ─────────────────────────────────────── */
    [data-testid="column"] { padding: 0 8px !important; }
    </style>
    """, unsafe_allow_html=True)
