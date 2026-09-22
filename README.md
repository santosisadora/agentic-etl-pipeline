# 🧩 Agentic ETL Pipeline: Self-Healing Data Extractor

A production-ready, autonomous Extract, Transform, and Load (ETL) pipeline that leverages Agentic AI to map messy, unstructured text into strict database schemas. 

Unlike traditional brittle regex-based parsers, this pipeline utilizes a **self-healing LangGraph loop**. If the LLM generates a payload that violates the target database schema, the pipeline does not crash. Instead, it catches the validation error and routes the exact error context back to the LLM to dynamically reason and correct its own output before committing to PostgreSQL.

## 🚀 Business Value & Use Cases

This architecture solves the core problem of unstructured data ingestion at scale:
*   **Healthcare EMR Ingestion:** Automatically parse shorthand clinical dictations into strict patient databases without manual data entry.
*   **Security Incident Triage:** Ingest unstructured employee breach reports, extract compromised assets/IPs, and automatically format structured SOC tickets.
*   **Financial Processing:** Extract highly variable vendor invoices into a uniform SQL accounting schema.
*   **Customer Support Routing:** Parse rambling customer emails to classify hardware vs. software issues, extract product IDs, and populate structured Zendesk routing tables.

## 🏗️ Architecture & Tech Stack

The system is built as a fully decoupled, containerized architecture:

*   **Orchestration & State:** `LangGraph` for cyclic agentic routing and `PostgresSaver` for durable checkpoint memory.
*   **LLM Engine:** `Gemini 3.8 Flash` via `ChatGoogleGenerativeAI` for low-latency reasoning.
*   **Validation:** `Pydantic` for strict data typing and schema enforcement.
*   **Backend:** `FastAPI` providing asynchronous REST endpoints.
*   **Database:** `PostgreSQL` for both state storage and final data persistence.
*   **Frontend:** `React.js` + `Tailwind CSS v4` + `Vite` for a high-performance, developer-tool aesthetic dashboard.
*   **Observability:** `LangSmith` natively integrated for tracing execution graphs, token usage, and latency.

## ⚙️ Quickstart (Docker Compose)

The easiest way to run the entire stack (Database, Backend API, and React UI) is via Docker.

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/agentic-etl-pipeline.git](https://github.com/yourusername/agentic-etl-pipeline.git)
cd agentic-etl-pipeline
```

2. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=agentic-etl-pipeline

3. Launch the Stack

Bash
docker compose up --build
4. Access the Applications

React Dashboard: http://localhost:5173

FastAPI Swagger Docs: http://localhost:8000/docs

LangSmith Dashboard: Check your LangSmith portal to view live execution traces.

🛠️ Local Development Setup
If you prefer to run the services locally without Docker:

Backend Setup

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:fastapi_app --reload --port 8000
Frontend Setup

Bash
cd frontend-react
npm install
npm run dev


📝 License & Author
Developed by Isadora Santos.
Released under the MIT License.
