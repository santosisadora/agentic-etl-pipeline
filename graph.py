import os
from typing import TypedDict, Optional, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Import the DB logic and LangGraph checkpointer tools
from db import save_encounter, DB_URI
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

load_dotenv()


# ==========================================
# PHASE 1: The Pydantic Schema
# ==========================================
class MonsterEncounter(BaseModel):
    monster_name: str = Field(description="Name of the cryptid or monster")
    threat_level: int = Field(description="Threat level from 1 to 10. Must be an integer.")
    abilities: List[str] = Field(description="List of supernatural or physical abilities")
    location_spotted: str = Field(description="Where the encounter took place")
    casualties: int = Field(default=0, description="Number of people injured or killed")


# ==========================================
# PHASE 2: LangGraph State & Nodes
# ==========================================
class PipelineState(TypedDict):
    raw_text: str
    extracted_data: Optional[dict]
    validation_errors: Optional[str]
    retries: int


llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0
)

extractor_llm = llm.with_structured_output(MonsterEncounter, method="json_schema")


def extract_node(state: PipelineState):
    retries = state.get("retries", 0)
    prompt = f"Extract the monster encounter details from this text:\n\n{state['raw_text']}"

    if state.get("validation_errors"):
        prompt += f"\n\nWARNING: Your previous attempt failed with these schema validation errors:\n{state['validation_errors']}\nPlease fix them and return the correct JSON structure."

    try:
        result = extractor_llm.invoke(prompt)
        extracted_dict = result.model_dump()
        return {"extracted_data": extracted_dict, "retries": retries + 1, "validation_errors": None}
    except Exception as e:
        return {"extracted_data": None, "retries": retries + 1,
                "validation_errors": f"Failed to parse LLM output: {str(e)}"}


def validate_node(state: PipelineState):
    extracted = state.get("extracted_data")
    if not extracted:
        return {"validation_errors": "No data was extracted by the LLM."}

    try:
        MonsterEncounter(**extracted)
        return {"validation_errors": None}
    except ValidationError as e:
        return {"validation_errors": str(e)}


def route_after_validation(state: PipelineState):
    if not state.get("validation_errors"):
        return "success"
    if state["retries"] >= 3:
        return "human_review"
    return "extract_node"


def success_node(state: PipelineState):
    """Save the clean data to our relational database table."""
    record_id = save_encounter(state["extracted_data"])
    state["extracted_data"]["db_id"] = record_id
    return state


def human_review_node(state: PipelineState):
    """Dead-letter queue for items the LLM couldn't fix."""
    return state


# ==========================================
# PHASE 3: Compile the Graph with Checkpointing
# ==========================================
workflow = StateGraph(PipelineState)

workflow.add_node("extract_node", extract_node)
workflow.add_node("validate_node", validate_node)
workflow.add_node("success", success_node)
workflow.add_node("human_review", human_review_node)

workflow.set_entry_point("extract_node")
workflow.add_edge("extract_node", "validate_node")

workflow.add_conditional_edges(
    "validate_node",
    route_after_validation,
    {
        "success": "success",
        "extract_node": "extract_node",
        "human_review": "human_review"
    }
)

# Set up the Postgres connection pool with a maximum size of 10 connections
connection_pool = ConnectionPool(
    conninfo=DB_URI,
    max_size=10,
    kwargs={"autocommit": True}
)

# Initialize the saver which ensures data integrity by durably storing checkpoints
checkpointer = PostgresSaver(connection_pool)
checkpointer.setup()

# Compile the app using the Postgres checkpointer
app = workflow.compile(checkpointer=checkpointer)