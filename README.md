# HR AI Assistant

A production-ready Agentic AI application for HR Operations and Employee Support built with LangGraph, LangChain, Mistral AI, and React.

## Features

- 📋 **HR Policy Q&A**: RAG-based answers to HR policy questions (leave, healthcare, retirement)
- 🏖️ **Leave Management**: Check balance and submit leave requests via REST APIs
- 💰 **Payroll Information**: View recent pay stubs and salary details
- 🔍 **LangSmith Observability**: Full tracing and monitoring of AI operations

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance web framework
- **LangChain** - LLM framework
- **LangGraph** - Agentic workflow orchestration
- **Mistral AI** - LLM and embeddings
- **FAISS** - Vector database
- **LangSmith** - Observability and monitoring

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Lucide React** - Icons

## Project Structure

```
hr-ai-assistant/
├── backend/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── hr_api_client.py     # REST API client for HR system
│   │   ├── document_loader.py   # PDF document loader
│   │   └── vector_store.py      # FAISS vector store
│   ├── agents/
│   │   ├── tools.py             # LangChain tools for HR operations
│   │   ├── policy_agent.py      # RAG agent for policy questions
│   │   └── orchestrator.py      # LangGraph workflow orchestrator
│   ├── api/
│   │   └── routes.py            # FastAPI routes
│   ├── data/
│   │   └── hr_policies/         # HR policy PDFs
│   ├── main.py                  # Application entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities and API client
│   │   ├── types/               # TypeScript types
│   │   └── App.tsx              # Main application
│   ├── index.html
│   └── package.json
│
└── README.md
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Chat UI     │  │ Quick       │  │ Employee Selection      │  │
│  │             │  │ Actions     │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   LangGraph Orchestrator                     ││
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐               ││
│  │  │ Intent   │───▶│ Router   │───▶│ Agent    │               ││
│  │  │Classifier│    │          │    │ Nodes    │               ││
│  │  └──────────┘    └──────────┘    └──────────┘               ││
│  │                       │                                      ││
│  │       ┌───────────────┼───────────────┐                     ││
│  │       ▼               ▼               ▼                     ││
│  │  ┌─────────┐    ┌──────────┐    ┌──────────┐               ││
│  │  │ Policy  │    │ Leave    │    │ Payroll  │               ││
│  │  │ RAG     │    │ Tools    │    │ Tools    │               ││
│  │  └────┬────┘    └────┬─────┘    └────┬─────┘               ││
│  │       │              │               │                      ││
│  └───────┼──────────────┼───────────────┼──────────────────────┘│
│          ▼              ▼               ▼                       │
│  ┌───────────┐   ┌─────────────────────────────┐               │
│  │  FAISS    │   │     HR System REST APIs     │               │
│  │  Vector   │   │  (Leave Balance, Submit,    │               │
│  │  Store    │   │   Pay Stubs)                │               │
│  └───────────┘   └─────────────────────────────┘               │
│          │                                                      │
│          ▼                                                      │
│  ┌───────────────┐     ┌─────────────────────┐                 │
│  │ Mistral AI    │     │    LangSmith        │                 │
│  │ (LLM + Embed) │     │   (Observability)   │                 │
│  └───────────────┘     └─────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Mistral AI API key
- (Optional) LangSmith API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run the backend
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Mistral AI (Required)
MISTRAL_API_KEY=your_mistral_api_key_here

# LangSmith (Optional - for observability)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=hr-ai-assistant
LANGSMITH_TRACING=true

# Database
DATABASE_URL=sqlite:///./hr_database.db

# Vector Store
VECTOR_STORE_PATH=./vector_store
HR_POLICIES_PATH=./data/hr_policies
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/chat` | Send chat message |
| GET | `/api/graph` | Get workflow visualization |
| POST | `/api/refresh-policies` | Refresh policy index |

### Chat Request Example

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "message": "What is my leave balance?",
    "thread_id": "default"
  }'
```

## Usage Examples

### Check Leave Balance
```
User: What is my current leave balance?
Assistant: Leave Balance for EMP001:
📅 Annual Leave (PTO): 15.5 days
🏥 Sick Leave: 8.0 days
👤 Personal Leave: 3.0 days
```

### Submit Leave Request
```
User: I want to take 3 days of annual leave from 2024-03-15 to 2024-03-17 for a family vacation
Assistant: ✅ Leave Request Submitted Successfully!
📋 Request ID: LR-A1B2C3D4
📅 Type: Annual Leave
📆 Dates: 2024-03-15 to 2024-03-17
📝 Reason: family vacation
⏳ Status: Pending Manager Approval
```

### View Pay Stubs
```
User: Show me my recent pay stubs
Assistant: 💰 Pay Stubs for EMP001 (Last 6 months):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 January 2024 (Paid: 2024-01-31)
  💵 Gross Salary: $7,500.00
  📉 Deductions: ...
  ✅ Net Salary: $5,575.00
```

### Ask Policy Questions
```
User: What are the healthcare benefits?
Assistant: Based on our Healthcare Benefits policy...
[Detailed response from RAG system]
```

## Adding HR Policy Documents

1. Place PDF files in `backend/data/hr_policies/`
2. Call the refresh endpoint or restart the backend:
   ```bash
   curl -X POST "http://localhost:8000/api/refresh-policies"
   ```

## LangSmith Observability

When configured with a LangSmith API key, all LLM calls and agent traces are logged for:
- Performance monitoring
- Debugging
- Cost tracking
- Quality evaluation

View traces at: https://smith.langchain.com

## Development

### Running Tests
```bash
cd backend
pytest tests/
```

### Code Formatting
```bash
# Backend
black backend/
isort backend/

# Frontend
npm run lint
npm run format
```

## License

MIT
