from typing import Dict, Any

def validate_code_input(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False
        
    required_fields = ['code', 'language']
    if not all(field in data for field in required_fields):
        return False
        
    if not isinstance(data['code'], str) or not data['code'].strip():
        return False
        
    if not isinstance(data['language'], str) or not data['language'].strip():
        return False
        
    # Add supported language validation if needed
    supported_languages = ['python', 'javascript', 'typescript', 'java']
    if data['language'].lower() not in supported_languages:
        return False
        
    return True