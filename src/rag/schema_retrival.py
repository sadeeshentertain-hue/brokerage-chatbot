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

    retrieved_docs = db.similarity_search(user_query, k=num_tables)
    print(f"Retrieved {len(retrieved_docs)} relevant schemas for query '{user_query}'.")
    schema_context = ""
    for doc in retrieved_docs:
        schema_context += f"\n--- TABLE SCHEMA ---\n{doc.page_content}\n"
    return schema_context