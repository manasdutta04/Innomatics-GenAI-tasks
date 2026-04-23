import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

class IngestionPipeline:
    def __init__(self, db_path: str = "data/chroma_db"):
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_pdf(self, file_path: str) -> bool:
        """Loads a PDF, chunks it, and adds to ChromaDB."""
        try:
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found.")
                return False

            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            chunks = self.text_splitter.split_documents(documents)
            
            # Persist to Chroma
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.db_path
            )
            print(f"Successfully processed {len(chunks)} chunks from {file_path}.")
            return True
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return False

    def get_retriever(self):
        """Returns a retriever object from the persisted store."""
        vectorstore = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    # Test ingestion if sample exists
    pipeline = IngestionPipeline()
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    # You can manually drop a PDF in data/ and call process_pdf here
