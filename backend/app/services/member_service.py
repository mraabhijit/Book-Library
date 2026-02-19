from typing import Annotated

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from app.redis_client import delete_cache, get_cache, invalidate_prefix, set_cache
from app.repositories.unit_of_work import UnitOfWork
from app.schemas import MemberCreate, MemberUpdate


class MemberService:
    def __init__(self, uow: Annotated[UnitOfWork, Depends(UnitOfWork)]):
        self.uow = uow

    async def get_members(
        self,
        limit: int = 10,
        offset: int = 0,
    ):
        cache_key = f"members:list:limit:{limit}:offset:{offset}"
        cached_members = await get_cache(cache_key)
        if cached_members:
            return cached_members

        members = await self.uow.members.get_members(limit, offset)

        await set_cache(cache_key, jsonable_encoder(members))
        return members

    async def get_member_by_id(
        self,
        member_id: int,
    ):
        cache_key = f"members:id:{member_id}"
        cached_member = await get_cache(cache_key)
        if cached_member:
            return cached_member

        member = await self.uow.members.get_member_by_id(member_id)

        await set_cache(cache_key, jsonable_encoder(member))
        return member

    async def create_member(
        self,
        member: MemberCreate,
    ):
        async with self.uow:
            new_member = await self.uow.members.create_member(member)
            await self.uow.session.flush()
            await self.uow.session.refresh(new_member)

        await invalidate_prefix("members:list")
        return new_member

    async def update_member(
        self,
        member_id: int,
        member: MemberUpdate,
    ):
        async with self.uow:
            updated_member = await self.uow.members.update_member(member_id, member)
            await self.uow.session.flush()
            await self.uow.session.refresh(updated_member)

        await delete_cache(f"members:id:{member_id}")
        await invalidate_prefix("members:list")
        return updated_member

    async def delete_member(
        self,
        member_id: int,
    ):
        async with self.uow:
            await self.uow.members.delete_member(member_id)

        await delete_cache(f"members:id:{member_id}")
        await invalidate_prefix("members:list")
