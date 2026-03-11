# Neighborhood Library Management System

A full-stack web application for managing a neighborhood library's books, members, and borrowing operations. Built to explore and benchmark different backend communication patterns (REST vs gRPC) and infrastructure layers (Redis caching, RabbitMQ messaging, Prometheus monitoring).

## Technology Stack

### Backend

- **Python 3.11+**
- **FastAPI** — REST API framework with async support
- **gRPC** — Alternative high-performance RPC server (parallel implementation)
- **SQLAlchemy 2.0** — Async ORM
- **PostgreSQL 15** — Primary database
- **Alembic** — Database migrations
- **Pydantic v2** — Data validation & settings
- **Redis 7** — Response caching (with automatic invalidation)
- **RabbitMQ** — Message broker for asynchronous event publishing
- **Prometheus** — Metrics collection (`prometheus-fastapi-instrumentator`)
- **pwdlib** — Password hashing
- **asyncpg** — Async PostgreSQL driver

### Frontend

#### Next.js (Primary)
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Axios** / React Context API

#### Vite (Alternative)
- **React + Vite**
- **Vanilla CSS**

### Notification Service

- **Go** — Standalone microservice
- **RabbitMQ** (amqp091-go) — Consumes borrow/return events
- Supports **email** and **SMS** notification stubs

### Infrastructure

- **Docker & Docker Compose** — Full containerized environment
- **Prometheus** — Metrics scraping (configurable)
- **RabbitMQ Management UI** — Available at port 15672

---

## Features

### Core Functionality

- Create, read, update, and delete **books**
- Create, read, update, and delete **members**
- **Borrow books** — with automatic due date (14 days) and availability tracking
- **Return books** — with timestamp and status update
- View **active borrowings** and complete **borrowing history**
- Query borrowings for a specific member

### Additional Features

- **Staff authentication** — JWT-based with OAuth2 password flow
- **Redis caching** — GET endpoints cached; cache invalidated on mutations
- **Event publishing** — Borrow/return actions publish events to RabbitMQ
- **Notification service** — Go microservice consumes events and dispatches notifications
- **Prometheus metrics** — REST API instrumented; gRPC server exposes metrics on port 9000
- **gRPC server** — Parallel implementation exposing the same domain via proto-defined services
- **Repository pattern** — Decoupled data access layer with protocol-defined interfaces
- **Service layer** — Business logic isolated from transport layer
- Validation: prevents deleting books that are borrowed or have borrowing history
- Validation: prevents deleting members with borrowing history

---

## Prerequisites

- **Docker** and **Docker Compose**
- **Git**

For local development without Docker:

- Python 3.11+ with **uv** (recommended) or **Conda**
- Node.js 20+
- Go 1.21+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+

---

## Quick Start with Docker Compose

### 1. Clone the Repository

```bash
git clone <repository-url>
cd LibraryApp
```

### 2. Create a Docker Network

The compose file uses an external network. Create it once:

```bash
docker network create library-network
```

### 3. Set Up Environment Variables

**`backend/.env.docker`**

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/library
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://guest:guest@rabbit:5672/
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**`frontend/.env.docker`**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**`notification-service/.env.docker`**

```bash
RABBITMQ_URL=amqp://guest:guest@rabbit:5672/
```

### 4. Start All Services

```bash
docker-compose up -d --build
```

This starts:

| Service               | Port(s)         | Description                          |
|-----------------------|-----------------|--------------------------------------|
| `postgres`            | 5433 (host)     | PostgreSQL database                  |
| `redis`               | 6379            | Redis cache                          |
| `rabbit`              | 5672, 15672     | RabbitMQ broker + management UI      |
| `backend`             | (internal only) | FastAPI REST + gRPC server           |
| `notification-service`| (internal only) | Go event consumer                    |
| `frontend`            | 3000            | Next.js frontend                     |

> **Note:** The backend port (8000) is intentionally not exposed to the host by default in `docker-compose.yml`. Uncomment the `ports` section under `backend` if you need direct access.

### 5. Run Database Migrations

```bash
docker-compose exec backend uv run alembic upgrade head
```

### 6. (Optional) Seed Sample Data

```bash
docker-compose exec backend uv run python seed_data.py
```

This creates:

- 2 staff users (admin@library.com / admin123, staff1@library.com / staff123)
- 10 books (8 available, 2 currently borrowed)
- 5 members
- 5 borrowing records (2 active, 3 returned)

