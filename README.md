#  A Trained-data RAG Chatbot

"" is an intelligent AI assistant designed to provide accurate, user-friendly, and easy-to-understand information about hospitals, doctors, treatments, and specialties. This project leverages Retrieval Augmented Generation (RAG) to deliver relevant Trained-data information based on a pre-ingested knowledge base.

## Features

*   **Interactive Chatbot:** A web-based interface for users to ask Trained-data-related questions.
*   **Contextual Conversations:** The AI remembers previous interactions to provide coherent and relevant responses.
*   **Data Ingestion:** Supports ingesting various document types (PDF, TXT, DOCX, HTML, etc.) into a vector store for retrieval.
*   **Trained-data-Specific Knowledge:** Trained with verified Trained-data information to answer queries about hospitals, doctors, treatments, and services.
*   **User and Session Management:** Manages user and session IDs to maintain chat history.
*   **API Endpoints:** Provides RESTful APIs for chat interaction and data ingestion.

## Technologies Used

*   **Backend:**
    *   **FastAPI:** For building the web API.
    *   **LangChain:** For orchestrating the RAG pipeline (document loading, chunking, embedding, retrieval, and LLM interaction).
    *   **Google Gemini API:** As the Large Language Model (LLM) for generating responses.
    *   **HuggingFace Embeddings:** For creating vector embeddings of documents.
    *   **ChromaDB:** As the vector store for efficient similarity search.
    *   **Peewee:** A lightweight ORM for SQLite database (`chat.db`) to store chat history.
    *   **python-dotenv:** For managing environment variables.
*   **Frontend:**
    *   **HTML, CSS, JavaScript:** Standard web technologies for the user interface.
    *   **Jinja2Templates:** For rendering HTML templates in FastAPI.
    *   **Marked.js:** For rendering Markdown content in chat messages.
*   **Database:**
    *   **SQLite:** For storing chat messages (`chat.db`).
    *   **ChromaDB:** For storing vector embeddings (`embedded_vec_db`).

## Project Structure

```
.
├── .env                          # Environment variables (API keys, paths, model names)
├── chat.db                       # SQLite database for chat history
├── main.py                       # Main FastAPI application entry point
├── controllers/                  # API route definitions
│   ├── __init__.py
│   ├── import_controller.py      # Endpoint for data ingestion
│   └── query_controller.py       # Endpoint for chat queries
├── data/                         # Directory for raw Trained-data data files
│   ├── get_all_treatmenthospitals.txt
│   ├── get-all-doctors.txt
│   ├── get-all-hospitals.txt
│   └── get-all-treatments.txt
├── db/                           # Database connection and setup
│   ├── __init__.py
│   └── db.py                     # Peewee SQLite database connection
├── embedded_vec_db/              # ChromaDB persistent directory for vector embeddings
│   └── chroma.sqlite3
│   └── ... (other ChromaDB files)
├── front_end/                    # Frontend static files and templates
│   ├── static/
│   │   ├── script.js             # Frontend JavaScript logic
│   │   └── style.css             # Frontend CSS styling
│   └── templates/
│       └── index.html            # Main HTML template for the chatbot UI
├── models/                       # Database models
│   ├── __init__.py
│   └── messages.py               # Peewee model for chat messages
├── services/                     # Core business logic and RAG components
│   ├── __init__.py
│   ├── import_service.py         # Handles document loading, chunking, embedding, and vector store population
│   └── query_service.py          # Manages chat engine, LLM interaction, and context retrieval
└── utilities/                    # Utility functions
    ├── __init__.py
    └── utills.py                 # API key verification utility
```

## Setup and Installation

### Prerequisites

*   Python 3.11+
*   `pip` (Python package installer)

### 1. Clone the Repository

```bash
git clone https://github.com/DanishRather/shared-rag.git
cd shared-rag
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```
*(Note: A `requirements.txt` file is assumed. If not present, you'll need to manually install `fastapi`, `uvicorn`, `langchain`, `langchain-google-genai`, `langchain-huggingface`, `langchain-community`, `langchain-core`, `langchain-text-splitters`, `python-dotenv`, `peewee`, `unstructured`, `chromadb`, `tiktoken`)*

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```dotenv
DATA_FOLDER_PATH = "./data"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
GEMINI_MODEL="gemini-2.5-flash"
CHROMA_DB_PATH = "./embedded_vec_db"
GOOGLE_API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY" # Replace with your actual Google Gemini API Key
API_KEY = "YOUR_API_KEY" # Replace with a strong API key for ingestion endpoint
```

*   **`GOOGLE_API_KEY`**: Obtain this from the Google AI Studio or Google Cloud Console.
*   **`API_KEY`**: This is a custom API key used to secure the `/api/import` endpoint. Choose a strong, unique key.

### 5. Prepare Data (Optional, but recommended for full functionality)

Place your Trained-data-related documents (e.g., `.txt`, `.pdf`, `.docx`, `.html`) into the `data/` directory. The project comes with some sample `.txt` files.

### 6. Ingest Data into Vector Store

Before you can chat with the RAG system, you need to ingest the data. This will process your documents, create embeddings, and store them in ChromaDB.

First, ensure your FastAPI application is running (see "Running the Application" below).
Then, open your browser or use a tool like `curl` or Postman to hit the import endpoint:

```bash
curl -X GET "http://localhost:8000/api/import" -H "x_api_key: YOUR_API_KEY"
```
Replace `YOUR_API_KEY` with the `API_KEY` you set in your `.env` file.

You should see a response like: `{"Message":"You are ready to interact with chat"}`

## Running the Application

To start the FastAPI application, navigate to the root directory of the project and run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

*   `main:app`: Refers to the `app` object within `main.py`.
*   `--reload`: Enables auto-reloading on code changes (useful for development).
*   `--host 0.0.0.0`: Makes the server accessible from other devices on your network.
*   `--port 8000`: Runs the server on port 8000.

Once the server is running, open your web browser and go to:

```
http://localhost:8000
```

You will see the chatbot interface.

## Usage

1.  **Open the Chatbot:** Click the "💬" button at the bottom right of the screen to open the chatbot widget.
2.  **Ask Questions:** Type your Trained-data-related queries into the input field and press Enter or click "Send".
3.  **Session Management:**
    *   **Session ID / User ID:** These are displayed in the dropdown menu (three dots icon) and are automatically generated and stored in your browser's local storage.
    *   **Reset Session:** Clears the current chat history for the active session.
    *   **Reset User:** Generates a new user ID and session ID, effectively starting fresh.
4.  **Maximize/Minimize:** Use the maximize icon (&#x26F6;) to expand the chatbot to full screen and the close icon (&#x2715;) to close it.

## Extending the Knowledge Base

To add more data to the RAG system:

1.  Place new documents (supported formats: `.pdf`, `.txt`, `.docx`, `.doc`, `.md`, `.log`, `.xlsx`, `.csv`, `.pptx`, `.html`, `.eml`) into the `data/` directory.
2.  Re-run the ingestion process by hitting the `/api/import` endpoint (as described in "Ingest Data into Vector Store"). This will add the new documents to your existing vector store.

## Contributing

(Add guidelines for contributing if this were an open-source project)

## To Run this RAG update the data folder by pasting your pdf data or excel... 
## make shure to update the env file with your credential:
## To run the this RAG update Create Virtual environement and run the fallowing command: uvicorn main:app --reload