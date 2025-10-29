# pgvector Knowledge Base (text_embedding)

This project uses PostgreSQL with the pgvector extension for storing embeddings and document chunks. The database runs in Docker (so it doesn't require a local Postgres install).

## Quick overview
- Docker Compose runs Postgres with the `pgvector/pgvector` image.
- The project expects the DB to be reachable on the host at `localhost` and a host port mapped to the container's `5432` (this repo uses `5435` by default).
- The SQL schema enabling the `vector` extension is in `schema.sql` and is loaded on container init.

## Prerequisites
- Docker Desktop installed and running
- (Optional) `psql` client on host for troubleshooting
- Python 3.10+ and a virtual environment if you want to run the Python scripts locally

## Files of interest
- `docker-compose.yml` - Docker config for Postgres + pgvector
- `schema.sql` - Database schema (creates `vector` extension and tables)
- `config.py` - App configuration and DB connection string (reads from environment variables)
- `ingestion.py`, `embedding_generator.py`, `advancedSearch.py` - example scripts to load and query the knowledge base

## Start the services (Docker)
Open a PowerShell terminal in the repository root and run:

```powershell
# Start Postgres with pgvector in detached mode
docker compose up -d

# Show running containers and port mapping
docker ps
```

By default the Postgres service in `docker-compose.yml` maps port `5435` on your host to `5432` inside the container (host:container -> `5435:5432`). If you changed the mapping, update `DB_PORT` accordingly (see below).

## Environment configuration
The project uses environment variables. You can create a `.env` file in the repo root to override defaults used in `config.py`.

Example `.env` (create this file in the project root):

```env
DB_HOST=localhost
DB_PORT=5435
DB_NAME=knowledge_base
DB_USER=postgres
DB_PASSWORD=000000

# Optional: override embedding settings
EMBEDDING_DIMENSION=768
```

Alternatively, set these env vars in your shell before running the scripts.

## Environment files: `.env` vs `.env.example`

- Keep real secret values (passwords, API keys) in a local `.env` file. Do not commit `.env` to version control.
- Keep a `.env.example` file in the repository as a template that documents which environment variables are required and shows example/default values.
- To create a local `.env` from the template, run (PowerShell):

```powershell
copy .env.example .env
```

- Fill in the real values in `.env`. This repo already includes a `.gitignore` entry for `.env` so your secrets won't be committed.

## Connect to the database from host (psql)
To test from the host machine (PowerShell) using `psql`:

```powershell
psql "postgresql://postgres:000000@localhost:5435/knowledge_base" -c "\conninfo"
```

If you get `password authentication failed`, see the Troubleshooting section below.

## Script Usage

### Data Ingestion (`ingestion.py`)
This script processes text files and stores them in the vector database with their embeddings.

```powershell
python ingestion.py <path_to_directory>
```

Parameters:
- `path`: (Required) Path to a directory containing text files to process. For example: `./news_articles`

The script will:
1. Load all `.txt` files from the specified directory
2. Split each document into chunks (configurable via `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`)
3. Store document metadata and text chunks in the database
4. Display progress information including number of chunks processed

Example:
```powershell
python ingestion.py ./news_articles
```

### Semantic Search (`advancedSearch.py`)
This script performs semantic search over the ingested documents using AI-powered query understanding.

```powershell
python advancedSearch.py "<query>" [--limit N] [--threshold X.X]
```

Parameters:
- `query`: (Required) The search query text in natural language
- `--limit`: (Optional) Number of results to return (default: 3)
- `--threshold`: (Optional) Similarity threshold from 0.0 to 1.0 (default: 0.5)

The script will:
1. Generate an example answer to guide the search
2. Convert the query to embeddings
3. Find similar text chunks in the database
4. Provide a final answer based on the retrieved context

Example:
```powershell
# Basic search
python advancedSearch.py "What are the latest developments in AI?"

# Search with custom parameters
python advancedSearch.py "Explain recent AI developments" --limit 5 --threshold 0.3
```

## Running Python scripts
1. Create and activate a virtual environment:

```powershell
python -m venv my_env
my_env\Scripts\Activate.ps1
```

2. Install dependencies using the provided `requirements.txt`:

```powershell
pip install -r requirements.txt
```

If you prefer a minimal install or want to add packages manually, you can still install individual packages such as `python-dotenv` or `psycopg2-binary`.

3. Make sure your `.env` (or environment) has the DB connection values matching `docker-compose.yml`, then run the scripts as described in the Script Usage section above.

## Troubleshooting: "password authentication failed"
If you see errors like `FATAL:  password authentication failed for user "postgres"` when connecting from the host:

1. Confirm the host port used by Docker (`docker ps`) and ensure `DB_PORT` matches it (e.g., 5435).
2. Check for a `.env` file overriding the password. `config.py` loads env vars and defaults to `000000` if not set.
3. Restart the container to ensure environment variables from `docker-compose.yml` are applied:

```powershell
docker compose down
docker compose up -d
```

4. If the host still can't authenticate, set/reset the postgres user's password inside the container:

```powershell
# Run this from host PowerShell
docker exec -it pgvector-test-db psql -U postgres -c "ALTER USER postgres WITH PASSWORD '000000';"
```

5. Try connecting again from the host with `psql`.

6. If you still fail, check `pg_hba.conf` or logs inside the container for additional hints:

```powershell
# Show recent logs
docker logs pgvector-test-db --tail 100
```

## Notes
- This README documents the current default port mapping `5435:5432`. If you prefer `5433` or another port, pick one and make sure both `docker-compose.yml` and `config.py` (or your `.env`) use the same host port.
- Consider adding a `requirements.txt` if you want reproducible Python installs.

## Next steps (suggested)
- Add `.env.example` to the repo with the sample variables above.
- Add a `requirements.txt` listing the Python dependencies.
- Add a short script or Makefile to automate starting services and running tests.

---

If you want, I can also create the `.env.example` and a `requirements.txt` with the likely packages used by this project. Let me know which you'd like next.