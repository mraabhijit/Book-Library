"""
Simple gRPC client to test the Books service
"""

import asyncio

import grpc
from protos import books_pb2, books_pb2_grpc, members_pb2, members_pb2_grpc


async def test_get_books():
    """Test GetBooks RPC"""
    # Create channel (connection to server)
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        # Create stub (client)
        stub = books_pb2_grpc.BookServiceStub(channel)

        # Make request
        request = books_pb2.GetBooksRequest()

        try:
            response = await stub.GetBooks(request)
            print("   GetBooks successful!")
            print(f"   Found {len(response.books)} books")

            for book in response.books:
                print(f"\n   {book.title}")
                print(f"   Author: {book.author}")
                print(f"   ISBN: {book.isbn}")
                print(f"   Available: {book.is_available}")

        except grpc.RpcError as e:
            print(f"   Error: {e.code()} - {e.details()}")


async def test_create_book():
    """Test CreateBook RPC"""
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        stub = books_pb2_grpc.BookServiceStub(channel)

        # Create request
        request = books_pb2.CreateBookRequest(
            title="gRPC Test Book",
            author="Test Author",
            isbn="9781234567890",
            description="A book created via gRPC",
        )

        try:
            response = await stub.CreateBook(request)
            print("\n   CreateBook successful!")
            print(f"   Created book ID: {response.id}")
            print(f"   Title: {response.title}")

        except grpc.RpcError as e:
            print(f"   Error: {e.code()} - {e.details()}")


async def test_get_members():
    """Test Getmembers RPC"""
    # Create channel (connection to server)
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        # Create stub (client)
        stub = members_pb2_grpc.MemberServiceStub(channel)

        # Make request
        request = members_pb2.GetMembersRequest()

        try:
            response = await stub.GetMembers(request)
            print("   GetMembers successful!")
            print(f"   Found {len(response.members)} members")

            for member in response.members:
                print(f"\n   {member.name}")
                print(f"   Email: {member.email}")
                print(f"   Phone: {member.phone}")

        except grpc.RpcError as e:
            print(f"   Error: {e.code()} - {e.details()}")


async def test_create_member():
    """Test CreateMember RPC"""
    async with grpc.aio.insecure_channel("localhost:50052") as channel:
        stub = members_pb2_grpc.MemberServiceStub(channel)

        # Create request
        request = members_pb2.CreateMemberRequest(
            name="gRPC Test User",
            email="testuser@grpc.com",
            phone="1234567895",
        )

        try:
            response = await stub.CreateMember(request)
            print("\n   CreateMember successful!")
            print(f"   Created member ID: {response.id}")
            print(f"   Name: {response.name}")

        except grpc.RpcError as e:
            print(f"   Error: {e.code()} - {e.details()}")


async def main():
    """Run all tests"""
    print("   Testing gRPC Service\n")
    print("=" * 50)

    await test_get_books()
    print("\n" + "=" * 50)

    # await test_create_book()
    # print("\n" + "=" * 50)

    await test_get_members()
    print("\n" + "=" * 50)

    # await test_create_member()
    # print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
