"""
Helper Utilities Module
Risk Level: LOW - Simple utility functions

This module contains well-tested, low-risk helper functions.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import re
import json


def get_app_info() -> Dict[str, str]:
    """Get application information."""
    return {
        "name": "Dummy App",
        "version": "0.1.0",
        "description": "A test application for R3 Agent E2E testing"
    }


def format_timestamp(timestamp: int) -> str:
    """
    Format Unix timestamp to ISO format.
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        ISO formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.isoformat()


def parse_timestamp(iso_string: str) -> int:
    """
    Parse ISO timestamp to Unix timestamp.
    
    Args:
        iso_string: ISO formatted datetime string
        
    Returns:
        Unix timestamp in seconds
    """
    dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    return int(dt.timestamp())


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string.
    
    Args:
        data: Data to serialize
        default: Default value if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        return default


def deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size.
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_dict(data: Dict, parent_key: str = "", separator: str = ".") -> Dict:
    """
    Flatten nested dictionary.
    
    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        separator: Key separator
        
    Returns:
        Flattened dictionary
    """
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data, keeping only last few characters visible.
    
    Args:
        data: Data to mask
        visible_chars: Number of characters to keep visible
        
    Returns:
        Masked string
    """
    if len(data) <= visible_chars:
        return "*" * len(data)
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]


def generate_correlation_id() -> str:
    """Generate a correlation ID for request tracing."""
    import uuid
    return str(uuid.uuid4())
