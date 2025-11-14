"""
main.py
-------
FastAPI entrypoint for the Finance Audit RAG backend.
Includes /health, /ingest, and /query routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import ingest_routes, query_routes
from backend.core.utils import log_info
import threading
from backend.core.watchdog_service import start_watchdog

app = FastAPI(
    title="Finance Audit RAG",
    description="Federated Retrieval-Augmented Generation system for financial audit compliance (SOX + SEC).",
    version="1.0.0",
)

# --------------------------
# Middleware (CORS)
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later restrict to Streamlit frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Routes
# --------------------------
app.include_router(ingest_routes.router)
app.include_router(query_routes.router)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=start_watchdog, daemon=True).start()

# --------------------------
# Health Check
# --------------------------
@app.get("/health")
def health_check():
    log_info("✅ Health check called.")
    return {"status": "ok", "message": "Finance Audit RAG backend is healthy."}

# --------------------------
# Run via: uvicorn backend.main:app --reload
# --------------------------
if __name__ == "__main__":
    import uvicorn
    log_info("🚀 Starting Finance Audit RAG backend...")
    uvicorn.run("backend.main:app", host="localhost", port=8000, reload=True)
