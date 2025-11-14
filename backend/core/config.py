# backend/core/config.py

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

# =========================================================
# 📦 Load Environment Variables
# =========================================================
load_dotenv()

# =========================================================
# 🔧 General App Configuration
# =========================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
PORT = int(os.getenv("PORT", 8000))

# =========AUTH==========
# ==============AUTH========
SECRET_KEY=os.getenv("SECRET_KEY","supersecretkey_change_this")
ALGORITHM = os.getenv("ALGORITHM","HS256") 
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")


# =========================================================
# 🧠 Azure OpenAI Configuration
# =========================================================

AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Models
AZURE_EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-3-large")
AZURE_CHAT_MODEL = os.getenv("AZURE_CHAT_MODEL", "gpt-4o-mini")

# =========================================================
# 💾 Vector Store Configuration
# =========================================================

VECTORSTORE_TYPE = os.getenv("VECTORSTORE_TYPE", "chroma")
# VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "./backend/data/vectorstores/")
# os.makedirs(VECTORSTORE_PATH, exist_ok=True)
VECTORSTORE_PATH = os.path.abspath(
    os.getenv("VECTORSTORE_PATH", "./backend/data/vectorstores/")
)
os.makedirs(VECTORSTORE_PATH, exist_ok=True)

print(f"[config] Debug: VECTORSTORE_PATH resolved to {VECTORSTORE_PATH}")
# =========================================================
# ⚙️ Azure Model Clients (LangChain Wrappers)
# =========================================================

def get_azure_embeddings():
    """Return an AzureOpenAIEmbeddings client instance."""
    return AzureOpenAIEmbeddings(
        azure_deployment=AZURE_EMBEDDING_MODEL,
        openai_api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
    )


def get_azure_chat_model(temperature: float = 0.2):
    """Return an AzureChatOpenAI model for generation."""
    return AzureChatOpenAI(
        azure_deployment=AZURE_CHAT_MODEL,
        openai_api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_API_KEY,
        temperature=temperature,
    )

# =========================================================
# 🧩 Unified Config Objects (Class + Instance)
# =========================================================

class Config:
    """Centralized access to app configuration values."""
    ENVIRONMENT = ENVIRONMENT
    LOG_LEVEL = LOG_LEVEL
    PORT = PORT
    VECTORSTORE_TYPE = VECTORSTORE_TYPE
    VECTORSTORE_PATH = VECTORSTORE_PATH
    AZURE_API_KEY = AZURE_API_KEY
    AZURE_ENDPOINT = AZURE_ENDPOINT
    AZURE_API_VERSION = AZURE_API_VERSION
    AZURE_EMBEDDING_MODEL = AZURE_EMBEDDING_MODEL
    AZURE_CHAT_MODEL = AZURE_CHAT_MODEL


# Keep old naming for backward compatibility
class Settings:
    ENV = ENVIRONMENT
    LOG_LEVEL = LOG_LEVEL
    PORT = PORT

    VECTORSTORE_TYPE = VECTORSTORE_TYPE
    VECTORSTORE_PATH = VECTORSTORE_PATH

    AZURE_API_KEY = AZURE_API_KEY
    AZURE_API_VERSION = AZURE_API_VERSION
    AZURE_OPENAI_ENDPOINT = AZURE_ENDPOINT

    AZURE_EMBEDDING_MODEL = AZURE_EMBEDDING_MODEL
    AZURE_CHAT_MODEL = AZURE_CHAT_MODEL

    # backward compatibility
    AZURE_EMBEDDING_DEPLOYMENT = AZURE_EMBEDDING_MODEL
    AZURE_CHAT_DEPLOYMENT = AZURE_CHAT_MODEL

    # AUTH
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES



# Export both for flexibility
config = Config()
settings = Settings()

# =========================================================
# 🧾 Startup Logs
# =========================================================

print(f"[config] ✅ Environment loaded: {Config.ENVIRONMENT}")
print(f"[config] 🔗 Using Azure endpoint: {Config.AZURE_ENDPOINT}")
print(f"[config] 💾 VectorStore: {Config.VECTORSTORE_TYPE} → {Config.VECTORSTORE_PATH}")
