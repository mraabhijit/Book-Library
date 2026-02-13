import time
from datetime import datetime

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from prometheus_client import Counter, Histogram

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


# Define metrics
GRPC_SERVER_HANDLED_TOTAL = Counter(
    "grpc_server_handled_total",
    "Total number of RPCs completed",
    ["grpc_service", "grpc_method", "grpc_code"],
)
GRPC_SERVER_HANDLING_SECONDS = Histogram(
    "grpc_server_handling_seconds",
    "Response latency in seconds",
    ["grpc_service", "grpc_method"],
)


class AsyncPromServerInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        # Extract service and method from /package.Service/Method
        parts = handler_call_details.method.split("/")
        service = parts[1] if len(parts) > 1 else "unknown"
        method = parts[2] if len(parts) > 2 else "unknown"

        start_time = time.time()

        try:
            response = await continuation(handler_call_details)
            code = "OK"
            return response
        except grpc.RpcError as e:
            code = e.code().name
            raise e
        except Exception:
            code = "INTERNAL"
            raise
        finally:
            latency = time.time() - start_time
            GRPC_SERVER_HANDLING_SECONDS.labels(
                grpc_service=service, grpc_method=method
            ).observe(latency)
            GRPC_SERVER_HANDLED_TOTAL.labels(
                grpc_service=service, grpc_method=method, grpc_code=code
            ).inc()
