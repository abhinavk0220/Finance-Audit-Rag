"""
query_routes.py
----------------
Handles querying across federated vector stores (FAISS + Chroma)
using Azure GPT-4o-mini for final reasoning and response.
"""

from logging import config
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pytest import Config
from backend.core.retrievers import get_federated_retriever
from backend.core.memory_tool import AuditMemory
from backend.core.utils import log_info, log_error
# from backend.core.config import Config
from backend.core.config import settings


from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import time

router = APIRouter(prefix="/query", tags=["Query"])

# --------------------------
# Request schema
# --------------------------
class QueryRequest(BaseModel):
    query: str


# --------------------------
# Setup model + memory
# --------------------------
def get_azure_chat_model():
    """Return GPT-4o-mini model from Azure OpenAI."""
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_API_KEY,
        deployment_name=settings.AZURE_CHAT_DEPLOYMENT,
        openai_api_version=settings.AZURE_API_VERSION,
        temperature=0.2,
    )


# --------------------------
# POST /query
# --------------------------
@router.post("/")
async def query_rag(request: QueryRequest):
    """
    Query the federated retriever (FAISS + Chroma)
    and get a response from Azure GPT-4o-mini.
    """
    start = time.time()
    try:
        log_info(f"🧠 Query received: {request.query}")

        # Initialize components
        llm = get_azure_chat_model()
        retriever = get_federated_retriever()
        memory = AuditMemory()

        # Build RAG Chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory.memory,
            verbose=False,
        )

        # Generate answer
        response = chain.invoke({"question": request.query})
        answer = response["answer"]

        # Log and save memory
        memory.add_message("user", request.query)
        memory.add_message("ai", answer)
        memory.save_memory()

        log_info(f"✅ Response generated in {round(time.time() - start, 2)}s")
        return {"status": "success", "response": answer}

    except Exception as e:
        log_error(f"❌ Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test_retriever")
async def test_retriever():
    from backend.core.retrievers import get_federated_retriever
    retriever = get_federated_retriever()
    results = retriever.get_relevant_documents("SOX controls or compliance testing")
    return {
        "docs_found": len(results),
        "samples": [r.page_content[:200] for r in results[:3]]
    }
