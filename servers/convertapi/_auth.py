"""
Authentication module for ConvertAPI MCP server.

Generated: 2026-04-24 08:32:26 UTC
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
    "BearerTokenAuth",
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "upload_file": [["secret"], ["token"]],
    "download_file": [["secret"], ["token"]],
    "delete_file": [["secret"], ["token"]],
    "get_file_metadata": [["secret"], ["token"]],
    "get_account": [["secret"], ["token"]],
    "get_usage_statistics": [["secret"], ["token"]],
    "convert_image_to_jpg": [["secret"], ["token"]],
    "convert_ai_to_png": [["secret"], ["token"]],
    "convert_image_to_pnm": [["secret"], ["token"]],
    "convert_ai_to_svg": [["secret"], ["token"]],
    "convert_ai_to_tiff": [["secret"], ["token"]],
    "convert_image_to_webp": [["secret"], ["token"]],
    "convert_image_bmp_to_jpg": [["secret"], ["token"]],
    "convert_image_to_pdf": [["secret"], ["token"]],
    "convert_image_bmp_to_png": [["secret"], ["token"]],
    "convert_image_bmp_to_pnm": [["secret"], ["token"]],
    "convert_image_to_svg_bmp": [["secret"], ["token"]],
    "convert_image_bmp_to_tiff": [["secret"], ["token"]],
    "convert_image_bmp_to_webp": [["secret"], ["token"]],
    "convert_csv_to_pdf": [["secret"], ["token"]],
    "convert_csv_to_xlsx": [["secret"], ["token"]],
    "convert_djvu_to_jpg": [["secret"], ["token"]],
    "convert_djvu_to_pdf": [["secret"], ["token"]],
    "convert_djvu_to_png": [["secret"], ["token"]],
    "convert_djvu_to_tiff": [["secret"], ["token"]],
    "convert_djvu_to_webp": [["secret"], ["token"]],
    "convert_document_to_docx": [["secret"], ["token"]],
    "compare_docx_documents": [["secret"], ["token"]],
    "convert_document_to_html": [["secret"], ["token"]],
    "convert_document_to_image": [["secret"], ["token"]],
    "convert_document_to_markdown": [["secret"], ["token"]],
    "convert_document_docx_to_odt": [["secret"], ["token"]],
    "convert_document_to_pdf": [["secret"], ["token"]],
    "convert_document_to_image_png": [["secret"], ["token"]],
    "convert_document_to_protected_word": [["secret"], ["token"]],
    "convert_document_docx_to_rtf": [["secret"], ["token"]],
    "convert_document_to_tiff": [["secret"], ["token"]],
    "convert_document_to_text": [["secret"], ["token"]],
    "convert_document_to_webp": [["secret"], ["token"]],
    "convert_docx_to_xml": [["secret"], ["token"]],
    "convert_document_to_jpg": [["secret"], ["token"]],
    "convert_dotx_to_pdf": [["secret"], ["token"]],
    "convert_dwf_to_jpg": [["secret"], ["token"]],
    "convert_dwf_to_pdf": [["secret"], ["token"]],
    "convert_dwf_to_png": [["secret"], ["token"]],
    "convert_dwf_to_svg": [["secret"], ["token"]],
    "convert_dwf_to_tiff": [["secret"], ["token"]],
    "convert_dwf_to_webp": [["secret"], ["token"]],
    "convert_dwg_to_jpg": [["secret"], ["token"]],
    "convert_dwg_to_pdf": [["secret"], ["token"]],
    "convert_dwg_to_png": [["secret"], ["token"]],
    "convert_dwg_to_svg": [["secret"], ["token"]],
    "convert_dwg_to_tiff": [["secret"], ["token"]],
    "convert_dwg_to_webp": [["secret"], ["token"]],
    "convert_dxf_to_jpg": [["secret"], ["token"]],
    "convert_dxf_to_pdf": [["secret"], ["token"]],
    "convert_dxf_to_png": [["secret"], ["token"]],
    "convert_dxf_to_svg": [["secret"], ["token"]],
    "convert_dxf_to_tiff": [["secret"], ["token"]],
    "convert_dxf_to_webp": [["secret"], ["token"]],
    "extract_email_attachments": [["secret"], ["token"]],
    "extract_email_metadata": [["secret"], ["token"]],
    "convert_email_to_image": [["secret"], ["token"]],
    "convert_eml_to_pdf": [["secret"], ["token"]],
    "convert_email_to_png": [["secret"], ["token"]],
    "convert_eml_to_tiff": [["secret"], ["token"]],
    "convert_eml_to_webp": [["secret"], ["token"]],
    "convert_eps_to_jpg": [["secret"], ["token"]],
    "convert_eps_to_pdf": [["secret"], ["token"]],
    "convert_eps_to_png": [["secret"], ["token"]],
    "convert_eps_to_tiff": [["secret"], ["token"]],
    "convert_epub_to_jpg": [["secret"], ["token"]],
    "convert_epub_to_pdf": [["secret"], ["token"]],
    "convert_epub_to_png": [["secret"], ["token"]],
    "convert_epub_to_tiff": [["secret"], ["token"]],
    "convert_epub_to_webp": [["secret"], ["token"]],
    "convert_file_to_pdf": [["secret"], ["token"]],
    "compress_files_to_archive": [["secret"], ["token"]],
    "convert_gif_animation": [["secret"], ["token"]],
    "convert_gif_to_jpg": [["secret"], ["token"]],
    "convert_gif_to_pdf": [["secret"], ["token"]],
    "convert_gif_to_png": [["secret"], ["token"]],
    "convert_gif_to_pnm": [["secret"], ["token"]],
    "convert_gif_to_svg": [["secret"], ["token"]],
    "convert_gif_to_tiff": [["secret"], ["token"]],
    "convert_gif_to_webp": [["secret"], ["token"]],
    "convert_heic_to_jpg": [["secret"], ["token"]],
    "convert_image_heic_to_jxl": [["secret"], ["token"]],
    "convert_heic_to_pdf": [["secret"], ["token"]],
    "convert_heic_to_png": [["secret"], ["token"]],
    "convert_image_heic_to_pnm": [["secret"], ["token"]],
    "convert_heic_to_svg": [["secret"], ["token"]],
    "convert_heic_to_tiff": [["secret"], ["token"]],
    "convert_image_heic_to_webp": [["secret"], ["token"]],
    "convert_heif_to_jpg": [["secret"], ["token"]],
    "convert_heif_to_pdf": [["secret"], ["token"]],
    "convert_html_to_docx": [["secret"], ["token"]],
    "convert_html_to_jpg": [["secret"], ["token"]],
    "convert_html_to_markdown": [["secret"], ["token"]],
    "convert_html_to_pdf": [["secret"], ["token"]],
    "convert_html_to_png": [["secret"], ["token"]],
    "convert_html_to_text": [["secret"], ["token"]],
    "convert_html_to_spreadsheet": [["secret"], ["token"]],
    "convert_html_to_xlsx": [["secret"], ["token"]],
    "convert_image_ico_to_jpg": [["secret"], ["token"]],
    "convert_ico_to_pdf": [["secret"], ["token"]],
    "convert_image_ico_to_png": [["secret"], ["token"]],
    "convert_icon_to_svg": [["secret"], ["token"]],
    "convert_image_ico_to_webp": [["secret"], ["token"]],
    "join_images": [["secret"], ["token"]],
    "convert_images_to_pdf": [["secret"], ["token"]],
    "convert_jfif_to_pdf": [["secret"], ["token"]],
    "compress_jpg_image": [["secret"], ["token"]],
    "convert_image_to_gif": [["secret"], ["token"]],
    "convert_image_format": [["secret"], ["token"]],
    "convert_image_jpg_to_jxl": [["secret"], ["token"]],
    "convert_image_to_pdf_jpeg": [["secret"], ["token"]],
    "convert_image_jpg_to_png": [["secret"], ["token"]],
    "convert_image_jpg_to_pnm": [["secret"], ["token"]],
    "convert_image_to_svg_jpg": [["secret"], ["token"]],
    "convert_image_to_tiff": [["secret"], ["token"]],
    "extract_text_from_image": [["secret"], ["token"]],
    "convert_image_jpg_to_webp": [["secret"], ["token"]],
    "convert_presentation_to_pptx": [["secret"], ["token"]],
    "convert_log_to_docx": [["secret"], ["token"]],
    "convert_log_to_pdf": [["secret"], ["token"]],
    "convert_log_to_text": [["secret"], ["token"]],
    "convert_markdown_to_html": [["secret"], ["token"]],
    "convert_markdown_to_pdf": [["secret"], ["token"]],
    "convert_mhtml_to_docx": [["secret"], ["token"]],
    "convert_mobi_to_jpg": [["secret"], ["token"]],
    "convert_mobi_to_pdf": [["secret"], ["token"]],
    "convert_mobi_to_png": [["secret"], ["token"]],
    "convert_mobi_to_tiff": [["secret"], ["token"]],
    "convert_email_to_jpg": [["secret"], ["token"]],
    "convert_msg_to_pdf": [["secret"], ["token"]],
    "convert_email_to_png_outlook": [["secret"], ["token"]],
    "convert_msg_to_tiff": [["secret"], ["token"]],
    "convert_message_to_webp": [["secret"], ["token"]],
    "convert_numbers_to_csv": [["secret"], ["token"]],
    "convert_numbers_to_xlsx": [["secret"], ["token"]],
    "convert_document_to_jpg_spreadsheet": [["secret"], ["token"]],
    "convert_odc_to_pdf": [["secret"], ["token"]],
    "convert_odc_to_png": [["secret"], ["token"]],
    "convert_document_to_jpg_formula": [["secret"], ["token"]],
    "convert_document_to_pdf_odf": [["secret"], ["token"]],
    "convert_document_to_png": [["secret"], ["token"]],
    "convert_odg_to_pdf": [["secret"], ["token"]],
    "convert_presentation_to_jpg": [["secret"], ["token"]],
    "convert_odp_to_pdf": [["secret"], ["token"]],
    "convert_presentation_to_png": [["secret"], ["token"]],
    "convert_spreadsheet_to_image": [["secret"], ["token"]],
    "convert_ods_to_pdf": [["secret"], ["token"]],
    "convert_ods_to_png": [["secret"], ["token"]],
    "convert_document_odt_to_docx": [["secret"], ["token"]],
    "convert_document_to_jpg_text": [["secret"], ["token"]],
    "convert_document_to_pdf_odt": [["secret"], ["token"]],
    "convert_document_to_png_text": [["secret"], ["token"]],
    "convert_document_odt_to_txt": [["secret"], ["token"]],
    "convert_document_to_xml": [["secret"], ["token"]],
    "convert_office_document_to_pdf": [["secret"], ["token"]],
    "convert_pages_to_docx": [["secret"], ["token"]],
    "convert_pages_to_text": [["secret"], ["token"]],
    "compress_pdf": [["secret"], ["token"]],
    "crop_pdf": [["secret"], ["token"]],
    "convert_pdf_to_csv": [["secret"], ["token"]],
    "delete_pdf_pages": [["secret"], ["token"]],
    "convert_pdf_to_docx": [["secret"], ["token"]],
    "extract_data_from_pdf": [["secret"], ["token"]],
    "extract_images_from_pdf": [["secret"], ["token"]],
    "extract_pdf_form_fields": [["secret"], ["token"]],
    "import_pdf_with_fdf_form_data": [["secret"], ["token"]],
    "flatten_pdf": [["secret"], ["token"]],
    "convert_pdf_to_html": [["secret"], ["token"]],
    "add_watermark_to_pdf": [["secret"], ["token"]],
    "convert_pdf_to_jpg": [["secret"], ["token"]],
    "merge_pdfs": [["secret"], ["token"]],
    "convert_pdf_to_metadata": [["secret"], ["token"]],
    "extract_text_from_pdf": [["secret"], ["token"]],
    "convert_pdf_to_pcl": [["secret"], ["token"]],
    "convert_pdf_to_pdf": [["secret"], ["token"]],
    "add_watermark_to_pdf_document": [["secret"], ["token"]],
    "convert_pdf_to_pdfa": [["secret"], ["token"]],
    "convert_pdf_to_pdfua": [["secret"], ["token"]],
    "convert_pdf_to_png": [["secret"], ["token"]],
    "convert_pdf_to_pptx": [["secret"], ["token"]],
    "convert_pdf_to_print": [["secret"], ["token"]],
    "protect_pdf": [["secret"], ["token"]],
    "convert_pdf_to_rasterized_image": [["secret"], ["token"]],
    "redact_pdf": [["secret"], ["token"]],
    "resize_pdf_pages": [["secret"], ["token"]],
    "rotate_pdf_pages": [["secret"], ["token"]],
    "convert_pdf_to_rtf": [["secret"], ["token"]],
    "split_pdf": [["secret"], ["token"]],
    "convert_pdf_to_svg": [["secret"], ["token"]],
    "convert_pdf_to_text_with_watermark": [["secret"], ["token"]],
    "convert_pdf_to_tiff": [["secret"], ["token"]],
    "convert_pdf_to_tiff_fax": [["secret"], ["token"]],
    "convert_pdf_to_text": [["secret"], ["token"]],
    "unprotect_pdf": [["secret"], ["token"]],
    "convert_pdf_to_webp": [["secret"], ["token"]],
    "convert_pdf_to_xlsx": [["secret"], ["token"]],
    "validate_pdfa_conformance": [["secret"], ["token"]],
    "convert_png_to_gif": [["secret"], ["token"]],
    "convert_image_png_to_jpg": [["secret"], ["token"]],
    "convert_image_to_pdf_png": [["secret"], ["token"]],
    "convert_image_png_to_pnm": [["secret"], ["token"]],
    "convert_image_to_svg": [["secret"], ["token"]],
    "convert_png_to_tiff": [["secret"], ["token"]],
    "convert_image_png_to_webp": [["secret"], ["token"]],
    "translate_po_file": [["secret"], ["token"]],
    "convert_presentation_to_jpg_template": [["secret"], ["token"]],
    "convert_presentation_template_to_pdf": [["secret"], ["token"]],
    "convert_presentation_to_png_template": [["secret"], ["token"]],
    "convert_potx_to_pptx": [["secret"], ["token"]],
    "convert_presentation_template_to_tiff": [["secret"], ["token"]],
    "convert_presentation_to_webp_template": [["secret"], ["token"]],
    "convert_presentation_to_jpg_slideshow": [["secret"], ["token"]],
    "convert_presentation_slideshow_to_pdf": [["secret"], ["token"]],
    "convert_presentation_to_png_slideshow": [["secret"], ["token"]],
    "convert_presentation_ppsx_to_pptx": [["secret"], ["token"]],
    "convert_presentation_slideshow_to_tiff": [["secret"], ["token"]],
    "convert_presentation_to_webp_slideshow": [["secret"], ["token"]],
    "convert_presentation_ppt_to_pptx": [["secret"], ["token"]],
    "convert_presentation_to_images": [["secret"], ["token"]],
    "convert_presentation_to_pdf": [["secret"], ["token"]],
    "convert_presentation_to_images_png": [["secret"], ["token"]],
    "convert_presentation": [["secret"], ["token"]],
    "encrypt_presentation": [["secret"], ["token"]],
    "convert_presentation_to_tiff": [["secret"], ["token"]],
    "convert_presentation_to_webp": [["secret"], ["token"]],
    "convert_prn_to_jpg": [["secret"], ["token"]],
    "convert_prn_to_pdf": [["secret"], ["token"]],
    "convert_prn_to_png": [["secret"], ["token"]],
    "convert_prn_to_tiff": [["secret"], ["token"]],
    "convert_postscript_to_jpg": [["secret"], ["token"]],
    "convert_postscript_to_pdf": [["secret"], ["token"]],
    "convert_postscript_to_png": [["secret"], ["token"]],
    "convert_postscript_to_tiff": [["secret"], ["token"]],
    "convert_psd_to_jpg": [["secret"], ["token"]],
    "convert_image_psd_to_png": [["secret"], ["token"]],
    "convert_image_psd_to_pnm": [["secret"], ["token"]],
    "convert_psd_to_svg": [["secret"], ["token"]],
    "convert_psd_to_tiff": [["secret"], ["token"]],
    "convert_image_psd_to_webp": [["secret"], ["token"]],
    "convert_publication_to_jpg": [["secret"], ["token"]],
    "convert_pub_to_pdf": [["secret"], ["token"]],
    "convert_pub_to_png": [["secret"], ["token"]],
    "convert_pub_to_tiff": [["secret"], ["token"]],
    "convert_rtf_to_html": [["secret"], ["token"]],
    "convert_rtf_to_jpg": [["secret"], ["token"]],
    "convert_rtf_to_pdf": [["secret"], ["token"]],
    "convert_rtf_to_text": [["secret"], ["token"]],
    "convert_svg_to_jpg": [["secret"], ["token"]],
    "convert_svg_to_pdf": [["secret"], ["token"]],
    "convert_svg_to_png": [["secret"], ["token"]],
    "convert_svg_to_pnm": [["secret"], ["token"]],
    "convert_svg_image": [["secret"], ["token"]],
    "convert_svg_to_tiff": [["secret"], ["token"]],
    "convert_svg_to_webp": [["secret"], ["token"]],
    "fill_template_to_docx": [["secret"], ["token"]],
    "convert_template_to_pdf": [["secret"], ["token"]],
    "convert_tiff_to_jpg": [["secret"], ["token"]],
    "convert_tiff_to_pdf": [["secret"], ["token"]],
    "convert_tiff_to_png": [["secret"], ["token"]],
    "convert_tiff_to_pnm": [["secret"], ["token"]],
    "convert_tiff_to_svg": [["secret"], ["token"]],
    "convert_tiff_image": [["secret"], ["token"]],
    "convert_image_tiff_to_webp": [["secret"], ["token"]],
    "convert_text_to_image": [["secret"], ["token"]],
    "convert_text_to_pdf": [["secret"], ["token"]],
    "convert_vsdx_to_jpg": [["secret"], ["token"]],
    "convert_vsdx_to_pdf": [["secret"], ["token"]],
    "convert_vsdx_to_png": [["secret"], ["token"]],
    "convert_vsdx_to_tiff": [["secret"], ["token"]],
    "convert_webpage_to_jpg": [["secret"], ["token"]],
    "convert_webpage_to_pdf": [["secret"], ["token"]],
    "convert_webpage_to_png": [["secret"], ["token"]],
    "convert_webpage_to_text": [["secret"], ["token"]],
    "convert_webp_to_gif": [["secret"], ["token"]],
    "convert_webp_to_jpg": [["secret"], ["token"]],
    "convert_webp_to_pdf": [["secret"], ["token"]],
    "convert_webp_to_png": [["secret"], ["token"]],
    "convert_webp_to_pnm": [["secret"], ["token"]],
    "convert_webp_to_svg": [["secret"], ["token"]],
    "convert_webp_to_tiff": [["secret"], ["token"]],
    "convert_webp_image": [["secret"], ["token"]],
    "convert_wpd_to_pdf": [["secret"], ["token"]],
    "convert_spreadsheet_format": [["secret"], ["token"]],
    "convert_spreadsheet_xls_to_xlsx": [["secret"], ["token"]],
    "convert_xlsb_to_csv": [["secret"], ["token"]],
    "convert_xlsb_to_pdf": [["secret"], ["token"]],
    "convert_spreadsheet_to_csv": [["secret"], ["token"]],
    "convert_spreadsheet_to_image_xlsx": [["secret"], ["token"]],
    "convert_spreadsheet_to_pdf": [["secret"], ["token"]],
    "convert_spreadsheet_to_image_png": [["secret"], ["token"]],
    "encrypt_xlsx_workbook": [["secret"], ["token"]],
    "convert_spreadsheet_to_tiff": [["secret"], ["token"]],
    "convert_spreadsheet_to_image_webp": [["secret"], ["token"]],
    "convert_spreadsheet_format_modern": [["secret"], ["token"]],
    "convert_spreadsheet_template_to_pdf": [["secret"], ["token"]],
    "convert_xml_to_docx": [["secret"], ["token"]],
    "extract_archive": [["secret"], ["token"]]
}
