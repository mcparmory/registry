"""
Authentication module for ElevenLabs MCP server.

Generated: 2026-05-11 19:45:03 UTC
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
    API Key authentication for ElevenLabs API Documentation.

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
    "list_speech_history": [["ApiKeyAuth"]],
    "get_speech_history_item": [["ApiKeyAuth"]],
    "delete_history_item": [["ApiKeyAuth"]],
    "get_speech_history_audio": [["ApiKeyAuth"]],
    "download_speech_items": [["ApiKeyAuth"]],
    "generate_sound": [["ApiKeyAuth"]],
    "isolate_audio": [["ApiKeyAuth"]],
    "isolate_audio_stream": [["ApiKeyAuth"]],
    "delete_voice_sample": [["ApiKeyAuth"]],
    "retrieve_voice_sample_audio": [["ApiKeyAuth"]],
    "generate_speech": [["ApiKeyAuth"]],
    "generate_speech_with_timestamps": [["ApiKeyAuth"]],
    "generate_speech_stream": [["ApiKeyAuth"]],
    "generate_speech_stream_with_timestamps": [["ApiKeyAuth"]],
    "generate_dialogue": [["ApiKeyAuth"]],
    "generate_dialogue_stream": [["ApiKeyAuth"]],
    "generate_dialogue_stream_with_timestamps": [["ApiKeyAuth"]],
    "generate_dialogue_with_timestamps": [["ApiKeyAuth"]],
    "convert_voice": [["ApiKeyAuth"]],
    "convert_speech_to_speech_stream": [["ApiKeyAuth"]],
    "generate_voice_previews": [["ApiKeyAuth"]],
    "create_voice": [["ApiKeyAuth"]],
    "design_voice": [["ApiKeyAuth"]],
    "remix_voice": [["ApiKeyAuth"]],
    "stream_voice_preview": [["ApiKeyAuth"]],
    "get_subscription_info": [["ApiKeyAuth"]],
    "get_user": [["ApiKeyAuth"]],
    "list_voices": [["ApiKeyAuth"]],
    "get_default_voice_settings": [["ApiKeyAuth"]],
    "get_voice_settings": [["ApiKeyAuth"]],
    "get_voice": [["ApiKeyAuth"]],
    "delete_voice": [["ApiKeyAuth"]],
    "configure_voice_settings": [["ApiKeyAuth"]],
    "create_voice_sample": [["ApiKeyAuth"]],
    "update_voice": [["ApiKeyAuth"]],
    "add_shared_voice": [["ApiKeyAuth"]],
    "generate_podcast": [["ApiKeyAuth"]],
    "apply_pronunciation_dictionaries": [["ApiKeyAuth"]],
    "list_projects": [["ApiKeyAuth"]],
    "create_studio_project": [["ApiKeyAuth"]],
    "get_project": [["ApiKeyAuth"]],
    "update_studio_project": [["ApiKeyAuth"]],
    "delete_project": [["ApiKeyAuth"]],
    "update_project_content": [["ApiKeyAuth"]],
    "convert_studio_project": [["ApiKeyAuth"]],
    "list_snapshots": [["ApiKeyAuth"]],
    "get_snapshot": [["ApiKeyAuth"]],
    "stream_project_snapshot_audio": [["ApiKeyAuth"]],
    "download_snapshot_archive": [["ApiKeyAuth"]],
    "list_chapters": [["ApiKeyAuth"]],
    "create_chapter": [["ApiKeyAuth"]],
    "get_chapter": [["ApiKeyAuth"]],
    "update_chapter": [["ApiKeyAuth"]],
    "delete_chapter": [["ApiKeyAuth"]],
    "convert_chapter": [["ApiKeyAuth"]],
    "list_chapter_snapshots": [["ApiKeyAuth"]],
    "get_chapter_snapshot": [["ApiKeyAuth"]],
    "get_chapter_snapshot_audio": [["ApiKeyAuth"]],
    "list_muted_tracks": [["ApiKeyAuth"]],
    "get_dubbing_resource": [["ApiKeyAuth"]],
    "add_dubbing_language": [["ApiKeyAuth"]],
    "create_segment": [["ApiKeyAuth"]],
    "update_segment_language": [["ApiKeyAuth"]],
    "reassign_segments": [["ApiKeyAuth"]],
    "delete_dubbing_segment": [["ApiKeyAuth"]],
    "regenerate_segment_transcriptions": [["ApiKeyAuth"]],
    "translate_dubbing_segments": [["ApiKeyAuth"]],
    "regenerate_dubs": [["ApiKeyAuth"]],
    "update_speaker": [["ApiKeyAuth"]],
    "add_speaker": [["ApiKeyAuth"]],
    "list_similar_voices": [["ApiKeyAuth"]],
    "render_dubbing": [["ApiKeyAuth"]],
    "list_dubs": [["ApiKeyAuth"]],
    "dub_media": [["ApiKeyAuth"]],
    "get_dubbing": [["ApiKeyAuth"]],
    "delete_dubbing": [["ApiKeyAuth"]],
    "download_dubbed_audio": [["ApiKeyAuth"]],
    "get_transcript_dubbing": [["ApiKeyAuth"]],
    "list_models": [["ApiKeyAuth"]],
    "create_audio_project": [["ApiKeyAuth"]],
    "get_audio_native_settings": [["ApiKeyAuth"]],
    "update_audio_native_content": [["ApiKeyAuth"]],
    "update_audio_native_content_from_url": [["ApiKeyAuth"]],
    "list_voices_shared": [["ApiKeyAuth"]],
    "find_similar_voices": [["ApiKeyAuth"]],
    "get_character_usage_metrics": [["ApiKeyAuth"]],
    "create_pronunciation_dictionary": [["ApiKeyAuth"]],
    "create_pronunciation_dictionary_from_rules": [["ApiKeyAuth"]],
    "get_pronunciation_dictionary": [["ApiKeyAuth"]],
    "update_pronunciation_dictionary": [["ApiKeyAuth"]],
    "replace_pronunciation_rules": [["ApiKeyAuth"]],
    "add_pronunciation_rules": [["ApiKeyAuth"]],
    "delete_pronunciation_rules": [["ApiKeyAuth"]],
    "download_pronunciation_dictionary_version": [["ApiKeyAuth"]],
    "list_pronunciation_dictionaries": [["ApiKeyAuth"]],
    "list_service_account_api_keys": [["ApiKeyAuth"]],
    "create_service_account_api_key": [["ApiKeyAuth"]],
    "revoke_service_account_api_key": [["ApiKeyAuth"]],
    "list_auth_connections": [["ApiKeyAuth"]],
    "delete_auth_connection": [["ApiKeyAuth"]],
    "list_service_accounts": [["ApiKeyAuth"]],
    "list_groups": [["ApiKeyAuth"]],
    "find_group": [["ApiKeyAuth"]],
    "remove_group_member": [["ApiKeyAuth"]],
    "add_group_member": [["ApiKeyAuth"]],
    "send_workspace_invite": [["ApiKeyAuth"]],
    "send_workspace_invitations": [["ApiKeyAuth"]],
    "revoke_workspace_invitation": [["ApiKeyAuth"]],
    "get_resource": [["ApiKeyAuth"]],
    "grant_resource_access": [["ApiKeyAuth"]],
    "revoke_resource_access": [["ApiKeyAuth"]],
    "list_workspace_webhooks": [["ApiKeyAuth"]],
    "transcribe_audio": [["ApiKeyAuth"]],
    "get_transcript": [["ApiKeyAuth"]],
    "delete_transcript": [["ApiKeyAuth"]],
    "list_evaluation_criteria": [["ApiKeyAuth"]],
    "get_evaluation_criterion": [["ApiKeyAuth"]],
    "update_eval_criterion": [["ApiKeyAuth"]],
    "delete_evaluation_criterion": [["ApiKeyAuth"]],
    "list_evaluations": [["ApiKeyAuth"]],
    "create_evaluation": [["ApiKeyAuth"]],
    "get_evaluation": [["ApiKeyAuth"]],
    "list_human_agents": [["ApiKeyAuth"]],
    "get_human_agent": [["ApiKeyAuth"]],
    "delete_human_agent": [["ApiKeyAuth"]],
    "list_evaluation_analytics": [["ApiKeyAuth"]],
    "get_criterion_analytics": [["ApiKeyAuth"]],
    "get_agent_analytics": [["ApiKeyAuth"]],
    "align_audio_to_text": [["ApiKeyAuth"]],
    "get_agent_conversation_signed_link": [["ApiKeyAuth"]],
    "initiate_outbound_call": [["ApiKeyAuth"]],
    "initiate_twilio_call": [["ApiKeyAuth"]],
    "initiate_whatsapp_call": [["ApiKeyAuth"]],
    "send_whatsapp_message": [["ApiKeyAuth"]],
    "create_agent_route": [["ApiKeyAuth"]],
    "list_agent_summaries": [["ApiKeyAuth"]],
    "get_agent": [["ApiKeyAuth"]],
    "update_agent_settings": [["ApiKeyAuth"]],
    "delete_agent": [["ApiKeyAuth"]],
    "get_agent_widget_config": [["ApiKeyAuth"]],
    "get_agent_share_link": [["ApiKeyAuth"]],
    "upload_agent_avatar": [["ApiKeyAuth"]],
    "list_agents": [["ApiKeyAuth"]],
    "get_knowledge_base_size": [["ApiKeyAuth"]],
    "estimate_agent_llm_cost": [["ApiKeyAuth"]],
    "duplicate_agent": [["ApiKeyAuth"]],
    "simulate_agent_conversation": [["ApiKeyAuth"]],
    "simulate_conversation_stream": [["ApiKeyAuth"]],
    "create_agent_test": [["ApiKeyAuth"]],
    "get_agent_test": [["ApiKeyAuth"]],
    "update_agent_test": [["ApiKeyAuth"]],
    "delete_agent_test": [["ApiKeyAuth"]],
    "fetch_agent_response_test_summaries": [["ApiKeyAuth"]],
    "list_agent_tests": [["ApiKeyAuth"]],
    "list_test_invocations": [["ApiKeyAuth"]],
    "run_agent_tests": [["ApiKeyAuth"]],
    "get_test_invocation": [["ApiKeyAuth"]],
    "resubmit_tests": [["ApiKeyAuth"]],
    "list_conversations": [["ApiKeyAuth"]],
    "list_conversation_users": [["ApiKeyAuth"]],
    "get_conversation": [["ApiKeyAuth"]],
    "delete_conversation": [["ApiKeyAuth"]],
    "get_conversation_audio": [["ApiKeyAuth"]],
    "submit_conversation_feedback": [["ApiKeyAuth"]],
    "search_conversation_messages": [["ApiKeyAuth"]],
    "search_conversation_messages_semantic": [["ApiKeyAuth"]],
    "list_phone_numbers": [["ApiKeyAuth"]],
    "import_phone_number": [["ApiKeyAuth"]],
    "get_phone_number": [["ApiKeyAuth"]],
    "update_phone_number": [["ApiKeyAuth"]],
    "delete_phone_number": [["ApiKeyAuth"]],
    "calculate_llm_expected_cost": [["ApiKeyAuth"]],
    "list_llms": [["ApiKeyAuth"]],
    "upload_file": [["ApiKeyAuth"]],
    "delete_conversation_file": [["ApiKeyAuth"]],
    "get_conversation_live_count": [["ApiKeyAuth"]],
    "get_knowledge_base_summaries": [["ApiKeyAuth"]],
    "list_knowledge_bases": [["ApiKeyAuth"]],
    "create_knowledge_base_document_from_url": [["ApiKeyAuth"]],
    "upload_knowledge_base_document": [["ApiKeyAuth"]],
    "add_text_document": [["ApiKeyAuth"]],
    "create_folder": [["ApiKeyAuth"]],
    "retrieve_knowledge_base_document": [["ApiKeyAuth"]],
    "rename_document": [["ApiKeyAuth"]],
    "delete_knowledge_base_document": [["ApiKeyAuth"]],
    "get_rag_index_overview": [["ApiKeyAuth"]],
    "batch_compute_rag_indexes": [["ApiKeyAuth"]],
    "refresh_knowledge_base_document": [["ApiKeyAuth"]],
    "list_rag_indexes": [["ApiKeyAuth"]],
    "index_knowledge_base_document": [["ApiKeyAuth"]],
    "delete_rag_index": [["ApiKeyAuth"]],
    "list_dependent_agents": [["ApiKeyAuth"]],
    "retrieve_knowledge_base_document_content": [["ApiKeyAuth"]],
    "get_knowledge_base_source_file_url": [["ApiKeyAuth"]],
    "retrieve_knowledge_base_chunk": [["ApiKeyAuth"]],
    "move_knowledge_base_document": [["ApiKeyAuth"]],
    "move_knowledge_base_entities": [["ApiKeyAuth"]],
    "list_tools": [["ApiKeyAuth"]],
    "create_tool": [["ApiKeyAuth"]],
    "get_tool": [["ApiKeyAuth"]],
    "update_tool": [["ApiKeyAuth"]],
    "delete_tool": [["ApiKeyAuth"]],
    "list_dependent_agents_tool": [["ApiKeyAuth"]],
    "create_workspace_secret": [["ApiKeyAuth"]],
    "update_secret": [["ApiKeyAuth"]],
    "delete_secret": [["ApiKeyAuth"]],
    "submit_batch_calls": [["ApiKeyAuth"]],
    "list_batch_calls": [["ApiKeyAuth"]],
    "get_batch_call": [["ApiKeyAuth"]],
    "delete_batch_call": [["ApiKeyAuth"]],
    "cancel_batch_call": [["ApiKeyAuth"]],
    "retry_batch_call": [["ApiKeyAuth"]],
    "initiate_outbound_sip_call": [["ApiKeyAuth"]],
    "list_mcp_servers": [["ApiKeyAuth"]],
    "register_mcp_server": [["ApiKeyAuth"]],
    "get_mcp_server": [["ApiKeyAuth"]],
    "configure_mcp_server": [["ApiKeyAuth"]],
    "delete_mcp_server": [["ApiKeyAuth"]],
    "list_mcp_server_tools": [["ApiKeyAuth"]],
    "approve_mcp_server_tool": [["ApiKeyAuth"]],
    "revoke_mcp_server_tool_approval": [["ApiKeyAuth"]],
    "create_tool_config_override": [["ApiKeyAuth"]],
    "get_tool_config_override": [["ApiKeyAuth"]],
    "override_mcp_tool_config": [["ApiKeyAuth"]],
    "get_whatsapp_account": [["ApiKeyAuth"]],
    "update_whatsapp_account": [["ApiKeyAuth"]],
    "delete_whatsapp_account": [["ApiKeyAuth"]],
    "list_whatsapp_accounts": [["ApiKeyAuth"]],
    "list_agent_branches": [["ApiKeyAuth"]],
    "create_agent_branch": [["ApiKeyAuth"]],
    "get_agent_branch": [["ApiKeyAuth"]],
    "update_branch": [["ApiKeyAuth"]],
    "merge_branch": [["ApiKeyAuth"]],
    "deploy_agent": [["ApiKeyAuth"]],
    "create_agent_draft": [["ApiKeyAuth"]],
    "delete_agent_draft": [["ApiKeyAuth"]],
    "list_environment_variables": [["ApiKeyAuth"]],
    "create_environment_variable": [["ApiKeyAuth"]],
    "get_environment_variable": [["ApiKeyAuth"]],
    "update_environment_variable": [["ApiKeyAuth"]],
    "generate_composition_plan": [["ApiKeyAuth"]],
    "compose_song": [["ApiKeyAuth"]],
    "compose_song_detailed": [["ApiKeyAuth"]],
    "compose_music": [["ApiKeyAuth"]],
    "upload_song": [["ApiKeyAuth"]],
    "separate_song_stems": [["ApiKeyAuth"]],
    "create_voice_pvc": [["ApiKeyAuth"]],
    "update_voice_pvc": [["ApiKeyAuth"]],
    "add_voice_samples": [["ApiKeyAuth"]],
    "update_voice_sample": [["ApiKeyAuth"]],
    "remove_voice_sample": [["ApiKeyAuth"]],
    "get_voice_sample_audio": [["ApiKeyAuth"]],
    "get_voice_sample_waveform": [["ApiKeyAuth"]],
    "get_speaker_separation_status": [["ApiKeyAuth"]],
    "separate_speakers": [["ApiKeyAuth"]],
    "get_speaker_audio": [["ApiKeyAuth"]],
    "train_voice": [["ApiKeyAuth"]],
    "submit_voice_verification": [["ApiKeyAuth"]]
}
