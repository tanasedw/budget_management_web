import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    /* ── FONT ── */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* ── HIDE STREAMLIT DEFAULTS ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── PAGE BACKGROUND ── */
    .stApp {
        background-color: #ffffff;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background-color: rgba(255,255,255,0.85);
        backdrop-filter: saturate(180%) blur(20px);
        border-right: 1px solid rgba(0,0,0,0.08);
    }

    /* ── BUTTONS — primary ── */
    .stButton > button {
        background: linear-gradient(135deg, #2D5A87 0%, #4A7C8A 100%);
        color: #ffffff;
        border: none;
        border-radius: 50px;
        padding: 10px 28px;
        font-size: 15px;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(45,90,135,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(45,90,135,0.3);
        color: #ffffff;
    }

    /* ── CARDS ── */
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 20px;
        padding: 20px 24px;
        border: none;
        box-shadow: 0 5px 20px rgba(0,0,0,0.07);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.10);
    }

    /* ── INPUTS ── */
    input, textarea, select {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        font-family: inherit !important;
    }
    input:focus, textarea:focus {
        border-color: #2D5A87 !important;
        box-shadow: 0 0 0 3px rgba(45,90,135,0.12) !important;
    }

    /* ── DATAFRAME / TABLE ── */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #d2d2d7;
    }

    /* ── SECTION HEADERS ── */
    h1 {
        font-size: 48px !important;
        font-weight: 700 !important;
        letter-spacing: -0.022em !important;
        color: #1d1d1f !important;
    }
    h2 {
        font-size: 32px !important;
        font-weight: 700 !important;
        letter-spacing: -0.018em !important;
        color: #1d1d1f !important;
    }
    h3 {
        font-size: 21px !important;
        font-weight: 600 !important;
        color: #1d1d1f !important;
    }

    /* ── SUCCESS / WARNING / ERROR ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
        border: none;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #d2d2d7;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-size: 14px;
        font-weight: 500;
        color: #6e6e73;
    }
    .stTabs [aria-selected="true"] {
        color: #2D5A87 !important;
        border-bottom: 2px solid #2D5A87 !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d2d2d7; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)
