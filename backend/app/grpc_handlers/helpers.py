from datetime import datetime

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from app.utils import verify_access_token


def datetime_to_timestamp(dt: datetime) -> Timestamp:
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts

async def get_current_user(context: grpc.aio.ServicerContext) -> int:
    metadata_raw = context.invocation_metadata()
    metadata = {k: v for k, v in metadata_raw} if metadata_raw else {}
    auth_header = metadata.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        await context.abort(
            grpc.StatusCode.UNAUTHENTICATED,
            "Missing or invalid token",
        )

    token = auth_header.split(" ")[1]
    staff_id = verify_access_token(token)

    if not staff_id:
        await context.abort(
            grpc.StatusCode.UNAUTHENTICATED,
            "Missing or invalid token",
        )
    return int(staff_id)