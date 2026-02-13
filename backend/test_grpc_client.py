"""
gRPC Client for testing Library App Services with Authentication
"""

import asyncio
from datetime import datetime, UTC, timedelta
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from protos import books_pb2, books_pb2_grpc
from protos import members_pb2, members_pb2_grpc
from protos import borrowings_pb2, borrowings_pb2_grpc
from protos import auth_pb2, auth_pb2_grpc


SERVER_ADDR = "localhost:50052"


def datetime_to_timestamp(dt):
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


async def test_auth_service(channel):
    print("--- Testing AuthService ---")
    stub = auth_pb2_grpc.AuthServiceStub(channel)

    # 1. Register
    print("Test Register:")
    try:
        reg_req = auth_pb2.RegisterRequest(
            username="testadmin",
            email="admin@library.com",
            password="securepassword123",
            full_name="Library Administrator",
        )
        staff = await stub.Register(reg_req)
        print(f"Registered Staff: {staff.username} (ID: {staff.id})")
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            print("Staff already exists, proceeding to login")
        else:
            raise e

    # 2. Login
    print("\nTest Login:")
    login_req = auth_pb2.LoginRequest(
        email="admin@library.com", password="securepassword123"
    )
    login_res = await stub.Login(login_req)
    token = login_res.access_token
    print(f"Login successful, received token (type: {login_res.token_type})")

    # 3. Get Current User (Protected)
    print("\nTest GetCurrentUser:")
    metadata = [("authorization", f"Bearer {token}")]
    me_req = auth_pb2.GetCurrentUserRequest()
    me = await stub.GetCurrentUser(me_req, metadata=metadata)
    print(f"Authenticated as: {me.username}")

    return token


async def test_book_service(channel, token):
    print("\n--- Testing BookService ---")
    stub = books_pb2_grpc.BookServiceStub(channel)
    metadata = [("authorization", f"Bearer {token}")]

    # 1. List Books (Unprotected)
    print("Test GetBooks (Unprotected):")
    list_req = books_pb2.GetBooksRequest()
    response = await stub.GetBooks(list_req)
    print(f"Found {len(response.books)} books")

    # 2. Create Book (Protected)
    print("\nTest CreateBook (Protected):")
    create_req = books_pb2.CreateBookRequest(
        title="gRPC Auth Masterclass",
        author="Security Expert",
        isbn="AUTH-TEST-101",
        description="A guide to gRPC authentication",
    )
    book = await stub.CreateBook(create_req, metadata=metadata)
    print(f"Created Book: {book.title} (ID: {book.id})")

    # 3. Get Book by ID (Protected)
    print("\nTest GetBook (Protected):")
    get_req = books_pb2.GetBookRequest(id=book.id)
    fetched_book = await stub.GetBook(get_req, metadata=metadata)
    print(f"Fetched Book: {fetched_book.title}")

    # 4. Update Book (Protected)
    print("\nTest UpdateBook (Protected):")
    update_req = books_pb2.UpdateBookRequest(
        id=book.id,
        title="gRPC Auth Masterclass (Updated Edition)",
        description="Updated with more security tips",
    )
    updated_book = await stub.UpdateBook(update_req, metadata=metadata)
    print(f"Updated Title: {updated_book.title}")

    return book.id


async def test_member_service(channel, token):
    print("\n--- Testing MemberService ---")
    stub = members_pb2_grpc.MemberServiceStub(channel)
    metadata = [("authorization", f"Bearer {token}")]

    # 1. Create Member (Protected)
    print("Test CreateMember (Protected):")
    create_req = members_pb2.CreateMemberRequest(
        name="Secure User", email="secure.user@example.com", phone="5550009999"
    )
    member = await stub.CreateMember(create_req, metadata=metadata)
    print(f"Created Member: {member.name} (ID: {member.id})")

    # 2. Get Member by ID (Protected)
    print("\nTest GetMember (Protected):")
    get_req = members_pb2.GetMemberRequest(id=member.id)
    fetched_member = await stub.GetMember(get_req, metadata=metadata)
    print(f"Fetched Member: {fetched_member.name}")

    # 3. Update Member (Protected)
    print("\nTest UpdateMember (Protected):")
    update_req = members_pb2.UpdateMemberRequest(
        id=member.id, name="Secure User Modified", phone="5550001111"
    )
    updated_member = await stub.UpdateMember(update_req, metadata=metadata)
    print(f"Updated Name: {updated_member.name}")

    # 4. List Members (Protected)
    print("\nTest GetMembers (Protected):")
    response = await stub.GetMembers(members_pb2.GetMembersRequest(), metadata=metadata)
    print(f"Total members found: {len(response.members)}")

    return member.id


