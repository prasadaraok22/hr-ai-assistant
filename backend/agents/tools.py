"""
HR Tools for LangGraph Agents
These tools invoke REST APIs for HR operations
"""
from datetime import datetime, date
from typing import Optional
from langchain_core.tools import tool

from models.schemas import LeaveType, LeaveRequestInput
from services.hr_api_client import HRSystemClient


# Global HR client instance (will be set by orchestrator)
_hr_client: Optional[HRSystemClient] = None


def set_hr_client(client: HRSystemClient):
    """Set the global HR client instance"""
    global _hr_client
    _hr_client = client


def get_hr_client() -> HRSystemClient:
    """Get the global HR client instance"""
    if _hr_client is None:
        raise ValueError("HR client not initialized")
    return _hr_client


@tool
async def get_leave_balance(employee_id: str) -> str:
    """
    Get the current leave balance for an employee.
    Use this tool when the user asks about their remaining leave days,
    PTO balance, or how many vacation/sick/personal days they have left.

    Args:
        employee_id: The employee's ID (e.g., EMP001)

    Returns:
        A formatted string with the employee's leave balance
    """
    client = get_hr_client()
    balance = await client.get_leave_balance(employee_id)

    if not balance:
        return f"Unable to retrieve leave balance for employee {employee_id}. Please contact HR."

    return f"""Leave Balance for {employee_id}:

📅 Annual Leave (PTO): {balance.annual_leave} days
🏥 Sick Leave: {balance.sick_leave} days
👤 Personal Leave: {balance.personal_leave} days

Total Available: {balance.annual_leave + balance.sick_leave + balance.personal_leave} days"""


@tool
async def submit_leave_request(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
) -> str:
    """
    Submit a leave request for an employee.
    Use this tool when the user wants to request time off, apply for leave,
    or book vacation/sick/personal days.

    Args:
        employee_id: The employee's ID (e.g., EMP001)
        leave_type: Type of leave (annual, sick, personal, maternity, paternity)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        reason: Reason for the leave request

    Returns:
        A formatted string with the leave request result
    """
    client = get_hr_client()

    try:
        # Parse and validate leave type
        leave_type_enum = LeaveType(leave_type.lower())
    except ValueError:
        return f"Invalid leave type: {leave_type}. Valid types are: annual, sick, personal, maternity, paternity"

    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-03-15)"

    # Validate dates
    if end < start:
        return "End date cannot be before start date"

    if start < date.today():
        return "Cannot submit leave request for past dates"

    # Create and submit request
    request = LeaveRequestInput(
        employee_id=employee_id,
        leave_type=leave_type_enum,
        start_date=start,
        end_date=end,
        reason=reason
    )

    result = await client.submit_leave_request(request)

    if result.status.value == "pending":
        return f"""✅ Leave Request Submitted Successfully!

📋 Request ID: {result.request_id}
📅 Type: {leave_type.capitalize()} Leave
📆 Dates: {start_date} to {end_date}
📝 Reason: {reason}
⏳ Status: Pending Manager Approval

{result.message}"""
    else:
        return f"""❌ Leave Request Failed

{result.message}

Please check your leave balance and try again, or contact HR for assistance."""


@tool
async def get_pay_stubs(employee_id: str, months: int = 6) -> str:
    """
    Get recent pay stub information for an employee.
    Use this tool when the user asks about their paycheck, salary details,
    pay history, or wants to see their recent pay stubs.

    Args:
        employee_id: The employee's ID (e.g., EMP001)
        months: Number of months of pay stubs to retrieve (default: 6)

    Returns:
        A formatted string with pay stub details
    """
    client = get_hr_client()
    pay_stubs = await client.get_pay_stubs(employee_id, months)

    if not pay_stubs:
        return f"No pay stub records found for employee {employee_id}. Please contact HR."

    result = f"💰 Pay Stubs for {employee_id} (Last {len(pay_stubs)} months):\n\n"

    for stub in pay_stubs:
        deductions_list = "\n".join([
            f"    • {key.replace('_', ' ').title()}: ${value:,.2f}"
            for key, value in stub.deductions.items()
        ])

        result += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {stub.pay_period} (Paid: {stub.pay_date})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  💵 Gross Salary: ${stub.gross_salary:,.2f}
  
  📉 Deductions:
{deductions_list}
  
  ✅ Net Salary: ${stub.net_salary:,.2f}

"""

    return result


# List of all available tools
HR_TOOLS = [get_leave_balance, submit_leave_request, get_pay_stubs]
