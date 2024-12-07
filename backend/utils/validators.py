
from typing import Dict, Any

def validate_code_input(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
        
    required_fields = ['code', 'language']
    if not all(field in data for field in required_fields):
        return False
        
    if not isinstance(data['code'], str) or not isinstance(data['language'], str):
        return False
        
    return True