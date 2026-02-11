# Neighborhood Library Management System

A full-stack web application for managing a neighborhood library's books, members, and borrowing operations.

## Technology Stack

### Backend
- Python 3.11+
- FastAPI (REST API framework)
- SQLAlchemy 2.0 (ORM with async support)
- PostgreSQL 15
- Alembic (database migrations)
- Pydantic v2 (data validation)

### Frontend
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Axios (HTTP client)

### Infrastructure
- Docker & Docker Compose
- PostgreSQL (containerized)

## Features

### Core Functionality
- Create, read, update, and delete books
- Create, read, update, and delete members
- Borrow books (with due date tracking)
- Return books
- View borrowing history
- Query books borrowed by specific members

### Additional Features
- Staff authentication and authorization
- Automatic due date calculation (14 days from borrow date)
- Validation to prevent deleting books that are borrowed or have borrowing history
- Validation to prevent deleting members with borrowing history
- Comprehensive error handling

## Prerequisites

- Docker and Docker Compose
- Git

For local development without Docker:
- Python 3.11+
- **uv** (recommended) or **Miniconda** for Python dependency management
- Node.js 20+
- PostgreSQL 15+

## Quick Start with Docker Compose

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LibraryApp
```

### 2. Set Up Environment Variables

Backend environment file already exists at `backend/.env.docker`. Update if needed:

```bash
# backend/.env.docker
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/library
```

Frontend environment file already exists at `frontend/.env.docker`. Update if needed:

```bash
# frontend/.env.docker
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start All Services

```bash
docker-compose up -d --build
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend application on port 3000

### 4. Run Database Migrations

```bash
docker-compose exec backend uv run alembic upgrade head
```

### 5. (Optional) Seed Sample Data

To populate the database with sample data for testing:

```bash
docker-compose exec backend uv run python seed_data.py
```

This will create:
- 2 staff users (admin/admin123, staff1/staff123)
- 10 books (8 available, 2 currently borrowed)
- 5 members
- 5 borrowing records (2 active, 3 returned)

### 6. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation (Swagger): http://localhost:8000/docs
- API Documentation (ReDoc): http://localhost:8000/redoc

Login credentials (if you ran seed script):
- Username: `admin`
- Password: `admin123`

You can use the Swagger UI at http://localhost:8000/docs to test all API endpoints interactively.

### 7. Stop All Services

```bash
docker-compose down
```

To remove all data including the database volume:

```bash
docker-compose down -v
```

## Local Development Setup

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Install dependencies using one of the following methods:

**Option A: Using uv (Recommended)**

```bash
uv sync
```

**Option B: Using Conda**

```bash
conda create -n library_env python=3.11 -y
conda activate library_env
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your local database URL and secret key
```

4. Start PostgreSQL (if not using Docker):

```bash
# Using Docker for PostgreSQL only
docker run -d \
  --name library-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=library \
  -p 5432:5432 \
  postgres:15
```

5. Run migrations:

```bash
# If using uv:
uv run alembic upgrade head

# If using conda:
alembic upgrade head
```

6. Start the backend server:

```bash
# If using uv:
uv run fastapi dev app/main.py

# If using conda:
fastapi dev app/main.py
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Set up environment variables:

```bash
cp .env.example .env.local
# Edit .env.local if needed
```

4. Start the development server:

```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## API Documentation

### Authentication

All endpoints except /api/auth/login and /api/books require authentication. Use the `/api/auth/login` endpoint to obtain a JWT token.

**Login:**
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```bash
Authorization: Bearer <access_token>
```

### Books Endpoints

- `GET /api/books` - List all books (supports filtering by title and author)
- `GET /api/books/{id}` - Get book by ID
- `POST /api/books` - Create new book
- `PUT /api/books/{id}` - Update book
- `DELETE /api/books/{id}` - Delete book (if not borrowed or has no borrowing history)

### Members Endpoints

- `GET /api/members` - List all members
- `GET /api/members/{id}` - Get member by ID
- `POST /api/members` - Create new member
- `PUT /api/members/{id}` - Update member
- `DELETE /api/members/{id}` - Delete member (only if no borrowing history)

### Borrowing Endpoints

- `POST /api/borrowings/borrow` - Borrow a book
- `PUT /api/borrowings/{id}/return` - Return a borrowed book
- `GET /api/borrowings` - List all active borrowings
- `GET /api/borrowings/history` - Get complete borrowing history
- `GET /api/borrowings/members/{member_id}` - Get borrowings for a specific member

For detailed API documentation with request/response schemas, visit http://localhost:8000/docs after starting the backend.

## Database Schema

### Tables

**books**
- id (Primary Key)
- title
- author
- isbn (Unique)
- description
- is_available (Boolean)
- created_at
- updated_at

**members**
- id (Primary Key)
- name
- email (Unique)
- phone (Unique)
- created_at
- updated_at

**borrowing_records**
- id (Primary Key)
- book_id (Foreign Key to books)
- member_id (Foreign Key to members)
- borrowed_date
- returned_date (NULL if not returned)
- created_at
- updated_at

**staffs**
- id (Primary Key)
- username (Unique)
- email (Unique)
- hashed_password
- full_name
- created_at

## Running Tests

### Backend Tests

```bash
cd backend
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Project Structure

```
LibraryApp/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # Database connection
│   │   ├── config.py         # Configuration
│   │   ├── utils.py          # Utility functions
│   │   └── main.py           # FastAPI application
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test files
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities and API client
│   │   └── types/            # TypeScript types
│   ├── public/               # Static assets
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Troubleshooting

### Database Connection Issues

If the backend cannot connect to PostgreSQL:

1. Ensure PostgreSQL is running:
```bash
docker-compose ps
```

2. Check PostgreSQL logs:
```bash
docker-compose logs postgres
```

3. Verify DATABASE_URL in backend/.env.docker matches the PostgreSQL service configuration

### Port Conflicts

If ports 3000, 5432, or 8000 are already in use:

1. Stop the conflicting service, or
2. Modify the port mappings in docker-compose.yml

### Frontend Cannot Connect to Backend

1. Verify backend is running on port 8000
2. Check NEXT_PUBLIC_API_URL in frontend/.env.docker
3. Ensure CORS is properly configured in backend/app/main.py

## Environment Variables Reference

### Backend (.env.docker)

- `SECRET_KEY` - Secret key for JWT token signing (required)
- `DATABASE_URL` - PostgreSQL connection string (required)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 30)

### Frontend (.env.docker)

- `NEXT_PUBLIC_API_URL` - Backend API base URL (required)

## Docker Commands Reference

### Rebuild and restart a single service:
```bash
docker-compose up -d --build <service-name>
```

### View logs for a service:
```bash
docker-compose logs -f <service-name>
```

### Execute command in a running container:
```bash
docker-compose exec <service-name> <command>
```

### Stop all services:
```bash
docker-compose down
```

### Remove all data including volumes:
```bash
docker-compose down -v
```

## License

This project is created as a take-home assessment for a Neighborhood Library Management System.

