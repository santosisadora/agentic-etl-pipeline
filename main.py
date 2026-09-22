import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import app
from db import init_db

fastapi_app = FastAPI(
    title="Agentic ETL API",
    description="Endpoint for self-healing unstructured data extraction",
    version="1.0.0"
)

# Allow React frontend to communicate with this API
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ... (Keep the rest of your main.py exactly the same) ...


# Initialize the final database tables on startup
@fastapi_app.on_event("startup")
def startup_event():
    init_db()


class ExtractionRequest(BaseModel):
    raw_text: str


@fastapi_app.post("/extract")
def extract_data(request: ExtractionRequest):
    # LangGraph checkpointers require a unique thread_id to track conversation memory
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "raw_text": request.raw_text,
        "retries": 0,
        "validation_errors": None,
        "extracted_data": None
    }

    try:
        # invoke() runs the graph from start to END synchronously
        result = app.invoke(initial_state, config=config)

        # Check if it ended in the human_review dead-letter queue
        if result["retries"] >= 3 and result.get("validation_errors"):
            return {
                "status": "failed",
                "thread_id": thread_id,
                "retries_attempted": result["retries"],
                "final_error": result["validation_errors"],
                "message": "Agent failed to self-correct and was sent to human review."
            }

        return {
            "status": "success",
            "thread_id": thread_id,
            "retries_attempted": result["retries"],
            "data": result["extracted_data"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))