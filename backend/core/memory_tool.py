# filename=backend/core/memory_tool.py
"""
memory_tool.py
---------------
Manages conversational memory and mock tools for SEC/SOX audit assistant.

Handles:
- Persistent memory using ConversationBufferMemory
- A simple placeholder for external tools (e.g. fetching new SEC data)
- Ready for LangChain integration with RAG pipelines
"""

from langchain.memory import ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict
import os
import json


class AuditMemory:
    """
    A wrapper around LangChain's ConversationBufferMemory
    that can persist and reload memory from disk.
    """

    def __init__(self, memory_path: str = "./backend/data/memory/session_memory.json"):
        self.memory_path = memory_path
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.load_memory()

    def save_memory(self):
        """Save memory to disk as JSON."""
        try:
            messages = messages_to_dict(self.memory.chat_memory.messages)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=2)
        except Exception as e:
            print(f"[AuditMemory] ⚠️ Error saving memory: {e}")

    def load_memory(self):
        """Load memory from disk if available."""
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                self.memory.chat_memory.messages = messages_from_dict(messages)
                print(f"[AuditMemory] 💾 Loaded memory from {self.memory_path}")
            else:
                print("[AuditMemory] 🧠 No existing memory file found, starting fresh.")
        except Exception as e:
            print(f"[AuditMemory] ⚠️ Error loading memory: {e}")

    def add_message(self, role: str, content: str):
        """Manually add messages (useful for pre-context or testing)."""
        if role.lower() == "user":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)

    def clear_memory(self):
        """Reset chat memory."""
        self.memory.clear()
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)
        print("[AuditMemory] 🧹 Memory cleared successfully.")


# -----------------------------
# Mock tool: SEC Update Fetcher
# -----------------------------

class SECFetchTool:
    """
    Placeholder for a future tool that fetches or indexes
    new SEC filings from public sources or APIs.
    """

    def __init__(self, data_dir: str = "./backend/data/public_sec_docs"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def list_documents(self):
        """List all SEC files currently available."""
        docs = [f for f in os.listdir(self.data_dir) if f.endswith(".txt") or f.endswith(".pdf")]
        print(f"[SECFetchTool] 📄 {len(docs)} SEC documents found.")
        return docs

    def fetch_new_filings(self):
        """Mock method to simulate fetching new SEC filings."""
        print("[SECFetchTool] 🔄 Fetching new filings (simulated)...")
        # Placeholder logic — later you can integrate EDGAR API or Azure Data Connector
        return ["10-K_Amazon_2024.txt", "10-Q_Apple_2024.txt"]


# Quick check
if __name__ == "__main__":
    mem = AuditMemory()
    mem.add_message("user", "What are SOX compliance controls?")
    mem.add_message("ai", "SOX controls ensure accurate financial reporting and data integrity.")
    mem.save_memory()
    print("[Test] ✅ Memory saved and working as expected.")

    tool = SECFetchTool()
    tool.list_documents()
