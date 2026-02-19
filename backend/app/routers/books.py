from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.routers.auth import CurrentUser
from app.schemas import BookCreate, BookResponse, BookUpdate
from app.services import BookService

router = APIRouter()


@router.get("", response_model=list[BookResponse])
async def get_books(
    service: Annotated[BookService, Depends(BookService)],
    title: str | None = None,
    author: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    books = await service.get_books(title, author, limit, offset)
    return books


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_by_id(
    book_id: int,
    current_user: CurrentUser,
    service: Annotated[BookService, Depends(BookService)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )
    return await service.get_book_by_id(book_id)


@router.post("", response_model=BookResponse)
async def create_book(
    book: BookCreate,
    current_user: CurrentUser,
    service: Annotated[BookService, Depends(BookService)],
):
    return await service.create_book(book)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book: BookUpdate,
    current_user: CurrentUser,
    service: Annotated[BookService, Depends(BookService)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )

    return await service.update_book(book_id, book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    current_user: CurrentUser,
    service: Annotated[BookService, Depends(BookService)],
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive",
        )
    await service.delete_book(book_id)
