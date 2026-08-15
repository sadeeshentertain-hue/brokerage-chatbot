import logging
from typing import Any

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from src.config.settings import settings

logger = logging.getLogger(__name__)


def create_schema_store(documents: Any):
    """Create vector store with database schema information.

    Returns:
        ChromaDB vector store for schema retrieval
    """
    try:
        embeddings = OpenAIEmbeddings(
            base_url=settings.OPENAI_API_BASE,
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        persist_directory = settings.CHROMA_DB_PATH or "./chroma_db"
        vectorstore = Chroma.from_documents(
            documents,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
    except Exception as e:
        logger.error("Error creating schema store: %s", e)
        raise ValueError(f"Failed to create schema store: {e}") from e
    return vectorstore

def load_table_schema(documents: Any):
    """Load table schema into a vector store.

    Returns:
        ChromaDB vector store for schema retrieval
    """
    try:
        vectorstore = create_schema_store(documents)
        logger.info("Vector store created with %s schema chunks.", len(vectorstore))
    except Exception as e:
        logger.exception("Error loading table schema: %s", e)
        raise ValueError(f"Failed to load table schema: {e}") from e
    return len(vectorstore)

def convertschemattodocument(schema_data: Any):
    # Ensure the root element is iterable as a list of tables
    if isinstance(schema_data, dict):
        # If the JSON wraps tables in a key like "tables": [...]
        if "tables" in schema_data:
            schema_data = schema_data["tables"]
        else:
            schema_data = [schema_data]
    table_documents = []
    # 2. Map exactly 1 table to 1 Document object
    for table in schema_data:
        table_name = table.get("name") or table.get("table_name", "unknown_table")
        description = table.get("description", "No description provided.")
        # Generate a clean, descriptive text block for the entire table
        text_representation = f"Table Name: {table_name}\nDescription: {description}\nColumns:\n"
    
        for col in table.get("columns", []):
            col_name = col.get("name")
            col_type = col.get("type", "UNKNOWN")
            col_desc = col.get("description", "")
        
            line = f"  - {col_name} ({col_type})"
            if col.get("primary_key") or col.get("is_primary"):
                line += " [PRIMARY KEY]"
            if col.get("foreign_key") or col.get("is_foreign"):
                line += f" [FOREIGN KEY references {col.get('references', 'other_table')}]"
            if col_desc:
                line += f" : {col_desc}"
            
            text_representation += line + "\n"
    
        # Store critical tracking attributes in flat metadata
        metadata = {
            "table_name": table_name,
            "type": "database_schema"
        }
    
        # Create the single Document container for this specific table
        doc = Document(page_content=text_representation, metadata=metadata)
        table_documents.append(doc)

    print(f"Generated {len(table_documents)} complete table documents (Zero Chunking Applied).")
    return table_documents