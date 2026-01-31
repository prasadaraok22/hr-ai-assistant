"""
HR Orchestrator Agent
Main agent that coordinates all HR operations using LangGraph
"""
import asyncio
from typing import Literal, Any, Dict, List
from datetime import date

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from config.settings import get_settings, setup_langsmith
from models.schemas import AgentState
from services.vector_store import HRVectorStore
from services.hr_api_client import HRSystemClient
from agents.policy_agent import HRPolicyAgent
from agents.tools import HR_TOOLS, set_hr_client, get_leave_balance, submit_leave_request, get_pay_stubs


class HROrchestrator:
    """Main orchestrator for HR AI Assistant using LangGraph"""

    def __init__(self):
        self.settings = get_settings()

        # Setup LangSmith observability
        setup_langsmith()

        # Initialize services
        self.hr_client = HRSystemClient(self.settings.hr_api_base_url)
        set_hr_client(self.hr_client)

        self.vector_store = HRVectorStore(
            mistral_api_key=self.settings.mistral_api_key,
            vector_store_path=self.settings.vector_store_path,
            policies_path=self.settings.hr_policies_path
        )

        # Initialize policy agent
        self.policy_agent = HRPolicyAgent(
            mistral_api_key=self.settings.mistral_api_key,
            vector_store=self.vector_store
        )

        # Initialize LLM with tools
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            mistral_api_key=self.settings.mistral_api_key,
            temperature=0.1
        )
        self.llm_with_tools = self.llm.bind_tools(HR_TOOLS)

        # Tool mapping for direct execution
        self.tool_map = {
            "get_leave_balance": get_leave_balance,
            "submit_leave_request": submit_leave_request,
            "get_pay_stubs": get_pay_stubs,
        }

        # Intent classifier
        self.classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for an HR AI Assistant. Classify the user's query into ONE of these categories:

POLICY_QUESTION - Questions about HR policies, benefits, procedures, rules, or general HR information
LEAVE_BALANCE - Checking current leave balance, PTO balance, remaining vacation days
LEAVE_REQUEST - Requesting time off, submitting leave, applying for vacation/sick/personal days
PAY_STUB - Questions about salary, paycheck, pay stubs, pay history, deductions
GENERAL - Greetings, thanks, unclear queries, or requests outside HR scope

