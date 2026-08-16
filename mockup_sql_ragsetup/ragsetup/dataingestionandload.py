import logging
from typing import Any

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from src.config.settings import settings

logger = logging.getLogger(__name__)


def _sanitize_chroma_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Chroma accepts only scalar metadata values; strip list/dict values to keep the schema documents valid."""
    safe_metadata: dict[str, Any] = {}
    for key, value in metadata.items():
        if key in {"columns", "primary_key", "foreign_keys", "metadata"}:
            continue
        if value is None or value == "":
            continue
        if isinstance(value, (list, tuple, set)):
            if not value:
                continue
            safe_metadata[key] = ", ".join(str(item) for item in value)
        elif isinstance(value, (str, int, float, bool)):
            safe_metadata[key] = value
        else:
            safe_metadata[key] = str(value)
    return safe_metadata


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

        persist_directory = settings.CHROMA_DB_PATH
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
    """Normalize schema JSON into LangChain Documents.

    The JSON can arrive in a few shapes:
    - a list of table objects
    - a dict with a "tables" key
    - a dict with a "data" key containing table objects
    - a single table object with nested "metadata" information
    """
    if isinstance(schema_data, dict):
        if "tables" in schema_data and isinstance(schema_data["tables"], list):
            schema_data = schema_data["tables"]
        elif "data" in schema_data and isinstance(schema_data["data"], list):
            schema_data = schema_data["data"]
        else:
            schema_data = [schema_data]

    table_documents = []
    for table in schema_data:
        if not isinstance(table, dict):
            continue

        metadata = table.get("metadata") if isinstance(table.get("metadata"), dict) else {}

        table_name = (
            metadata.get("table_name")
            or table.get("table_name")
            or table.get("name")
            or table.get("tableName")
            or table.get("id", "unknown_table")
        )
        description = (
            metadata.get("description")
            or table.get("description")
            or "No description provided."
        )
        columns = metadata.get("columns") if isinstance(metadata.get("columns"), list) else table.get("columns", [])

        text_representation = f"Table Name: {table_name}\nDescription: {description}\nColumns:\n"

        primary_keys = set(metadata.get("primary_key", []) or [])
        foreign_keys = metadata.get("foreign_keys", []) or []

        for col in columns:
            if not isinstance(col, dict):
                continue

            col_name = col.get("name") or col.get("column_name") or "unknown_column"
            col_type = col.get("type", "UNKNOWN")
            col_desc = col.get("description", "")

            line = f"  - {col_name} ({col_type})"
            if col.get("primary_key") or col.get("is_primary") or col_name in primary_keys:
                line += " [PRIMARY KEY]"

            if col.get("foreign_key") or col.get("is_foreign"):
                references = col.get("references") or col.get("references_table") or "other_table"
                line += f" [FOREIGN KEY references {references}]"
            elif any(
                isinstance(fk, dict)
                and (
                    (col_name in (fk.get("column") or []))
                    or (col_name in (fk.get("columns") or []))
                )
                for fk in foreign_keys
            ):
                fk_ref = next(
                    (
                        fk.get("references_table")
                        for fk in foreign_keys
                        if isinstance(fk, dict)
                        and (
                            (col_name in (fk.get("column") or []))
                            or (col_name in (fk.get("columns") or []))
                        )
                    ),
                    "other_table",
                )
                line += f" [FOREIGN KEY references {fk_ref}]"

            if col_desc:
                line += f" : {col_desc}"

            text_representation += line + "\n"

        metadata_doc = {
            "table_name": table_name,
            "type": "database_schema",
            "description": description,
        }
        if isinstance(metadata, dict):
            metadata_doc.update(_sanitize_chroma_metadata(metadata))

        doc = Document(page_content=text_representation, metadata=metadata_doc)
        table_documents.append(doc)

    print(f"Generated {len(table_documents)} complete table documents (Zero Chunking Applied).")
    print(table_documents)
    return table_documents