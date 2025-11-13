import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/query/"

st.set_page_config(
    page_title="Finance Audit RAG Assistant",
    page_icon="💼",
    layout="wide",
)

# Load CSS & JS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

with open("assets/animations.js") as f:
    st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

# Theme setup
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
st.sidebar.button(f"{theme_icon} Toggle Theme", on_click=toggle_theme)

# Header
st.markdown(f"""
<div class="app-container {st.session_state.theme}">
    <div class="header">
        <h1>Finance Audit RAG Assistant 💼</h1>
        <p>Your AI partner for compliance, SOX, and SEC-related insights ⚡</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Info")
    st.write("**Backend API:** `127.0.0.1:8000`")
    st.write("**Cache:** Redis enabled ✅")
    st.write("**Model:** Azure GPT-4o-mini")
    st.write("**Retriever:** FAISS + Chroma Ensemble")
    st.caption("💡 Cached responses appear instantly!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat Input
query = st.text_input("🔍 Ask your question...", placeholder="e.g., Explain Section 404 compliance...", label_visibility="collapsed")

col1, col2, _ = st.columns([1, 1, 5])  # Tweaked columns for better button spacing
with col1:
    ask = st.button("✨ Send")
with col2:
    clear = st.button("🗑️ Clear Chat")

if clear:
    st.session_state.chat_history = []
    st.rerun() # Use rerun for a cleaner clear

if ask and query:
    with st.spinner("Thinking... 💭"):
        try:
            response = requests.post(API_URL, json={"query": query}, timeout=60)
            if response.status_code == 200:
                answer = response.json()["response"]
                st.session_state.chat_history.append({"role": "user", "content": query})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Server error: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Connection failed: {e}")

# Chat History
for msg in st.session_state.chat_history:
    role_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
    st.markdown(f"""
        <div class="chat-bubble {role_class}">
            <b>{'👤 User' if msg['role'] == 'user' else '💡 Assistant'}:</b>
            <span>{msg['content']}</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)