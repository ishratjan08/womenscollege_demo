import logging
import os
import json
import csv
import uuid
from pathlib import Path
from typing import List, Optional, Dict,Callable, Any

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    UnstructuredFileLoader,
    PyPDFLoader,
    PDFPlumberLoader
)
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import pdfplumber
load_dotenv()

EMBEDDING_MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
folder_path = os.getenv("DATA_FOLDER_PATH", "./data")  # fallback to ./data if not set

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


SUPPORTED_EXTENSIONS = {
    ".pdf", ".txt", ".docx", ".doc", ".md", ".log",
    ".xlsx", ".csv", ".pptx", ".html", ".eml", ".json"
}


class UniversalFileLoader:
    """
    Loads and parses supported files from a directory.
    Handles .txt with JSON structure, .csv as row-wise documents,
    and other formats using UnstructuredFileLoader.
    """

    def __init__(self, folder_path: str, max_files: int = 70):
        self.folder_path = Path(folder_path)
        self.max_files = max_files

        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")
        logger.info(f"Initialized UniversalFileLoader with folder: {self.folder_path}")

    def _convert_json_to_text(self, json_obj: Any) -> str:
        if isinstance(json_obj, dict):
            return "\n".join(f"{k}: {v}" for k, v in json_obj.items())
        elif isinstance(json_obj, list):
            return "\n\n".join(self._convert_json_to_text(item) for item in json_obj)
        else:
            return str(json_obj)

    def _handle_txt_file(self, file_path: Path) -> List[Document]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                json_data = json.loads(content)
                readable_text = self._convert_json_to_text(json_data)

                temp_path = file_path.parent / f"__parsed__{file_path.name}"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(readable_text)

                loader = UnstructuredFileLoader(str(temp_path))
                docs = loader.load()
                temp_path.unlink()
                return docs

            except json.JSONDecodeError:
                logger.warning(f"{file_path.name} is plain text or invalid JSON. Loading normally.")
                loader = UnstructuredFileLoader(str(file_path))
                return loader.load()

        except Exception as e:
            logger.error(f"Error reading {file_path.name}: {e}")
            return []

    def _handle_csv_file(self, file_path: Path) -> List[Document]:
        documents = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    content = "\n".join(f"{k}: {v}" for k, v in row.items()).strip()
                    if not content:
                        logger.warning(f"Skipping empty row {idx} in {file_path.name}")
                        continue
                    documents.append(Document(page_content=content, metadata={"source": file_path.name, "row": idx}))
            logger.info(f"Loaded {len(documents)} rows from CSV: {file_path.name}")
        except Exception as e:
            logger.error(f"Error loading CSV {file_path.name}: {e}")
        return documents

    def _handle_pdf_file(self, file_path: Path) -> List[Document]:
        """
        Load a PDF file and return a list of Documents.
        Tries PyPDFLoader first; if no text is extracted, falls back to pdfplumber.
        """
        try:
            # --- Try PyPDFLoader ---
            loader = PyPDFLoader(str(file_path))

            docs = loader.load()
            # Filter out empty page_content
            docs = [doc for doc in docs if doc.page_content.strip()]
            
            if docs:
                return docs
            
            # --- Fallback: pdfplumber ---
            full_text = ""
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        full_text += page_text + "\n\n"

            full_text = full_text.strip()
            if not full_text:
                logger.warning(f"No text extracted from PDF: {file_path.name}")
                return []

            # Save to temp file and load via UnstructuredFileLoader for consistency
            temp_path = file_path.parent / f"__parsed__{file_path.name}.txt"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            loader = UnstructuredFileLoader(str(temp_path))
            docs = loader.load()
            temp_path.unlink()
            return docs

        except Exception as e:
            logger.error(f"Error reading PDF {file_path.name}: {e}")
            return []
    def load_documents(self, count: int = None) -> List[Document]:
        documents = []
        file_count = 0
        max_files = count if count is not None else self.max_files

        for file in sorted(self.folder_path.glob("*")):
            if file_count >= max_files:
                break

            ext = file.suffix.lower()
            if ext in SUPPORTED_EXTENSIONS:
                try:
                    if ext == ".txt":
                        docs = self._handle_txt_file(file)
                    elif ext == ".csv":
                        docs = self._handle_csv_file(file)
                    elif ext == ".pdf":
                        docs = self._handle_pdf_file(file)
                        logger.info(f'{len(docs)} documents loaded from PDF file: {file.name}')
                    elif ext == ".json":
                        # Support standalone .json files
                        with open(file, "r", encoding="utf-8") as f:
                            json_data = json.load(f)
                        readable_text = self._convert_json_to_text(json_data)
                        docs = [Document(page_content=readable_text, metadata={"source": file.name})]
                    else:
                        loader = UnstructuredFileLoader(str(file))
                        docs = loader.load()

                    if docs:
                        documents.extend(docs)
                        file_count += 1
                        logger.info(f"Loaded file: {file.name} ({len(docs)} documents)")
                    else:
                        logger.warning(f"No content extracted from: {file.name}")

                except Exception as e:
                    logger.warning(f"Failed to load {file.name}: {e}")
            else:
                logger.warning(f"Skipped unsupported file: {file.name}")

        logger.info(f"Total files loaded: {file_count}")
        return documents

