"""
TOON (Token-Oriented Object Notation) Parser and Serializer
A lightweight, human-readable data format optimized for APIs and configuration.
"""

import re
from typing import Any, Dict, List, Union


class TOONParser:
    """Parser for TOON format"""
    
    def __init__(self):
        self.pos = 0
        self.text = ""
    
    def parse(self, text: str) -> Any:
        """Parse TOON string to Python object"""
        self.text = text.strip()
        self.pos = 0
        self._skip_whitespace_and_comments()
        return self._parse_value()
    
    def _skip_whitespace_and_comments(self):
        """Skip whitespace and comments"""
        while self.pos < len(self.text):
            # Skip whitespace
            if self.text[self.pos].isspace():
                self.pos += 1
                continue
            
            # Skip comments (# to end of line)
            if self.text[self.pos] == '#':
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
                continue
            
            break
    
    def _parse_value(self) -> Any:
        """Parse any TOON value"""
        self._skip_whitespace_and_comments()
        
        if self.pos >= len(self.text):
            return None
        
        char = self.text[self.pos]
        
        # Object
        if char == '{':
            return self._parse_object()
        
        # Array
        if char == '[':
            return self._parse_array()
        
        # String
        if char in ('"', "'"):
            return self._parse_string()
        
        # Unquoted string / identifier / number
        return self._parse_unquoted()
    
    def _parse_object(self) -> Dict[str, Any]:
        """Parse TOON object"""
        obj = {}
        self.pos += 1  # skip '{'
        
        while True:
            self._skip_whitespace_and_comments()
            
            if self.pos >= len(self.text) or self.text[self.pos] == '}':
                self.pos += 1
                break
            
            # Parse key
            key = self._parse_key()
            
            self._skip_whitespace_and_comments()
            
            # Expect colon
            if self.pos >= len(self.text) or self.text[self.pos] not in (':', '='):
                raise ValueError(f"Expected ':' or '=' at position {self.pos}")
            self.pos += 1
            
            # Parse value
            value = self._parse_value()
            obj[key] = value
            
            self._skip_whitespace_and_comments()
            
            # Check for comma or end
            if self.pos < len(self.text) and self.text[self.pos] == ',':
                self.pos += 1
            elif self.pos < len(self.text) and self.text[self.pos] != '}':
                raise ValueError(f"Expected ',' or '}}' at position {self.pos}")
        
        return obj
    
    def _parse_array(self) -> List[Any]:
        """Parse TOON array"""
        arr = []
        self.pos += 1  # skip '['
        
        while True:
            self._skip_whitespace_and_comments()
            
            if self.pos >= len(self.text) or self.text[self.pos] == ']':
                self.pos += 1
                break
            
            value = self._parse_value()
            arr.append(value)
            
            self._skip_whitespace_and_comments()
            
            if self.pos < len(self.text) and self.text[self.pos] == ',':
                self.pos += 1
            elif self.pos < len(self.text) and self.text[self.pos] != ']':
                raise ValueError(f"Expected ',' or ']' at position {self.pos}")
        
        return arr
    
    def _parse_string(self) -> str:
        """Parse quoted string"""
        quote = self.text[self.pos]
        self.pos += 1
        start = self.pos
        
        while self.pos < len(self.text):
            if self.text[self.pos] == '\\' and self.pos + 1 < len(self.text):
                self.pos += 2
                continue
            
            if self.text[self.pos] == quote:
                result = self.text[start:self.pos]
                self.pos += 1
                return self._unescape_string(result)
            
            self.pos += 1
        
        raise ValueError(f"Unclosed string starting at position {start}")
    
    def _parse_key(self) -> str:
        """Parse object key"""
        self._skip_whitespace_and_comments()
        
        if self.text[self.pos] in ('"', "'"):
            return self._parse_string()
        else:
            return self._parse_identifier()
    
    def _parse_identifier(self) -> str:
        """Parse unquoted identifier"""
        start = self.pos
        
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isalnum() or char in ('_', '-', '.'):
                self.pos += 1
            else:
                break
        
        return self.text[start:self.pos]
    
    def _parse_unquoted(self) -> Union[str, int, float, bool, None]:
        """Parse unquoted value (number, boolean, null, or string)"""
        start = self.pos
        
        # Try to parse as number or boolean
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isalnum() or char in ('_', '-', '.', '+', 'e', 'E'):
                self.pos += 1
            else:
                break
        
        value = self.text[start:self.pos]
        
        # Check for boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        if value.lower() == 'null' or value.lower() == 'nil':
            return None
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
    
    @staticmethod
    def _unescape_string(s: str) -> str:
        """Unescape special characters in string"""
        replacements = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\\\': '\\',
            '\\"': '"',
            "\\'": "'",
        }
        for old, new in replacements.items():
            s = s.replace(old, new)
        return s


