"""
Ip2location.io Ip Geolocation Api MCP Server - Validators

Generated: 2026-04-09 17:24:47 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import base64
import ipaddress
import re
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, model_serializer, model_validator

__all__ = [
    "StrictModel",
    "PermissiveModel",
    "SuccessResponse",
]

# ============================================================================
# Format Validators
# ============================================================================
# Essential format validation for OpenAPI/JSON Schema formats.
# Validates request data before forwarding to API endpoints.

# Integer range constants
_INT32_MIN, _INT32_MAX = -2_147_483_648, 2_147_483_647
_INT64_MIN, _INT64_MAX = -9_223_372_036_854_775_808, 9_223_372_036_854_775_807
_UINT32_MAX = 4_294_967_295
_UINT64_MAX = 18_446_744_073_709_551_615
_INT8_MIN, _INT8_MAX = -128, 127
_INT16_MIN, _INT16_MAX = -32_768, 32_767
_UINT8_MAX = 255
_UINT16_MAX = 65_535
_DOUBLE_INT_MAX = 9_007_199_254_740_991  # 2^53 - 1
_SF_INTEGER_MAX = 999_999_999_999_999  # 15 digits

def _validate_int32(value):
    """Validate int32 range: -2,147,483,648 to 2,147,483,647"""
    if isinstance(value, float):
        raise ValueError(f"Invalid int32: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (_INT32_MIN <= num <= _INT32_MAX):
        raise ValueError(f"Value {num} outside int32 range")
    return value

def _validate_int64(value):
    """Validate int64 range: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807"""
    if isinstance(value, float):
        raise ValueError(f"Invalid int64: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (_INT64_MIN <= num <= _INT64_MAX):
        raise ValueError(f"Value {num} outside int64 range")
    return value

def _validate_uint32(value):
    """Validate uint32 range: 0 to 4,294,967,295"""
    if isinstance(value, float):
        raise ValueError(f"Invalid uint32: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (0 <= num <= _UINT32_MAX):
        raise ValueError(f"Value {num} outside uint32 range")
    return value

def _validate_uint64(value):
    """Validate uint64 range: 0 to 18,446,744,073,709,551,615"""
    if isinstance(value, float):
        raise ValueError(f"Invalid uint64: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (0 <= num <= _UINT64_MAX):
        raise ValueError(f"Value {num} outside uint64 range")
    return value

def _validate_byte(value):
    """Validate base64-encoded string (standard or URL-safe)"""
    if not isinstance(value, str):
        raise ValueError(f"Invalid byte: expected string, got {type(value).__name__}")
    try:
        standard_b64 = value.replace('-', '+').replace('_', '/')
        padding = len(standard_b64) % 4
        if padding:
            standard_b64 += '=' * (4 - padding)
        base64.b64decode(standard_b64, validate=True)
    except Exception as e:
        display = value[:50] + '...' if len(value) > 50 else value
        raise ValueError(f"Invalid base64: '{display}'") from e
    return value

def _validate_binary(value):
    """Validate binary data (accepts string or bytes)"""
    if isinstance(value, (bytes, str)):
        return value
    raise ValueError(f"Invalid binary: expected string or bytes, got {type(value).__name__}")

def _validate_date_time(value):
    """Validate RFC 3339 / ISO 8601 date-time: YYYY-MM-DDTHH:MM:SS[.fraction][Z|+/-HH:MM|+/-HHMM]"""
    if not isinstance(value, str):
        raise ValueError("Invalid date-time: expected string")
    pattern = r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid RFC 3339 date-time")
    return value

def _validate_date(value):
    """Validate RFC 3339 full-date: YYYY-MM-DD"""
    if not isinstance(value, str):
        raise ValueError("Invalid date: expected string")
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid date (YYYY-MM-DD)")
    return value

def _validate_time(value):
    """Validate RFC 3339 time: HH:MM:SS[.fraction][Z|+/-HH:MM]"""
    if not isinstance(value, str):
        raise ValueError("Invalid time: expected string")
    pattern = r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(\.\d+)?(Z|[+-]([01]\d|2[0-3]):[0-5]\d)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid RFC 3339 time")
    return value

def _validate_duration(value):
    """Validate ISO 8601 duration: P[n]Y[n]M[n]DT[n]H[n]M[n]S or P[n]W"""
    if not isinstance(value, str):
        raise ValueError("Invalid duration: expected string")
    date_pattern = r'^P(?=\d|T)(\d+Y)?(\d+M)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$'
    week_pattern = r'^P\d+W$'
    if not (re.match(date_pattern, value) or re.match(week_pattern, value)):
        raise ValueError(f"'{value}' is not valid ISO 8601 duration")
    return value

def _validate_email(value):
    """Validate email address (RFC 5322 simplified)"""
    if not isinstance(value, str):
        raise ValueError("Invalid email: expected string")
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)+$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid email")
    return value

def _validate_hostname(value):
    """Validate hostname (RFC 1123)"""
    if not isinstance(value, str):
        raise ValueError("Invalid hostname: expected string")
    if not value or len(value) > 253:
        raise ValueError(f"Hostname must be 1-253 characters, got {len(value)}")
    labels = value.rstrip('.').split('.')
    for label in labels:
        if not label or len(label) > 63:
            raise ValueError(f"Invalid hostname label: '{label}'")
        if label.startswith('-') or label.endswith('-'):
            raise ValueError(f"Hostname label '{label}' cannot start or end with hyphen")
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$|^[a-zA-Z0-9]$', label):
            raise ValueError(f"Hostname label '{label}' contains invalid characters")
    return value

def _validate_ipv4(value):
    """Validate IPv4 address"""
    if not isinstance(value, str):
        raise ValueError("Invalid ipv4: expected string")
    pattern = r'^((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid IPv4 address")
    return value

def _validate_ipv6(value):
    """Validate IPv6 address"""
    if not isinstance(value, str):
        raise ValueError("Invalid ipv6: expected string")
    try:
        ipaddress.IPv6Address(value)
    except Exception as e:
        raise ValueError(f"'{value}' is not a valid IPv6 address") from e
    return value

def _validate_uri(value):
    """Validate URI (RFC 3986)"""
    if not isinstance(value, str):
        raise ValueError("Invalid uri: expected string")
    result = urlparse(value)
    if not result.scheme:
        raise ValueError("URI must have a scheme")
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*$', result.scheme):
        raise ValueError(f"Invalid URI scheme: '{result.scheme}'")
    if not (result.netloc or result.path or result.query or result.fragment):
        raise ValueError("URI must have content after scheme")
    return value

def _validate_uri_reference(value):
    """Validate URI-reference (RFC 3986) - URI or relative reference"""
    if not isinstance(value, str):
        raise ValueError("Invalid uri-reference: expected string")
    if not value:
        return value
    result = urlparse(value)
    if result.scheme:
        return _validate_uri(value)
    return value

def _validate_uuid(value):
    """Validate UUID"""
    if not isinstance(value, str):
        raise ValueError("Invalid uuid: expected string")
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid UUID")
    return value

def _validate_uri_template(value):
    """Validate URI Template (RFC 6570)

    URI templates contain expressions enclosed in braces that are expanded
    to produce URIs. Examples:
    - https://api.example.com/users/{id}
    - https://api.example.com/repos/{owner}/{repo}
    - https://api.example.com{/path*}
    """
    if not isinstance(value, str):
        raise ValueError("Invalid uri-template: expected string")
    if not value:
        return value
    # RFC 6570 expression pattern: {[operator][var-list]}
    # Operators: + # . / ; ? & = , ! @ |
    # Variable modifiers: :prefix *
    expr_pattern = r'\{[+#./;?&=,!@|]?[a-zA-Z0-9_]+(?::[0-9]+|\*)?(?:,[a-zA-Z0-9_]+(?::[0-9]+|\*)?)*\}'
    # Check that all braces are properly balanced and contain valid expressions
    temp = re.sub(expr_pattern, '', value)
    if '{' in temp or '}' in temp:
        # Check for unmatched or malformed expressions
        if temp.count('{') != temp.count('}'):
            raise ValueError(f"'{value}' has unbalanced braces in URI template")
        raise ValueError(f"'{value}' contains invalid URI template expression")
    return value

def _validate_unix_time(value):
    """Validate Unix timestamp (seconds since epoch)

    Accepts integer or numeric string representing seconds since 1970-01-01T00:00:00Z.
    Valid range: 0 to 253402300799 (9999-12-31T23:59:59Z)
    """
    if isinstance(value, float):
        # Allow float but warn about potential precision loss
        if value != int(value):
            raise ValueError(f"Unix timestamp '{value}' has fractional seconds; use milliseconds format or integer")
        value = int(value)
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError as e:
            raise ValueError(f"'{value}' is not a valid Unix timestamp") from e
    if not isinstance(value, int):
        raise ValueError(f"Invalid unix-time: expected integer, got {type(value).__name__}")
    # Reasonable range: 1970-01-01 to 9999-12-31
    if not (0 <= value <= 253402300799):
        raise ValueError(f"Unix timestamp {value} outside valid range (0 to 253402300799)")
    return value

def _validate_phone_number(value):
    """Validate phone number (E.164 international format)

    E.164 format: +[country code][subscriber number]
    - Starts with +
    - 1-3 digit country code
    - Total length: 8-15 digits (excluding +)

    Examples: +14155552671, +442071234567, +861012345678
    """
    if not isinstance(value, str):
        raise ValueError("Invalid phone-number: expected string")
    # E.164 pattern: + followed by 8-15 digits
    pattern = r'^\+[1-9]\d{7,14}$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid E.164 phone number (expected +[country][number], 8-15 digits)")
    return value

def _validate_json_pointer(value):
    """Validate JSON Pointer (RFC 6901)

    A JSON Pointer is a string of tokens separated by '/'.
    - Empty string "" references the whole document
    - Must start with '/' if non-empty
    - '~' must be escaped as '~0', '/' as '~1'

    Examples: "", "/foo", "/foo/0", "/a~1b", "/m~0n"
    """
    if not isinstance(value, str):
        raise ValueError("Invalid json-pointer: expected string")
    if value == "":
        return value  # Empty string is valid (references root)
    if not value.startswith('/'):
        raise ValueError(f"JSON Pointer '{value}' must start with '/' or be empty")
    # Check for invalid escape sequences (~ not followed by 0 or 1)
    i = 0
    while i < len(value):
        if value[i] == '~':
            if i + 1 >= len(value) or value[i + 1] not in ('0', '1'):
                raise ValueError(f"Invalid escape sequence in JSON Pointer at position {i}")
            i += 2
        else:
            i += 1
    return value

def _validate_regex(value):
    """Validate regular expression (ECMA 262 dialect)

    Validates that the string is a syntactically valid regular expression.
    Note: Python's re module is used, which is mostly compatible with ECMA 262.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid regex: expected string")
    try:
        re.compile(value)
    except re.error as e:
        raise ValueError(f"'{value}' is not a valid regular expression: {e}") from e
    return value

