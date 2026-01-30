"""
HR System API Client
This service makes REST API calls to the HR system for:
- Leave balance retrieval
- Leave submission
- Pay stub retrieval
"""
import httpx
from typing import List, Optional
from datetime import date, timedelta
import json
import uuid

from models.schemas import (
    LeaveBalance,
    LeaveRequestInput,
    LeaveRequestResponse,
    LeaveStatus,
    PayStub,
)


class HRSystemClient:
    """Client for HR System REST APIs"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

        # In-memory mock data (in production, these would be actual API calls)
        self._mock_leave_balances = {
            "EMP001": LeaveBalance(
                employee_id="EMP001",
                annual_leave=15.5,
                sick_leave=8.0,
                personal_leave=3.0
            ),
            "EMP002": LeaveBalance(
                employee_id="EMP002",
                annual_leave=20.0,
                sick_leave=10.0,
                personal_leave=5.0
            ),
            "EMP003": LeaveBalance(
                employee_id="EMP003",
                annual_leave=12.0,
                sick_leave=6.0,
                personal_leave=4.0
            ),
        }

        self._mock_pay_stubs = self._generate_mock_pay_stubs()

    def _generate_mock_pay_stubs(self) -> dict:
        """Generate mock pay stubs for demo"""
        stubs = {}
        employees = ["EMP001", "EMP002", "EMP003"]

        for emp_id in employees:
            stubs[emp_id] = []
            base_salary = 7500.0 if emp_id == "EMP001" else (8500.0 if emp_id == "EMP002" else 6500.0)

            for i in range(6):
                pay_date = date.today() - timedelta(days=30 * i)
                deductions = {
                    "federal_tax": round(base_salary * 0.12, 2),
                    "state_tax": round(base_salary * 0.05, 2),
                    "health_insurance": 200.0,
                    "dental_insurance": 50.0,
                    "retirement_401k": round(base_salary * 0.06, 2),
                    "social_security": round(base_salary * 0.062, 2),
                }
                total_deductions = sum(deductions.values())

                stubs[emp_id].append(PayStub(
                    employee_id=emp_id,
                    pay_period=pay_date.strftime("%B %Y"),
                    gross_salary=base_salary,
                    deductions=deductions,
                    net_salary=round(base_salary - total_deductions, 2),
                    pay_date=pay_date
                ))

        return stubs

    async def get_leave_balance(self, employee_id: str) -> Optional[LeaveBalance]:
        """
        Get leave balance for an employee via REST API

        In production, this would call:
        GET {base_url}/employees/{employee_id}/leave-balance
        """
        try:
            # Mock implementation - in production, uncomment the API call
            # response = await self.client.get(
            #     f"{self.base_url}/employees/{employee_id}/leave-balance"
            # )
            # response.raise_for_status()
            # return LeaveBalance(**response.json())

            # Return mock data
            if employee_id in self._mock_leave_balances:
                return self._mock_leave_balances[employee_id]

            # Default balance for unknown employees
            return LeaveBalance(
                employee_id=employee_id,
                annual_leave=20.0,
                sick_leave=10.0,
                personal_leave=5.0
            )

        except Exception as e:
            print(f"Error fetching leave balance: {e}")
            return None

    async def submit_leave_request(self, request: LeaveRequestInput) -> LeaveRequestResponse:
        """
        Submit leave request via REST API

        In production, this would call:
        POST {base_url}/employees/{employee_id}/leave-requests
        """
        try:
            # Mock implementation - in production, uncomment the API call
            # response = await self.client.post(
            #     f"{self.base_url}/employees/{request.employee_id}/leave-requests",
            #     json=request.model_dump(mode="json")
            # )
            # response.raise_for_status()
            # return LeaveRequestResponse(**response.json())

            # Validate leave balance
            balance = await self.get_leave_balance(request.employee_id)
            if not balance:
                return LeaveRequestResponse(
                    request_id="",
                    status=LeaveStatus.REJECTED,
                    message="Employee not found"
                )

            days_requested = (request.end_date - request.start_date).days + 1
            leave_attr = f"{request.leave_type.value}_leave"
            available = getattr(balance, leave_attr, 0)

            if days_requested > available:
                return LeaveRequestResponse(
                    request_id="",
                    status=LeaveStatus.REJECTED,
                    message=f"Insufficient {request.leave_type.value} leave balance. "
                            f"Available: {available} days, Requested: {days_requested} days"
                )

            # Create successful response
            request_id = f"LR-{uuid.uuid4().hex[:8].upper()}"

            # Update mock balance
            if request.employee_id in self._mock_leave_balances:
                setattr(
                    self._mock_leave_balances[request.employee_id],
                    leave_attr,
                    available - days_requested
                )

            return LeaveRequestResponse(
                request_id=request_id,
                status=LeaveStatus.PENDING,
                message=f"Leave request submitted successfully. "
                        f"Request ID: {request_id}. "
                        f"{days_requested} day(s) of {request.leave_type.value} leave "
                        f"from {request.start_date} to {request.end_date}. "
                        f"Pending manager approval."
            )

        except Exception as e:
            return LeaveRequestResponse(
                request_id="",
                status=LeaveStatus.REJECTED,
                message=f"Error submitting leave request: {str(e)}"
            )

    async def get_pay_stubs(self, employee_id: str, months: int = 6) -> List[PayStub]:
        """
        Get pay stubs for an employee via REST API

        In production, this would call:
        GET {base_url}/employees/{employee_id}/pay-stubs?months={months}
        """
        try:
            # Mock implementation - in production, uncomment the API call
            # response = await self.client.get(
            #     f"{self.base_url}/employees/{employee_id}/pay-stubs",
            #     params={"months": months}
            # )
            # response.raise_for_status()
            # return [PayStub(**stub) for stub in response.json()]

            # Return mock data
            if employee_id in self._mock_pay_stubs:
                return self._mock_pay_stubs[employee_id][:months]

            # Generate default pay stubs for unknown employees
            stubs = []
            for i in range(months):
                pay_date = date.today() - timedelta(days=30 * i)
                deductions = {
                    "federal_tax": 900.0,
                    "state_tax": 375.0,
                    "health_insurance": 200.0,
                    "retirement_401k": 450.0,
                }
                stubs.append(PayStub(
                    employee_id=employee_id,
                    pay_period=pay_date.strftime("%B %Y"),
                    gross_salary=7500.0,
                    deductions=deductions,
                    net_salary=5575.0,
                    pay_date=pay_date
                ))
            return stubs

        except Exception as e:
            print(f"Error fetching pay stubs: {e}")
            return []

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
