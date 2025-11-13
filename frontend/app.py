# frontend/app.py

import streamlit as st
import requests

st.set_page_config(page_title="Finance Audit RAG", layout="centered")
st.title("📊 Finance Audit RAG Chat")

# Input text box
query = st.text_input("Ask a question about SOX / SEC filings:")

# Backend URL (adjust if running on a different host/port)
API_URL = "http://localhost:8000/query/"

if st.button("Submit") and query:
    with st.spinner("Fetching answer..."):
        try:
            response = requests.post(
                API_URL,
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                answer = response.json().get("response", "No answer returned.")
                st.success(answer)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

# Optional: display a footer
st.markdown("---")
st.markdown("💡 This app queries the RAG pipeline via your FastAPI backend.")
