import asyncio
import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from prometheus_client import start_http_server
from protos import (
    auth_pb2,
    auth_pb2_grpc,
    books_pb2,
    books_pb2_grpc,
    borrowings_pb2,
    borrowings_pb2_grpc,
    members_pb2,
    members_pb2_grpc,
)

from app.grpc_handlers import (
    AsyncPromServerInterceptor,
    AuthServicer,
    BookServicer,
    BorrowingServicer,
    MemberServicer,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def serve():
    """
    Main function that creates and runs the gRPC server
    This is similar to how FastAPI creates an app with app = FastAPI()
    """

    # ============================================
    # 1. CREATE THE SERVER
    # ============================================
    server = grpc.aio.server(
        # ThreadPoolExecutor: Manages worker threads for handling requests
        # max_workers=10 means up to 10 requests can be processed simultaneously
        futures.ThreadPoolExecutor(max_workers=100),
        interceptors=[AsyncPromServerInterceptor()],
        # Options: Configuration for the server
        options=[
            # Maximum message size: 10MB (default is 4MB)
            # Useful if you're sending/receiving large data
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
            # Don't reuse port (Windows compatibility)
            ("grpc.so_reuseport", 0),
        ],
    )
    # ============================================
    # 2. REGISTER YOUR SERVICES
    # ============================================
    # This tells the server: "When someone calls BookService methods,
    # use the BookServicer class to handle them"
    #
    # Similar to FastAPI's: app.include_router(books_router)
    auth_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServicer(),
        server,
    )
    books_pb2_grpc.add_BookServiceServicer_to_server(
        BookServicer(),  # Your handler class (the implementation)
        server,  # The server to add it to
    )
    members_pb2_grpc.add_MemberServiceServicer_to_server(
        MemberServicer(),
        server,
    )
    borrowings_pb2_grpc.add_BorrowingServiceServicer_to_server(
        BorrowingServicer(),
        server,
    )
    # ============================================
    # 3. ENABLE REFLECTION (Optional but useful)
    # ============================================
    # Reflection allows tools like grpcurl to discover what services
    # your server offers without needing the .proto files
    #
    # Think of it like FastAPI's automatic /docs endpoint
    SERVICE_NAMES = (
        # The full name of your BookService from the .proto file
        auth_pb2.DESCRIPTOR.services_by_name["AuthService"].full_name,
        books_pb2.DESCRIPTOR.services_by_name["BookService"].full_name,
        members_pb2.DESCRIPTOR.services_by_name["MemberService"].full_name,
        borrowings_pb2.DESCRIPTOR.services_by_name["BorrowingService"].full_name,
        # The reflection service itself (meta-service)
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    # ============================================
    # 4. BIND TO A PORT
    # ============================================
    # Tell the server which address and port to listen on
    # "0.0.0.0:50052" means:
    #   - 0.0.0.0 = listen on ALL network interfaces (localhost + external)
    #   - 50052 = the port number
    #
    # Similar to: uvicorn.run(app, host="0.0.0.0", port=8000)
    listen_addr = "0.0.0.0:50052"
    server.add_insecure_port(listen_addr)
    # Note: "insecure" means no TLS/SSL encryption
    # For production, you'd use add_secure_port() with certificates

    # ============================================
    # 5. START HTTP SERVER FOR PROMETHEUS
    # ============================================
    start_http_server(9000)
    logger.info("   Prometheus metric available on port 9000")

    # ============================================
    # 6. START THE SERVER
    # ============================================
    # Actually start listening for connections
    await server.start()
    logger.info("   gRPC Server is running!")
    logger.info("   - Books Service: available")
    logger.info("   - Reflection: enabled")

    async def shutdown():
        logger.info("   Shutting down gRPC server...")
        await server.stop(grace=5)  # 5 second grace period
        logger.info("   Server stopped!")

    # ============================================
    # 7. KEEP THE SERVER RUNNING
    # ============================================
    # This blocks forever, keeping the server alive
    # until you press Ctrl+C or the process is killed
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        await shutdown()
    except Exception as e:
        logger.error(f"   Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # asyncio.run() creates an event loop and runs the serve() function
    asyncio.run(serve())