async def test_borrowing_service(channel, token, book_id, member_id):
    print("\n--- Testing BorrowingService ---")
    stub = borrowings_pb2_grpc.BorrowingServiceStub(channel)
    metadata = [("authorization", f"Bearer {token}")]

    # 1. Borrow Book (Protected)
    print("Test BorrowBook (Protected):")
    due_date = datetime.now(UTC) + timedelta(days=14)
    borrow_req = borrowings_pb2.BorrowRequest(
        book_id=book_id, member_id=member_id, due_date=datetime_to_timestamp(due_date)
    )
    record = await stub.BorrowBook(borrow_req, metadata=metadata)
    print(f"Borrowing Created - ID: {record.id}, Status: {record.status}")

    # 2. Get Current Borrowings (Protected)
    print("\nTest GetCurrentBorrowings (Protected):")
    current = await stub.GetCurrentBorrowings(
        borrowings_pb2.GetBorrowRequest(), metadata=metadata
    )
    print(f"Active records: {len(current.borrowings)}")

    # 3. Get Member Borrowings (Protected)
    print("\nTest GetMemberBorrowings (Protected):")
    member_req = borrowings_pb2.GetMemberBorrowingsRequest(id=member_id)
    member_records = await stub.GetMemberBorrowings(member_req, metadata=metadata)
    print(f"Member records: {len(member_records.borrowings)}")

    # 4. Return Book (Protected)
    print("\nTest ReturnBook (Protected):")
    return_req = borrowings_pb2.ReturnRequest(book_id=book_id, member_id=member_id)
    returned = await stub.ReturnBook(return_req, metadata=metadata)
    print(f"Return Recorded - ID: {returned.id}, Status: {returned.status}")

    # 5. Get History (Protected)
    print("\nTest GetBorrowingsHistory (Protected):")
    history = await stub.GetBorrowingsHistory(
        borrowings_pb2.GetBorrowRequest(), metadata=metadata
    )
    print(f"Total history: {len(history.borrowings)}")


async def cleanup(token, book_id, member_id):
    print("\n--- Cleanup ---")
    async with grpc.aio.insecure_channel(SERVER_ADDR) as channel:
        book_stub = books_pb2_grpc.BookServiceStub(channel)
        member_stub = members_pb2_grpc.MemberServiceStub(channel)
        metadata = [("authorization", f"Bearer {token}")]

        try:
            await book_stub.DeleteBook(
                books_pb2.DeleteBookRequest(id=book_id), metadata=metadata
            )
            print(f"Deleted Book ID: {book_id}")
            await member_stub.DeleteMember(
                members_pb2.DeleteMemberRequest(id=member_id), metadata=metadata
            )
            print(f"Deleted Member ID: {member_id}")
        except grpc.RpcError as e:
            print(f"Cleanup failed: {e.details()}")


async def main():
    print("Starting Auth-Enabled gRPC Test Suite")
    print("=" * 40)

    try:
        async with grpc.aio.insecure_channel(SERVER_ADDR) as channel:
            # First, authenticate
            token = await test_auth_service(channel)

            # Test Books
            book_id = await test_book_service(channel, token)

            # Test Members
            member_id = await test_member_service(channel, token)

            # Test Borrowings
            await test_borrowing_service(channel, token, book_id, member_id)

            # Final Cleanup
            await cleanup(token, book_id, member_id)

    except grpc.RpcError as e:
        print(f"Test failure: {e.code()} - {e.details()}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

    print("=" * 40)
    print("Tests Finished")


if __name__ == "__main__":
    asyncio.run(main())