def _validate_date_time_rfc2822(value):
    """Validate RFC 2822 date-time (email format)

    Format: Day, DD Mon YYYY HH:MM:SS +/-HHMM
    Examples:
    - Thu, 21 Dec 2023 16:01:07 +0000
    - Mon, 15 Jan 2024 09:30:00 -0500
    """
    if not isinstance(value, str):
        raise ValueError("Invalid date-time-rfc-2822: expected string")
    # RFC 2822 pattern (simplified)
    pattern = r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} [+-]\d{4}$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid RFC 2822 date-time")
    return value

def _validate_date_time_rfc1123(value):
    """Validate RFC 1123 date-time (HTTP format)

    Format: Day, DD Mon YYYY HH:MM:SS GMT
    Examples:
    - Thu, 21 Dec 2023 16:01:07 GMT
    - Mon, 15 Jan 2024 09:30:00 GMT

    Note: RFC 1123 requires GMT timezone (no offset).
    """
    if not isinstance(value, str):
        raise ValueError("Invalid date-time-rfc1123: expected string")
    pattern = r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} GMT$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid RFC 1123 date-time (must use GMT)")
    return value

def _validate_decimal(value):
    """Validate decimal number (arbitrary precision)

    Accepts string representation of decimal numbers to preserve precision.
    Scientific notation is supported.

    Examples: "123.456", "-0.001", "1.23e10", "1E-5"
    """
    if isinstance(value, (int, float)):
        return value  # Native numeric types are valid
    if not isinstance(value, str):
        raise ValueError(f"Invalid decimal: expected string or number, got {type(value).__name__}")
    # Decimal pattern: optional sign, digits, optional decimal part, optional exponent
    pattern = r'^-?(\d+\.?\d*|\d*\.?\d+)([eE][+-]?\d+)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid decimal number")
    return value

