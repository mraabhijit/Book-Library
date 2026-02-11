from typing import Annotated

from app import models
from app.database import get_db
from app.routers.auth import CurrentUser
from app.schemas import MemberCreate, MemberResponse, MemberUpdate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("", response_model=list[MemberResponse])
async def get_members(
    current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(models.Member))
    return result.scalars().all()


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member_by_id(
    member_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )

    result = await db.execute(
        select(models.Member).where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    return member


@router.post("", response_model=MemberResponse)
async def create_member(
    member: MemberCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Member).where(
            func.lower(models.Member.email) == member.email.lower()
        )
    )
    existing_member = result.scalars().first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already in use."
        )

    if member.phone:
        result = await db.execute(
            select(models.Member).where(
                func.lower(models.Member.phone) == member.phone.lower()
            )
        )
        existing_member = result.scalars().first()
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone already in use."
            )

    new_member = models.Member(**member.model_dump())
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return new_member


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: int,
    member: MemberUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )

    result = await db.execute(
        select(models.Member).where(models.Member.id == member_id)
    )
    existing_member = result.scalars().first()
    if not existing_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    if member.email:
        result = await db.execute(
            select(models.Member).where(
                func.lower(models.Member.email) == member.email.lower(),
                models.Member.id != member_id,
            )
        )
        email_conflict = result.scalars().first()
        if email_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use."
            )

    if member.phone:
        result = await db.execute(
            select(models.Member).where(
                models.Member.phone == member.phone.lower(),
                models.Member.id != member_id,
            )
        )
        phone_conflict = result.scalars().first()
        if phone_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Phone already in use."
            )

    updated_data = member.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(existing_member, field, value)

    await db.commit()
    await db.refresh(existing_member)
    return existing_member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )

    result = await db.execute(
        select(models.Member).where(models.Member.id == member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    result = await db.execute(
        select(models.Borrowing.member_id).where(
            models.Borrowing.member_id == member.id,
        )
    )
    borrowings = result.scalars().first()
    if borrowings:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete member with borrowing history.",
        )

    await db.delete(member)
    await db.commit()
