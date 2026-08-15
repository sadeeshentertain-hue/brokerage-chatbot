from logging import log
import os
import tempfile
from urllib.parse import urlparse

import requests
from langchain_community.document_loaders import PyPDFLoader
from logging import log
from typing import Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config.settings import settings


def validate_and_load_pdf(url: str):
    """
    Validates a URL, verifies the file exists, downloads it to a temp file,
    and loads it using PyPDFLoader.
    """
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL format: {url}")
    except Exception:
        raise ValueError(f"Could not parse URL: {url}")

    log.info(f"Verifying access to: {url}...")
    try:
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code != 200:
            raise ConnectionError(f"URL not accessible. Status Code: {response.status_code}")
            
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            raise ValueError(f"Target is not a PDF. Content-Type: {content_type}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error while connecting to URL: {e}")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_pdf.write(chunk)
            temp_file_path = temp_pdf.name

        log.info(f"Downloading successful. Loading from temp source: {temp_file_path}")
        
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        log.info(f"Successfully loaded {len(documents)} pages.")

        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            log.info("Temporary file cleaned up.")

        return documents

    except Exception as e:
        raise RuntimeError(f"Failed to load PDF content: {e}")

def create_policy_store(documents: Any):
    """Create vector store with underwriting policies (loaded from PDF).

    Returns:
        ChromaDB vector store for policy retrieval
    """
    try:
        # Split policies into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        policy_chunks = text_splitter.split_documents(documents)
        
        embeddings = OpenAIEmbeddings(
            base_url=settings.OPENAI_API_BASE,
            model=settings.OPENAI_LLM_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        vectorstore = Chroma.from_documents(
            policy_chunks, embedding=embeddings, persist_directory="./chroma_db" 
        )
    except Exception as e:
        log.error(f"Error creating policy store: {e}")
        raise ValueError(f"Failed to create policy store: {e}") from e
    return vectorstore

def load_policy_store(url: str):
    """Load existing vector store with underwriting policies (from PDF).

    Returns:
        ChromaDB vector store for policy retrieval
    """
    try:
        documents = validate_and_load_pdf(url)
        vectorstore = create_policy_store(documents)
        log.info(f"Vector store created with {len(vectorstore)} policy chunks.")
    except Exception as e:
        log.error(f"Error loading policy store: {e}")
        raise ValueError(f"Failed to load policy store: {e}") from e
    return len(vectorstore)