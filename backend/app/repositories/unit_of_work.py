from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import (
    BookRepository,
    MemberRepository,
    BorrowingRepository,
    StaffRepository,
)


class UnitOfWork:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        self.session = session
        # Repositories are now instantiated with the UoW's session
        self.books = BookRepository(session)
        self.members = MemberRepository(session)
        self.borrowings = BorrowingRepository(session)
        self.staff = StaffRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
