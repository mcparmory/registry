"""
Authentication module for MailerSend MCP server.

Generated: 2026-05-05 15:31:48 UTC
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
    Bearer token authentication for MailerSend API.

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
    "send_email": [["bearerAuth"]],
    "send_bulk_emails": [["bearerAuth"]],
    "get_bulk_email_status": [["bearerAuth"]],
    "list_activities_for_domain": [["bearerAuth"]],
    "get_activity": [["bearerAuth"]],
    "get_activity_data_by_date_range": [["bearerAuth"]],
    "list_opens_by_country": [["bearerAuth"]],
    "list_opens_by_user_agent": [["bearerAuth"]],
    "get_opens_by_reading_environment": [["bearerAuth"]],
    "list_domains": [["bearerAuth"]],
    "create_domain": [["bearerAuth"]],
    "get_domain": [["bearerAuth"]],
    "delete_domain": [["bearerAuth"]],
    "list_recipients_for_domain": [["bearerAuth"]],
    "update_domain_settings": [["bearerAuth"]],
    "list_dns_records": [["bearerAuth"]],
    "get_domain_verification_status": [["bearerAuth"]],
    "list_sender_identities": [["bearerAuth"]],
    "create_sender_identity": [["bearerAuth"]],
    "get_sender_identity": [["bearerAuth"]],
    "update_sender_identity": [["bearerAuth"]],
    "delete_sender_identity": [["bearerAuth"]],
    "get_sender_identity_by_email": [["bearerAuth"]],
    "update_sender_identity_by_email": [["bearerAuth"]],
    "delete_sender_identity_by_email": [["bearerAuth"]],
    "list_inbound_routes": [["bearerAuth"]],
    "get_inbound_route": [["bearerAuth"]],
    "update_inbound_route": [["bearerAuth"]],
    "delete_inbound_route": [["bearerAuth"]],
    "list_messages": [["bearerAuth"]],
    "get_message": [["bearerAuth"]],
    "list_scheduled_messages": [["bearerAuth"]],
    "get_scheduled_message": [["bearerAuth"]],
    "delete_scheduled_message": [["bearerAuth"]],
    "list_blocklist_recipients": [["bearerAuth"]],
    "add_blocklist_recipients": [["bearerAuth"]],
    "delete_blocklist_recipients": [["bearerAuth"]],
    "list_hard_bounces_recipients": [["bearerAuth"]],
    "add_recipients_to_hard_bounces_suppression": [["bearerAuth"]],
    "delete_hard_bounces_recipients": [["bearerAuth"]],
    "list_spam_complaint_recipients": [["bearerAuth"]],
    "add_spam_complaints_recipients": [["bearerAuth"]],
    "delete_spam_complaints_recipients": [["bearerAuth"]],
    "list_unsubscribed_recipients": [["bearerAuth"]],
    "add_unsubscribe_recipients": [["bearerAuth"]],
    "delete_unsubscribed_recipients": [["bearerAuth"]],
    "list_recipients": [["bearerAuth"]],
    "get_recipient": [["bearerAuth"]],
    "delete_recipient": [["bearerAuth"]],
    "list_templates": [["bearerAuth"]],
    "list_webhooks": [["bearerAuth"]],
    "get_webhook": [["bearerAuth"]],
    "delete_webhook": [["bearerAuth"]],
    "verify_email": [["bearerAuth"]],
    "list_email_verification_lists": [["bearerAuth"]],
    "create_email_verification_list": [["bearerAuth"]],
    "get_email_verification_list": [["bearerAuth"]],
    "verify_email_verification_list": [["bearerAuth"]],
    "list_email_verification_results": [["bearerAuth"]],
    "update_token_status": [["bearerAuth"]],
    "delete_token": [["bearerAuth"]],
    "list_users": [["bearerAuth"]],
    "get_user": [["bearerAuth"]],
    "update_user_role": [["bearerAuth"]],
    "delete_user": [["bearerAuth"]],
    "send_sms": [["bearerAuth"]],
    "list_sms_phone_numbers": [["bearerAuth"]],
    "get_sms_phone_number": [["bearerAuth"]],
    "update_sms_phone_number_pause_status": [["bearerAuth"]],
    "delete_sms_number": [["bearerAuth"]],
    "list_sms_messages": [["bearerAuth"]],
    "get_sms_message": [["bearerAuth"]],
    "list_sms_activities": [["bearerAuth"]],
    "get_sms_message_activity": [["bearerAuth"]],
    "list_sms_recipients": [["bearerAuth"]],
    "get_sms_recipient": [["bearerAuth"]],
    "update_sms_recipient_status": [["bearerAuth"]],
    "list_sms_webhooks": [["bearerAuth"]],
    "get_sms_webhook": [["bearerAuth"]],
    "update_sms_webhook": [["bearerAuth"]],
    "delete_sms_webhook": [["bearerAuth"]],
    "list_sms_inbound_routes": [["bearerAuth"]],
    "get_sms_inbound_route": [["bearerAuth"]],
    "update_sms_inbound_route": [["bearerAuth"]],
    "delete_sms_inbound_route": [["bearerAuth"]],
    "list_smtp_users": [["bearerAuth"]],
    "get_smtp_user": [["bearerAuth"]],
    "update_smtp_user": [["bearerAuth"]],
    "delete_smtp_user": [["bearerAuth"]]
}
