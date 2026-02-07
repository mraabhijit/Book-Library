import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestMembersEndpoints:
    """Test suite for members endpoints."""

    async def test_get_members_empty(self, client: AsyncClient):
        """Test getting members when database is empty."""
        response = await client.get("/api/members")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_member(self, client: AsyncClient, sample_member_data):
        """Test creating a new member."""
        response = await client.post("/api/members", json=sample_member_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == sample_member_data["name"]
        assert data["email"] == sample_member_data["email"]
        assert data["phone"] == sample_member_data["phone"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_member_duplicate_email(
        self, client: AsyncClient, sample_member_data
    ):
        """Test creating a member with duplicate email fails."""
        # Create first member
        await client.post("/api/members", json=sample_member_data)

        # Try to create duplicate with different phone
        duplicate_data = sample_member_data.copy()
        duplicate_data["phone"] = "9876543210"

        response = await client.post("/api/members", json=duplicate_data)
        assert response.status_code == 409
        assert "Email already in use" in response.json()["detail"]

    async def test_create_member_duplicate_phone(
        self, client: AsyncClient, sample_member_data
    ):
        """Test creating a member with duplicate phone fails."""
        # Create first member
        await client.post("/api/members", json=sample_member_data)

        # Try to create duplicate with different email
        duplicate_data = sample_member_data.copy()
        duplicate_data["email"] = "different@example.com"

        response = await client.post("/api/members", json=duplicate_data)
        assert response.status_code == 409
        assert "Phone already in use" in response.json()["detail"]

    async def test_create_member_case_insensitive_email(
        self, client: AsyncClient, sample_member_data
    ):
        """Test that email comparison is case-insensitive."""
        await client.post("/api/members", json=sample_member_data)

        # Try with uppercase email
        duplicate_data = sample_member_data.copy()
        duplicate_data["email"] = sample_member_data["email"].upper()
        duplicate_data["phone"] = "9876543210"

        response = await client.post("/api/members", json=duplicate_data)
        assert response.status_code == 409

    async def test_get_members_list(self, client: AsyncClient, sample_member_data):
        """Test getting list of members."""
        await client.post("/api/members", json=sample_member_data)

        response = await client.get("/api/members")
        assert response.status_code == 200

        members = response.json()
        assert len(members) == 1
        assert members[0]["email"] == sample_member_data["email"]

    async def test_get_member_by_id(self, client: AsyncClient, sample_member_data):
        """Test getting a specific member by ID."""
        # Create member
        create_response = await client.post("/api/members", json=sample_member_data)
        member_id = create_response.json()["id"]

        # Get member by ID
        response = await client.get(f"/api/members/{member_id}")
        assert response.status_code == 200
        assert response.json()["id"] == member_id

    async def test_get_member_by_id_not_found(self, client: AsyncClient):
        """Test getting a non-existent member."""
        response = await client.get("/api/members/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_member_invalid_id(self, client: AsyncClient):
        """Test getting a member with invalid ID."""
        response = await client.get("/api/members/0")
        assert response.status_code == 422
        assert "must be positive" in response.json()["detail"]

    async def test_update_member(self, client: AsyncClient, sample_member_data):
        """Test updating a member."""
        # Create member
        create_response = await client.post("/api/members", json=sample_member_data)
        member_id = create_response.json()["id"]

        # Update member
        update_data = {"name": "Jane Doe", "phone": "9876543210"}
        response = await client.put(f"/api/members/{member_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert data["phone"] == "9876543210"
        assert data["email"] == sample_member_data["email"]  # Unchanged

    async def test_update_member_email_conflict(
        self, client: AsyncClient, sample_member_data
    ):
        """Test updating member with email that belongs to another member."""
        # Create first member
        await client.post("/api/members", json=sample_member_data)

        # Create second member
        second_member_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "9876543210",
        }
        create_response = await client.post("/api/members", json=second_member_data)
        second_member_id = create_response.json()["id"]

        # Try to update second member with first member's email
        response = await client.put(
            f"/api/members/{second_member_id}",
            json={"email": sample_member_data["email"]},
        )
        assert response.status_code == 409
        assert "Email already in use" in response.json()["detail"]

    async def test_update_member_phone_conflict(
        self, client: AsyncClient, sample_member_data
    ):
        """Test updating member with phone that belongs to another member."""
        # Create first member
        await client.post("/api/members", json=sample_member_data)

        # Create second member
        second_member_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "9876543210",
        }
        create_response = await client.post("/api/members", json=second_member_data)
        second_member_id = create_response.json()["id"]

        # Try to update second member with first member's phone
        response = await client.put(
            f"/api/members/{second_member_id}",
            json={"phone": sample_member_data["phone"]},
        )
        assert response.status_code == 409
        assert "Phone already in use" in response.json()["detail"]

    async def test_update_member_not_found(self, client: AsyncClient):
        """Test updating a non-existent member."""
        update_data = {"name": "Updated Name"}
        response = await client.put("/api/members/999", json=update_data)
        assert response.status_code == 404

    async def test_delete_member(self, client: AsyncClient, sample_member_data):
        """Test deleting a member."""
        # Create member
        create_response = await client.post("/api/members", json=sample_member_data)
        member_id = create_response.json()["id"]

        # Delete member
        response = await client.delete(f"/api/members/{member_id}")
        assert response.status_code == 204

        # Verify member is deleted
        get_response = await client.get(f"/api/members/{member_id}")
        assert get_response.status_code == 404

    async def test_delete_member_not_found(self, client: AsyncClient):
        """Test deleting a non-existent member."""
        response = await client.delete("/api/members/999")
        assert response.status_code == 404

    async def test_delete_member_invalid_id(self, client: AsyncClient):
        """Test deleting a member with invalid ID."""
        response = await client.delete("/api/members/0")
        assert response.status_code == 422
