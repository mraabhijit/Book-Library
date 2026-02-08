from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import settings
from app.database import get_db
from app.schemas import StaffCreate, StaffResponse, Token
from app.utils import (
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)

router = APIRouter()


@router.post("/register", response_model=StaffResponse)
async def create_staff(
    staff: StaffCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Staff).where(
            func.lower(models.Staff.username) == staff.username.lower()
        )
    )
    existing_staff = result.scalars().first()
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = await db.execute(
        select(models.Staff).where(
            func.lower(models.Staff.email) == staff.email.lower()
        ),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_staff = models.Staff(
        email=staff.email.lower(),
        username=staff.username,
        hashed_password=hash_password(staff.password),
        full_name=staff.full_name,
    )
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff


@router.get("/me", response_model=StaffResponse)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    staff_id = verify_access_token(token)
    if staff_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        staff_id_int = int(staff_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(models.Staff).where(models.Staff.id == staff_id_int)
    )
    staff = result.scalars().first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return staff


@router.post("/login", response_model=Token)
async def login_for_acces_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Staff).where(
            func.lower(models.Staff.email) == form_data.username.lower()
        )
    )
    staff = result.scalars().first()

    if not staff or not verify_password(form_data.password, staff.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(staff.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


CurrentUser = Annotated[models.Staff, Depends(get_current_user)]
