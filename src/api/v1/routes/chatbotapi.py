import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/brokeragent", tags=["Chat & Agents"])


@router.post("/ragload", summary="Load table schema documents for RAG processing")
async def stream_chat_response(url: str):
    """Validate the JSON file URL and return a success or error message."""
    try:
        if not url or not str(url).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": ["URL is required."]},
            )

        file_url = str(url).strip()
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

                json.loads(content.decode("utf-8"))
        except (HTTPError, URLError, ValueError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"errors": [f"JSON file not found or invalid: {file_url}"]},
            ) from exc

        return {"message": "Table schema documents loaded successfully."}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("RAG document loading failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"errors": [f"Document loading failed: {str(exc)}"]},
        ) from exc