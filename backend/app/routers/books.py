from typing import Annotated

from app import models
from app.database import get_db
from app.routers.auth import CurrentUser
from app.schemas import BookCreate, BookResponse, BookUpdate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("", response_model=list[BookResponse])
async def get_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    title: str | None = None,
    author: str | None = None,
):
    query = select(models.Book)
    if title:
        query = query.where(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(models.Book.author.ilike(f"%{author}%"))
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_by_id(
    book_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )

    result = await db.execute(
        select(models.Book).where(models.Book.id == book_id),
    )

    book = result.scalars().first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@router.post("", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Book).where(models.Book.isbn == book.isbn))
    existing_book = result.scalars().first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book with this ISBN already exists",
        )

    new_book = models.Book(**book.model_dump())

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )

    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    existing_book = result.scalars().first()
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    updated_data = book.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(existing_book, field, value)
    # updated_at gets auto updated due to onupdate

    await db.commit()
    await db.refresh(existing_book)
    return existing_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )

    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    existing_book = result.scalars().first()
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if not existing_book.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book that is currently borrowed or marked as unavailable.",
        )

    await db.delete(existing_book)
    await db.commit()
