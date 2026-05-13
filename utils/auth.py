"""
Authentication Utility Module
=============================
Handles password hashing, verification, and user session management.
Uses Werkzeug's built-in security functions for password hashing.
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """
    Hash a plain-text password using PBKDF2 with SHA-256.
    
    Args:
        password (str): The plain-text password to hash.
    
    Returns:
        str: The hashed password string (includes salt).
    """
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def verify_password(password_hash, password):
    """
    Verify a plain-text password against a stored hash.
    
    Args:
        password_hash (str): The stored hashed password.
        password (str): The plain-text password to check.
    
    Returns:
        bool: True if password matches, False otherwise.
    """
    return check_password_hash(password_hash, password)


def is_valid_email(email):
    """
    Basic email format validation.
    
    Args:
        email (str): Email address to validate.
    
    Returns:
        bool: True if email format is valid.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_strong_password(password):
    """
    Check if password meets minimum strength requirements.
    Requirements: At least 6 characters long.
    
    Args:
        password (str): Password to check.
    
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks.
    Removes potentially dangerous HTML tags and scripts.
    
    Args:
        text (str): Raw user input text.
    
    Returns:
        str: Sanitized text safe for display.
    """
    if text is None:
        return ""
    import re
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()
