import uuid
from db import init_db
from graph import app

# 1. Create the final Postgres table if it doesn't exist yet
print("Initializing database...")
init_db()

# 2. Provide the tricky text that causes a schema failure
messy_text = """
Log entry 402: We saw the thing again. Locals call it the 'Swamp Stalker'. 
It had glowing eyes and could turn invisible. Spooked us near Blackwood Ridge. 
Threat level is definitely a 'High'. Nobody died but two guys twisted their ankles running.
"""

# 3. LangGraph requires a unique thread_id to save the state in Postgres
config = {"configurable": {"thread_id": str(uuid.uuid4())}}
initial_state = {
    "raw_text": messy_text,
    "retries": 0,
    "validation_errors": None,
    "extracted_data": None
}

print("\nRunning the agentic pipeline...")

# We will use .stream() here so we can watch the agent self-heal in the terminal
for event in app.stream(initial_state, config=config):
    for node_name, node_state in event.items():
        print(f"\n⚙️ Executed Node: {node_name}")

        if node_name == "validate_node" and node_state.get("validation_errors"):
            print(f"   🚨 ERROR DETECTED: {node_state['validation_errors']}")
            print("   -> Routing back to LLM for self-correction...")

        elif node_name == "success":
            print("\n✅ Final Clean Data Saved to Postgres:")
            print(node_state["extracted_data"])