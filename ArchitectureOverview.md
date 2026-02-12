# Architecture Overview

## Tech Stack

### Backend:
- **Framework:** FastAPI (modern, fast, auto-generates OpenAPI docs)
- **ORM:** SQLAlchemy 2.0 (with async support)
- **Database:** PostgreSQL 15+
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** JWT (JSON Web Tokens) with OAuth2 password flow
- **Password Hashing:** pwdlib
- **Environment:** Python 3.11+

### Frontend:
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State Management:** React Context API (for authentication)

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
│ id (PK)         │◄────────┤ book_id (FK)         │         │ id (PK)         │
│ title           │         │ member_id (FK)       ├────────►│ name            │
│ author          │         │ borrowed_date        │         │ email (UNIQUE)  │
│ isbn (UNIQUE)   │         │ returned_date        │         │ phone (UNIQUE)  │
│ description     │         │ created_at           │         │ created_at      │
│ is_available    │         │ updated_at           │         │ updated_at      │
│ created_at      │         │                      │         └─────────────────┘
│ updated_at      │         │ *due_date (computed) │
└─────────────────┘         │ *status (computed)   │         ┌─────────────────┐
                            └──────────────────────┘         │     STAFFS      │
                                                             ├─────────────────┤
                                                             │ id (PK)         │
                                                             │ username (UNQ)  │
                                                             │ email (UNIQUE)  │
                                                             │ hashed_password │
                                                             │ full_name       │
                                                             │ created_at      │
                                                             └─────────────────┘
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
    borrowed_date TIMESTAMP,
    returned_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_borrowing_book_id ON borrowing_records(book_id);
CREATE INDEX idx_borrowing_member_id ON borrowing_records(member_id);
```

**Note:** `due_date` and `status` are computed properties in the application layer:
- `due_date` = `borrowed_date + 14 days`
- `status` = `"BORROWED"` if `returned_date` is NULL, else `"RETURNED"`

#### 4. staffs

```sql
CREATE TABLE staffs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Key Design Decisions:

- ✅ **Keep borrowing history** - Don't delete records when returned (set `returned_date`)
- ✅ **`is_available` flag on books** - Quick lookup without JOIN
- ✅ **Email as unique identifier** - Natural key for members and staff
- ✅ **Indexes** - Optimize common queries (by member, by book)
- ✅ **ON DELETE RESTRICT** - Prevent accidental data loss
- ✅ **Computed properties** - `due_date` and `status` calculated in application layer for flexibility
- ✅ **JWT Authentication** - Stateless authentication for staff members
- ✅ **Password hashing** - pwdlib for secure password storage

---

## Backend Architecture

### Project Structure:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment config (DB URL, JWT secret, etc.)
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy ORM models (Book, Member, Borrowing, Staff)
│   ├── schemas.py              # Pydantic schemas (request/response)
│   ├── utils.py                # Utility functions (JWT, password hashing)
│   │
│   └── routers/                # API endpoints
│       ├── __init__.py
│       ├── auth.py             # Authentication endpoints
│       ├── books.py            # Books CRUD
│       ├── members.py          # Members CRUD
│       └── borrowings.py       # Borrowing operations
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── seed_data.py                # Database seeding script
├── test_connection.py          # Database connection test
├── uv.lock
├── pyproject.toml
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

### Layer Responsibilities:

- **`config.py`** - Environment configuration using Pydantic Settings
- **`database.py`** - Async database engine and session management
- **`main.py`** - FastAPI app initialization, CORS, router registration, lifespan events
- **`models.py`** - SQLAlchemy ORM models with relationships and computed properties
- **`schemas.py`** - Pydantic models for request/response validation
- **`utils.py`** - JWT token creation/verification, password hashing/verification, OAuth2 scheme
- **`routers/`** - API endpoints organized by resource (auth, books, members, borrowings)
- **`routers/auth.py`** - Authentication endpoints (register, login, get current user)
- **Error Handling** - Using FastAPI's HTTPException for all error responses

---

## API Design (REST)

**Base URL:** `http://localhost:8000/api`