class Chunker:
    """
    Splits documents into overlapping chunks.
    - CSV rows (with 'row' in metadata) are treated as individual chunks.
    - Other documents are split using recursive character splitter.
    - Filters out empty chunks to ensure embedding success.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("Invalid chunk size or overlap.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False
        )
        logger.info(f"Chunker initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def split_text_with_metadata(self, text: str, metadata: Optional[Dict] = None) -> List[Document]:
        if not text.strip():
            return []
        try:
            chunks = self.text_splitter.create_documents([text], metadatas=[metadata or {}])
            return [chunk for chunk in chunks if chunk.page_content.strip()]
        except Exception as e:
            logger.error(f"Failed to split text: {e}", exc_info=True)
            return []

    def split_documents(self, documents: List[Document]) -> List[Document]:
        all_chunks = []
        for doc in documents:
            if doc.metadata.get("row") is not None:
                # Already chunked row from CSV
                if doc.page_content.strip():
                    all_chunks.append(doc)
            else:
                chunks = self.split_text_with_metadata(doc.page_content, doc.metadata)
                all_chunks.extend(chunks)
        logger.info(f"Split {len(documents)} docs into {len(all_chunks)} chunks.")
        return all_chunks

    def prepare_for_embedding(self, documents: List[Document]) -> List[Document]:
        """
        Splits and filters documents before embedding.
        Ensures only non-empty documents are returned.
        """
        split_docs = self.split_documents(documents)
        clean_docs = [doc for doc in split_docs if doc.page_content.strip()]
        logger.info(f"Prepared {len(clean_docs)} cleaned documents for embedding.")
        return clean_docs

class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        try:
            self.model = HuggingFaceEmbeddings(model_name=model_name)
            logger.info(f"Embedding model initialized: {model_name}")
        except Exception as e:
            logger.critical(f"Embedding model initialization failed: {e}", exc_info=True)
            raise

    def embed_documents(self, docs: List[Document]) -> List[Dict[str, Any]]:
        for i, doc in enumerate(docs):
            logger.info(f"Document {i} metadata:", doc.metadata)                                                                                      
        texts = [doc.page_content for doc in docs]
        embeddings = self.model.embed_documents(texts)
        ids = [str(uuid.uuid4()) for _ in docs]

        results = [
            {"id": doc_id, "document": doc, "embedding": emb}
            for doc_id, doc, emb in zip(ids, docs, embeddings)
        ]
        logger.info(f"Embedded {len(results)} documents.")
        return results

    def embed_query(self, query: str) -> List[float]:
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")
        return self.model.embed_query(query)


class VectorStoreManager:
    def __init__(self, embedding_function: Embeddings, collection_name: str = "rag_collection"):
        self.persist_directory = os.getenv("CHROMA_DB_PATH", "vectorstore/chroma_db")
        self.collection_name = collection_name
        self.embedding_function = embedding_function
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory
        )

    def add_embedding_record(self, embed_records: List[Dict]):
        docs = [record["document"] for record in embed_records]
        ids = [record["id"] for record in embed_records]
        self.vectorstore.add_documents(documents=docs, ids=ids)

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vectorstore:
            raise RuntimeError("Vectorstore not initialized.")
        return self.vectorstore.similarity_search(query, k=k)


# Instantiate objects
document_loader_object = UniversalFileLoader(folder_path)
chunker_object = Chunker()
embedder_object = Embedder()
vectorstore_object = VectorStoreManager(embedding_function=embedder_object.model)


def ingest_html():
    documents = document_loader_object.load_documents()
    logger.info("Loaded %d raw documents.", len(documents))

    final_chunks_with_metadata = chunker_object.split_documents(documents)
    logger.info("Split into %d chunks with metadata.", len(final_chunks_with_metadata))

    embedder_value = embedder_object.embed_documents(final_chunks_with_metadata)
    logger.info("Generated %d embeddings.", len(embedder_value))

    vectorstore_object.add_embedding_record(embedder_value)
    logger.info("Successfully embedded and added %d chunks to the vector store.", len(final_chunks_with_metadata))