class TOONSerializer:
    """Serializer for TOON format"""
    
    def __init__(self, pretty: bool = True, indent: int = 2):
        self.pretty = pretty
        self.indent = indent
        self.current_indent = 0
    
    def serialize(self, obj: Any) -> str:
        """Convert Python object to TOON string"""
        self.current_indent = 0
        return self._serialize_value(obj)
    
    def _serialize_value(self, obj: Any) -> str:
        """Serialize any value"""
        if obj is None:
            return 'null'
        
        if isinstance(obj, bool):
            return 'true' if obj else 'false'
        
        if isinstance(obj, (int, float)):
            return str(obj)
        
        if isinstance(obj, str):
            return self._serialize_string(obj)
        
        if isinstance(obj, dict):
            return self._serialize_object(obj)
        
        if isinstance(obj, (list, tuple)):
            return self._serialize_array(obj)
        
        return self._serialize_string(str(obj))
    
    def _serialize_object(self, obj: Dict[str, Any]) -> str:
        """Serialize object"""
        if not obj:
            return '{}'
        
        lines = ['{']
        self.current_indent += self.indent
        
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            line = ' ' * self.current_indent + f'{key}: {self._serialize_value(value)}'
            if i < len(items) - 1:
                line += ','
            lines.append(line)
        
        self.current_indent -= self.indent
        lines.append(' ' * self.current_indent + '}')
        
        return '\n'.join(lines) if self.pretty else ''.join(lines)
    
    def _serialize_array(self, arr: Union[List[Any], tuple]) -> str:
        """Serialize array"""
        if not arr:
            return '[]'
        
        if not self.pretty or all(isinstance(item, (int, float, bool, type(None), str)) and not isinstance(item, dict) for item in arr):
            # Inline for simple arrays
            items = [self._serialize_value(item) for item in arr]
            return '[' + ', '.join(items) + ']'
        
        lines = ['[']
        self.current_indent += self.indent
        
        for i, item in enumerate(arr):
            line = ' ' * self.current_indent + self._serialize_value(item)
            if i < len(arr) - 1:
                line += ','
            lines.append(line)
        
        self.current_indent -= self.indent
        lines.append(' ' * self.current_indent + ']')
        
        return '\n'.join(lines) if self.pretty else ''.join(lines)
    
    def _serialize_string(self, s: str) -> str:
        """Serialize string with proper escaping"""
        # Check if string needs quotes
        if self._needs_quotes(s):
            escaped = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            return f'"{escaped}"'
        return s
    
    @staticmethod
    def _needs_quotes(s: str) -> bool:
        """Check if string needs quotes"""
        if not s:
            return True
        if s.lower() in ('true', 'false', 'null', 'nil'):
            return True
        if s[0].isdigit() or s[0] in ('+', '-'):
            return True
        if not all(c.isalnum() or c in ('_', '-', '.') for c in s):
            return True
        return False


def parse_toon(text: str) -> Any:
    """Parse TOON string to Python object"""
    parser = TOONParser()
    return parser.parse(text)


def serialize_toon(obj: Any, pretty: bool = True) -> str:
    """Convert Python object to TOON string"""
    serializer = TOONSerializer(pretty=pretty)
    return serializer.serialize(obj)


# Alias for convenience
dumps = serialize_toon
loads = parse_toon
