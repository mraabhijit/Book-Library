from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.routers.auth import CurrentUser
from app.schemas import (
    BorrowRequest,
    BorrowResponse,
    ReturnRequest,
    ReturnResponse,
)
from app.services import BorrowingService


router = APIRouter()


@router.get("", response_model=list[BorrowResponse])
async def get_current_borrowing_records(
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_current_borrowing_records(limit, offset)


@router.get("/members/{member_id}", response_model=list[BorrowResponse])
async def get_borrowing_records_by_member_id(
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
    member_id: int,
    limit: int = 10,
    offset: int = 0,
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive.",
        )

    return await service.get_borrowing_records_by_member_id(member_id, limit, offset)


@router.get("/history", response_model=list[BorrowResponse])
async def get_borrowing_records(
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_all_borrowings_history(limit, offset)


@router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(
    borrow_request: BorrowRequest,
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
):
    return await service.borrow_book(borrow_request.book_id, borrow_request.member_id)


@router.put("/return", response_model=ReturnResponse)
async def return_book(
    return_request: ReturnRequest,
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
):
    return await service.return_book(return_request.book_id, return_request.member_id)


@router.get("/books/{book_id}", response_model=list[BorrowResponse])
async def get_borrowing_records_by_book_id(
    current_user: CurrentUser,
    service: Annotated[BorrowingService, Depends(BorrowingService)],
    book_id: int,
    limit: int = 10,
    offset: int = 0,
):
    if book_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="book_id must be positive.",
        )

    return await service.get_borrowing_records_by_book_id(book_id, limit, offset)
