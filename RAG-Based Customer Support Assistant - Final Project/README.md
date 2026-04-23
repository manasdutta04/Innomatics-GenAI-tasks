# 🤖 iSupport assistant

A state-of-the-art **Retrieval-Augmented Generation (RAG)** customer support system built with **LangGraph**, **ChromaDB**, and **Ollama**.

## 🌟 Key Features
- **Intelligent RAG**: Seamlessly ingest PDF documentation and retrieve grounded answers using local embeddings.
- **Workflow Orchestration**: Powered by **LangGraph**, enabling cyclical logic and state management.
- **Human-in-the-Loop (HITL)**: Automated escalation of sensitive or complex queries for human agent approval.
- **Privacy First**: Runs entirely locally using **Qwen 2.5 (7B)** via Ollama.
- **Premium UI**: A sleek, dark-themed Streamlit interface with real-time status updates and operator dashboards.

## 🛠️ Architecture
The system follows a graph-based decision tree:
1. **Classifier**: Detects user intent (Routine vs. Sensitive).
2. **Retriever**: Fetches relevant context from the vector store if routine.
3. **HITL Node**: Triggers a breakpoint if escalation is required.
4. **Generator**: Synthesizes the final response using the LLM.

## 🚀 Getting Started

### 1. Prerequisites
- [Ollama](https://ollama.com/) installed and running.
- Pull the model: `ollama pull qwen2.5:7b`

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run src/app.py
```

## 📂 Project Structure
- `src/`: Core logic (Ingestion, Graph Engine, Streamlit UI).
- `docs/`: HLD, LLD, and Technical Documentation.
- `data/`: Vector database and uploaded documents.
- `scripts/`: Utility scripts (e.g., demo PDF generation).

## 📄 Demo Knowledge Base
We have provided a demo PDF at `data/iSupport_Guide.pdf`. You can upload this in the sidebar to test the RAG capabilities immediately.

---
Built for the Innomatics GenAI Internship Final Project.

- **Data Layer**: Knowledge base documents in `data/`
- **Vector Store**: ChromaDB for storing document embeddings
- **Embeddings**: HuggingFace sentence-transformers for creating embeddings
- **Interface**: Streamlit for user interaction

## Workflow

1. Documents are loaded and split into chunks.
2. Embeddings are created using HuggingFace sentence-transformers.
3. Chunks are stored in ChromaDB vector store.
4. User query is embedded and similar documents are retrieved.
5. Retrieved documents are passed to GPT-2 LLM with the query to generate an answer.