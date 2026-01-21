"""
Tests for Utility Functions
Coverage: HIGH - Utilities are well-tested
"""

import pytest
from app.utils.helpers import (
    get_app_info,
    format_timestamp,
    slugify,
    truncate_string,
    safe_json_loads,
    safe_json_dumps,
    deep_merge,
    chunk_list,
    flatten_dict,
    mask_sensitive_data
)
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_phone,
    validate_url,
    validate_credit_card,
    validate_cvv,
    sanitize_input
)


class TestHelpers:
    """Test cases for helper functions."""
    
    def test_get_app_info(self):
        """Test app info retrieval."""
        info = get_app_info()
        assert "name" in info
        assert "version" in info
        assert info["name"] == "Dummy App"
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        result = format_timestamp(1609459200)  # 2021-01-01 00:00:00 UTC
        assert "2021-01-01" in result
    
    def test_slugify(self):
        """Test text slugification."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("Hello  World") == "hello-world"
        assert slugify("Hello!@#World") == "helloworld"
        assert slugify("  hello  ") == "hello"
    
    def test_truncate_string(self):
        """Test string truncation."""
        assert truncate_string("Hello World", 20) == "Hello World"
        assert truncate_string("Hello World", 8) == "Hello..."
        assert truncate_string("Hi", 5) == "Hi"
    
    def test_safe_json_loads(self):
        """Test safe JSON parsing."""
        assert safe_json_loads('{"key": "value"}') == {"key": "value"}
        assert safe_json_loads("invalid") is None
        assert safe_json_loads("invalid", {}) == {}
    
    def test_safe_json_dumps(self):
        """Test safe JSON serialization."""
        assert safe_json_dumps({"key": "value"}) == '{"key": "value"}'
    
    def test_deep_merge(self):
        """Test deep dictionary merge."""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"d": 3}, "e": 4}
        result = deep_merge(base, override)
        assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
    
    def test_chunk_list(self):
        """Test list chunking."""
        items = [1, 2, 3, 4, 5]
        chunks = chunk_list(items, 2)
        assert chunks == [[1, 2], [3, 4], [5]]
    
    def test_flatten_dict(self):
        """Test dictionary flattening."""
        data = {"a": {"b": {"c": 1}}}
        result = flatten_dict(data)
        assert result == {"a.b.c": 1}
    
    def test_mask_sensitive_data(self):
        """Test data masking."""
        assert mask_sensitive_data("1234567890", 4) == "******7890"
        assert mask_sensitive_data("123", 4) == "***"


class TestValidators:
    """Test cases for validators."""
    
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        assert error is None
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        is_valid, error = validate_email("invalid-email")
        assert is_valid is False
        assert error is not None
    
    def test_validate_email_empty(self):
        """Test empty email."""
        is_valid, error = validate_email("")
        assert is_valid is False
    
    def test_validate_password_strong(self):
        """Test strong password."""
        is_valid, error = validate_password("SecurePass123!")
        assert is_valid is True
    
    def test_validate_password_weak(self):
        """Test weak password."""
        is_valid, error = validate_password("weak")
        assert is_valid is False
    
    def test_validate_username_valid(self):
        """Test valid username."""
        is_valid, error = validate_username("user_123")
        assert is_valid is True
    
    def test_validate_username_invalid(self):
        """Test invalid username."""
        is_valid, error = validate_username("123user")  # Can't start with number
        assert is_valid is False
    
    def test_validate_phone_valid(self):
        """Test valid phone number."""
        is_valid, error = validate_phone("+1 (555) 123-4567")
        assert is_valid is True
    
    def test_validate_url_valid(self):
        """Test valid URL."""
        is_valid, error = validate_url("https://example.com/path")
        assert is_valid is True
    
    def test_validate_url_invalid(self):
        """Test invalid URL."""
        is_valid, error = validate_url("not-a-url")
        assert is_valid is False
    
    def test_validate_credit_card_valid(self):
        """Test valid credit card (Luhn check)."""
        # Test card number that passes Luhn
        is_valid, error = validate_credit_card("4532015112830366")
        assert is_valid is True
    
    def test_validate_credit_card_invalid(self):
        """Test invalid credit card."""
        is_valid, error = validate_credit_card("1234567890123456")
        assert is_valid is False
    
    def test_validate_cvv_valid(self):
        """Test valid CVV."""
        is_valid, error = validate_cvv("123")
        assert is_valid is True
        
        is_valid, error = validate_cvv("1234")  # Amex
        assert is_valid is True
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        result = sanitize_input("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
