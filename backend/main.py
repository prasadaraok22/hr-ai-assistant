"""
HR AI Assistant - Main Application
Production-ready FastAPI application for HR Operations
"""
# === SSL BYPASS - MUST BE FIRST IMPORT ===
import ssl_bypass  # noqa: F401
# === END SSL BYPASS ===

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("=" * 60)
    print("🚀 Starting HR AI Assistant")
    print("=" * 60)

    # Startup: Initialize orchestrator (lazy loading on first request)
    yield

    # Shutdown: Cleanup
    print("👋 Shutting down HR AI Assistant")


app = FastAPI(
    title="HR AI Assistant",
    description="""
    Production-ready Agentic AI application for HR Operations and Employee Support.
    
    ## Features
    - 📋 **HR Policy Q&A**: RAG-based answers to HR policy questions
    - 🏖️ **Leave Management**: Check balance and submit leave requests
    - 💰 **Payroll Information**: View recent pay stubs and salary details
    
    ## Tech Stack
    - **LangGraph**: Agentic workflow orchestration
    - **LangChain**: LLM framework
    - **Mistral AI**: LLM and embeddings
    - **FAISS**: Vector database
    - **LangSmith**: Observability and monitoring
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HR AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
