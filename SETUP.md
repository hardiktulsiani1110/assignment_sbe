
## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd atlys
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

4. Configure environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/atlys
   SECRET_KEY=your-secret-key
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=your-admin-password
   ```

5. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

6. Start the server:
   ```bash
   uv run python server.py
   ```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
