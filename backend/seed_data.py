"""
Seed script to populate the database with sample data for testing.

Usage:
    uv run python seed_data.py
    # or
    python seed_data.py
"""

import asyncio
from datetime import datetime, timedelta, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker, engine, Base
from app.models import Book, Member, Borrowing, Staff
from app.utils import get_password_hash


async def clear_database():
    """Drop and recreate all tables."""
    print("Clearing existing data...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database cleared and tables recreated.")


async def seed_staff(session: AsyncSession):
    """Create sample staff users."""
    print("\nSeeding staff users...")

    staff_users = [
        Staff(
            username="admin",
            email="admin@library.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Library Administrator",
        ),
        Staff(
            username="staff1",
            email="staff1@library.com",
            hashed_password=get_password_hash("staff123"),
            full_name="John Librarian",
        ),
    ]

    session.add_all(staff_users)
    await session.commit()
    print(f"Created {len(staff_users)} staff users")
    print("  - Username: admin, Password: admin123")
    print("  - Username: staff1, Password: staff123")


async def seed_books(session: AsyncSession):
    """Create sample books."""
    print("\nSeeding books...")

    books = [
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="9780743273565",
            description="A classic American novel set in the Jazz Age",
            is_available=True,
        ),
        Book(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            isbn="9780061120084",
            description="A gripping tale of racial injustice and childhood innocence",
            is_available=True,
        ),
        Book(
            title="1984",
            author="George Orwell",
            isbn="9780451524935",
            description="A dystopian social science fiction novel",
            is_available=True,
        ),
        Book(
            title="Pride and Prejudice",
            author="Jane Austen",
            isbn="9780141439518",
            description="A romantic novel of manners",
            is_available=True,
        ),
        Book(
            title="The Catcher in the Rye",
            author="J.D. Salinger",
            isbn="9780316769174",
            description="A story about teenage rebellion and alienation",
            is_available=False,
        ),
        Book(
            title="Harry Potter and the Philosopher's Stone",
            author="J.K. Rowling",
            isbn="9780747532699",
            description="The first book in the Harry Potter series",
            is_available=True,
        ),
        Book(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            isbn="9780547928227",
            description="A fantasy novel and children's book",
            is_available=True,
        ),
        Book(
            title="Fahrenheit 451",
            author="Ray Bradbury",
            isbn="9781451673319",
            description="A dystopian novel about a future where books are banned",
            is_available=False,
        ),
        Book(
            title="The Lord of the Rings",
            author="J.R.R. Tolkien",
            isbn="9780544003415",
            description="An epic high-fantasy novel",
            is_available=True,
        ),
        Book(
            title="Animal Farm",
            author="George Orwell",
            isbn="9780451526342",
            description="An allegorical novella about Stalinism",
            is_available=True,
        ),
    ]

    session.add_all(books)
    await session.commit()
    print(f"Created {len(books)} books")

    # Refresh to get IDs
    for book in books:
        await session.refresh(book)

    return books


async def seed_members(session: AsyncSession):
    """Create sample members."""
    print("\nSeeding members...")

    members = [
        Member(name="Alice Johnson", email="alice.johnson@email.com", phone="555-0101"),
        Member(name="Bob Smith", email="bob.smith@email.com", phone="555-0102"),
        Member(
            name="Carol Williams", email="carol.williams@email.com", phone="555-0103"
        ),
        Member(name="David Brown", email="david.brown@email.com", phone="555-0104"),
        Member(name="Eve Davis", email="eve.davis@email.com", phone="555-0105"),
    ]

    session.add_all(members)
    await session.commit()
    print(f"Created {len(members)} members")

    # Refresh to get IDs
    for member in members:
        await session.refresh(member)

    return members


async def seed_borrowings(
    session: AsyncSession, books: list[Book], members: list[Member]
):
    """Create sample borrowing records."""
    print("\nSeeding borrowing records...")

    now = datetime.now(UTC)

    borrowings = [
        # Active borrowing (The Catcher in the Rye borrowed by Alice)
        Borrowing(
            book_id=books[4].id,  # The Catcher in the Rye
            member_id=members[0].id,  # Alice Johnson
            borrowed_date=now - timedelta(days=5),
            returned_date=None,
        ),
        # Active borrowing (Fahrenheit 451 borrowed by Bob)
        Borrowing(
            book_id=books[7].id,  # Fahrenheit 451
            member_id=members[1].id,  # Bob Smith
            borrowed_date=now - timedelta(days=10),
            returned_date=None,
        ),
        # Returned borrowing (1984 borrowed and returned by Carol)
        Borrowing(
            book_id=books[2].id,  # 1984
            member_id=members[2].id,  # Carol Williams
            borrowed_date=now - timedelta(days=30),
            returned_date=now - timedelta(days=16),
        ),
        # Returned borrowing (Pride and Prejudice borrowed and returned by David)
        Borrowing(
            book_id=books[3].id,  # Pride and Prejudice
            member_id=members[3].id,  # David Brown
            borrowed_date=now - timedelta(days=25),
            returned_date=now - timedelta(days=11),
        ),
        # Returned borrowing (The Great Gatsby borrowed and returned by Eve)
        Borrowing(
            book_id=books[0].id,  # The Great Gatsby
            member_id=members[4].id,  # Eve Davis
            borrowed_date=now - timedelta(days=20),
            returned_date=now - timedelta(days=6),
        ),
    ]

    session.add_all(borrowings)
    await session.commit()
    print(f"Created {len(borrowings)} borrowing records")
    print(
        f"  - {sum(1 for b in borrowings if b.returned_date is None)} active borrowings"
    )
    print(
        f"  - {sum(1 for b in borrowings if b.returned_date is not None)} returned books"
    )


async def main():
    """Main function to seed the database."""
    print("=" * 60)
    print("Library Management System - Database Seeding")
    print("=" * 60)

    # Clear existing data
    await clear_database()

    # Create a session
    async with async_session_maker() as session:
        # Seed data in order
        await seed_staff(session)
        books = await seed_books(session)
        members = await seed_members(session)
        await seed_borrowings(session, books, members)

    print("\n" + "=" * 60)
    print("Database seeding completed successfully!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Login with username: admin, password: admin123")
    print("  2. Access the API at http://localhost:8000/docs")
    print("  3. View books, members, and borrowing records")
    print("\nSample data includes:")
    print("  - 2 staff users")
    print("  - 10 books (8 available, 2 currently borrowed)")
    print("  - 5 members")
    print("  - 5 borrowing records (2 active, 3 returned)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
