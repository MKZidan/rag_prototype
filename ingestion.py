
import argparse
import subprocess
import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DB_CONFIG, TEXT_CONFIG
# from database import IngestionDB
from database import IngestionDB
from logger import get_logger

def create_database_and_tables():
    """Create database and required tables if they do not exist."""
    logger = get_logger()
    try:
        # ensure psql exists
        if not shutil.which("psql"):
            raise RuntimeError("psql not found on PATH")
        cmd = [
            "psql",
            "-h", DB_CONFIG['host'],
            "-U", DB_CONFIG['user'],
            "-d", DB_CONFIG['database'],
            "-f", "schema.sql",
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = DB_CONFIG['password']
        subprocess.run(cmd, check=True, env=env) 

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise

def load_documents_from_directory(directory_path):
    print("==== Loading documents from directory ====")
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                documents.append({"id": filename, "text": file.read(), "path": directory_path + '/' + filename})
    return documents

# Function to split text into chunks
def split_text(text, chunk_size=TEXT_CONFIG['chunk_size'], chunk_overlap=TEXT_CONFIG['chunk_overlap']):
    chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_text(text)
    return chunks

def ingest_data():
    parser = argparse.ArgumentParser(description="Ingest text files into pgvector knowledge base")
    parser.add_argument("path", help="Path to text file or directory containing text files")
    args = parser.parse_args()

    documents = load_documents_from_directory(args.path)
    db = IngestionDB()
    total_chunks = 0
    for doc in documents:
        doc_id = db.insert_document(doc['id'], doc['path'], len(doc['text']))
            
        # Chunk the document text
        chunks = split_text(doc['text'])
        total_chunks += len(chunks)
        db.insert_chunks(doc_id, chunks)
        print(f"Inserted document {doc['id']} with {len(chunks)} chunks.")

    print(f"Total chunks inserted: {total_chunks}")

if __name__ == "__main__":
    ingest_data()
    # create_database_and_tables()
