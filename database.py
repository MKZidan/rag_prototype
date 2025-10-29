import psycopg2
from config import DB_CONFIG
import subprocess
import shutil
import os
from typing import List, Tuple, Optional
from embedding_generator import generate_embedding
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
    
class DataBaseConnection:
    def __init__(self):
        self.connection = None
        self.logger = get_logger()
           
        # Establish connection
        self.connect()
    
    def __del__(self):
        self.close()

    def connect(self):
        """Establish database connection."""
        try:
            print(DB_CONFIG)
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.connection.autocommit = False
            self.logger.info("Connected to database")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Disconnected from database")
            
class IngestionDB(DataBaseConnection):
    def __init__(self):
        super().__init__()

    def insert_document(self, filename: str, file_path: str, file_size: int) -> int:
        """Insert document record and return document ID."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return -1
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO kb_docs (filename, file_path, file_size, status)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """, (filename, file_path, file_size, 'processing'))
            doc_id = cursor.fetchone()[0]
            self.connection.commit()
            return doc_id

    def insert_chunks(self, doc_id: int, chunks: List[str]):
        """Insert chunks with embeddings."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return
        with self.connection.cursor() as cursor:
            chunk_index = 0
            for chunk_text in chunks:
                self.insert_chunk(doc_id, chunk_text, chunk_index)
                chunk_index += 1
            self.connection.commit()
            self.update_ivfflat_index()

    def insert_chunk(self, doc_id: int, chunk_text: str, chunk_index: int):
        """Insert a single chunk with embedding."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return

        with self.connection.cursor() as cursor:
            # Convert embedding list to string format for PostgreSQL vector type
            embedding_str = generate_embedding(chunk_text)

            cursor.execute("""
                INSERT INTO kb_chunks (doc_id, chunk_text, chunk_index, chunk_size, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (doc_id, chunk_text, chunk_index, len(chunk_text), embedding_str))

    def update_document_status(self, doc_id: int, status: str):
        """Update document status, for example completed or failed."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE kb_docs 
                SET status = %s, processed_date = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, doc_id))
            self.connection.commit()

    def update_ivfflat_index(self):
        """Rebuild the IVFFLAT index for embeddings."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return
        with self.connection.cursor() as cursor:
            cursor.execute("DROP INDEX IF EXISTS kb_chunks_embedding_idx;")
            cursor.execute("CREATE INDEX kb_chunks_embedding_idx ON kb_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);")
            self.connection.commit()
    
class SearchDB(DataBaseConnection):
    def __init__(self):
        super().__init__()

    def search_similar_chunks(self, embedding_str: str, threshold: float, limit: int) -> List[Tuple[int, str, float]]:
        """Search for similar chunks based on embedding."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return []
                
        with self.connection.cursor() as cursor:
            cursor.execute("SET ivfflat.probes = 3;")

            cursor.execute("""
                    SELECT 
                        1 - (c.embedding <=> %s) as similarity,
                        c.chunk_text,
                        d.filename,
                        c.chunk_index,
                        c.doc_id,
                        c.chunk_size,
                        c.metadata as chunk_metadata,
                        d.filename,
                        d.metadata as doc_metadata
                    FROM kb_chunks c
                    JOIN kb_docs d ON c.doc_id = d.id
                    WHERE 1 - (c.embedding <=> %s) > %s
                    ORDER BY c.embedding <=> %s
                    LIMIT %s
                """, (embedding_str, embedding_str, threshold, embedding_str, limit))
            
            results = cursor.fetchall()
            return results

    def search_similar_chunks_no_index(self, embedding_str: str, threshold: float, limit: int) -> List[Tuple[int, str, float]]:
        """Search for similar chunks based on embedding without using index."""
        if self.connection == None:
            self.logger.error('No Data Basew Connection')
            return []
                
        with self.connection.cursor() as cursor:
            cursor.execute("""
                    SELECT 
                        c.id,
                        c.doc_id,
                        c.chunk_text,
                        c.chunk_index,
                        c.chunk_size,
                        c.metadata as chunk_metadata,
                        1 - (c.embedding <=> %s) as similarity,
                        d.filename,
                        d.metadata as doc_metadata
                    FROM kb_chunks c
                    JOIN kb_docs d ON c.doc_id = d.id
                    WHERE 1 - (c.embedding <=> %s) > %s
                    ORDER BY (1 - (c.embedding <=> %s)) DESC
                    LIMIT %s
                """, (embedding_str, embedding_str, threshold, embedding_str, limit))
            
            results = cursor.fetchall()
            return results