Respond with ONLY the category name, nothing else."""),
            ("human", "{query}")
        ])

        # Build the workflow
        self.app = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("policy_rag", self._handle_policy_question)
        workflow.add_node("tool_agent", self._call_tool_agent)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("general_response", self._handle_general)
        workflow.add_node("finalize", self._finalize_response)

        # Set entry point
        workflow.set_entry_point("classify_intent")

        # Add conditional routing from classifier
        workflow.add_conditional_edges(
            "classify_intent",
            self._route_by_intent,
            {
                "policy_rag": "policy_rag",
                "tool_agent": "tool_agent",
                "general": "general_response"
            }
        )

        # Tool agent routing - check if tools need to be executed
        workflow.add_conditional_edges(
            "tool_agent",
            self._should_execute_tools,
            {
                "execute": "execute_tools",
                "skip": "finalize"
            }
        )

        # After tool execution, go to finalize
        workflow.add_edge("execute_tools", "finalize")

        # All paths lead to finalize then END
        workflow.add_edge("policy_rag", "finalize")
        workflow.add_edge("general_response", "finalize")
        workflow.add_edge("finalize", END)

        # Compile with memory checkpointer
        checkpointer = MemorySaver()
        return workflow.compile(checkpointer=checkpointer)

    def _classify_intent(self, state: AgentState) -> dict:
        """Classify the user's intent"""
        print("\n" + "=" * 50)
        print("🔍 Classifying Intent")
        print("=" * 50)

        chain = self.classifier_prompt | self.llm
        response = chain.invoke({"query": state.query})
        intent = response.content.strip().upper()

        print(f"Query: {state.query}")
        print(f"Intent: {intent}")

        return {"intent": intent}

    def _route_by_intent(self, state: AgentState) -> Literal["policy_rag", "tool_agent", "general"]:
        """Route to appropriate handler based on intent"""
        intent = state.intent

        if intent == "POLICY_QUESTION":
            return "policy_rag"
        elif intent in ["LEAVE_BALANCE", "LEAVE_REQUEST", "PAY_STUB"]:
            return "tool_agent"
        else:
            return "general"

    def _handle_policy_question(self, state: AgentState) -> dict:
        """Handle policy questions using RAG"""
        print("\n" + "=" * 50)
        print("📚 Policy RAG Agent")
        print("=" * 50)

        response = self.policy_agent.answer_sync(state.query)

        return {"policy_response": response}

    def _call_tool_agent(self, state: AgentState) -> dict:
        """Call the tool-equipped agent to determine which tools to use"""
        print("\n" + "=" * 50)
        print("🔧 Tool Agent")
        print("=" * 50)

        # Create system message based on intent
        system_message = f"""You are an HR Assistant helping employee {state.employee_id}.
Today's date is {date.today().isoformat()}.

Based on the user's request, use the appropriate tool:
- get_leave_balance: To check remaining leave days
- submit_leave_request: To submit a leave request (extract dates in YYYY-MM-DD format)
- get_pay_stubs: To view salary/paycheck information

Always use the employee_id: {state.employee_id}
Extract all required information from the user's message.
If information is missing for a leave request, ask the user to provide it."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": state.query}
        ]

        response = self.llm_with_tools.invoke(messages)

        # Store tool calls for tracking
        tool_calls = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tc in response.tool_calls:
                tool_calls.append({
                    "name": tc["name"],
                    "args": tc["args"]
                })
            print(f"Tool calls identified: {tool_calls}")

        # If no tool calls but there's content, use that as the response
        if not tool_calls and response.content:
            return {"policy_response": response.content, "tool_calls": []}

        return {"tool_calls": tool_calls}

    def _should_execute_tools(self, state: AgentState) -> Literal["execute", "skip"]:
        """Determine if tools should be executed"""
        if state.tool_calls and len(state.tool_calls) > 0:
            return "execute"
        return "skip"

    def _execute_tools(self, state: AgentState) -> dict:
        """Execute the tools directly"""
        print("\n" + "=" * 50)
        print("⚙️ Executing Tools")
        print("=" * 50)

        results = []

        for tool_call in state.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"Executing: {tool_name} with args: {tool_args}")

            if tool_name in self.tool_map:
                tool_func = self.tool_map[tool_name]
                try:
                    # Execute tool asynchronously
                    result = asyncio.get_event_loop().run_until_complete(
                        tool_func.ainvoke(tool_args)
                    )
                    results.append(result)
                    print(f"Tool result: {result[:100]}..." if len(str(result)) > 100 else f"Tool result: {result}")
                except RuntimeError:
                    # If no event loop, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(tool_func.ainvoke(tool_args))
                        results.append(result)
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"Error executing tool {tool_name}: {e}")
                    results.append(f"Error executing {tool_name}: {str(e)}")
            else:
                results.append(f"Unknown tool: {tool_name}")

        # Combine results
        combined_result = "\n\n".join(results) if results else "No results from tools."

        return {"policy_response": combined_result}

    def _handle_general(self, state: AgentState) -> dict:
        """Handle general queries and greetings"""
        print("\n" + "=" * 50)
        print("💬 General Response")
        print("=" * 50)

        response = """Hello! I'm your HR AI Assistant. I can help you with:

🏖️ **Leave Management**
   • Check your leave balance
   • Submit leave requests
   
💰 **Payroll Information**
   • View your recent pay stubs
   • Understand your deductions
   
📋 **HR Policies**
   • Leave policies and procedures
   • Healthcare benefits
   • Retirement benefits
   • And more!

How can I assist you today?"""

        return {"policy_response": response}

    def _finalize_response(self, state: AgentState) -> dict:
        """Finalize the response"""
        print("\n" + "=" * 50)
        print("✅ Finalizing Response")
        print("=" * 50)

        # Use policy_response as final response
        final_response = state.policy_response if state.policy_response else ""

        # Default response if nothing else
        if not final_response:
            final_response = "I apologize, but I couldn't process your request. Please try again or contact HR directly."

        print(f"Final response length: {len(final_response)} chars")

        return {"final_response": final_response}

    async def chat(self, employee_id: str, query: str, thread_id: str = "default") -> dict:
        """Process a chat message"""
        initial_state = AgentState(
            employee_id=employee_id,
            query=query
        )

        config = {
            "configurable": {"thread_id": f"{employee_id}-{thread_id}"},
            "recursion_limit": 25
        }

        # Run the workflow
        result = await self.app.ainvoke(initial_state, config=config)

        return {
            "response": result.get("final_response", ""),
            "employee_id": employee_id,
            "thread_id": thread_id,
            "tool_calls": result.get("tool_calls", [])
        }

    def chat_sync(self, employee_id: str, query: str, thread_id: str = "default") -> dict:
        """Synchronous version of chat"""
        initial_state = AgentState(
            employee_id=employee_id,
            query=query
        )

        config = {
            "configurable": {"thread_id": f"{employee_id}-{thread_id}"},
            "recursion_limit": 25
        }

        result = self.app.invoke(initial_state, config=config)

        return {
            "response": result.get("final_response", ""),
            "employee_id": employee_id,
            "thread_id": thread_id,
            "tool_calls": result.get("tool_calls", [])
        }

    def get_graph_visualization(self) -> str:
        """Get Mermaid diagram of the workflow"""
        return self.app.get_graph().draw_mermaid()
