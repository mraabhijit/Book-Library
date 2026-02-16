from datetime import timedelta
from typing import Annotated

from fastapi import Depends

from app.config import settings
from app.repositories.unit_of_work import UnitOfWork
from app.schemas import StaffCreate, Token
from app.utils import (
    create_access_token,
    verify_password,
    verify_access_token,
)
from app.exceptions import InvalidCredentialsError


class AuthService:
    def __init__(self, uow: Annotated[UnitOfWork, Depends(UnitOfWork)]):
        self.uow = uow

    async def register_staff(self, staff_data: StaffCreate):
        async with self.uow:
            new_staff = await self.uow.staff.create_staff(staff_data)
            await self.uow.session.flush()
            await self.uow.session.refresh(new_staff)
            return new_staff

    async def login(self, email: str, password: str) -> Token:
        staff = await self.uow.staff.get_staff_by_email(email)

        if not staff or not verify_password(password, staff.hashed_password):
            raise InvalidCredentialsError(message="Incorrect email or password")

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(staff.id)}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(self, token: str):
        staff_id = verify_access_token(token)
        if staff_id is None:
            raise InvalidCredentialsError(message="Invalid or expired token")

        try:
            staff_id_int = int(staff_id)
        except (TypeError, ValueError):
            raise InvalidCredentialsError(message="Invalid or expired token")

        staff = await self.uow.staff.get_staff_by_id(staff_id_int)
        return staff