def _validate_iri(value):
    """Validate IRI - Internationalized Resource Identifier (RFC 3987)

    IRIs extend URIs to support Unicode characters.
    This is a simplified validation that checks basic structure.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid iri: expected string")
    result = urlparse(value)
    if not result.scheme:
        raise ValueError("IRI must have a scheme")
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*$', result.scheme):
        raise ValueError(f"Invalid IRI scheme: '{result.scheme}'")
    if not (result.netloc or result.path or result.query or result.fragment):
        raise ValueError("IRI must have content after scheme")
    return value

def _validate_iri_reference(value):
    """Validate IRI-reference (RFC 3987) - IRI or relative reference

    Internationalized equivalent of uri-reference.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid iri-reference: expected string")
    if not value:
        return value
    result = urlparse(value)
    if result.scheme:
        return _validate_iri(value)
    return value

def _validate_int8(value):
    """Validate int8 range: -128 to 127"""
    if isinstance(value, float):
        raise ValueError(f"Invalid int8: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (_INT8_MIN <= num <= _INT8_MAX):
        raise ValueError(f"Value {num} outside int8 range")
    return value

def _validate_int16(value):
    """Validate int16 range: -32,768 to 32,767"""
    if isinstance(value, float):
        raise ValueError(f"Invalid int16: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (_INT16_MIN <= num <= _INT16_MAX):
        raise ValueError(f"Value {num} outside int16 range")
    return value

def _validate_uint8(value):
    """Validate uint8 range: 0 to 255"""
    if isinstance(value, float):
        raise ValueError(f"Invalid uint8: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (0 <= num <= _UINT8_MAX):
        raise ValueError(f"Value {num} outside uint8 range")
    return value

def _validate_uint16(value):
    """Validate uint16 range: 0 to 65,535"""
    if isinstance(value, float):
        raise ValueError(f"Invalid uint16: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (0 <= num <= _UINT16_MAX):
        raise ValueError(f"Value {num} outside uint16 range")
    return value

def _validate_double_int(value):
    """Validate double-int: integer storable in IEEE 754 double without precision loss

    Range: -(2^53-1) to 2^53-1 = -9,007,199,254,740,991 to 9,007,199,254,740,991
    """
    if isinstance(value, float):
        raise ValueError(f"Invalid double-int: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (-_DOUBLE_INT_MAX <= num <= _DOUBLE_INT_MAX):
        raise ValueError(f"Value {num} outside double-int range (±2^53-1)")
    return value

def _validate_date_time_local(value):
    """Validate local date-time (RFC 3339 without timezone)

    Format: YYYY-MM-DDTHH:MM:SS[.fraction] — timezone component forbidden.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid date-time-local: expected string")
    pattern = r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid local date-time (no timezone allowed)")
    return value

def _validate_time_local(value):
    """Validate local time (RFC 3339 without timezone)

    Format: HH:MM:SS[.fraction] — timezone component forbidden.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid time-local: expected string")
    pattern = r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(\.\d+)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not valid local time (no timezone allowed)")
    return value

def _validate_http_date(value):
    """Validate HTTP-date (RFC 7231 §7.1.1.1)

    Accepts three sub-formats:
    - IMF-fixdate: Sun, 06 Nov 1994 08:49:37 GMT
    - RFC 850: Sunday, 06-Nov-94 08:49:37 GMT
    - asctime: Sun Nov  6 08:49:37 1994
    """
    if not isinstance(value, str):
        raise ValueError("Invalid http-date: expected string")
    # IMF-fixdate: Sun, 06 Nov 1994 08:49:37 GMT
    imf_fixdate = r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} GMT$'
    # RFC 850: Sunday, 06-Nov-94 08:49:37 GMT
    rfc850 = r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), \d{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2} \d{2}:\d{2}:\d{2} GMT$'
    # asctime: Sun Nov  6 08:49:37 1994
    asctime = r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ \d]\d \d{2}:\d{2}:\d{2} \d{4}$'
    if not (re.match(imf_fixdate, value) or re.match(rfc850, value) or re.match(asctime, value)):
        raise ValueError(f"'{value}' is not a valid HTTP-date")
    return value

def _validate_decimal128(value):
    """Validate IEEE 754 decimal128 (34 significant digits)

    Accepts number or string. String may include NaN, -INF, INF.
    """
    if isinstance(value, (int, float)):
        s = str(value)
        digits = s.lstrip('-').replace('.', '').lstrip('0')
        if len(digits) > 34:
            raise ValueError(f"decimal128 allows max 34 significant digits, got {len(digits)}")
        return value
    if not isinstance(value, str):
        raise ValueError(f"Invalid decimal128: expected string or number, got {type(value).__name__}")
    if value in ('NaN', '-NaN', 'INF', '-INF', '+INF', 'Infinity', '-Infinity', '+Infinity'):
        return value
    pattern = r'^-?(\d+\.?\d*|\d*\.?\d+)([eE][+-]?\d+)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid decimal128 value")
    digits = re.sub(r'[eE][+-]?\d+$', '', value).lstrip('-').replace('.', '').lstrip('0')
    if len(digits) > 34:
        raise ValueError(f"decimal128 allows max 34 significant digits, got {len(digits)}")
    return value

def _validate_commonmark(value):
    """Validate CommonMark-formatted text (content format, string check only)"""
    if not isinstance(value, str):
        raise ValueError(f"Invalid commonmark: expected string, got {type(value).__name__}")
    return value

def _validate_html(value):
    """Validate HTML-formatted text (content format, string check only)"""
    if not isinstance(value, str):
        raise ValueError(f"Invalid html: expected string, got {type(value).__name__}")
    return value

def _validate_char(value):
    """Validate single character"""
    if not isinstance(value, str):
        raise ValueError(f"Invalid char: expected string, got {type(value).__name__}")
    if len(value) != 1:
        raise ValueError(f"char format requires exactly 1 character, got {len(value)}")
    return value

def _validate_idn_email(value):
    """Validate internationalized email address (RFC 6531)

    Extends RFC 5322 email to accept non-ASCII characters in local-part and domain.
    """
    if not isinstance(value, str):
        raise ValueError("Invalid idn-email: expected string")
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid internationalized email")
    return value

def _validate_idn_hostname(value):
    """Validate internationalized hostname (RFC 5890)

    Extends RFC 1123 hostname to accept non-ASCII labels (A-labels/U-labels).
    """
    if not isinstance(value, str):
        raise ValueError("Invalid idn-hostname: expected string")
    if not value or len(value) > 253:
        raise ValueError(f"Hostname must be 1-253 characters, got {len(value)}")
    labels = value.rstrip('.').split('.')
    for label in labels:
        if not label or len(label) > 63:
            raise ValueError(f"Invalid hostname label: '{label}'")
        if label.startswith('-') or label.endswith('-'):
            raise ValueError(f"Hostname label '{label}' cannot start or end with hyphen")
        if label.startswith('xn--'):
            # A-label (Punycode): must be ASCII alphanumeric + hyphens
            if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', label):
                raise ValueError(f"Invalid A-label: '{label}'")
        else:
            # U-label or ASCII: allow word chars (including Unicode) and hyphens
            if not re.match(r'^[\w][\w-]*[\w]$|^[\w]$', label, re.UNICODE):
                raise ValueError(f"Invalid hostname label: '{label}'")
    return value

def _validate_relative_json_pointer(value):
    """Validate Relative JSON Pointer (draft)

    Format: non-negative-integer followed by either a JSON Pointer or '#'.
    Examples: "0", "1/foo", "2/bar/0", "0#"
    """
    if not isinstance(value, str):
        raise ValueError("Invalid relative-json-pointer: expected string")
    pattern = r'^(0|[1-9]\d*)(#|(/[^/]*)*)?$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid Relative JSON Pointer")
    return value

def _validate_media_range(value):
    """Validate media-range (RFC 9110)

    Format: type "/" subtype with optional parameters. Wildcards supported.
    Examples: "text/html", "application/json", "text/*", "*/*", "text/html;charset=utf-8"
    """
    if not isinstance(value, str):
        raise ValueError("Invalid media-range: expected string")
    pattern = r'^(\*|[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_.+]*)/(\*|[a-zA-Z0-9][a-zA-Z0-9!#$&\-^_.+]*)(;\s*[a-zA-Z0-9!#$&\-^_.+]+=("[^"]*"|[^\s;,]*))*$'
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid media-range")
    return value

def _validate_sf_integer(value):
    """Validate Structured Fields integer (RFC 8941)

    Range: -999,999,999,999,999 to 999,999,999,999,999 (15 digits).
    """
    if isinstance(value, float):
        raise ValueError(f"Invalid sf-integer: '{value}' is float, expected integer")
    num = int(value) if isinstance(value, str) else value
    if not (-_SF_INTEGER_MAX <= num <= _SF_INTEGER_MAX):
        raise ValueError(f"Value {num} outside sf-integer range (±999,999,999,999,999)")
    return value

def _validate_sf_decimal(value):
    """Validate Structured Fields decimal (RFC 8941)

    Up to 12 integer digits + '.' + up to 3 fractional digits.
    """
    if isinstance(value, (int, float)):
        s = str(value)
    elif isinstance(value, str):
        s = value
    else:
        raise ValueError(f"Invalid sf-decimal: expected number or string, got {type(value).__name__}")
    pattern = r'^-?\d{1,12}(\.\d{1,3})?$'
    if not re.match(pattern, s):
        raise ValueError(f"'{value}' is not a valid sf-decimal (max 12 integer + 3 fractional digits)")
    return value

def _validate_sf_string(value):
    """Validate Structured Fields string (RFC 8941)

    Printable ASCII only (%x20-%x7E).
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid sf-string: expected string, got {type(value).__name__}")
    for ch in value:
        if not ('\x20' <= ch <= '\x7e'):
            raise ValueError(f"sf-string contains non-printable ASCII: {ch!r}")
    return value

def _validate_sf_token(value):
    r"""Validate Structured Fields token (RFC 8941)

    Pattern: (ALPHA / "*") *(tchar / ":" / "/")
    tchar = "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid sf-token: expected string, got {type(value).__name__}")
    pattern = r"^[A-Za-z*][A-Za-z0-9!#$%&'*+\-.^_`|~:/]*$"
    if not re.match(pattern, value):
        raise ValueError(f"'{value}' is not a valid sf-token")
    return value

def _validate_sf_boolean(value):
    """Validate Structured Fields boolean (RFC 8941)

    Exact match: '?0' or '?1'.
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid sf-boolean: expected string, got {type(value).__name__}")
    if value not in ('?0', '?1'):
        raise ValueError(f"sf-boolean must be '?0' or '?1', got '{value}'")
    return value

def _validate_sf_binary(value):
    """Validate Structured Fields binary (RFC 8941)

    Format: ':' + base64 content + ':'.
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid sf-binary: expected string, got {type(value).__name__}")
    if not value.startswith(':') or not value.endswith(':') or len(value) < 2:
        raise ValueError("sf-binary must be enclosed in ':' delimiters")
    inner = value[1:-1]
    if inner and not re.match(r'^[A-Za-z0-9+/]*=*$', inner):
        raise ValueError("sf-binary contains invalid base64 content")
    return value

# Format validator registry
# Full OAS Format Registry coverage (https://spec.openapis.org/registry/format/)
# plus custom extensions for common API patterns.
FORMAT_VALIDATORS: dict[str, Any] = {
    # ── OAS Format Registry: Integer formats ──
    "int8": _validate_int8,
    "int16": _validate_int16,
    "int32": _validate_int32,
    "int64": _validate_int64,
    "uint8": _validate_uint8,
    "uint16": _validate_uint16,
    "uint32": _validate_uint32,
    "uint64": _validate_uint64,
    "double-int": _validate_double_int,
    # ── OAS Format Registry: Number formats ──
    "float": lambda v: v,   # Python-native, no additional validation
    "double": lambda v: v,  # Python-native, no additional validation
    "decimal": _validate_decimal,
    "decimal128": _validate_decimal128,
    # ── OAS Format Registry: Binary/encoding formats ──
    "byte": _validate_byte,
    "binary": _validate_binary,
    "base64url": _validate_byte,  # Deprecated registry alias — our byte validator handles URL-safe
    # ── OAS Format Registry: Date/time formats ──
    "date-time": _validate_date_time,
    "date": _validate_date,
    "time": _validate_time,
    "duration": _validate_duration,
    "date-time-local": _validate_date_time_local,
    "time-local": _validate_time_local,
    "http-date": _validate_http_date,
    "unixtime": _validate_unix_time,
    # ── OAS Format Registry: String/text formats ──
    "password": lambda v: v,  # UI hint only per OAS spec — no validation
    "commonmark": _validate_commonmark,
    "html": _validate_html,
    "char": _validate_char,
    "regex": _validate_regex,
    # ── OAS Format Registry: Email/hostname formats ──
    "email": _validate_email,
    "idn-email": _validate_idn_email,
    "hostname": _validate_hostname,
    "idn-hostname": _validate_idn_hostname,
    # ── OAS Format Registry: Network/identifier formats ──
    "ipv4": _validate_ipv4,
    "ipv6": _validate_ipv6,
    "uri": _validate_uri,
    "uri-reference": _validate_uri_reference,
    "uri-template": _validate_uri_template,
    "iri": _validate_iri,
    "iri-reference": _validate_iri_reference,
    "uuid": _validate_uuid,
    "json-pointer": _validate_json_pointer,
    "relative-json-pointer": _validate_relative_json_pointer,
    "media-range": _validate_media_range,
    # ── OAS Format Registry: Structured Fields (RFC 8941) ──
    "sf-integer": _validate_sf_integer,
    "sf-decimal": _validate_sf_decimal,
    "sf-string": _validate_sf_string,
    "sf-token": _validate_sf_token,
    "sf-boolean": _validate_sf_boolean,
    "sf-binary": _validate_sf_binary,
    # ── Custom formats (not in registry) ──
    "date-time-rfc-2822": _validate_date_time_rfc2822,
    "date-time-rfc1123": _validate_date_time_rfc1123,
    "unix-time": _validate_unix_time,
    "timestamp": _validate_unix_time,  # Alias for unix-time
    "phone-number": _validate_phone_number,
    "url": _validate_uri,  # Alias for uri
}

# ============================================================================
# Base Classes
# ============================================================================

class StrictModel(BaseModel):
    """
    Base model with strict validation.

    - Rejects unknown fields (extra='forbid')
    - Validates json_schema_extra format specifications
    - Collapses to None when all fields are None (nested model cleanup)
    - Used for request models, component schemas, and schemas with unevaluatedProperties: false
    """
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    @model_serializer(mode='wrap')
    def _serialize_or_none(self, handler) -> dict[str, Any] | None:
        """Collapse to None when all fields are None.

        Prevents empty nested objects (e.g. {"outOfOfficeProperties": {}}) from
        being sent to upstream APIs. When all fields in a nested model are None,
        the model serializes as None so that exclude_none=True on the parent
        drops it entirely.
        """
        data = handler(self)
        if isinstance(data, dict) and all(v is None for v in data.values()):
            return None
        return data

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to post-filter None values produced by nested serializers.

        Pydantic's exclude_none checks field values before serializers run,
        so nested models that collapse to None via _serialize_or_none are not
        excluded by the built-in exclude_none. This override applies a second
        pass to remove them.
        """
        data = super().model_dump(**kwargs)
        if not isinstance(data, dict):
            return {}
        if kwargs.get('exclude_none'):
            return {k: v for k, v in data.items() if v is not None}
        return data

    @model_validator(mode='after')
    def validate_formats(self) -> StrictModel:
        """Validate all fields that have a format specified in json_schema_extra."""
        for field_name, field_info in self.__class__.model_fields.items():
            json_extra = field_info.json_schema_extra
            if not json_extra or not isinstance(json_extra, dict):
                continue

            format_name = json_extra.get('format')
            if not format_name or not isinstance(format_name, str):
                continue

            value = getattr(self, field_name)
            if value is None:
                continue

            if format_name in FORMAT_VALIDATORS:
                try:
                    FORMAT_VALIDATORS[format_name](value)
                except ValueError as e:
                    raise ValueError(f"Field '{field_name}' format validation failed: {e}") from e

        return self

class PermissiveModel(BaseModel):
    """
    Base model with permissive validation.

    - Allows unknown fields (extra='allow')
    - Validates json_schema_extra format specifications
    - Collapses to None when all fields are None (nested model cleanup)
    - Used for response models, components in response context,
      request models without additionalProperties: false,
      and schemas with unevaluatedProperties: true
    """
    model_config = ConfigDict(
        extra='allow',
    )

    @model_serializer(mode='wrap')
    def _serialize_or_none(self, handler) -> dict[str, Any] | None:
        """Collapse to None when all fields are None.

        Prevents empty nested objects (e.g. {"outOfOfficeProperties": {}}) from
        being sent to upstream APIs. When all fields in a nested model are None,
        the model serializes as None so that exclude_none=True on the parent
        drops it entirely.
        """
        data = handler(self)
        if isinstance(data, dict) and all(v is None for v in data.values()):
            return None
        return data

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to post-filter None values produced by nested serializers.

        Pydantic's exclude_none checks field values before serializers run,
        so nested models that collapse to None via _serialize_or_none are not
        excluded by the built-in exclude_none. This override applies a second
        pass to remove them.
        """
        data = super().model_dump(**kwargs)
        if not isinstance(data, dict):
            return {}
        if kwargs.get('exclude_none'):
            return {k: v for k, v in data.items() if v is not None}
        return data

    @model_validator(mode='after')
    def validate_formats(self) -> PermissiveModel:
        """Validate all fields that have a format specified in json_schema_extra."""
        for field_name, field_info in self.__class__.model_fields.items():
            json_extra = field_info.json_schema_extra
            if not json_extra or not isinstance(json_extra, dict):
                continue

            format_name = json_extra.get('format')
            if not format_name or not isinstance(format_name, str):
                continue

            value = getattr(self, field_name)
            if value is None:
                continue

            if format_name in FORMAT_VALIDATORS:
                try:
                    FORMAT_VALIDATORS[format_name](value)
                except ValueError as e:
                    raise ValueError(f"Field '{field_name}' format validation failed: {e}") from e

        return self

# ============================================================================
# Utility Models
# ============================================================================

class SuccessResponse(BaseModel):
    """
    Success confirmation for operations without response content.

    Used for DELETE, PUT, PATCH, and POST operations that return empty response
    bodies (status 200/201/204 with no content schema).
    """
    message: str

    model_config = ConfigDict(
        frozen=True,
        extra='forbid',
        str_strip_whitespace=True,
        validate_assignment=True,
    )
