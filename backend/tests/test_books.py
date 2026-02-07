import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestBooksEndpoints:
    """Test suite for books endpoints."""

    async def test_get_books_empty(self, client: AsyncClient):
        """Test getting books when database is empty."""
        response = await client.get("/api/books")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_book(self, client: AsyncClient, sample_book_data):
        """Test creating a new book."""
        response = await client.post("/api/books", json=sample_book_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == sample_book_data["title"]
        assert data["author"] == sample_book_data["author"]
        assert data["isbn"] == sample_book_data["isbn"]
        assert data["is_available"] is True
        assert "id" in data
        assert "created_at" in data

    async def test_create_book_duplicate_isbn(
        self, client: AsyncClient, sample_book_data
    ):
        """Test creating a book with duplicate ISBN fails."""
        # Create first book
        await client.post("/api/books", json=sample_book_data)

        # Try to create duplicate
        response = await client.post("/api/books", json=sample_book_data)
        assert response.status_code == 409
        assert "ISBN already exists" in response.json()["detail"]

    async def test_get_books_list(self, client: AsyncClient, sample_book_data):
        """Test getting list of books."""
        # Create a book first
        await client.post("/api/books", json=sample_book_data)

        response = await client.get("/api/books")
        assert response.status_code == 200

        books = response.json()
        assert len(books) == 1
        assert books[0]["title"] == sample_book_data["title"]

    async def test_get_books_filter_by_title(
        self, client: AsyncClient, sample_book_data
    ):
        """Test filtering books by title."""
        await client.post("/api/books", json=sample_book_data)

        # Should find the book
        response = await client.get("/api/books?title=Gatsby")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Should not find the book
        response = await client.get("/api/books?title=NonExistent")
        assert response.status_code == 200
        assert len(response.json()) == 0

    async def test_get_books_filter_by_author(
        self, client: AsyncClient, sample_book_data
    ):
        """Test filtering books by author."""
        await client.post("/api/books", json=sample_book_data)

        response = await client.get("/api/books?author=Fitzgerald")
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_get_book_by_id(self, client: AsyncClient, sample_book_data):
        """Test getting a specific book by ID."""
        # Create book
        create_response = await client.post("/api/books", json=sample_book_data)
        book_id = create_response.json()["id"]

        # Get book by ID
        response = await client.get(f"/api/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["id"] == book_id

    async def test_get_book_by_id_not_found(self, client: AsyncClient):
        """Test getting a non-existent book."""
        response = await client.get("/api/books/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_book_invalid_id(self, client: AsyncClient):
        """Test getting a book with invalid ID (negative or zero)."""
        response = await client.get("/api/books/0")
        assert response.status_code == 422
        assert "must be positive" in response.json()["detail"]

        response = await client.get("/api/books/-1")
        assert response.status_code == 422

    async def test_update_book(self, client: AsyncClient, sample_book_data):
        """Test updating a book."""
        # Create book
        create_response = await client.post("/api/books", json=sample_book_data)
        book_id = create_response.json()["id"]

        # Update book
        update_data = {"title": "Updated Title", "description": "New description"}
        response = await client.put(f"/api/books/{book_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"
        assert data["author"] == sample_book_data["author"]  # Unchanged

    async def test_update_book_not_found(self, client: AsyncClient):
        """Test updating a non-existent book."""
        update_data = {"title": "Updated Title"}
        response = await client.put("/api/books/999", json=update_data)
        assert response.status_code == 404

    async def test_update_book_partial(self, client: AsyncClient, sample_book_data):
        """Test partial update of a book."""
        # Create book
        create_response = await client.post("/api/books", json=sample_book_data)
        book_id = create_response.json()["id"]

        # Update only availability
        response = await client.put(
            f"/api/books/{book_id}", json={"is_available": False}
        )

        assert response.status_code == 200
        assert response.json()["is_available"] is False
        assert response.json()["title"] == sample_book_data["title"]

    async def test_delete_book(self, client: AsyncClient, sample_book_data):
        """Test deleting a book."""
        # Create book
        create_response = await client.post("/api/books", json=sample_book_data)
        book_id = create_response.json()["id"]

        # Delete book
        response = await client.delete(f"/api/books/{book_id}")
        assert response.status_code == 204

        # Verify book is deleted
        get_response = await client.get(f"/api/books/{book_id}")
        assert get_response.status_code == 404

    async def test_delete_book_not_found(self, client: AsyncClient):
        """Test deleting a non-existent book."""
        response = await client.delete("/api/books/999")
        assert response.status_code == 404

    async def test_delete_book_invalid_id(self, client: AsyncClient):
        """Test deleting a book with invalid ID."""
        response = await client.delete("/api/books/0")
        assert response.status_code == 422
