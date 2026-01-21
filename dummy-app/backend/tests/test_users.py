"""
Tests for User CRUD Operations
Coverage: MEDIUM - Some test gaps for demo purposes
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestUserCRUD:
    """Test cases for user CRUD operations."""
    
    def test_create_user(self):
        """Test user creation."""
        response = client.post("/api/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
    
    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        response = client.post("/api/users/", json={
            "username": "testuser2",
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 400
    
    # TODO: Add test for duplicate username
    # TODO: Add test for duplicate email
    
    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        response = client.get("/api/users/nonexistent")
        assert response.status_code == 404
    
    def test_list_users(self):
        """Test listing users."""
        response = client.get("/api/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    # TODO: Add test for pagination
    # TODO: Add test for filtering by active status
    
    def test_delete_user_not_found(self):
        """Test deleting non-existent user."""
        response = client.delete("/api/users/nonexistent")
        assert response.status_code == 404


# NOTE: More tests should be added for:
# - User update operations
# - Deactivate/activate flows
# - Edge cases in validation