### 7. Access the Application

| URL                          | Description                  |
|------------------------------|------------------------------|
| http://localhost:3000        | Frontend application         |
| http://localhost:8000        | Backend REST API             |
| http://localhost:8000/docs   | Swagger UI (interactive)     |
| http://localhost:8000/redoc  | ReDoc documentation          |
| http://localhost:8000/metrics| Prometheus metrics endpoint  |
| http://localhost:15672       | RabbitMQ management UI       |

**Default login credentials (after running seed script):**

- Username: `admin@library.com`
- Password: `admin123`

### 8. Stop All Services

```bash
docker-compose down
```

To remove all data including the database volume:

```bash
docker-compose down -v
```

---

## Local Development Setup

### Backend Setup

```bash
cd backend
```

**Install dependencies:**

```bash
# Using uv (recommended)
uv sync

# Using conda
conda create -n library_env python=3.11 -y
conda activate library_env
pip install -r requirements.txt
```

**Configure environment:**

```bash
cp .env.example .env
# Edit .env with your local DB URL, Redis URL, and RabbitMQ URL
```

**Start infrastructure (Docker only):**

```bash
docker run -d --name library-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=library -p 5432:5432 postgres:15
docker run -d --name library-redis -p 6379:6379 redis:7-alpine
docker run -d --name library-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

**Run migrations and start:**

```bash
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

**Start the gRPC server (separate terminal):**

```bash
uv run python -m app.grpc_server
# Listens on port 50052 | Prometheus metrics on port 9000
```

Backend REST API: http://localhost:8000
gRPC server: `localhost:50052`

### Frontend Setup (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend: http://localhost:3000

### Frontend Setup (Vite)

```bash
cd frontend-vite
npm install
npm run dev
```

### Notification Service Setup (Go)

```bash
cd notification-service
cp .env.example .env
go run ./cmd/...
```

---

## Project Structure

```
LibraryApp/
│
├── backend/
│   ├── app/
│   │   ├── grpc_handlers/        # gRPC service handlers (Books, Members, Borrowings, Auth)
│   │   ├── routers/              # REST API endpoints (auth, books, members, borrowings)
│   │   ├── repositories/         # Data access layer (protocol-defined interfaces + PG implementations)
│   │   ├── services/             # Business logic layer
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   ├── schemas.py            # Pydantic request/response schemas
│   │   ├── database.py           # Async DB engine and session management
│   │   ├── redis_client.py       # Redis cache helpers (get/set/delete/invalidate)
│   │   ├── grpc_server.py        # gRPC server entry point
│   │   ├── config.py             # Pydantic Settings configuration
│   │   ├── exceptions.py         # Custom domain exceptions
│   │   ├── dependencies.py       # FastAPI dependency injection
│   │   └── main.py               # FastAPI app entry point
│   ├── alembic/                  # Database migration scripts
│   ├── protos/                   # .proto files + generated Python stubs
│   ├── pubsub/                   # RabbitMQ connection and topology setup
│   ├── seed_data.py              # Database seeding script
│   ├── test_grpc_client.py       # gRPC integration test client
│   ├── pyproject.toml
│   └── Dockerfile
│
├── notification-service/         # Go microservice
│   ├── cmd/                      # Entry point
│   └── internal/
│       ├── config/               # Environment config
│       ├── handler/              # RabbitMQ message handler
│       ├── models/               # Event models
│       ├── notifier/             # Email + SMS notification stubs
│       └── rabbitmq/             # Consumer setup
│
├── frontend/                     # Next.js frontend
│   ├── src/
│   │   ├── app/                  # Next.js App Router pages (login, register, admin)
│   │   ├── components/           # Reusable React components
│   │   ├── context/              # AuthContext provider
│   │   └── lib/                  # API client (Axios) and TypeScript types
│   └── Dockerfile
│
├── frontend-vite/                # Vite + React alternative frontend
│   └── src/
│       ├── pages/                # Page components
│       ├── components/           # Shared UI components
│       ├── services/             # API service layer
│       └── context/              # Auth context
│
├── benchmarks/
│   ├── benchmark_rest.py         # REST API load test
│   ├── benchmark_grpc.py         # gRPC load test
│   └── benchmark_redis.py        # Redis cache latency test
│
├── monitoring/
│   └── prometheus.yml            # Prometheus scrape configuration
│
├── prometheus/                   # Prometheus data (volume mount)
├── definitions.json              # RabbitMQ topology definitions
├── rabbitmq.conf                 # RabbitMQ configuration
└── docker-compose.yml
```

