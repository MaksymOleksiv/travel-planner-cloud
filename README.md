# Travel Planner - Backend API

A RESTful API for managing travel projects and places to visit. Built with FastAPI, SQLAlchemy, and integrated with the Art Institute of Chicago API.

## Features

- CRUD operations for travel projects
- Integration with Art Institute of Chicago API for artwork/place data
- Automatic project status management (active/completed)
- Validation and business logic enforcement
- Docker support for easy deployment
- Interactive API documentation (Swagger UI)

## Tech Stack

- **Framework**: FastAPI 0.129.0
- **Database**: SQLite with SQLAlchemy 2.0.46 (async)
- **Migrations**: Alembic 1.18.4
- **HTTP Client**: httpx 0.28.1
- **Python**: 3.12+

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OR Python 3.12+ (for local development)

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd Test-Assessment-Travel-Planner-Backend
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start the application:
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
APP_ENV=development
DATABASE_URL=sqlite+aiosqlite:///./travel_planner.db
ARTIC_API_BASE_URL=https://api.artic.edu/api/v1
ARTIC_API_TIMEOUT=10
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For frontend developers: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed endpoint specifications, request/response examples, and integration tips.

## API Endpoints

### Travel Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/` | List all projects (with pagination) |
| GET | `/api/v1/projects/{id}` | Get a single project with all places |
| POST | `/api/v1/projects/` | Create a new project (optionally with places) |
| PATCH | `/api/v1/projects/{id}` | Update project information |
| DELETE | `/api/v1/projects/{id}` | Delete project (if no places are visited) |

### Project Places

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{project_id}/places/` | List all places in a project |
| GET | `/api/v1/projects/{project_id}/places/{place_id}` | Get a single place |
| POST | `/api/v1/projects/{project_id}/places/` | Add a place to a project |
| PATCH | `/api/v1/projects/{project_id}/places/{place_id}` | Update place notes/visited status |

## Usage Examples

### Create a Project with Places

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Art Tour",
    "description": "Visit famous artworks",
    "start_date": "2026-03-01",
    "place_external_ids": [4, 20684, 27992]
  }'
```

### List Projects

```bash
curl http://localhost:8000/api/v1/projects/?limit=10&offset=0
```

### Get Project Details

```bash
curl http://localhost:8000/api/v1/projects/1
```

### Update Project

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "description": "New description"
  }'
```

### Add a Place to Existing Project

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/places/ \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": 27992
  }'
```

### Update Place (Mark as Visited)

```bash
curl -X PATCH http://localhost:8000/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Beautiful artwork!",
    "is_visited": true
  }'
```

### Delete Project

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1
```

## Business Logic

### Project Status

- **Active**: Default status when project is created
- **Completed**: Automatically set when all places in the project are marked as visited

### Validation Rules

1. **Maximum 10 places per project**: Cannot add more than 10 places
2. **Minimum 1 place**: Project should have at least one place (can be added after creation)
3. **Unique places**: Cannot add the same external_id to a project twice
4. **API validation**: Each place must exist in the Art Institute API
5. **Delete protection**: Cannot delete a project if any place is marked as visited

## Project Structure

```
app/
├── api/
│   ├── dependencies.py          # Dependency injection
│   └── v1/
│       ├── router.py            # Main API router
│       └── routes/
│           ├── projects.py      # Project endpoints
│           └── project_places.py # Place endpoints
├── core/
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database setup
│   └── exceptions.py            # Custom exceptions
├── models/
│   ├── project.py               # Project ORM model
│   └── project_place.py         # ProjectPlace ORM model
├── repositories/
│   ├── project_repository.py    # Project data access
│   └── project_place_repository.py # Place data access
├── schemas/
│   ├── project.py               # Project Pydantic schemas
│   └── project_place.py         # Place Pydantic schemas
├── services/
│   └── artic_service.py         # Art Institute API client
└── main.py                      # Application entry point
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment | `development` |
| `DATABASE_URL` | SQLite database connection string | `sqlite+aiosqlite:///./travel_planner.db` |
| `ARTIC_API_BASE_URL` | Art Institute API base URL | `https://api.artic.edu/api/v1` |
| `ARTIC_API_TIMEOUT` | API request timeout in seconds | `10` |
