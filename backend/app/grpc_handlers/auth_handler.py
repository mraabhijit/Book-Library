from datetime import timedelta

import grpc
from protos import auth_pb2, auth_pb2_grpc
from sqlalchemy import func, select

from app import models
from app.config import settings
from app.database import AsyncSessionLocal
from app.grpc_handlers.helpers import get_current_user
from app.utils import (
    create_access_token,
    hash_password,
    verify_password,
)


def staff_to_proto(staff: models.Staff) -> auth_pb2.Staff:
    return auth_pb2.Staff(
        id=staff.id,
        username=staff.username,
        email=staff.email,
        full_name=staff.full_name,
    )


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    async def Register(
        self, request: auth_pb2.RegisterRequest, context: grpc.aio.ServicerContext
    ) -> auth_pb2.Staff:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Staff).where(
                    func.lower(models.Staff.username) == request.username.lower()
                )
            )
            existing_staff = result.scalars().first()
            if existing_staff:
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "Username taken",
                )
            result = await db.execute(
                select(models.Staff).where(
                    func.lower(models.Staff.email) == request.email.lower()
                )
            )
            existing_email = result.scalars().first()
            if existing_email:
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "Email already registered",
                )

            new_staff = models.Staff(
                email=request.email.lower(),
                username=request.username,
                hashed_password=hash_password(request.password),
                full_name=request.full_name if request.HasField("full_name") else "",
            )

            db.add(new_staff)
            await db.commit()
            await db.refresh(new_staff)
            return staff_to_proto(new_staff)

    async def GetCurrentUser(
        self,
        request: auth_pb2.GetCurrentUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> auth_pb2.Staff:
        staff_id = await get_current_user(context)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Staff).where(models.Staff.id == int(staff_id))
            )
            staff = result.scalars().first()

            if not staff:
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Missing or invalid token"
                )

        return staff_to_proto(staff)

    async def Login(
        self, request: auth_pb2.LoginRequest, context: grpc.aio.ServicerContext
    ) -> auth_pb2.LoginResponse:
        """Login and return a JWT access token"""
        async with AsyncSessionLocal() as db:
            # Find staff by email
            result = await db.execute(
                select(models.Staff).where(
                    func.lower(models.Staff.email) == request.email.lower()
                )
            )
            staff = result.scalars().first()
            if not staff or not verify_password(
                request.password, staff.hashed_password
            ):
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Incorrect email or password"
                )
            # Generate token
            access_token_expires = timedelta(
                minutes=settings.access_token_expire_minutes
            )
            access_token = create_access_token(
                data={"sub": str(staff.id)}, expires_delta=access_token_expires
            )

            return auth_pb2.LoginResponse(
                access_token=access_token, token_type="bearer"
            )
