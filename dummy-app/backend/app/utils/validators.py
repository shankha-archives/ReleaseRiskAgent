"""
Input Validators Module
Risk Level: LOW - Input validation utilities

This module contains well-tested validation functions.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email too long"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password too long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Requirements:
    - 3-50 characters
    - Alphanumeric and underscores only
    - Cannot start with a number
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be at most 50 characters"
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Username must start with a letter and contain only letters, numbers, and underscores"
    
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits, optionally starting with +)
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, None


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    pattern = r'^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(/.*)?$'
    
    if not re.match(pattern, url):
        return False, "Invalid URL format"
    
    if len(url) > 2048:
        return False, "URL too long"
    
    return True, None


def validate_credit_card(card_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate credit card number using Luhn algorithm.
    
    Args:
        card_number: Credit card number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not card_number:
        return False, "Card number is required"
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', card_number)
    
    # Check if all digits
    if not cleaned.isdigit():
        return False, "Card number must contain only digits"
    
    # Check length (13-19 digits)
    if len(cleaned) < 13 or len(cleaned) > 19:
        return False, "Invalid card number length"
    
    # Luhn algorithm
    digits = [int(d) for d in cleaned]
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    if checksum % 10 != 0:
        return False, "Invalid card number"
    
    return True, None


def validate_cvv(cvv: str) -> Tuple[bool, Optional[str]]:
    """
    Validate CVV/CVC code.
    
    Args:
        cvv: CVV code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cvv:
        return False, "CVV is required"
    
    if not cvv.isdigit():
        return False, "CVV must contain only digits"
    
    if len(cvv) not in [3, 4]:
        return False, "CVV must be 3 or 4 digits"
    
    return True, None


def validate_expiry_date(month: int, year: int) -> Tuple[bool, Optional[str]]:
    """
    Validate card expiry date.
    
    Args:
        month: Expiry month (1-12)
        year: Expiry year (4-digit)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from datetime import datetime
    
    if month < 1 or month > 12:
        return False, "Invalid expiry month"
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    if year < current_year:
        return False, "Card has expired"
    
    if year == current_year and month < current_month:
        return False, "Card has expired"
    
    if year > current_year + 20:
        return False, "Invalid expiry year"
    
    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Replace potentially dangerous characters
    replacements = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
        '&': '&amp;'
    }
    
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)
    
    return result
