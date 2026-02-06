# Architecture Overview

## Tech Stack

### Backend:
- **Framework:** FastAPI (modern, fast, auto-generates OpenAPI docs)
- **ORM:** SQLAlchemy 2.0 (with async support)
- **Database:** PostgreSQL 15+
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Environment:** Python 3.11+

### Frontend:
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios or Fetch API
- **UI Components:** Shadcn/ui (optional, for professional look)

### Infrastructure:
- **Containerization:** Docker + Docker Compose
- **Database Client:** asyncpg (for async PostgreSQL)

---

## Database Schema Design

### Entity Relationship Diagram (ERD):

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│     BOOKS       │         │  BORROWING_RECORDS   │         │    MEMBERS      │
├─────────────────┤         ├──────────────────────┤         ├─────────────────┤
│ id (PK)         │◄───────┤ book_id (FK)         │         │ id (PK)         │
│ title           │         │ member_id (FK)       ├────────►│ name            │
│ author          │         │ borrowed_date        │         │ email (UNIQUE)  │
│ isbn            │         │ due_date             │         │ phone           │
│ description     │         │ returned_date        │         │ created_at      │
│ is_available    │         │ status               │         │ updated_at      │
│ created_at      │         │ created_at           │         └─────────────────┘
│ updated_at      │         │ updated_at           │
└─────────────────┘         └──────────────────────┘
```

### Table Definitions:

#### 1. books

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    description TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. members

```sql
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. borrowing_records

```sql
CREATE TABLE borrowing_records (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    borrowed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    returned_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'borrowed', -- 'borrowed', 'returned', 'overdue'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_borrowing_book_id ON borrowing_records(book_id);
CREATE INDEX idx_borrowing_member_id ON borrowing_records(member_id);
CREATE INDEX idx_borrowing_status ON borrowing_records(status);
```

### Key Design Decisions:

- ✅ **Keep borrowing history** - Don't delete records when returned (set `returned_date`)
- ✅ **`is_available` flag on books** - Quick lookup without JOIN
- ✅ **Email as unique identifier** - Natural key for members
- ✅ **Status enum** - Track borrowed/returned/overdue states
- ✅ **Indexes** - Optimize common queries (by member, by book, by status)
- ✅ **ON DELETE RESTRICT** - Prevent accidental data loss

---

## Backend Architecture

### Project Structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment config (DB URL, etc.)
│   ├── database.py             # Database connection & session
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrowing_record.py
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrowing.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── books.py
│   │   ├── members.py
│   │   └── borrowing.py
│   │
│   ├── crud/                   # Database operations
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── member.py
│   │   └── borrowing.py
│   │
│   └── exceptions.py           # Custom exceptions
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                      # Unit tests (optional for take-home)
│   └── __init__.py
│
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

### Layer Responsibilities:

- **`main.py`** - App initialization, CORS, middleware
- **`models/`** - SQLAlchemy ORM models (database tables)
- **`schemas/`** - Pydantic models (API validation)
- **`routers/`** - API endpoints (HTTP handlers)
- **`crud/`** - Database operations (separation of concerns)
- **`exceptions.py`** - Custom exceptions (BookNotAvailable, MemberNotFound, etc.)

---

## API Design (REST)

**Base URL:** `http://localhost:8000/api/v1`

### Books Endpoints:

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/books` | List all books | - | `Book[]` |
| GET | `/books/{id}` | Get book by ID | - | `Book` |
| POST | `/books` | Create new book | `BookCreate` | `Book` |
| PUT | `/books/{id}` | Update book | `BookUpdate` | `Book` |
| DELETE | `/books/{id}` | Delete book | - | `204 No Content` |

### Members Endpoints:

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/members` | List all members | - | `Member[]` |
| GET | `/members/{id}` | Get member by ID | - | `Member` |
| POST | `/members` | Create new member | `MemberCreate` | `Member` |
| PUT | `/members/{id}` | Update member | `MemberUpdate` | `Member` |
| DELETE | `/members/{id}` | Delete member | - | `204 No Content` |

