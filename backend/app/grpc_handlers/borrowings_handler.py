from datetime import UTC, datetime

import grpc
from protos import borrowings_pb2, borrowings_pb2_grpc
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models
from app.database import AsyncSessionLocal
from app.grpc_handlers.books_handler import book_to_proto
from app.grpc_handlers.helpers import datetime_to_timestamp, get_current_user
from app.grpc_handlers.members_handler import member_to_proto


def borrowing_to_proto(borrowing: models.Borrowing) -> borrowings_pb2.BorrowResponse:
    return borrowings_pb2.BorrowResponse(
        id=borrowing.id,
        book_id=borrowing.book_id,
        member_id=borrowing.member_id,
        due_date=(
            datetime_to_timestamp(borrowing.due_date) if borrowing.due_date else None
        ),
        borrowed_date=datetime_to_timestamp(borrowing.borrowed_date),
        status=borrowing.status,
        returned_date=(
            datetime_to_timestamp(borrowing.returned_date)
            if borrowing.returned_date
            else None
        ),
        book=book_to_proto(borrowing.book),
        member=member_to_proto(borrowing.member),
    )


def return_to_proto(borrowing: models.Borrowing) -> borrowings_pb2.ReturnResponse:
    return borrowings_pb2.ReturnResponse(
        id=borrowing.id,
        book_id=borrowing.book_id,
        member_id=borrowing.member_id,
        status=borrowing.status,
        returned_date=(
            datetime_to_timestamp(borrowing.returned_date)
            if borrowing.returned_date
            else None
        ),
        book=book_to_proto(borrowing.book),
        member=member_to_proto(borrowing.member),
    )


class BorrowingServicer(borrowings_pb2_grpc.BorrowingServiceServicer):
    async def GetBorrowingsHistory(
        self,
        request: borrowings_pb2.GetBorrowRequest,
        context: grpc.aio.ServicerContext,
    ) -> borrowings_pb2.GetBorrowingsResponse:
        await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Borrowing)
                .options(selectinload(models.Borrowing.book))
                .options(selectinload(models.Borrowing.member))
                .order_by(models.Borrowing.borrowed_date.desc())
            )
            records = result.scalars().all()
            return borrowings_pb2.GetBorrowingsResponse(
                borrowings=[borrowing_to_proto(borrow) for borrow in records]
            )

    async def GetCurrentBorrowings(
        self,
        request: borrowings_pb2.GetBorrowRequest,
        context: grpc.aio.ServicerContext,
    ) -> borrowings_pb2.GetBorrowingsResponse:
        await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Borrowing)
                .options(selectinload(models.Borrowing.book))
                .options(selectinload(models.Borrowing.member))
                .where(models.Borrowing.returned_date.is_(None))
                .order_by(models.Borrowing.borrowed_date.desc())
            )
            records = result.scalars().all()
            return borrowings_pb2.GetBorrowingsResponse(
                borrowings=[borrowing_to_proto(borrow) for borrow in records]
            )

    async def GetMemberBorrowings(
        self,
        request: borrowings_pb2.GetMemberBorrowingsRequest,
        context: grpc.aio.ServicerContext,
    ) -> borrowings_pb2.GetBorrowingsResponse:
        await get_current_user(context)
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "member id must be positive.",
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Member).where(models.Member.id == request.id)
            )
            member = result.scalars().first()
            if not member:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Member not found.")

            result = await db.execute(
                select(models.Borrowing)
                .options(selectinload(models.Borrowing.book))
                .options(selectinload(models.Borrowing.member))
                .where(models.Borrowing.member_id == request.id)
                .order_by(models.Borrowing.borrowed_date.desc())
            )
            records = result.scalars().all()
            return borrowings_pb2.GetBorrowingsResponse(
                borrowings=[borrowing_to_proto(borrow) for borrow in records]
            )

    async def BorrowBook(
        self,
        request: borrowings_pb2.BorrowRequest,
        context: grpc.aio.ServicerContext,
    ) -> borrowings_pb2.BorrowResponse:
        await get_current_user(context)
        if request.book_id <= 0 or request.member_id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "book id and member id must be positive",
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Book)
                .where(models.Book.id == request.book_id)
                .with_for_update()
            )
            book = result.scalars().first()
            if not book:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Book not found.",
                )

            if not book.is_available:
                await context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION,
                    "Book not available.",
                )

            result = await db.execute(
                select(models.Member)
                .where(models.Member.id == request.member_id)
                .with_for_update()
            )
            member = result.scalars().first()
            if not member:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Member not found.")

            new_borrow_record = models.Borrowing(
                book_id=request.book_id,
                member_id=request.member_id,
                borrowed_date=datetime.now(UTC),
            )

            db.add(new_borrow_record)

            book.is_available = False
            await db.commit()
            await db.refresh(new_borrow_record, attribute_names=["book", "member"])
            return borrowing_to_proto(new_borrow_record)

    async def ReturnBook(
        self,
        request: borrowings_pb2.ReturnRequest,
        context: grpc.aio.ServicerContext,
    ) -> borrowings_pb2.ReturnResponse:
        await get_current_user(context)
        if request.book_id <= 0 or request.member_id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "book id and member id must be positive",
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Borrowing)
                .options(selectinload(models.Borrowing.book))
                .options(selectinload(models.Borrowing.member))
                .where(
                    models.Borrowing.book_id == request.book_id,
                    models.Borrowing.member_id == request.member_id,
                    models.Borrowing.returned_date.is_(None),
                )
                .with_for_update()
            )
            borrowing = result.scalars().first()
            if not borrowing:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "No borrowing record found for provided book_id and member_id.",
                )

            borrowing.returned_date = datetime.now(UTC)
            borrowing.book.is_available = True

            await db.commit()
            await db.refresh(borrowing, attribute_names=["book", "member"])
            return return_to_proto(borrowing)
