from typing import Annotated

from app import models
from app.database import get_db
from app.redis_client import delete_cache, get_cache, invalidate_prefix, set_cache
from app.routers.auth import CurrentUser
from app.schemas import BookCreate, BookResponse, BookUpdate
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("", response_model=list[BookResponse])
async def get_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    title: str | None = None,
    author: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    cache_key = (
        f"books:list:title:{title}:author:{author}:limit:{limit}:offset:{offset}"
    )
    cached_books = await get_cache(cache_key)
    if cached_books:
        return cached_books

    query = select(models.Book)
    if title:
        query = query.where(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.where(models.Book.author.ilike(f"%{author}%"))

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    books = result.scalars().all()

    await set_cache(cache_key, jsonable_encoder(books), expire=600)
    return books


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

    cache_key = f"books:id:{book_id}"
    cached_book = await get_cache(cache_key)
    if cached_book:
        return cached_book

    result = await db.execute(
        select(models.Book).where(models.Book.id == book_id),
    )

    book = result.scalars().first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    await set_cache(cache_key, jsonable_encoder(book))
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

    await invalidate_prefix("books:list")
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

    result = await db.execute(
        select(models.Borrowing).where(
            models.Borrowing.book_id == book_id,
            models.Borrowing.returned_date.is_(None),
        )
    )
    is_borrowed = result.scalars().first()
    if is_borrowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a borrowed book",
        )

    updated_data = book.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(existing_book, field, value)
    # updated_at gets auto updated due to onupdate

    await db.commit()
    await db.refresh(existing_book)

    await delete_cache(f"books:id:{book_id}")
    await invalidate_prefix("books:list")
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

    result = await db.execute(
        select(models.Borrowing).where(models.Borrowing.book_id == existing_book.id)
    )
    has_borrowing_history = result.scalars().first()
    if has_borrowing_history:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book with borrowing history.",
        )

    await db.delete(existing_book)
    await db.commit()

    await delete_cache(f"books:id:{book_id}")
    await invalidate_prefix("books:list")
