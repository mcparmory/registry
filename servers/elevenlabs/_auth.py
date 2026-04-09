"""
Authentication module for ElevenLabs MCP server.

Generated: 2026-04-09 17:20:47 UTC
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
    "list_speech_history": [["xi_api_key"]],
    "get_speech_history_item": [["xi_api_key"]],
    "delete_history_item": [["xi_api_key"]],
    "get_speech_history_audio": [["xi_api_key"]],
    "download_speech_items": [["xi_api_key"]],
    "generate_sound": [["xi_api_key"]],
    "isolate_audio": [["xi_api_key"]],
    "isolate_audio_stream": [["xi_api_key"]],
    "delete_voice_sample": [["xi_api_key"]],
    "retrieve_voice_sample_audio": [["xi_api_key"]],
    "generate_speech": [["xi_api_key"]],
    "generate_speech_with_timestamps": [["xi_api_key"]],
    "generate_speech_stream": [["xi_api_key"]],
    "generate_speech_stream_with_timestamps": [["xi_api_key"]],
    "generate_dialogue": [["xi_api_key"]],
    "generate_dialogue_stream": [["xi_api_key"]],
    "generate_dialogue_stream_with_timestamps": [["xi_api_key"]],
    "generate_dialogue_with_timestamps": [["xi_api_key"]],
    "convert_voice": [["xi_api_key"]],
    "convert_speech_to_speech_stream": [["xi_api_key"]],
    "generate_voice_previews": [["xi_api_key"]],
    "create_voice": [["xi_api_key"]],
    "design_voice": [["xi_api_key"]],
    "remix_voice": [["xi_api_key"]],
    "stream_voice_preview": [["xi_api_key"]],
    "get_subscription_info": [["xi_api_key"]],
    "get_user": [["xi_api_key"]],
    "list_voices": [["xi_api_key"]],
    "get_default_voice_settings": [["xi_api_key"]],
    "get_voice_settings": [["xi_api_key"]],
    "get_voice": [["xi_api_key"]],
    "delete_voice": [["xi_api_key"]],
    "configure_voice_settings": [["xi_api_key"]],
    "create_voice_sample": [["xi_api_key"]],
    "update_voice": [["xi_api_key"]],
    "add_shared_voice": [["xi_api_key"]],
    "generate_podcast": [["xi_api_key"]],
    "apply_pronunciation_dictionaries": [["xi_api_key"]],
    "list_projects": [["xi_api_key"]],
    "create_studio_project": [["xi_api_key"]],
    "get_project": [["xi_api_key"]],
    "update_studio_project": [["xi_api_key"]],
    "delete_project": [["xi_api_key"]],
    "update_project_content": [["xi_api_key"]],
    "convert_studio_project": [["xi_api_key"]],
    "list_snapshots": [["xi_api_key"]],
    "get_snapshot": [["xi_api_key"]],
    "stream_project_snapshot_audio": [["xi_api_key"]],
    "download_snapshot_archive": [["xi_api_key"]],
    "list_chapters": [["xi_api_key"]],
    "create_chapter": [["xi_api_key"]],
    "get_chapter": [["xi_api_key"]],
    "update_chapter": [["xi_api_key"]],
    "delete_chapter": [["xi_api_key"]],
    "convert_chapter": [["xi_api_key"]],
    "list_chapter_snapshots": [["xi_api_key"]],
    "get_chapter_snapshot": [["xi_api_key"]],
    "get_chapter_snapshot_audio": [["xi_api_key"]],
    "list_muted_tracks": [["xi_api_key"]],
    "get_dubbing_resource": [["xi_api_key"]],
    "add_dubbing_language": [["xi_api_key"]],
    "create_segment": [["xi_api_key"]],
    "update_segment_language": [["xi_api_key"]],
    "reassign_segments": [["xi_api_key"]],
    "delete_dubbing_segment": [["xi_api_key"]],
    "regenerate_segment_transcriptions": [["xi_api_key"]],
    "translate_dubbing_segments": [["xi_api_key"]],
    "regenerate_dubs": [["xi_api_key"]],
    "update_speaker": [["xi_api_key"]],
    "add_speaker": [["xi_api_key"]],
    "list_similar_voices": [["xi_api_key"]],
    "render_dubbing": [["xi_api_key"]],
    "list_dubs": [["xi_api_key"]],
    "dub_media": [["xi_api_key"]],
    "get_dubbing": [["xi_api_key"]],
    "delete_dubbing": [["xi_api_key"]],
    "download_dubbed_audio": [["xi_api_key"]],
    "get_transcript_dubbing": [["xi_api_key"]],
    "list_models": [["xi_api_key"]],
    "create_audio_project": [["xi_api_key"]],
    "get_audio_native_settings": [["xi_api_key"]],
    "update_audio_native_content": [["xi_api_key"]],
    "update_audio_native_content_from_url": [["xi_api_key"]],
    "list_voices_shared": [["xi_api_key"]],
    "find_similar_voices": [["xi_api_key"]],
    "get_character_usage_metrics": [["xi_api_key"]],
    "create_pronunciation_dictionary": [["xi_api_key"]],
    "create_pronunciation_dictionary_from_rules": [["xi_api_key"]],
    "get_pronunciation_dictionary": [["xi_api_key"]],
    "update_pronunciation_dictionary": [["xi_api_key"]],
    "replace_pronunciation_rules": [["xi_api_key"]],
    "add_pronunciation_rules": [["xi_api_key"]],
    "delete_pronunciation_rules": [["xi_api_key"]],
    "download_pronunciation_dictionary_version": [["xi_api_key"]],
    "list_pronunciation_dictionaries": [["xi_api_key"]],
    "list_service_account_api_keys": [["xi_api_key"]],
    "create_service_account_api_key": [["xi_api_key"]],
    "revoke_service_account_api_key": [["xi_api_key"]],
    "list_auth_connections": [["xi_api_key"]],
    "delete_auth_connection": [["xi_api_key"]],
    "list_service_accounts": [["xi_api_key"]],
    "list_groups": [["xi_api_key"]],
    "find_group": [["xi_api_key"]],
    "remove_group_member": [["xi_api_key"]],
    "add_group_member": [["xi_api_key"]],
    "send_workspace_invite": [["xi_api_key"]],
    "send_workspace_invitations": [["xi_api_key"]],
    "revoke_workspace_invitation": [["xi_api_key"]],
    "get_resource": [["xi_api_key"]],
    "grant_resource_access": [["xi_api_key"]],
    "revoke_resource_access": [["xi_api_key"]],
    "list_workspace_webhooks": [["xi_api_key"]],
    "transcribe_audio": [["xi_api_key"]],
    "get_transcript": [["xi_api_key"]],
    "delete_transcript": [["xi_api_key"]],
    "list_evaluation_criteria": [["xi_api_key"]],
    "get_evaluation_criterion": [["xi_api_key"]],
    "update_eval_criterion": [["xi_api_key"]],
    "delete_evaluation_criterion": [["xi_api_key"]],
    "list_evaluations": [["xi_api_key"]],
    "create_evaluation": [["xi_api_key"]],
    "get_evaluation": [["xi_api_key"]],
    "list_human_agents": [["xi_api_key"]],
    "get_human_agent": [["xi_api_key"]],
    "delete_human_agent": [["xi_api_key"]],
    "list_evaluation_analytics": [["xi_api_key"]],
    "get_criterion_analytics": [["xi_api_key"]],
    "get_agent_analytics": [["xi_api_key"]],
    "align_audio_to_text": [["xi_api_key"]],
    "get_agent_conversation_signed_link": [["xi_api_key"]],
    "initiate_outbound_call": [["xi_api_key"]],
    "initiate_twilio_call": [["xi_api_key"]],
    "initiate_whatsapp_call": [["xi_api_key"]],
    "send_whatsapp_message": [["xi_api_key"]],
    "create_agent_route": [["xi_api_key"]],
    "list_agent_summaries": [["xi_api_key"]],
    "get_agent": [["xi_api_key"]],
    "update_agent_settings": [["xi_api_key"]],
    "delete_agent": [["xi_api_key"]],
    "get_agent_widget_config": [["xi_api_key"]],
    "get_agent_share_link": [["xi_api_key"]],
    "upload_agent_avatar": [["xi_api_key"]],
    "list_agents": [["xi_api_key"]],
    "get_knowledge_base_size": [["xi_api_key"]],
    "estimate_agent_llm_cost": [["xi_api_key"]],
    "duplicate_agent": [["xi_api_key"]],
    "simulate_agent_conversation": [["xi_api_key"]],
    "simulate_conversation_stream": [["xi_api_key"]],
    "create_agent_test": [["xi_api_key"]],
    "get_agent_test": [["xi_api_key"]],
    "update_agent_test": [["xi_api_key"]],
    "delete_agent_test": [["xi_api_key"]],
    "fetch_agent_response_test_summaries": [["xi_api_key"]],
    "list_agent_tests": [["xi_api_key"]],
    "list_test_invocations": [["xi_api_key"]],
    "run_agent_tests": [["xi_api_key"]],
    "get_test_invocation": [["xi_api_key"]],
    "resubmit_tests": [["xi_api_key"]],
    "list_conversations": [["xi_api_key"]],
    "list_conversation_users": [["xi_api_key"]],
    "get_conversation": [["xi_api_key"]],
    "delete_conversation": [["xi_api_key"]],
    "get_conversation_audio": [["xi_api_key"]],
    "submit_conversation_feedback": [["xi_api_key"]],
    "search_conversation_messages": [["xi_api_key"]],
    "search_conversation_messages_semantic": [["xi_api_key"]],
    "list_phone_numbers": [["xi_api_key"]],
    "import_phone_number": [["xi_api_key"]],
    "get_phone_number": [["xi_api_key"]],
    "update_phone_number": [["xi_api_key"]],
    "delete_phone_number": [["xi_api_key"]],
    "calculate_llm_expected_cost": [["xi_api_key"]],
    "list_llms": [["xi_api_key"]],
    "upload_file": [["xi_api_key"]],
    "delete_conversation_file": [["xi_api_key"]],
    "get_conversation_live_count": [["xi_api_key"]],
    "get_knowledge_base_summaries": [["xi_api_key"]],
    "list_knowledge_bases": [["xi_api_key"]],
    "create_knowledge_base_document_from_url": [["xi_api_key"]],
    "upload_knowledge_base_document": [["xi_api_key"]],
    "add_text_document": [["xi_api_key"]],
    "create_folder": [["xi_api_key"]],
    "retrieve_knowledge_base_document": [["xi_api_key"]],
    "rename_document": [["xi_api_key"]],
    "delete_knowledge_base_document": [["xi_api_key"]],
    "get_rag_index_overview": [["xi_api_key"]],
    "batch_compute_rag_indexes": [["xi_api_key"]],
    "refresh_knowledge_base_document": [["xi_api_key"]],
    "list_rag_indexes": [["xi_api_key"]],
    "index_knowledge_base_document": [["xi_api_key"]],
    "delete_rag_index": [["xi_api_key"]],
    "list_dependent_agents": [["xi_api_key"]],
    "retrieve_knowledge_base_document_content": [["xi_api_key"]],
    "get_knowledge_base_source_file_url": [["xi_api_key"]],
    "retrieve_knowledge_base_chunk": [["xi_api_key"]],
    "move_knowledge_base_document": [["xi_api_key"]],
    "move_knowledge_base_entities": [["xi_api_key"]],
    "list_tools": [["xi_api_key"]],
    "create_tool": [["xi_api_key"]],
    "get_tool": [["xi_api_key"]],
    "update_tool": [["xi_api_key"]],
    "delete_tool": [["xi_api_key"]],
    "list_dependent_agents_tool": [["xi_api_key"]],
    "create_workspace_secret": [["xi_api_key"]],
    "update_secret": [["xi_api_key"]],
    "delete_secret": [["xi_api_key"]],
    "submit_batch_calls": [["xi_api_key"]],
    "list_batch_calls": [["xi_api_key"]],
    "get_batch_call": [["xi_api_key"]],
    "delete_batch_call": [["xi_api_key"]],
    "cancel_batch_call": [["xi_api_key"]],
    "retry_batch_call": [["xi_api_key"]],
    "initiate_outbound_sip_call": [["xi_api_key"]],
    "list_mcp_servers": [["xi_api_key"]],
    "register_mcp_server": [["xi_api_key"]],
    "get_mcp_server": [["xi_api_key"]],
    "configure_mcp_server": [["xi_api_key"]],
    "delete_mcp_server": [["xi_api_key"]],
    "list_mcp_server_tools": [["xi_api_key"]],
    "approve_mcp_server_tool": [["xi_api_key"]],
    "revoke_mcp_server_tool_approval": [["xi_api_key"]],
    "create_tool_config_override": [["xi_api_key"]],
    "get_tool_config_override": [["xi_api_key"]],
    "override_mcp_tool_config": [["xi_api_key"]],
    "get_whatsapp_account": [["xi_api_key"]],
    "update_whatsapp_account": [["xi_api_key"]],
    "delete_whatsapp_account": [["xi_api_key"]],
    "list_whatsapp_accounts": [["xi_api_key"]],
    "list_agent_branches": [["xi_api_key"]],
    "create_agent_branch": [["xi_api_key"]],
    "get_agent_branch": [["xi_api_key"]],
    "update_branch": [["xi_api_key"]],
    "merge_branch": [["xi_api_key"]],
    "deploy_agent": [["xi_api_key"]],
    "create_agent_draft": [["xi_api_key"]],
    "delete_agent_draft": [["xi_api_key"]],
    "list_environment_variables": [["xi_api_key"]],
    "create_environment_variable": [["xi_api_key"]],
    "get_environment_variable": [["xi_api_key"]],
    "update_environment_variable": [["xi_api_key"]],
    "generate_composition_plan": [["xi_api_key"]],
    "compose_song": [["xi_api_key"]],
    "compose_song_detailed": [["xi_api_key"]],
    "compose_music": [["xi_api_key"]],
    "upload_song": [["xi_api_key"]],
    "separate_song_stems": [["xi_api_key"]],
    "create_voice_pvc": [["xi_api_key"]],
    "update_voice_pvc": [["xi_api_key"]],
    "add_voice_samples": [["xi_api_key"]],
    "update_voice_sample": [["xi_api_key"]],
    "remove_voice_sample": [["xi_api_key"]],
    "get_voice_sample_audio": [["xi_api_key"]],
    "get_voice_sample_waveform": [["xi_api_key"]],
    "get_speaker_separation_status": [["xi_api_key"]],
    "separate_speakers": [["xi_api_key"]],
    "get_speaker_audio": [["xi_api_key"]],
    "train_voice": [["xi_api_key"]],
    "submit_voice_verification": [["xi_api_key"]]
}
