"""
gRPC Client for testing Library App Services
"""

import asyncio
from datetime import datetime, UTC, timedelta
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from protos import books_pb2, books_pb2_grpc
from protos import members_pb2, members_pb2_grpc
from protos import borrowings_pb2, borrowings_pb2_grpc


SERVER_ADDR = "localhost:50052"


def datetime_to_timestamp(dt):
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


async def test_book_service(channel):
    print("--- Testing BookService ---")
    stub = books_pb2_grpc.BookServiceStub(channel)

    # 1. Create Book
    print("Test CreateBook:")
    create_req = books_pb2.CreateBookRequest(
        title="gRPC Test Volume",
        author="Master Coder",
        isbn="123-TEST-999",
        description="A technical manual for gRPC",
    )
    book = await stub.CreateBook(create_req)
    print(f"Created: {book.title} (ID: {book.id})")

    # 2. Get Book by ID
    print("\nTest GetBook:")
    get_req = books_pb2.GetBookRequest(id=book.id)
    fetched_book = await stub.GetBook(get_req)
    print(f"Fetched: {fetched_book.title}")

    # 3. Update Book
    print("\nTest UpdateBook:")
    update_req = books_pb2.UpdateBookRequest(
        id=book.id,
        title="gRPC Test Volume (Updated)",
        description="Updated description",
    )
    updated_book = await stub.UpdateBook(update_req)
    print(f"Updated Title: {updated_book.title}")

    # 4. List Books with Filter
    print("\nTest GetBooks (Filter):")
    list_req = books_pb2.GetBooksRequest(title="gRPC")
    response = await stub.GetBooks(list_req)
    print(f"Found {len(response.books)} books matching 'gRPC'")

    return book.id


async def test_member_service(channel):
    print("\n--- Testing MemberService ---")
    stub = members_pb2_grpc.MemberServiceStub(channel)

    # 1. Create Member
    print("Test CreateMember:")
    create_req = members_pb2.CreateMemberRequest(
        name="Test Member", email="test.member@example.com", phone="5550123456"
    )
    member = await stub.CreateMember(create_req)
    print(f"Created: {member.name} (ID: {member.id})")

    # 2. Get Member by ID
    print("\nTest GetMember:")
    get_req = members_pb2.GetMemberRequest(id=member.id)
    fetched_member = await stub.GetMember(get_req)
    print(f"Fetched: {fetched_member.name}")

    # 3. Update Member
    print("\nTest UpdateMember:")
    update_req = members_pb2.UpdateMemberRequest(
        id=member.id, name="Test Member Revised", phone="5550123999"
    )
    updated_member = await stub.UpdateMember(update_req)
    print(f"Updated Name: {updated_member.name}")

    # 4. List Members
    print("\nTest GetMembers:")
    response = await stub.GetMembers(members_pb2.GetMembersRequest())
    print(f"Total members found: {len(response.members)}")

    return member.id


async def test_borrowing_service(channel, book_id, member_id):
    print("\n--- Testing BorrowingService ---")
    stub = borrowings_pb2_grpc.BorrowingServiceStub(channel)

    # 1. Borrow Book
    print("Test BorrowBook:")
    due_date = datetime.now(UTC) + timedelta(days=14)
    borrow_req = borrowings_pb2.BorrowRequest(
        book_id=book_id, member_id=member_id, due_date=datetime_to_timestamp(due_date)
    )
    record = await stub.BorrowBook(borrow_req)
    print(f"Borrowed ID: {record.id}, Status: {record.status}")

    # 2. Get Current Borrowings
    print("\nTest GetCurrentBorrowings:")
    current = await stub.GetCurrentBorrowings(borrowings_pb2.GetBorrowRequest())
    print(f"Active borrowings found: {len(current.borrowings)}")

    # 3. Get Member Borrowings
    print("\nTest GetMemberBorrowings:")
    member_req = borrowings_pb2.GetMemberBorrowingsRequest(id=member_id)
    member_records = await stub.GetMemberBorrowings(member_req)
    print(f"Records for member {member_id}: {len(member_records.borrowings)}")

    # 4. Return Book
    print("\nTest ReturnBook:")
    return_req = borrowings_pb2.ReturnRequest(book_id=book_id, member_id=member_id)
    returned = await stub.ReturnBook(return_req)
    print(f"Returned ID: {returned.id}, New Status: {returned.status}")

    # 5. Get History
    print("\nTest GetBorrowingsHistory:")
    history = await stub.GetBorrowingsHistory(borrowings_pb2.GetBorrowRequest())
    print(f"History records found: {len(history.borrowings)}")


async def cleanup(book_id, member_id):
    print("\n--- Cleanup ---")
    async with grpc.aio.insecure_channel(SERVER_ADDR) as channel:
        book_stub = books_pb2_grpc.BookServiceStub(channel)
        member_stub = members_pb2_grpc.MemberServiceStub(channel)

        try:
            await book_stub.DeleteBook(books_pb2.DeleteBookRequest(id=book_id))
            print(f"Deleted Book ID: {book_id}")
            await member_stub.DeleteMember(
                members_pb2.DeleteMemberRequest(id=member_id)
            )
            print(f"Deleted Member ID: {member_id}")
        except grpc.RpcError as e:
            print(f"Cleanup failed: {e.details()}")


async def main():
    print("Starting gRPC Test Suite")
    print("=" * 40)

    try:
        async with grpc.aio.insecure_channel(SERVER_ADDR) as channel:
            # Test Books and get an ID for borrowing test
            book_id = await test_book_service(channel)

            # Test Members and get an ID for borrowing test
            member_id = await test_member_service(channel)

            # Test Borrowings
            await test_borrowing_service(channel, book_id, member_id)

            # Final Cleanup
            await cleanup(book_id, member_id)

    except grpc.RpcError as e:
        print(f"Overall test failure: {e.code()} - {e.details()}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

    print("=" * 40)
    print("Tests Finished")


if __name__ == "__main__":
    asyncio.run(main())
