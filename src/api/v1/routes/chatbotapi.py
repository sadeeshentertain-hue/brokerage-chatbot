import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException, status
from langchain_core.messages import HumanMessage
from src.graph.chatbot_graph import create_and_compile_workflow
from src.graph.state.agentstate import AgentState
from src.utils.sanitize_data import sanitize_all_input

from mockup_sql_ragsetup.ragsetup.dataingestionandload import convertschemattodocument, load_table_schema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brokeragent", tags=["Chat & Agents"])

def normalize_json_url(file_url: str) -> str:
    """Convert GitHub browser URLs to raw JSON URLs so they return file content."""
    parsed = urlparse(file_url)
    if parsed.netloc.lower() == "github.com" and "/blob/" in parsed.path:
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 4:
            owner, repo, _, branch, *rest = path_parts
            if branch and rest:
                raw_path = "/".join([owner, repo, branch, *rest])
                return f"https://raw.githubusercontent.com/{raw_path}"
    return file_url


@router.post("/ragload", summary="Load table schema documents for RAG processing")
async def stream_chat_response(url: str):
    """Validate the JSON file URL and return a success or error message."""
    try:
        if not url or not str(url).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": ["URL is required."]},
            )

        file_url = normalize_json_url(str(url).strip())
        parsed = urlparse(file_url)

        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": [f"Invalid URL: {file_url}"]},
            )

        try:
            with urlopen(file_url, timeout=10) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"errors": [f"JSON file not found: {file_url}"]},
                    )

                content = response.read()
                if not content:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"errors": [f"JSON file is empty: {file_url}"]},
                    )

                data = json.loads(content.decode("utf-8"))
        except (HTTPError, URLError, ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errors": [f"JSON file not found or invalid: {file_url}"]},
            ) from exc
        print(f"Loaded JSON data from {file_url}: {data}")
        table_documents = convertschemattodocument(data)
        len_doc = load_table_schema(table_documents)

        return {"message": "Table schema documents loaded successfully.", "loaded_documents": len_doc}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("RAG document loading failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"errors": [f"Document loading failed: {str(exc)}"]},
        ) from exc

@router.post("/broker-chat", summary="Chat with the broker agent")
async def broker_chat_response(query: str):
    """broker agent chat endpoint."""
    sanitize_data = sanitize_all_input(query)
    sql_query = ""
    app = create_and_compile_workflow()

    config = {"configurable": {"thread_id": "session_unique_id_123"}}

    # 2. Structure your incoming state data
    # Match the key name to your State definition (usually "messages")
    graph_input = {
        "messages": [
            HumanMessage(content="Hello! Can you share the list of vendors and their agreements?"),
       ]
    }

    state:AgentState = AgentState(
        user_query=sanitize_data,
    )


    # 3. Invoke the graph synchronously
    output_state = app.invoke(state)

    return f"graph created: {output_state}"

    # sql_query = generate_sql_from_question(sanitize_data)  # Call the RAG SQL generation function
    # results = run_sqlite_query(sql_query)  # Execute the generated SQL query against the SQLite database
    # formatted_response = generate_llm_response(sanitize_data, results)  # Format the LLM response
    # return {"response": formatted_response, "sql_query": sql_query,"DB_results": results,
    #         "formatted_response": formatted_response}