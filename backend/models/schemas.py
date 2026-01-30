from pydantic import BaseModel, Field
from datetime import date
from typing import List, Dict, Optional, Any, Annotated
from enum import Enum
import operator


class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveRequestInput(BaseModel):
    """Input model for leave request"""
    employee_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str


class LeaveRequestResponse(BaseModel):
    """Response model for leave request"""
    request_id: str
    status: LeaveStatus
    message: str


class LeaveBalance(BaseModel):
    """Leave balance model"""
    employee_id: str
    annual_leave: float = 20.0
    sick_leave: float = 10.0
    personal_leave: float = 5.0
    maternity_leave: float = 0.0
    paternity_leave: float = 0.0


class PayStub(BaseModel):
    """Pay stub model"""
    employee_id: str
    pay_period: str
    gross_salary: float
    deductions: Dict[str, float]
    net_salary: float
    pay_date: date


class Employee(BaseModel):
    """Employee model"""
    employee_id: str
    name: str
    email: str
    department: str
    hire_date: date


# LangGraph State
class AgentState(BaseModel):
    """State for the HR Agent workflow"""
    employee_id: str
    query: str
    messages: Annotated[List[Dict[str, Any]], operator.add] = Field(default_factory=list)

    # Context from RAG
    context: str = ""

    # Agent results
    intent: str = ""
    leave_balance: Optional[LeaveBalance] = None
    pay_stubs: List[PayStub] = Field(default_factory=list)
    leave_request_result: Optional[LeaveRequestResponse] = None
    policy_response: str = ""

    # Final response
    final_response: str = ""

    # Tool calls tracking
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


# API Models
class ChatRequest(BaseModel):
    """Chat request model"""
    employee_id: str
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    employee_id: str
    thread_id: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
