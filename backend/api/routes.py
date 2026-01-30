"""
FastAPI Routes for HR AI Assistant
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio

from models.schemas import ChatRequest, ChatResponse
from agents.orchestrator import HROrchestrator

router = APIRouter()

# Singleton orchestrator instance
_orchestrator: Optional[HROrchestrator] = None


def get_orchestrator() -> HROrchestrator:
    """Get or create the orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        print("Initializing HR Orchestrator...")
        _orchestrator = HROrchestrator()
        print("✓ HR Orchestrator initialized")
    return _orchestrator


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HR AI Assistant",
        "version": "1.0.0"
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for HR AI Assistant

    - Processes employee queries
    - Routes to appropriate agent (Policy RAG, Leave, Payroll)
    - Returns AI-generated response
    """
    try:
        orchestrator = get_orchestrator()
        result = await orchestrator.chat(
            employee_id=request.employee_id,
            query=request.message,
            thread_id=request.thread_id
        )
        return ChatResponse(**result)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph")
async def get_workflow_graph():
    """
    Get the workflow graph visualization (Mermaid format)
    """
    try:
        orchestrator = get_orchestrator()
        mermaid = orchestrator.get_graph_visualization()
        return {"graph": mermaid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-policies")
async def refresh_policies(background_tasks: BackgroundTasks):
    """
    Refresh the policy vector store
    Re-indexes all HR policy documents
    """
    try:
        orchestrator = get_orchestrator()
        background_tasks.add_task(orchestrator.vector_store.refresh_index)
        return {"message": "Policy refresh initiated", "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mock HR System API endpoints (for demo/testing)
@router.get("/v1/hr-system/employees/{employee_id}/leave-balance")
async def mock_leave_balance(employee_id: str):
    """Mock endpoint for leave balance API"""
    orchestrator = get_orchestrator()
    balance = await orchestrator.hr_client.get_leave_balance(employee_id)
    if balance:
        return balance.model_dump()
    raise HTTPException(status_code=404, detail="Employee not found")


@router.get("/v1/hr-system/employees/{employee_id}/pay-stubs")
async def mock_pay_stubs(employee_id: str, months: int = 6):
    """Mock endpoint for pay stubs API"""
    orchestrator = get_orchestrator()
    stubs = await orchestrator.hr_client.get_pay_stubs(employee_id, months)
    return [stub.model_dump() for stub in stubs]
