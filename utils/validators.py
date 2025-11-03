from email_validator import validate_email, EmailNotValidError
import re

def validate_email_format(email):
    """
    Validate email format using email-validator library.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (is_valid: bool, normalized_email: str or error_message: str)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required and must be a string"
    
    try:
        # Validate and normalize the email address
        # This checks DNS and format validity
        valid = validate_email(email, check_deliverability=False)
        # Returns normalized email (lowercase, etc.)
        return True, valid.email
    except EmailNotValidError as e:
        # Email is not valid; return the error message
        return False, str(e)

def validate_username(username):
    """
    Validate username format.
    
    Rules:
    - 3-20 characters
    - Alphanumeric and underscores only
    - Cannot start or end with underscore
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not username or not isinstance(username, str):
        return False, "Username is required and must be a string"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return False, "Username must be no more than 20 characters long"
    
    # Alphanumeric and underscores only
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    # Cannot start or end with underscore
    if username.startswith('_') or username.endswith('_'):
        return False, "Username cannot start or end with an underscore"
    
    # Cannot start with a number
    if username[0].isdigit():
        return False, "Username cannot start with a number"
    
    return True, None

def validate_password(password):
    """
    Validate password strength.
    
    Rules:
    - At least 6 characters
    - At least one letter and one number (or special char)
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required and must be a string"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password must be no more than 128 characters long"
    
    # Check for at least one letter and one number/special char
    has_letter = re.search(r'[a-zA-Z]', password)
    has_number_or_special = re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    if not has_number_or_special:
        return False, "Password must contain at least one number or special character"
    
    return True, None
