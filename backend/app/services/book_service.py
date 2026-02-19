from typing import Annotated

import aio_pika
from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from app.dependencies import get_rmq_channel
from app.redis_client import delete_cache, get_cache, invalidate_prefix, set_cache
from app.repositories.unit_of_work import UnitOfWork
from app.schemas import BookCreate, BookUpdate
from pubsub import Topology, publish_json


class BookService:
    def __init__(
        self,
        uow: Annotated[UnitOfWork, Depends(UnitOfWork)],
        rmq_channel: Annotated[aio_pika.RobustChannel, Depends(get_rmq_channel)],
    ):
        self.uow = uow
        self.rmq_channel = rmq_channel

    async def get_books(
        self,
        title: str | None = None,
        author: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = (
            f"books:list:title:{title}:author:{author}:limit:{limit}:offset:{offset}"
        )
        cached_books = await get_cache(cache_key)
        if cached_books:
            return cached_books

        books = await self.uow.books.get_books(title, author, limit, offset)

        await set_cache(cache_key, jsonable_encoder(books), expire=600)
        return books

    async def get_book_by_id(
        self,
        book_id: int,
    ):
        cache_key = f"books:id:{book_id}"
        cached_book = await get_cache(cache_key)
        if cached_book:
            return cached_book

        book = await self.uow.books.get_book_by_id(book_id)

        await set_cache(cache_key, jsonable_encoder(book))
        return book

    async def create_book(
        self,
        book: BookCreate,
    ):
        async with self.uow:
            new_book = await self.uow.books.create_book(book)

            await self.uow.session.flush()
            await self.uow.session.refresh(new_book)

        await invalidate_prefix("books:list")

        await publish_json(
            channel=self.rmq_channel,
            exchange=Topology.DIRECT_EXCHANGE,
            key=Topology.CREATION_KEY,
            val={
                "event": "book_created",
                "book_id": new_book.id,
                "title": new_book.title,
                "author": new_book.author,
                "description": new_book.description or "",
            },
        )
        return new_book

    async def update_book(
        self,
        book_id: int,
        book: BookUpdate,
    ):
        async with self.uow:
            updated_book = await self.uow.books.update_book(book_id, book)
            await self.uow.session.flush()
            await self.uow.session.refresh(updated_book)

        await delete_cache(f"books:id:{book_id}")
        await invalidate_prefix("books:list")
        return updated_book

    async def delete_book(
        self,
        book_id: int,
    ):
        async with self.uow:
            await self.uow.books.delete_book(book_id)

        await delete_cache(f"books:id:{book_id}")
        await invalidate_prefix("books:list")
