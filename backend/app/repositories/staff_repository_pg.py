from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.schemas import StaffCreate
from app.exceptions import AlreadyExistsError, NotFoundError
from app.utils import hash_password


class StaffRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_staff_by_username(self, username: str) -> models.Staff | None:
        result = await self.db.execute(
            select(models.Staff).where(
                func.lower(models.Staff.username) == username.lower()
            )
        )
        return result.scalars().first()

    async def get_staff_by_email(self, email: str) -> models.Staff | None:
        result = await self.db.execute(
            select(models.Staff).where(func.lower(models.Staff.email) == email.lower())
        )
        return result.scalars().first()

    async def get_staff_by_id(self, staff_id: int) -> models.Staff:
        result = await self.db.execute(
            select(models.Staff).where(models.Staff.id == staff_id)
        )
        staff = result.scalars().first()
        if not staff:
            raise NotFoundError(message="Staff member not found.")
        return staff

    async def create_staff(self, staff: StaffCreate) -> models.Staff:
        # Check username and email uniqueness first
        if await self.get_staff_by_username(staff.username):
            raise AlreadyExistsError(message="Username already exists")

        if await self.get_staff_by_email(staff.email):
            raise AlreadyExistsError(message="Email already registered")

        new_staff = models.Staff(
            email=staff.email.lower(),
            username=staff.username,
            hashed_password=hash_password(staff.password),
            full_name=staff.full_name,
        )
        self.db.add(new_staff)
        return new_staff
