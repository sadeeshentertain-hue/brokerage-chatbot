import os

from src.config.settings import settings
try:
    from langchain_chroma import Chroma
except ModuleNotFoundError:  # pragma: no cover
    from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_chroma_db():
    """Initialize and return a Chroma vector store instance."""
    embeddings = OpenAIEmbeddings(
        base_url=settings.OPENAI_API_BASE,
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        )

    db = Chroma(
        persist_directory=settings.CHROMA_DB_PATH,
        embedding_function=embeddings
    )
    return db

def get_relevant_schemas(user_query: str, num_tables: int = 4) -> str:
    """Searches Chroma DB and formats retrieved table schemas into a single string."""
    db = get_chroma_db()
    print(f"Searching for relevant schemas for query: '{user_query}' with num_tables={num_tables}")

    collection = getattr(db, "_collection", None) or getattr(db, "_chroma_collection", None)
    total_docs = collection.count() if collection is not None else 0
    print(f"Total documents available in DB: {total_docs}")

    if collection is not None:
        results = collection.get(include=["documents", "metadatas"])
        for i in range(len(results.get("ids", []))):
            doc_id = results["ids"][i]
            doc_text = results["documents"][i] if results.get("documents") else "None"
            doc_meta = results["metadatas"][i] if results.get("metadatas") else {}
            print(f"Document ID: {doc_id}, Text: {doc_text}, Metadata: {doc_meta}")

    retrieved_docs = db.similarity_search(user_query, k=num_tables)
    print(f"Retrieved {len(retrieved_docs)} relevant schemas for query '{user_query}'.")
    schema_context = ""
    print(f"retrieved_docs: {retrieved_docs}")
    for doc in retrieved_docs:
        schema_context += f"\n--- TABLE SCHEMA ---\n{doc.page_content}\n"
    return schema_context