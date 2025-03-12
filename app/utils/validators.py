"""
Validation utility functions.
"""
import re

def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Validate password requirements.
    
    Args:
        password: Password string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not password or len(password) < 8:
        return False
    
    has_digit = any(char.isdigit() for char in password)
    has_letter = any(char.isalpha() for char in password)
    
    return has_digit and has_letter

def validate_name(name):
    """
    Validate name format.
    
    Args:
        name: Name string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name) < 2:
        return False
    
    return bool(re.match(r'^[A-Za-z\s\-]+$', name))

def validate_numeric_string(value, min_val=None, max_val=None):
    """
    Validate that a string can be converted to a number and is within range.
    
    Args:
        value: String to validate
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return False
        if max_val is not None and num_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False 