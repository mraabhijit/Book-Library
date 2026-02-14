from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.database import get_db
from app.schemas import (
    BorrowRequest,
    BorrowResponse,
    ReturnRequest,
    ReturnResponse,
)
from app.routers.auth import CurrentUser

router = APIRouter()


@router.get("", response_model=list[BorrowResponse])
async def get_current_borrowing_records(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10,
    offset: int = 0,
):
    records = await db.execute(
        select(models.Borrowing)
        .options(selectinload(models.Borrowing.book))
        .options(selectinload(models.Borrowing.member))
        .where(models.Borrowing.returned_date.is_(None))
        .order_by(models.Borrowing.borrowed_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return records.scalars().all()


@router.get("/members/{member_id}", response_model=list[BorrowResponse])
async def get_borrowing_records_by_member_id(
    member_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10,
    offset: int = 0,
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive.",
        )

    records = await db.execute(
        select(models.Member).where(models.Member.id == member_id)
    )
    member = records.scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )

    records = await db.execute(
        select(models.Borrowing)
        .options(selectinload(models.Borrowing.book))
        .options(selectinload(models.Borrowing.member))
        .where(models.Borrowing.member_id == member_id)
        .order_by(models.Borrowing.borrowed_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return records.scalars().all()


@router.get("/history", response_model=list[BorrowResponse])
async def get_borrowing_records(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10,
    offset: int = 0,
):
    records = await db.execute(
        select(models.Borrowing)
        .options(selectinload(models.Borrowing.book))
        .options(selectinload(models.Borrowing.member))
        .order_by(models.Borrowing.borrowed_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return records.scalars().all()


@router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(
    borrow_request: BorrowRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Book).where(models.Book.id == borrow_request.book_id)
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found.",
        )

    if not book.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book not available.",
        )

    result = await db.execute(
        select(models.Member).where(models.Member.id == borrow_request.member_id)
    )
    member = result.scalars().first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found."
        )
    record = await create_borrowing_record(borrow_request, db)

    book.is_available = False
    await db.commit()
    await db.refresh(record, attribute_names=["book", "member"])
    return record


async def create_borrowing_record(
    borrow_request: BorrowRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> models.Borrowing:
    new_borrow_record = models.Borrowing(
        book_id=borrow_request.book_id,
        member_id=borrow_request.member_id,
        borrowed_date=datetime.now(UTC),
    )

    db.add(new_borrow_record)
    return new_borrow_record


@router.put("/return", response_model=ReturnResponse)
async def return_book(
    return_request: ReturnRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    record = await get_borrowing_record(return_request, db)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No borrowing record found for provided book_id and member_id.",
        )

    record.returned_date = datetime.now(UTC)
    record.book.is_available = True
    # Keep original due date to check if it was returned late

    await db.commit()
    await db.refresh(record, attribute_names=["book", "member"])
    return record


async def get_borrowing_record(
    return_request: ReturnRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> models.Borrowing | None:
    result = await db.execute(
        select(models.Borrowing)
        .options(selectinload(models.Borrowing.book))
        .options(selectinload(models.Borrowing.member))
        .where(
            models.Borrowing.book_id == return_request.book_id,
            models.Borrowing.member_id == return_request.member_id,
            models.Borrowing.returned_date.is_(None),
        )
    )
    return result.scalars().first()
