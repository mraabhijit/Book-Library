import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
class TestBorrowingsEndpoints:
    """Test suite for borrowings endpoints."""

    # ==================== Helper Fixtures ====================

    @pytest_asyncio.fixture
    async def created_book(self, client: AsyncClient, sample_book_data):
        """Create a book and return its data."""
        response = await client.post("/api/books", json=sample_book_data)
        return response.json()

    @pytest_asyncio.fixture
    async def created_member(self, client: AsyncClient, sample_member_data):
        """Create a member and return its data."""
        response = await client.post("/api/members", json=sample_member_data)
        return response.json()

    @pytest_asyncio.fixture
    async def second_book(self, client: AsyncClient):
        """Create a second book for testing."""
        book_data = {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "978-0-452-28423-4",
            "description": "Dystopian novel",
        }
        response = await client.post("/api/books", json=book_data)
        return response.json()

    @pytest_asyncio.fixture
    async def second_member(self, client: AsyncClient):
        """Create a second member for testing."""
        member_data = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "9876543210",
        }
        response = await client.post("/api/members", json=member_data)
        return response.json()

    # ==================== GET Endpoints Tests ====================

    async def test_get_current_borrowing_records_empty(self, client: AsyncClient):
        """Test getting current borrowing records when none exist."""
        response = await client.get("/api/borrowings")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_borrowing_history_empty(self, client: AsyncClient):
        """Test getting borrowing history when none exist."""
        response = await client.get("/api/borrowings/history")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_borrowing_records_by_member_id_not_found(
        self, client: AsyncClient
    ):
        """Test getting borrowing records for non-existent member."""
        response = await client.get("/api/borrowings/members/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_borrowing_records_by_member_id_invalid(
        self, client: AsyncClient
    ):
        """Test getting borrowing records with invalid member ID."""
        response = await client.get("/api/borrowings/members/0")
        assert response.status_code == 422
        assert "must be positive" in response.json()["detail"]

        response = await client.get("/api/borrowings/members/-1")
        assert response.status_code == 422

    async def test_get_borrowing_records_by_member_id_empty(
        self, client: AsyncClient, created_member
    ):
        """Test getting borrowing records for member with no borrowings."""
        member_id = created_member["id"]
        response = await client.get(f"/api/borrowings/members/{member_id}")
        assert response.status_code == 200
        assert response.json() == []

    # ==================== Borrow Book Tests ====================

    async def test_borrow_book_success(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test successfully borrowing a book."""
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }

        response = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response.status_code == 200

        data = response.json()
        assert data["book_id"] == created_book["id"]
        assert data["member_id"] == created_member["id"]
        assert "borrowed_date" in data
        assert data["status"] == "BORROWED"
        assert data["returned_date"] is None

        # Verify nested book and member data
        assert data["book"]["id"] == created_book["id"]
        assert data["book"]["title"] == created_book["title"]
        assert data["member"]["id"] == created_member["id"]
        assert data["member"]["email"] == created_member["email"]

    async def test_borrow_book_marks_unavailable(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test that borrowing a book marks it as unavailable."""
        book_id = created_book["id"]

        # Verify book is available initially
        book_response = await client.get(f"/api/books/{book_id}")
        assert book_response.json()["is_available"] is True

        # Borrow the book
        borrow_data = {
            "book_id": book_id,
            "member_id": created_member["id"],
        }
        await client.post("/api/borrowings/borrow", json=borrow_data)

        # Verify book is now unavailable
        book_response = await client.get(f"/api/books/{book_id}")
        assert book_response.json()["is_available"] is False

    async def test_borrow_book_not_found(self, client: AsyncClient, created_member):
        """Test borrowing a non-existent book."""
        borrow_data = {
            "book_id": 999,
            "member_id": created_member["id"],
        }

        response = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]

    async def test_borrow_book_member_not_found(
        self, client: AsyncClient, created_book
    ):
        """Test borrowing with non-existent member."""
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": 999,
        }

        response = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response.status_code == 404
        assert "Member not found" in response.json()["detail"]

    async def test_borrow_book_already_borrowed(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test borrowing a book that is already borrowed."""
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }

        # First borrow should succeed
        response1 = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response1.status_code == 200

        # Second borrow should fail
        response2 = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response2.status_code == 400
        assert "not available" in response2.json()["detail"].lower()

    async def test_borrow_book_invalid_book_id(
        self, client: AsyncClient, created_member
    ):
        """Test borrowing with invalid book_id (validation)."""
        borrow_data = {
            "book_id": 0,  # Invalid: must be > 0
            "member_id": created_member["id"],
        }

        response = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response.status_code == 422  # Validation error

    async def test_borrow_book_invalid_member_id(
        self, client: AsyncClient, created_book
    ):
        """Test borrowing with invalid member_id (validation)."""
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": -1,  # Invalid: must be > 0
        }

        response = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response.status_code == 422  # Validation error

    # ==================== Return Book Tests ====================

    async def test_return_book_success(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test successfully returning a borrowed book."""
        # First borrow the book
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        await client.post("/api/borrowings/borrow", json=borrow_data)

        # Now return it
        return_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        response = await client.put("/api/borrowings/return", json=return_data)
        assert response.status_code == 200

        data = response.json()
        assert data["book_id"] == created_book["id"]
        assert data["member_id"] == created_member["id"]
        assert data["status"] == "RETURNED"
        assert data["returned_date"] is not None

    async def test_return_book_marks_available(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test that returning a book marks it as available."""
        book_id = created_book["id"]

        # Borrow the book
        borrow_data = {
            "book_id": book_id,
            "member_id": created_member["id"],
        }
        await client.post("/api/borrowings/borrow", json=borrow_data)

        # Verify book is unavailable
        book_response = await client.get(f"/api/books/{book_id}")
        assert book_response.json()["is_available"] is False

        # Return the book
        return_data = {
            "book_id": book_id,
            "member_id": created_member["id"],
        }
        await client.put("/api/borrowings/return", json=return_data)

        # Verify book is now available
        book_response = await client.get(f"/api/books/{book_id}")
        assert book_response.json()["is_available"] is True

    async def test_return_book_not_borrowed(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test returning a book that was never borrowed."""
        return_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }

        response = await client.put("/api/borrowings/return", json=return_data)
        assert response.status_code == 404
        assert "No borrowing record found" in response.json()["detail"]

    async def test_return_book_wrong_member(
        self, client: AsyncClient, created_book, created_member, second_member
    ):
        """Test returning a book borrowed by a different member."""
        # Member 1 borrows the book
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        await client.post("/api/borrowings/borrow", json=borrow_data)

        # Member 2 tries to return it
        return_data = {
            "book_id": created_book["id"],
            "member_id": second_member["id"],
        }
        response = await client.put("/api/borrowings/return", json=return_data)
        assert response.status_code == 404
        assert "No borrowing record found" in response.json()["detail"]

    async def test_return_book_already_returned(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test returning a book that was already returned."""
        # Borrow the book
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        await client.post("/api/borrowings/borrow", json=borrow_data)

        # Return it once
        return_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        response1 = await client.put("/api/borrowings/return", json=return_data)
        assert response1.status_code == 200

        # Try to return it again
        response2 = await client.put("/api/borrowings/return", json=return_data)
        assert response2.status_code == 404
        assert "No borrowing record found" in response2.json()["detail"]

    # ==================== GET Current Borrowings Tests ====================

    async def test_get_current_borrowing_records(
        self, client: AsyncClient, created_book, created_member, second_book
    ):
        """Test getting current (unreturned) borrowing records."""
        # Borrow two books
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": second_book["id"], "member_id": created_member["id"]},
        )

        # Get current borrowings
        response = await client.get("/api/borrowings")
        assert response.status_code == 200

        records = response.json()
        assert len(records) == 2
        assert all(record["status"] == "BORROWED" for record in records)
        assert all(record["returned_date"] is None for record in records)

    async def test_get_current_borrowing_excludes_returned(
        self, client: AsyncClient, created_book, created_member, second_book
    ):
        """Test that current borrowings exclude returned books."""
        # Borrow two books
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": second_book["id"], "member_id": created_member["id"]},
        )

        # Return one book
        await client.put(
            "/api/borrowings/return",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )

        # Get current borrowings - should only have one
        response = await client.get("/api/borrowings")
        assert response.status_code == 200

        records = response.json()
        assert len(records) == 1
        assert records[0]["book_id"] == second_book["id"]
        assert records[0]["status"] == "BORROWED"

    # ==================== GET History Tests ====================

    async def test_get_borrowing_history(
        self, client: AsyncClient, created_book, created_member, second_book
    ):
        """Test getting complete borrowing history."""
        # Borrow two books
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": second_book["id"], "member_id": created_member["id"]},
        )

        # Return one book
        await client.put(
            "/api/borrowings/return",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )

        # Get history - should have both
        response = await client.get("/api/borrowings/history")
        assert response.status_code == 200

        records = response.json()
        assert len(records) == 2

        # One should be returned, one borrowed
        statuses = {record["status"] for record in records}
        assert statuses == {"BORROWED", "RETURNED"}

    # ==================== GET by Member ID Tests ====================

    async def test_get_borrowing_records_by_member_id(
        self,
        client: AsyncClient,
        created_book,
        created_member,
        second_member,
        second_book,
    ):
        """Test getting borrowing records for a specific member."""
        # Member 1 borrows book 1
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )

        # Member 2 borrows book 2
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": second_book["id"], "member_id": second_member["id"]},
        )

        # Get member 1's records
        response = await client.get(f"/api/borrowings/members/{created_member['id']}")
        assert response.status_code == 200

        records = response.json()
        assert len(records) == 1
        assert records[0]["member_id"] == created_member["id"]
        assert records[0]["book_id"] == created_book["id"]

    async def test_get_borrowing_records_by_member_includes_returned(
        self, client: AsyncClient, created_book, created_member, second_book
    ):
        """Test that member's records include both borrowed and returned books."""
        # Borrow two books
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )
        await client.post(
            "/api/borrowings/borrow",
            json={"book_id": second_book["id"], "member_id": created_member["id"]},
        )

        # Return one book
        await client.put(
            "/api/borrowings/return",
            json={"book_id": created_book["id"], "member_id": created_member["id"]},
        )

        # Get member's records - should have both
        response = await client.get(f"/api/borrowings/members/{created_member['id']}")
        assert response.status_code == 200

        records = response.json()
        assert len(records) == 2

    # ==================== Edge Cases ====================

    async def test_borrow_return_reborrow_cycle(
        self, client: AsyncClient, created_book, created_member
    ):
        """Test borrowing, returning, and borrowing again the same book."""
        borrow_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }
        return_data = {
            "book_id": created_book["id"],
            "member_id": created_member["id"],
        }

        # First borrow
        response1 = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response1.status_code == 200

        # Return
        response2 = await client.put("/api/borrowings/return", json=return_data)
        assert response2.status_code == 200

        # Borrow again - should succeed
        response3 = await client.post("/api/borrowings/borrow", json=borrow_data)
        assert response3.status_code == 200

        # Check history has 2 records
        history_response = await client.get("/api/borrowings/history")
        assert len(history_response.json()) == 2