---

## API Documentation

### Authentication

All endpoints except `GET /api/books` and `POST /api/auth/login` require a valid JWT Bearer token.

**Login:**

```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@library.com&password=admin123
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:

```
Authorization: Bearer <access_token>
```

### Endpoints Reference

#### Auth
| Method | Endpoint           | Auth | Description              |
|--------|--------------------|------|--------------------------|
| POST   | `/api/auth/register` | No  | Register a new staff user |
| POST   | `/api/auth/login`    | No  | Login (returns JWT)       |
| GET    | `/api/auth/me`       | Yes | Get current staff user    |

#### Books
| Method | Endpoint          | Auth | Description                         |
|--------|-------------------|------|-------------------------------------|
| GET    | `/api/books`      | No   | List all books (filter by title/author, Redis cached) |
| GET    | `/api/books/{id}` | Yes  | Get book by ID (Redis cached)       |
| POST   | `/api/books`      | Yes  | Create new book (invalidates cache) |
| PUT    | `/api/books/{id}` | Yes  | Update book (invalidates cache)     |
| DELETE | `/api/books/{id}` | Yes  | Delete book (if no borrow history)  |

#### Members
| Method | Endpoint            | Auth | Description                          |
|--------|---------------------|------|--------------------------------------|
| GET    | `/api/members`      | Yes  | List all members                     |
| GET    | `/api/members/{id}` | Yes  | Get member by ID                     |
| POST   | `/api/members`      | Yes  | Create new member                    |
| PUT    | `/api/members/{id}` | Yes  | Update member                        |
| DELETE | `/api/members/{id}` | Yes  | Delete member (if no borrow history) |

#### Borrowings
| Method | Endpoint                            | Auth | Description                      |
|--------|-------------------------------------|------|----------------------------------|
| GET    | `/api/borrowings`                   | Yes  | List active borrowings           |
| GET    | `/api/borrowings/history`           | Yes  | Full borrowing history           |
| GET    | `/api/borrowings/members/{id}`      | Yes  | Borrowings for a specific member |
| POST   | `/api/borrowings/borrow`            | Yes  | Borrow a book (publishes event)  |
| PUT    | `/api/borrowings/{id}/return`       | Yes  | Return a book (publishes event)  |

For full request/response schemas, visit http://localhost:8000/docs after starting the backend.

---

## gRPC Server

The project includes a parallel gRPC implementation exposing the same domain logic. It runs as a separate process on port **50052** and exposes Prometheus metrics on port **9000**.

**Proto services defined:**
- `AuthService` — Login + token generation
- `BookService` — Full CRUD
- `MemberService` — Full CRUD
- `BorrowingService` — Borrow, return, list, history

**Server reflection** is enabled — you can introspect services with `grpcurl` without needing the `.proto` files:

```bash
grpcurl -plaintext localhost:50052 list
```

**Run the gRPC client test:**

```bash
cd backend
uv run python test_grpc_client.py
```

---

## Redis Caching

Redis is used for response caching on book endpoints. Cached responses are automatically invalidated on any write operation (create/update/delete).

| Operation              | Cache Behavior              |
|------------------------|-----------------------------|
| `GET /api/books`       | Cache hit after first fetch |
| `GET /api/books/{id}`  | Cache hit after first fetch |
| `POST /api/books`      | Invalidates list cache      |
| `PUT /api/books/{id}`  | Invalidates item + list     |
| `DELETE /api/books/{id}` | Invalidates item + list   |

Run the Redis cache benchmark:

```bash
cd benchmarks
python benchmark_redis.py
```

---

## Database Schema

### Entity Relationship

```
BOOKS ────< BORROWING_RECORDS >──── MEMBERS
              (book_id FK)             
              (member_id FK)          STAFFS (independent)
