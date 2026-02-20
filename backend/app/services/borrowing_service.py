from datetime import UTC, datetime
from typing import Annotated

import aio_pika
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from app.dependencies import get_rmq_channel
from app.redis_client import get_cache, set_cache, delete_cache, invalidate_prefix
from app.repositories.unit_of_work import UnitOfWork
from app.exceptions import ActionForbiddenError, NotFoundError
from pubsub import Topology, publish_json


class BorrowingService:
    def __init__(
        self,
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        rmq_channel: Annotated[aio_pika.RobustChannel, Depends(get_rmq_channel)],
    ):
        self.uow = uow
        self.rmq_channel = rmq_channel

    async def get_current_borrowing_records(
        self,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = f"borrowings:list:limit:{limit}:offset:{offset}"
        cached_borrowings = await get_cache(cache_key)
        if cached_borrowings:
            return cached_borrowings

        borrowings = await self.uow.borrowings.get_active_borrowings(limit, offset)
        await set_cache(cache_key, jsonable_encoder(borrowings))
        return borrowings

    async def get_borrowing_records_by_member_id(
        self,
        member_id: int,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = f"borrowings:member_id:{member_id}:limit:{limit}:offset:{offset}"
        cached_borrowings = await get_cache(cache_key)
        if cached_borrowings:
            return cached_borrowings

        borrowings = await self.uow.borrowings.get_borrowings_by_member_id(
            member_id, limit, offset
        )
        await set_cache(cache_key, jsonable_encoder(borrowings))
        return borrowings

    async def get_borrowing_records_by_book_id(
        self,
        book_id: int,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = f"borrowings:book_id:{book_id}:limit:{limit}:offset:{offset}"
        cached_borrowings = await get_cache(cache_key)
        if cached_borrowings:
            return cached_borrowings

        borrowings = await self.uow.borrowings.get_borrowings_by_book_id(
            book_id, limit, offset
        )
        await set_cache(cache_key, jsonable_encoder(borrowings))
        return borrowings

    async def get_all_borrowings_history(
        self,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = f"borrowings:history:limit:{limit}:offset:{offset}"
        cached_borrowings = await get_cache(cache_key)
        if cached_borrowings:
            return cached_borrowings

        borrowings = await self.uow.borrowings.get_all_borrowings_history(limit, offset)
        await set_cache(cache_key, jsonable_encoder(borrowings))
        return borrowings

    async def borrow_book(self, book_id: int, member_id: int):
        async with self.uow:
            book = await self.uow.books.get_book_by_id(book_id)
            if not book.is_available:
                raise ActionForbiddenError(message="Book not available")

            _ = await self.uow.members.get_member_by_id(member_id)

            record = await self.uow.borrowings.create_record(book_id, member_id)

            book.is_available = False
            await self.uow.session.flush()
            await self.uow.session.refresh(record, attribute_names=["book", "member"])

        await delete_cache(f"books:id:{book_id}")
        await invalidate_prefix("books:list")
        await invalidate_prefix("borrowings")

        await publish_json(
            channel=self.rmq_channel,
            exchange=Topology.DIRECT_EXCHANGE,
            key=Topology.BORROWING_KEY,
            val={
                "event": "book_borrowed",
                "book_id": book_id,
                "member_id": member_id,
                "book_title": book.title,
                "member_name": record.member.name,
                "member_phone": record.member.phone,
                "borrowed_date": (
                    record.borrowed_date.isoformat() if record.borrowed_date else None
                ),
                "due_date": record.due_date.isoformat() if record.due_date else None,
            },
        )

        return record

    async def return_book(
        self,
        book_id: int,
        member_id: int,
    ):
        async with self.uow:
            record = await self.uow.borrowings.get_active_record(book_id, member_id)
            if not record:
                raise NotFoundError(
                    message="No active borrowing record not found for Book and Member specified."
                )

            record.returned_date = datetime.now(UTC)
            record.book.is_available = True
            # Keep original due date to check if it was returned late

            await self.uow.session.flush()
            await self.uow.session.refresh(record, attribute_names=["book", "member"])

        await delete_cache(f"books:id:{book_id}")
        await invalidate_prefix("books:list")
        await invalidate_prefix("borrowings")

        await publish_json(
            channel=self.rmq_channel,
            exchange=Topology.DIRECT_EXCHANGE,
            key=Topology.RETURNED_KEY,
            val={
                "event": "book_returned",
                "book_id": book_id,
                "member_id": member_id,
                "book_title": record.book.title,
                "member_name": record.member.name,
                "member_phone": record.member.phone,
                "borrowed_date": (
                    record.borrowed_date.isoformat() if record.borrowed_date else None
                ),
                "due_date": record.due_date.isoformat() if record.due_date else None,
                "returned_date": (
                    record.returned_date.isoformat() if record.returned_date else None
                ),
            },
        )

        return record
