# Technical Documentation: iSupport assistant

## 1. Introduction
This system is an advanced AI-driven customer support assistant (iSupport assistant) that utilizes **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers from a specific knowledge base (PDF). It integrates **LangGraph** for sophisticated workflow management, enabling **Human-in-the-Loop (HITL)** escalation for sensitive queries.

## 2. Design Decisions

### Chunking Strategy
We chose **RecursiveCharacterTextSplitter** with a chunk size of 1000 and overlap of 100. This ensures that semantic context isn't lost at boundaries while keeping chunks small enough for efficient LLM processing.

### Embedding & Vector Store
*   **all-MiniLM-L6-v2**: Selected for its balance between performance and local resource usage. It produces 384-dimensional vectors.
*   **ChromaDB**: Chosen for its native integration with LangChain and robust local persistence.

### Workflow Orchestration
**LangGraph** was chosen over traditional linear chains because it allows for stateful, multi-step cycles and native "interrupt" capabilities, which are essential for true HITL implementation.

## 3. Workflow Explanation

### Node Responsibilities
*   **Classifier**: Acts as the "Brain," determining the path based on user intent.
*   **Retriever**: Interacts with ChromaDB to fetch grounding data.
*   **Generator**: Uses the `qwen2.5` model to synthesize the final answer.
*   **HITL Node**: Serves as a logical checkpoint for human verification.

### State Transitions
The graph manages a `TypedDict` state. Every node returns updates to this state. The `interrupt` mechanism allows the graph to be "frozen" and "thawed" by external UI actions.

## 4. HITL Implementation
Human intervention is triggered when the `Classifier` detects a sensitive intent or when retrieval fails to find relevant information.
*   **Mechanism**: `interrupt_before=["human_review"]`.
*   **Benefit**: Increases system reliability and safety by preventing the LLM from hallucinating on sensitive topics (e.g., pricing, legal issues).

## 5. Challenges & Trade-offs
*   **Accuracy vs. Speed**: Larger chunks provide more context but slow down retrieval and generation. 1000 chars is our "sweet spot."
*   **Cost vs. Performance**: Using local models (Qwen) eliminates API costs but requires local GPU/RAM resources.

## 6. Testing Strategy
*   **Sample Queries**: 
    *   "What is the return policy?" (Expected: Routine RAG response)
    *   "I want a refund immediately!" (Expected: HITL Escalation)
    *   "How do I install the app?" (Expected: Routine RAG response)
*   **Validation**: Checked against the "faq.pdf" content to ensure no hallucinations.

## 7. Future Enhancements
*   **Multi-document Support**: Allowing multiple PDFs to be uploaded.
*   **Memory Integration**: Persistent chat history across sessions.
*   **Feedback Loop**: User "thumbs up/down" to refine embeddings.
