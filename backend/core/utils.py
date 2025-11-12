"""
utils.py
--------
General-purpose helpers for the Finance Audit RAG system.
Includes file loading, logging, and safe directory handling.
"""

import os
import datetime
import logging
from typing import List
from langchain_community.document_loaders import TextLoader


# --------------------------
# Logging Configuration
# --------------------------

LOG_PATH = "./backend/logs/app.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def log_info(message: str):
    """Write info message to both console and log file."""
    print(f"[INFO] {message}")
    logging.info(message)

def log_error(message: str):
    """Write error message to both console and log file."""
    print(f"[ERROR] {message}")
    logging.error(message)


# --------------------------
# File & Directory Utilities
# --------------------------

def ensure_dir(path: str):
    """Ensure a directory exists."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        log_info(f"Created directory: {path}")


def list_text_files(directory: str) -> List[str]:
    """Return all .txt files in a directory."""
    ensure_dir(directory)
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]


def load_documents_from_dir(directory: str):
    """Load all .txt documents from a directory into LangChain Document objects."""
    from langchain.schema import Document

    ensure_dir(directory)
    txt_files = list_text_files(directory)
    docs = []

    if not txt_files:
        log_info(f"No .txt files found in {directory}")
        return docs

    for file in txt_files:
        try:
            loader = TextLoader(file, encoding="utf-8")
            docs.extend(loader.load())
            log_info(f"Loaded document: {os.path.basename(file)}")
        except Exception as e:
            log_error(f"Failed to load {file}: {e}")

    log_info(f"✅ Loaded {len(docs)} total documents from {directory}")
    return docs


# --------------------------
# Time Utilities
# --------------------------

def timestamp() -> str:
    """Return formatted timestamp string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------
# Quick Check
# --------------------------
if __name__ == "__main__":
    log_info("Testing utils.py logging and document loader...")
    ensure_dir("./backend/data/sox_docs")
    docs = load_documents_from_dir("./backend/data/sox_docs")
    log_info(f"Documents loaded: {len(docs)}")
