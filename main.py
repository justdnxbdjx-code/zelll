from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import pyodbc
import openai
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector
from azure.identity import DefaultAzureCredential

app = FastAPI(title="Zelvio Backend API")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load env from Azure Key Vault via App Settings
SQL_CONNECTION_STRING = os.getenv("SQL_CONNECTION_STRING")
BLOB_CONN_STRING = os.getenv("BLOB_CONN_STRING")
AISEARCH_ENDPOINT = os.getenv("AISEARCH_ENDPOINT")
AISEARCH_ADMIN_KEY = os.getenv("AISEARCH_ADMIN_KEY")
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_API_KEY = os.getenv("AOAI_API_KEY")

# Initialize clients
blob_client = BlobServiceClient.from_connection_string(BLOB_CONN_STRING)
search_client = SearchClient(AISEARCH_ENDPOINT, "docs-index", AISEARCH_ADMIN_KEY)
openai.api_base = AOAI_ENDPOINT
openai.api_key = AOAI_API_KEY

@app.get("/")
def home():
    return {"message": "Zelvio API is running ✅"}

@app.post("/upload")
async def upload_file(file: UploadFile):
    container = blob_client.get_container_client("uploads")
    container.upload_blob(name=file.filename, data=file.file)
    return {"filename": file.filename, "status": "uploaded"}

@app.get("/query")
def query_docs(q: str):
    results = search_client.search(search_text=q)
    return [doc for doc in results]
