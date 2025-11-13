"""
watchdog_service.py
-------------------
Monitors document folders for file changes and triggers automatic ingestion.
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.core.utils import log_info, log_error
from backend.core.rag_pipeline import ingest_corpus  # ✅ Import the FUNCTION, not the module

# --------------------------
# File Change Handler
# --------------------------
class IngestionEventHandler(FileSystemEventHandler):
    """Handles automatic ingestion when files change."""

    def on_modified(self, event):
        if event.is_directory:
            return
        log_info(f"📄 File change detected: {event.src_path}")
        try:
            log_info("🔁 Running automatic re-ingestion via Watchdog...")
            ingest_corpus("./backend/data/private")  # ✅ This calls the function
            log_info("✅ Watchdog ingestion completed successfully.")
        except Exception as e:
            log_error(f"❌ Watchdog ingestion failed: {e}")

    def on_created(self, event):
        if event.is_directory:
            return
        log_info(f"📄 New file detected: {event.src_path}")
        try:
            log_info("🔁 Running automatic re-ingestion via Watchdog...")
            ingest_corpus("./backend/data/private")
            log_info("✅ Watchdog ingestion completed successfully.")
        except Exception as e:
            log_error(f"❌ Watchdog ingestion failed: {e}")

# --------------------------
# Watchdog Runner
# --------------------------
def start_watchdog():
    """Start monitoring all data directories for changes."""
    paths_to_watch = [
        "./backend/data/public",
        "./backend/data/private",
        "./backend/data/sox_docs",
    ]

    event_handler = IngestionEventHandler()
    observer = Observer()

    for path in paths_to_watch:
        log_info(f"👀 Watching directory: {path}")
        observer.schedule(event_handler, path, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
