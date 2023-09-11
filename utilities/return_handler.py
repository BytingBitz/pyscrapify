''' Created: 12/09/2023 '''

# External Dependencies
from functools import wraps
from typing import List, Dict, get_args, get_origin, Any
from selenium.webdriver.remote.webdriver import WebElement

# Internal Dependencies
from utilities.exception_handler import ScraperExceptions as SE

def returns(expected_type: Any):
    ''' Purpose: Decorator wraps function and verifies contents of return match
        expected return type. If expected_type argument is provided, return will
        be matched to type argument. '''
    
    if expected_type is None:
        expected_type = type(None)
    
    def type_check(value, expected) -> bool:
        origin = get_origin(expected)
        args = get_args(expected)
        # Direct check for basic types
        if isinstance(value, (bool, str, int, WebElement)):
            return isinstance(value, expected)
        # Check for None
        if value is None and expected == type(None):
            return True
        # Check for List type
        if origin is List:
            if not isinstance(value, list):
                return False
            expected_item_type = args[0]
            return all(type_check(item, expected_item_type) for item in value)
        # Check for Dict type
        if origin is Dict:
            if not isinstance(value, dict):
                return False
            expected_key_type, expected_val_type = args
            return (all(isinstance(key, expected_key_type) for key in value.keys()) and 
                    all(type_check(val, expected_val_type) for val in value.values()))
        return False

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('FUCKEN HELLO')
            result = func(*args, **kwargs)
            expected = expected_type if expected_type else func.__annotations__.get('return', Any)
            if not type_check(result, expected):
                raise SE.BadScraper(f"Expected {func.__name__} to return {expected}, got {type(result)}")
            return result
        return wrapper
    
    return decorator