### Borrowing Endpoints:

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/borrow` | Borrow a book | `BorrowRequest` | `BorrowingRecord` |
| POST | `/return` | Return a book | `ReturnRequest` | `BorrowingRecord` |
| GET | `/borrowed` | List all currently borrowed books | - | `BorrowingRecord[]` |
| GET | `/members/{id}/borrowed` | Get member's borrowed books | - | `BorrowingRecord[]` |
| GET | `/borrowing-history` | Get all borrowing history | - | `BorrowingRecord[]` |

### Sample Request/Response:

**POST /api/v1/borrow**

```json
// Request
{
  "book_id": 1,
  "member_id": 5,
  "due_date": "2026-02-19T00:00:00Z"  // Optional, 14 days default
}

// Response (200 OK)
{
  "id": 10,
  "book_id": 1,
  "member_id": 5,
  "borrowed_date": "2026-02-05T14:00:00Z",
  "due_date": "2026-02-19T00:00:00Z",
  "returned_date": null,
  "status": "borrowed",
  "book": {
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald"
  },
  "member": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com"
  }
}

// Error Response (400 Bad Request)
{
  "detail": "Book is not available for borrowing"
}
```

---

## Business Logic & Validation

### Borrow Operation:

```python
# Pseudo-code for borrow logic
def borrow_book(book_id, member_id, due_date):
    # 1. Check if book exists
    book = get_book_by_id(book_id)
    if not book:
        raise BookNotFound()
    
    # 2. Check if book is available
    if not book.is_available:
        raise BookNotAvailable()
    
    # 3. Check if member exists
    member = get_member_by_id(member_id)
    if not member:
        raise MemberNotFound()
    
    # 4. Create borrowing record
    record = create_borrowing_record(
        book_id=book_id,
        member_id=member_id,
        due_date=due_date or (now() + 14 days)
    )
    
    # 5. Mark book as unavailable
    update_book(book_id, is_available=False)
    
    return record
```

### Return Operation:

```python
def return_book(borrowing_record_id):
    # 1. Get borrowing record
    record = get_borrowing_record(borrowing_record_id)
    if not record:
        raise RecordNotFound()
    
    # 2. Check if already returned
    if record.returned_date:
        raise AlreadyReturned()
    
    # 3. Update record
    update_borrowing_record(
        id=borrowing_record_id,
        returned_date=now(),
        status='returned'
    )
    
    # 4. Mark book as available
    update_book(record.book_id, is_available=True)
    
    return record
```

---

## Frontend Architecture

### Project Structure:

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home/Dashboard
│   ├── books/
│   │   ├── page.tsx            # Books list
│   │   └── [id]/
│   │       └── page.tsx        # Book details/edit
│   ├── members/
│   │   ├── page.tsx            # Members list
│   │   └── [id]/
│   │       └── page.tsx        # Member details/edit
│   └── borrowing/
│       └── page.tsx            # Borrowing dashboard
│
├── components/
│   ├── BookForm.tsx
│   ├── MemberForm.tsx
│   ├── BorrowForm.tsx
│   ├── BookTable.tsx
│   ├── MemberTable.tsx
│   └── BorrowedBooksTable.tsx
│
├── lib/
│   ├── api.ts                  # API client functions
│   └── types.ts                # TypeScript types
│
├── package.json
└── tailwind.config.ts
```

### Key Pages:

- **Dashboard (`/`)** - Overview with stats
- **Books (`/books`)** - List, add, edit, delete books
- **Members (`/members`)** - List, add, edit, delete members
- **Borrowing (`/borrowing`)** - Borrow/return interface, view borrowed books

---

## Development Workflow

### Phase 1: Backend Foundation (Days 1-2)
1. Set up Docker Compose (PostgreSQL) - Done
2. Initialize FastAPI project - Done
3. Create SQLAlchemy models - Done
4. Set up Alembic migrations
5. Create database schema

### Phase 2: Backend APIs (Days 3-5)
1. Implement Books CRUD
2. Implement Members CRUD
3. Implement Borrowing logic
4. Add validation & error handling
5. Test with Swagger UI

### Phase 3: Frontend (Days 6-8)
1. Set up Next.js project
2. Create Books management page
3. Create Members management page
4. Create Borrowing dashboard
5. Connect to backend API

### Phase 4: Polish (Days 9-10)
1. Integration testing
2. Error handling on frontend
3. README documentation
4. Seed data script
5. Final review
