import os
import io
from pypdf import PdfReader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

PERSIST_DIRECTORY = "./chroma_db"
vector_store = Chroma(
    collection_name="chatbot_knowledge",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIRECTORY,
)


def extract_and_store_pdf(file_bytes: bytes, session_id: str):
    reader = PdfReader(io.BytesIO(file_bytes))
    raw_text = ""
    for page in reader.pages:
        raw_text += page.extract_text() or ""

    if not raw_text.strip():
        raise ValueError("Could not extract text from the PDF.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(raw_text)

    docs = [
        Document(page_content=chunk, metadata={"session_id": session_id})
        for chunk in chunks
    ]

    vector_store.add_documents(docs)


def retrieve_context_for_session(query: str, session_id: str, k: int = 3) -> str:
    try:
        # Use direct similarity search with metadata filter with fallback safety
        results = vector_store.similarity_search(
            query, k=k, filter={"session_id": session_id}
        )
        if not results:
            return ""
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        print(f"RAG retrieval warning (continuing without context): {e}")
        return ""


def delete_session_documents(session_id: str):
    try:
        vector_store.delete(where={"session_id": session_id})
    except Exception as e:
        print(f"Error deleting session documents: {e}")
