from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.exceptions import NotFoundError


class BorrowingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_borrowings(
        self, limit: int, offset: int
    ) -> list[models.Borrowing]:
        records = await self.db.execute(
            select(models.Borrowing)
            .options(selectinload(models.Borrowing.book))
            .options(selectinload(models.Borrowing.member))
            .where(models.Borrowing.returned_date.is_(None))
            .order_by(models.Borrowing.borrowed_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return records.scalars().all()

    async def get_borrowings_by_member_id(
        self, member_id: int, limit: int, offset: int
    ) -> list[models.Borrowing]:
        records = await self.db.execute(
            select(models.Member).where(models.Member.id == member_id)
        )
        member = records.scalars().first()
        if not member:
            raise NotFoundError(message="Member not found.")

        records = await self.db.execute(
            select(models.Borrowing)
            .options(selectinload(models.Borrowing.book))
            .options(selectinload(models.Borrowing.member))
            .where(models.Borrowing.member_id == member_id)
            .order_by(models.Borrowing.borrowed_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return records.scalars().all()

    async def get_borrowings_by_book_id(
        self, book_id: int, limit: int, offset: int
    ) -> list[models.Borrowing]:
        records = await self.db.execute(
            select(models.Book).where(models.Book.id == book_id)
        )
        book = records.scalars().first()
        if not book:
            raise NotFoundError(message="Book not found.")

        records = await self.db.execute(
            select(models.Borrowing)
            .options(selectinload(models.Borrowing.book))
            .options(selectinload(models.Borrowing.member))
            .where(models.Borrowing.book_id == book_id)
            .order_by(models.Borrowing.borrowed_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return records.scalars().all()

    async def get_all_borrowings_history(
        self, limit: int, offset: int
    ) -> list[models.Borrowing]:
        records = await self.db.execute(
            select(models.Borrowing)
            .options(selectinload(models.Borrowing.book))
            .options(selectinload(models.Borrowing.member))
            .order_by(models.Borrowing.borrowed_date.desc())
            .limit(limit)
            .offset(offset)
        )
        return records.scalars().all()

    async def create_record(self, book_id: int, member_id: int) -> models.Borrowing:
        new_record = models.Borrowing(
            book_id=book_id,
            member_id=member_id,
            borrowed_date=datetime.now(UTC),
        )
        self.db.add(new_record)
        return new_record

    async def get_active_record(
        self, book_id: int, member_id: int
    ) -> models.Borrowing | None:
        result = await self.db.execute(
            select(models.Borrowing)
            .options(selectinload(models.Borrowing.book))
            .options(selectinload(models.Borrowing.member))
            .where(
                models.Borrowing.book_id == book_id,
                models.Borrowing.member_id == member_id,
                models.Borrowing.returned_date.is_(None),
            )
        )
        return result.scalars().first()