```

### Tables

**`books`** — `id`, `title`, `author`, `isbn (UNIQUE)`, `description`, `is_available`, `created_at`, `updated_at`

**`members`** — `id`, `name`, `email (UNIQUE)`, `phone (UNIQUE)`, `created_at`, `updated_at`

**`borrowing_records`** — `id`, `book_id (FK)`, `member_id (FK)`, `borrowed_date`, `returned_date`, `created_at`, `updated_at`
- `due_date` — computed property: `borrowed_date + 14 days`
- `status` — computed property: `"BORROWED"` | `"RETURNED"`

**`staffs`** — `id`, `username (UNIQUE)`, `email (UNIQUE)`, `hashed_password`, `full_name`, `created_at`

---

## Testing

### Interactive API Testing (Swagger UI)

1. Start the backend
2. Open http://localhost:8000/docs
3. Run seed data: `docker-compose exec backend uv run python seed_data.py`
4. Click **Authorize** → login with `admin@library.com` / `admin123`
5. Test all endpoints interactively

### Alternative: Postman

Import the OpenAPI schema from http://localhost:8000/openapi.json into Postman.

### gRPC Testing

```bash
cd backend
uv run python test_grpc_client.py
```

### Redis Cache Benchmark

```bash
python benchmarks/benchmark_redis.py
```

---

## Performance Comparison

Benchmark setup: **50 concurrent users, 20 requests/user (1,100 total requests)**

| Metric              | FastAPI REST (async) | gRPC (100 workers) |
|---------------------|----------------------|--------------------|
| Total Requests      | 1,100                | 1,100              |
| Total Time (s)      | 12.27                | 50.99              |
| Throughput (req/s)  | 89.67                | 21.57              |
| Avg Latency (ms)    | 486.52               | 2,312.18           |
| P95 Latency (ms)    | 2,355.10             | 16,183.18          |

> For this simple CRUD workload, async FastAPI REST significantly outperforms the gRPC server, owing mostly to the overhead of thread-pool-based gRPC handling for I/O-bound operations at this scale.

---

## Environment Variables Reference

### Backend (`.env` / `.env.docker`)

| Variable                    | Description                                | Default  |
|-----------------------------|--------------------------------------------|----------|
| `SECRET_KEY`                | JWT signing secret (required)              | —        |
| `DATABASE_URL`              | PostgreSQL connection string (required)    | —        |
| `REDIS_URL`                 | Redis connection string                    | —        |
| `RABBITMQ_URL`              | RabbitMQ AMQP connection string            | —        |
| `ALGORITHM`                 | JWT algorithm                              | `HS256`  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL                               | `30`     |

### Frontend (`.env.docker`)

| Variable                | Description                      |
|-------------------------|----------------------------------|
| `NEXT_PUBLIC_API_URL`   | Backend REST API base URL        |

### Notification Service (`.env.docker`)

| Variable        | Description                   |
|-----------------|-------------------------------|
| `RABBITMQ_URL`  | RabbitMQ AMQP connection URL  |

---

## Docker Commands Reference

```bash
# Start all services
docker-compose up -d --build

# Rebuild and restart a single service
docker-compose up -d --build <service-name>

# View logs for a service
docker-compose logs -f <service-name>

# Execute a command in a running container
docker-compose exec <service-name> <command>

# Stop all services (preserve data)
docker-compose down

# Stop all services and remove volumes
docker-compose down -v
```

---

## Troubleshooting

### Database Connection Issues

```bash
docker-compose ps          # Check service status
docker-compose logs postgres   # View PostgreSQL logs
```

Verify `DATABASE_URL` in `backend/.env.docker` matches the PostgreSQL service config.

### Redis Not Caching

Ensure `REDIS_URL` is set and the `redis` service is healthy:

```bash
docker-compose logs redis
```

### RabbitMQ Events Not Consumed

Check that both `backend` and `notification-service` are connected to `library-network`:

```bash
docker-compose logs rabbit
docker-compose logs notification-service
```

Access the RabbitMQ management UI at http://localhost:15672 (user: `guest`, password: `guest`) to inspect queues and message flow.

### Port Conflicts

If ports 3000, 5432/5433, 6379, 5672, or 15672 are in use, modify the port mappings in `docker-compose.yml`.

### Frontend Cannot Connect to Backend

- Ensure backend port 8000 is exposed (uncomment in `docker-compose.yml`)
- Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.docker`

---

## License

Simple Neighborhood Library App built to compare REST and gRPC performance, and to explore infrastructure layers including Redis caching, RabbitMQ pub/sub messaging, and Prometheus observability.
