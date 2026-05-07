# =========================
# main_app.py
# =========================

import streamlit as st

from app_pages.home import show_home
from app_pages.dashboard import show_dashboard
from app_pages.chatbot import show_chatbot


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Shop BI Assistant",
    layout="wide"
)


# =====================================================
# SESSION STATE
# =====================================================

if "data" not in st.session_state:
    st.session_state.data = None

if "data_source" not in st.session_state:
    st.session_state.data_source = None


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("🏪 Shop BI Assistant")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Dashboard",
        "🤖 AI Assistant"
    ]
)


# =====================================================
# PAGE ROUTING
# =====================================================

if page == "🏠 Home":
    show_home()

elif page == "📊 Dashboard":
    show_dashboard()

elif page == "🤖 AI Assistant":
    show_chatbot()