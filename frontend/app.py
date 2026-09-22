import streamlit as st
import time
import uuid
import pandas as pd
from graph import app

# 1. Page Config
st.set_page_config(layout="wide", page_title="Agentic ETL", initial_sidebar_state="collapsed")

# 2. Custom CSS Injection (The Magic)
st.markdown("""
    <style>
        /* Hide default Streamlit chrome */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Modern, glowing button */
        .stButton > button {
            width: 100%;
            background-color: #6366f1;
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #4f46e5;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
            border-color: #6366f1;
            color: white;
        }

        /* Live Terminal Box */
        .terminal-box {
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: 'Courier New', Courier, monospace;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #334155;
            height: 350px;
            overflow-y: auto;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
        }
        .term-info { color: #38bdf8; }
        .term-warn { color: #facc15; }
        .term-error { color: #f87171; }
        .term-success { color: #4ade80; }

        /* Title Styling */
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        .gradient-text {
            background: -webkit-linear-gradient(45deg, #6366f1, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown('<p class="main-title"><span class="gradient-text">Agentic</span> ETL Pipeline</p>', unsafe_allow_html=True)
st.markdown(
    "<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -10px;'>Autonomous unstructured data extraction and schema-healing.</p>",
    unsafe_allow_html=True)
st.divider()

# 4. Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📥 Raw Data Feed")
    default_text = "Log entry 402: We saw the thing again. Locals call it the 'Swamp Stalker'. It had glowing eyes and could turn invisible. Spooked us near Blackwood Ridge. Threat level is definitely a 'High'. Nobody died but two guys twisted their ankles running."

    raw_text = st.text_area("Unstructured Text", value=default_text, height=280, label_visibility="collapsed")
    start_button = st.button("🚀 Initialize Extraction Agent")

with col2:
    st.markdown("### ⚡ Agent Execution Logs")
    # This empty container will hold our custom HTML terminal
    terminal_placeholder = st.empty()

    # Render an empty terminal on load
    terminal_placeholder.markdown('<div class="terminal-box">Waiting for system initialization...</div>',
                                  unsafe_allow_html=True)

# 5. Execution Logic & UI Updates
if start_button and raw_text:
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "raw_text": raw_text,
        "retries": 0,
        "validation_errors": None,
        "extracted_data": None
    }

    # We build the terminal log string dynamically
    log_content = "<span class='term-info'>[SYSTEM] Booting LangGraph Orchestrator...</span><br/>"
    terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
    time.sleep(0.5)

    final_data = None

    for event in app.stream(initial_state, config=config):
        for node_name, node_state in event.items():

            if node_name == "extract_node":
                attempt = node_state.get('retries', 1)
                log_content += f"<span class='term-warn'>[AGENT] Attempt {attempt}: Executing Gemini 3.8 Flash extraction...</span><br/>"
                terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
                time.sleep(1.2)

            elif node_name == "validate_node":
                errors = node_state.get("validation_errors")
                if errors:
                    log_content += f"<span class='term-error'>[VALIDATION] FAILED: {errors}</span><br/>"
                    log_content += f"<span class='term-info'>[SYSTEM] Rerouting error context back to LLM for self-correction...</span><br/>"
                    terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>',
                                                  unsafe_allow_html=True)
                    time.sleep(2)
                else:
                    log_content += f"<span class='term-success'>[VALIDATION] PASSED: Output strictly matches Pydantic schema.</span><br/>"
                    terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>',
                                                  unsafe_allow_html=True)
                    time.sleep(0.8)

            elif node_name == "success":
                log_content += f"<span class='term-success'>[DATABASE] Committing clean payload to PostgreSQL...</span><br/>"
                log_content += f"<span class='term-info'>[SYSTEM] Pipeline execution completed successfully.</span>"
                terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
                final_data = node_state.get('extracted_data', {})

            elif node_name == "human_review":
                log_content += f"<span class='term-error'>[SYSTEM] FATAL: Max retries reached. Routing to dead-letter queue.</span><br/>"
                terminal_placeholder.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)
                break

    # 6. Render the final output as a sleek Database Table
    if final_data:
        st.divider()
        st.markdown("### 💾 Postgres Database Record")

        # Convert dictionary to Pandas DataFrame for a clean table UI
        df = pd.DataFrame([final_data])
        # Reorder columns to put db_id first
        cols = ['db_id'] + [col for col in df.columns if col != 'db_id']
        df = df[cols]

        st.dataframe(df, use_container_width=True, hide_index=True)