### Authentication Endpoints:

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| POST | `/auth/register` | Register new staff | `StaffCreate` | `StaffResponse` | No |
| POST | `/auth/login` | Login staff (OAuth2) | `OAuth2PasswordRequestForm` | `Token` | No |
| GET | `/auth/me` | Get current user | - | `StaffResponse` | Yes |

### Books Endpoints:

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| GET | `/books/` | List all books | - | `BookResponse[]` | No |
| GET | `/books/{id}` | Get book by ID | - | `BookResponse` | Yes |
| POST | `/books/` | Create new book | `BookCreate` | `BookResponse` | Yes |
| PUT | `/books/{id}` | Update book | `BookUpdate` | `BookResponse` | Yes |
| DELETE | `/books/{id}` | Delete book | - | `204 No Content` | Yes |

### Members Endpoints:

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| GET | `/members/` | List all members | - | `MemberResponse[]` | Yes |
| GET | `/members/{id}` | Get member by ID | - | `MemberResponse` | Yes |
| POST | `/members/` | Create new member | `MemberCreate` | `MemberResponse` | Yes |
| PUT | `/members/{id}` | Update member | `MemberUpdate` | `MemberResponse` | Yes |
| DELETE | `/members/{id}` | Delete member | - | `204 No Content` | Yes |

### Borrowing Endpoints:

| Method | Endpoint | Description | Request Body | Response | Auth Required |
|--------|----------|-------------|--------------|----------|---------------|
| GET | `/borrowings/` | List currently borrowed books | - | `BorrowResponse[]` | Yes |
| GET | `/borrowings/history` | Get all borrowing history | - | `BorrowResponse[]` | Yes |
| GET | `/borrowings/members/{id}` | Get member's borrowing records | - | `BorrowResponse[]` | Yes |
| POST | `/borrowings/borrow` | Borrow a book | `BorrowRequest` | `BorrowResponse` | Yes |
| PUT | `/borrowings/return` | Return a book | `ReturnRequest` | `ReturnResponse` | Yes |

### Sample Request/Response:

**POST /api/auth/login**

```json
// Request (form-data)
username: staff@library.com
password: securepassword123

// Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**POST /api/borrowings/borrow**

```json
// Request (requires Bearer token)
{
  "book_id": 1,
  "member_id": 5,
  "due_date": null  // Optional, computed as borrowed_date + 14 days
}

// Response (200 OK)
{
  "id": 10,
  "book_id": 1,
  "member_id": 5,
  "borrowed_date": "2026-02-12T06:45:00Z",
  "due_date": "2026-02-26T06:45:00Z",  // Computed property
  "returned_date": null,
  "status": "BORROWED",  // Computed property
  "book": {
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "9780743273565",
    "is_available": false
  },
  "member": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890"
  }
}

// Error Response (400 Bad Request)
{
  "detail": "Book not available."
}

// Error Response (401 Unauthorized)
{
  "detail": "Not authenticated"
}
```

---

## Business Logic & Validation

### Authentication Flow:

```python
# Staff Registration
async def create_staff(staff: StaffCreate, db: AsyncSession):
    # 1. Check if username already exists (case-insensitive)
    # 2. Check if email already exists (case-insensitive)
    # 3. Hash password using pwdlib
    # 4. Create staff record
    # 5. Return staff (without password)

# Staff Login
async def login(credentials: OAuth2PasswordRequestForm, db: AsyncSession):
    # 1. Find staff by email (username field contains email)
    # 2. Verify password using pwdlib
    # 3. Create JWT access token with staff.id as subject
    # 4. Return token (expires in configured minutes)

# Protected Endpoints
async def get_current_user(token: str, db: AsyncSession):
    # 1. Verify JWT token
    # 2. Extract staff_id from token subject
    # 3. Fetch staff from database
    # 4. Return staff or raise 401 Unauthorized
