import streamlit as st
import os
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from src.graph_engine import CustomerSupportGraph
from src.ingestion import IngestionPipeline

# --- Page Config ---
st.set_page_config(
    page_title="iSupport assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .stSidebar {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    h1 {
        color: #58a6ff;
        font-family: 'Outfit', sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #58a6ff;
        color: #58a6ff;
    }
    .approval-box {
        background-color: #1c2128;
        border: 1px solid #f85149;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

@st.cache_resource
def get_engine():
    return CustomerSupportGraph()

def check_ollama_connection(url="http://localhost:11434"):
    import http.client
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        port = parsed.port if parsed.port else (80 if parsed.scheme == "http" else 443)
        conn = http.client.HTTPConnection(parsed.hostname, port, timeout=2)
        conn.request("GET", "/")
        response = conn.getresponse()
        return response.status == 200
    except Exception:
        return False

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Settings")
    
    # Ollama URL Setting
    ollama_url = st.text_input("🔗 Ollama Server URL", value="http://localhost:11434", help="Change this if using ngrok or a remote server.")
    st.session_state.ollama_url = ollama_url

    st.markdown("---")
    st.subheader("📁 Knowledge Base")
    st.markdown("Upload a PDF to ground the assistant's responses.")
    
    uploaded_file = st.file_uploader("Drop PDF here", type="pdf")
    if uploaded_file:
        file_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("✨ Process Knowledge", use_container_width=True):
            progress_text = "Parsing and Embedding PDF..."
            my_bar = st.progress(0, text=progress_text)
            
            for percent_complete in range(100):
                import time
                time.sleep(0.001)
                my_bar.progress(percent_complete + 1, text=progress_text)
            
            success = st.session_state.ingestion.process_pdf(file_path)
            if success:
                st.success("✅ Knowledge base updated!")
            else:
                st.error("❌ Failed to process PDF.")

    st.markdown("---")
    st.subheader("🖥️ System Health")
    ollama_ok = check_ollama_connection(st.session_state.ollama_url)
    if ollama_ok:
        st.success(f"Ollama: Online")
    else:
        st.error(f"Ollama: Offline")
        
    db_path = "data/chroma_db"
    if os.path.exists(db_path):
        st.success("Vector DB: Initialized")
    else:
        st.warning("Vector DB: Not Found")

    st.markdown("---")
    st.subheader("🗑️ Reset Session")
    if st.button("Clear Memory", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

if "engine" not in st.session_state:
    connected = check_ollama_connection(st.session_state.ollama_url)
    if not connected:
        st.error(f"❌ **Ollama Not Detected at {st.session_state.ollama_url}**")
        st.markdown(f"""
            **How to connect:**
            1. Ensure Ollama is running.
            2. If remote, ensure the URL is public (e.g., ngrok).
            3. On your local machine, run: `set OLLAMA_HOST=0.0.0.0` before starting Ollama.
            4. Refresh this page.
        """)
        st.stop()
    
    with st.spinner("🚀 Initializing AI Engine..."):
        st.session_state.engine = CustomerSupportGraph(base_url=st.session_state.ollama_url)

if "ingestion" not in st.session_state:
    st.session_state.ingestion = IngestionPipeline()

# --- Main UI ---
st.title("🤖 iSupport assistant")
st.markdown("#### *Advanced RAG with Human-in-the-Loop Escalation*")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check for pending approvals (HITL)
config = {"configurable": {"thread_id": st.session_state.thread_id}}
try:
    state = st.session_state.engine.workflow.get_state(config)
except Exception:
    state = None

if state and state.next:
    # We are at a breakpoint (interrupt)
    st.warning("🚨 **Escalation Alert**: A human agent is required to review this response.")
    with st.expander("🛠️ Manager Review Panel", expanded=True):
        st.markdown('<div class="approval-box">', unsafe_allow_html=True)
        st.write(f"**Customer Query**: `{state.values['messages'][-1].content}`")
        st.write(f"**System Recommendation**: {state.values['intent'].upper()}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve Release", key="approve", use_container_width=True):
                with st.spinner("Finalizing response..."):
                    st.session_state.engine.workflow.invoke(None, config)
                st.rerun()
        with col2:
            if st.button("❌ Manual Override", key="deny", use_container_width=True):
                st.session_state.engine.workflow.update_state(config, {"approval_granted": False})
                st.session_state.engine.workflow.invoke(None, config)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Ask a support question..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Invoke Graph
    with st.chat_message("assistant"):
        with st.spinner("🧠 AI is processing your request..."):
            # Initial invocation
            inputs = {"messages": [HumanMessage(content=prompt)]}
            result = st.session_state.engine.workflow.invoke(inputs, config)
            
            # Check if we hit an interrupt
            new_state = st.session_state.engine.workflow.get_state(config)
            if not new_state.next:
                answer = result["messages"][-1].content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.info("🔄 Your request requires human review. Please see the **Manager Review Panel** above.")
                st.rerun()


# Footer
st.markdown("---")
st.caption("© 2026 Manas Dutta - Built with ❤️ and LangGraph")