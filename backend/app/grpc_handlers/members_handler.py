import grpc
from protos import common_pb2, members_pb2, members_pb2_grpc
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app import models
from app.database import AsyncSessionLocal
from app.grpc_handlers.helpers import datetime_to_timestamp, get_current_user


def member_to_proto(member: models.Member) -> members_pb2.Member:
    return members_pb2.Member(
        id=member.id,
        name=member.name or "",
        email=member.email,
        phone=member.phone or "",
        created_at=datetime_to_timestamp(member.created_at),
        updated_at=datetime_to_timestamp(member.updated_at),
    )


class MemberServicer(members_pb2_grpc.MemberServiceServicer):
    async def GetMembers(
        self,
        request: members_pb2.GetMembersRequest,
        context: grpc.aio.ServicerContext,
    ) -> members_pb2.GetMembersResponse:
        await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(models.Member))
            members = result.scalars().all()
            return members_pb2.GetMembersResponse(
                members=[member_to_proto(member) for member in members]
            )

    async def GetMember(
        self,
        request: members_pb2.GetMemberRequest,
        context: grpc.aio.ServicerContext,
    ) -> members_pb2.Member:
        await get_current_user(context)
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "member_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Member).where(models.Member.id == request.id)
            )
            member = result.scalars().first()
            if not member:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Member not found")
            return member_to_proto(member)

    async def CreateMember(
        self,
        request: members_pb2.CreateMemberRequest,
        context: grpc.aio.ServicerContext,
    ) -> members_pb2.Member:
        await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Member).where(
                    func.lower(models.Member.email) == request.email.lower()
                )
            )
            existing_member = result.scalars().first()
            if existing_member:
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS, "Email or Phone already in use."
                )

            if request.HasField("phone"):
                result = await db.execute(
                    select(models.Member).where(models.Member.phone == request.phone)
                )

                phone_in_use = result.scalars().first()
                if phone_in_use:
                    await context.abort(
                        grpc.StatusCode.ALREADY_EXISTS, "Email or Phone already in use."
                    )

            new_member = models.Member(
                name=request.name if request.HasField("name") else None,
                email=request.email.lower(),
                phone=request.phone if request.HasField("phone") else None,
            )

            db.add(new_member)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS, "Email or Phone already in use."
                )

            await db.refresh(new_member)
            return member_to_proto(new_member)

    async def UpdateMember(
        self,
        request: members_pb2.UpdateMemberRequest,
        context: grpc.aio.ServicerContext,
    ) -> members_pb2.Member:
        await get_current_user(context)
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "member_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Member)
                .where(models.Member.id == request.id)
                .with_for_update()
            )
            existing_member = result.scalars().first()
            if not existing_member:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Member not found")

            if request.HasField("phone"):
                result = await db.execute(
                    select(models.Member)
                    .where(
                        models.Member.phone == request.phone,
                        models.Member.id != request.id,
                    )
                    .with_for_update()
                )
                phone_in_use = result.scalars().first()
                if phone_in_use:
                    await context.abort(
                        grpc.StatusCode.ALREADY_EXISTS, "Phone already in use."
                    )
                existing_member.phone = request.phone

            if request.HasField("name"):
                existing_member.name = request.name

            await db.commit()
            await db.refresh(existing_member)
            return member_to_proto(existing_member)

    async def DeleteMember(
        self,
        request: members_pb2.DeleteMemberRequest,
        context: grpc.aio.ServicerContext,
    ) -> common_pb2.Empty:
        await get_current_user(context)
        if request.id <= 0:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "member_id must be positive"
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Member)
                .where(models.Member.id == request.id)
                .with_for_update()
            )
            member = result.scalars().first()
            if not member:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Member not found")

            result = await db.execute(
                select(models.Borrowing.member_id)
                .where(models.Borrowing.member_id == request.id)
                .with_for_update()
            )
            has_history = result.scalars().first()

            if has_history:
                await context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION,
                    "Cannot delete member with borrowing history",
                )

            await db.delete(member)
            await db.commit()

            return common_pb2.Empty()
