import grpc
from protos import books_pb2, books_pb2_grpc, common_pb2
from sqlalchemy import select

from app import models
from app.database import AsyncSessionLocal
from app.grpc_handlers.helpers import datetime_to_timestamp, get_current_user


def book_to_proto(book: models.Book) -> books_pb2.Book:
    return books_pb2.Book(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description or "",
        is_available=book.is_available,
        created_at=datetime_to_timestamp(book.created_at),
        updated_at=datetime_to_timestamp(book.updated_at),
    )


class BookServicer(books_pb2_grpc.BookServiceServicer):
    async def GetBooks(
        self,
        request: books_pb2.GetBooksRequest,
        context: grpc.aio.ServicerContext,
    ) -> books_pb2.GetBooksResponse:
        """Get all books with optional filters"""
        async with AsyncSessionLocal() as db:
            query = select(models.Book)

            if request.HasField("title"):
                query = query.where(models.Book.title.ilike(f"%{request.title}%"))

            if request.HasField("author"):
                query = query.where(models.Book.author.ilike(f"%{request.author}%"))

            result = await db.execute(query)
            books = result.scalars().all()

            return books_pb2.GetBooksResponse(
                books=[book_to_proto(book) for book in books]
            )

    async def GetBook(
        self,
        request: books_pb2.GetBookRequest,
        context: grpc.aio.ServicerContext,
    ) -> books_pb2.Book:
        await get_current_user(context)
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "book_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Book).where(models.Book.id == request.id)
            )
            book = result.scalars().first()

            if not book:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")
            return book_to_proto(book)

    async def CreateBook(
        self,
        request: books_pb2.CreateBookRequest,
        context: grpc.aio.ServicerContext,
    ) -> books_pb2.Book:
        await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Book).where(models.Book.isbn == request.isbn)
            )
            existing_book = result.scalars().first()

            if existing_book:
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS, "Book with this ISBN already exists"
                )

            new_book = models.Book(
                title=request.title,
                author=request.author,
                isbn=request.isbn,
                description=request.description
                if request.HasField("description")
                else None,
            )

            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)

            return book_to_proto(new_book)

    async def UpdateBook(
        self,
        request: books_pb2.UpdateBookRequest,
        context: grpc.aio.ServicerContext,
    ) -> books_pb2.Book:
        """
        Update an existing book
        Equivalent to: PUT /api/books/{id}
        """
        await get_current_user(context)
        # Validation
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "book_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            # Get existing book
            result = await db.execute(
                select(models.Book)
                .where(models.Book.id == request.id)
                .with_for_update()
            )
            book = result.scalars().first()

            if not book:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")

            # Check if book is currently borrowed (same as REST)
            result = await db.execute(
                select(models.Borrowing)
                .where(
                    models.Borrowing.book_id == request.id,
                    models.Borrowing.returned_date.is_(None),
                )
                .with_for_update()
            )
            is_borrowed = result.scalars().first()

            if is_borrowed:
                await context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION, "Cannot update a borrowed book"
                )

            # Update only provided fields
            if request.HasField("title"):
                book.title = request.title
            if request.HasField("author"):
                book.author = request.author
            if request.HasField("description"):
                book.description = request.description
            if request.HasField("is_available"):
                book.is_available = request.is_available

            await db.commit()
            await db.refresh(book)

            return book_to_proto(book)

    async def DeleteBook(
        self,
        request: books_pb2.DeleteBookRequest,
        context: grpc.aio.ServicerContext,
    ) -> common_pb2.Empty:
        """
        Delete a book
        Equivalent to: DELETE /api/books/{id}
        """
        await get_current_user(context)
        # Validation
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "book_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            # Get existing book
            result = await db.execute(
                select(models.Book)
                .where(models.Book.id == request.id)
                .with_for_update()
            )
            book = result.scalars().first()

            if not book:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Book not found")

            # Check if book is available (same as REST)
            if not book.is_available:
                await context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION,
                    "Cannot delete book that is currently borrowed or marked as unavailable",
                )

            # Check borrowing history (same as REST)
            result = await db.execute(
                select(models.Borrowing)
                .where(models.Borrowing.book_id == book.id)
                .with_for_update()
            )
            has_history = result.scalars().first()

            if has_history:
                await context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION,
                    "Cannot delete book with borrowing history",
                )

            await db.delete(book)
            await db.commit()

            return common_pb2.Empty()
