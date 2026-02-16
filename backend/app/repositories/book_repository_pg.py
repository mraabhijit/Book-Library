from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.schemas import BookCreate, BookUpdate
from app.exceptions import (
    AlreadyExistsError,
    ActionForbiddenError,
    NotFoundError,
)


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_books(
        self, title: str | None, author: str | None, limit: int, offset: int
    ) -> list[models.Book]:
        query = select(models.Book)
        if title:
            query = query.where(models.Book.title.ilike(f"%{title}%"))
        if author:
            query = query.where(models.Book.author.ilike(f"%{author}%"))

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        books = result.scalars().all()

        return books

    async def get_book_by_id(self, book_id: int) -> models.Book:
        result = await self.db.execute(
            select(models.Book).where(models.Book.id == book_id),
        )

        book = result.scalars().first()
        if not book:
            raise NotFoundError(message="Book not found")

        return book

    async def create_book(self, book: BookCreate) -> models.Book:
        result = await self.db.execute(
            select(models.Book).where(models.Book.isbn == book.isbn)
        )
        existing_book = result.scalars().first()
        if existing_book:
            raise AlreadyExistsError(
                message="Book with this ISBN already exists",
            )

        new_book = models.Book(**book.model_dump())

        self.db.add(new_book)

        return new_book

    async def update_book(
        self,
        book_id: int,
        book: BookUpdate,
    ) -> models.Book:
        result = await self.db.execute(
            select(models.Book).where(models.Book.id == book_id)
        )
        existing_book = result.scalars().first()
        if not existing_book:
            raise NotFoundError(message="Book not found")

        result = await self.db.execute(
            select(models.Borrowing).where(
                models.Borrowing.book_id == book_id,
                models.Borrowing.returned_date.is_(None),
            )
        )
        is_borrowed = result.scalars().first()
        if is_borrowed:
            raise ActionForbiddenError(
                message="Cannot update a borrowed book",
            )

        updated_data = book.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(existing_book, field, value)

        return existing_book

    async def delete_book(self, book_id):
        result = await self.db.execute(
            select(models.Book).where(models.Book.id == book_id)
        )
        existing_book = result.scalars().first()
        if not existing_book:
            raise NotFoundError(message="Book not found")

        if not existing_book.is_available:
            raise ActionForbiddenError(
                message="Cannot delete book that is currently borrowed or marked as unavailable.",
            )

        result = await self.db.execute(
            select(models.Borrowing).where(models.Borrowing.book_id == existing_book.id)
        )
        has_borrowing_history = result.scalars().first()
        if has_borrowing_history:
            raise ActionForbiddenError(
                message="Cannot delete book with borrowing history.",
            )

        await self.db.delete(existing_book)
