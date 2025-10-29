-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create kb_docs table for document metadata
CREATE TABLE kb_docs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB
);

-- Create kb_chunks table for text chunks with embeddings
CREATE TABLE kb_chunks (
    id SERIAL PRIMARY KEY,
    doc_id INTEGER REFERENCES kb_docs(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_size INTEGER,
    embedding vector(768), -- OpenAI text-embedding-3-small dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create additional indexes for common queries
CREATE INDEX idx_kb_chunks_doc_id ON kb_chunks(doc_id);
CREATE INDEX idx_kb_chunks_chunk_index ON kb_chunks(doc_id, chunk_index);
CREATE INDEX idx_kb_docs_status ON kb_docs(status);
