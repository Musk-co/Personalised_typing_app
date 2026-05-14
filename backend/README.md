# Backend Directory

FastAPI backend for the Personalized Adaptive Typing Trainer.

## Structure

- `app/` - Main application code
  - `api/` - REST API routes and schemas
  - `core/` - Business logic (adapters, evaluator)
  - `db/` - Database models and initialization
  - `utils/` - Utility functions

- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   ```

3. Run development server:
   ```bash
   python -m app.main
   # Or using uvicorn directly:
   uvicorn app.main:app --reload
   ```

4. Visit API docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Architecture

### Adapter System
The core of the application is the **adapter system** which handles typing difficulty recommendations:

- **Rule-Based Adapter** (`core/adapters/rule_based.py`): Uses configurable thresholds
- **ML Adapter** (`core/adapters/ml_ready.py`): Stub for future ML implementation

Swap adapters via the `ADAPTER_TYPE` environment variable.

### Database Schema
See [docs/DATABASE_SCHEMA.md](../docs/DATABASE_SCHEMA.md) for detailed schema documentation.

## API Endpoints

All endpoints are prefixed with `/api/v1`:

- **Auth**: `/auth/*` - Registration, login, token refresh
- **Sessions**: `/sessions/*` - Create, read, update typing sessions
- **Users**: `/users/*` - User profiles and preferences
- **Analytics**: `/analytics/*` - Statistics and progress tracking
- **Adapter**: `/adapter/*` - Adapter configuration and recommendations

See [docs/API_SPEC.md](../docs/API_SPEC.md) for detailed API specifications.
