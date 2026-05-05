"""
Authentication module for PDF.co API MCP server.

Generated: 2026-05-05 15:49:30 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

__all__ = [
    "APIKeyAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class APIKeyAuth:
    """
    API Key authentication for PDF.co API.

    Supports header, query parameter, cookie, and path-based API key injection.
    Configure location and parameter name via constructor arguments.
    """

    def __init__(self, env_var: str = "API_KEY", location: str = "header",
                 param_name: str = "Authorization", prefix: str = ""):
        """Initialize API key authentication from environment variable.

        Args:
            env_var: Environment variable name containing the API key.
            location: Where to inject the key - 'header', 'query', 'cookie', or 'path'.
            param_name: Name of the header, query parameter, cookie, or path placeholder.
            prefix: Optional prefix before the key value (e.g., 'Bearer').
        """
        self.location = location
        self.param_name = param_name
        self.prefix = prefix
        self.api_key = os.getenv(env_var, "").strip()

        # Check for empty API key
        if not self.api_key:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable API Key auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "bot placeholder"]
        api_key_lower = self.api_key.lower()

        if any(p in api_key_lower for p in placeholders):
            raise ValueError(
                f"API key appears to be a placeholder ({self.api_key[:20]}...). "
                "Please set a real API key or leave empty to disable API Key auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        if self.location != "header":
            return {}
        if self.param_name == "Authorization":
            # Use explicit prefix if set; otherwise send the key raw (no Bearer assumption —
            # apiKey schemes that happen to use the Authorization header don't imply Bearer)
            prefix = self.prefix + " " if self.prefix else ""
            return {"Authorization": f"{prefix}{self.api_key}"}
        value = f"{self.prefix} {self.api_key}" if self.prefix else self.api_key
        return {self.param_name: value}

    def get_auth_params(self) -> dict[str, str]:
        """Get authentication query parameters."""
        if self.location != "query":
            return {}
        return {self.param_name: self.api_key}

    def get_auth_cookies(self) -> dict[str, str]:
        """Get authentication cookies."""
        if self.location != "cookie":
            return {}
        return {self.param_name: self.api_key}

    def get_auth_path_params(self) -> dict[str, str]:
        """Get authentication path parameters for URL template substitution."""
        if self.location != "path":
            return {}
        return {self.param_name: self.api_key}


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "extract_invoice_data": [["ApiKeyAuth"]],
    "extract_data_from_pdf_document": [["ApiKeyAuth"]],
    "list_document_parser_templates": [["ApiKeyAuth"]],
    "get_document_parser_template": [["ApiKeyAuth"]],
    "extract_pdf_attachments": [["ApiKeyAuth"]],
    "add_content_to_pdf": [["ApiKeyAuth"]],
    "replace_text_in_pdf": [["ApiKeyAuth"]],
    "replace_text_with_image_in_pdf": [["ApiKeyAuth"]],
    "delete_text_from_pdf": [["ApiKeyAuth"]],
    "convert_pdf_to_csv": [["ApiKeyAuth"]],
    "convert_pdf_to_json": [["ApiKeyAuth"]],
    "convert_pdf_to_json_with_ai": [["ApiKeyAuth"]],
    "convert_pdf_to_text": [["ApiKeyAuth"]],
    "convert_pdf_to_text_fast": [["ApiKeyAuth"]],
    "convert_pdf_to_xls": [["ApiKeyAuth"]],
    "convert_pdf_to_xlsx": [["ApiKeyAuth"]],
    "convert_pdf_to_xml": [["ApiKeyAuth"]],
    "convert_pdf_to_html": [["ApiKeyAuth"]],
    "convert_pdf_to_jpg": [["ApiKeyAuth"]],
    "convert_pdf_to_png": [["ApiKeyAuth"]],
    "convert_pdf_to_webp": [["ApiKeyAuth"]],
    "convert_pdf_to_tiff": [["ApiKeyAuth"]],
    "convert_pdf_from_doc": [["ApiKeyAuth"]],
    "convert_pdf_from_csv": [["ApiKeyAuth"]],
    "convert_pdf_from_image": [["ApiKeyAuth"]],
    "convert_pdf_from_url": [["ApiKeyAuth"]],
    "convert_pdf_from_html": [["ApiKeyAuth"]],
    "list_templates_html": [["ApiKeyAuth"]],
    "get_html_template": [["ApiKeyAuth"]],
    "convert_email_to_pdf": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_csv": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_json": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_html": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_text": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_xml": [["ApiKeyAuth"]],
    "convert_spreadsheet_to_pdf": [["ApiKeyAuth"]],
    "merge_pdfs": [["ApiKeyAuth"]],
    "merge_documents_to_pdf": [["ApiKeyAuth"]],
    "split_pdf": [["ApiKeyAuth"]],
    "split_pdf_by_text_search": [["ApiKeyAuth"]],
    "get_pdf_form_fields": [["ApiKeyAuth"]],
    "search_pdf_text": [["ApiKeyAuth"]],
    "search_tables_in_pdf": [["ApiKeyAuth"]],
    "make_pdf_searchable": [["ApiKeyAuth"]],
    "convert_pdf_to_unsearchable": [["ApiKeyAuth"]],
    "compress_pdf": [["ApiKeyAuth"]],
    "get_pdf_info": [["ApiKeyAuth"]],
    "get_job_status": [["ApiKeyAuth"]],
    "get_account_credit_balance": [["ApiKeyAuth"]],
    "classify_document": [["ApiKeyAuth"]],
    "send_email_with_attachment": [["ApiKeyAuth"]],
    "extract_email_components": [["ApiKeyAuth"]],
    "extract_email_attachments": [["ApiKeyAuth"]],
    "delete_temporary_file": [["ApiKeyAuth"]],
    "upload_file_from_url": [["ApiKeyAuth"]],
    "upload_file_from_url_direct": [["ApiKeyAuth"]],
    "create_file_from_base64": [["ApiKeyAuth"]],
    "get_file_upload_presigned_url": [["ApiKeyAuth"]],
    "add_password_to_pdf": [["ApiKeyAuth"]],
    "remove_pdf_password": [["ApiKeyAuth"]],
    "delete_pdf_pages": [["ApiKeyAuth"]],
    "rotate_pdf_pages": [["ApiKeyAuth"]],
    "auto_rotate_pdf_pages": [["ApiKeyAuth"]],
    "generate_barcode": [["ApiKeyAuth"]],
    "read_barcodes_from_url": [["ApiKeyAuth"]]
}
