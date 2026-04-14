"""
Authentication module for ConvertAPI MCP server.

Generated: 2026-04-14 18:18:45 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = [
    "BearerTokenAuth",
    "JWTBearerAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BearerTokenAuth:
    """
    Bearer token authentication for ConvertAPI.

    Configuration:
        Provide the raw token in the environment variable.
        The authorization scheme prefix is automatically inserted.
    """

    def __init__(self, env_var: str = "BEARER_TOKEN", token_format: str = "Bearer"):
        """Initialize bearer token authentication from environment variable.

        Args:
            env_var: Environment variable name containing the bearer token.
            token_format: Authorization scheme prefix (e.g., 'Bearer').
        """
        self.token_format = token_format
        self.token = os.getenv(env_var, "").strip()

        # Check for empty token
        if not self.token:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable Bearer Token auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "sk_test_placeholder"]
        token_lower = self.token.lower()

        if any(p in token_lower for p in placeholders):
            raise ValueError(
                f"Bearer token appears to be a placeholder ({self.token[:20]}...). "
                "Please set a real token or leave empty to disable Bearer Token auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            'Authorization': f'{self.token_format} {self.token}'
        }

class JWTBearerAuth:
    """
    JWT Bearer authentication for ConvertAPI.

    Generates short-lived JWTs signed with a private key (RFC 7523).
    Supports two modes:
    - Direct JWT: signed token used directly as Bearer token (e.g. GitHub Apps)
    - Token exchange: signed JWT exchanged at a token URL for an access token
      (e.g. Google service accounts)

    Configuration (environment variables):
        - JWT_PRIVATE_KEY: Absolute path to .pem file OR inline PEM key (required).
          Inline: encode newlines as literal \\n for single-line .env storage.
        - JWT_ISSUER_ID: Issuer claim value — App ID, Team ID, etc. (required)
        - JWT_ALGORITHM: Signing algorithm (default: RS256)
        - JWT_EXPIRY: Token lifetime in seconds (default: 600)
        - JWT_AUDIENCE: Audience claim (optional)
        - JWT_KEY_ID: Key ID for JWT header kid field (optional)
        - JWT_TOKEN_URL: Token exchange endpoint (optional — if set, exchanges JWT for access token)
        - JWT_SCOPES: Comma-separated scopes for token exchange (optional)
    """

    def __init__(self):
        """Initialize JWT Bearer authentication from environment variables."""
        import jwt as pyjwt  # PyJWT

        self._pyjwt = pyjwt

        # Required
        raw_key = os.getenv("JWT_PRIVATE_KEY", "").strip()
        if not raw_key:
            raise ValueError(
                "JWT_PRIVATE_KEY environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )
        # Support both inline PEM and file path:
        # - Starts with "-----BEGIN" → inline PEM (newlines may be escaped as \n)
        # - Otherwise → treat as file path to .pem file
        if raw_key.startswith("-----"):
            self._private_key = raw_key.replace("\\n", "\n")
        else:
            key_path = Path(raw_key)
            # Resolve relative paths against the server directory (where .env lives)
            if not key_path.is_absolute():
                key_path = Path(__file__).parent / key_path
            if not key_path.exists():
                raise ValueError(
                    f"JWT_PRIVATE_KEY points to '{raw_key}' but file not found. "
                    "Provide either an inline PEM key or a valid file path."
                )
            self._private_key = key_path.read_text()

        self._issuer = os.getenv("JWT_ISSUER_ID", "").strip()
        if not self._issuer:
            raise ValueError(
                "JWT_ISSUER_ID environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )

        # Optional — empty values fall back to defaults
        self._algorithm = os.getenv("JWT_ALGORITHM", "").strip() or "RS256"
        self._expiry = int(os.getenv("JWT_EXPIRY", "").strip() or "600")
        self._audience = os.getenv("JWT_AUDIENCE", "").strip() or None
        self._key_id = os.getenv("JWT_KEY_ID", "").strip() or None
        self._token_url = os.getenv("JWT_TOKEN_URL", "").strip() or None
        self._scopes = os.getenv("JWT_SCOPES", "").strip() or None

        # Token cache
        self._cached_token: str | None = None
        self._token_expires_at: float = 0

    def _generate_jwt(self) -> str:
        """Generate a signed JWT."""
        now = int(time.time())
        payload: dict = {
            "iat": now,
            "exp": now + self._expiry,
            "iss": self._issuer,
        }
        if self._audience:
            payload["aud"] = self._audience

        headers: dict = {}
        if self._key_id:
            headers["kid"] = self._key_id

        return self._pyjwt.encode(
            payload,
            self._private_key,
            algorithm=self._algorithm,
            headers=headers or None,
        )

    def _is_token_expired(self) -> bool:
        """Check if cached token is expired or near-expiry (30s buffer)."""
        return time.time() >= (self._token_expires_at - 30)

    def _get_token(self) -> str:
        """Get a valid token, generating/exchanging as needed."""
        if self._cached_token and not self._is_token_expired():
            return self._cached_token

        jwt_token = self._generate_jwt()

        if self._token_url:
            # Exchange JWT for access token at token endpoint
            import httpx
            data: dict = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_token,
            }
            if self._scopes:
                data["scope"] = self._scopes

            response = httpx.post(self._token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            token = token_data["access_token"]
            expires_in = token_data.get("expires_in", self._expiry)
            self._token_expires_at = time.time() + expires_in
        else:
            # Direct JWT — use as-is
            token = jwt_token
            self._token_expires_at = time.time() + self._expiry

        self._cached_token = token
        return token

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        return {"Authorization": f"Bearer {self._get_token()}"}

    def clear_token(self) -> None:
        """Clear cached token (called on 401 response)."""
        self._cached_token = None
        self._token_expires_at = 0


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "upload_file": [],
    "download_file": [],
    "delete_file": [],
    "get_file_metadata": [],
    "get_account": [["secret"]],
    "get_usage_statistics": [["secret"]],
    "convert_image_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_ai_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_ai_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_ai_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_image_bmp_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_image_bmp_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_bmp_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_svg_bmp": [["secret"], ["token"], ["jwt"]],
    "convert_image_bmp_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_image_bmp_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_csv_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_csv_to_xlsx": [["secret"], ["token"], ["jwt"]],
    "convert_djvu_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_djvu_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_djvu_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_djvu_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_djvu_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_docx": [["secret"], ["token"], ["jwt"]],
    "compare_docx_documents": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_html": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_image": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_markdown": [["secret"], ["token"], ["jwt"]],
    "convert_document_docx_to_odt": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_image_png": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_protected_word": [["secret"], ["token"], ["jwt"]],
    "convert_document_docx_to_rtf": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_text": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_docx_to_xml": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_dotx_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_dwf_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_dwg_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_dxf_to_webp": [["secret"], ["token"], ["jwt"]],
    "extract_email_attachments": [["secret"], ["token"], ["jwt"]],
    "extract_email_metadata": [["secret"], ["token"], ["jwt"]],
    "convert_email_to_image": [["secret"], ["token"], ["jwt"]],
    "convert_eml_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_email_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_eml_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_eml_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_eps_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_eps_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_eps_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_eps_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_epub_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_epub_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_epub_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_epub_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_epub_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_file_to_pdf": [["secret"], ["token"], ["jwt"]],
    "compress_files_to_archive": [["secret"], ["token"], ["jwt"]],
    "convert_gif_animation": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_gif_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_heic_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_image_heic_to_jxl": [["secret"], ["token"], ["jwt"]],
    "convert_heic_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_heic_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_heic_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_heic_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_heic_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_image_heic_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_heif_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_heif_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_markdown": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_text": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_spreadsheet": [["secret"], ["token"], ["jwt"]],
    "convert_html_to_xlsx": [["secret"], ["token"], ["jwt"]],
    "convert_image_ico_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_ico_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_image_ico_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_icon_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_image_ico_to_webp": [["secret"], ["token"], ["jwt"]],
    "join_images": [["secret"], ["token"], ["jwt"]],
    "convert_images_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_jfif_to_pdf": [["secret"], ["token"], ["jwt"]],
    "compress_jpg_image": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_gif": [["secret"], ["token"], ["jwt"]],
    "convert_image_format": [["secret"], ["token"], ["jwt"]],
    "convert_image_jpg_to_jxl": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_pdf_jpeg": [["secret"], ["token"], ["jwt"]],
    "convert_image_jpg_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_jpg_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_svg_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_tiff": [["secret"], ["token"], ["jwt"]],
    "extract_text_from_image": [["secret"], ["token"], ["jwt"]],
    "convert_image_jpg_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_pptx": [["secret"], ["token"], ["jwt"]],
    "convert_log_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_log_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_log_to_text": [["secret"], ["token"], ["jwt"]],
    "convert_markdown_to_html": [["secret"], ["token"], ["jwt"]],
    "convert_markdown_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_mhtml_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_mobi_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_mobi_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_mobi_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_mobi_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_email_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_msg_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_email_to_png_outlook": [["secret"], ["token"], ["jwt"]],
    "convert_msg_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_message_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_numbers_to_csv": [["secret"], ["token"], ["jwt"]],
    "convert_numbers_to_xlsx": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_jpg_spreadsheet": [["secret"], ["token"], ["jwt"]],
    "convert_odc_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_odc_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_jpg_formula": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_pdf_odf": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_odg_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_odp_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_image": [["secret"], ["token"], ["jwt"]],
    "convert_ods_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_ods_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_document_odt_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_jpg_text": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_pdf_odt": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_png_text": [["secret"], ["token"], ["jwt"]],
    "convert_document_odt_to_txt": [["secret"], ["token"], ["jwt"]],
    "convert_document_to_xml": [["secret"], ["token"], ["jwt"]],
    "convert_office_document_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pages_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_pages_to_text": [["secret"], ["token"], ["jwt"]],
    "compress_pdf": [["secret"], ["token"], ["jwt"]],
    "crop_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_csv": [["secret"], ["token"], ["jwt"]],
    "delete_pdf_pages": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_docx": [["secret"], ["token"], ["jwt"]],
    "extract_data_from_pdf": [["secret"], ["token"], ["jwt"]],
    "extract_images_from_pdf": [["secret"], ["token"], ["jwt"]],
    "extract_pdf_form_fields": [["secret"], ["token"], ["jwt"]],
    "import_pdf_with_fdf_form_data": [["secret"], ["token"], ["jwt"]],
    "flatten_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_html": [["secret"], ["token"], ["jwt"]],
    "add_watermark_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_jpg": [["secret"], ["token"], ["jwt"]],
    "merge_pdfs": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_metadata": [["secret"], ["token"], ["jwt"]],
    "extract_text_from_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_pcl": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_pdf": [["secret"], ["token"], ["jwt"]],
    "add_watermark_to_pdf_document": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_pdfa": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_pdfua": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_pptx": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_print": [["secret"], ["token"], ["jwt"]],
    "protect_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_rasterized_image": [["secret"], ["token"], ["jwt"]],
    "redact_pdf": [["secret"], ["token"], ["jwt"]],
    "resize_pdf_pages": [["secret"], ["token"], ["jwt"]],
    "rotate_pdf_pages": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_rtf": [["secret"], ["token"], ["jwt"]],
    "split_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_text_with_watermark": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_tiff_fax": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_text": [["secret"], ["token"], ["jwt"]],
    "unprotect_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_pdf_to_xlsx": [["secret"], ["token"], ["jwt"]],
    "validate_pdfa_conformance": [["secret"], ["token"], ["jwt"]],
    "convert_png_to_gif": [["secret"], ["token"], ["jwt"]],
    "convert_image_png_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_pdf_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_png_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_image_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_png_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_image_png_to_webp": [["secret"], ["token"], ["jwt"]],
    "translate_po_file": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_jpg_template": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_template_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_png_template": [["secret"], ["token"], ["jwt"]],
    "convert_potx_to_pptx": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_template_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_webp_template": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_jpg_slideshow": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_slideshow_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_png_slideshow": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_ppsx_to_pptx": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_slideshow_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_webp_slideshow": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_ppt_to_pptx": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_images": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_images_png": [["secret"], ["token"], ["jwt"]],
    "convert_presentation": [["secret"], ["token"], ["jwt"]],
    "encrypt_presentation": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_presentation_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_prn_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_prn_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_prn_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_prn_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_postscript_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_postscript_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_postscript_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_postscript_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_psd_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_image_psd_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_image_psd_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_psd_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_psd_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_image_psd_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_publication_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_pub_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_pub_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_pub_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_rtf_to_html": [["secret"], ["token"], ["jwt"]],
    "convert_rtf_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_rtf_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_rtf_to_text": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_svg_image": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_svg_to_webp": [["secret"], ["token"], ["jwt"]],
    "fill_template_to_docx": [["secret"], ["token"], ["jwt"]],
    "convert_template_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_tiff_image": [["secret"], ["token"], ["jwt"]],
    "convert_image_tiff_to_webp": [["secret"], ["token"], ["jwt"]],
    "convert_text_to_image": [["secret"], ["token"], ["jwt"]],
    "convert_text_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_vsdx_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_vsdx_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_vsdx_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_vsdx_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_webpage_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_webpage_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_webpage_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_webpage_to_text": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_gif": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_jpg": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_png": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_pnm": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_svg": [["secret"], ["token"], ["jwt"]],
    "convert_webp_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_webp_image": [["secret"], ["token"], ["jwt"]],
    "convert_wpd_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_format": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_xls_to_xlsx": [["secret"], ["token"], ["jwt"]],
    "convert_xlsb_to_csv": [["secret"], ["token"], ["jwt"]],
    "convert_xlsb_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_csv": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_image_xlsx": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_image_png": [["secret"], ["token"], ["jwt"]],
    "encrypt_xlsx_workbook": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_tiff": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_to_image_webp": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_format_modern": [["secret"], ["token"], ["jwt"]],
    "convert_spreadsheet_template_to_pdf": [["secret"], ["token"], ["jwt"]],
    "convert_xml_to_docx": [["secret"], ["token"], ["jwt"]],
    "extract_archive": [["secret"], ["token"], ["jwt"]]
}
