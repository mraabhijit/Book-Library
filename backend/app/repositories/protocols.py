from typing import Protocol

from app import models
from app.schemas import (
    BookCreate,
    BookUpdate,
    MemberCreate,
    MemberUpdate,
)


class BookRepositoryProtocol(Protocol):
    async def get_books(
        self,
        title: str | None,
        author: str | None,
        limit: int,
        offset: int,
    ) -> list[models.Book]: ...

    async def get_book_by_id(self, book_id: int) -> models.Book: ...

    async def create_book(self, book: BookCreate) -> models.Book: ...

    async def update_book(
        self,
        book_id: int,
        book: BookUpdate,
    ) -> models.Book: ...

    async def delete_book(self, book_id): ...


class MemberRepositoryProtocol(Protocol):
    async def get_members(self, limit: int, offset: int) -> list[models.Member]: ...

    async def get_member_by_id(self, member_id: int) -> models.Member: ...

    async def create_member(self, member: MemberCreate) -> models.Member: ...

    async def update_member(
        self, member_id: int, member: MemberUpdate
    ) -> models.Member: ...

    async def delete_member(self, member_id: int): ...


class BorrowingRepositoryProtocol(Protocol):
    async def get_active_borrowings(
        self, limit: int, offset: int
    ) -> list[models.Borrowing]: ...

    async def get_borrowings_by_member_id(
        self, member_id: int, limit: int, offset: int
    ) -> list[models.Borrowing]: ...

    async def get_borrowings_by_book_id(
        self, book_id: int, limit: int, offset: int
    ) -> list[models.Borrowing]: ...

    async def get_all_borrowings_history(
        self, limit: int, offset: int
    ) -> list[models.Borrowing]: ...

    async def create_record(self, book_id: int, member_id: int) -> models.Borrowing: ...

    async def get_active_record(
        self, book_id: int, member_id: int
    ) -> models.Borrowing | None: ...
