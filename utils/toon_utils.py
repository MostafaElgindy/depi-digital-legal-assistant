"""
TOON Utilities Module
======================
Utilities for TOON serialization and deserialization.
TOON (Text Object Notation) - Alternative format to JSON, more readable.
"""

from typing import Any, Dict, Union, Type, List
from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import Response as FastAPIResponse
from starlette.background import BackgroundTask
from datetime import datetime, date
import re


# ==================== Content Type ====================
TOON_CONTENT_TYPE = "application/toon"


# ==================== TOON Serializer ====================

class TOONSerializer:
    """
    Custom serializer for TOON format.
    Converts Python data to TOON text and vice versa.
    """
    
    @staticmethod
    def dumps(data: Any, indent: str = "") -> str:
        """Convert Python data to TOON text."""
        lines = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    continue
                    
                clean_key = str(key).replace(" ", "_")
                
                if isinstance(value, str):
                    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                    lines.append(f'{indent}{clean_key} = "{escaped}"')
                    
                elif isinstance(value, bool):
                    lines.append(f'{indent}{clean_key} = {str(value).lower()}')
                    
                elif isinstance(value, (int, float)):
                    lines.append(f'{indent}{clean_key} = {value}')
                    
                elif isinstance(value, (datetime, date)):
                    lines.append(f'{indent}{clean_key} = "{value.isoformat()}"')
                    
                elif isinstance(value, list):
                    if len(value) == 0:
                        lines.append(f'{indent}{clean_key} = []')
                    elif all(isinstance(item, (str, int, float, bool)) for item in value):
                        items = []
                        for item in value:
                            if isinstance(item, str):
                                items.append(f'"{item}"')
                            elif isinstance(item, bool):
                                items.append(str(item).lower())
                            else:
                                items.append(str(item))
                        lines.append(f'{indent}{clean_key} = [{", ".join(items)}]')
                    else:
                        for item in value:
                            lines.append(f'\n{indent}[[{clean_key}]]')
                            if isinstance(item, dict):
                                lines.append(TOONSerializer.dumps(item, indent))
                            else:
                                lines.append(f'{indent}value = "{item}"')
                                
                elif isinstance(value, dict):
                    lines.append(f'\n{indent}[{clean_key}]')
                    lines.append(TOONSerializer.dumps(value, indent))
                    
                else:
                    lines.append(f'{indent}{clean_key} = "{str(value)}"')
        else:
            lines.append(f'value = "{str(data)}"')
            
        return "\n".join(lines)
    
    @staticmethod
    def loads(toon_string: str) -> Dict[str, Any]:
        """Convert TOON text to Python data."""
        result = {}
        current_section = result
        
        lines = toon_string.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('[[') and line.endswith(']]'):
                array_name = line[2:-2].strip()
                if array_name not in result:
                    result[array_name] = []
                new_item = {}
                result[array_name].append(new_item)
                current_section = new_item
                continue
            
            if line.startswith('[') and line.endswith(']'):
                section_name = line[1:-1].strip()
                parts = section_name.split('.')
                current_section = TOONSerializer._ensure_path(result, parts)
                continue
            
            eq_index = line.find('=')
            if eq_index > 0:
                key = line[:eq_index].strip()
                value = line[eq_index + 1:].strip()
                current_section[key] = TOONSerializer._parse_value(value)
        
        return result
    
    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse TOON value"""
        value = value.strip()
        
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1].replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        
        if re.match(r'^-?\d+\.\d+$', value):
            return float(value)
        
        if re.match(r'^-?\d+$', value):
            return int(value)
        
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            if not inner:
                return []
            
            items = []
            current_item = ""
            in_string = False
            
            for char in inner:
                if char == '"' and (not current_item or current_item[-1] != '\\'):
                    in_string = not in_string
                    current_item += char
                elif char == ',' and not in_string:
                    if current_item.strip():
                        items.append(TOONSerializer._parse_value(current_item.strip()))
                    current_item = ""
                else:
                    current_item += char
            
            if current_item.strip():
                items.append(TOONSerializer._parse_value(current_item.strip()))
            
            return items
        
        return value
    
    @staticmethod
    def _ensure_path(obj: dict, path: List[str]) -> dict:
        """Ensure path exists in object"""
        current = obj
        for key in path:
            if key not in current:
                current[key] = {}
            current = current[key]
        return current


# ==================== Serialization Functions ====================

def serialize_to_toon(data: Any) -> str:
    """Convert Python data to TOON format."""
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='python')
    
    data = _convert_datetime_recursive(data)
    
    return TOONSerializer.dumps(data)


def deserialize_from_toon(toon_string: str) -> Dict[str, Any]:
    """Convert TOON text to Python data."""
    return TOONSerializer.loads(toon_string)


def _convert_datetime_recursive(data: Any) -> Any:
    """Convert all datetime objects in data to strings."""
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: _convert_datetime_recursive(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_datetime_recursive(item) for item in data]
    return data


# ==================== Pydantic Integration ====================

def toon_to_pydantic(toon_string: str, model_class: Type[BaseModel]) -> BaseModel:
    """
    Convert TOON text to Pydantic model.
    
    Args:
        toon_string: Text in TOON format
        model_class: Pydantic Model class
    
    Returns:
        BaseModel: Pydantic object
    """
    data = deserialize_from_toon(toon_string)
    return model_class(**data)


def pydantic_to_toon(model: BaseModel) -> str:
    """
    Convert Pydantic model to TOON text.
    
    Args:
        model: Pydantic object
    
    Returns:
        str: Text in TOON format
    """
    return serialize_to_toon(model)


# ==================== FastAPI Integration ====================

class TOONResponse(FastAPIResponse):
    """
    Custom Response class for FastAPI that sends data in TOON format.
    
    Usage:
        return TOONResponse(content={"message": "Hello"})
    """
    media_type = TOON_CONTENT_TYPE
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Dict[str, str] = None,
        background: BackgroundTask = None,
    ):
        # Convert content to TOON
        if content is not None:
            body = serialize_to_toon(content)
        else:
            body = ""
        
        super().__init__(
            content=body.encode("utf-8"),
            status_code=status_code,
            headers=headers,
            media_type=self.media_type,
            background=background,
        )


async def parse_toon_request(request: Request) -> Dict[str, Any]:
    """
    Read and parse TOON request from FastAPI Request.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Dict[str, Any]: Parsed data
    
    Raises:
        ValueError: If content is invalid
    """
    body = await request.body()
    body_str = body.decode("utf-8")
    
    if not body_str.strip():
        return {}
    
    try:
        return deserialize_from_toon(body_str)
    except Exception as e:
        raise ValueError(f"Invalid TOON format: {str(e)}")


# ==================== Error Handling ====================

def create_error_toon(
    error_code: str,
    error_message: str,
    details: str = None
) -> str:
    """
    Create error message in TOON format.
    
    Args:
        error_code: Error code
        error_message: Error message
        details: Additional details (optional)
    
    Returns:
        str: Error message in TOON format
    """
    from datetime import datetime
    
    error_data = {
        "success": False,
        "error_code": error_code,
        "error_message": error_message,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        error_data["details"] = details
    
    return serialize_to_toon(error_data)


def create_success_toon(data: Dict[str, Any]) -> str:
    """
    Create success message in TOON format.
    
    Args:
        data: Data to send
    
    Returns:
        str: Message in TOON format
    """
    from datetime import datetime
    
    response_data = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        **data
    }
    
    return serialize_to_toon(response_data)


# ==================== TOON Format Documentation ====================
"""
TOON Format (TOML Object Notation):
====================================

TOON is a data format similar to TOML but optimized for use as a JSON alternative.

Format Examples:
----------------

1. Simple values:
   name = "Ahmed"
   age = 25
   is_active = true

2. Lists:
   colors = ["red", "green", "blue"]
   numbers = [1, 2, 3]

3. Nested objects:
   [user]
   name = "Ahmed"
   email = "ahmed@example.com"
   
   [user.address]
   city = "Cairo"
   country = "Egypt"

4. Response example:
   success = true
   timestamp = "2024-01-15T10:30:00"
   
   [data]
   query = "What are citizen rights?"
   answer = "According to Article 53..."
   
   [[data.sources]]
   content = "Article text..."
   page_number = 10
"""
