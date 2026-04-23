import os
from typing import TypedDict, Annotated, Sequence, Literal
import operator

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.ingestion import IngestionPipeline

# Define the state object
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    intent: Literal["support", "escalate"]
    approval_granted: bool

class CustomerSupportGraph:
    def __init__(self, model_name: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, temperature=0, base_url=base_url)
        self.retriever = IngestionPipeline(base_url=base_url).get_retriever()
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        graph = StateGraph(AgentState)

        # Define Nodes
        graph.add_node("classifier", self.classify_intent)
        graph.add_node("retriever", self.retrieve_context)
        graph.add_node("generator", self.generate_answer)
        graph.add_node("human_review", self.human_review_node)

        # Define Edges
        graph.set_entry_point("classifier")
        
        graph.add_conditional_edges(
            "classifier",
            self.route_after_classification,
            {
                "support": "retriever",
                "escalate": "human_review"
            }
        )

        graph.add_edge("retriever", "generator")
        graph.add_edge("human_review", "generator")
        graph.add_edge("generator", END)

        # Compile with checkpointing and interrupt
        return graph.compile(
            checkpointer=self.memory,
            interrupt_before=["human_review"]
        )

    # --- Node Implementations ---

    def classify_intent(self, state: AgentState):
        """Classifies the query as routine support or escalation required."""
        last_message = state["messages"][-1].content
        
        prompt = ChatPromptTemplate.from_template(
            "You are an intent classifier for a customer support system.\n"
            "Analyze the following user query and classify it as 'support' or 'escalate'.\n\n"
            "ESCALATE if:\n"
            "- The user mentions 'refund', 'money back', or 'billing'.\n"
            "- The user is angry, using caps, or seems very frustrated.\n"
            "- The user asks for a 'human', 'manager', or 'supervisor'.\n"
            "- The query is complex and involves legal or safety issues.\n\n"
            "SUPPORT if:\n"
            "- The query is a general question about product features, technical help, or company info.\n\n"
            "User Query: {query}\n\n"
            "Intent (ONLY return 'support' or 'escalate'):"
        )
        
        chain = prompt | self.llm
        response = chain.invoke({"query": last_message})
        intent = response.content.strip().lower()
        
        print(f"DEBUG: Detected intent -> {intent}")
        
        if "escalate" in intent:
            return {"intent": "escalate"}
        return {"intent": "support"}

    def retrieve_context(self, state: AgentState):
        """Retrieves documents from ChromaDB."""
        query = state["messages"][-1].content
        try:
            docs = self.retriever.invoke(query)
            context = "\n".join([d.page_content for d in docs])
            
            # If no context found or retriever fails, force escalation
            if not context.strip():
                return {"context": "No relevant documentation found in the knowledge base.", "intent": "escalate"}
                
            return {"context": context}
        except Exception as e:
            print(f"ERROR: Retrieval failed -> {e}")
            return {"context": "Error accessing knowledge base.", "intent": "escalate"}

    def human_review_node(self, state: AgentState):
        """Logic for human intervention. The graph will interrupt BEFORE this node."""
        # This node is reached after the interrupt is resumed.
        # We assume approval is granted if we reached here.
        return {"approval_granted": True}

    def generate_answer(self, state: AgentState):
        """Generates the final response."""
        context = state.get("context", "No context provided.")
        intent = state.get("intent", "support")
        messages = state["messages"]
        
        if intent == "escalate" and not state.get("approval_granted", False):
            return {"messages": [AIMessage(content="I am escalating your request to a human agent for further assistance. Please wait.") ]}

        prompt = ChatPromptTemplate.from_template(
            "You are a professional customer support assistant.\n"
            "Use the provided context to answer the user's question.\n"
            "If you don't know the answer, say you don't know.\n"
            "Context: {context}\n"
            "History: {history}\n"
            "User: {query}\n"
            "Assistant:"
        )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "context": context,
            "history": messages[:-1],
            "query": messages[-1].content
        })
        
        return {"messages": [AIMessage(content=response.content)]}

    # --- Routing ---

    def route_after_classification(self, state: AgentState):
        return state["intent"]

if __name__ == "__main__":
    # Test initialization
    engine = CustomerSupportGraph()
    print("Graph Engine Initialized.")