```

### Borrow Operation:

```python
# Actual implementation from routers/borrowings.py
async def borrow_book(borrow_request: BorrowRequest, current_user: Staff, db: AsyncSession):
    # 1. Check if book exists
    book = await db.get(Book, borrow_request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    
    # 2. Check if book is available
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Book not available.")
    
    # 3. Check if member exists
    member = await db.get(Member, borrow_request.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
    
    # 4. Create borrowing record
    record = Borrowing(
        book_id=borrow_request.book_id,
        member_id=borrow_request.member_id,
        borrowed_date=datetime.now(UTC)
    )
    db.add(record)
    
    # 5. Mark book as unavailable
    book.is_available = False
    
    # 6. Commit and return with relationships loaded
    await db.commit()
    await db.refresh(record, attribute_names=["book", "member"])
    return record  # due_date and status computed automatically
```

### Return Operation:

```python
# Actual implementation from routers/borrowings.py
async def return_book(return_request: ReturnRequest, current_user: Staff, db: AsyncSession):
    # 1. Find active borrowing record for book and member
    record = await db.execute(
        select(Borrowing)
        .options(selectinload(Borrowing.book), selectinload(Borrowing.member))
        .where(
            Borrowing.book_id == return_request.book_id,
            Borrowing.member_id == return_request.member_id,
            Borrowing.returned_date.is_(None)  # Only unreturned books
        )
    )
    record = record.scalars().first()
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail="No borrowing record found for provided book_id and member_id."
        )
    
    # 2. Update record with return date
    record.returned_date = datetime.now(UTC)
    
    # 3. Mark book as available
    record.book.is_available = True
    
    # 4. Commit and return
    await db.commit()
    await db.refresh(record, attribute_names=["book", "member"])
    return record  # status automatically becomes "RETURNED"
```

### Computed Properties:

```python
# In models.py - Borrowing model
@property
def due_date(self) -> datetime | None:
    """Calculate due date as 14 days after borrowed date"""
    if self.borrowed_date:
        return self.borrowed_date + timedelta(days=14)
    return None

@property
def status(self) -> str:
    """Determine status based on returned_date"""
    return "RETURNED" if self.returned_date else "BORROWED"
```

---

## Frontend Architecture

### Project Structure:

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with metadata
│   │   ├── page.tsx            # Home page (redirects to login/admin)
│   │   ├── globals.css         # Global styles and Tailwind imports
│   │   │
│   │   ├── login/
│   │   │   └── page.tsx        # Login page
│   │   │
│   │   ├── register/
│   │   │   └── page.tsx        # Staff registration page
│   │   │
│   │   └── admin/
│   │       └── page.tsx        # Admin dashboard (all-in-one)
│   │
│   ├── components/
│   │   ├── Header.tsx          # Navigation header
│   │   ├── SideBar.tsx         # Sidebar navigation
│   │   ├── SearchBar.tsx       # Search functionality
│   │   ├── BookTable.tsx       # Reusable book table
│   │   │
│   │   └── admin/              # Admin-specific components
│   │       ├── BookSection.tsx      # Books management section
│   │       ├── MemberSection.tsx    # Members management section
│   │       └── BorrowingSection.tsx # Borrowings management section
│   │
│   ├── context/
│   │   └── AuthContext.tsx     # Authentication context provider
│   │
│   └── lib/
│       ├── api.ts              # Axios API client with interceptors
│       └── types.ts            # TypeScript interfaces
│
├── public/
│   └── (static assets)
│
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.mjs
├── .env.example
└── Dockerfile
```

### Key Pages:

- **Home (`/`)** - Landing page that redirects based on auth status
- **Login (`/login`)** - Staff authentication with JWT
- **Register (`/register`)** - New staff registration
- **Admin Dashboard (`/admin`)** - Unified dashboard with three sections:
  - **Books Section** - List, add, edit, delete books with search
  - **Members Section** - List, add, edit, delete members with search
  - **Borrowings Section** - Borrow/return books, view history

### Authentication Flow:

1. User logs in via `/login` with email and password
2. Backend returns JWT access token
3. Frontend stores token in localStorage
4. Axios interceptor adds `Authorization: Bearer <token>` to all requests
5. Protected routes check for token and redirect to login if missing
6. Token is verified on backend for all protected endpoints

---
