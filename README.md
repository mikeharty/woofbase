# WoofBase 🐕 wow

such fullstack application for browsing and discovering dog breeds. very built with FastAPI backend and React frontend. amaze

## Features such

-   Auto-sync with upstream dog breed API much
-   Paginated breed listing wow
-   Breed images (when available) very

## Getting Started wow

### Prerequisites such

-   Docker and Docker Compose very
-   Node.js (for local frontend development much)
-   Python 3.13 wow

### Running with Docker Compose amaze

1. Clone the repository such
2. Run the entire stack wow:

    ```bash
    docker-compose up --build
    ```

3. Open your browser very:
    - Frontend: http://localhost:5173 much
    - Backend API: http://localhost:8000 wow
    - API Docs: http://localhost:8000/docs such

### Local Development amaze

#### Backend wow

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

#### Frontend such

```bash
cd frontend
npm install
npm run dev
```

## Architecture very

-   Backend: FastAPI with SQLAlchemy, Local In-Memory Cache, PostgreSQL database wow
-   Frontend: React + TypeScript + Vite much
-   Robustness: Local caching, asynchronous data synchronization, retries with exponential backoff + random jitter amaze

## API Endpoints such

-   `GET /dogs?page=<int>` - Get paginated dog breeds wow

## Serious tho

I inspected the provided API and saw the following characteristics:

-   Intermittent long response times (could just be cold starts)
-   Inconsistent responses for the same pages, but consistent results when status code is 200

You can see the tests I ran to investigate these issues in `backend/clients/olive-tests.py`.

The design I implemented aims to mitigate these issues by:

-   Caching responses locally using both an in-memory cache (would be redis in prod) and a persistent database
-   Asynchronous background synchronization to avoid blocking user requests
-   Retries with exponential backoff and random jitter to handle transient API failures
-   Logging to monitor sync status and issues
-   Graceful degradation to serve cached data when the upstream API is unavailable
-   Facade API to abstract away upstream API issues from frontend
