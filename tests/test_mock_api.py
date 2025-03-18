"""
Tests for the mock Kaltura API.

These tests verify that the mock Kaltura API works correctly.
"""

import uuid

import pytest

from tests.mocks.mock_kaltura_api import MockKalturaAPI, MockKalturaClientWrapper

# Only run tests with asyncio backend to avoid trio dependency issues
pytestmark = pytest.mark.asyncio


class TestMockKalturaAPI:
    """Tests for the mock Kaltura API."""

    async def test_list_media(self):
        """Test listing media entries."""
        api = MockKalturaAPI()

        # List media entries
        response = await api.list_media()

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0
        assert response.totalCount > 0

        # Verify first entry
        entry = response.objects[0]
        assert hasattr(entry, "id")
        assert hasattr(entry, "name")
        assert hasattr(entry, "description")

    async def test_get_media_entry(self):
        """Test getting a media entry."""
        api = MockKalturaAPI()

        # Get first entry ID
        list_response = await api.list_media()
        entry_id = list_response.objects[0].id

        # Get media entry
        entry = await api.get_media_entry(entry_id)

        # Verify entry
        assert entry is not None
        assert entry.id == entry_id
        assert hasattr(entry, "name")
        assert hasattr(entry, "description")

    async def test_add_update_delete_media(self):
        """Test adding, updating, and deleting a media entry."""
        api = MockKalturaAPI()

        # Add media entry
        from tests.mocks.mock_kaltura_api import KalturaMediaEntry

        entry = KalturaMediaEntry(id="0_test_media", name="Test Media", description="Test Description", tags="test,media")

        added_entry = await api.add_media_entry(entry)

        # Verify added entry
        assert added_entry is not None
        assert hasattr(added_entry, "id")
        assert added_entry.name == "Test Media"
        assert added_entry.description == "Test Description"

        # Update media entry
        updated_entry = KalturaMediaEntry(name="Updated Test Media", description="Updated Test Description")

        updated_entry = await api.update_media_entry(added_entry.id, updated_entry)

        # Verify updated entry
        assert updated_entry is not None
        assert updated_entry.id == added_entry.id
        assert updated_entry.name == "Updated Test Media"
        assert updated_entry.description == "Updated Test Description"

        # Delete media entry
        await api.delete_media_entry(added_entry.id)

        # Verify entry is deleted
        with pytest.raises((ValueError, KeyError)):
            await api.get_media_entry(added_entry.id)

    async def test_list_categories(self):
        """Test listing categories."""
        api = MockKalturaAPI()

        # List categories
        response = await api.list_categories()

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0
        assert response.totalCount > 0

        # Verify first category
        category = response.objects[0]
        assert hasattr(category, "id")
        assert hasattr(category, "name")
        assert hasattr(category, "fullName")

    async def test_get_category(self):
        """Test getting a category."""
        api = MockKalturaAPI()

        # Get first category ID
        list_response = await api.list_categories()
        category_id = list_response.objects[0].id

        # Get category
        category = await api.get_category(category_id)

        # Verify category
        assert category is not None
        assert category.id == category_id
        assert hasattr(category, "name")
        assert hasattr(category, "fullName")

    async def test_add_update_delete_category(self):
        """Test adding, updating, and deleting a category."""
        api = MockKalturaAPI()

        # Add category
        from tests.mocks.mock_kaltura_api import KalturaCategory

        category = KalturaCategory(id=100, name="Test Category", description="Test Description", parentId=0)

        added_category = await api.add_category(category)

        # Verify added category
        assert added_category is not None
        assert hasattr(added_category, "id")
        assert added_category.name == "Test Category"
        assert added_category.description == "Test Description"

        # Update category
        updated_category = KalturaCategory(name="Updated Test Category", description="Updated Test Description")

        updated_category = await api.update_category(added_category.id, updated_category)

        # Verify updated category
        assert updated_category is not None
        assert updated_category.id == added_category.id
        assert updated_category.name == "Updated Test Category"
        assert updated_category.description == "Updated Test Description"

        # Delete category
        await api.delete_category(added_category.id)

        # Verify category is deleted
        with pytest.raises((ValueError, KeyError)):
            await api.get_category(added_category.id)

    async def test_list_users(self):
        """Test listing users."""
        api = MockKalturaAPI()

        # List users
        response = await api.list_users()

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0
        assert response.totalCount > 0

        # Verify first user
        user = response.objects[0]
        assert hasattr(user, "id")
        assert hasattr(user, "screenName")
        assert hasattr(user, "email")

    async def test_get_user(self):
        """Test getting a user."""
        api = MockKalturaAPI()

        # Get first user ID
        list_response = await api.list_users()
        user_id = list_response.objects[0].id

        # Get user
        user = await api.get_user(user_id)

        # Verify user
        assert user is not None
        assert user.id == user_id
        assert hasattr(user, "screenName")
        assert hasattr(user, "email")

    async def test_add_update_delete_user(self):
        """Test adding, updating, and deleting a user."""
        api = MockKalturaAPI()

        # Add user
        from tests.mocks.mock_kaltura_api import KalturaUser

        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        user = KalturaUser(
            id=user_id,
            screenName="Test User",
            email=f"{user_id}@example.com",
            firstName="Test",
            lastName="User",
        )

        added_user = await api.add_user(user)

        # Verify added user
        assert added_user is not None
        assert added_user.id == user_id
        assert added_user.screenName == "Test User"
        assert added_user.email == f"{user_id}@example.com"

        # Update user
        updated_user = KalturaUser(screenName="Updated Test User", firstName="Updated", lastName="User")

        updated_user = await api.update_user(user_id, updated_user)

        # Verify updated user
        assert updated_user is not None
        assert updated_user.id == user_id
        assert updated_user.screenName == "Updated Test User"
        assert updated_user.firstName == "Updated"

        # Delete user
        await api.delete_user(user_id)

        # Verify user is deleted
        with pytest.raises((ValueError, KeyError)):
            await api.get_user(user_id)


class TestMockKalturaClientWrapper:
    """Tests for the mock Kaltura client wrapper."""

    async def test_initialize(self):
        """Test initializing the client wrapper."""
        client = MockKalturaClientWrapper()
        await client.initialize()

        # Verify client is initialized
        assert client.session_id is not None

    async def test_ensure_valid_ks(self):
        """Test ensuring a valid Kaltura session."""
        client = MockKalturaClientWrapper()

        # Ensure valid KS
        ks = await client.ensure_valid_ks()

        # Verify KS
        assert ks is not None
        assert ks == client.session_id

    async def test_execute_request_media_list(self):
        """Test executing a media list request."""
        client = MockKalturaClientWrapper()

        # Execute request
        response = await client.execute_request("media", "list")

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0

    async def test_execute_request_media_get(self):
        """Test executing a media get request."""
        client = MockKalturaClientWrapper()

        # Get first entry ID
        list_response = await client.execute_request("media", "list")
        entry_id = list_response.objects[0].id

        # Execute request
        response = await client.execute_request("media", "get", entryId=entry_id)

        # Verify response
        assert response is not None
        assert response.id == entry_id

    async def test_execute_request_category_list(self):
        """Test executing a category list request."""
        client = MockKalturaClientWrapper()

        # Execute request
        response = await client.execute_request("category", "list")

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0

    async def test_execute_request_user_list(self):
        """Test executing a user list request."""
        client = MockKalturaClientWrapper()

        # Execute request
        response = await client.execute_request("user", "list")

        # Verify response
        assert response is not None
        assert hasattr(response, "objects")
        assert hasattr(response, "totalCount")
        assert len(response.objects) > 0
