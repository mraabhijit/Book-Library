from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.schemas import MemberCreate, MemberUpdate

from app.exceptions import AlreadyExistsError, ActionForbiddenError, NotFoundError


class MemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_members(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[models.Member]:
        result = await self.db.execute(
            select(models.Member).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def get_member_by_id(
        self,
        member_id: int,
    ) -> models.Member:
        result = await self.db.execute(
            select(models.Member).where(models.Member.id == member_id)
        )
        member = result.scalars().first()
        if not member:
            raise NotFoundError(message="Member not found.")
        return member

    async def create_member(
        self,
        member: MemberCreate,
    ) -> models.Member:
        result = await self.db.execute(
            select(models.Member).where(
                func.lower(models.Member.email) == member.email.lower()
            )
        )
        existing_member = result.scalars().first()
        if existing_member:
            raise AlreadyExistsError(message="Email already in use.")

        if member.phone:
            result = await self.db.execute(
                select(models.Member).where(
                    func.lower(models.Member.phone) == member.phone.lower()
                )
            )
            existing_member = result.scalars().first()
            if existing_member:
                raise AlreadyExistsError(message="Phone already in use.")

        new_member = models.Member(**member.model_dump())
        self.db.add(new_member)

        return new_member

    async def update_member(
        self,
        member_id: int,
        member: MemberUpdate,
    ) -> models.Member:
        result = await self.db.execute(
            select(models.Member).where(models.Member.id == member_id)
        )
        existing_member = result.scalars().first()
        if not existing_member:
            raise NotFoundError(message="Member not found.")

        if member.email:
            result = await self.db.execute(
                select(models.Member).where(
                    func.lower(models.Member.email) == member.email.lower(),
                    models.Member.id != member_id,
                )
            )
            email_conflict = result.scalars().first()
            if email_conflict:
                raise AlreadyExistsError(message="Email already in use.")

        if member.phone:
            result = await self.db.execute(
                select(models.Member).where(
                    models.Member.phone == member.phone.lower(),
                    models.Member.id != member_id,
                )
            )
            phone_conflict = result.scalars().first()
            if phone_conflict:
                raise AlreadyExistsError(message="Phone already in use.")

        updated_data = member.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(existing_member, field, value)

        return existing_member

    async def delete_member(
        self,
        member_id: int,
    ):
        if member_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="member_id must be positive",
            )

        result = await self.db.execute(
            select(models.Member).where(models.Member.id == member_id)
        )
        member = result.scalars().first()
        if not member:
            raise NotFoundError(message="Member not found.")

        result = await self.db.execute(
            select(models.Borrowing.member_id).where(
                models.Borrowing.member_id == member.id,
            )
        )
        borrowings = result.scalars().first()
        if borrowings:
            raise ActionForbiddenError(
                message="Cannot delete member with borrowing history.",
            )

        await self.db.delete(member)
