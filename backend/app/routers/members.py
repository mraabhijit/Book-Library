from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.routers.auth import CurrentUser
from app.schemas import MemberCreate, MemberResponse, MemberUpdate
from app.services import MemberService

router = APIRouter()


@router.get("", response_model=list[MemberResponse])
async def get_members(
    current_user: CurrentUser,
    service: Annotated[MemberService, Depends(MemberService)],
    limit: int = 10,
    offset: int = 0,
):
    return await service.get_members(limit, offset)


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member_by_id(
    member_id: int,
    current_user: CurrentUser,
    service: Annotated[MemberService, Depends(MemberService)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )
    return await service.get_member_by_id(member_id)


@router.post("", response_model=MemberResponse)
async def create_member(
    member: MemberCreate,
    current_user: CurrentUser,
    service: Annotated[MemberService, Depends(MemberService)],
):
    return await service.create_member(member)


@router.put("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: int,
    member: MemberUpdate,
    current_user: CurrentUser,
    service: Annotated[MemberService, Depends(MemberService)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )

    return await service.update_member(member_id, member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: int,
    current_user: CurrentUser,
    service: Annotated[MemberService, Depends(MemberService)],
):
    if member_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="member_id must be positive",
        )

    await service.delete_member(member_id)
