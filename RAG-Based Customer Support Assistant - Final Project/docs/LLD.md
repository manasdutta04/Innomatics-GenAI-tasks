# Low-Level Design (LLD): RAG-Based Customer Support Assistant

## 1. Module-Level Design

### Document Processing & Embedding
*   **Class**: `DocumentManager`
*   **Functions**:
    *   `ingest_pdf(file_path)`: Loads PDF, splits text, and adds to ChromaDB.
    *   `clear_database()`: Resets the vector store.

### Graph Execution Module
*   **State Class**: `AgentState(TypedDict)`
    *   `messages`: List of BaseMessage (history).
    *   `context`: List of Documents retrieved.
    *   `intent`: Literal["support", "escalate"].
    *   `next_step`: The next node to execute.

### HITL Module
*   **Breakpoint Logic**: Uses `graph.compile(checkpointer=memory, interrupt_before=["human_review"])`.
*   **State Persistence**: `MemorySaver` preserves the thread state across Streamlit reruns.

## 2. Data Structures

### State Object
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    intent: str
    approved: bool
```

### Query-Response Schema
*   **Input**: JSON `{ "query": string, "thread_id": string }`
*   **Output**: JSON `{ "answer": string, "sources": list, "status": "completed" | "pending_approval" }`

## 3. Workflow Design (LangGraph)

### Nodes
1.  `classifier`: Uses LLM to determine if the query is "Standard" or "Sensitive".
2.  `retriever`: Performs similarity search against ChromaDB.
3.  `responder`: Prompts LLM with context + query to generate response.
4.  `human_review`: A dummy node where the graph pauses.

### Edges
*   `START` -> `classifier`
*   `classifier` -> `retriever` (if standard)
*   `classifier` -> `human_review` (if sensitive)
*   `retriever` -> `responder`
*   `human_review` -> `responder` (after approval)

## 4. Conditional Routing Logic

### Intent Detection Prompt
> "Classify the user query into: 'SUPPORT' (routine help) or 'ESCALATE' (refunds, complaints, sensitive data). Return only the word."

### Escalation Criteria
*   Keywords: "refund", "manager", "legal", "complain", "fail".
*   Sentiment: High frustration or anger.
*   Missing Context: When the retriever returns zero relevant chunks.

## 5. API / Interface Design

### Streamlit Interaction Flow
1.  User enters message.
2.  Graph starts executing.
3.  If it hits `human_review`, UI displays "Review Required" status.
4.  Human agent clicks "Approve" -> UI updates state and resumes graph.
5.  Answer is displayed to user.

## 6. Error Handling

*   **No Chunks Found**: The `retriever` node detects empty results and sets intent to `ESCALATE`.
*   **LLM Timeout**: Implemented with retry logic in LangChain.
*   **Corrupt PDF**: Validated during ingestion with `try-except` blocks.
