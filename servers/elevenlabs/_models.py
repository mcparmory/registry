"""
Elevenlabs MCP Server - Pydantic Models

Generated: 2026-05-11 19:45:03 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import AfterValidator, Field, RootModel


def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v

def _check_property_names_c4546ddd(v: dict) -> dict:
    """Validate all dict keys satisfy: key in ('gpt-4o-mini', 'gpt-4o', 'gpt-4', 'gpt-4-turbo', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5.2-chat-latest', 'gpt-5-mini', 'gpt-5-nano', 'gpt-3.5-turbo', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'claude-sonnet-4-5', 'claude-sonnet-4-6', 'claude-sonnet-4', 'claude-haiku-4-5', 'claude-3-7-sonnet', 'claude-3-5-sonnet', 'claude-3-5-sonnet-v1', 'claude-3-haiku', 'grok-beta', 'custom-llm', 'qwen3-4b', 'qwen3-30b-a3b', 'gpt-oss-20b', 'gpt-oss-120b', 'glm-45-air-fp8', 'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.0-flash-lite-001', 'gemini-2.0-flash-001', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001', 'gemini-1.5-pro-002', 'gemini-1.5-pro-001', 'claude-sonnet-4@20250514', 'claude-sonnet-4-5@20250929', 'claude-haiku-4-5@20251001', 'claude-3-7-sonnet@20250219', 'claude-3-5-sonnet@20240620', 'claude-3-5-sonnet-v2@20241022', 'claude-3-haiku@20240307', 'gpt-5-2025-08-07', 'gpt-5.1-2025-11-13', 'gpt-5.2-2025-12-11', 'gpt-5-mini-2025-08-07', 'gpt-5-nano-2025-08-07', 'gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'gpt-4.1-nano-2025-04-14', 'gpt-4o-mini-2024-07-18', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4-0613', 'gpt-4-0314', 'gpt-4-turbo-2024-04-09', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-1106', 'watt-tool-8b', 'watt-tool-70b')."""
    for _key in v:
        if _key not in ('gpt-4o-mini', 'gpt-4o', 'gpt-4', 'gpt-4-turbo', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5.2-chat-latest', 'gpt-5-mini', 'gpt-5-nano', 'gpt-3.5-turbo', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'claude-sonnet-4-5', 'claude-sonnet-4-6', 'claude-sonnet-4', 'claude-haiku-4-5', 'claude-3-7-sonnet', 'claude-3-5-sonnet', 'claude-3-5-sonnet-v1', 'claude-3-haiku', 'grok-beta', 'custom-llm', 'qwen3-4b', 'qwen3-30b-a3b', 'gpt-oss-20b', 'gpt-oss-120b', 'glm-45-air-fp8', 'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.0-flash-lite-001', 'gemini-2.0-flash-001', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001', 'gemini-1.5-pro-002', 'gemini-1.5-pro-001', 'claude-sonnet-4@20250514', 'claude-sonnet-4-5@20250929', 'claude-haiku-4-5@20251001', 'claude-3-7-sonnet@20250219', 'claude-3-5-sonnet@20240620', 'claude-3-5-sonnet-v2@20241022', 'claude-3-haiku@20240307', 'gpt-5-2025-08-07', 'gpt-5.1-2025-11-13', 'gpt-5.2-2025-12-11', 'gpt-5-mini-2025-08-07', 'gpt-5-nano-2025-08-07', 'gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'gpt-4.1-nano-2025-04-14', 'gpt-4o-mini-2024-07-18', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4-0613', 'gpt-4-0314', 'gpt-4-turbo-2024-04-09', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-1106', 'watt-tool-8b', 'watt-tool-70b'):
            raise ValueError(f"key '{_key}' does not satisfy: key in ('gpt-4o-mini', 'gpt-4o', 'gpt-4', 'gpt-4-turbo', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5.2-chat-latest', 'gpt-5-mini', 'gpt-5-nano', 'gpt-3.5-turbo', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'claude-sonnet-4-5', 'claude-sonnet-4-6', 'claude-sonnet-4', 'claude-haiku-4-5', 'claude-3-7-sonnet', 'claude-3-5-sonnet', 'claude-3-5-sonnet-v1', 'claude-3-haiku', 'grok-beta', 'custom-llm', 'qwen3-4b', 'qwen3-30b-a3b', 'gpt-oss-20b', 'gpt-oss-120b', 'glm-45-air-fp8', 'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.0-flash-lite-001', 'gemini-2.0-flash-001', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001', 'gemini-1.5-pro-002', 'gemini-1.5-pro-001', 'claude-sonnet-4@20250514', 'claude-sonnet-4-5@20250929', 'claude-haiku-4-5@20251001', 'claude-3-7-sonnet@20250219', 'claude-3-5-sonnet@20240620', 'claude-3-5-sonnet-v2@20241022', 'claude-3-haiku@20240307', 'gpt-5-2025-08-07', 'gpt-5.1-2025-11-13', 'gpt-5.2-2025-12-11', 'gpt-5-mini-2025-08-07', 'gpt-5-nano-2025-08-07', 'gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'gpt-4.1-nano-2025-04-14', 'gpt-4o-mini-2024-07-18', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4-0613', 'gpt-4-0314', 'gpt-4-turbo-2024-04-09', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-1106', 'watt-tool-8b', 'watt-tool-70b')")
    return v

def _check_property_names_9463730f(v: dict) -> dict:
    """Validate all dict keys satisfy: key in ('admin', 'editor', 'commenter', 'viewer')."""
    for _key in v:
        if _key not in ('admin', 'editor', 'commenter', 'viewer'):
            raise ValueError(f"key '{_key}' does not satisfy: key in ('admin', 'editor', 'commenter', 'viewer')")
    return v



__all__ = [
    "AddChapterRequest",
    "AddFromFileRequest",
    "AddFromRulesRequest",
    "AddLanguageRequest",
    "AddMcpServerToolApprovalRouteRequest",
    "AddMcpToolConfigOverrideRouteRequest",
    "AddMemberRequest",
    "AddProjectRequest",
    "AddPvcVoiceSamplesRequest",
    "AddRulesRequest",
    "AddSharingVoiceRequest",
    "AddToolRouteRequest",
    "AddVoiceRequest",
    "AudioIsolationRequest",
    "AudioIsolationStreamRequest",
    "AudioNativeProjectUpdateContentEndpointRequest",
    "AudioNativeUpdateContentFromUrlRequest",
    "CancelBatchCallRequest",
    "CancelFileUploadRouteRequest",
    "ComposeDetailedRequest",
    "ComposePlanRequest",
    "ConvertChapterEndpointRequest",
    "ConvertProjectEndpointRequest",
    "CreateAgentDeploymentRouteRequest",
    "CreateAgentDraftRouteRequest",
    "CreateAgentResponseTestRouteRequest",
    "CreateAgentRouteRequest",
    "CreateAudioNativeProjectRequest",
    "CreateBatchCallRequest",
    "CreateBranchRouteRequest",
    "CreateClipRequest",
    "CreateDubbingRequest",
    "CreateEnvironmentVariableRequest",
    "CreateFileDocumentRouteRequest",
    "CreateFolderRouteRequest",
    "CreateMcpServerRouteRequest",
    "CreatePhoneNumberRouteRequest",
    "CreatePodcastRequest",
    "CreatePvcVoiceRequest",
    "CreateSecretRouteRequest",
    "CreateServiceAccountApiKeyRequest",
    "CreateSpeakerRequest",
    "CreateTextDocumentRouteRequest",
    "CreateUrlDocumentRouteRequest",
    "CreateVoiceRequest",
    "DeleteAgentDraftRouteRequest",
    "DeleteAgentRouteRequest",
    "DeleteAuthConnectionRequest",
    "DeleteBatchCallRequest",
    "DeleteChapterEndpointRequest",
    "DeleteChatResponseTestRouteRequest",
    "DeleteConversationRouteRequest",
    "DeleteDubbingRequest",
    "DeleteEvalCriterionRouteRequest",
    "DeleteHumanAgentRouteRequest",
    "DeleteInviteRequest",
    "DeleteKnowledgeBaseDocumentRequest",
    "DeleteMcpServerRouteRequest",
    "DeletePhoneNumberRouteRequest",
    "DeleteProjectRequest",
    "DeletePvcVoiceSampleRequest",
    "DeleteRagIndexRequest",
    "DeleteSampleRequest",
    "DeleteSecretRouteRequest",
    "DeleteSegmentRequest",
    "DeleteServiceAccountApiKeyRequest",
    "DeleteSpeechHistoryItemRequest",
    "DeleteToolRouteRequest",
    "DeleteTranscriptByIdRequest",
    "DeleteVoiceRequest",
    "DeleteWhatsappAccountRequest",
    "DownloadSpeechHistoryItemsRequest",
    "DubRequest",
    "DuplicateAgentRouteRequest",
    "EditChapterRequest",
    "EditProjectContentRequest",
    "EditProjectRequest",
    "EditPvcVoiceRequest",
    "EditPvcVoiceSampleRequest",
    "EditVoiceRequest",
    "EditVoiceSettingsRequest",
    "ForcedAlignmentRequest",
    "GenerateRequest",
    "GetAgentAnalyticsRouteRequest",
    "GetAgentKnowledgeBaseSizeRequest",
    "GetAgentKnowledgeBaseSummariesRouteRequest",
    "GetAgentLinkRouteRequest",
    "GetAgentLlmExpectedCostCalculationRequest",
    "GetAgentResponseTestRouteRequest",
    "GetAgentResponseTestsSummariesRouteRequest",
    "GetAgentRouteRequest",
    "GetAgentsRouteRequest",
    "GetAgentSummariesRouteRequest",
    "GetAgentWidgetRouteRequest",
    "GetAudioFromSampleRequest",
    "GetAudioFullFromSpeechHistoryItemRequest",
    "GetAudioNativeProjectSettingsEndpointRequest",
    "GetBatchCallRequest",
    "GetBranchesRouteRequest",
    "GetBranchRouteRequest",
    "GetChapterByIdEndpointRequest",
    "GetChapterSnapshotEndpointRequest",
    "GetChapterSnapshotsRequest",
    "GetChaptersRequest",
    "GetConversationAudioRouteRequest",
    "GetConversationHistoriesRouteRequest",
    "GetConversationHistoryRouteRequest",
    "GetConversationSignedLinkRequest",
    "GetConversationUsersRouteRequest",
    "GetCriterionAnalyticsRouteRequest",
    "GetDocumentationChunkFromKnowledgeBaseRequest",
    "GetDocumentationFromKnowledgeBaseRequest",
    "GetDubbedFileRequest",
    "GetDubbedMetadataRequest",
    "GetDubbingResourceRequest",
    "GetDubbingTranscriptsRequest",
    "GetEnvironmentVariableRequest",
    "GetEvalCriterionRouteRequest",
    "GetEvaluationAnalyticsRouteRequest",
    "GetEvaluationRouteRequest",
    "GetHumanAgentRouteRequest",
    "GetKnowledgeBaseContentRequest",
    "GetKnowledgeBaseDependentAgentsRequest",
    "GetKnowledgeBaseListRouteRequest",
    "GetKnowledgeBaseSourceFileUrlRequest",
    "GetLibraryVoicesRequest",
    "GetLiveCountRequest",
    "GetMcpRouteRequest",
    "GetMcpToolConfigOverrideRouteRequest",
    "GetOrCreateRagIndexesRequest",
    "GetPhoneNumberRouteRequest",
    "GetProjectByIdRequest",
    "GetProjectMutedTracksEndpointRequest",
    "GetProjectSnapshotEndpointRequest",
    "GetProjectSnapshotsRequest",
    "GetPronunciationDictionariesMetadataRequest",
    "GetPronunciationDictionaryMetadataRequest",
    "GetPronunciationDictionaryVersionPlsRequest",
    "GetPublicLlmExpectedCostCalculationRequest",
    "GetPvcSampleAudioRequest",
    "GetPvcSampleSpeakersRequest",
    "GetPvcSampleVisualWaveformRequest",
    "GetRagIndexesRequest",
    "GetResourceMetadataRequest",
    "GetServiceAccountApiKeysRouteRequest",
    "GetSimilarLibraryVoicesRequest",
    "GetSimilarVoicesForSpeakerRequest",
    "GetSpeakerAudioRequest",
    "GetSpeechHistoryItemByIdRequest",
    "GetSpeechHistoryRequest",
    "GetTestInvocationRouteRequest",
    "GetToolDependentAgentsRouteRequest",
    "GetToolRouteRequest",
    "GetToolsRouteRequest",
    "GetTranscriptByIdRequest",
    "GetUserVoicesV2Request",
    "GetVoiceByIdRequest",
    "GetVoiceSettingsRequest",
    "GetWhatsappAccountRequest",
    "GetWorkspaceBatchCallsRequest",
    "GetWorkspaceWebhooksRouteRequest",
    "HandleSipTrunkOutboundCallRequest",
    "HandleTwilioOutboundCallRequest",
    "InviteUserRequest",
    "InviteUsersBulkRequest",
    "ListChatResponseTestsRouteRequest",
    "ListDubsRequest",
    "ListEnvironmentVariablesRequest",
    "ListEvaluationsRouteRequest",
    "ListHumanAgentsRouteRequest",
    "ListMcpServerToolsRouteRequest",
    "ListTestInvocationsRouteRequest",
    "MergeBranchIntoTargetRequest",
    "MigrateSegmentsRequest",
    "PatchAgentSettingsRouteRequest",
    "PatchPronunciationDictionaryRequest",
    "PostAgentAvatarRouteRequest",
    "PostConversationFeedbackRouteRequest",
    "PostKnowledgeBaseBulkMoveRouteRequest",
    "PostKnowledgeBaseMoveRouteRequest",
    "RagIndexStatusRequest",
    "RefreshUrlDocumentRouteRequest",
    "RegisterTwilioCallRequest",
    "RemoveMcpServerToolApprovalRouteRequest",
    "RemoveMemberRequest",
    "RemoveRulesRequest",
    "RenderRequest",
    "RequestPvcManualVerificationRequest",
    "ResubmitTestsRouteRequest",
    "RetryBatchCallRequest",
    "RunAgentTestSuiteRouteRequest",
    "RunConversationSimulationRouteRequest",
    "RunConversationSimulationRouteStreamRequest",
    "RunPvcVoiceTrainingRequest",
    "SearchGroupsRequest",
    "SeparateSongStemsRequest",
    "SetRulesRequest",
    "ShareResourceEndpointRequest",
    "SmartSearchConversationMessagesRouteRequest",
    "SoundGenerationRequest",
    "SpeechToSpeechFullRequest",
    "SpeechToSpeechStreamRequest",
    "SpeechToTextRequest",
    "StartSpeakerSeparationRequest",
    "StreamChapterSnapshotAudioRequest",
    "StreamComposeRequest",
    "StreamProjectSnapshotArchiveEndpointRequest",
    "StreamProjectSnapshotAudioEndpointRequest",
    "TextSearchConversationMessagesRouteRequest",
    "TextToDialogueFullWithTimestampsRequest",
    "TextToDialogueRequest",
    "TextToDialogueStreamRequest",
    "TextToDialogueStreamWithTimestampsRequest",
    "TextToSpeechFullRequest",
    "TextToSpeechFullWithTimestampsRequest",
    "TextToSpeechStreamRequest",
    "TextToSpeechStreamWithTimestampsRequest",
    "TextToVoiceDesignRequest",
    "TextToVoicePreviewStreamRequest",
    "TextToVoiceRemixRequest",
    "TextToVoiceRequest",
    "TranscribeRequest",
    "TranslateRequest",
    "TriggerEvaluationRouteRequest",
    "UnshareResourceEndpointRequest",
    "UpdateAgentResponseTestRouteRequest",
    "UpdateBranchRouteRequest",
    "UpdateDocumentRouteRequest",
    "UpdateEnvironmentVariableRequest",
    "UpdateEvalCriterionRouteRequest",
    "UpdateMcpServerConfigRouteRequest",
    "UpdateMcpToolConfigOverrideRouteRequest",
    "UpdatePhoneNumberRouteRequest",
    "UpdatePronunciationDictionariesRequest",
    "UpdateSecretRouteRequest",
    "UpdateSegmentLanguageRequest",
    "UpdateSpeakerRequest",
    "UpdateToolRouteRequest",
    "UpdateWhatsappAccountRequest",
    "UploadFileRouteRequest",
    "UploadSongRequest",
    "UsageCharactersRequest",
    "WhatsappOutboundCallRequest",
    "WhatsappOutboundMessageRequest",
    "AgentDeploymentRequestItem",
    "AgentFailureResponseExample",
    "AgentSuccessfulResponseExample",
    "AuthConnectionLocator",
    "BackupLlmDefault",
    "BackupLlmDisabled",
    "BackupLlmOverride",
    "ChapterContentBlockInputModel",
    "ClientToolConfigInput",
    "ConstantSchemaOverride",
    "ConvAiDynamicVariable",
    "ConvAiEnvVarLocator",
    "ConvAiSecretLocator",
    "ConvAiUserSecretDbModel",
    "ConversationHistoryTranscriptCommonModelInput",
    "CreateAgentRouteBodyConversationConfig",
    "CreateAgentRouteBodyPlatformSettings",
    "CreateAgentRouteBodyWorkflow",
    "CriterionItemRequest",
    "DataExtractionFieldRequest",
    "DialogueInput",
    "DynamicVariableAssignment",
    "DynamicVariableSchemaOverride",
    "EnvironmentAuthConnectionLocator",
    "EnvironmentVariableAuthConnectionValueRequest",
    "EnvironmentVariableSecretValueRequest",
    "ExportOptions",
    "GetOrCreateRagIndexRequestModel",
    "InboundSipTrunkConfigRequestModel",
    "KnowledgeBaseLocator",
    "LlmSchemaOverride",
    "McpToolApprovalHash",
    "McpToolConfigInput",
    "McpToolConfigOverride",
    "OutboundCallRecipient",
    "OutboundSipTrunkConfigRequestModel",
    "PodcastBulletinMode",
    "PodcastConversationMode",
    "PodcastTextSource",
    "PodcastUrlSource",
    "PromptEvaluationCriteria",
    "PronunciationDictionaryAliasRuleRequestModel",
    "PronunciationDictionaryPhonemeRuleRequestModel",
    "PronunciationDictionaryVersionLocatorDbModel",
    "PronunciationDictionaryVersionLocatorRequestModel",
    "RegionConfigRequest",
    "ResubmitTestsRouteBodyAgentConfigOverride",
    "RunAgentTestSuiteRouteBodyAgentConfigOverride",
    "SingleTestRunRequestModel",
    "SongSection",
    "SystemToolConfigInput",
    "TestFromConversationMetadataInput",
    "ToolMockConfig",
    "UnitTestToolCallEvaluationModelInput",
    "WebhookToolConfigInput",
    "WhatsAppTemplateBodyComponentParams",
    "WhatsAppTemplateButtonComponentParams",
    "WhatsAppTemplateHeaderComponentParams",
    "WorkflowEdgeModelInput",
    "WorkflowEndNodeModelInput",
    "WorkflowOverrideAgentNodeModelInput",
    "WorkflowPhoneNumberNodeModelInput",
    "WorkflowStandaloneAgentNodeModelInput",
    "WorkflowStartNodeModelInput",
    "WorkflowToolNodeModelInput",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_speech_history
class GetSpeechHistoryRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of history items to return per request. Useful for controlling response size and pagination.")
    start_after_history_item_id: str | None = Field(default=None, description="History item ID to start pagination after. Use this to fetch subsequent pages of results when working with large collections.")
    voice_id: str | None = Field(default=None, description="Filter results to a specific voice. Retrieve available voice IDs from the list voices endpoint.")
    model_id: str | None = Field(default=None, description="Filter results to a specific text-to-speech model.", examples=['eleven_turbo_v2', 'eleven_multilingual_v2'])
    date_before_unix: int | None = Field(default=None, description="Filter to history items created before this date (exclusive). Provide as a Unix timestamp.", examples=[1640995200])
    date_after_unix: int | None = Field(default=None, description="Filter to history items created on or after this date (inclusive). Provide as a Unix timestamp.", examples=[1640995200])
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Order results by creation date in ascending or descending order.", examples=['desc', 'asc'])
    source: Literal["TTS", "STS"] | None = Field(default=None, description="Filter results by the source that generated the audio item.", examples=['TTS'])
class GetSpeechHistoryRequest(StrictModel):
    """Retrieve a paginated list of your generated audio items with optional filtering by voice, model, date range, and source. Results are ordered by creation date."""
    query: GetSpeechHistoryRequestQuery | None = None

# Operation: get_speech_history_item
class GetSpeechHistoryItemByIdRequestPath(StrictModel):
    history_item_id: str = Field(default=..., description="The unique identifier of the history item to retrieve. You can obtain available history item IDs by calling the list speech history operation.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetSpeechHistoryItemByIdRequest(StrictModel):
    """Retrieves a specific speech synthesis history item by its ID. Use this to access details about a previously generated speech synthesis request."""
    path: GetSpeechHistoryItemByIdRequestPath

# Operation: delete_history_item
class DeleteSpeechHistoryItemRequestPath(StrictModel):
    history_item_id: str = Field(default=..., description="The unique identifier of the history item to delete. You can retrieve available history item IDs using the list history items endpoint.", examples=['VW7YKqPnjY4h39yTbx2L'])
class DeleteSpeechHistoryItemRequest(StrictModel):
    """Delete a speech history item by its ID. This removes the item from your speech synthesis history."""
    path: DeleteSpeechHistoryItemRequestPath

# Operation: get_speech_history_audio
class GetAudioFullFromSpeechHistoryItemRequestPath(StrictModel):
    history_item_id: str = Field(default=..., description="The unique identifier of the speech history item from which to retrieve the audio file.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetAudioFullFromSpeechHistoryItemRequest(StrictModel):
    """Retrieve the audio file associated with a specific speech synthesis history item. Use the history item ID obtained from the speech history list to download the generated audio."""
    path: GetAudioFullFromSpeechHistoryItemRequestPath

# Operation: download_speech_items
class DownloadSpeechHistoryItemsRequestBody(StrictModel):
    history_item_ids: list[str] = Field(default=..., description="List of history item IDs to download. Retrieve available IDs and metadata from the list speech history endpoint. Order is preserved in the output archive.")
    output_format: str | None = Field(default=None, description="Audio file format for transcoding. Specify the desired output format for the downloaded audio files.")
class DownloadSpeechHistoryItemsRequest(StrictModel):
    """Download one or more speech history items as audio files. Single items are returned as individual audio files, while multiple items are packaged into a .zip archive."""
    body: DownloadSpeechHistoryItemsRequestBody

# Operation: generate_sound
class SoundGenerationRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio codec, sample rate, and bitrate for the generated sound. Higher bitrates and sample rates require appropriate subscription tiers.")
class SoundGenerationRequestBody(StrictModel):
    text: str = Field(default=..., description="Detailed text description of the sound effect to generate. Be descriptive about the audio characteristics, environment, and desired qualities.", examples=['A large, ancient wooden door slowly opening in an eerie, abandoned castle..'])
    loop: bool | None = Field(default=None, description="Enable seamless looping for the generated sound effect. Only supported with the eleven_text_to_sound_v2 model.")
    duration_seconds: float | None = Field(default=None, description="Target duration of the generated sound in seconds. If not specified, the optimal duration will be automatically determined from the text description.")
    prompt_influence: float | None = Field(default=None, description="Controls how strictly the generation adheres to the text description. Higher values produce more consistent results but less variation; lower values allow more creative freedom.")
    model_id: str | None = Field(default=None, description="The AI model to use for sound generation. Determines the quality and capabilities of the generated audio.", examples=['eleven_text_to_sound_v2'])
class SoundGenerationRequest(StrictModel):
    """Generate realistic sound effects from text descriptions using advanced AI models. Perfect for video production, voice-overs, and game audio."""
    query: SoundGenerationRequestQuery | None = None
    body: SoundGenerationRequestBody

# Operation: isolate_audio
class AudioIsolationRequestBody(StrictModel):
    audio: str = Field(default=..., description="Base64-encoded file content for upload. The audio file to process for noise removal and vocal/speech isolation. Accepts binary audio data in common formats.", json_schema_extra={'format': 'byte'})
class AudioIsolationRequest(StrictModel):
    """Removes background noise and isolates vocals or speech from an audio file. Returns the cleaned audio with background noise suppressed."""
    body: AudioIsolationRequestBody

# Operation: isolate_audio_stream
class AudioIsolationStreamRequestBody(StrictModel):
    audio: str = Field(default=..., description="Base64-encoded file content for upload. The audio file to process for isolation. The audio data should be provided in binary format.", json_schema_extra={'format': 'byte'})
class AudioIsolationStreamRequest(StrictModel):
    """Removes background noise from audio and streams the isolated vocals or speech. Processes the provided audio file and returns the cleaned result as a stream."""
    body: AudioIsolationStreamRequestBody

# Operation: delete_voice_sample
class DeleteSampleRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice containing the sample to delete.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the sample to delete from the specified voice.", examples=['VW7YKqPnjY4h39yTbx2L'])
class DeleteSampleRequest(StrictModel):
    """Permanently removes a sample from a voice by its ID. This action cannot be undone."""
    path: DeleteSampleRequestPath

# Operation: retrieve_voice_sample_audio
class GetAudioFromSampleRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice containing the sample. You can retrieve available voice IDs from the voices list endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the sample within the specified voice. You can retrieve available sample IDs by fetching the voice details endpoint.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetAudioFromSampleRequest(StrictModel):
    """Retrieves the audio file associated with a specific sample attached to a voice. Use this to download or access audio data for voice samples."""
    path: GetAudioFromSampleRequestPath

# Operation: generate_speech
class TextToSpeechFullRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to use for speech generation. Available voices can be retrieved from the voices endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class TextToSpeechFullRequestQuery(StrictModel):
    output_format: Literal["alaw_8000", "mp3_22050_32", "mp3_24000_48", "mp3_44100_128", "mp3_44100_192", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "opus_48000_128", "opus_48000_192", "opus_48000_32", "opus_48000_64", "opus_48000_96", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "pcm_8000", "ulaw_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000", "wav_8000"] | None = Field(default=None, description="The audio format and quality for the generated speech, specified as codec_sample_rate_bitrate. Higher bitrates and sample rates require higher subscription tiers. Defaults to MP3 at 44.1kHz with 128kbps bitrate.")
class TextToSpeechFullRequestBodyVoiceSettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls voice consistency and emotional range. Lower values (closer to 0) produce more varied emotional expression, while higher values (closer to 1) create more consistent but potentially monotonous speech.", ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Controls how closely the generated speech adheres to the original voice characteristics. Higher values maintain stronger voice similarity, while lower values allow more variation.", ge=0.0, le=1.0)
    style: float | None = Field(default=None, validation_alias="style", serialization_alias="style", description="Amplifies the stylistic characteristics of the voice. A value of 0 applies no style exaggeration. Higher values increase style intensity but may increase latency and computational usage.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Adjusts speech playback speed. A value of 1.0 is normal speed; values below 1.0 slow down speech, while values above 1.0 speed it up.")
class TextToSpeechFullRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content to be converted into speech.", examples=['This is a test for the API of ElevenLabs.'])
    model_id: str | None = Field(default=None, description="The AI model to use for speech generation. The model must support text-to-speech capability. Defaults to the multilingual v2 model.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce a specific language for the model and text normalization. The model must support the specified language or an error will be returned.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="A list of pronunciation dictionary locators to apply to the text in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    previous_request_ids: list[str] | None = Field(default=None, description="Request IDs of previously generated audio samples to maintain continuity when splitting large tasks. Improves speech flow when combining multiple generations. Maximum of 3 request IDs. Works best with the same model across generations.", examples=[['09bOJkdYVjKy2oOiiVtR', '0p2uKqOnZyce22SPZ9d5', '1KYvY8WZAKmcjCJ1mvVB']])
    next_request_ids: list[str] | None = Field(default=None, description="Request IDs of audio samples that follow this generation. Useful for maintaining natural flow when regenerating a sample within a sequence. Maximum of 3 request IDs. Works best with the same model across generations.", examples=[['3tPgBrD1UdW3snUkGw1K', '4D1jAxiRFkolBNUGzXkU', '4c8Z4aWliVR2oipYRXhj']])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always applies normalization (e.g., spelling out numbers), and 'off' skips normalization entirely.", examples=[True])
    apply_language_text_normalization: bool | None = Field(default=None, description="Enables language-specific text normalization for improved pronunciation in supported languages. Currently only supported for Japanese. Warning: may significantly increase request latency.", examples=[True])
    voice_settings: TextToSpeechFullRequestBodyVoiceSettings | None = None
class TextToSpeechFullRequest(StrictModel):
    """Converts text into natural-sounding speech using a selected voice and returns audio in your preferred format. Supports voice customization through stability, similarity, style, and speed controls, with optional pronunciation dictionaries and continuity features for multi-part audio generation."""
    path: TextToSpeechFullRequestPath
    query: TextToSpeechFullRequestQuery | None = None
    body: TextToSpeechFullRequestBody

# Operation: generate_speech_with_timestamps
class TextToSpeechFullWithTimestampsRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The voice identifier to use for speech generation. Available voices can be retrieved from the voices endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class TextToSpeechFullWithTimestampsRequestQuery(StrictModel):
    output_format: Literal["alaw_8000", "mp3_22050_32", "mp3_24000_48", "mp3_44100_128", "mp3_44100_192", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "opus_48000_128", "opus_48000_192", "opus_48000_32", "opus_48000_64", "opus_48000_96", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "pcm_8000", "ulaw_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000", "wav_8000"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and certain formats require higher subscription tiers.")
class TextToSpeechFullWithTimestampsRequestBodyVoiceSettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control ranging from 0 (high emotional range) to 1 (monotonous). Lower values produce more expressive speech with greater variation.", ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Voice similarity control ranging from 0 to 1. Higher values make the AI adhere more closely to the original voice characteristics.", ge=0.0, le=1.0)
    style: float | None = Field(default=None, validation_alias="style", serialization_alias="style", description="Style exaggeration level for the voice. Non-zero values amplify the speaker's style but increase computational resources and latency.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Speech speed multiplier where 1.0 is normal speed, values below 1.0 slow down speech, and values above 1.0 speed it up.")
class TextToSpeechFullWithTimestampsRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content to convert into speech audio.", examples=['This is a test for the API of ElevenLabs.'])
    model_id: str | None = Field(default=None, description="The AI model identifier to use for text-to-speech conversion. The model must support text-to-speech capability.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language processing and text normalization. The model must support the specified language.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="List of pronunciation dictionary locators to apply to the text in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    previous_request_ids: list[str] | None = Field(default=None, description="Request IDs of previously generated speech samples to maintain continuity. Used when splitting large tasks across multiple requests. Maximum of 3 request IDs. Results are best when using the same model across generations.", examples=[['09bOJkdYVjKy2oOiiVtR', '0p2uKqOnZyce22SPZ9d5', '1KYvY8WZAKmcjCJ1mvVB']])
    next_request_ids: list[str] | None = Field(default=None, description="Request IDs of subsequent speech samples to maintain continuity. Useful for regenerating a sample while preserving natural flow with following audio. Maximum of 3 request IDs. Results are best when using the same model across generations.", examples=[['3tPgBrD1UdW3snUkGw1K', '4D1jAxiRFkolBNUGzXkU', '4c8Z4aWliVR2oipYRXhj']])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization automatically, 'on' always applies it, 'off' disables it. Normalization handles conversions like spelling out numbers.", examples=[True])
    apply_language_text_normalization: bool | None = Field(default=None, description="Enable language-specific text normalization for proper pronunciation. Currently supported for Japanese only. Warning: may significantly increase request latency.", examples=[True])
    voice_settings: TextToSpeechFullWithTimestampsRequestBodyVoiceSettings | None = None
class TextToSpeechFullWithTimestampsRequest(StrictModel):
    """Convert text to speech audio with precise character-level timing information for synchronizing audio playback with text. Returns audio file and timestamp data for each character."""
    path: TextToSpeechFullWithTimestampsRequestPath
    query: TextToSpeechFullWithTimestampsRequestQuery | None = None
    body: TextToSpeechFullWithTimestampsRequestBody

# Operation: generate_speech_stream
class TextToSpeechStreamRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The voice to use for speech generation. Available voices can be retrieved from the voices endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class TextToSpeechStreamRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers.")
class TextToSpeechStreamRequestBodyVoiceSettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variation; higher values produce more consistent, monotonous speech.", ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Voice similarity adherence between 0.0 and 1.0. Controls how closely the generated speech matches the original voice characteristics.", ge=0.0, le=1.0)
    style: float | None = Field(default=None, validation_alias="style", serialization_alias="style", description="Style exaggeration intensity. Amplifies the speaker's original style characteristics. Non-zero values increase computational cost and latency.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Speech speed multiplier. Use 1.0 for normal speed, values below 1.0 to slow down, and values above 1.0 to speed up.")
class TextToSpeechStreamRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content to convert into speech.", examples=['This is a test for the API of ElevenLabs.'])
    model_id: str | None = Field(default=None, description="The AI model to use for speech generation. Must support text-to-speech capability. Query available models via the models endpoint.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language processing and text normalization. The model must support the specified language.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="Pronunciation dictionary locators to apply custom pronunciation rules. Specified as objects with pronunciation_dictionary_id and version_id. Applied in order, maximum 3 per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    previous_request_ids: list[str] | None = Field(default=None, description="Request IDs from previously generated samples to maintain speech continuity. Improves flow when splitting large tasks across multiple requests. Maximum 3 IDs, best results with consistent model.", examples=[['09bOJkdYVjKy2oOiiVtR', '0p2uKqOnZyce22SPZ9d5', '1KYvY8WZAKmcjCJ1mvVB']])
    next_request_ids: list[str] | None = Field(default=None, description="Request IDs from samples that follow this generation. Maintains natural flow when regenerating a sample within a sequence. Maximum 3 IDs, best results with consistent model.", examples=[['3tPgBrD1UdW3snUkGw1K', '4D1jAxiRFkolBNUGzXkU', '4c8Z4aWliVR2oipYRXhj']])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization automatically, 'on' always applies it, 'off' disables it. Normalization handles number spelling and similar conversions.", examples=[True])
    apply_language_text_normalization: bool | None = Field(default=None, description="Enable language-specific text normalization for proper pronunciation. Currently supported for Japanese only. Warning: significantly increases request latency.", examples=[True])
    voice_settings: TextToSpeechStreamRequestBodyVoiceSettings | None = None
class TextToSpeechStreamRequest(StrictModel):
    """Converts text into streaming audio using a specified voice. Returns audio as a continuous stream in your chosen format, ideal for real-time playback or large content."""
    path: TextToSpeechStreamRequestPath
    query: TextToSpeechStreamRequestQuery | None = None
    body: TextToSpeechStreamRequestBody

# Operation: generate_speech_stream_with_timestamps
class TextToSpeechStreamWithTimestampsRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The voice identifier to use for speech synthesis. Available voices can be retrieved from the voices endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class TextToSpeechStreamWithTimestampsRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers.")
class TextToSpeechStreamWithTimestampsRequestBodyVoiceSettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control ranging from 0 (high emotional range) to 1 (monotonous). Lower values produce more expressive speech with greater variation.", ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Voice similarity control ranging from 0 to 1, determining how closely the synthesis adheres to the original voice characteristics.", ge=0.0, le=1.0)
    style: float | None = Field(default=None, validation_alias="style", serialization_alias="style", description="Style exaggeration level (0 to 1+) that amplifies the speaker's original style. Non-zero values increase computational cost and latency.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Speech speed multiplier where 1.0 is normal speed, values below 1.0 slow down speech, and values above 1.0 accelerate it.")
class TextToSpeechStreamWithTimestampsRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content to convert into speech audio.", examples=['This is a test for the API of ElevenLabs.'])
    model_id: str | None = Field(default=None, description="The model identifier for speech synthesis. The model must support text-to-speech conversion. Available models can be queried from the models endpoint.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language-specific processing and text normalization. The model must support the specified language.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="Pronunciation dictionary locators to apply custom pronunciation rules. Accepts up to 3 locators applied in order, each containing a pronunciation_dictionary_id and version_id.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    previous_request_ids: list[str] | None = Field(default=None, description="Request IDs from previously generated speech samples to maintain continuity. Accepts up to 3 IDs applied in order. Improves flow when splitting large tasks across multiple requests.", examples=[['09bOJkdYVjKy2oOiiVtR', '0p2uKqOnZyce22SPZ9d5', '1KYvY8WZAKmcjCJ1mvVB']])
    next_request_ids: list[str] | None = Field(default=None, description="Request IDs from subsequent speech samples to maintain continuity. Accepts up to 3 IDs applied in order. Useful when regenerating a sample while preserving natural flow with following content.", examples=[['3tPgBrD1UdW3snUkGw1K', '4D1jAxiRFkolBNUGzXkU', '4c8Z4aWliVR2oipYRXhj']])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization when appropriate, 'on' always applies it, 'off' disables it. Normalization handles conversions like spelling out numbers.", examples=[True])
    apply_language_text_normalization: bool | None = Field(default=None, description="Enable language-specific text normalization for improved pronunciation in supported languages. Currently only supports Japanese. Warning: may significantly increase request latency.", examples=[True])
    voice_settings: TextToSpeechStreamWithTimestampsRequestBodyVoiceSettings | None = None
class TextToSpeechStreamWithTimestampsRequest(StrictModel):
    """Converts text to speech audio and returns a stream of JSON objects containing base64-encoded audio chunks with character-level timing information, enabling precise synchronization of audio with text."""
    path: TextToSpeechStreamWithTimestampsRequestPath
    query: TextToSpeechStreamWithTimestampsRequestQuery | None = None
    body: TextToSpeechStreamWithTimestampsRequestBody

# Operation: generate_dialogue
class TextToDialogueRequestQuery(StrictModel):
    output_format: Literal["wav_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000"] | Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). MP3 192kbps requires Creator tier or above; PCM and WAV at 44.1kHz require Pro tier or above. μ-law format is commonly used for Twilio integrations.")
class TextToDialogueRequestBodySettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variation; higher values produce more monotonous, consistent speech.", ge=0.0, le=1.0)
class TextToDialogueRequestBody(StrictModel):
    inputs: list[DialogueInput] = Field(default=..., description="Array of dialogue segments, each containing text and a voice ID. Order is preserved in the output. Maximum of 10 unique voice IDs per request.", examples=[[{'text': 'Hello, how are you?', 'voice_id': 'bYTqZQo3Jz7LQtmGTgwi'}, {'text': "I'm doing well, thank you!", 'voice_id': '6lCwbsX1yVjD49QmpkTR'}]])
    model_id: str | None = Field(default=None, description="Model identifier for text-to-speech conversion. Query available models via GET /v1/models and verify can_do_text_to_speech capability.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language for the model and text normalization. Returns an error if the model does not support the specified language.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="List of pronunciation dictionary locators to apply in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization based on system decision, 'on' always applies it, 'off' disables it. Normalization handles cases like spelling out numbers.", examples=[True])
    settings: TextToDialogueRequestBodySettings | None = None
class TextToDialogueRequest(StrictModel):
    """Converts a list of text and voice ID pairs into multi-voice dialogue audio. Supports up to 10 unique voices per request with configurable audio format, model, stability, and text normalization settings."""
    query: TextToDialogueRequestQuery | None = None
    body: TextToDialogueRequestBody

# Operation: generate_dialogue_stream
class TextToDialogueStreamRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Some formats require higher subscription tiers: MP3 192kbps requires Creator tier or above, PCM 44.1kHz requires Pro tier or above. μ-law format is commonly used for Twilio integrations.")
class TextToDialogueStreamRequestBodySettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variability; higher values produce more consistent, monotonous speech.", ge=0.0, le=1.0)
class TextToDialogueStreamRequestBody(StrictModel):
    inputs: list[DialogueInput] = Field(default=..., description="Array of dialogue turns, each containing text to speak and the voice ID to use. Order matters—items are processed sequentially to create the dialogue flow. Maximum of 10 unique voice IDs per request.", examples=[[{'text': 'Hello, how are you?', 'voice_id': 'bYTqZQo3Jz7LQtmGTgwi'}, {'text': "I'm doing well, thank you!", 'voice_id': '6lCwbsX1yVjD49QmpkTR'}]])
    model_id: str | None = Field(default=None, description="Model identifier for text-to-speech processing. The model must support text-to-speech capability. Query available models via GET /v1/models and check the can_do_text_to_speech property.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language processing and text normalization. If the selected model doesn't support the specified language, an error will be returned.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="List of pronunciation dictionary locators to apply in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization automatically based on content (e.g., spelling out numbers), 'on' always applies normalization, 'off' disables it entirely.", examples=[True])
    settings: TextToDialogueStreamRequestBodySettings | None = None
class TextToDialogueStreamRequest(StrictModel):
    """Converts a list of text and voice ID pairs into multi-voice dialogue speech and streams the audio. Useful for creating conversations, interviews, or multi-speaker content with different voices."""
    query: TextToDialogueStreamRequestQuery | None = None
    body: TextToDialogueStreamRequestBody

# Operation: generate_dialogue_stream_with_timestamps
class TextToDialogueStreamWithTimestampsRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio codec, sample rate, and bitrate configuration. Format is codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require elevated subscription tiers.")
class TextToDialogueStreamWithTimestampsRequestBodySettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls voice consistency and emotional variation. Lower values (closer to 0) produce greater emotional range and variability. Higher values (closer to 1) produce more consistent, monotonous delivery.", ge=0.0, le=1.0)
class TextToDialogueStreamWithTimestampsRequestBody(StrictModel):
    inputs: list[DialogueInput] = Field(default=..., description="Array of dialogue turn objects, each pairing text content with a voice ID. Processed in order to create sequential dialogue. Maximum of 10 unique voice IDs per request.", examples=[[{'text': 'Hello, how are you?', 'voice_id': 'bYTqZQo3Jz7LQtmGTgwi'}, {'text': "I'm doing well, thank you!", 'voice_id': '6lCwbsX1yVjD49QmpkTR'}]])
    model_id: str | None = Field(default=None, description="The TTS model to use for synthesis. Query available models via GET /v1/models and verify can_do_text_to_speech capability.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language processing and text normalization. The selected model must support the specified language.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="Ordered list of pronunciation dictionary references to apply custom pronunciations. Applied sequentially in the order provided. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always normalizes (e.g., converts numbers to words), 'off' disables normalization.", examples=[True])
    settings: TextToDialogueStreamWithTimestampsRequestBodySettings | None = None
class TextToDialogueStreamWithTimestampsRequest(StrictModel):
    """Converts text and voice ID pairs into streamed dialogue audio with precise timestamps. Returns a continuous stream of JSON objects containing base64-encoded audio chunks and their corresponding timing information."""
    query: TextToDialogueStreamWithTimestampsRequestQuery | None = None
    body: TextToDialogueStreamWithTimestampsRequestBody

# Operation: generate_dialogue_with_timestamps
class TextToDialogueFullWithTimestampsRequestQuery(StrictModel):
    output_format: Literal["wav_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000"] | Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio codec, sample rate, and bitrate format. Format is specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and certain formats require higher subscription tiers.")
class TextToDialogueFullWithTimestampsRequestBodySettings(StrictModel):
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Voice stability control affecting emotional range and consistency. Lower values produce broader emotional variation; higher values result in more monotonous, emotionally limited speech.", ge=0.0, le=1.0)
class TextToDialogueFullWithTimestampsRequestBody(StrictModel):
    inputs: list[DialogueInput] = Field(default=..., description="List of dialogue turns, each containing text to be spoken and the voice ID to use for that turn. Maximum of 10 unique voice IDs per request. Turns are processed in order.", examples=[[{'text': 'Hello, how are you?', 'voice_id': 'bYTqZQo3Jz7LQtmGTgwi'}, {'text': "I'm doing well, thank you!", 'voice_id': '6lCwbsX1yVjD49QmpkTR'}]])
    model_id: str | None = Field(default=None, description="The text-to-speech model to use for generation. Must support text-to-speech capability. Query available models via GET /v1/models to verify can_do_text_to_speech property.")
    language_code: str | None = Field(default=None, description="ISO 639-1 language code to enforce language for the model and text normalization. If the model does not support the specified language, an error will be returned.")
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorRequestModel] | None = Field(default=None, description="Custom pronunciation dictionary rules to apply to the text in order. Each locator references a specific dictionary version. Maximum of 3 locators per request.", examples=[[{'pronunciation_dictionary_id': 'test', 'version_id': 'id2'}]])
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(default=None, description="Text normalization mode: 'auto' applies normalization based on system decision, 'on' always applies it, 'off' disables it. Normalization handles cases like spelling out numbers.", examples=[True])
    settings: TextToDialogueFullWithTimestampsRequestBodySettings | None = None
class TextToDialogueFullWithTimestampsRequest(StrictModel):
    """Generate dialogue from text with precise character-level timing information for audio-text synchronization. Each dialogue turn is converted to speech using specified voice IDs and returned with exact timestamp markers."""
    query: TextToDialogueFullWithTimestampsRequestQuery | None = None
    body: TextToDialogueFullWithTimestampsRequestBody

# Operation: convert_voice
class SpeechToSpeechFullRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The target voice to apply to the audio. Use the voices endpoint to discover available voices and their characteristics.", examples=['21m00Tcm4TlvDq8ikWAM'])
class SpeechToSpeechFullRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio encoding format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers.")
class SpeechToSpeechFullRequestBody(StrictModel):
    audio: str = Field(default=..., description="Base64-encoded file content for upload. The source audio file containing the content and emotional expression to transfer to the target voice.", json_schema_extra={'format': 'byte'})
    model_id: str | None = Field(default=None, description="The speech-to-speech model to use for conversion. Query available models to verify speech conversion support via the can_do_voice_conversion property.")
    remove_background_noise: bool | None = Field(default=None, description="Enable background noise removal from the input audio using audio isolation. Only applicable when using the Voice Changer model.", examples=[True])
    voice_settings: str | None = Field(default=None, description="Voice settings overriding stored settings for the given voice. They are applied only on the given request. Needs to be send as a JSON encoded string.")
class SpeechToSpeechFullRequest(StrictModel):
    """Transform audio from one voice to another while preserving the original emotion, timing, and delivery characteristics. The input audio's content and emotional qualities control the output speech generation."""
    path: SpeechToSpeechFullRequestPath
    query: SpeechToSpeechFullRequestQuery | None = None
    body: SpeechToSpeechFullRequestBody

# Operation: convert_speech_to_speech_stream
class SpeechToSpeechStreamRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The target voice identifier to apply to the input audio. Use the voices endpoint to discover available voices.", examples=['21m00Tcm4TlvDq8ikWAM'])
class SpeechToSpeechStreamRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio encoding format for the response, specified as codec_sample_rate_bitrate. Higher bitrates and sample rates may require elevated subscription tiers.")
class SpeechToSpeechStreamRequestBody(StrictModel):
    audio: str = Field(default=..., description="Base64-encoded file content for upload. The source audio file containing the content and emotional characteristics that will control the generated speech output.", json_schema_extra={'format': 'byte'})
    model_id: str | None = Field(default=None, description="The model identifier to use for voice conversion. Verify the model supports speech-to-speech conversion via the can_do_voice_conversion property.")
    remove_background_noise: bool | None = Field(default=None, description="Enable background noise removal from the input audio using audio isolation. Only applicable when using the Voice Changer model.", examples=[True])
    voice_settings: str | None = Field(default=None, description="Voice settings overriding stored settings for the given voice. They are applied only on the given request. Needs to be send as a JSON encoded string.")
class SpeechToSpeechStreamRequest(StrictModel):
    """Convert audio from one voice to another with streaming output, maintaining full control over emotion, timing, and delivery. The input audio's content and emotional characteristics drive the generated speech in the target voice."""
    path: SpeechToSpeechStreamRequestPath
    query: SpeechToSpeechStreamRequestQuery | None = None
    body: SpeechToSpeechStreamRequestBody

# Operation: generate_voice_previews
class TextToVoiceRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio codec, sample rate, and bitrate for the generated preview samples. Higher bitrates and sample rates provide better quality but require higher subscription tiers.")
class TextToVoiceRequestBody(StrictModel):
    voice_description: str = Field(default=..., description="Detailed description of the desired voice characteristics. The system uses this to generate voice previews matching your specifications.", min_length=20, max_length=1000, examples=['A sassy squeaky mouse'])
    loudness: float | None = Field(default=None, description="Volume level of the generated voice samples, ranging from quietest to loudest. A value of 0 corresponds to approximately -24 LUFS.", ge=-1.0, le=1.0, examples=[0.5])
    quality: float | None = Field(default=None, description="Voice quality level that balances output fidelity with variety. Higher values produce more consistent, polished voices with less variation across previews.", ge=-1.0, le=1.0, examples=[0.9])
    should_enhance: bool | None = Field(default=None, description="Automatically expand and refine the voice description using AI to add detail and improve generation quality. Useful for simple or brief descriptions.", examples=[True])
class TextToVoiceRequest(StrictModel):
    """Generate multiple voice preview samples based on a text description to help you select a custom voice. Each preview includes a unique voice ID and audio sample that can be used to create the final voice."""
    query: TextToVoiceRequestQuery | None = None
    body: TextToVoiceRequestBody

# Operation: create_voice
class CreateVoiceRequestBody(StrictModel):
    voice_name: str = Field(default=..., description="The name for the new voice being created.", examples=['Sassy squeaky mouse'])
    voice_description: str = Field(default=..., description="A detailed description of the voice characteristics and use case. Must be between 20 and 1000 characters.", min_length=20, max_length=1000, examples=['A sassy squeaky mouse'])
    generated_voice_id: str = Field(default=..., description="The ID of the generated voice preview to finalize. Obtain this from the response of POST /v1/text-to-voice/design or POST /v1/text-to-voice/:voice_id/remix operations.", examples=['37HceQefKmEi3bGovXjL'])
    labels: dict[str, str] | None = Field(default=None, description="Optional metadata tags to associate with the created voice for organization and filtering purposes.", examples=[{'language': 'en'}])
class CreateVoiceRequest(StrictModel):
    """Create a persistent voice from a previously generated voice preview. This endpoint finalizes a voice design by converting a generated_voice_id (obtained from design or remix operations) into a named voice asset."""
    body: CreateVoiceRequestBody

# Operation: design_voice
class TextToVoiceDesignRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio codec, sample rate, and bitrate for the generated voice samples. Higher bitrates and sample rates require appropriate subscription tiers.")
class TextToVoiceDesignRequestBody(StrictModel):
    voice_description: str = Field(default=..., description="Detailed description of the desired voice characteristics. Used to guide voice generation and should include personality, tone, and acoustic qualities.", min_length=20, max_length=1000, examples=['A sassy squeaky mouse'])
    model_id: Literal["eleven_multilingual_ttv_v2", "eleven_ttv_v3"] | None = Field(default=None, description="AI model version to use for voice generation. Different models may produce varying quality and multilingual support.", examples=['eleven_multilingual_ttv_v2'])
    loudness: float | None = Field(default=None, description="Volume level adjustment for the generated voice, where -1 is quietest and 1 is loudest. A value of 0 corresponds to approximately -24 LUFS.", ge=-1.0, le=1.0, examples=[0.5])
    stream_previews: bool | None = Field(default=None, description="When enabled, voice previews are streamed separately via the stream endpoint instead of being included in the response. Useful for reducing response payload size.", examples=[True])
    should_enhance: bool | None = Field(default=None, description="Automatically enhance the voice description with AI-generated details to improve voice generation quality and variety. Expands simple prompts into more comprehensive descriptions.", examples=[True])
    quality: float | None = Field(default=None, description="Quality level for voice generation, where higher values produce better output but with less variation across previews.", ge=-1.0, le=1.0, examples=[0.9])
class TextToVoiceDesignRequest(StrictModel):
    """Generate voice design previews based on a detailed description. Returns multiple voice options with audio samples that can be used to create a custom voice."""
    query: TextToVoiceDesignRequestQuery | None = None
    body: TextToVoiceDesignRequestBody

# Operation: remix_voice
class TextToVoiceRemixRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The ID of the voice to remix. Use the voices list endpoint to discover available voices.", examples=['21m00Tcm4TlvDq8ikWAM'])
class TextToVoiceRemixRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate. MP3 at 192kbps requires Creator tier or higher. PCM at 44.1kHz requires Pro tier or higher. μ-law format is compatible with Twilio.")
class TextToVoiceRemixRequestBody(StrictModel):
    voice_description: str = Field(default=..., description="Detailed description of the voice modifications to apply. Be specific about desired characteristics such as pitch, tone, pace, or emotional qualities.", min_length=5, max_length=1000, examples=['Make the voice have a higher pitch.'])
    loudness: float | None = Field(default=None, description="Volume level of the generated voice, ranging from -1 (quietest) to 1 (loudest), with 0 corresponding to approximately -24 LUFS.", ge=-1.0, le=1.0, examples=[0.5])
    stream_previews: bool | None = Field(default=None, description="When true, returns only generated voice IDs without audio previews in the response. Audio can then be streamed separately via the stream endpoint.", examples=[True])
class TextToVoiceRemixRequest(StrictModel):
    """Generate voice previews by remixing an existing voice based on a descriptive prompt. Returns multiple voice preview options with generated voice IDs that can be used to create new voices."""
    path: TextToVoiceRemixRequestPath
    query: TextToVoiceRemixRequestQuery | None = None
    body: TextToVoiceRemixRequestBody

# Operation: stream_voice_preview
class TextToVoicePreviewStreamRequestPath(StrictModel):
    generated_voice_id: str = Field(default=..., description="The unique identifier of the generated voice preview to stream.", examples=['37HceQefKmEi3bGovXjL'])
class TextToVoicePreviewStreamRequest(StrictModel):
    """Stream audio data for a voice preview that was previously generated using the voice design endpoint. This operation returns the audio content as a continuous stream."""
    path: TextToVoicePreviewStreamRequestPath

# Operation: list_voices
class GetUserVoicesV2RequestQuery(StrictModel):
    next_page_token: str | None = Field(default=None, description="Token for retrieving the next page of results. Use this with the has_more flag from the previous response to implement reliable pagination.", examples=['0'])
    page_size: int | None = Field(default=None, description="Maximum number of voices to return per page. Must not exceed 100. Note that page 0 may include additional default voices.")
    sort: str | None = Field(default=None, description="Field to sort results by. Use 'created_at_unix' for chronological ordering or 'name' for alphabetical ordering. Note that 'created_at_unix' may not be available for older voices.", examples=['created_at_unix'])
    sort_direction: str | None = Field(default=None, description="Direction to sort results in. Use 'asc' for ascending or 'desc' for descending order.", examples=['desc'])
    voice_type: str | None = Field(default=None, description="Filter voices by type. 'non-default' includes all voices except default voices. 'saved' includes non-default voices plus any default voices added to collections.")
    category: str | None = Field(default=None, description="Filter voices by their creation category or source.")
    fine_tuning_state: str | None = Field(default=None, description="Filter professional voice clones by their fine-tuning state. Only applicable to professional voices.")
    collection_id: str | None = Field(default=None, description="Filter voices to only those belonging to a specific collection by its ID.")
    include_total_count: bool | None = Field(default=None, description="Include the total count of matching voices in the response. Note that this count is a live snapshot and may change between requests. Use the has_more flag for pagination instead. Only enable when you need the total count for display purposes, as it incurs a performance cost.", examples=[True])
    voice_ids: list[str] | None = Field(default=None, description="Retrieve specific voices by their IDs. Accepts up to 100 voice IDs in a single request.")
class GetUserVoicesV2Request(StrictModel):
    """Retrieve a paginated list of available voices with advanced filtering, sorting, and search capabilities. Supports filtering by voice type, category, fine-tuning state, and collection membership."""
    query: GetUserVoicesV2RequestQuery | None = None

# Operation: get_voice_settings
class GetVoiceSettingsRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice whose settings you want to retrieve. Use the list voices endpoint to discover available voice IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetVoiceSettingsRequest(StrictModel):
    """Retrieve the configuration settings for a specific voice, including similarity boost (Clarity + Similarity Enhancement) and stability parameters that control voice quality characteristics."""
    path: GetVoiceSettingsRequestPath

# Operation: get_voice
class GetVoiceByIdRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to retrieve. You can list all available voices to discover valid IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetVoiceByIdRequest(StrictModel):
    """Retrieve detailed metadata for a specific voice, including its properties and configuration. Use this to get information about a voice before using it for text-to-speech synthesis."""
    path: GetVoiceByIdRequestPath

# Operation: delete_voice
class DeleteVoiceRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to delete. You can retrieve available voice IDs from the list voices endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteVoiceRequest(StrictModel):
    """Permanently deletes a voice by its ID. This action cannot be undone."""
    path: DeleteVoiceRequestPath

# Operation: configure_voice_settings
class EditVoiceSettingsRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to configure. Use the list voices endpoint to discover available voice IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditVoiceSettingsRequestBody(StrictModel):
    stability: float | None = Field(default=None, description="Controls voice consistency and emotional range. Lower values (closer to 0) produce more varied emotional expression, while higher values (closer to 1) result in more consistent but potentially monotonous output.", ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, description="Controls how closely the generated voice matches the original voice characteristics. Higher values enforce stricter adherence to the original voice, while lower values allow more deviation.", ge=0.0, le=1.0)
    style: float | None = Field(default=None, description="Amplifies the stylistic characteristics of the original speaker. Non-zero values increase computational resource usage and may increase latency.")
    speed: float | None = Field(default=None, description="Adjusts speech playback speed relative to normal rate. Use 1.0 for default speed, values below 1.0 to slow down, and values above 1.0 to speed up.")
class EditVoiceSettingsRequest(StrictModel):
    """Configure voice parameters for a specific voice, including stability, similarity, style, and speed adjustments. These settings control how the voice is generated and how closely it adheres to the original voice characteristics."""
    path: EditVoiceSettingsRequestPath
    body: EditVoiceSettingsRequestBody | None = None

# Operation: create_voice_sample
class AddVoiceRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this voice, shown in selection dropdowns and voice management interfaces.", examples=['John Smith'])
    files: list[Annotated[str, Field(json_schema_extra={'format': 'byte'})]] = Field(default=..., description="Base64-encoded file content for upload. Audio file paths for voice cloning samples. Provide multiple recordings to improve voice quality and consistency. Order does not affect processing.")
    remove_background_noise: bool | None = Field(default=None, description="Enable background noise removal using audio isolation processing. Only use if your samples contain background noise, as it may degrade quality for clean recordings.", examples=[True])
    description: str | None = Field(default=None, description="Optional metadata describing the voice characteristics, tone, and intended use cases.", examples=['An old American male voice with a slight hoarseness in his throat. Perfect for news.'])
    labels: dict[str, str] | str | None = Field(default=None, description="Categorical metadata for voice classification. Supports language code, accent variant, gender, and age range to help organize and filter voices.", examples=['{"language": "en", "accent": "en-US", "gender": "male", "age": "middle-aged"}'])
class AddVoiceRequest(StrictModel):
    """Create a new voice in VoiceLab by uploading audio samples for voice cloning. The voice will be added to your collection and available for use in voice synthesis."""
    body: AddVoiceRequestBody

# Operation: update_voice
class EditVoiceRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditVoiceRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this voice, shown in voice selection dropdowns.", examples=['John Smith'])
    files: list[Annotated[str, Field(json_schema_extra={'format': 'byte'})]] | None = Field(default=None, description="Base64-encoded file content for upload. Audio files to add to the voice. Supported formats include MP3, WAV, and other common audio formats.")
    remove_background_noise: bool | None = Field(default=None, description="Enable automatic background noise removal from audio samples using audio isolation. Only use if samples contain background noise, as it may degrade quality otherwise.", examples=[True])
    description: str | None = Field(default=None, description="A brief description of the voice characteristics, tone, and intended use cases.", examples=['An old American male voice with a slight hoarseness in his throat. Perfect for news.'])
    labels: dict[str, str] | str | None = Field(default=None, description="Metadata labels describing the voice. Supported keys include language (ISO 639-1 code), accent (BCP 47 tag), gender, and age.", examples=['{"language": "en", "accent": "en-US", "gender": "male", "age": "middle-aged"}'])
class EditVoiceRequest(StrictModel):
    """Update the name, description, labels, and audio samples of a voice you created. Optionally apply background noise removal to improve audio quality."""
    path: EditVoiceRequestPath
    body: EditVoiceRequestBody

# Operation: add_shared_voice
class AddSharingVoiceRequestPath(StrictModel):
    public_user_id: str = Field(default=..., description="The public user ID of the ElevenLabs user who owns the shared voice.", examples=['63e06b7e7cafdc46be4d2e0b3f045940231ae058d508589653d74d1265a574ca'])
    voice_id: str = Field(default=..., description="The unique identifier of the voice to add to your collection.", examples=['21m00Tcm4TlvDq8ikWAM'])
class AddSharingVoiceRequestBody(StrictModel):
    new_name: str = Field(default=..., description="The display name for this voice in your voice collection. This name will appear in your voice selection dropdown.", examples=['John Smith'])
    bookmarked: bool | None = Field(default=None, description="Whether to bookmark this voice for quick access in your collection.")
class AddSharingVoiceRequest(StrictModel):
    """Add a shared voice from another user to your personal voice collection. The voice will be displayed in your voice dropdown with a custom name you assign."""
    path: AddSharingVoiceRequestPath
    body: AddSharingVoiceRequestBody

# Operation: generate_podcast
class CreatePodcastRequestBody(StrictModel):
    model_id: str = Field(default=..., description="The voice model to use for audio generation. Query GET /v1/models to see all available models.", examples=['eleven_multilingual_v2'])
    mode: PodcastConversationMode | PodcastBulletinMode = Field(default=..., description="The podcast format type. 'conversation' generates dialogue between two voices (host and guest), while 'bulletin' generates a single-voice monologue.", examples=[{'conversation': {'guest_voice_id': 'bYTqZQo3Jz7LQtmGTgwi', 'host_voice_id': '6lCwbsX1yVjD49QmpkTR'}}])
    source: PodcastTextSource | PodcastUrlSource | list[PodcastTextSource | PodcastUrlSource] = Field(default=..., description="The content source for podcast generation. Can be a URL, text content, or other supported source formats.", examples=[{'url': 'https://en.wikipedia.org/wiki/Cognitive_science'}])
    quality_preset: Literal["standard", "high", "highest", "ultra", "ultra_lossless"] | None = Field(default=None, description="Audio output quality level. Higher quality settings provide better audio fidelity with improved processing.", examples=['standard'])
    duration_scale: Literal["short", "default", "long"] | None = Field(default=None, description="Target podcast length. Controls the amount of content included in the generated podcast.", examples=['short'])
    language: str | None = Field(default=None, description="Two-letter ISO 639-1 language code for the podcast content and voice generation.", min_length=2, max_length=2, examples=['en'])
    intro: str | None = Field(default=None, description="Optional opening text to prepend to the podcast. Useful for branding or context-setting.", max_length=1500, examples=['Welcome to the podcast.'])
    outro: str | None = Field(default=None, description="Optional closing text to append to the podcast. Useful for calls-to-action or sign-offs.", max_length=1500, examples=['Thank you for listening!'])
    instructions_prompt: str | None = Field(default=None, description="Custom instructions to guide the podcast generation style, tone, and content treatment. Use this to enforce accuracy, adjust formality, or specify audience appropriateness.", max_length=3000, examples=['Ensure the podcast remains factual, accurate and appropriate for all audiences.'])
    highlights: list[str] | None = Field(default=None, description="Key themes or highlights summarizing the podcast content. Each highlight should be a brief phrase between 10-70 characters.", examples=[['Emphasize the importance of AI on education']])
    callback_url: str | None = Field(default=None, description="Webhook URL for conversion status notifications. The service will POST status updates when the project and chapters complete processing, including success/error details.", examples=[['https://www.test.com/my-api/projects-status']])
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(default=None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always normalizes, 'apply_english' normalizes assuming English text, and 'off' disables normalization.")
class CreatePodcastRequest(StrictModel):
    """Generate a podcast by converting source content into audio using AI-powered text-to-speech. Supports both conversational (two-voice dialogue) and bulletin (monologue) formats with customizable quality, duration, language, and styling options."""
    body: CreatePodcastRequestBody

# Operation: apply_pronunciation_dictionaries
class UpdatePronunciationDictionariesRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to which pronunciation dictionaries will be applied.", examples=['21m00Tcm4TlvDq8ikWAM'])
class UpdatePronunciationDictionariesRequestBody(StrictModel):
    pronunciation_dictionary_locators: list[PronunciationDictionaryVersionLocatorDbModel] = Field(default=..., description="An ordered list of pronunciation dictionary references to apply to the project. Each reference must include the dictionary ID and its version ID. Multiple dictionaries can be specified as separate form entries.", examples=[['{"pronunciation_dictionary_id": "21m00Tcm4TlvDq8ikWAM", "version_id": "BdF0s0aZ3oFoKnDYdTox"}']])
    invalidate_affected_text: bool | None = Field(default=None, description="Whether to automatically mark text in the project for reconversion when dictionaries are applied or removed.", examples=[False])
class UpdatePronunciationDictionariesRequest(StrictModel):
    """Apply pronunciation dictionaries to a Studio project. The operation automatically marks affected text for reconversion when dictionaries are added or removed."""
    path: UpdatePronunciationDictionariesRequestPath
    body: UpdatePronunciationDictionariesRequestBody

# Operation: create_studio_project
class AddProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the Studio project used for identification and display purposes.", examples=['Project 1'])
    default_title_voice_id: str | None = Field(default=None, description="The voice ID to use as the default voice for new titles in this project.", examples=['21m00Tcm4TlvDq8ikWAM'])
    default_paragraph_voice_id: str | None = Field(default=None, description="The voice ID to use as the default voice for new paragraphs in this project.", examples=['21m00Tcm4TlvDq8ikWAM'])
    default_model_id: str | None = Field(default=None, description="The model ID to use for audio generation in this project. Query GET /v1/models to list available models.", examples=['eleven_multilingual_v2'])
    quality_preset: Literal["standard", "high", "ultra", "ultra_lossless"] | None = Field(default=None, description="The output quality level for generated audio, ranging from standard (128kbps) to ultra lossless (705.6kbps, fully lossless).", examples=['standard'])
    author: str | None = Field(default=None, description="The author name to include as metadata in downloaded audio files.", examples=['William Shakespeare'])
    description: str | None = Field(default=None, description="A description of the Studio project's content and purpose.", examples=['A tragic love story between two young lovers.'])
    genres: list[str] | None = Field(default=None, description="A list of genres associated with this project for categorization and discovery.", examples=[['Romance', 'Drama']])
    target_audience: Literal["children", "young adult", "adult", "all ages"] | None = Field(default=None, description="The intended audience demographic for this project's content.", examples=['adult'])
    language: str | None = Field(default=None, description="The primary language of the project content as a two-letter ISO 639-1 language code.", min_length=2, max_length=2, examples=['en'])
    content_type: str | None = Field(default=None, description="The type of content in this project (e.g., Book, Article, Screenplay).", examples=['Book'])
    original_publication_date: str | None = Field(default=None, description="The original publication date of the content in YYYY-MM-DD or YYYY format.", pattern='^\\d{4}-\\d{2}-\\d{2}$|^\\d{4}$', examples=['1597-01-01'])
    mature_content: bool | None = Field(default=None, description="Whether this project contains mature content that may not be suitable for all audiences.", examples=[False])
    isbn_number: str | None = Field(default=None, description="The ISBN number of the project to include as metadata in downloaded audio files.", examples=['0-306-40615-2'])
    volume_normalization: bool | None = Field(default=None, description="Whether to apply postprocessing to normalize audio volume to audiobook standards when downloading the project.", examples=[False])
    callback_url: str | None = Field(default=None, description="A webhook URL that receives conversion status notifications for the project and its chapters. Notifications include success/error status with project and chapter IDs.", examples=[['https://www.test.com/my-api/projects-status']])
    fiction: Literal["fiction", "non-fiction"] | None = Field(default=None, description="Whether the content is fiction or non-fiction.", examples=['fiction'])
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(default=None, description="Controls text normalization behavior: 'auto' decides automatically, 'on' always applies, 'apply_english' applies with English assumption, 'off' disables normalization.")
    auto_convert: bool | None = Field(default=None, description="Whether to automatically convert the project to audio immediately upon creation.")
    auto_assign_voices: bool | None = Field(default=None, description="Whether to automatically assign voices to phrases during project creation. This is an alpha feature.")
    source_type: Literal["blank", "book", "article", "genfm", "video", "screenplay"] | None = Field(default=None, description="The initialization type for the project: blank (empty), book (from document), article, genfm, video, or screenplay.", examples=['book'])
    create_publishing_read: bool | None = Field(default=None, description="Whether to create a corresponding read for direct publishing in draft state alongside the project.")
    from_document: str | None = Field(default=None, description="Base64-encoded file content for upload. An optional .epub, .pdf, .txt or similar file can be provided. If provided, we will initialize the Studio project with its content. If this is set, 'from_url' and 'from_content' must be null. If neither 'from_url', 'from_document', 'from_content' are provided we will initialize the Studio project as blank.", json_schema_extra={'format': 'byte'})
    from_content_json: str | None = Field(default=None, description="\n    An optional content to initialize the Studio project with. If this is set, 'from_url' and 'from_document' must be null. If neither 'from_url', 'from_document', 'from_content' are provided we will initialize the Studio project as blank.\n\n    Example:\n    [{\"name\": \"Chapter A\", \"blocks\": [{\"sub_type\": \"p\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"A\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"B\", \"type\": \"tts_node\"}]}, {\"sub_type\": \"h1\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"C\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"D\", \"type\": \"tts_node\"}]}]}, {\"name\": \"Chapter B\", \"blocks\": [{\"sub_type\": \"p\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"E\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"F\", \"type\": \"tts_node\"}]}, {\"sub_type\": \"h2\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"G\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"H\", \"type\": \"tts_node\"}]}]}]\n    ", examples=['[{"name": "Chapter A", "blocks": [{"sub_type": "p", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "A", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "B", "type": "tts_node"}]}, {"sub_type": "h1", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "C", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "D", "type": "tts_node"}]}]}, {"name": "Chapter B", "blocks": [{"sub_type": "p", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "E", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "F", "type": "tts_node"}]}, {"sub_type": "h2", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "G", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "H", "type": "tts_node"}]}]}]'])
    pronunciation_dictionary_locators: list[str] | None = Field(default=None, description="A list of pronunciation dictionary locators (pronunciation_dictionary_id, version_id) encoded as a list of JSON strings for pronunciation dictionaries to be applied to the text. A list of json encoded strings is required as adding projects may occur through formData as opposed to jsonBody. To specify multiple dictionaries use multiple --form lines in your curl, such as --form 'pronunciation_dictionary_locators=\"{\\\"pronunciation_dictionary_id\\\":\\\"Vmd4Zor6fplcA7WrINey\\\",\\\"version_id\\\":\\\"hRPaxjlTdR7wFMhV4w0b\\\"}\"' --form 'pronunciation_dictionary_locators=\"{\\\"pronunciation_dictionary_id\\\":\\\"JzWtcGQMJ6bnlWwyMo7e\\\",\\\"version_id\\\":\\\"lbmwxiLu4q6txYxgdZqn\\\"}\"'.", examples=[['{"pronunciation_dictionary_id": "21m00Tcm4TlvDq8ikWAM", "version_id": "BdF0s0aZ3oFoKnDYdTox"}']])
    voice_settings: str | None = Field(default=None, description="    Optional voice settings overrides for the project, encoded as a list of JSON strings.\n\n    Example:\n    [\"{\\\"voice_id\\\": \\\"21m00Tcm4TlvDq8ikWAM\\\", \\\"stability\\\": 0.7, \\\"similarity_boost\\\": 0.8, \\\"style\\\": 0.5, \\\"speed\\\": 1.0, \\\"use_speaker_boost\\\": true}\"]\n    ", examples=[['{"voice_id": "21m00Tcm4TlvDq8ikWAM", "stability": 0.7, "similarity_boost": 0.8, "style": 0.5, "speed": 1.0, "use_speaker_boost": true}']])
class AddProjectRequest(StrictModel):
    """Creates a new Studio project for audio content generation. Projects can be initialized as blank, from a document, or from a URL, with customizable voices, audio quality, and metadata."""
    body: AddProjectRequestBody

# Operation: get_project
class GetProjectByIdRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetProjectByIdRequestQuery(StrictModel):
    share_id: str | None = Field(default=None, description="Optional share identifier to access a shared version of the project.")
class GetProjectByIdRequest(StrictModel):
    """Retrieve detailed information about a specific Studio project. Returns comprehensive project metadata including configuration, settings, and other project-specific details."""
    path: GetProjectByIdRequestPath
    query: GetProjectByIdRequestQuery | None = None

# Operation: update_studio_project
class EditProjectRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the Studio project used for identification and organization.", examples=['Project 1'])
    default_title_voice_id: str = Field(default=..., description="The voice ID to use as the default voice for newly created title sections.", examples=['21m00Tcm4TlvDq8ikWAM'])
    default_paragraph_voice_id: str = Field(default=..., description="The voice ID to use as the default voice for newly created paragraph sections.", examples=['21m00Tcm4TlvDq8ikWAM'])
    author: str | None = Field(default=None, description="Optional author name that will be embedded as metadata in exported MP3 files when the project or chapters are downloaded.", examples=['William Shakespeare'])
    isbn_number: str | None = Field(default=None, description="Optional ISBN number that will be embedded as metadata in exported MP3 files when the project or chapters are downloaded.", examples=['0-306-40615-2'])
    volume_normalization: bool | None = Field(default=None, description="When enabled, applies audio postprocessing to downloaded files to ensure compliance with audiobook volume normalization standards.", examples=[False])
class EditProjectRequest(StrictModel):
    """Updates a Studio project with new metadata, voice settings, and audio processing preferences. Changes apply to the project configuration and affect how new content is generated and exported."""
    path: EditProjectRequestPath
    body: EditProjectRequestBody

# Operation: delete_project
class DeleteProjectRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to delete.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteProjectRequest(StrictModel):
    """Permanently deletes a Studio project and all associated data. This action cannot be undone."""
    path: DeleteProjectRequestPath

# Operation: update_project_content
class EditProjectContentRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditProjectContentRequestBody(StrictModel):
    auto_convert: bool | None = Field(default=None, description="Whether to automatically convert the Studio project to audio format. Defaults to false if not specified.")
    from_document: str | None = Field(default=None, description="Base64-encoded file content for upload. An optional .epub, .pdf, .txt or similar file can be provided. If provided, we will initialize the Studio project with its content. If this is set, 'from_url' and 'from_content' must be null. If neither 'from_url', 'from_document', 'from_content' are provided we will initialize the Studio project as blank.", json_schema_extra={'format': 'byte'})
    from_content_json: str | None = Field(default=None, description="\n    An optional content to initialize the Studio project with. If this is set, 'from_url' and 'from_document' must be null. If neither 'from_url', 'from_document', 'from_content' are provided we will initialize the Studio project as blank.\n\n    Example:\n    [{\"name\": \"Chapter A\", \"blocks\": [{\"sub_type\": \"p\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"A\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"B\", \"type\": \"tts_node\"}]}, {\"sub_type\": \"h1\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"C\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"D\", \"type\": \"tts_node\"}]}]}, {\"name\": \"Chapter B\", \"blocks\": [{\"sub_type\": \"p\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"E\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"F\", \"type\": \"tts_node\"}]}, {\"sub_type\": \"h2\", \"nodes\": [{\"voice_id\": \"6lCwbsX1yVjD49QmpkT0\", \"text\": \"G\", \"type\": \"tts_node\"}, {\"voice_id\": \"6lCwbsX1yVjD49QmpkT1\", \"text\": \"H\", \"type\": \"tts_node\"}]}]}]\n    ", examples=['[{"name": "Chapter A", "blocks": [{"sub_type": "p", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "A", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "B", "type": "tts_node"}]}, {"sub_type": "h1", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "C", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "D", "type": "tts_node"}]}]}, {"name": "Chapter B", "blocks": [{"sub_type": "p", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "E", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "F", "type": "tts_node"}]}, {"sub_type": "h2", "nodes": [{"voice_id": "6lCwbsX1yVjD49QmpkT0", "text": "G", "type": "tts_node"}, {"voice_id": "6lCwbsX1yVjD49QmpkT1", "text": "H", "type": "tts_node"}]}]}]'])
class EditProjectContentRequest(StrictModel):
    """Updates the content of a Studio project. Optionally converts the project to audio format during the update."""
    path: EditProjectContentRequestPath
    body: EditProjectContentRequestBody | None = None

# Operation: convert_studio_project
class ConvertProjectEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to convert.", examples=['21m00Tcm4TlvDq8ikWAM'])
class ConvertProjectEndpointRequest(StrictModel):
    """Initiates conversion of a Studio project and all of its associated chapters. This operation processes the entire project structure for conversion."""
    path: ConvertProjectEndpointRequestPath

# Operation: list_snapshots
class GetProjectSnapshotsRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project for which to retrieve snapshots.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetProjectSnapshotsRequest(StrictModel):
    """Retrieves a list of all snapshots for a specified Studio project. Snapshots capture the state of a project at a point in time."""
    path: GetProjectSnapshotsRequestPath

# Operation: get_snapshot
class GetProjectSnapshotEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the snapshot.", examples=['21m00Tcm4TlvDq8ikWAM'])
    project_snapshot_id: str = Field(default=..., description="The unique identifier of the project snapshot to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetProjectSnapshotEndpointRequest(StrictModel):
    """Retrieves a specific project snapshot by its ID. Use this to access saved project state and configuration data."""
    path: GetProjectSnapshotEndpointRequestPath

# Operation: stream_project_snapshot_audio
class StreamProjectSnapshotAudioEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the snapshot.", examples=['21m00Tcm4TlvDq8ikWAM'])
    project_snapshot_id: str = Field(default=..., description="The unique identifier of the project snapshot whose audio should be streamed.", examples=['21m00Tcm4TlvDq8ikWAM'])
class StreamProjectSnapshotAudioEndpointRequestBody(StrictModel):
    convert_to_mpeg: bool | None = Field(default=None, description="Whether to convert the streamed audio to MPEG format. Defaults to false, streaming in the original format.")
class StreamProjectSnapshotAudioEndpointRequest(StrictModel):
    """Stream audio from a Studio project snapshot. Optionally convert the audio to MPEG format during streaming."""
    path: StreamProjectSnapshotAudioEndpointRequestPath
    body: StreamProjectSnapshotAudioEndpointRequestBody | None = None

# Operation: download_snapshot_archive
class StreamProjectSnapshotArchiveEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the snapshot to archive.", examples=['21m00Tcm4TlvDq8ikWAM'])
    project_snapshot_id: str = Field(default=..., description="The unique identifier of the project snapshot to archive and download.", examples=['21m00Tcm4TlvDq8ikWAM'])
class StreamProjectSnapshotArchiveEndpointRequest(StrictModel):
    """Downloads a compressed archive containing all audio files from a specific Studio project snapshot. Returns the archive as a binary stream ready for download."""
    path: StreamProjectSnapshotArchiveEndpointRequestPath

# Operation: list_chapters
class GetChaptersRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project whose chapters you want to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetChaptersRequest(StrictModel):
    """Retrieves all chapters for a specified Studio project. Returns a list of chapters with their metadata and properties."""
    path: GetChaptersRequestPath

# Operation: create_chapter
class AddChapterRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project where the chapter will be created.", examples=['21m00Tcm4TlvDq8ikWAM'])
class AddChapterRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the chapter used for identification and organization within the project.", examples=['Chapter 1'])
class AddChapterRequest(StrictModel):
    """Creates a new chapter in a Studio project, either as a blank chapter or populated from a URL source."""
    path: AddChapterRequestPath
    body: AddChapterRequestBody

# Operation: get_chapter
class GetChapterByIdEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetChapterByIdEndpointRequest(StrictModel):
    """Retrieves detailed information about a specific chapter within a Studio project."""
    path: GetChapterByIdEndpointRequestPath

# Operation: update_chapter
class EditChapterRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditChapterRequestBodyContent(StrictModel):
    blocks: list[ChapterContentBlockInputModel] = Field(default=..., validation_alias="blocks", serialization_alias="blocks", description="An ordered array of content blocks that comprise the chapter. Each block defines a section of content within the chapter.")
class EditChapterRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name of the chapter for identification purposes.", examples=['Chapter 1'])
    content: EditChapterRequestBodyContent
class EditChapterRequest(StrictModel):
    """Updates an existing chapter in a Studio project, including its name and content blocks."""
    path: EditChapterRequestPath
    body: EditChapterRequestBody

# Operation: delete_chapter
class DeleteChapterEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter to delete.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter to delete.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteChapterEndpointRequest(StrictModel):
    """Permanently deletes a chapter from a Studio project. This action cannot be undone."""
    path: DeleteChapterEndpointRequestPath

# Operation: convert_chapter
class ConvertChapterEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter to convert.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter to be converted.", examples=['21m00Tcm4TlvDq8ikWAM'])
class ConvertChapterEndpointRequest(StrictModel):
    """Initiates the conversion process for a specific chapter within a Studio project. This asynchronous operation transforms the chapter content into the desired output format."""
    path: ConvertChapterEndpointRequestPath

# Operation: list_chapter_snapshots
class GetChapterSnapshotsRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter for which to retrieve snapshots.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetChapterSnapshotsRequest(StrictModel):
    """Retrieves all snapshots for a chapter, which are audio versions automatically created whenever the chapter is converted. Each snapshot can be downloaded as audio."""
    path: GetChapterSnapshotsRequestPath

# Operation: get_chapter_snapshot
class GetChapterSnapshotEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter within the project.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_snapshot_id: str = Field(default=..., description="The unique identifier of the specific chapter snapshot to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetChapterSnapshotEndpointRequest(StrictModel):
    """Retrieves a specific chapter snapshot from a Studio project. Use this to access saved states or versions of a chapter."""
    path: GetChapterSnapshotEndpointRequestPath

# Operation: get_chapter_snapshot_audio
class StreamChapterSnapshotAudioRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project containing the chapter.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_id: str = Field(default=..., description="The unique identifier of the chapter within the project.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chapter_snapshot_id: str = Field(default=..., description="The unique identifier of the chapter snapshot to stream.", examples=['21m00Tcm4TlvDq8ikWAM'])
class StreamChapterSnapshotAudioRequestBody(StrictModel):
    convert_to_mpeg: bool | None = Field(default=None, description="Whether to convert the streamed audio to MPEG format. Defaults to false, returning the original audio format.")
class StreamChapterSnapshotAudioRequest(StrictModel):
    """Retrieve and stream audio from a chapter snapshot. Use the list snapshots endpoint to discover available snapshots for a chapter."""
    path: StreamChapterSnapshotAudioRequestPath
    body: StreamChapterSnapshotAudioRequestBody | None = None

# Operation: list_muted_tracks
class GetProjectMutedTracksEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to query for muted tracks.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetProjectMutedTracksEndpointRequest(StrictModel):
    """Retrieves a list of chapter IDs that have muted tracks in a Studio project. Use this to identify which chapters contain audio that has been muted."""
    path: GetProjectMutedTracksEndpointRequestPath

# Operation: get_dubbing_resource
class GetDubbingResourceRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project created from the dubbing endpoint with studio mode enabled.")
class GetDubbingResourceRequest(StrictModel):
    """Retrieves the dubbing resource for a given dubbing project ID that was created with studio enabled. Use this to access the generated dubbing output and associated metadata."""
    path: GetDubbingResourceRequestPath

# Operation: add_dubbing_language
class AddLanguageRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to which the language will be added.")
class AddLanguageRequestBody(StrictModel):
    language: str | None = Field(default=..., description="The target language code in ElevenLabs Turbo V2/V2.5 format to add to the dubbing resource.")
class AddLanguageRequest(StrictModel):
    """Add a supported language to a dubbing project resource. The language is registered but does not automatically generate transcripts, translations, or audio content."""
    path: AddLanguageRequestPath
    body: AddLanguageRequestBody

# Operation: create_segment
class CreateClipRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the speaker.")
    speaker_id: str = Field(default=..., description="The unique identifier of the speaker within the dubbing project.")
class CreateClipRequestBody(StrictModel):
    start_time: float = Field(default=..., description="The start time of the segment in seconds (relative to the media timeline).")
    end_time: float = Field(default=..., description="The end time of the segment in seconds (relative to the media timeline). Must be greater than the start time.")
    translations: dict[str, str] | None = Field(default=None, description="Optional translations for the segment content, organized by language code. Specify translations for any languages beyond the default project language.")
class CreateClipRequest(StrictModel):
    """Creates a new segment for a speaker in a dubbing project with specified start and end times across all available languages. The segment is created without automatically generating transcripts, translations, or audio content."""
    path: CreateClipRequestPath
    body: CreateClipRequestBody

# Operation: update_segment_language
class UpdateSegmentLanguageRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the segment to modify.")
    segment_id: str = Field(default=..., description="The unique identifier of the segment within the dubbing project to be updated.")
    language: str = Field(default=..., description="The language identifier for which the segment content should be modified.")
class UpdateSegmentLanguageRequestBody(StrictModel):
    start_time: float | None = Field(default=None, description="The start time of the segment in seconds. Defines when the segment begins in the audio timeline.")
    end_time: float | None = Field(default=None, description="The end time of the segment in seconds. Defines when the segment ends in the audio timeline.")
class UpdateSegmentLanguageRequest(StrictModel):
    """Modify the text and/or timing of a specific segment in a particular language within a dubbing project. Changes are applied only to the specified language and do not automatically trigger dub regeneration."""
    path: UpdateSegmentLanguageRequestPath
    body: UpdateSegmentLanguageRequestBody | None = None

# Operation: reassign_segments
class MigrateSegmentsRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the segments to reassign.")
class MigrateSegmentsRequestBody(StrictModel):
    segment_ids: list[str] = Field(default=..., description="Array of segment identifiers to reassign to the target speaker. Order is preserved as provided.")
    speaker_id: str = Field(default=..., description="The unique identifier of the speaker to assign the segments to.")
class MigrateSegmentsRequest(StrictModel):
    """Reassign one or more segments in a dubbing project to a different speaker. This operation changes the speaker attribution for the specified segments."""
    path: MigrateSegmentsRequestPath
    body: MigrateSegmentsRequestBody

# Operation: delete_dubbing_segment
class DeleteSegmentRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the segment to be deleted.")
    segment_id: str = Field(default=..., description="The unique identifier of the segment to be deleted from the dubbing project.")
class DeleteSegmentRequest(StrictModel):
    """Removes a single segment from a dubbing project. This operation permanently deletes the specified segment and cannot be undone."""
    path: DeleteSegmentRequestPath

# Operation: regenerate_segment_transcriptions
class TranscribeRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the segments to transcribe.")
class TranscribeRequestBody(StrictModel):
    segments: list[str] = Field(default=..., description="An array of segment identifiers to regenerate transcriptions for. Order is preserved as provided.")
class TranscribeRequest(StrictModel):
    """Regenerate transcriptions for specified segments within a dubbing project. This operation updates only the transcription text and does not affect existing translations or dubs."""
    path: TranscribeRequestPath
    body: TranscribeRequestBody

# Operation: translate_dubbing_segments
class TranslateRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to translate.")
class TranslateRequestBody(StrictModel):
    segments: list[str] = Field(default=..., description="List of segment identifiers to translate. Only these segments will be processed; order is preserved as provided.")
    languages: list[str] = Field(default=..., description="List of target language codes to translate for each specified segment. Only these languages will be generated.")
class TranslateRequest(StrictModel):
    """Regenerate translations for specified segments and languages in a dubbing project. Automatically transcribes any missing transcriptions but does not regenerate dubs."""
    path: TranslateRequestPath
    body: TranslateRequestBody

# Operation: regenerate_dubs
class DubRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to regenerate dubs for.")
class DubRequestBody(StrictModel):
    segments: list[str] = Field(default=..., description="List of segment identifiers to dub. Only the specified segments will be processed; order is preserved as provided.")
    languages: list[str] = Field(default=..., description="List of language codes to dub for each segment. Only the specified languages will be processed; order is preserved as provided.")
class DubRequest(StrictModel):
    """Regenerate dubs for specified segments and languages in a dubbing project. Automatically transcribes and translates any missing transcriptions and translations."""
    path: DubRequestPath
    body: DubRequestBody

# Operation: update_speaker
class UpdateSpeakerRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the speaker.")
    speaker_id: str = Field(default=..., description="The unique identifier of the speaker to update.")
class UpdateSpeakerRequestBody(StrictModel):
    speaker_name: str | None = Field(default=None, description="The display name to assign to this speaker.")
    voice_id: str | None = Field(default=None, description="The voice identifier, either from the ElevenLabs voice library or a cloning option ('track-clone' or 'clip-clone').")
    voice_style: float | None = Field(default=None, description="The voice style intensity for supported models. Valid range is 0.0 to 1.0, defaults to 1.0.")
    languages: list[str] | None = Field(default=None, description="List of language codes to apply these speaker changes to. If empty or omitted, changes apply to all languages in the project.")
class UpdateSpeakerRequest(StrictModel):
    """Update speaker metadata in a dubbing project, including voice selection and styling. Supports both ElevenLabs library voices and voice cloning options."""
    path: UpdateSpeakerRequestPath
    body: UpdateSpeakerRequestBody | None = None

# Operation: add_speaker
class CreateSpeakerRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to which the speaker will be added.")
class CreateSpeakerRequestBody(StrictModel):
    speaker_name: str | None = Field(default=None, description="A human-readable label for this speaker to identify it within the dubbing project.")
    voice_id: str | None = Field(default=None, description="The voice identifier to use for this speaker. Can be a voice from the ElevenLabs voice library or a special clone type for custom voice cloning.")
    voice_style: float | None = Field(default=None, description="The voice style intensity for models that support style control. Valid range is 0.0 to 1.0, with 1.0 as the default.")
class CreateSpeakerRequest(StrictModel):
    """Add a new speaker to a dubbing project with a specified voice and optional styling. Each speaker represents a distinct voice track within the dubbing resource."""
    path: CreateSpeakerRequestPath
    body: CreateSpeakerRequestBody | None = None

# Operation: list_similar_voices
class GetSimilarVoicesForSpeakerRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the speaker.")
    speaker_id: str = Field(default=..., description="The unique identifier of the speaker within the dubbing project to find similar voices for.")
class GetSimilarVoicesForSpeakerRequest(StrictModel):
    """Retrieve the top 10 voices from the ElevenLabs library that are most similar to a specified speaker in a dubbing project. Results include voice IDs, names, descriptions, and sample audio recordings where available."""
    path: GetSimilarVoicesForSpeakerRequestPath

# Operation: render_dubbing
class RenderRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to render.")
    language: str = Field(default=..., description="The target language code for rendering (e.g., 'es' for Spanish). Use 'original' to render the source track.")
class RenderRequestBody(StrictModel):
    render_type: Literal["mp4", "aac", "mp3", "wav", "aaf", "tracks_zip", "clips_zip"] = Field(default=..., description="The output format for the rendered media.")
    normalize_volume: bool | None = Field(default=None, description="Whether to apply volume normalization to the rendered audio.")
class RenderRequest(StrictModel):
    """Generate output media for a specific language in a dubbing project using the current Studio state. All segments must be dubbed before rendering to be included in the output; renders are processed asynchronously."""
    path: RenderRequestPath
    body: RenderRequestBody

# Operation: list_dubs
class ListDubsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of dubs to return per request. Defaults to 100 if not specified.", ge=1, le=200)
    dubbing_status: Literal["dubbing", "dubbed", "failed"] | None = Field(default=None, description="Filter results by the current processing state of the dub.")
    filter_by_creator: Literal["personal", "others", "all"] | None = Field(default=None, description="Filter results by creator: show only your dubs, dubs shared by others, or all dubs you have access to.", examples=['all'])
    order_by: Literal["created_at"] | None = Field(default=None, description="Specify which field to use for ordering the results.")
    order_direction: Literal["DESCENDING", "ASCENDING"] | None = Field(default=None, description="Specify the sort direction for the ordered results.")
class ListDubsRequest(StrictModel):
    """Retrieve a list of dubs you have access to, with filtering and sorting options. Results can be filtered by status, creator, and ordered by specified fields."""
    query: ListDubsRequestQuery | None = None

# Operation: dub_media
class CreateDubbingRequestBody(StrictModel):
    csv_file: str | None = Field(default=None, description="Base64-encoded file content for upload. CSV file containing transcription and translation metadata for manual dubbing mode. Used to override automatic transcription and provide custom timing and speaker information.", json_schema_extra={'format': 'byte'})
    name: str | None = Field(default=None, description="Human-readable name for the dubbing project to help organize and identify the job.")
    source_url: str | None = Field(default=None, description="URL pointing to the source video or audio file to be dubbed. Must be publicly accessible.")
    source_lang: str | None = Field(default=None, description="Language code of the source content using ISO 639-1 or ISO 639-3 format. Set to 'auto' to automatically detect the language.")
    target_lang: str | None = Field(default=None, description="Language code for the target dub using ISO 639-1 or ISO 639-3 format. Determines which language the content will be dubbed into.")
    target_accent: str | None = Field(default=None, description="Optional accent preference to apply when selecting voices and informing translation dialect. This is an experimental feature.")
    num_speakers: int | None = Field(default=None, description="Number of distinct speakers to use in the dubbing. Set to 0 to automatically detect the speaker count from the source audio.")
    watermark: bool | None = Field(default=None, description="Whether to add a watermark overlay to the output video file.")
    start_time: int | None = Field(default=None, description="Start time in seconds from which to begin dubbing the source file. Useful for processing only a segment of the content.")
    end_time: int | None = Field(default=None, description="End time in seconds at which to stop dubbing the source file. Useful for processing only a segment of the content.")
    highest_resolution: bool | None = Field(default=None, description="Whether to process and output the video at the highest available resolution. May increase processing time and resource usage.")
    drop_background_audio: bool | None = Field(default=None, description="Whether to remove background audio from the final dub. Recommended for content like speeches or monologues where background noise should not be preserved.")
    use_profanity_filter: bool | None = Field(default=None, description="Whether to censor profanities in transcripts by replacing them with '[censored]'. This is a beta feature.")
    dubbing_studio: bool | None = Field(default=None, description="Whether to prepare the output for editing in the dubbing studio interface or as a dubbing resource for further processing.")
    disable_voice_cloning: bool | None = Field(default=None, description="Whether to use similar voices from the ElevenLabs Voice Library instead of cloning the original speaker's voice. Requires 'add_voice_from_voice_library' workspace permission and consumes available custom voice slots.")
    mode: Literal["automatic", "manual"] | None = Field(default=None, description="Processing mode for the dubbing job. Use 'automatic' for standard processing or 'manual' when providing a custom CSV transcript. Manual mode is experimental and not recommended for production use.")
    csv_fps: float | None = Field(default=None, description="Frames per second value to use when parsing timecodes in the CSV file. If omitted, FPS will be automatically inferred from the timecode data.")
class CreateDubbingRequest(StrictModel):
    """Dubs an audio or video file into a target language with automatic speaker detection and voice synthesis. Supports advanced options for quality control, voice customization, and manual transcript editing."""
    body: CreateDubbingRequestBody | None = None

# Operation: get_dubbing
class GetDubbedMetadataRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to retrieve metadata for.")
class GetDubbedMetadataRequest(StrictModel):
    """Retrieve metadata about a dubbing project, including its current processing status and completion state."""
    path: GetDubbedMetadataRequestPath

# Operation: delete_dubbing
class DeleteDubbingRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project to delete.")
class DeleteDubbingRequest(StrictModel):
    """Permanently deletes a dubbing project and all associated data. This action cannot be undone."""
    path: DeleteDubbingRequestPath

# Operation: download_dubbed_audio
class GetDubbedFileRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the dubbed content.")
    language_code: str = Field(default=..., description="The language code specifying which dubbed audio track to retrieve.")
class GetDubbedFileRequest(StrictModel):
    """Download the dubbed audio file in MP3 or MP4 format for a specific language. Returns the original automatic dub result; for edited dubs created in Dubbing Studio, use the render endpoint instead."""
    path: GetDubbedFileRequestPath

# Operation: get_transcript_dubbing
class GetDubbingTranscriptsRequestPath(StrictModel):
    dubbing_id: str = Field(default=..., description="The unique identifier of the dubbing project containing the transcript to retrieve.")
    language_code: str = Field(default=..., description="The language for which to retrieve the transcript. Use 'source' to fetch the original media transcript, or provide an ISO 639 language code.", examples=['source', 'en', 'fra'])
    format_type: Literal["srt", "webvtt", "json"] = Field(default=..., description="The output format for the transcript. Use 'srt' or 'webvtt' for subtitle formats, or 'json' for a full transcript (JSON format is not yet supported for Dubbing Studio).", examples=['srt', 'webvtt', 'json'])
class GetDubbingTranscriptsRequest(StrictModel):
    """Retrieve the transcript for a specific language in a dubbing project. Supports multiple output formats including subtitle formats (SRT, WebVTT) and JSON transcripts."""
    path: GetDubbingTranscriptsRequestPath

# Operation: create_audio_project
class CreateAudioNativeProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the audio project.")
    author: str | None = Field(default=None, description="The author name displayed in the audio player and at the start of the article. Uses the default author from Player settings if not specified.")
    voice_id: str | None = Field(default=None, description="The voice ID used for text-to-speech synthesis. Uses the default voice from Player settings if not specified.")
    model_id: str | None = Field(default=None, description="The TTS model ID used by the player. Uses the default model from Player settings if not specified.")
    auto_convert: bool | None = Field(default=None, description="Whether to automatically convert the project content to audio upon creation.")
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(default=None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always applies normalization, 'apply_english' applies normalization assuming English text, and 'off' disables normalization.")
    pronunciation_dictionary_locators: list[str] | None = Field(default=None, description="A list of pronunciation dictionary locators, each containing a pronunciation_dictionary_id and version_id pair. Multiple dictionaries can be applied to customize pronunciation of specific terms.", examples=[['{"pronunciation_dictionary_id": "21m00Tcm4TlvDq8ikWAM", "version_id": "BdF0s0aZ3oFoKnDYdTox"}']])
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. Either txt or HTML input file containing the article content. HTML should be formatted as follows '&lt;html&gt;&lt;body&gt;&lt;div&gt;&lt;p&gt;Your content&lt;/p&gt;&lt;h3&gt;More of your content&lt;/h3&gt;&lt;p&gt;Some more of your content&lt;/p&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;'", json_schema_extra={'format': 'byte'})
    text_color: dict | None = Field(default=None, description="Text color used in the player. If not provided, default text color set in the Player settings is used.")
    background_color: str | None = Field(default=None, description="Background color used in the player. If not provided, default background color set in the Player settings is used.")
class CreateAudioNativeProjectRequest(StrictModel):
    """Creates an Audio Native enabled project with optional automatic conversion to audio. Returns a project ID and embeddable HTML snippet for audio playback."""
    body: CreateAudioNativeProjectRequestBody

# Operation: get_audio_native_settings
class GetAudioNativeProjectSettingsEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project for which to retrieve Audio Native settings.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetAudioNativeProjectSettingsEndpointRequest(StrictModel):
    """Retrieve player settings and configuration for an Audio Native project. Use this to access the current settings applied to a specific project."""
    path: GetAudioNativeProjectSettingsEndpointRequestPath

# Operation: update_audio_native_content
class AudioNativeProjectUpdateContentEndpointRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the Studio project to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class AudioNativeProjectUpdateContentEndpointRequestBody(StrictModel):
    auto_convert: bool | None = Field(default=None, description="Automatically convert the project to audio format after content update.")
    auto_publish: bool | None = Field(default=None, description="Automatically publish a new project snapshot after conversion completes. Only applies when auto_convert is enabled.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. Either txt or HTML input file containing the article content. HTML should be formatted as follows '&lt;html&gt;&lt;body&gt;&lt;div&gt;&lt;p&gt;Your content&lt;/p&gt;&lt;h5&gt;More of your content&lt;/h5&gt;&lt;p&gt;Some more of your content&lt;/p&gt;&lt;/div&gt;&lt;/body&gt;&lt;/html&gt;'", json_schema_extra={'format': 'byte'})
class AudioNativeProjectUpdateContentEndpointRequest(StrictModel):
    """Updates content for an Audio-Native project with optional automatic conversion and publishing. Use this to modify project content and trigger downstream processing workflows."""
    path: AudioNativeProjectUpdateContentEndpointRequestPath
    body: AudioNativeProjectUpdateContentEndpointRequestBody | None = None

# Operation: update_audio_native_content_from_url
class AudioNativeUpdateContentFromUrlRequestBody(StrictModel):
    url: str = Field(default=..., description="The web page URL from which to extract content for the AudioNative project.", examples=['https://elevenlabs.io/blog/the_first_ai_that_can_laugh/'])
    author: str | None = Field(default=None, description="Optional author name to display in the player and insert at the start of the article. Uses the default author from Player settings if not provided.")
class AudioNativeUpdateContentFromUrlRequest(StrictModel):
    """Extracts content from a provided URL, updates the matching AudioNative project, and queues it for conversion and auto-publishing."""
    body: AudioNativeUpdateContentFromUrlRequestBody

# Operation: list_voices_shared
class GetLibraryVoicesRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of voices to return per page. Limited to 100 voices maximum.")
    category: Literal["professional", "famous", "high_quality"] | None = Field(default=None, description="Filter voices by category type.", examples=['professional'])
    gender: str | None = Field(default=None, description="Filter voices by gender.", examples=['male'])
    age: str | None = Field(default=None, description="Filter voices by age group.", examples=['young'])
    accent: str | None = Field(default=None, description="Filter voices by accent.", examples=['american'])
    language: str | None = Field(default=None, description="Filter voices by language code.", examples=['en'])
    locale: str | None = Field(default=None, description="Filter voices by locale code.", examples=['en-US'])
    use_cases: list[str] | None = Field(default=None, description="Filter voices by one or more use cases. Multiple use cases can be specified to find voices suitable for specific applications.", examples=['audiobook'])
    featured: bool | None = Field(default=None, description="When enabled, returns only voices marked as featured.", examples=[True])
    min_notice_period_days: int | None = Field(default=None, description="Filter voices that require a minimum notice period before use, specified in days.", examples=[30])
    include_custom_rates: bool | None = Field(default=None, description="When enabled, includes voices that have custom pricing rates.", examples=[True])
    include_live_moderated: bool | None = Field(default=None, description="When enabled, includes voices that are live moderated.", examples=[True])
    reader_app_enabled: bool | None = Field(default=None, description="When enabled, returns only voices that are enabled for the reader app.", examples=[True])
    owner_id: str | None = Field(default=None, description="Filter voices by the public owner ID of the voice creator.", examples=['7c9fab611d9a0e1fb2e7448a0c294a8804efc2bcc324b0a366a5d5232b7d1532'])
    sort: str | None = Field(default=None, description="Sort results by the specified criteria.", examples=['created_date'])
    page: int | None = Field(default=None, description="Page number for pagination, starting from 0.")
class GetLibraryVoicesRequest(StrictModel):
    """Retrieves a paginated list of shared voices with optional filtering by category, demographics, language, use cases, and other attributes. Useful for discovering available voices for text-to-speech applications."""
    query: GetLibraryVoicesRequestQuery | None = None

# Operation: find_similar_voices
class GetSimilarLibraryVoicesRequestBody(StrictModel):
    audio_file: str | None = Field(default=None, description="Base64-encoded file content for upload. Audio sample file to match against library voices. Used as the reference for similarity comparison.", json_schema_extra={'format': 'byte'})
    similarity_threshold: float | None = Field(default=None, description="Similarity threshold for filtering results. Lower values return more similar voices. Valid range is 0 to 2.", examples=[0.5])
    top_k: int | None = Field(default=None, description="Maximum number of similar voices to return. If similarity_threshold is also specified, fewer voices may be returned. Valid range is 1 to 100.", examples=[10])
class GetSimilarLibraryVoicesRequest(StrictModel):
    """Find voices from the library that are similar to a provided audio sample. Returns a ranked list of matching voices based on similarity scoring."""
    body: GetSimilarLibraryVoicesRequestBody | None = None

# Operation: get_character_usage_metrics
class UsageCharactersRequestQuery(StrictModel):
    start_unix: int = Field(default=..., description="Start of the usage window as a UTC Unix timestamp in milliseconds. Use 00:00:00 of the first day to include it in the results.", examples=['1685574000'])
    end_unix: int = Field(default=..., description="End of the usage window as a UTC Unix timestamp in milliseconds. Use 23:59:59 of the last day to include it in the results.", examples=['1688165999'])
    include_workspace_metrics: bool | None = Field(default=None, description="Include usage statistics for the entire workspace in addition to user-specific metrics.")
    breakdown_type: Literal["none", "voice", "voice_multiplier", "user", "groups", "api_keys", "all_api_keys", "product_type", "model", "resource", "request_queue", "region", "subresource_id", "reporting_workspace_id", "has_api_key", "request_source"] | None = Field(default=None, description="Dimension to break down usage metrics by. The 'user' breakdown requires include_workspace_metrics to be true.")
    aggregation_bucket_size: int | None = Field(default=None, description="Custom aggregation interval in seconds. When specified, overrides the default daily aggregation.")
    metric: Literal["credits", "tts_characters", "minutes_used", "request_count", "ttfb_avg", "ttfb_p95", "fiat_units_spent", "concurrency", "concurrency_average"] | None = Field(default=None, description="The usage metric to aggregate and return in the results.")
class UsageCharactersRequest(StrictModel):
    """Retrieve character usage metrics for the current user or entire workspace over a specified time period. Results can be aggregated by time interval and broken down by various dimensions such as voice, user, or API key."""
    query: UsageCharactersRequestQuery

# Operation: create_pronunciation_dictionary
class AddFromFileRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the pronunciation dictionary used for identification and reference within the system.", examples=['My Dictionary'])
    description: str | None = Field(default=None, description="An optional description of the pronunciation dictionary to provide additional context about its contents or purpose.", examples=["Contains pronunciation's of our character names"])
    workspace_access: Literal["admin", "editor", "commenter", "viewer"] | None = Field(default=None, description="The workspace access level that determines permissions for other users to interact with this dictionary. If not provided, defaults to no access.", examples=['viewer'])
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. A lexicon .pls file which we will use to initialize the project with.", json_schema_extra={'format': 'byte'})
class AddFromFileRequest(StrictModel):
    """Creates a new pronunciation dictionary from a lexicon .PLS file. The dictionary can be configured with access permissions for workspace collaboration."""
    body: AddFromFileRequestBody

# Operation: create_pronunciation_dictionary_from_rules
class AddFromRulesRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the pronunciation dictionary used for identification and reference purposes.", examples=['My Dictionary'])
    description: str | None = Field(default=None, description="An optional description of the pronunciation dictionary to provide additional context about its contents or purpose.", examples=["Contains pronunciation's of our character names"])
    workspace_access: Literal["admin", "editor", "commenter", "viewer"] | None = Field(default=None, description="The access level for workspace users. Determines whether users can administer, edit, comment on, or only view the dictionary. Defaults to no access if not specified.", examples=['viewer'])
    rules: list[dict] | None = Field(default=None, description="List of pronunciation rules. Rule can be either:\n    an alias rule: {'string_to_replace': 'a', 'type': 'alias', 'alias': 'b', }\n    or a phoneme rule: {'string_to_replace': 'a', 'type': 'phoneme', 'phoneme': 'b', 'alphabet': 'ipa' }", examples=["\n    [\n        {'string_to_replace': 'a', 'type': 'alias', 'alias': 'b' },\n        {'string_to_replace': 'c', 'type': 'phoneme', 'phoneme': 'd', 'alphabet': 'ipa' }\n    ]"])
class AddFromRulesRequest(StrictModel):
    """Creates a new pronunciation dictionary from provided rules. The dictionary can be configured with access permissions for workspace collaboration."""
    body: AddFromRulesRequestBody

# Operation: get_pronunciation_dictionary
class GetPronunciationDictionaryMetadataRequestPath(StrictModel):
    pronunciation_dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary to retrieve metadata for.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetPronunciationDictionaryMetadataRequest(StrictModel):
    """Retrieve metadata for a specific pronunciation dictionary by its ID. Returns configuration details and properties of the pronunciation dictionary."""
    path: GetPronunciationDictionaryMetadataRequestPath

# Operation: update_pronunciation_dictionary
class PatchPronunciationDictionaryRequestPath(StrictModel):
    pronunciation_dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class PatchPronunciationDictionaryRequestBody(StrictModel):
    archived: bool | None = Field(default=None, description="Set whether the pronunciation dictionary should be archived. Archived dictionaries are retained but no longer active.", examples=[True])
    name: str | None = Field(default=None, description="A human-readable name for the pronunciation dictionary used for identification and organization purposes.", examples=['My Dictionary'])
class PatchPronunciationDictionaryRequest(StrictModel):
    """Partially update a pronunciation dictionary by modifying its name or archive status without affecting the version. Only specified fields will be updated."""
    path: PatchPronunciationDictionaryRequestPath
    body: PatchPronunciationDictionaryRequestBody | None = None

# Operation: replace_pronunciation_rules
class SetRulesRequestPath(StrictModel):
    pronunciation_dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class SetRulesRequestBody(StrictModel):
    rules: list[PronunciationDictionaryAliasRuleRequestModel | PronunciationDictionaryPhonemeRuleRequestModel] = Field(default=..., description="An ordered list of pronunciation rules to apply. Each rule maps a string to either an alias (another string) or a phoneme (with a specified alphabet such as IPA). All existing rules will be replaced with this list.", examples=["\n    [\n        {'string_to_replace': 'a', 'type': 'alias', 'alias': 'b' },\n        {'string_to_replace': 'c', 'type': 'phoneme', 'phoneme': 'd', 'alphabet': 'ipa' }\n    ]"])
class SetRulesRequest(StrictModel):
    """Replace all pronunciation rules in a dictionary with a new set of rules. Rules can define phonetic aliases or phoneme mappings using specified alphabets."""
    path: SetRulesRequestPath
    body: SetRulesRequestBody

# Operation: add_pronunciation_rules
class AddRulesRequestPath(StrictModel):
    pronunciation_dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary to modify.", examples=['21m00Tcm4TlvDq8ikWAM'])
class AddRulesRequestBody(StrictModel):
    rules: list[PronunciationDictionaryAliasRuleRequestModel | PronunciationDictionaryPhonemeRuleRequestModel] = Field(default=..., description="An ordered list of pronunciation rules to add or update. Each rule must be either an alias rule (mapping one string to another alias) or a phoneme rule (mapping a string to a phoneme in a specified alphabet such as IPA).", examples=["\n    [\n        {'string_to_replace': 'a', 'type': 'alias', 'alias': 'b' },\n        {'string_to_replace': 'c', 'type': 'phoneme', 'phoneme': 'd', 'alphabet': 'ipa' }\n    ]"])
class AddRulesRequest(StrictModel):
    """Add or update pronunciation rules in a dictionary. Rules with duplicate string_to_replace values will replace existing rules."""
    path: AddRulesRequestPath
    body: AddRulesRequestBody

# Operation: delete_pronunciation_rules
class RemoveRulesRequestPath(StrictModel):
    pronunciation_dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary from which rules will be removed.", examples=['21m00Tcm4TlvDq8ikWAM'])
class RemoveRulesRequestBody(StrictModel):
    rule_strings: list[str] = Field(default=..., description="An array of rule strings to remove from the pronunciation dictionary. Each string represents a rule to be deleted. Order is not significant.", examples=["['a', 'b']"])
class RemoveRulesRequest(StrictModel):
    """Remove one or more pronunciation rules from a pronunciation dictionary. Specify the dictionary ID and provide the list of rule strings to be deleted."""
    path: RemoveRulesRequestPath
    body: RemoveRulesRequestBody

# Operation: download_pronunciation_dictionary_version
class GetPronunciationDictionaryVersionPlsRequestPath(StrictModel):
    dictionary_id: str = Field(default=..., description="The unique identifier of the pronunciation dictionary to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
    version_id: str = Field(default=..., description="The unique identifier of the specific version of the pronunciation dictionary to download.", examples=['BdF0s0aZ3oFoKnDYdTox'])
class GetPronunciationDictionaryVersionPlsRequest(StrictModel):
    """Download a PLS (Pronunciation Lexicon Specification) file containing the rules for a specific version of a pronunciation dictionary."""
    path: GetPronunciationDictionaryVersionPlsRequestPath

# Operation: list_pronunciation_dictionaries
class GetPronunciationDictionariesMetadataRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of pronunciation dictionaries to return per request. Must be between 1 and 100.", ge=1, le=100)
    sort: Literal["creation_time_unix", "name"] | None = Field(default=None, description="Field to sort the results by. Choose between creation time or alphabetical name ordering.", examples=['creation_time_unix'])
    sort_direction: str | None = Field(default=None, description="Direction to sort the results in. Use ascending for oldest-first or newest-first, descending for newest-first or Z-to-A ordering.", examples=['descending'])
class GetPronunciationDictionariesMetadataRequest(StrictModel):
    """Retrieve a paginated list of pronunciation dictionaries you have access to, with sorting and filtering options. Returns metadata for each dictionary including creation date and name."""
    query: GetPronunciationDictionariesMetadataRequestQuery | None = None

# Operation: list_service_account_api_keys
class GetServiceAccountApiKeysRouteRequestPath(StrictModel):
    service_account_user_id: str = Field(default=..., description="The unique identifier of the service account for which to retrieve API keys.")
class GetServiceAccountApiKeysRouteRequest(StrictModel):
    """Retrieve all API keys associated with a specific service account. Use this to view and manage authentication credentials for programmatic access."""
    path: GetServiceAccountApiKeysRouteRequestPath

# Operation: create_service_account_api_key
class CreateServiceAccountApiKeyRequestPath(StrictModel):
    service_account_user_id: str = Field(default=..., description="The unique identifier of the service account for which to create the API key.")
class CreateServiceAccountApiKeyRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the API key to help identify its purpose or usage context.")
    permissions: list[Literal["text_to_speech", "speech_to_speech", "speech_to_text", "models_read", "models_write", "voices_read", "voices_write", "speech_history_read", "speech_history_write", "sound_generation", "audio_isolation", "voice_generation", "dubbing_read", "dubbing_write", "pronunciation_dictionaries_read", "pronunciation_dictionaries_write", "user_read", "user_write", "projects_read", "projects_write", "audio_native_read", "audio_native_write", "workspace_read", "workspace_write", "forced_alignment", "convai_read", "convai_write", "music_generation", "image_video_generation", "add_voice_from_voice_library", "create_instant_voice_clone", "create_professional_voice_clone", "publish_voice_to_voice_library", "share_voice_externally", "create_user_api_key", "workspace_analytics_full_read", "webhooks_write", "service_account_write", "group_members_manage", "workspace_members_read", "workspace_members_invite", "workspace_members_remove", "terms_of_service_accept"]] | Literal["all"] = Field(default=..., description="The set of permissions to grant this API key, controlling which XI API operations it can perform.")
    character_limit: int | None = Field(default=None, description="Optional monthly character limit for this API key. When set, requests that would exceed this limit will be rejected, preventing unexpected usage charges.")
class CreateServiceAccountApiKeyRequest(StrictModel):
    """Generate a new API key for a service account with specified permissions and optional usage limits. The created key can be used to authenticate requests to the XI API on behalf of the service account."""
    path: CreateServiceAccountApiKeyRequestPath
    body: CreateServiceAccountApiKeyRequestBody

# Operation: revoke_service_account_api_key
class DeleteServiceAccountApiKeyRequestPath(StrictModel):
    service_account_user_id: str = Field(default=..., description="The unique identifier of the service account that owns the API key to be deleted.")
    api_key_id: str = Field(default=..., description="The unique identifier of the API key to be revoked and deleted.")
class DeleteServiceAccountApiKeyRequest(StrictModel):
    """Revoke and permanently delete an API key associated with a service account. This action cannot be undone."""
    path: DeleteServiceAccountApiKeyRequestPath

# Operation: delete_auth_connection
class DeleteAuthConnectionRequestPath(StrictModel):
    auth_connection_id: str = Field(default=..., description="The unique identifier of the authentication connection to delete.")
class DeleteAuthConnectionRequest(StrictModel):
    """Delete an authentication connection from the workspace. This removes the stored credentials and configuration for the specified auth connection."""
    path: DeleteAuthConnectionRequestPath

# Operation: find_group
class SearchGroupsRequestQuery(StrictModel):
    name: str = Field(default=..., description="The name of the user group to search for. The search will match against group names in the workspace.")
class SearchGroupsRequest(StrictModel):
    """Searches for user groups in the workspace by name. Returns matching group(s) or an empty result if no groups are found."""
    query: SearchGroupsRequestQuery

# Operation: remove_group_member
class RemoveMemberRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group from which the member will be removed.")
class RemoveMemberRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the workspace member to remove from the group.")
class RemoveMemberRequest(StrictModel):
    """Remove a member from a user group. Requires `group_members_manage` permission to perform this action."""
    path: RemoveMemberRequestPath
    body: RemoveMemberRequestBody

# Operation: add_group_member
class AddMemberRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to which the member will be added.")
class AddMemberRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the workspace member to add to the group.")
class AddMemberRequest(StrictModel):
    """Adds a workspace member to a user group. Requires group_members_manage permission."""
    path: AddMemberRequestPath
    body: AddMemberRequestBody

# Operation: send_workspace_invite
class InviteUserRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the user to invite to the workspace.", examples=['john.doe@testmail.com'])
    seat_type: Literal["workspace_admin", "workspace_member", "workspace_lite_member"] | None = Field(default=None, description="The permission level to assign the invited user within the workspace.", examples=['workspace_member', 'workspace_admin'])
    group_ids: list[str] | None = Field(default=None, description="List of group IDs to assign the invited user to. Groups determine access permissions and organizational structure within the workspace.", examples=[['group_id_1', 'group_id_2']])
class InviteUserRequest(StrictModel):
    """Sends an email invitation to join the workspace. The recipient will be prompted to create an account if needed, and upon acceptance will be added as a workspace user consuming one available seat. Requires WORKSPACE_MEMBERS_INVITE permission."""
    body: InviteUserRequestBody

# Operation: send_workspace_invitations
class InviteUsersBulkRequestBody(StrictModel):
    emails: list[str] = Field(default=..., description="List of email addresses to invite. All emails must belong to verified domains associated with your workspace.", examples=['john.doe@testmail.com'])
    seat_type: Literal["workspace_admin", "workspace_member", "workspace_lite_member"] | None = Field(default=None, description="The permission level to assign to invited users within the workspace.", examples=['workspace_member', 'workspace_admin'])
    group_ids: list[str] | None = Field(default=None, description="List of group IDs to assign the invited users to upon acceptance. Groups organize users and manage permissions within the workspace.", examples=[['group_id_1', 'group_id_2']])
class InviteUsersBulkRequest(StrictModel):
    """Send email invitations to multiple users to join your workspace. Invitees must have email addresses from verified domains, and accepted invitations will add them as workspace users consuming available seats."""
    body: InviteUsersBulkRequestBody

# Operation: revoke_workspace_invitation
class DeleteInviteRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the invitation recipient whose invitation should be revoked.", examples=['john.doe@testmail.com'])
class DeleteInviteRequest(StrictModel):
    """Revoke an existing workspace invitation by email address. The invitation will remain visible in the recipient's inbox but will no longer be activatable to join the workspace. Only workspace members with WORKSPACE_MEMBERS_INVITE permission can perform this action."""
    body: DeleteInviteRequestBody

# Operation: get_resource
class GetResourceMetadataRequestPath(StrictModel):
    resource_id: str = Field(default=..., description="The unique identifier of the resource to retrieve.")
class GetResourceMetadataRequestQuery(StrictModel):
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(default=..., description="The category of the resource. Determines which resource type's metadata will be returned.")
class GetResourceMetadataRequest(StrictModel):
    """Retrieves metadata for a specific resource by its ID and type. Use this to fetch detailed information about any resource in your workspace."""
    path: GetResourceMetadataRequestPath
    query: GetResourceMetadataRequestQuery

# Operation: grant_resource_access
class ShareResourceEndpointRequestPath(StrictModel):
    resource_id: str = Field(default=..., description="The unique identifier of the resource to share.")
class ShareResourceEndpointRequestBody(StrictModel):
    role: Literal["admin", "editor", "commenter", "viewer"] = Field(default=..., description="The access level to grant to the principal. Determines what actions the principal can perform on the resource.")
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(default=..., description="The category of resource being shared. Determines the type of object referenced by resource_id.")
    user_email: str | None = Field(default=None, description="The email address of the user or service account to grant access to. The principal must already exist in your workspace.")
    group_id: str | None = Field(default=None, description="The unique identifier of the group to grant access to. Use the special value 'default' to target the default permissions principals have on this resource.")
    workspace_api_key_id: str | None = Field(default=None, description="The unique identifier of the workspace API key to grant access to. This is the key ID found in workspace settings, not the API key credential itself. Access will be granted to the service account associated with this key.")
class ShareResourceEndpointRequest(StrictModel):
    """Grant or update a role on a workspace resource for a user, service account, group, or API key. This operation overrides any existing role the principal has on the resource. You must have admin access to the resource to perform this action."""
    path: ShareResourceEndpointRequestPath
    body: ShareResourceEndpointRequestBody

# Operation: revoke_resource_access
class UnshareResourceEndpointRequestPath(StrictModel):
    resource_id: str = Field(default=..., description="The unique identifier of the workspace resource to revoke access from.")
class UnshareResourceEndpointRequestBody(StrictModel):
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(default=..., description="The category of the workspace resource being modified.")
    user_email: str | None = Field(default=None, description="The email address of the user or service account to revoke access from. The user or service account must exist in your workspace.")
    group_id: str | None = Field(default=None, description="The identifier of the group to revoke access from. Use 'default' to target default permissions principals have on this resource.")
    workspace_api_key_id: str | None = Field(default=None, description="The identifier of the workspace API key to revoke access from. This is the key ID found in workspace settings, not the authentication key itself. Access will be revoked from the service account associated with this API key.")
class UnshareResourceEndpointRequest(StrictModel):
    """Removes all access permissions for a user, service account, group, or workspace API key to a workspace resource. The requester must have admin access to the resource."""
    path: UnshareResourceEndpointRequestPath
    body: UnshareResourceEndpointRequestBody

# Operation: list_workspace_webhooks
class GetWorkspaceWebhooksRouteRequestQuery(StrictModel):
    include_usages: bool | None = Field(default=None, description="Include active usage statistics for each webhook. Only accessible to workspace administrators.", examples=[False])
class GetWorkspaceWebhooksRouteRequest(StrictModel):
    """Retrieve all webhooks configured for a workspace. Optionally include active usage statistics for each webhook (admin-only feature)."""
    query: GetWorkspaceWebhooksRouteRequestQuery | None = None

# Operation: transcribe_audio
class SpeechToTextRequestBody(StrictModel):
    model_id: Literal["scribe_v1", "scribe_v2"] = Field(default=..., description="The transcription model to use. Choose between scribe_v1 (standard) or scribe_v2 (enhanced with additional features like verbatim control).")
    language_code: str | None = Field(default=None, description="ISO-639-1 or ISO-639-3 language code of the audio content. Providing the language can improve transcription accuracy; if omitted, language is automatically detected.")
    tag_audio_events: bool | None = Field(default=None, description="Whether to identify and tag audio events such as laughter, footsteps, and other non-speech sounds in the transcript.")
    num_speakers: int | None = Field(default=None, description="Maximum number of speakers expected in the audio. Helps the model predict speaker transitions more accurately. If not specified, the model uses its maximum supported speaker count (up to 32).", ge=1, le=32)
    timestamps_granularity: Literal["none", "word", "character"] | None = Field(default=None, description="Timestamp precision level in the transcript. 'word' provides timestamps for each word, 'character' provides character-level timestamps within words, and 'none' omits timestamps.")
    diarize: bool | None = Field(default=None, description="Whether to perform speaker diarization to identify and label which speaker is talking at each point in the transcript.")
    diarization_threshold: float | None = Field(default=None, description="Sensitivity threshold for speaker diarization (only applies when diarize is true and num_speakers is not specified). Higher values reduce speaker fragmentation but increase the risk of merging distinct speakers; lower values do the opposite. The model selects a default threshold based on the chosen model_id if not provided.", ge=0.1, le=0.4)
    additional_formats: list[ExportOptions] | None = Field(default=None, description="List of additional output formats to generate alongside the default transcript. Each format can optionally include speaker labels and timestamps. Maximum of 10 formats per request.", max_length=10, examples=[[{'format': 'srt', 'include_speakers': True, 'include_timestamps': True}, {'format': 'txt', 'include_speakers': False}]])
    cloud_storage_url: str | None = Field(default=None, description="HTTPS URL of the audio or video file to transcribe. The file must be publicly accessible and under 2GB. Supports cloud storage URLs (S3, Google Cloud Storage, Cloudflare R2) and pre-signed URLs with authentication tokens. Exactly one of file or cloud_storage_url must be provided.", examples=['https://storage.googleapis.com/my-bucket/folder/audio.mp3', 'https://my-bucket.s3.us-west-2.amazonaws.com/folder/audio.mp3', 'https://account123.r2.cloudflarestorage.com/my-bucket/audio.mp3', 'https://cdn.example.com/media/audio.wav'])
    webhook: bool | None = Field(default=None, description="Whether to process the request asynchronously and deliver results via configured webhooks. When enabled, the request returns immediately without the transcription result.")
    webhook_id: str | None = Field(default=None, description="ID of a specific webhook endpoint to receive the transcription result. Only valid when webhook is true. If omitted, results are sent to all configured speech-to-text webhooks.")
    use_multi_channel: bool | None = Field(default=None, description="Whether to transcribe multi-channel audio independently, treating each channel as a separate speaker. Supports up to 5 channels; each word in the response includes a channel_index field indicating its source channel.")
    webhook_metadata: str | dict[str, Any] | None = Field(default=None, description="Custom metadata to include in webhook responses for request correlation and tracking. Must be a JSON object with maximum depth of 2 levels and total size under 16KB. Useful for associating results with internal IDs or job references.", examples=['{"user_id": "123", "session_id": "abc-def-ghi"}', '{"request_type": "interview", "participant_name": "John Doe"}'])
    entity_detection: str | list[str] | None = Field(default=None, description="Entity detection configuration to identify and extract entities from the transcript. Accepts 'all' for all entity types, specific entity type names, or a list of types/categories (pii, phi, pci, other, offensive_language). Detected entities are returned with their text, type, and character positions. Incurs additional costs.")
    no_verbatim: bool | None = Field(default=None, description="Whether to remove filler words, false starts, and non-speech sounds from the transcript for a cleaner output. Only supported with the scribe_v2 model.")
    entity_redaction: str | list[str] | None = Field(default=None, description="Entity types or categories to redact from the transcript text. Accepts the same format as entity_detection ('all', specific categories like 'pii' or 'phi', or a list of entity types). Must be a subset of entity_detection if both are specified. When redaction is enabled, the entities field is not returned.")
    keyterms: list[str] | None = Field(default=None, description="List of domain-specific words or phrases to bias the model toward recognizing with higher accuracy. Each keyterm must be under 50 characters and contain at most 5 words. Maximum 1000 keyterms per request. Requests with over 100 keyterms incur a minimum 20-second billable duration. Incurs additional costs.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The file to transcribe. All major audio and video formats are supported. Exactly one of the file or cloud_storage_url parameters must be provided. The file size must be less than 3.0GB.", json_schema_extra={'format': 'byte'})
class SpeechToTextRequest(StrictModel):
    """Transcribe audio or video files to text with support for speaker diarization, multi-channel processing, and entity detection. Supports synchronous responses or asynchronous webhook delivery with optional custom metadata for request tracking."""
    body: SpeechToTextRequestBody

# Operation: get_transcript
class GetTranscriptByIdRequestPath(StrictModel):
    transcription_id: str = Field(default=..., description="The unique identifier of the transcript to retrieve.")
class GetTranscriptByIdRequest(StrictModel):
    """Retrieve a previously generated transcript by its unique identifier. Use this operation to access transcription results after they have been processed."""
    path: GetTranscriptByIdRequestPath

# Operation: delete_transcript
class DeleteTranscriptByIdRequestPath(StrictModel):
    transcription_id: str = Field(default=..., description="The unique identifier of the transcript to delete.")
class DeleteTranscriptByIdRequest(StrictModel):
    """Permanently delete a transcript by its unique ID. This action cannot be undone."""
    path: DeleteTranscriptByIdRequestPath

# Operation: get_evaluation_criterion
class GetEvalCriterionRouteRequestPath(StrictModel):
    criterion_id: str = Field(default=..., description="The unique identifier of the evaluation criterion to retrieve.")
class GetEvalCriterionRouteRequest(StrictModel):
    """Retrieve a specific evaluation criterion by its ID for speech-to-text evaluation tasks. Use this to fetch detailed information about a criterion used in assessment workflows."""
    path: GetEvalCriterionRouteRequestPath

# Operation: update_eval_criterion
class UpdateEvalCriterionRouteRequestPath(StrictModel):
    criterion_id: str = Field(default=..., description="The unique identifier of the evaluation criterion to update.")
class UpdateEvalCriterionRouteRequestBodyDataExtractionConfig(StrictModel):
    fields: list[DataExtractionFieldRequest] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="An array of field identifiers or definitions associated with this evaluation criterion. Specifies which fields are evaluated.")
class UpdateEvalCriterionRouteRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The name of the evaluation criterion. Must be between 1 and 200 characters.", min_length=1, max_length=200)
    criteria: list[CriterionItemRequest] | None = Field(default=None, description="An array of evaluation criteria details. Order and structure should match the evaluation framework requirements.")
    data_extraction_config: UpdateEvalCriterionRouteRequestBodyDataExtractionConfig
class UpdateEvalCriterionRouteRequest(StrictModel):
    """Update an existing evaluation criterion for speech-to-text assessment. Modify the criterion name, evaluation criteria details, and associated fields."""
    path: UpdateEvalCriterionRouteRequestPath
    body: UpdateEvalCriterionRouteRequestBody

# Operation: delete_evaluation_criterion
class DeleteEvalCriterionRouteRequestPath(StrictModel):
    criterion_id: str = Field(default=..., description="The unique identifier of the evaluation criterion to delete.")
class DeleteEvalCriterionRouteRequest(StrictModel):
    """Delete a specific evaluation criterion from the speech-to-text evaluation system. This operation permanently removes the criterion and cannot be undone."""
    path: DeleteEvalCriterionRouteRequestPath

# Operation: list_evaluations
class ListEvaluationsRouteRequestQuery(StrictModel):
    agent_id: str | None = Field(default=None, description="Filter evaluations by the agent ID that created or is associated with the evaluation.")
    eval_criterion_id: str | None = Field(default=None, description="Filter evaluations by the evaluation criterion ID used to assess performance.")
    status: str | None = Field(default=None, description="Filter evaluations by their current status (e.g., pending, completed, failed).")
    created_after: str | None = Field(default=None, description="Filter evaluations created on or after this date. Use ISO 8601 format.")
    created_before: str | None = Field(default=None, description="Filter evaluations created on or before this date. Use ISO 8601 format.")
    sort_by: str | None = Field(default=None, description="Sort results by a specific field (e.g., created_at, status, agent_id).")
    sort_dir: str | None = Field(default=None, description="Sort direction for results: ascending or descending order.")
    page_size: int | None = Field(default=None, description="Number of evaluations to return per page for pagination.")
class ListEvaluationsRouteRequest(StrictModel):
    """Retrieve a list of speech-to-text evaluations with filtering, sorting, and pagination options. Filter by agent, evaluation criterion, status, and creation date range."""
    query: ListEvaluationsRouteRequestQuery | None = None

# Operation: create_evaluation
class TriggerEvaluationRouteRequestBody(StrictModel):
    transcript_id: str = Field(default=..., description="The unique identifier of the transcript to be evaluated.")
    agent_id: str = Field(default=..., description="The unique identifier of the agent performing the evaluation.")
    eval_criterion_id: str = Field(default=..., description="The unique identifier of the evaluation criterion to apply during the evaluation.")
    labels: dict[str, str] | None = Field(default=None, description="Custom labels or metadata to attach to the evaluation as key-value pairs.")
    agent_name: str | None = Field(default=None, description="The display name of the agent performing the evaluation for reference purposes.")
class TriggerEvaluationRouteRequest(StrictModel):
    """Trigger a new evaluation for a speech-to-text transcript by specifying the transcript, evaluating agent, and evaluation criteria. Optionally provide custom labels and agent name for context."""
    body: TriggerEvaluationRouteRequestBody

# Operation: get_evaluation
class GetEvaluationRouteRequestPath(StrictModel):
    evaluation_id: str = Field(default=..., description="The unique identifier of the evaluation to retrieve.")
class GetEvaluationRouteRequest(StrictModel):
    """Retrieve detailed information about a specific speech-to-text evaluation by its unique identifier."""
    path: GetEvaluationRouteRequestPath

# Operation: list_human_agents
class ListHumanAgentsRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of human agents to return per page. Controls pagination size for the results.")
class ListHumanAgentsRouteRequest(StrictModel):
    """Retrieve a paginated list of human agents available for speech-to-text evaluation tasks. Use pagination to control the number of results returned per request."""
    query: ListHumanAgentsRouteRequestQuery | None = None

# Operation: get_human_agent
class GetHumanAgentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the human agent to retrieve.")
class GetHumanAgentRouteRequest(StrictModel):
    """Retrieve detailed information about a specific human agent in the speech-to-text evaluation system. Use this to access agent profiles and evaluation data."""
    path: GetHumanAgentRouteRequestPath

# Operation: delete_human_agent
class DeleteHumanAgentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the human agent to delete.")
class DeleteHumanAgentRouteRequest(StrictModel):
    """Remove a human agent from the speech-to-text evaluation system. This operation permanently deletes the agent and their associated routing configuration."""
    path: DeleteHumanAgentRouteRequestPath

# Operation: list_evaluation_analytics
class GetEvaluationAnalyticsRouteRequestQuery(StrictModel):
    created_after: str | None = Field(default=None, description="Filter results to include only evaluations created on or after this date. Specify in ISO 8601 format.")
    created_before: str | None = Field(default=None, description="Filter results to include only evaluations created on or before this date. Specify in ISO 8601 format.")
class GetEvaluationAnalyticsRouteRequest(StrictModel):
    """Retrieve analytics data for speech-to-text evaluations, optionally filtered by creation date range. Use this to analyze evaluation metrics and performance trends over time."""
    query: GetEvaluationAnalyticsRouteRequestQuery | None = None

# Operation: get_criterion_analytics
class GetCriterionAnalyticsRouteRequestPath(StrictModel):
    criterion_id: str = Field(default=..., description="The unique identifier of the evaluation criterion to retrieve analytics for.")
class GetCriterionAnalyticsRouteRequestQuery(StrictModel):
    created_after: str | None = Field(default=None, description="Filter analytics to include only records created on or after this date. Specify in ISO 8601 format.")
    created_before: str | None = Field(default=None, description="Filter analytics to include only records created on or before this date. Specify in ISO 8601 format.")
class GetCriterionAnalyticsRouteRequest(StrictModel):
    """Retrieve analytics data for a specific evaluation criterion, with optional filtering by creation date range. Use this to analyze performance metrics and insights for a particular criterion."""
    path: GetCriterionAnalyticsRouteRequestPath
    query: GetCriterionAnalyticsRouteRequestQuery | None = None

# Operation: get_agent_analytics
class GetAgentAnalyticsRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the human agent for which to retrieve analytics.")
class GetAgentAnalyticsRouteRequestQuery(StrictModel):
    created_after: str | None = Field(default=None, description="Filter to include only analytics created on or after this date. Specify in ISO 8601 format.")
    created_before: str | None = Field(default=None, description="Filter to include only analytics created on or before this date. Specify in ISO 8601 format.")
class GetAgentAnalyticsRouteRequest(StrictModel):
    """Retrieve analytics data for a specific human agent in the speech-to-text evaluation system. Optionally filter results by creation date range."""
    path: GetAgentAnalyticsRouteRequestPath
    query: GetAgentAnalyticsRouteRequestQuery | None = None

# Operation: align_audio_to_text
class ForcedAlignmentRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The audio file to align with the transcript. Supports all major audio formats with a maximum file size of 1GB.", json_schema_extra={'format': 'byte'})
    text: str = Field(default=..., description="The text transcript to align with the audio. Can be in any text format; diarization (speaker identification) is not currently supported.")
    enabled_spooled_file: bool | None = Field(default=None, description="Enable streaming processing for large files that cannot fit in memory. When true, the file is streamed to the server and processed in chunks.")
class ForcedAlignmentRequest(StrictModel):
    """Synchronize an audio file with a text transcript to extract precise timing information for each character and word. Supports all major audio formats up to 1GB in size."""
    body: ForcedAlignmentRequestBody

# Operation: get_agent_conversation_signed_link
class GetConversationSignedLinkRequestQuery(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent with which to start the conversation.", examples=['21m00Tcm4TlvDq8ikWAM'])
    include_conversation_id: bool | None = Field(default=None, description="Whether to include a unique conversation ID in the response. When enabled, the signed URL can only be used once.")
    branch_id: str | None = Field(default=None, description="The specific branch variant of the agent to use for the conversation.")
class GetConversationSignedLinkRequest(StrictModel):
    """Generate a signed URL to initiate a conversation with an authorized agent. The signed URL provides secure access to start a new conversation session."""
    query: GetConversationSignedLinkRequestQuery

# Operation: initiate_outbound_call
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(StrictModel):
    soft_timeout_config: dict[str, Any] | None = Field(default=None, validation_alias="soft_timeout_config", serialization_alias="soft_timeout_config", description="Configuration for soft timeout feedback, allowing the agent to provide immediate responses (e.g., acknowledgments) while processing longer LLM responses.")
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(StrictModel):
    voice_id: str | None = Field(default=None, validation_alias="voice_id", serialization_alias="voice_id", description="Identifier for the text-to-speech voice to use for agent responses.")
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls the consistency of the generated speech, with higher values producing more stable output.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Controls the playback speed of generated speech, where higher values increase speech rate.")
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Controls how closely the generated speech matches the target voice characteristics.")
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="Optional initial message the agent will speak when the call connects. If omitted, the agent waits for the caller to speak first.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="Language code for the agent's automatic speech recognition and text-to-speech processing.")
    prompt: dict[str, Any] | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="Configuration object specifying the LLM model and system prompt that defines the agent's behavior and knowledge.")
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(StrictModel):
    turn: HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn | None = None
    tts: HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts | None = None
    agent: HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent | None = None
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(StrictModel):
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The platform or integration through which the call was initiated.")
class HandleTwilioOutboundCallRequestBodyConversationInitiationClientData(StrictModel):
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="Identifier for the end user or customer participating in this call, used for tracking and attribution by the agent owner.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Key-value pairs of custom variables that can be referenced in the agent's prompt or system instructions to personalize the conversation.")
    conversation_config_override: HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride | None = None
    source_info: HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataSourceInfo | None = None
class HandleTwilioOutboundCallRequestBody(StrictModel):
    agent_id: str = Field(default=..., description="Unique identifier of the AI agent that will handle the call.")
    agent_phone_number_id: str = Field(default=..., description="Identifier of the Twilio phone number resource to use as the caller.")
    to_number: str = Field(default=..., description="The destination phone number to call in E.164 format or standard phone number format.")
    call_recording_enabled: bool | None = Field(default=None, description="Whether Twilio should record the audio of this call for compliance, quality assurance, or archival purposes.")
    conversation_initiation_client_data: HandleTwilioOutboundCallRequestBodyConversationInitiationClientData | None = None
class HandleTwilioOutboundCallRequest(StrictModel):
    """Initiate an outbound phone call through Twilio with AI agent capabilities, including voice synthesis, language support, and optional call recording."""
    body: HandleTwilioOutboundCallRequestBody

# Operation: initiate_twilio_call
class RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(StrictModel):
    soft_timeout_config: dict[str, Any] | None = Field(default=None, validation_alias="soft_timeout_config", serialization_alias="soft_timeout_config", description="Configuration for soft timeout feedback, allowing the agent to provide immediate acknowledgment messages while processing longer LLM responses.")
class RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(StrictModel):
    voice_id: str | None = Field(default=None, validation_alias="voice_id", serialization_alias="voice_id", description="Identifier for the text-to-speech voice model to use for agent responses.")
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls the consistency of generated speech output, affecting how natural and varied the voice sounds.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Controls the playback speed of generated speech, where higher values increase speech rate.")
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Controls how closely the generated speech matches the target voice characteristics.")
class RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="Opening message the agent will speak when the call connects. If empty, the agent waits for the caller to speak first.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="Language code for automatic speech recognition (ASR) and text-to-speech (TTS) processing during the call.")
    prompt: dict[str, Any] | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="Configuration object containing the LLM model identifier and system prompt that defines the agent's behavior and knowledge domain.")
class RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverride(StrictModel):
    turn: RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn | None = None
    tts: RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts | None = None
    agent: RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent | None = None
class RegisterTwilioCallRequestBodyConversationInitiationClientDataSourceInfo(StrictModel):
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="Channel or platform through which this call was initiated, used for analytics and routing decisions.")
class RegisterTwilioCallRequestBodyConversationInitiationClientData(StrictModel):
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="Identifier for the end user or customer participating in this call, used by the agent owner for tracking and analytics.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Custom key-value variables that can be passed to the agent prompt for dynamic personalization or context injection during the conversation.")
    conversation_config_override: RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverride | None = None
    source_info: RegisterTwilioCallRequestBodyConversationInitiationClientDataSourceInfo | None = None
class RegisterTwilioCallRequestBody(StrictModel):
    agent_id: str = Field(default=..., description="Unique identifier of the AI agent that will handle this call.")
    from_number: str = Field(default=..., description="The phone number initiating the call (caller ID for outbound, destination for inbound).")
    to_number: str = Field(default=..., description="The phone number receiving the call (destination for outbound, caller ID for inbound).")
    direction: Literal["inbound", "outbound"] | None = Field(default=None, description="Direction of the call flow. Inbound calls originate from external parties; outbound calls are initiated by the system.")
    conversation_initiation_client_data: RegisterTwilioCallRequestBodyConversationInitiationClientData | None = None
class RegisterTwilioCallRequest(StrictModel):
    """Initiate a Twilio voice call with an AI agent and return TwiML configuration for call routing. Supports both inbound and outbound call directions with customizable agent behavior, voice settings, and conversation parameters."""
    body: RegisterTwilioCallRequestBody

# Operation: initiate_whatsapp_call
class WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(StrictModel):
    soft_timeout_config: dict[str, Any] | None = Field(default=None, validation_alias="soft_timeout_config", serialization_alias="soft_timeout_config", description="Configuration for soft timeout feedback, allowing the agent to send intermediate messages while processing longer LLM responses to keep the conversation feeling responsive.")
class WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(StrictModel):
    voice_id: str | None = Field(default=None, validation_alias="voice_id", serialization_alias="voice_id", description="The voice ID to use for text-to-speech synthesis during the call.")
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="The stability parameter for speech synthesis, controlling consistency of the generated voice.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="The speed parameter for speech synthesis, controlling how fast the agent speaks.")
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="The similarity boost parameter for speech synthesis, controlling how closely the voice matches the selected voice ID.")
class WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="The initial message the agent will speak when the call connects. If empty, the agent will wait for the user to speak first.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="The language code for the agent's automatic speech recognition and text-to-speech (e.g., 'en-US', 'es-ES').")
    prompt: dict[str, Any] | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="The system prompt that defines the agent's behavior, personality, and instructions for handling the conversation.")
class WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(StrictModel):
    turn: WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn | None = None
    tts: WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts | None = None
    agent: WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent | None = None
class WhatsappOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(StrictModel):
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The source or channel through which the call was initiated.")
class WhatsappOutboundCallRequestBodyConversationInitiationClientData(StrictModel):
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The ID of the end user initiating this call, used by the agent owner for tracking and identifying conversation participants.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Dynamic variables that can be passed to customize the agent's behavior and responses during the call.")
    conversation_config_override: WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride | None = None
    source_info: WhatsappOutboundCallRequestBodyConversationInitiationClientDataSourceInfo | None = None
class WhatsappOutboundCallRequestBody(StrictModel):
    whatsapp_phone_number_id: str = Field(default=..., description="The WhatsApp Business Account phone number ID that will be used to make the outbound call.")
    whatsapp_user_id: str = Field(default=..., description="The WhatsApp user ID of the recipient who will receive the outbound call.")
    whatsapp_call_permission_request_template_name: str = Field(default=..., description="The name of the WhatsApp-approved call permission request template to use for initiating the call.")
    whatsapp_call_permission_request_template_language_code: str = Field(default=..., description="The language code of the call permission request template (e.g., 'en_US', 'es_ES').")
    agent_id: str = Field(default=..., description="The ID of the AI agent that will handle the conversation during the call.")
    conversation_initiation_client_data: WhatsappOutboundCallRequestBodyConversationInitiationClientData | None = None
class WhatsappOutboundCallRequest(StrictModel):
    """Initiate an outbound voice call to a WhatsApp user through a configured WhatsApp Business Account. The call uses a pre-approved permission request template and connects to an AI agent for conversation."""
    body: WhatsappOutboundCallRequestBody

# Operation: send_whatsapp_message
class WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(StrictModel):
    soft_timeout_config: dict[str, Any] | None = Field(default=None, validation_alias="soft_timeout_config", serialization_alias="soft_timeout_config", description="Configuration for soft timeout feedback, allowing the agent to send intermediate messages (e.g., acknowledgments) while processing longer responses.")
class WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(StrictModel):
    voice_id: str | None = Field(default=None, validation_alias="voice_id", serialization_alias="voice_id", description="The voice ID to use for text-to-speech synthesis when the agent responds with audio.")
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls the consistency of the generated speech, ranging from low variability to high variability.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Controls the speed of generated speech playback.")
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Controls how closely the generated speech matches the selected voice characteristics.")
class WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="The initial message the agent will send to start the conversation. If empty, the agent waits for the user to send the first message.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="The language for the agent's automatic speech recognition (ASR) and text-to-speech (TTS) processing.")
    prompt: dict[str, Any] | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="Configuration object containing the LLM model and system prompt that defines the agent's behavior and capabilities.")
class WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverride(StrictModel):
    turn: WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn | None = None
    tts: WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTts | None = None
    agent: WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent | None = None
class WhatsappOutboundMessageRequestBodyConversationInitiationClientDataSourceInfo(StrictModel):
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The channel or platform through which this conversation was initiated.")
class WhatsappOutboundMessageRequestBodyConversationInitiationClientData(StrictModel):
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="Identifier for the end user participating in this conversation, used by the agent owner for tracking and analytics.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Additional dynamic variables to be substituted into the template or used by the agent during the conversation.")
    conversation_config_override: WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverride | None = None
    source_info: WhatsappOutboundMessageRequestBodyConversationInitiationClientDataSourceInfo | None = None
class WhatsappOutboundMessageRequestBody(StrictModel):
    whatsapp_phone_number_id: str = Field(default=..., description="The WhatsApp phone number ID associated with your business account that will send the message.")
    whatsapp_user_id: str = Field(default=..., description="The WhatsApp user ID (recipient) who will receive the message.")
    template_name: str = Field(default=..., description="The name of the WhatsApp message template to use for this outbound message.")
    template_language_code: str = Field(default=..., description="The language code for the template (e.g., 'en', 'es', 'fr'). Must match the template's supported languages.")
    template_params: list[WhatsAppTemplateHeaderComponentParams | WhatsAppTemplateBodyComponentParams | WhatsAppTemplateButtonComponentParams] = Field(default=..., description="An ordered array of parameter values to substitute into the template placeholders. Order and format must match the template definition.")
    agent_id: str = Field(default=..., description="The ID of the AI agent that will handle the conversation if this message initiates an interactive session.")
    conversation_initiation_client_data: WhatsappOutboundMessageRequestBodyConversationInitiationClientData | None = None
class WhatsappOutboundMessageRequest(StrictModel):
    """Send an outbound message to a WhatsApp user using a predefined template with optional AI agent configuration for interactive conversations."""
    body: WhatsappOutboundMessageRequestBody

# Operation: create_agent_route
class CreateAgentRouteRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A name to make the agent easier to find", examples=['My agent'])
    tags: list[str] | None = Field(default=None, description="Tags to help classify and filter the agent", examples=[['Customer Support', 'Technical Help', 'Eleven']])
    platform_settings: CreateAgentRouteBodyPlatformSettings | None = Field(default=None, description="Platform settings including widget config, auth, privacy, guardrails, and evaluation")
    conversation_config: CreateAgentRouteBodyConversationConfig | None = Field(default=None, description="Conversation configuration including ASR, TTS, turn handling, and agent prompt settings")
    workflow: CreateAgentRouteBodyWorkflow | None = Field(default=None, description="Workflow definition with nodes and edges")
class CreateAgentRouteRequest(StrictModel):
    """Create Agent"""
    body: CreateAgentRouteRequestBody | None = None

# Operation: list_agent_summaries
class GetAgentSummariesRouteRequestQuery(StrictModel):
    agent_ids: list[str] = Field(default=..., description="List of agent IDs to retrieve summaries for. Order is not significant. Each ID should be a valid agent identifier.", examples=['J3Pbu5gP6NNKBscdCdwB', 'K4Qcu6hQ7OOLCtdeDeXC'])
class GetAgentSummariesRouteRequest(StrictModel):
    """Retrieve summaries for the specified agents. Provide a list of agent IDs to get their summary information."""
    query: GetAgentSummariesRouteRequestQuery

# Operation: get_agent
class GetAgentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to retrieve.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class GetAgentRouteRequestQuery(StrictModel):
    version_id: str | None = Field(default=None, description="The specific version of the agent to retrieve. If not provided, the latest version is used.", examples=['agtvrsn_8901k4t9z5defmb8vh3e9361y7nj'])
    branch_id: str | None = Field(default=None, description="The specific branch of the agent to retrieve. If not provided, the default branch is used.", examples=['agtbranch_0901k4aafjxxfxt93gd841r7tv5t'])
class GetAgentRouteRequest(StrictModel):
    """Retrieve the configuration and settings for a specific agent. Optionally specify a particular version or branch to retrieve."""
    path: GetAgentRouteRequestPath
    query: GetAgentRouteRequestQuery | None = None

# Operation: update_agent_settings
class PatchAgentSettingsRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to update.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class PatchAgentSettingsRouteRequestQuery(StrictModel):
    enable_versioning_if_not_enabled: bool | None = Field(default=None, description="Automatically enable versioning for this agent if not already enabled, allowing you to track and manage configuration changes.")
    branch_id: str | None = Field(default=None, description="The branch identifier to target for updates. If not specified, updates apply to the main agent configuration.", examples=['agtbranch_0901k4aafjxxfxt93gd841r7tv5t'])
class PatchAgentSettingsRouteRequestBodyWorkflow(StrictModel):
    edges: dict[str, WorkflowEdgeModelInput] | None = Field(default=None, validation_alias="edges", serialization_alias="edges", description="Workflow edges defining connections and transitions between nodes in the agent's conversation flow.")
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(default=None, validation_alias="nodes", serialization_alias="nodes", description="Workflow nodes representing conversation states, actions, or processing steps in the agent's logic.", min_length=1)
class PatchAgentSettingsRouteRequestBody(StrictModel):
    conversation_config: dict[str, Any] | None = Field(default=None, description="Configuration settings that control conversation behavior, orchestration, and interaction patterns.")
    platform_settings: dict[str, Any] | None = Field(default=None, description="Platform-level settings for deployment, integrations, and non-conversation features.")
    name: str | None = Field(default=None, description="A human-readable name for the agent to improve discoverability and organization.", examples=['My agent'])
    tags: list[str] | None = Field(default=None, description="Classification tags for organizing and filtering agents by category or function.", examples=[['Customer Support', 'Technical Help', 'Eleven']])
    version_description: str | None = Field(default=None, description="A description of the changes in this version, used when publishing updates to versioned agents.")
    workflow: PatchAgentSettingsRouteRequestBodyWorkflow | None = None
class PatchAgentSettingsRouteRequest(StrictModel):
    """Updates agent settings including conversation configuration, platform settings, workflow structure, metadata, and versioning. Changes are applied to the specified agent or branch."""
    path: PatchAgentSettingsRouteRequestPath
    query: PatchAgentSettingsRouteRequestQuery | None = None
    body: PatchAgentSettingsRouteRequestBody | None = None

# Operation: delete_agent
class DeleteAgentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to delete.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class DeleteAgentRouteRequest(StrictModel):
    """Permanently delete an agent and remove it from the system. This action cannot be undone."""
    path: DeleteAgentRouteRequestPath

# Operation: get_agent_widget_config
class GetAgentWidgetRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose widget configuration you want to retrieve.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class GetAgentWidgetRouteRequestQuery(StrictModel):
    conversation_signature: str | None = Field(default=None, description="An optional expiring token that enables WebSocket conversation initiation. Generate tokens using the conversation signed URL endpoint.")
class GetAgentWidgetRouteRequest(StrictModel):
    """Retrieve the widget configuration for a specific agent, including settings needed to embed or display the agent's conversational interface."""
    path: GetAgentWidgetRouteRequestPath
    query: GetAgentWidgetRouteRequestQuery | None = None

# Operation: get_agent_share_link
class GetAgentLinkRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent for which to retrieve the share link.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class GetAgentLinkRouteRequest(StrictModel):
    """Retrieve the shareable link for an agent that can be used to share the agent with others."""
    path: GetAgentLinkRouteRequestPath

# Operation: upload_agent_avatar
class PostAgentAvatarRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to update with the new avatar image.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class PostAgentAvatarRouteRequestBody(StrictModel):
    avatar_file: str = Field(default=..., description="Base64-encoded file content for upload. An image file to use as the agent's avatar. The file will be processed and stored for display in the widget.", json_schema_extra={'format': 'byte'})
class PostAgentAvatarRouteRequest(StrictModel):
    """Upload and set a profile image for an agent that will be displayed in the chat widget."""
    path: PostAgentAvatarRouteRequestPath
    body: PostAgentAvatarRouteRequestBody

# Operation: list_agents
class GetAgentsRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of agents to return per request. Must be between 1 and 100.", ge=1, le=100)
    archived: bool | None = Field(default=None, description="Filter results to show only archived or active agents.", examples=[False])
    created_by_user_id: str | None = Field(default=None, description="Filter agents by the user ID of their creator. Use '@me' to refer to the authenticated user. Takes precedence over other ownership filters.")
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Order direction for sorting results in ascending or descending sequence.")
    sort_by: Literal["name", "created_at"] | None = Field(default=None, description="Field to sort results by. Choose between agent name or creation timestamp.")
class GetAgentsRouteRequest(StrictModel):
    """Retrieve a paginated list of your agents with their metadata. Results can be filtered by archived status and creator, and sorted by name or creation date."""
    query: GetAgentsRouteRequestQuery | None = None

# Operation: get_knowledge_base_size
class GetAgentKnowledgeBaseSizeRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose knowledge base size you want to retrieve.")
class GetAgentKnowledgeBaseSizeRequest(StrictModel):
    """Retrieves the total number of pages stored in an agent's knowledge base. Use this to understand the size and scope of the knowledge base associated with a specific agent."""
    path: GetAgentKnowledgeBaseSizeRequestPath

# Operation: estimate_agent_llm_cost
class GetAgentLlmExpectedCostCalculationRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent for which to calculate expected LLM token usage.")
class GetAgentLlmExpectedCostCalculationRequestBody(StrictModel):
    prompt_length: int | None = Field(default=None, description="The length of the input prompt in characters. Used to estimate token consumption for the prompt component.")
    number_of_pages: int | None = Field(default=None, description="The total number of pages in PDF documents or URLs indexed in the agent's Knowledge Base. Used to estimate token consumption for RAG retrieval and context injection.")
    rag_enabled: bool | None = Field(default=None, description="Whether Retrieval-Augmented Generation (RAG) is enabled for the agent. When enabled, additional tokens are consumed for knowledge base retrieval and context augmentation.")
class GetAgentLlmExpectedCostCalculationRequest(StrictModel):
    """Estimates the expected number of LLM tokens required for an agent based on prompt length, knowledge base content, and RAG configuration. Use this to forecast token consumption and associated costs before deployment."""
    path: GetAgentLlmExpectedCostCalculationRequestPath
    body: GetAgentLlmExpectedCostCalculationRequestBody | None = None

# Operation: duplicate_agent
class DuplicateAgentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to duplicate.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class DuplicateAgentRouteRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional custom name for the duplicated agent to help identify it.", examples=['My agent'])
class DuplicateAgentRouteRequest(StrictModel):
    """Create a new agent by duplicating an existing agent. The new agent will have the same configuration as the source agent, with an optional custom name."""
    path: DuplicateAgentRouteRequestPath
    body: DuplicateAgentRouteRequestBody | None = None

# Operation: simulate_agent_conversation
class RunConversationSimulationRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to simulate. This ID is provided when the agent is created.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfigPrompt(StrictModel):
    prompt: str | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="System prompt that guides the agent's behavior, personality, and response style.")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(default=None, validation_alias="llm", serialization_alias="llm", description="The language model to use for generating agent responses. Ensure the selected model is supported in your data residency environment if applicable.")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(default=None, validation_alias="reasoning_effort", serialization_alias="reasoning_effort", description="Control the model's reasoning depth. Higher effort levels enable more complex reasoning but may increase latency. Only supported by certain models.")
    thinking_budget: int | None = Field(default=None, validation_alias="thinking_budget", serialization_alias="thinking_budget", description="Maximum number of tokens allocated for the model's internal reasoning process. Set to 0 to disable thinking if the model supports it.")
    max_tokens: int | None = Field(default=None, validation_alias="max_tokens", serialization_alias="max_tokens", description="Maximum number of tokens the model can generate in its response. Use -1 for unlimited tokens (respects model defaults).")
    built_in_tools: dict[str, Any] | None = Field(default=None, validation_alias="built_in_tools", serialization_alias="built_in_tools", description="System tools available to the agent during the conversation, such as web search, calculator, or database lookup.")
    native_mcp_server_ids: list[str] | None = Field(default=None, validation_alias="native_mcp_server_ids", serialization_alias="native_mcp_server_ids", description="List of Native MCP (Model Context Protocol) server IDs that provide additional capabilities and integrations to the agent.", max_length=10)
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(default=None, validation_alias="knowledge_base", serialization_alias="knowledge_base", description="Knowledge bases the agent can reference to retrieve relevant information and context during conversations.")
    custom_llm: dict[str, Any] | None = Field(default=None, validation_alias="custom_llm", serialization_alias="custom_llm", description="Custom LLM configuration details when using a proprietary or self-hosted language model. Required if llm is set to 'custom-llm'.")
    ignore_default_personality: bool | None = Field(default=None, validation_alias="ignore_default_personality", serialization_alias="ignore_default_personality", description="Exclude the default personality and behavioral guidelines from the system prompt, allowing full control via the custom prompt parameter.")
    rag: dict[str, Any] | None = Field(default=None, validation_alias="rag", serialization_alias="rag", description="Retrieval-Augmented Generation (RAG) settings to enable the agent to search and cite information from external sources.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Timezone for displaying the current time in the system prompt. Use standard timezone identifiers to ensure accurate time context in agent responses.")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(default=None, validation_alias="backup_llm_config", serialization_alias="backup_llm_config", description="Fallback LLM configuration for automatic cascading if the primary model fails or times out. Can be disabled, use system defaults, or specify a custom priority order.")
    cascade_timeout_seconds: float | None = Field(default=None, validation_alias="cascade_timeout_seconds", serialization_alias="cascade_timeout_seconds", description="Time in seconds to wait before cascading to a backup LLM if the primary model does not respond.", ge=2.0, le=15.0)
class RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfig(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="Optional opening message for the agent to deliver. If provided, the agent speaks first; if empty, the simulated user initiates the conversation.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="Language code for the agent's speech recognition and text-to-speech capabilities.")
    hinglish_mode: bool | None = Field(default=None, validation_alias="hinglish_mode", serialization_alias="hinglish_mode", description="Enable Hinglish (Hindi-English mix) responses when language is set to Hindi.")
    disable_first_message_interruptions: bool | None = Field(default=None, validation_alias="disable_first_message_interruptions", serialization_alias="disable_first_message_interruptions", description="Prevent the simulated user from interrupting the agent while the first message is being delivered.")
    prompt: RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfigPrompt | None = None
class RunConversationSimulationRouteRequestBodySimulationSpecification(StrictModel):
    tool_mock_config: dict[str, ToolMockConfig] | None = Field(default=None, validation_alias="tool_mock_config", serialization_alias="tool_mock_config", description="Mock configurations for tools to simulate tool responses without making actual external calls.")
    partial_conversation_history: list[ConversationHistoryTranscriptCommonModelInput] | None = Field(default=None, validation_alias="partial_conversation_history", serialization_alias="partial_conversation_history", description="Pre-existing conversation history to resume from. Allows testing agent behavior in the context of an ongoing conversation rather than starting fresh.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Dynamic variables to inject into the prompt and conversation context, enabling parameterized testing scenarios.")
    simulated_user_config: RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfig | None = None
class RunConversationSimulationRouteRequestBody(StrictModel):
    extra_evaluation_criteria: list[PromptEvaluationCriteria] | None = Field(default=None, description="Custom evaluation criteria to assess agent performance during the simulation, such as response quality, accuracy, or adherence to guidelines.")
    new_turns_limit: int | None = Field(default=None, description="Maximum number of conversation turns to generate in the simulation. Prevents excessively long simulations.")
    simulation_specification: RunConversationSimulationRouteRequestBodySimulationSpecification | None = None
class RunConversationSimulationRouteRequest(StrictModel):
    """Simulate a conversation between an AI agent and a simulated user to test agent behavior, responses, and conversation flow. Useful for validating agent configurations, prompts, and tool integrations before deployment."""
    path: RunConversationSimulationRouteRequestPath
    body: RunConversationSimulationRouteRequestBody | None = None

# Operation: simulate_conversation_stream
class RunConversationSimulationRouteStreamRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to simulate the conversation with.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfigPrompt(StrictModel):
    prompt: str | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="System prompt that guides the agent's behavior and responses during the conversation.")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(default=None, validation_alias="llm", serialization_alias="llm", description="The language model to use for generating agent responses. Must be supported in your data residency environment if applicable.")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(default=None, validation_alias="reasoning_effort", serialization_alias="reasoning_effort", description="Level of reasoning effort for the model. Only applicable to models that support extended reasoning.")
    thinking_budget: int | None = Field(default=None, validation_alias="thinking_budget", serialization_alias="thinking_budget", description="Maximum number of tokens allocated for model thinking. Set to 0 to disable thinking if supported by the model.")
    max_tokens: int | None = Field(default=None, validation_alias="max_tokens", serialization_alias="max_tokens", description="Maximum number of tokens the model can generate in its response. Use -1 for no limit.")
    built_in_tools: dict[str, Any] | None = Field(default=None, validation_alias="built_in_tools", serialization_alias="built_in_tools", description="Built-in system tools available to the agent during the conversation (e.g., web search, calculator, file operations).")
    native_mcp_server_ids: list[str] | None = Field(default=None, validation_alias="native_mcp_server_ids", serialization_alias="native_mcp_server_ids", description="List of Native MCP server identifiers to integrate with the agent for extended functionality.", max_length=10)
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(default=None, validation_alias="knowledge_base", serialization_alias="knowledge_base", description="List of knowledge bases the agent can reference to provide informed responses.")
    custom_llm: dict[str, Any] | None = Field(default=None, validation_alias="custom_llm", serialization_alias="custom_llm", description="Configuration object for a custom LLM provider. Required when llm parameter is set to 'custom-llm'.")
    ignore_default_personality: bool | None = Field(default=None, validation_alias="ignore_default_personality", serialization_alias="ignore_default_personality", description="Exclude default personality traits and behavioral guidelines from the system prompt.")
    rag: dict[str, Any] | None = Field(default=None, validation_alias="rag", serialization_alias="rag", description="Configuration for Retrieval-Augmented Generation to enhance agent responses with external data sources.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Timezone identifier for displaying current time in the system prompt. Use standard timezone names to ensure accurate time context.")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(default=None, validation_alias="backup_llm_config", serialization_alias="backup_llm_config", description="Configuration for fallback LLM cascading behavior when the primary model is unavailable or times out.")
    cascade_timeout_seconds: float | None = Field(default=None, validation_alias="cascade_timeout_seconds", serialization_alias="cascade_timeout_seconds", description="Time in seconds to wait before cascading to a backup LLM if the primary model does not respond.", ge=2.0, le=15.0)
class RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfig(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="Optional initial message for the agent to speak. If empty, the agent waits for the simulated user to initiate the conversation.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="Language code for the agent's speech recognition and text-to-speech processing.")
    hinglish_mode: bool | None = Field(default=None, validation_alias="hinglish_mode", serialization_alias="hinglish_mode", description="Enable Hinglish (Hindi-English mix) responses when language is set to Hindi.")
    disable_first_message_interruptions: bool | None = Field(default=None, validation_alias="disable_first_message_interruptions", serialization_alias="disable_first_message_interruptions", description="Prevent the simulated user from interrupting the agent while the first message is being delivered.")
    prompt: RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfigPrompt | None = None
class RunConversationSimulationRouteStreamRequestBodySimulationSpecification(StrictModel):
    tool_mock_config: dict[str, ToolMockConfig] | None = Field(default=None, validation_alias="tool_mock_config", serialization_alias="tool_mock_config", description="Configuration for mocking tool responses during simulation to test agent behavior without executing real tools.")
    partial_conversation_history: list[ConversationHistoryTranscriptCommonModelInput] | None = Field(default=None, validation_alias="partial_conversation_history", serialization_alias="partial_conversation_history", description="Existing conversation history to resume from. If empty, the simulation starts fresh. Messages should be in chronological order.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Dynamic variables to inject into the agent's context and prompts during the conversation simulation.")
    simulated_user_config: RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfig | None = None
class RunConversationSimulationRouteStreamRequestBody(StrictModel):
    extra_evaluation_criteria: list[PromptEvaluationCriteria] | None = Field(default=None, description="List of custom evaluation criteria to assess the agent's performance during the conversation simulation.")
    new_turns_limit: int | None = Field(default=None, description="Maximum number of new conversation turns to generate before ending the simulation.")
    simulation_specification: RunConversationSimulationRouteStreamRequestBodySimulationSpecification | None = None
class RunConversationSimulationRouteStreamRequest(StrictModel):
    """Simulate a conversation between an agent and a simulated user with streamed responses. The response streams partial message lists that should be concatenated, concluding with a final message containing conversation analysis."""
    path: RunConversationSimulationRouteStreamRequestPath
    body: RunConversationSimulationRouteStreamRequestBody | None = None

# Operation: create_agent_test
class CreateAgentResponseTestRouteRequestBody(StrictModel):
    from_conversation_metadata: TestFromConversationMetadataInput | None = Field(default=None, description="Metadata from the source conversation if this test was derived from an existing conversation.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, description="Key-value pairs to substitute into the agent configuration during test execution, enabling parameterized testing.")
    chat_history: list[ConversationHistoryTranscriptCommonModelInput] | None = Field(default=None, description="Conversation history to provide context for the agent's response. Ordered list of messages representing the dialogue leading up to the test.", max_length=200)
    type_: Literal["llm"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Type of test to execute. Determines whether the test evaluates LLM responses or simulated conversations.")
    success_condition: str | None = Field(default=None, description="Evaluation prompt that determines test success. Should be a boolean-returning prompt that assesses whether the agent's response meets expectations.")
    success_examples: list[AgentSuccessfulResponseExample] | None = Field(default=None, description="Reference responses demonstrating successful agent behavior. Used to validate that the agent produces similar quality responses.", max_length=5)
    failure_examples: list[AgentFailureResponseExample] | None = Field(default=None, description="Reference responses demonstrating failed agent behavior. Used to ensure the agent avoids producing similar problematic responses.", max_length=5)
    name: str = Field(default=..., description="Human-readable name for this test case.")
    tool_call_parameters: UnitTestToolCallEvaluationModelInput | None = Field(default=None, description="Criteria for evaluating tool calls made by the agent. Leave empty to skip tool call validation.")
    check_any_tool_matches: bool | None = Field(default=None, description="When true, the test passes if any tool call matches the criteria. When false, the test fails if the agent returns multiple tool calls.")
    simulation_scenario: str | None = Field(default=None, description="Description of the simulated user scenario and persona for simulation-based tests. Provides context for multi-turn conversation evaluation.")
    simulation_max_turns: int | None = Field(default=None, description="Maximum number of conversation turns to execute in simulation tests. Controls test duration and complexity.", ge=1, le=50)
    simulation_environment: str | None = Field(default=None, description="Execution environment for the simulation test. Defaults to production if not specified.")
class CreateAgentResponseTestRouteRequest(StrictModel):
    """Creates a new test case for evaluating agent responses. Tests can validate response quality, tool usage, or simulate multi-turn conversations with configurable success criteria."""
    body: CreateAgentResponseTestRouteRequestBody

# Operation: get_agent_test
class GetAgentResponseTestRouteRequestPath(StrictModel):
    test_id: str = Field(default=..., description="The unique identifier of the agent response test to retrieve.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class GetAgentResponseTestRouteRequest(StrictModel):
    """Retrieves a specific agent response test by its ID. Use this to fetch details about a previously created test."""
    path: GetAgentResponseTestRouteRequestPath

# Operation: update_agent_test
class UpdateAgentResponseTestRouteRequestPath(StrictModel):
    test_id: str = Field(default=..., description="The unique identifier of the agent response test to update.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class UpdateAgentResponseTestRouteRequestBody(StrictModel):
    from_conversation_metadata: TestFromConversationMetadataInput | None = Field(default=None, description="Metadata from the conversation this test was originally created from, if applicable.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, description="Key-value pairs of dynamic variables to substitute into the agent configuration during test execution.")
    chat_history: list[ConversationHistoryTranscriptCommonModelInput] | None = Field(default=None, description="Conversation history to use as context for the test. Ordered list of messages exchanged before the agent response being tested.", max_length=200)
    type_: Literal["llm"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of test to run. Determines how the agent response is evaluated.")
    success_condition: str | None = Field(default=None, description="A prompt that evaluates whether the agent's response meets success criteria. Should return a boolean value (True for success, False for failure).")
    success_examples: list[AgentSuccessfulResponseExample] | None = Field(default=None, description="List of example responses that should be considered successful outcomes. Used to validate test behavior.", max_length=5)
    failure_examples: list[AgentFailureResponseExample] | None = Field(default=None, description="List of example responses that should be considered failures. Used to validate test behavior.", max_length=5)
    name: str = Field(default=..., description="A descriptive name for the test.")
    tool_call_parameters: UnitTestToolCallEvaluationModelInput | None = Field(default=None, description="Criteria for evaluating tool calls made by the agent. If not provided, tool call validation is skipped.")
    check_any_tool_matches: bool | None = Field(default=None, description="When True, the test passes if any tool call matches the criteria. When False, the test fails if the agent returns multiple tool calls.")
    simulation_scenario: str | None = Field(default=None, description="Description of the simulation scenario and user persona for simulation-based tests.")
    simulation_max_turns: int | None = Field(default=None, description="Maximum number of conversation turns allowed in simulation tests. Controls test duration and complexity.", ge=1, le=50)
    simulation_environment: str | None = Field(default=None, description="The environment context for running the simulation test. Defaults to production if not specified.")
class UpdateAgentResponseTestRouteRequest(StrictModel):
    """Updates an agent response test configuration by ID. Allows modification of test criteria, success/failure examples, dynamic variables, and simulation settings."""
    path: UpdateAgentResponseTestRouteRequestPath
    body: UpdateAgentResponseTestRouteRequestBody

# Operation: delete_agent_test
class DeleteChatResponseTestRouteRequestPath(StrictModel):
    test_id: str = Field(default=..., description="The unique identifier of the agent response test to delete.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class DeleteChatResponseTestRouteRequest(StrictModel):
    """Deletes an agent response test by its ID. This removes the test configuration and associated test data from the system."""
    path: DeleteChatResponseTestRouteRequestPath

# Operation: fetch_agent_response_test_summaries
class GetAgentResponseTestsSummariesRouteRequestBody(StrictModel):
    test_ids: list[str] = Field(default=..., description="List of unique test IDs to retrieve summaries for. Each ID identifies a specific agent response test.", examples=[['test_id_1', 'test_id_2']])
class GetAgentResponseTestsSummariesRouteRequest(StrictModel):
    """Retrieve summaries for multiple agent response tests by their IDs. Returns a mapping of test IDs to their corresponding test summary data."""
    body: GetAgentResponseTestsSummariesRouteRequestBody

# Operation: list_agent_tests
class ListChatResponseTestsRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of tests to return per request. Must be between 1 and 100.", ge=1, le=100)
    types: list[Literal["llm", "tool", "simulation", "folder"]] | None = Field(default=None, description="Filter results to include only tests and folders matching the specified types. When provided, only items of these types are returned.")
    sort_mode: Literal["default", "folders_first"] | None = Field(default=None, description="Determines the sort order for results. Use 'folders_first' to display folders before tests, or 'default' for standard ordering.")
class ListChatResponseTestsRouteRequest(StrictModel):
    """Retrieve a paginated list of agent response tests with optional filtering by test type and custom sorting. Supports organizing results with folders displayed first if needed."""
    query: ListChatResponseTestsRouteRequestQuery | None = None

# Operation: list_test_invocations
class ListTestInvocationsRouteRequestQuery(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose test invocations should be retrieved.")
    page_size: int | None = Field(default=None, description="Maximum number of test invocations to return per request. Defaults to 30 if not specified.", ge=1, le=100)
class ListTestInvocationsRouteRequest(StrictModel):
    """Retrieve a paginated list of test invocations for a specific agent. Supports optional pagination control to manage result set size."""
    query: ListTestInvocationsRouteRequestQuery

# Operation: run_agent_tests
class RunAgentTestSuiteRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to test.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class RunAgentTestSuiteRouteRequestBody(StrictModel):
    tests: list[SingleTestRunRequestModel] = Field(default=..., description="Array of test configurations to execute. Each test validates specific agent behaviors or criteria.", min_length=1, max_length=1000)
    branch_id: str | None = Field(default=None, description="Agent branch identifier to test against. If omitted, tests run on the default agent configuration.")
    agent_config_override: RunAgentTestSuiteRouteBodyAgentConfigOverride | None = Field(default=None, description="Agent configuration overrides for test execution")
class RunAgentTestSuiteRouteRequest(StrictModel):
    """Execute a suite of tests against a conversational AI agent with optional configuration overrides. Tests validate agent behavior, quality, and compliance against specified criteria."""
    path: RunAgentTestSuiteRouteRequestPath
    body: RunAgentTestSuiteRouteRequestBody

# Operation: get_test_invocation
class GetTestInvocationRouteRequestPath(StrictModel):
    test_invocation_id: str = Field(default=..., description="The unique identifier of the test invocation to retrieve. This ID is provided when tests are executed.")
class GetTestInvocationRouteRequest(StrictModel):
    """Retrieves a specific test invocation by its ID. Use this to fetch details about a test invocation that was previously executed."""
    path: GetTestInvocationRouteRequestPath

# Operation: resubmit_tests
class ResubmitTestsRouteRequestPath(StrictModel):
    test_invocation_id: str = Field(default=..., description="The unique identifier of the test invocation containing the test runs to resubmit. This ID is returned when tests are initially executed.")
class ResubmitTestsRouteRequestBody(StrictModel):
    test_run_ids: list[str] = Field(default=..., description="List of test run IDs to resubmit. Each ID identifies a specific test case within the invocation to be re-executed.", min_length=1, max_length=1000)
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose tests should be resubmitted.")
    branch_id: str | None = Field(default=None, description="Branch ID for running tests against a specific agent variant or configuration. If omitted, tests run against the agent's default configuration.")
    agent_config_override: ResubmitTestsRouteBodyAgentConfigOverride | None = Field(default=None, description="Agent configuration overrides for test resubmission")
class ResubmitTestsRouteRequest(StrictModel):
    """Resubmit specific test runs from a completed test invocation to re-evaluate agent performance with potentially updated configurations. Allows selective resubmission of individual test cases within a test batch."""
    path: ResubmitTestsRouteRequestPath
    body: ResubmitTestsRouteRequestBody

# Operation: list_conversations
class GetConversationHistoriesRouteRequestQuery(StrictModel):
    agent_id: str | None = Field(default=None, description="Filter conversations to a specific agent by its unique identifier.", examples=['21m00Tcm4TlvDq8ikWAM'])
    call_successful: Literal["success", "failure", "unknown"] | None = Field(default=None, description="Filter conversations by the result of the success evaluation.", examples=['success'])
    call_duration_min_secs: int | None = Field(default=None, description="Filter conversations with a minimum call duration in seconds.")
    call_duration_max_secs: int | None = Field(default=None, description="Filter conversations with a maximum call duration in seconds.")
    rating_max: int | None = Field(default=None, description="Filter conversations with a maximum overall rating on a scale of 1-5.", ge=1, le=5)
    rating_min: int | None = Field(default=None, description="Filter conversations with a minimum overall rating on a scale of 1-5.", ge=1, le=5)
    has_feedback_comment: bool | None = Field(default=None, description="Filter to only conversations that include user feedback comments.")
    user_id: str | None = Field(default=None, description="Filter conversations by the user ID who initiated them.")
    evaluation_params: list[str] | None = Field(default=None, description="Filter by evaluation criteria results. Specify as criteria_id:result pairs; parameter can be repeated for multiple criteria.")
    data_collection_params: list[str] | None = Field(default=None, description="Filter by data collection fields using comparison operators. Format: id:op:value where op is one of eq, neq, gt, gte, lt, lte, in, exists, or missing. For 'in' operator, pipe-delimit multiple values. Parameter can be repeated for multiple filters.")
    tool_names: list[str] | None = Field(default=None, description="Filter conversations by the names of tools used during the call. Specify multiple tool names as separate array items.")
    main_languages: list[str] | None = Field(default=None, description="Filter conversations by detected main language using language codes. Specify multiple languages as separate array items.")
    page_size: int | None = Field(default=None, description="Maximum number of conversations to return per request. Cannot exceed 100.", ge=1, le=100)
    summary_mode: Literal["exclude", "include"] | None = Field(default=None, description="Include or exclude transcript summaries in the response.")
    conversation_initiation_source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, description="Filter conversations by their initiation source (SDK, integration, or communication platform).")
    branch_id: str | None = Field(default=None, description="Filter conversations by branch ID.")
class GetConversationHistoriesRouteRequest(StrictModel):
    """Retrieve all conversations for agents owned by the user, with extensive filtering options by agent, call metrics, ratings, evaluation results, and conversation metadata."""
    query: GetConversationHistoriesRouteRequestQuery | None = None

# Operation: list_conversation_users
class GetConversationUsersRouteRequestQuery(StrictModel):
    agent_id: str | None = Field(default=None, description="The ID of the agent to filter conversations by.", examples=['21m00Tcm4TlvDq8ikWAM'])
    branch_id: str | None = Field(default=None, description="Filter conversations to a specific branch by its ID.")
    page_size: int | None = Field(default=None, description="Maximum number of users to return per page. Valid range is 1 to 100.", ge=1, le=100)
    sort_by: Literal["last_contact_unix_secs", "conversation_count"] | None = Field(default=None, description="Field to sort results by. Choose between most recent contact time or total conversation count.")
class GetConversationUsersRouteRequest(StrictModel):
    """Retrieve a paginated list of distinct users from conversations, with options to filter by agent and branch, and sort by contact recency or conversation frequency."""
    query: GetConversationUsersRouteRequestQuery | None = None

# Operation: get_conversation
class GetConversationHistoryRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetConversationHistoryRouteRequest(StrictModel):
    """Retrieve the full details and history of a specific conversation by its ID. Use this to access conversation metadata, messages, and related information."""
    path: GetConversationHistoryRouteRequestPath

# Operation: delete_conversation
class DeleteConversationRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation to delete.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteConversationRouteRequest(StrictModel):
    """Permanently delete a conversation and all associated data. This action cannot be undone."""
    path: DeleteConversationRouteRequestPath

# Operation: get_conversation_audio
class GetConversationAudioRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation whose audio recording you want to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetConversationAudioRouteRequest(StrictModel):
    """Retrieve the audio recording of a specific conversation. Returns the audio file associated with the conversation ID."""
    path: GetConversationAudioRouteRequestPath

# Operation: submit_conversation_feedback
class PostConversationFeedbackRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation to provide feedback for.", examples=['21m00Tcm4TlvDq8ikWAM'])
class PostConversationFeedbackRouteRequestBody(StrictModel):
    feedback: Literal["like", "dislike"] | None = Field(default=None, description="The feedback sentiment for the conversation, either positive or negative.", examples=['like'])
class PostConversationFeedbackRouteRequest(StrictModel):
    """Submit feedback for a conversation to indicate user satisfaction. Feedback can be positive ('like') or negative ('dislike')."""
    path: PostConversationFeedbackRouteRequestPath
    body: PostConversationFeedbackRouteRequestBody | None = None

# Operation: search_conversation_messages
class TextSearchConversationMessagesRouteRequestQuery(StrictModel):
    text_query: str = Field(default=..., description="The search query text to match against conversation messages using full-text and fuzzy search algorithms.", examples=['refund policy'])
    agent_id: str | None = Field(default=None, description="Filter results to conversations handled by a specific agent.", examples=['21m00Tcm4TlvDq8ikWAM'])
    call_successful: Literal["success", "failure", "unknown"] | None = Field(default=None, description="Filter results by the outcome of the conversation (success, failure, or unknown).", examples=['success'])
    call_duration_min_secs: int | None = Field(default=None, description="Filter conversations with a minimum duration in seconds.")
    call_duration_max_secs: int | None = Field(default=None, description="Filter conversations with a maximum duration in seconds.")
    rating_max: int | None = Field(default=None, description="Filter conversations with a maximum overall rating on a scale of 1-5.", ge=1, le=5)
    rating_min: int | None = Field(default=None, description="Filter conversations with a minimum overall rating on a scale of 1-5.", ge=1, le=5)
    has_feedback_comment: bool | None = Field(default=None, description="Include only conversations that have user feedback comments.")
    user_id: str | None = Field(default=None, description="Filter conversations by the user ID who initiated them.")
    evaluation_params: list[str] | None = Field(default=None, description="Filter by evaluation criteria results. Specify as criteria_id:result pairs (repeatable parameter).")
    data_collection_params: list[str] | None = Field(default=None, description="Filter by data collection fields using comparison operators. Format: id:operator:value where operator is eq, neq, gt, gte, lt, lte, in, exists, or missing. Use pipe-delimited values for 'in' operator (repeatable parameter).")
    tool_names: list[str] | None = Field(default=None, description="Filter conversations by the names of tools used during the call (repeatable parameter).")
    main_languages: list[str] | None = Field(default=None, description="Filter conversations by detected primary language using language codes (repeatable parameter).")
    page_size: int | None = Field(default=None, description="Number of results to return per page.", ge=1, le=50)
    summary_mode: Literal["exclude", "include"] | None = Field(default=None, description="Include or exclude transcript summaries in the response.")
    conversation_initiation_source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, description="Filter conversations by their initiation source (SDK, integration, or communication platform).")
    branch_id: str | None = Field(default=None, description="Filter conversations by branch ID.")
class TextSearchConversationMessagesRouteRequest(StrictModel):
    """Search conversation transcripts using full-text and fuzzy matching with optional filtering by agent, user, call metrics, ratings, language, and other conversation attributes."""
    query: TextSearchConversationMessagesRouteRequestQuery

# Operation: search_conversation_messages_semantic
class SmartSearchConversationMessagesRouteRequestQuery(StrictModel):
    text_query: str = Field(default=..., description="The search query text to match against conversation messages using semantic similarity. Accepts natural language queries describing intent, topics, or specific requests.", examples=['Customer asking to cancel and get money back'])
    agent_id: str | None = Field(default=None, description="Filter results to messages from a specific agent. If omitted, searches across all agents in the conversation.", examples=['21m00Tcm4TlvDq8ikWAM'])
    page_size: int | None = Field(default=None, description="Number of results to return per page. Controls pagination size for large result sets.", ge=1, le=50)
class SmartSearchConversationMessagesRouteRequest(StrictModel):
    """Search conversation transcripts using semantic similarity to find relevant messages based on meaning and intent rather than exact keyword matches. Returns the most contextually relevant messages from conversation history."""
    query: SmartSearchConversationMessagesRouteRequestQuery

# Operation: import_phone_number
class CreatePhoneNumberRouteRequestBody(StrictModel):
    phone_number: str = Field(default=..., description="The phone number to import in E.164 format or provider-specific format.")
    label: str = Field(default=..., description="A descriptive label for this phone number to identify it in your system.")
    provider: Literal["twilio"] | None = Field(default=None, description="The telecommunications provider to import from. Defaults to Twilio if not specified.")
    sid: str | None = Field(default=None, description="Your Twilio Account SID for authentication. Required when provider is set to Twilio.")
    token: str | None = Field(default=None, description="Your Twilio Auth Token for authentication. Required when provider is set to Twilio.")
    region_config: RegionConfigRequest | None = Field(default=None, description="Additional Twilio region configuration settings to optimize call routing and compliance for specific geographic regions.")
    inbound_trunk_config: InboundSipTrunkConfigRequestModel | None = Field(default=None, description="SIP trunk configuration for inbound call routing, including server address, port, and authentication credentials.")
    outbound_trunk_config: OutboundSipTrunkConfigRequestModel | None = Field(default=None, description="SIP trunk configuration for outbound call routing, including server address, port, and authentication credentials.")
class CreatePhoneNumberRouteRequest(StrictModel):
    """Import a phone number from your provider configuration (Twilio or SIP trunk) to enable inbound and outbound calling capabilities."""
    body: CreatePhoneNumberRouteRequestBody

# Operation: get_phone_number
class GetPhoneNumberRouteRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier of the phone number to retrieve.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class GetPhoneNumberRouteRequest(StrictModel):
    """Retrieve details for a specific phone number by its ID. Returns the phone number configuration and associated metadata."""
    path: GetPhoneNumberRouteRequestPath

# Operation: update_phone_number
class UpdatePhoneNumberRouteRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier of the phone number to update.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class UpdatePhoneNumberRouteRequestBodyInboundTrunkConfigCredentials(StrictModel):
    username: str = Field(default=..., validation_alias="username", serialization_alias="username", description="Username credential for inbound SIP trunk authentication.")
class UpdatePhoneNumberRouteRequestBodyInboundTrunkConfig(StrictModel):
    allowed_addresses: list[str] | None = Field(default=None, validation_alias="allowed_addresses", serialization_alias="allowed_addresses", description="List of IP addresses or CIDR blocks permitted to use this trunk. Each entry can be a single IP address or a CIDR notation block.")
    allowed_numbers: list[str] | None = Field(default=None, validation_alias="allowed_numbers", serialization_alias="allowed_numbers", description="List of phone numbers authorized to use this trunk.")
    remote_domains: list[str] | None = Field(default=None, validation_alias="remote_domains", serialization_alias="remote_domains", description="List of remote SIP server domains used for validating TLS certificates during secure connections.")
    credentials: UpdatePhoneNumberRouteRequestBodyInboundTrunkConfigCredentials
class UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfigCredentials(StrictModel):
    username: str = Field(default=..., validation_alias="username", serialization_alias="username", description="Username credential for outbound SIP trunk authentication.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="Password credential for outbound SIP trunk authentication. If omitted, the existing password remains unchanged.")
class UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfig(StrictModel):
    media_encryption: Literal["disabled", "allowed", "required"] | None = Field(default=None, validation_alias="media_encryption", serialization_alias="media_encryption", description="Media encryption policy for outbound calls. Controls whether RTP traffic is encrypted.")
    address: str = Field(default=..., validation_alias="address", serialization_alias="address", description="Hostname or IP address where SIP INVITE requests are routed.")
    transport: Literal["auto", "udp", "tcp", "tls"] | None = Field(default=None, validation_alias="transport", serialization_alias="transport", description="SIP transport protocol for signaling. Auto-detection attempts to select the optimal protocol.")
    headers: dict[str, str] | None = Field(default=None, validation_alias="headers", serialization_alias="headers", description="Custom SIP X-* headers to include in INVITE requests. Useful for identifying calls or passing metadata to the SIP provider.")
    credentials: UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfigCredentials
class UpdatePhoneNumberRouteRequestBody(StrictModel):
    agent_id: str | None = Field(default=None, description="The ID of the agent to assign to this phone number for handling incoming calls.")
    label: str | None = Field(default=None, description="A human-readable label or name for this phone number.")
    livekit_stack: Literal["standard", "static"] | None = Field(default=None, description="LiveKit media server stack configuration for call handling.")
    inbound_trunk_config: UpdatePhoneNumberRouteRequestBodyInboundTrunkConfig
    outbound_trunk_config: UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfig
class UpdatePhoneNumberRouteRequest(StrictModel):
    """Update the routing configuration and credentials for a phone number, including assigned agent, SIP trunk settings, and security policies."""
    path: UpdatePhoneNumberRouteRequestPath
    body: UpdatePhoneNumberRouteRequestBody

# Operation: delete_phone_number
class DeletePhoneNumberRouteRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier of the phone number to delete.", examples=['TeaqRRdTcIfIu2i7BYfT'])
class DeletePhoneNumberRouteRequest(StrictModel):
    """Delete a phone number from your ConvAI account by its ID. This action is permanent and cannot be undone."""
    path: DeletePhoneNumberRouteRequestPath

# Operation: calculate_llm_expected_cost
class GetPublicLlmExpectedCostCalculationRequestBody(StrictModel):
    prompt_length: int = Field(default=..., description="The length of the input prompt in characters. This determines the token consumption for the initial request.")
    number_of_pages: int = Field(default=..., description="The total number of pages in PDF documents or URLs indexed in the agent's knowledge base. Used to estimate retrieval and processing costs when RAG is enabled.")
    rag_enabled: bool = Field(default=..., description="Whether Retrieval-Augmented Generation (RAG) is enabled. When enabled, the cost calculation includes knowledge base retrieval and context augmentation overhead.")
class GetPublicLlmExpectedCostCalculationRequest(StrictModel):
    """Calculate the expected cost of using various LLM models based on prompt length, knowledge base size, and RAG configuration. Returns a list of available models with their associated usage costs."""
    body: GetPublicLlmExpectedCostCalculationRequestBody

# Operation: upload_file
class UploadFileRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation to which the file will be uploaded.")
class UploadFileRouteRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The image or PDF file to upload. Supported formats include common image types (JPEG, PNG, etc.) and PDF documents.", json_schema_extra={'format': 'byte'})
class UploadFileRouteRequest(StrictModel):
    """Upload an image or PDF file to a conversation. Returns a unique file ID for referencing the file in subsequent conversation messages."""
    path: UploadFileRouteRequestPath
    body: UploadFileRouteRequestBody

# Operation: delete_conversation_file
class CancelFileUploadRouteRequestPath(StrictModel):
    conversation_id: str = Field(default=..., description="The unique identifier of the conversation containing the file to be deleted.")
    file_id: str = Field(default=..., description="The unique identifier of the file upload to be removed from the conversation.")
class CancelFileUploadRouteRequest(StrictModel):
    """Remove a file upload from a conversation. This operation is only available if the file has not yet been used within the conversation."""
    path: CancelFileUploadRouteRequestPath

# Operation: get_conversation_live_count
class GetLiveCountRequestQuery(StrictModel):
    agent_id: str | None = Field(default=None, description="Filter the live count to conversations handled by a specific agent. Omit to get the total count across all agents.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetLiveCountRequest(StrictModel):
    """Retrieve the current count of active ongoing conversations. Optionally filter results to a specific agent."""
    query: GetLiveCountRequestQuery | None = None

# Operation: get_knowledge_base_summaries
class GetAgentKnowledgeBaseSummariesRouteRequestQuery(StrictModel):
    document_ids: list[str] = Field(default=..., description="List of knowledge base document IDs to retrieve summaries for. IDs must be valid document identifiers from your knowledge base.", min_length=1, max_length=100, examples=[['21m00Tcm4TlvDq8ikWAM', '31n11Udm5UmwEr9jkXBN']])
class GetAgentKnowledgeBaseSummariesRouteRequest(StrictModel):
    """Retrieve summaries for multiple knowledge base documents by their IDs. Useful for quickly accessing document metadata and content previews without loading full documents."""
    query: GetAgentKnowledgeBaseSummariesRouteRequestQuery

# Operation: list_knowledge_bases
class GetKnowledgeBaseListRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of documents to return per page. Defaults to 30 documents.", ge=1, le=100)
    created_by_user_id: str | None = Field(default=None, description="Filter results to documents created by a specific user. Use '@me' to refer to the authenticated user. Takes precedence over ownership filters.")
    types: list[Literal["file", "url", "text", "folder"]] | None = Field(default=None, description="Filter results to only include documents of specified types. Provide as an array of type identifiers.")
    folders_first: bool | None = Field(default=None, description="Whether to display folder documents before other document types in the results.")
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Order direction for sorting results in ascending or descending sequence.")
    sort_by: Literal["name", "created_at", "updated_at", "size"] | None = Field(default=None, description="Field to sort results by. Choose from document name, creation date, last update date, or file size.")
class GetKnowledgeBaseListRouteRequest(StrictModel):
    """Retrieve a paginated list of available knowledge base documents with filtering and sorting options. Results can be filtered by creator, document type, and sorted by various fields."""
    query: GetKnowledgeBaseListRouteRequestQuery | None = None

# Operation: create_knowledge_base_document_from_url
class CreateUrlDocumentRouteRequestBody(StrictModel):
    url: str = Field(default=..., description="The complete URL of the webpage to scrape and add to the knowledge base. Must be a valid, publicly accessible web address.")
    name: str | None = Field(default=None, description="A human-readable label for this document within the knowledge base. Helps identify and organize the document for agent reference.", min_length=1)
class CreateUrlDocumentRouteRequest(StrictModel):
    """Create a knowledge base document by scraping and indexing content from a specified webpage. The agent will use this document to access and reference the webpage content when interacting with users."""
    body: CreateUrlDocumentRouteRequestBody

# Operation: upload_knowledge_base_document
class CreateFileDocumentRouteRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The file content to upload as a knowledge base document. Accepts binary file formats for documentation.", json_schema_extra={'format': 'byte'})
    name: str | None = Field(default=None, description="A human-readable name for the document. If not provided, a default name will be generated.", min_length=1)
class CreateFileDocumentRouteRequest(StrictModel):
    """Upload a file to create a new knowledge base document that the agent can access and reference when interacting with users."""
    body: CreateFileDocumentRouteRequestBody

# Operation: add_text_document
class CreateTextDocumentRouteRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content to be added to the knowledge base. This will be indexed for search and retrieval.")
    name: str | None = Field(default=None, description="A human-readable name for the document. If not provided, a default name will be generated.", min_length=1)
class CreateTextDocumentRouteRequest(StrictModel):
    """Add a text document to the knowledge base. The document will be indexed and made available for retrieval and analysis."""
    body: CreateTextDocumentRouteRequestBody

# Operation: create_folder
class CreateFolderRouteRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the folder. Used to identify and organize document groups within the knowledge base.", min_length=1)
class CreateFolderRouteRequest(StrictModel):
    """Create a new folder in the knowledge base for organizing and grouping related documents together."""
    body: CreateFolderRouteRequestBody

# Operation: retrieve_knowledge_base_document
class GetDocumentationFromKnowledgeBaseRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document to retrieve from the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetDocumentationFromKnowledgeBaseRequestQuery(StrictModel):
    agent_id: str | None = Field(default=None, description="Optional agent identifier to scope the knowledge base query to a specific agent.")
class GetDocumentationFromKnowledgeBaseRequest(StrictModel):
    """Retrieve detailed information about a specific document from the agent's knowledge base. Use the documentation ID returned when the document was added to access its content and metadata."""
    path: GetDocumentationFromKnowledgeBaseRequestPath
    query: GetDocumentationFromKnowledgeBaseRequestQuery | None = None

# Operation: rename_document
class UpdateDocumentRouteRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document to rename. This ID is provided when the document is initially added to the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
class UpdateDocumentRouteRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the document. Must be at least one character long.", min_length=1)
class UpdateDocumentRouteRequest(StrictModel):
    """Rename a document in the knowledge base by updating its display name."""
    path: UpdateDocumentRouteRequestPath
    body: UpdateDocumentRouteRequestBody

# Operation: delete_knowledge_base_document
class DeleteKnowledgeBaseDocumentRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document or folder to delete from the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteKnowledgeBaseDocumentRequestQuery(StrictModel):
    force: bool | None = Field(default=None, description="Force deletion of the document or folder even if it is currently used by agents. When enabled, the document will be removed from all dependent agents, and all child documents and folders within non-empty folders will also be deleted.")
class DeleteKnowledgeBaseDocumentRequest(StrictModel):
    """Permanently delete a document or folder from the knowledge base. Optionally force deletion even if the document is in use by agents, which will also remove it from dependent agents and delete all child documents in non-empty folders."""
    path: DeleteKnowledgeBaseDocumentRequestPath
    query: DeleteKnowledgeBaseDocumentRequestQuery | None = None

# Operation: batch_compute_rag_indexes
class GetOrCreateRagIndexesRequestBody(StrictModel):
    items: list[GetOrCreateRagIndexRequestModel] = Field(default=..., description="Array of RAG index requests for knowledge base documents. Each item specifies a document to index. Order is preserved in the response.", min_length=1, max_length=100)
class GetOrCreateRagIndexesRequest(StrictModel):
    """Computes and retrieves RAG (Retrieval-Augmented Generation) indexes for multiple knowledge base documents in a single batch operation. Supports up to 100 documents per request for efficient index creation and retrieval."""
    body: GetOrCreateRagIndexesRequestBody

# Operation: refresh_knowledge_base_document
class RefreshUrlDocumentRouteRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document in the knowledge base to refresh. This ID is provided when the document is initially added.", examples=['21m00Tcm4TlvDq8ikWAM'])
class RefreshUrlDocumentRouteRequest(StrictModel):
    """Manually refresh a URL-based document in the knowledge base by re-fetching its content from the source URL. Use this to update stale or outdated document content."""
    path: RefreshUrlDocumentRouteRequestPath

# Operation: list_rag_indexes
class GetRagIndexesRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the knowledge base document for which to retrieve RAG indexes.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetRagIndexesRequest(StrictModel):
    """Retrieve all RAG indexes associated with a specified knowledge base document. Returns metadata about each index configured for the document."""
    path: GetRagIndexesRequestPath

# Operation: index_knowledge_base_document
class RagIndexStatusRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document in the knowledge base that you want to index or check the indexing status for.", examples=['21m00Tcm4TlvDq8ikWAM'])
class RagIndexStatusRequestBody(StrictModel):
    model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] = Field(default=..., description="The embedding model to use for RAG indexing. This determines how the document content will be vectorized for semantic search.")
class RagIndexStatusRequest(StrictModel):
    """Trigger or retrieve the RAG indexing status for a knowledge base document. If the document hasn't been indexed yet, this operation initiates the indexing task; otherwise, it returns the current indexing status."""
    path: RagIndexStatusRequestPath
    body: RagIndexStatusRequestBody

# Operation: delete_rag_index
class DeleteRagIndexRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the knowledge base document whose RAG index will be deleted.", examples=['21m00Tcm4TlvDq8ikWAM'])
    rag_index_id: str = Field(default=..., description="The unique identifier of the RAG index to delete for the specified document.", examples=['21m00Tcm4TlvDq8ikWAM'])
class DeleteRagIndexRequest(StrictModel):
    """Delete a RAG index associated with a knowledge base document. This removes the indexed data used for retrieval-augmented generation on that document."""
    path: DeleteRagIndexRequestPath

# Operation: list_dependent_agents
class GetKnowledgeBaseDependentAgentsRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the knowledge base document for which to retrieve dependent agents.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetKnowledgeBaseDependentAgentsRequestQuery(StrictModel):
    dependent_type: Literal["direct", "transitive", "all"] | None = Field(default=None, description="Filter results by dependency relationship type. Use 'direct' for agents directly referencing this document, 'transitive' for agents indirectly depending on it, or 'all' to include both.")
    page_size: int | None = Field(default=None, description="Maximum number of agents to return per request. Must be between 1 and 100.", ge=1, le=100)
class GetKnowledgeBaseDependentAgentsRequest(StrictModel):
    """Retrieve a list of agents that depend on a specific knowledge base document. Supports filtering by dependency type (direct, transitive, or all) with pagination."""
    path: GetKnowledgeBaseDependentAgentsRequestPath
    query: GetKnowledgeBaseDependentAgentsRequestQuery | None = None

# Operation: retrieve_knowledge_base_document_content
class GetKnowledgeBaseContentRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document in the knowledge base, provided when the document was initially added.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetKnowledgeBaseContentRequest(StrictModel):
    """Retrieve the complete content of a document stored in the knowledge base. Use the documentation ID returned when the document was added to access its full text."""
    path: GetKnowledgeBaseContentRequestPath

# Operation: get_knowledge_base_source_file_url
class GetKnowledgeBaseSourceFileUrlRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the knowledge base document. This ID is provided when the document is initially added to the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
class GetKnowledgeBaseSourceFileUrlRequest(StrictModel):
    """Retrieve a signed URL to download the original source file of a document stored in the knowledge base. The URL is temporary and can be used to access the file directly."""
    path: GetKnowledgeBaseSourceFileUrlRequestPath

# Operation: retrieve_knowledge_base_chunk
class GetDocumentationChunkFromKnowledgeBaseRequestPath(StrictModel):
    documentation_id: str = Field(default=..., description="The unique identifier of the document in the knowledge base. This ID is provided when the document is initially added to the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
    chunk_id: str = Field(default=..., description="The unique identifier of the specific chunk within the document. Chunks are sequential segments of a document created during RAG processing.", examples=[1])
class GetDocumentationChunkFromKnowledgeBaseRequestQuery(StrictModel):
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = Field(default=None, description="The embedding model used to generate and retrieve the chunk. Determines the vector representation used for semantic search and retrieval.", examples=['e5_mistral_7b_instruct'])
class GetDocumentationChunkFromKnowledgeBaseRequest(StrictModel):
    """Retrieve a specific chunk from a knowledge base document used by the RAG system. Returns the chunk content and metadata for the specified documentation and chunk identifiers."""
    path: GetDocumentationChunkFromKnowledgeBaseRequestPath
    query: GetDocumentationChunkFromKnowledgeBaseRequestQuery | None = None

# Operation: move_knowledge_base_document
class PostKnowledgeBaseMoveRouteRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to move within the knowledge base.", examples=['21m00Tcm4TlvDq8ikWAM'])
class PostKnowledgeBaseMoveRouteRequestBody(StrictModel):
    move_to: str | None = Field(default=None, description="The destination folder identifier where the document should be moved. Omit this parameter to move the document to the root folder.")
class PostKnowledgeBaseMoveRouteRequest(StrictModel):
    """Moves a knowledge base document from its current location to a specified folder. If no destination folder is provided, the document is moved to the root folder."""
    path: PostKnowledgeBaseMoveRouteRequestPath
    body: PostKnowledgeBaseMoveRouteRequestBody | None = None

# Operation: move_knowledge_base_entities
class PostKnowledgeBaseBulkMoveRouteRequestBody(StrictModel):
    document_ids: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(default=..., description="The IDs of the documents or folders to move. Accepts between 1 and 20 entity IDs in a single operation.", min_length=1, max_length=20, examples=[['21m00Tcm4TlvDq8ikWAM', '31m00Tcm4TlvDq8ikWBM']])
    move_to: str | None = Field(default=None, description="The destination folder ID where entities will be moved. Omit this parameter to move entities to the root folder.")
class PostKnowledgeBaseBulkMoveRouteRequest(StrictModel):
    """Moves multiple documents or folders within a knowledge base to a specified destination folder. If no destination is provided, entities are moved to the root folder."""
    body: PostKnowledgeBaseBulkMoveRouteRequestBody

# Operation: list_tools
class GetToolsRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of tools to return per request. Must be between 1 and 100.", ge=1, le=100)
    created_by_user_id: str | None = Field(default=None, description="Filter results to tools created by a specific user. Use '@me' to refer to the authenticated user. Takes precedence over ownership filters.")
    types: list[Literal["webhook", "client", "api_integration_webhook"]] | None = Field(default=None, description="Filter results to include only tools of specified types. Provide as an array of tool type values.")
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Order direction for sorting results in ascending or descending sequence.")
    sort_by: Literal["name", "created_at"] | None = Field(default=None, description="Field to sort results by. Choose between tool name or creation timestamp.")
class GetToolsRouteRequest(StrictModel):
    """Retrieve all available tools in the workspace with optional filtering by creator, type, and sorting capabilities."""
    query: GetToolsRouteRequestQuery | None = None

# Operation: create_tool
class AddToolRouteRequestBody(StrictModel):
    tool_config: WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput = Field(default=..., description="The tool configuration object that defines the tool's metadata, input parameters, and behavior. This should include the tool name, description, parameter schema, and any other required configuration properties.")
class AddToolRouteRequest(StrictModel):
    """Register a new tool in the workspace to make it available for use in conversations. The tool configuration defines its name, description, parameters, and execution behavior."""
    body: AddToolRouteRequestBody

# Operation: get_tool
class GetToolRouteRequestPath(StrictModel):
    tool_id: str = Field(default=..., description="The unique identifier of the tool to retrieve.")
class GetToolRouteRequest(StrictModel):
    """Retrieve a specific tool available in the workspace by its ID. Use this to fetch tool details and configuration."""
    path: GetToolRouteRequestPath

# Operation: update_tool
class UpdateToolRouteRequestPath(StrictModel):
    tool_id: str = Field(default=..., description="The unique identifier of the tool to be updated.")
class UpdateToolRouteRequestBody(StrictModel):
    tool_config: WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput = Field(default=..., description="The configuration object containing the tool's settings and parameters to be updated.")
class UpdateToolRouteRequest(StrictModel):
    """Update the configuration of an existing tool in the workspace. Modify tool settings and behavior by providing updated configuration parameters."""
    path: UpdateToolRouteRequestPath
    body: UpdateToolRouteRequestBody

# Operation: delete_tool
class DeleteToolRouteRequestPath(StrictModel):
    tool_id: str = Field(default=..., description="The unique identifier of the tool to delete.")
class DeleteToolRouteRequestQuery(StrictModel):
    force: bool | None = Field(default=None, description="Force deletion of the tool even if it is currently used by agents or branches. When enabled, the tool will be automatically removed from all dependent agents and branches.")
class DeleteToolRouteRequest(StrictModel):
    """Delete a tool from the workspace. Optionally force deletion to remove the tool from all dependent agents and branches regardless of current usage."""
    path: DeleteToolRouteRequestPath
    query: DeleteToolRouteRequestQuery | None = None

# Operation: list_dependent_agents_tool
class GetToolDependentAgentsRouteRequestPath(StrictModel):
    tool_id: str = Field(default=..., description="The unique identifier of the tool for which to retrieve dependent agents.")
class GetToolDependentAgentsRouteRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of agents to return per request. Useful for pagination control.", ge=1, le=100)
class GetToolDependentAgentsRouteRequest(StrictModel):
    """Retrieve a paginated list of agents that depend on a specific tool. Use this to understand tool usage and impact across your agent ecosystem."""
    path: GetToolDependentAgentsRouteRequestPath
    query: GetToolDependentAgentsRouteRequestQuery | None = None

# Operation: create_workspace_secret
class CreateSecretRouteRequestBody(StrictModel):
    type_: Literal["new"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The category or classification of the secret (e.g., API key, password, token, connection string). Determines how the secret is handled and validated.")
    name: str = Field(default=..., description="A unique identifier for the secret within the workspace. Used to reference the secret in configurations and workflows.")
    value: str = Field(default=..., description="The sensitive value to be securely stored. This value is encrypted and not returned in subsequent API responses.")
class CreateSecretRouteRequest(StrictModel):
    """Create a new secret for the Convai workspace. Secrets are securely stored credentials or sensitive values that can be referenced in workspace configurations."""
    body: CreateSecretRouteRequestBody

# Operation: update_secret
class UpdateSecretRouteRequestPath(StrictModel):
    secret_id: str = Field(default=..., description="The unique identifier of the secret to update.")
class UpdateSecretRouteRequestBody(StrictModel):
    type_: Literal["update"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type or category of the secret (e.g., API key, password, token).")
    name: str = Field(default=..., description="The display name or label for the secret.")
    value: str = Field(default=..., description="The secret value or credential data to store.")
class UpdateSecretRouteRequest(StrictModel):
    """Update an existing secret in the Convai workspace. Modify the secret's type, name, or value by providing the secret ID and updated details."""
    path: UpdateSecretRouteRequestPath
    body: UpdateSecretRouteRequestBody

# Operation: delete_secret
class DeleteSecretRouteRequestPath(StrictModel):
    secret_id: str = Field(default=..., description="The unique identifier of the secret to delete.")
class DeleteSecretRouteRequest(StrictModel):
    """Delete a workspace secret. The secret must not be in use by any active configurations before deletion."""
    path: DeleteSecretRouteRequestPath

# Operation: submit_batch_calls
class CreateBatchCallRequestBodyWhatsappParams(StrictModel):
    whatsapp_call_permission_request_template_name: str = Field(default=..., validation_alias="whatsapp_call_permission_request_template_name", serialization_alias="whatsapp_call_permission_request_template_name", description="Name of the WhatsApp message template to use for requesting call permissions from recipients.")
    whatsapp_call_permission_request_template_language_code: str = Field(default=..., validation_alias="whatsapp_call_permission_request_template_language_code", serialization_alias="whatsapp_call_permission_request_template_language_code", description="Language code for the WhatsApp permission request template (e.g., en, es, fr). Must match a supported language for the specified template.")
class CreateBatchCallRequestBody(StrictModel):
    call_name: str = Field(default=..., description="Display name or identifier for this batch call campaign.")
    agent_id: str = Field(default=..., description="Unique identifier of the conversational AI agent to use for the calls.")
    recipients: list[OutboundCallRecipient] = Field(default=..., description="List of recipient phone numbers or contact identifiers to call. Order is preserved for sequential processing.", max_length=10000)
    scheduled_time_unix: int | None = Field(default=None, description="Unix timestamp (seconds since epoch) for when to start executing the batch calls. If omitted, calls begin immediately.")
    agent_phone_number_id: str | None = Field(default=None, description="Phone number identifier associated with the agent making the calls. Required for certain call routing configurations.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Timezone identifier (e.g., America/New_York, Europe/London) for interpreting scheduled_time_unix in local context.")
    target_concurrency_limit: int | None = Field(default=None, description="Maximum number of simultaneous calls allowed in this batch. When set, this limit takes precedence over workspace or agent-level capacity settings.", ge=1)
    whatsapp_params: CreateBatchCallRequestBodyWhatsappParams
class CreateBatchCallRequest(StrictModel):
    """Submit a batch call request to schedule multiple outbound calls to recipients. Supports scheduling, concurrency limits, and WhatsApp permission request templates."""
    body: CreateBatchCallRequestBody

# Operation: list_batch_calls
class GetWorkspaceBatchCallsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of batch calls to return per request. Controls pagination size for the result set.")
    last_doc: str | None = Field(default=None, description="Cursor token for pagination. Provide the last document identifier from a previous request to retrieve the next page of results.")
class GetWorkspaceBatchCallsRequest(StrictModel):
    """Retrieve all batch calls for the current workspace with pagination support. Use limit and last_doc parameters to control result set size and navigate through pages."""
    query: GetWorkspaceBatchCallsRequestQuery | None = None

# Operation: get_batch_call
class GetBatchCallRequestPath(StrictModel):
    batch_id: str = Field(default=..., description="The unique identifier of the batch call to retrieve.")
class GetBatchCallRequest(StrictModel):
    """Retrieve detailed information about a specific batch call, including all recipients and their call status."""
    path: GetBatchCallRequestPath

# Operation: delete_batch_call
class DeleteBatchCallRequestPath(StrictModel):
    batch_id: str = Field(default=..., description="The unique identifier of the batch call to delete.")
class DeleteBatchCallRequest(StrictModel):
    """Permanently delete a batch call and all associated recipient records. Note that conversation history will be retained even after deletion."""
    path: DeleteBatchCallRequestPath

# Operation: cancel_batch_call
class CancelBatchCallRequestPath(StrictModel):
    batch_id: str = Field(default=..., description="The unique identifier of the batch call to cancel.")
class CancelBatchCallRequest(StrictModel):
    """Cancel a running batch call and set all recipients to cancelled status. This operation terminates the batch calling process immediately."""
    path: CancelBatchCallRequestPath

# Operation: retry_batch_call
class RetryBatchCallRequestPath(StrictModel):
    batch_id: str = Field(default=..., description="The unique identifier of the batch call to retry. This specifies which batch's failed and no-response recipients should be called again.")
class RetryBatchCallRequest(StrictModel):
    """Retry a failed batch call by re-attempting to reach recipients who did not respond or experienced call failures. This operation allows you to reprocess a specific batch without creating a new batch call."""
    path: RetryBatchCallRequestPath

# Operation: initiate_outbound_sip_call
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(StrictModel):
    soft_timeout_config: dict[str, Any] | None = Field(default=None, validation_alias="soft_timeout_config", serialization_alias="soft_timeout_config", description="Configuration for soft timeout feedback, allowing the agent to provide immediate responses (e.g., acknowledgments) while processing longer LLM responses.")
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(StrictModel):
    voice_id: str | None = Field(default=None, validation_alias="voice_id", serialization_alias="voice_id", description="The voice ID to use for text-to-speech synthesis. Determines the voice characteristics of the agent's spoken responses.")
    stability: float | None = Field(default=None, validation_alias="stability", serialization_alias="stability", description="Controls the consistency of the generated speech, ranging from low variability to high variability in tone and delivery.")
    speed: float | None = Field(default=None, validation_alias="speed", serialization_alias="speed", description="Controls the speed of the generated speech, where lower values slow down speech and higher values speed it up.")
    similarity_boost: float | None = Field(default=None, validation_alias="similarity_boost", serialization_alias="similarity_boost", description="Controls how closely the generated speech matches the selected voice ID, balancing between voice similarity and speech quality.")
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(StrictModel):
    first_message: str | None = Field(default=None, validation_alias="first_message", serialization_alias="first_message", description="The initial message the agent will speak when the call connects. If empty, the agent waits for the caller to speak first.")
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="The language code for the agent's automatic speech recognition (ASR) and text-to-speech (TTS) processing.")
    prompt: dict[str, Any] | None = Field(default=None, validation_alias="prompt", serialization_alias="prompt", description="Configuration for the LLM behavior, including the model selection and system prompt that defines the agent's personality and capabilities.")
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(StrictModel):
    turn: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn | None = None
    tts: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts | None = None
    agent: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent | None = None
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(StrictModel):
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(default=None, validation_alias="source", serialization_alias="source", description="The source or channel through which the call was initiated, used for analytics and tracking purposes.")
class HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientData(StrictModel):
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="Identifier for the end user or customer participating in this call, used by the agent owner for tracking and user identification.")
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(default=None, validation_alias="dynamic_variables", serialization_alias="dynamic_variables", description="Custom variables that can be passed to the agent and used within the prompt or conversation context for dynamic behavior.")
    conversation_config_override: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride | None = None
    source_info: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataSourceInfo | None = None
class HandleSipTrunkOutboundCallRequestBody(StrictModel):
    agent_id: str = Field(default=..., description="Unique identifier of the AI agent that will handle the outbound call.")
    agent_phone_number_id: str = Field(default=..., description="Unique identifier of the phone number resource associated with the agent for this call.")
    to_number: str = Field(default=..., description="The destination phone number to call in E.164 format or standard phone number format.")
    conversation_initiation_client_data: HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientData | None = None
class HandleSipTrunkOutboundCallRequest(StrictModel):
    """Initiates an outbound call through a SIP trunk with an AI agent. The agent can be configured with custom voice settings, initial messaging, and LLM behavior to handle the conversation."""
    body: HandleSipTrunkOutboundCallRequestBody

# Operation: register_mcp_server
class CreateMcpServerRouteRequestBodyConfig(StrictModel):
    approval_policy: Literal["auto_approve_all", "require_approval_all", "require_approval_per_tool"] | None = Field(default=None, validation_alias="approval_policy", serialization_alias="approval_policy", description="Approval policy that determines whether tools from this server require manual approval before execution. Choose 'auto_approve_all' to execute immediately, 'require_approval_all' to require approval for every tool call, or 'require_approval_per_tool' to configure approval on a per-tool basis.")
    tool_approval_hashes: list[McpToolApprovalHash] | None = Field(default=None, validation_alias="tool_approval_hashes", serialization_alias="tool_approval_hashes", description="List of tool approval hashes that are pre-approved for execution. Only used when approval_policy is set to 'require_approval_per_tool'. Each hash corresponds to a specific tool that should skip approval.")
    transport: Literal["SSE", "STREAMABLE_HTTP"] | None = Field(default=None, validation_alias="transport", serialization_alias="transport", description="Communication protocol used to connect to the MCP server. SSE (Server-Sent Events) is the default for real-time streaming, while STREAMABLE_HTTP is an alternative transport option.")
    url: str | ConvAiSecretLocator = Field(default=..., validation_alias="url", serialization_alias="url", description="The HTTPS endpoint URL where the MCP server is hosted. If the URL contains sensitive credentials, store it as a workspace secret reference instead of a plain string.")
    secret_token: ConvAiSecretLocator | ConvAiUserSecretDbModel | None = Field(default=None, validation_alias="secret_token", serialization_alias="secret_token", description="Authorization token sent in the request header to authenticate with the MCP server. Store sensitive tokens as workspace secrets rather than plain text.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(default=None, validation_alias="request_headers", serialization_alias="request_headers", description="Custom HTTP headers to include in all requests to the MCP server. Useful for passing additional authentication credentials or metadata required by the server.")
    auth_connection: AuthConnectionLocator | EnvironmentAuthConnectionLocator | None = Field(default=None, validation_alias="auth_connection", serialization_alias="auth_connection", description="Reference to a pre-configured authentication connection in your workspace. Use this to leverage existing auth credentials instead of providing token or headers directly.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="Display name for this MCP server configuration. Used to identify the server in your workspace and in agent logs.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional description explaining the purpose and capabilities of this MCP server.")
    force_pre_tool_speech: bool | None = Field(default=None, validation_alias="force_pre_tool_speech", serialization_alias="force_pre_tool_speech", description="If enabled, the agent will speak before executing any tool from this server, allowing the user to hear what action is about to be taken.")
    disable_interruptions: bool | None = Field(default=None, validation_alias="disable_interruptions", serialization_alias="disable_interruptions", description="If enabled, users cannot interrupt the agent while any tool from this server is executing. Useful for critical operations that must complete without interruption.")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(default=None, validation_alias="tool_call_sound", serialization_alias="tool_call_sound", description="Predefined sound effect to play when tools from this server begin execution. Helps provide audio feedback during tool execution.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(default=None, validation_alias="tool_call_sound_behavior", serialization_alias="tool_call_sound_behavior", description="Controls when the tool call sound plays: 'auto' plays the sound only when appropriate, 'always' plays it every time a tool executes.")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(default=None, validation_alias="execution_mode", serialization_alias="execution_mode", description="Execution timing for tools from this server: 'immediate' runs the tool right away, 'post_tool_speech' waits for the agent to finish speaking first, 'async' runs in the background without blocking the agent.")
    tool_config_overrides: list[McpToolConfigOverride] | None = Field(default=None, validation_alias="tool_config_overrides", serialization_alias="tool_config_overrides", description="List of per-tool configuration overrides that customize behavior for specific tools, superseding the server-level defaults. Each override targets a tool by identifier and applies custom settings.")
    disable_compression: bool | None = Field(default=None, validation_alias="disable_compression", serialization_alias="disable_compression", description="If enabled, HTTP compression is disabled for requests to this MCP server. Enable this only if the server does not properly support compressed responses.")
class CreateMcpServerRouteRequestBody(StrictModel):
    config: CreateMcpServerRouteRequestBodyConfig
class CreateMcpServerRouteRequest(StrictModel):
    """Register a new MCP (Model Context Protocol) server in your workspace to enable tool execution through that server. Configure authentication, approval policies, and execution behavior for all tools provided by this server."""
    body: CreateMcpServerRouteRequestBody

# Operation: get_mcp_server
class GetMcpRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server to retrieve.")
class GetMcpRouteRequest(StrictModel):
    """Retrieve a specific MCP server configuration from your workspace. Use this to access detailed settings and metadata for a configured MCP server."""
    path: GetMcpRouteRequestPath

# Operation: configure_mcp_server
class UpdateMcpServerConfigRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server to configure.")
class UpdateMcpServerConfigRouteRequestBodySecretToken(StrictModel):
    secret_id: str = Field(default=..., validation_alias="secret_id", serialization_alias="secret_id", description="The secret identifier for credentials or API keys used to authenticate with this MCP server.")
class UpdateMcpServerConfigRouteRequestBody(StrictModel):
    approval_policy: Literal["auto_approve_all", "require_approval_all", "require_approval_per_tool"] | None = Field(default=None, description="The approval workflow mode for tool execution from this server. Controls whether tools require manual approval before execution.")
    force_pre_tool_speech: bool | None = Field(default=None, description="When enabled, forces the system to speak tool descriptions aloud before execution, overriding the server's default setting.")
    disable_interruptions: bool | None = Field(default=None, description="When enabled, prevents user interruptions during tool execution, overriding the server's default setting.")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(default=None, description="The sound effect to play during tool execution for all tools from this server.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(default=None, description="Controls when the tool call sound plays during execution.")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(default=None, description="Determines the execution timing for tools from this server. Immediate executes right away, post_tool_speech waits for narration, and async runs in the background.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(default=None, description="HTTP headers to include in all requests sent to this MCP server, such as custom authentication or tracking headers.")
    disable_compression: bool | None = Field(default=None, description="When enabled, disables HTTP compression for requests to this MCP server to reduce processing overhead.")
    auth_connection: AuthConnectionLocator | EnvironmentAuthConnectionLocator | None = Field(default=None, description="Optional authentication connection configuration for establishing secure communication with this MCP server.")
    secret_token: UpdateMcpServerConfigRouteRequestBodySecretToken
class UpdateMcpServerConfigRouteRequest(StrictModel):
    """Update configuration settings for an MCP server, including approval policies, audio behavior, execution modes, and authentication. Changes apply to all tools provided by this server."""
    path: UpdateMcpServerConfigRouteRequestPath
    body: UpdateMcpServerConfigRouteRequestBody

# Operation: delete_mcp_server
class DeleteMcpServerRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server to delete.")
class DeleteMcpServerRouteRequest(StrictModel):
    """Remove a specific MCP server configuration from the workspace. This action permanently deletes the server and its associated settings."""
    path: DeleteMcpServerRouteRequestPath

# Operation: list_mcp_server_tools
class ListMcpServerToolsRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server for which to retrieve available tools.")
class ListMcpServerToolsRouteRequest(StrictModel):
    """Retrieve all tools available for a specific MCP server configuration. Returns a complete list of tools that can be invoked through the specified MCP server."""
    path: ListMcpServerToolsRouteRequestPath

# Operation: approve_mcp_server_tool
class AddMcpServerToolApprovalRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP Server to which the tool approval applies.")
class AddMcpServerToolApprovalRouteRequestBody(StrictModel):
    tool_name: str = Field(default=..., description="The name of the MCP tool being approved for use.")
    tool_description: str = Field(default=..., description="A human-readable description of what the MCP tool does and its purpose.")
    input_schema: dict[str, Any] | None = Field(default=None, description="The input schema that defines the parameters and structure expected by the MCP tool, as defined on the MCP server before any ElevenLabs processing.")
    approval_policy: Literal["auto_approved", "requires_approval"] | None = Field(default=None, description="The approval policy that determines whether this tool requires explicit approval before each use or is automatically approved.")
class AddMcpServerToolApprovalRouteRequest(StrictModel):
    """Grant approval for a specific MCP tool when the server is configured to use per-tool approval mode. This enables fine-grained control over which tools are available for use."""
    path: AddMcpServerToolApprovalRouteRequestPath
    body: AddMcpServerToolApprovalRouteRequestBody

# Operation: revoke_mcp_server_tool_approval
class RemoveMcpServerToolApprovalRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP Server from which to revoke tool approval.")
    tool_name: str = Field(default=..., description="The name of the MCP tool to revoke approval for.")
class RemoveMcpServerToolApprovalRouteRequest(StrictModel):
    """Revoke approval for a specific MCP tool on a server when using per-tool approval mode. This removes the tool from the approved list, preventing its use until re-approved."""
    path: RemoveMcpServerToolApprovalRouteRequestPath

# Operation: create_tool_config_override
class AddMcpToolConfigOverrideRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server containing the tool to configure.")
class AddMcpToolConfigOverrideRouteRequestBody(StrictModel):
    force_pre_tool_speech: bool | None = Field(default=None, description="When enabled, forces the system to speak a message before executing this tool, overriding the server's default setting.")
    disable_interruptions: bool | None = Field(default=None, description="When enabled, prevents user interruptions during this tool's execution, overriding the server's default setting.")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(default=None, description="The sound effect to play when this tool is invoked, overriding the server's default sound setting.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(default=None, description="Controls when the tool call sound plays: automatically based on context or always when the tool executes.")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(default=None, description="Determines when this tool executes relative to speech output: immediately, after tool speech completes, or asynchronously.")
    assignments: list[DynamicVariableAssignment] | None = Field(default=None, description="Dynamic variable assignments that will be available to this MCP tool during execution. Order is preserved as specified.")
    input_overrides: dict[str, ConstantSchemaOverride | DynamicVariableSchemaOverride | LlmSchemaOverride] | None = Field(default=None, description="JSON path mappings to override specific input parameters for this tool, allowing selective input transformation or substitution.")
    tool_name: str = Field(default=..., description="The exact name of the MCP tool within the server to apply these configuration overrides to.")
class AddMcpToolConfigOverrideRouteRequest(StrictModel):
    """Create configuration overrides for a specific MCP tool, allowing fine-grained control over tool execution behavior, audio feedback, and input handling independent of server-level settings."""
    path: AddMcpToolConfigOverrideRouteRequestPath
    body: AddMcpToolConfigOverrideRouteRequestBody

# Operation: get_tool_config_override
class GetMcpToolConfigOverrideRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server containing the tool.")
    tool_name: str = Field(default=..., description="The name of the MCP tool for which to retrieve configuration overrides.")
class GetMcpToolConfigOverrideRouteRequest(StrictModel):
    """Retrieve configuration overrides for a specific MCP tool within an MCP server. Use this to fetch customized tool settings that differ from default configurations."""
    path: GetMcpToolConfigOverrideRouteRequestPath

# Operation: override_mcp_tool_config
class UpdateMcpToolConfigOverrideRouteRequestPath(StrictModel):
    mcp_server_id: str = Field(default=..., description="The unique identifier of the MCP server containing the tool to configure.")
    tool_name: str = Field(default=..., description="The name of the MCP tool whose configuration overrides should be updated.")
class UpdateMcpToolConfigOverrideRouteRequestBody(StrictModel):
    force_pre_tool_speech: bool | None = Field(default=None, description="Force the system to speak before executing this tool, overriding the server's default setting.")
    disable_interruptions: bool | None = Field(default=None, description="Prevent user interruptions during this tool's execution, overriding the server's default setting.")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(default=None, description="The sound to play when this tool is invoked, overriding the server's default sound.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(default=None, description="Control when the tool call sound plays: automatically based on context or always when the tool executes.")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(default=None, description="Specify when this tool executes: immediately, after speech completes, or asynchronously.")
    assignments: list[DynamicVariableAssignment] | None = Field(default=None, description="Dynamic variable assignments to pass to this MCP tool during execution. Order is preserved if significant for the tool's logic.")
    input_overrides: dict[str, ConstantSchemaOverride | DynamicVariableSchemaOverride | LlmSchemaOverride] | None = Field(default=None, description="JSON path mappings that override specific input fields for this tool, allowing selective parameter customization.")
class UpdateMcpToolConfigOverrideRouteRequest(StrictModel):
    """Override configuration settings for a specific MCP tool, allowing fine-grained control over behavior like speech timing, interruptions, and execution mode independent of server-level defaults."""
    path: UpdateMcpToolConfigOverrideRouteRequestPath
    body: UpdateMcpToolConfigOverrideRouteRequestBody | None = None

# Operation: get_whatsapp_account
class GetWhatsappAccountRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier for the WhatsApp phone number associated with the account.")
class GetWhatsappAccountRequest(StrictModel):
    """Retrieve details for a specific WhatsApp account using its phone number ID. Returns account configuration and status information."""
    path: GetWhatsappAccountRequestPath

# Operation: update_whatsapp_account
class UpdateWhatsappAccountRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier for the WhatsApp phone number account to update.")
class UpdateWhatsappAccountRequestBody(StrictModel):
    assigned_agent_id: str | None = Field(default=None, description="The ID of the agent to assign to this WhatsApp account for handling conversations.")
    enable_messaging: bool | None = Field(default=None, description="Enable or disable messaging functionality for this WhatsApp account.")
    enable_audio_message_response: bool | None = Field(default=None, description="Enable or disable automatic audio message response capability for this WhatsApp account.")
class UpdateWhatsappAccountRequest(StrictModel):
    """Update configuration settings for a WhatsApp account, including agent assignment and messaging capabilities. Changes take effect immediately."""
    path: UpdateWhatsappAccountRequestPath
    body: UpdateWhatsappAccountRequestBody | None = None

# Operation: delete_whatsapp_account
class DeleteWhatsappAccountRequestPath(StrictModel):
    phone_number_id: str = Field(default=..., description="The unique identifier for the WhatsApp phone number account to delete.")
class DeleteWhatsappAccountRequest(StrictModel):
    """Permanently delete a WhatsApp account and remove it from the ConvAI platform. This action cannot be undone."""
    path: DeleteWhatsappAccountRequestPath

# Operation: list_agent_branches
class GetBranchesRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose branches should be retrieved.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class GetBranchesRouteRequestQuery(StrictModel):
    include_archived: bool | None = Field(default=None, description="Whether to include archived branches in the results. Defaults to excluding archived branches.")
    limit: int | None = Field(default=None, description="Maximum number of branches to return in the response. Must be between 2 and 100 inclusive.", le=100, gt=1)
class GetBranchesRouteRequest(StrictModel):
    """Retrieves a list of branches for a specified agent. Optionally includes archived branches and supports result limiting."""
    path: GetBranchesRouteRequestPath
    query: GetBranchesRouteRequestQuery | None = None

# Operation: create_agent_branch
class CreateBranchRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent to create a branch for.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class CreateBranchRouteRequestBodyWorkflow(StrictModel):
    edges: dict[str, WorkflowEdgeModelInput] | None = Field(default=None, validation_alias="edges", serialization_alias="edges", description="Optional edge definitions for the agent's conversation flow in this branch.")
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(default=None, validation_alias="nodes", serialization_alias="nodes", description="Optional node definitions for the agent's conversation flow in this branch.", min_length=1)
class CreateBranchRouteRequestBody(StrictModel):
    parent_version_id: str = Field(default=..., description="The version ID of the main branch to use as the base for this new branch.")
    name: str = Field(default=..., description="The name of the new branch. Must be unique within the agent and cannot exceed 140 characters.", max_length=140)
    description: str = Field(default=..., description="A description of the branch's purpose or contents. Cannot exceed 4096 characters.", max_length=4096)
    conversation_config: dict[str, Any] | None = Field(default=None, description="Optional configuration changes to apply to conversation settings for this branch.")
    platform_settings: dict[str, Any] | None = Field(default=None, description="Optional platform-specific settings changes to apply to this branch.")
    workflow: CreateBranchRouteRequestBodyWorkflow | None = None
class CreateBranchRouteRequest(StrictModel):
    """Create a new branch from a specified version of an agent's main branch. Branches allow you to develop and test agent configurations independently before merging changes back to the main branch."""
    path: CreateBranchRouteRequestPath
    body: CreateBranchRouteRequestBody

# Operation: get_agent_branch
class GetBranchRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent that contains the branch.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
    branch_id: str = Field(default=..., description="The unique identifier of the branch to retrieve.", examples=['agtbranch_0901k4aafjxxfxt93gd841r7tv5t'])
class GetBranchRouteRequest(StrictModel):
    """Retrieve detailed information about a specific agent branch, including its configuration and settings."""
    path: GetBranchRouteRequestPath

# Operation: update_branch
class UpdateBranchRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent that owns the branch.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
    branch_id: str = Field(default=..., description="The unique identifier of the branch to update.", examples=['agtbranch_0901k4aafjxxfxt93gd841r7tv5t'])
class UpdateBranchRouteRequestBody(StrictModel):
    name: str | None = Field(default=None, description="New name for the branch. Must be unique within the agent.", min_length=1, max_length=140)
    is_archived: bool | None = Field(default=None, description="Whether to archive the branch. Archived branches are hidden from normal operations but retain their data.")
    protection_status: Literal["writer_perms_required", "admin_perms_required"] | None = Field(default=None, description="The access control level required to modify the branch.")
class UpdateBranchRouteRequest(StrictModel):
    """Update agent branch properties including name, archival status, and access control permissions. Allows modification of branch configuration and protection levels."""
    path: UpdateBranchRouteRequestPath
    body: UpdateBranchRouteRequestBody | None = None

# Operation: merge_branch
class MergeBranchIntoTargetRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent containing the branches to merge.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
    source_branch_id: str = Field(default=..., description="The unique identifier of the source branch to merge from.", examples=['agtbrch_8901k4t9z5defmb8vh3e9361y7nj'])
class MergeBranchIntoTargetRequestQuery(StrictModel):
    target_branch_id: str = Field(default=..., description="The unique identifier of the target branch to merge into. Must be the main branch.", examples=['agtbrch_8901k4t9z5defmb8vh3e9361y7nj'])
class MergeBranchIntoTargetRequestBody(StrictModel):
    archive_source_branch: bool | None = Field(default=None, description="Whether to archive the source branch after a successful merge.")
class MergeBranchIntoTargetRequest(StrictModel):
    """Merge a source branch into a target branch, optionally archiving the source branch after the merge completes."""
    path: MergeBranchIntoTargetRequestPath
    query: MergeBranchIntoTargetRequestQuery
    body: MergeBranchIntoTargetRequestBody | None = None

# Operation: deploy_agent
class CreateAgentDeploymentRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent for which to create or update deployments.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class CreateAgentDeploymentRouteRequestBodyDeploymentRequest(StrictModel):
    requests: list[AgentDeploymentRequestItem] = Field(default=..., validation_alias="requests", serialization_alias="requests", description="An ordered list of deployment configurations, each specifying a branch and its traffic allocation strategy. Order may affect deployment precedence.", examples=[[{'branch_id': 'agtbrch_8901k4t9z5defmb8vh3e9361y7nj', 'deployment_strategy': {'traffic_percentage': 0.5}}]])
class CreateAgentDeploymentRouteRequestBody(StrictModel):
    deployment_request: CreateAgentDeploymentRouteRequestBodyDeploymentRequest
class CreateAgentDeploymentRouteRequest(StrictModel):
    """Create or update deployments for an agent, specifying which branches to deploy and how to distribute traffic across them."""
    path: CreateAgentDeploymentRouteRequestPath
    body: CreateAgentDeploymentRouteRequestBody

# Operation: create_agent_draft
class CreateAgentDraftRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent for which to create a draft.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class CreateAgentDraftRouteRequestQuery(StrictModel):
    branch_id: str = Field(default=..., description="The unique identifier of the agent branch where the draft will be created.", examples=['agtbrch_8901k4t9z5defmb8vh3e9361y7nj'])
class CreateAgentDraftRouteRequestBodyWorkflow(StrictModel):
    edges: dict[str, WorkflowEdgeModelInput] | None = Field(default=None, validation_alias="edges", serialization_alias="edges", description="Workflow connections defining how nodes interact. Each edge represents a transition or data flow between nodes in the agent's workflow graph.")
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(default=None, validation_alias="nodes", serialization_alias="nodes", description="Workflow nodes representing individual components or steps in the agent's logic. Nodes define actions, decision points, or processing stages.", min_length=1)
class CreateAgentDraftRouteRequestBody(StrictModel):
    conversation_config: dict[str, Any] = Field(default=..., description="Configuration object defining conversation behavior, including parameters for dialogue flow, response handling, and interaction settings.")
    platform_settings: dict[str, Any] = Field(default=..., description="Configuration object specifying platform-specific settings such as deployment targets, feature flags, and integration parameters.")
    name: str = Field(default=..., description="A human-readable name for the draft to help identify and organize different versions.")
    tags: list[str] | None = Field(default=None, description="Optional labels for categorizing and filtering the agent draft. Tags enable organization by use case, domain, or other classification criteria.", examples=[['Customer Support', 'Technical Help', 'Eleven']])
    workflow: CreateAgentDraftRouteRequestBodyWorkflow | None = None
class CreateAgentDraftRouteRequest(StrictModel):
    """Create a new draft version of an agent with specified configuration, platform settings, and workflow structure. Drafts allow you to develop and test agent changes before publishing."""
    path: CreateAgentDraftRouteRequestPath
    query: CreateAgentDraftRouteRequestQuery
    body: CreateAgentDraftRouteRequestBody

# Operation: delete_agent_draft
class DeleteAgentDraftRouteRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the agent whose draft should be deleted.", examples=['agent_3701k3ttaq12ewp8b7qv5rfyszkz'])
class DeleteAgentDraftRouteRequestQuery(StrictModel):
    branch_id: str = Field(default=..., description="The identifier of the agent branch containing the draft to delete.", examples=['agtbrch_8901k4t9z5defmb8vh3e9361y7nj'])
class DeleteAgentDraftRouteRequest(StrictModel):
    """Delete a draft version of an agent. This removes the unpublished changes associated with the specified agent and branch."""
    path: DeleteAgentDraftRouteRequestPath
    query: DeleteAgentDraftRouteRequestQuery

# Operation: list_environment_variables
class ListEnvironmentVariablesRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of environment variables to return per request. Useful for pagination when working with large variable sets.", ge=1, le=100)
    label: str | None = Field(default=None, description="Filter results to return only environment variables matching this exact label value.")
    type_: Literal["string", "secret", "auth_connection"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results by variable type to narrow down to specific categories of environment variables.")
class ListEnvironmentVariablesRequest(StrictModel):
    """Retrieve all environment variables configured in your workspace with optional filtering by label or variable type. Results are paginated for efficient data retrieval."""
    query: ListEnvironmentVariablesRequestQuery | None = None

# Operation: create_environment_variable
class CreateEnvironmentVariableRequestBody(StrictModel):
    type_: Literal["string"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type or category of the environment variable, determining how it will be processed and used within the workspace.")
    label: str = Field(default=..., description="A unique identifier label for this environment variable within the workspace. Used to reference the variable in configurations and deployments.")
    values: dict[str, str] = Field(default=..., description="A mapping of environment names to their corresponding values. Must include at least a 'production' key with its associated value for production deployments.")
class CreateEnvironmentVariableRequest(StrictModel):
    """Create a new environment variable for the workspace with environment-specific values. Environment variables enable dynamic configuration management across different deployment environments."""
    body: CreateEnvironmentVariableRequestBody

# Operation: get_environment_variable
class GetEnvironmentVariableRequestPath(StrictModel):
    env_var_id: str = Field(default=..., description="The unique identifier of the environment variable to retrieve.")
class GetEnvironmentVariableRequest(StrictModel):
    """Retrieve a specific environment variable by its unique identifier. Use this to fetch configuration values stored in your environment."""
    path: GetEnvironmentVariableRequestPath

# Operation: update_environment_variable
class UpdateEnvironmentVariableRequestPath(StrictModel):
    env_var_id: str = Field(default=..., description="The unique identifier of the environment variable to update.")
class UpdateEnvironmentVariableRequestBody(StrictModel):
    values: dict[str, str | EnvironmentVariableSecretValueRequest | EnvironmentVariableAuthConnectionValueRequest] = Field(default=..., description="A mapping of environment names to their values. Set an environment's value to null to remove it from the variable (production environment is required and cannot be removed).")
class UpdateEnvironmentVariableRequest(StrictModel):
    """Update an environment variable's values across different environments. Set values to null to remove a specific environment (production environment cannot be removed)."""
    path: UpdateEnvironmentVariableRequestPath
    body: UpdateEnvironmentVariableRequestBody

# Operation: generate_composition_plan
class ComposePlanRequestBodySourceCompositionPlan(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Array of musical styles and directions that should be emphasized throughout the entire composition. Specify in English for optimal results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Array of musical styles and directions to exclude from the entire composition. Specify in English for optimal results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Array of song sections defining the structure and progression of the composition. Order matters and determines the sequence of sections in the final output.", max_length=30)
class ComposePlanRequestBody(StrictModel):
    prompt: str = Field(default=..., description="Text prompt describing the desired composition, musical style, mood, and any specific creative direction.", max_length=4100)
    music_length_ms: int | None = Field(default=None, description="Target duration for the composition in milliseconds. If omitted, the model will automatically determine an appropriate length based on the prompt.", ge=3000, le=600000)
    model_id: Literal["music_v1"] | None = Field(default=None, description="The AI model version to use for generating the composition plan.")
    source_composition_plan: ComposePlanRequestBodySourceCompositionPlan
class ComposePlanRequest(StrictModel):
    """Generate a detailed composition plan from a text prompt, specifying musical structure, styles, and duration for music generation."""
    body: ComposePlanRequestBody

# Operation: compose_song
class GenerateRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3 at 44.1kHz with 128kbps bitrate). Higher bitrates and PCM formats require appropriate subscription tier.")
class GenerateRequestBodyMusicPrompt(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Array of musical styles and directions to include throughout the entire song. Specify in English for optimal results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Array of musical styles and directions to exclude from the entire song. Specify in English for optimal results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array defining the song structure, including individual sections with their characteristics and durations.", max_length=30)
class GenerateRequestBodyCompositionPlan(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Array of musical styles and directions to include throughout the entire song. Specify in English for optimal results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Array of musical styles and directions to exclude from the entire song. Specify in English for optimal results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array defining the song structure, including individual sections with their characteristics and durations.", max_length=30)
class GenerateRequestBody(StrictModel):
    prompt: str | None = Field(default=None, description="Simple text description of the song to generate. Cannot be combined with composition_plan. Use this for quick, straightforward song generation.", max_length=4100)
    music_length_ms: int | None = Field(default=None, description="Target song duration in milliseconds. Only used with prompt-based generation. The model will adjust to fit this duration if provided.", ge=3000, le=600000)
    model_id: Literal["music_v1"] | None = Field(default=None, description="AI model version to use for music generation.")
    force_instrumental: bool | None = Field(default=None, description="When enabled, ensures the generated song contains no vocals and is purely instrumental. Only applicable with prompt-based generation.")
    use_phonetic_names: bool | None = Field(default=None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word-level timestamps.")
    respect_sections_durations: bool | None = Field(default=None, description="Controls section duration enforcement in composition plans. When true, strictly respects each section's specified duration. When false, allows duration adjustments for improved quality and latency while maintaining total song length.")
    music_prompt: GenerateRequestBodyMusicPrompt
    composition_plan: GenerateRequestBodyCompositionPlan
class GenerateRequest(StrictModel):
    """Generate a complete song from either a text prompt or a detailed composition plan, with control over musical style, structure, and audio output format."""
    query: GenerateRequestQuery | None = None
    body: GenerateRequestBody

# Operation: compose_song_detailed
class ComposeDetailedRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec, sample rate, and bitrate. Higher bitrates and sample rates may require elevated subscription tiers.")
class ComposeDetailedRequestBodyMusicPrompt(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Musical styles and directions to include throughout the entire song. Use English language for optimal results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Musical styles and directions to exclude from the entire song. Use English language for optimal results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array of song sections, each with duration, style, and lyrical content specifications. Order determines playback sequence.", max_length=30)
class ComposeDetailedRequestBodyCompositionPlan(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Musical styles and directions to include throughout the entire song when using composition_plan. Use English language for optimal results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Musical styles and directions to exclude from the entire song when using composition_plan. Use English language for optimal results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array of song sections for composition_plan, each with duration, style, and lyrical content specifications. Order determines playback sequence.", max_length=30)
class ComposeDetailedRequestBody(StrictModel):
    prompt: str | None = Field(default=None, description="Text-based prompt describing the song to generate. Mutually exclusive with composition_plan. Provide creative direction, mood, genre, and lyrical themes.", max_length=4100)
    music_length_ms: int | None = Field(default=None, description="Target song duration in milliseconds. Only applicable with prompt-based generation. If omitted, the model automatically determines length based on prompt content.", ge=3000, le=600000)
    model_id: Literal["music_v1"] | None = Field(default=None, description="AI model version to use for music generation.")
    force_instrumental: bool | None = Field(default=None, description="When enabled, ensures the generated song contains no vocals. Only works with prompt-based generation.")
    use_phonetic_names: bool | None = Field(default=None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word timestamps.")
    respect_sections_durations: bool | None = Field(default=None, description="Controls section duration enforcement in composition_plan. When true, strictly respects each section's specified duration. When false, allows duration flexibility for improved quality and latency while maintaining total song length.")
    with_timestamps: bool | None = Field(default=None, description="When enabled, the response includes precise word-level timestamps indicating when each lyric occurs in the generated audio.")
    music_prompt: ComposeDetailedRequestBodyMusicPrompt
    composition_plan: ComposeDetailedRequestBodyCompositionPlan
class ComposeDetailedRequest(StrictModel):
    """Generate a complete song with detailed metadata from either a text prompt or a structured composition plan. Returns audio file and optional word-level timestamps."""
    query: ComposeDetailedRequestQuery | None = None
    body: ComposeDetailedRequestBody

# Operation: compose_music
class StreamComposeRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Audio output format specified as codec, sample rate, and bitrate. Higher bitrates and sample rates may require elevated subscription tiers.")
class StreamComposeRequestBodyMusicPrompt(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Musical styles and directions to include throughout the entire composition. Use English language for best results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Musical styles and directions to exclude from the entire composition. Use English language for best results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array defining distinct sections of the song, each with its own musical characteristics and transitions.", max_length=30)
class StreamComposeRequestBodyCompositionPlan(StrictModel):
    positive_global_styles: list[str] = Field(default=..., validation_alias="positive_global_styles", serialization_alias="positive_global_styles", description="Musical styles and directions to include throughout the entire composition. Use English language for best results.", max_length=50)
    negative_global_styles: list[str] = Field(default=..., validation_alias="negative_global_styles", serialization_alias="negative_global_styles", description="Musical styles and directions to exclude from the entire composition. Use English language for best results.", max_length=50)
    sections: list[SongSection] = Field(default=..., validation_alias="sections", serialization_alias="sections", description="Ordered array defining distinct sections of the song, each with its own musical characteristics and transitions.", max_length=30)
class StreamComposeRequestBody(StrictModel):
    prompt: str | None = Field(default=None, description="Simple text description to generate a song from. Mutually exclusive with composition_plan. Use English for optimal results.", max_length=4100)
    music_length_ms: int | None = Field(default=None, description="Target duration for the generated composition in milliseconds. Only applicable when using prompt-based generation. If omitted, the model determines length based on the prompt.", ge=3000, le=600000)
    model_id: Literal["music_v1"] | None = Field(default=None, description="The generative model version to use for music composition.")
    force_instrumental: bool | None = Field(default=None, description="When enabled, ensures the generated composition contains no vocals. Only applicable with prompt-based generation.")
    use_phonetic_names: bool | None = Field(default=None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word-level timestamps.")
    music_prompt: StreamComposeRequestBodyMusicPrompt
    composition_plan: StreamComposeRequestBodyCompositionPlan
class StreamComposeRequest(StrictModel):
    """Generate and stream composed music from either a text prompt or a detailed composition plan. Supports various audio formats and customizable musical styles."""
    query: StreamComposeRequestQuery | None = None
    body: StreamComposeRequestBody

# Operation: upload_song
class UploadSongRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The audio file to upload in binary format.", json_schema_extra={'format': 'byte'})
    extract_composition_plan: bool | None = Field(default=None, description="Whether to generate and return the composition plan for the uploaded song. Enabling this increases response latency.")
class UploadSongRequest(StrictModel):
    """Upload a music file for use in inpainting workflows. This operation is restricted to enterprise clients with access to the inpainting feature."""
    body: UploadSongRequestBody

# Operation: separate_song_stems
class SeparateSongStemsRequestQuery(StrictModel):
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(default=None, description="Output format for the separated stems, specified as codec_sample_rate_bitrate. MP3 192kbps requires Creator tier or above; PCM 44.1kHz requires Pro tier or above. μ-law format is commonly used for Twilio audio inputs.")
class SeparateSongStemsRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The audio file to separate into individual stems. Provide the binary audio data.", json_schema_extra={'format': 'byte'})
    stem_variation_id: Literal["two_stems_v1", "six_stems_v1"] | None = Field(default=None, description="The stem separation model variation to use. Two-stem splits into vocals and instruments; six-stem provides more granular separation.")
class SeparateSongStemsRequest(StrictModel):
    """Separate an audio file into individual musical stems (vocals, drums, bass, etc.). This operation may have high latency depending on audio file length."""
    query: SeparateSongStemsRequestQuery | None = None
    body: SeparateSongStemsRequestBody

# Operation: create_voice_pvc
class CreatePvcVoiceRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this voice, shown in voice selection dropdowns and UI.", max_length=100, examples=['John Smith'])
    language: str = Field(default=..., description="The language code for the voice samples and voice model training.", examples=['en'])
    description: str | None = Field(default=None, description="Optional description providing context about the voice characteristics and intended use cases.", max_length=500, examples=['An old American male voice with a slight hoarseness in his throat. Perfect for news.'])
    labels: dict[str, str] | None = Field(default=None, description="Optional metadata labels to categorize and describe the voice. Supports language, accent, gender, and age attributes.", examples=['{"language": "en", "accent": "en-US", "gender": "male", "age": "middle-aged"}'])
class CreatePvcVoiceRequest(StrictModel):
    """Creates a new PVC voice with metadata. Voice samples can be added later to train the voice model."""
    body: CreatePvcVoiceRequestBody

# Operation: update_voice_pvc
class EditPvcVoiceRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
class EditPvcVoiceRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Display name for the voice as shown in voice selection interfaces.", max_length=100, examples=['John Smith'])
    language: str | None = Field(default=None, description="Language code of the voice samples (e.g., 'en' for English).", examples=['en'])
    description: str | None = Field(default=None, description="Detailed description of the voice characteristics and intended use cases.", max_length=500, examples=['An old American male voice with a slight hoarseness in his throat. Perfect for news.'])
    labels: dict[str, str] | None = Field(default=None, description="Classification labels for the voice including language, accent, gender, and age characteristics.", examples=['{"language": "en", "accent": "en-US", "gender": "male", "age": "middle-aged"}'])
class EditPvcVoiceRequest(StrictModel):
    """Update metadata for a PVC (Professional Voice Clone) voice, including name, language, description, and classification labels."""
    path: EditPvcVoiceRequestPath
    body: EditPvcVoiceRequestBody | None = None

# Operation: add_voice_samples
class AddPvcVoiceSamplesRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the PVC voice to add samples to. Use the voices list endpoint to retrieve available voice IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
class AddPvcVoiceSamplesRequestBody(StrictModel):
    files: list[Annotated[str, Field(json_schema_extra={'format': 'byte'})]] = Field(default=..., description="Base64-encoded file content for upload. Audio files to add to the voice. Provide one or more audio files in supported formats to expand the voice training dataset.")
    remove_background_noise: bool | None = Field(default=None, description="Enable automatic background noise removal from audio samples using audio isolation. Disable if samples contain minimal background noise, as processing may reduce quality.", examples=[True])
class AddPvcVoiceSamplesRequest(StrictModel):
    """Add audio samples to a PVC (Personal Voice Clone) to enhance voice quality and training data. Optionally remove background noise from samples to improve voice clarity."""
    path: AddPvcVoiceSamplesRequestPath
    body: AddPvcVoiceSamplesRequestBody

# Operation: update_voice_sample
class EditPvcVoiceSampleRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice model containing the sample to update.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the voice sample to update.", examples=['VW7YKqPnjY4h39yTbx2L'])
class EditPvcVoiceSampleRequestBody(StrictModel):
    remove_background_noise: bool | None = Field(default=None, description="Enable background noise removal using audio isolation. Only apply if the sample contains background noise, as it may degrade quality otherwise.", examples=[True])
    selected_speaker_ids: list[str] | None = Field(default=None, description="List of speaker IDs to use for PVC training. Sending a new list will replace any previously selected speakers for this sample.", examples=['speaker_0'])
    trim_start_time: int | None = Field(default=None, description="The start time of the audio segment to use for PVC training, specified in milliseconds from the beginning of the file.", examples=[0])
    trim_end_time: int | None = Field(default=None, description="The end time of the audio segment to use for PVC training, specified in milliseconds from the beginning of the file.", examples=[10])
    file_name: str | None = Field(default=None, description="The name to assign to the audio file for PVC training purposes.", examples=['sample.mp3'])
class EditPvcVoiceSampleRequest(StrictModel):
    """Update a PVC voice sample by applying noise removal, selecting speakers, adjusting trim times, or changing the file name. Changes are applied to the specified sample within a voice model."""
    path: EditPvcVoiceSampleRequestPath
    body: EditPvcVoiceSampleRequestBody | None = None

# Operation: remove_voice_sample
class DeletePvcVoiceSampleRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the PVC voice from which to remove the sample.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the sample to be deleted from the voice.", examples=['VW7YKqPnjY4h39yTbx2L'])
class DeletePvcVoiceSampleRequest(StrictModel):
    """Remove a sample from a PVC (Professional Voice Clone) voice. This permanently deletes the specified sample, which cannot be undone."""
    path: DeletePvcVoiceSampleRequestPath

# Operation: get_voice_sample_audio
class GetPvcSampleAudioRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice whose sample audio you want to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the specific voice sample to retrieve.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetPvcSampleAudioRequestQuery(StrictModel):
    remove_background_noise: bool | None = Field(default=None, description="Enable background noise removal using audio isolation. Note: applying this to samples without background noise may degrade audio quality.", examples=[True])
class GetPvcSampleAudioRequest(StrictModel):
    """Retrieve the first 30 seconds of audio from a voice sample, with optional background noise removal using audio isolation technology."""
    path: GetPvcSampleAudioRequestPath
    query: GetPvcSampleAudioRequestQuery | None = None

# Operation: get_voice_sample_waveform
class GetPvcSampleVisualWaveformRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice whose sample waveform you want to retrieve.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the voice sample whose waveform you want to retrieve.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetPvcSampleVisualWaveformRequest(StrictModel):
    """Retrieve the visual waveform representation of a specific voice sample. This waveform can be used to visualize the audio characteristics of the sample."""
    path: GetPvcSampleVisualWaveformRequestPath

# Operation: get_speaker_separation_status
class GetPvcSampleSpeakersRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice whose sample is being analyzed.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the voice sample undergoing speaker separation analysis.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetPvcSampleSpeakersRequest(StrictModel):
    """Retrieve the current status of speaker separation processing for a voice sample and list any detected speakers if the process is complete."""
    path: GetPvcSampleSpeakersRequestPath

# Operation: separate_speakers
class StartSpeakerSeparationRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to be used for the separation process.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the audio sample to be processed for speaker separation.", examples=['VW7YKqPnjY4h39yTbx2L'])
class StartSpeakerSeparationRequest(StrictModel):
    """Initiate speaker separation processing for an audio sample, which identifies and isolates individual speakers within the sample."""
    path: StartSpeakerSeparationRequestPath

# Operation: get_speaker_audio
class GetSpeakerAudioRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice. Use the voices list endpoint to discover available voice IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
    sample_id: str = Field(default=..., description="The unique identifier of the sample within the specified voice.", examples=['VW7YKqPnjY4h39yTbx2L'])
    speaker_id: str = Field(default=..., description="The unique identifier of the speaker whose audio should be extracted. Use the speakers list endpoint for the voice and sample to discover available speaker IDs.", examples=['VW7YKqPnjY4h39yTbx2L'])
class GetSpeakerAudioRequest(StrictModel):
    """Retrieve the isolated audio track for a specific speaker from a voice sample. This operation extracts and returns only the audio corresponding to the designated speaker."""
    path: GetSpeakerAudioRequestPath

# Operation: train_voice
class RunPvcVoiceTrainingRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to train. You can retrieve available voices from the voices list endpoint.", examples=['21m00Tcm4TlvDq8ikWAM'])
class RunPvcVoiceTrainingRequestBody(StrictModel):
    model_id: str | None = Field(default=None, description="The AI model version to use for training. Specifies which voice conversion model architecture to apply during the training process.", examples=['eleven_turbo_v2'])
class RunPvcVoiceTrainingRequest(StrictModel):
    """Start a PVC (Personal Voice Cloning) training process for a specified voice. This initiates the model training that enables voice customization and optimization."""
    path: RunPvcVoiceTrainingRequestPath
    body: RunPvcVoiceTrainingRequestBody | None = None

# Operation: submit_voice_verification
class RequestPvcManualVerificationRequestPath(StrictModel):
    voice_id: str = Field(default=..., description="The unique identifier of the voice to be verified. Use the voices list endpoint to retrieve available voice IDs.", examples=['21m00Tcm4TlvDq8ikWAM'])
class RequestPvcManualVerificationRequestBody(StrictModel):
    files: list[Annotated[str, Field(json_schema_extra={'format': 'byte'})]] = Field(default=..., description="Base64-encoded file content for upload. Array of verification document files to submit for manual review. Documents should be in a supported format and clearly demonstrate voice ownership or authorization.")
    extra_text: str | None = Field(default=None, description="Optional additional context or information to support the verification request, such as clarification about the voice or usage intent.")
class RequestPvcManualVerificationRequest(StrictModel):
    """Submit verification documents for manual review of a PVC (Premium Voice Clone) voice. This process validates the voice identity before it can be used in production."""
    path: RequestPvcManualVerificationRequestPath
    body: RequestPvcManualVerificationRequestBody

# ============================================================================
# Component Models
# ============================================================================

class AgentDeploymentPercentageStrategy(PermissiveModel):
    type_: Literal["percentage"] | None = Field('percentage', validation_alias="type", serialization_alias="type")
    traffic_percentage: float = Field(..., description="Traffic percentage to deploy", ge=0.0, le=100.0)

class AgentDeploymentRequestItem(PermissiveModel):
    branch_id: str = Field(..., description="ID of the branch to deploy")
    deployment_strategy: AgentDeploymentPercentageStrategy

class AgentFailureResponseExample(PermissiveModel):
    response: str
    type_: Literal["failure"] = Field(..., validation_alias="type", serialization_alias="type")

class AgentMetadata(PermissiveModel):
    agent_id: str
    branch_id: str | None = None
    workflow_node_id: str | None = None
    version_id: str | None = None

class AgentSuccessfulResponseExample(PermissiveModel):
    response: str
    type_: Literal["success"] = Field(..., validation_alias="type", serialization_alias="type")

class AgentTransfer(PermissiveModel):
    agent_id: str
    condition: str
    delay_ms: int | None = 0
    transfer_message: str | None = None
    enable_transferred_agent_first_message: bool | None = False
    is_workflow_node_transfer: bool | None = False

class AllowlistItem(PermissiveModel):
    hostname: str = Field(..., description="The hostname of the allowed origin")

class AsrConversationalConfigWorkflowOverride(PermissiveModel):
    quality: Literal["high"] | None = Field(None, description="The quality of the transcription")
    provider: Literal["elevenlabs", "scribe_realtime"] | None = Field(None, description="The provider of the transcription service")
    user_input_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field(None, description="The format of the audio to be transcribed")
    keywords: list[str] | None = Field(None, description="Keywords to boost prediction probability for")

class AstBooleanNodeInput(PermissiveModel):
    type_: Literal["boolean_literal"] | None = Field('boolean_literal', validation_alias="type", serialization_alias="type")
    value: bool = Field(..., description="Value of this literal.")

class AstDynamicVariableNodeInput(PermissiveModel):
    type_: Literal["dynamic_variable"] | None = Field('dynamic_variable', validation_alias="type", serialization_alias="type")
    name: str = Field(..., description="The name of the dynamic variable.")

class AstNumberNodeInput(PermissiveModel):
    type_: Literal["number_literal"] | None = Field('number_literal', validation_alias="type", serialization_alias="type")
    value: float = Field(..., description="Value of this literal.")

class AstStringNodeInput(PermissiveModel):
    type_: Literal["string_literal"] | None = Field('string_literal', validation_alias="type", serialization_alias="type")
    value: str = Field(..., description="Value of this literal.")

class AstllmNodeInputV1(PermissiveModel):
    type_: Literal["llm"] | None = Field('llm', validation_alias="type", serialization_alias="type")
    prompt: str = Field(..., description="The prompt to evaluate to a boolean value. Deprecated. Use a boolean schema instead.")

class AttachedTestModel(PermissiveModel):
    test_id: str
    workflow_node_id: str | None = None

class AuthConnectionLocator(PermissiveModel):
    """Used to reference an auth connection from the workspace's auth connection store."""
    auth_connection_id: str

class BackupLlmDefault(PermissiveModel):
    preference: Literal["default"] | None = 'default'

class BackupLlmDisabled(PermissiveModel):
    preference: Literal["disabled"] | None = 'disabled'

class BackupLlmOverride(PermissiveModel):
    preference: Literal["override"] | None = 'override'
    order: list[Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"]]

class ChapterContentParagraphTtsNodeInputModel(PermissiveModel):
    type_: Literal["tts_node"] = Field(..., validation_alias="type", serialization_alias="type")
    text: str
    voice_id: str

class ChapterContentBlockInputModel(PermissiveModel):
    sub_type: Literal["p", "h1", "h2", "h3"] | None = None
    nodes: list[ChapterContentParagraphTtsNodeInputModel]
    block_id: str | None = None

class CheckRentalAvailabilityParams(PermissiveModel):
    smb_tool_type: Literal["check_rental_availability"] | None = 'check_rental_availability'

class CheckServiceAvailabilityParams(PermissiveModel):
    smb_tool_type: Literal["check_service_availability"] | None = 'check_service_availability'

class ConstantSchemaOverride(PermissiveModel):
    source: Literal["constant"] | None = 'constant'
    constant_value: str | int | float | bool = Field(..., description="The constant value to use")

class ConvAiDynamicVariable(PermissiveModel):
    """Used to reference a dynamic variable."""
    variable_name: str

class ConvAiEnvVarLocator(PermissiveModel):
    """Used to reference an environment variable by label."""
    env_var_label: str

class ConvAiSecretLocator(PermissiveModel):
    """Used to reference a secret from the agent's secret store."""
    secret_id: str

class ConvAiUserSecretDbModel(PermissiveModel):
    """User-specific secret model that are not shared with other users in a workspace."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    encrypted_value: str
    nonce: str

class ConversationConfigOverride(PermissiveModel):
    text_only: bool | None = Field(None, description="If enabled audio will not be processed and only text will be used, use to avoid audio pricing.")

class ConversationConfigWorkflowOverride(PermissiveModel):
    text_only: bool | None = Field(None, description="If enabled audio will not be processed and only text will be used, use to avoid audio pricing.")
    max_duration_seconds: int | None = Field(None, description="The maximum duration of a conversation in seconds")
    client_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to the client")
    monitoring_enabled: bool | None = Field(None, description="Enable real-time monitoring of conversations via WebSocket")
    monitoring_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to monitoring connections.")

class ConversationHistoryMultivoiceMessagePartModel(PermissiveModel):
    """Represents a single voice part of a multi-voice message."""
    text: str
    voice_label: str | None = Field(...)
    time_in_call_secs: int | None = Field(...)

class ConversationHistoryMultivoiceMessageModel(PermissiveModel):
    """Represents a message from a multi-voice agent."""
    parts: list[ConversationHistoryMultivoiceMessagePartModel]

class ConversationHistoryTranscriptToolCallClientDetails(PermissiveModel):
    type_: Literal["client"] | None = Field('client', validation_alias="type", serialization_alias="type")
    parameters: str

class ConversationHistoryTranscriptToolCallMcpDetails(PermissiveModel):
    type_: Literal["mcp"] | None = Field('mcp', validation_alias="type", serialization_alias="type")
    mcp_server_id: str
    mcp_server_name: str
    integration_type: str
    parameters: dict[str, str] | None = None
    approval_policy: str
    requires_approval: bool | None = False
    mcp_tool_name: str | None = ''
    mcp_tool_description: str | None = ''

class ConversationHistoryTranscriptToolCallWebhookDetails(PermissiveModel):
    type_: Literal["webhook"] | None = Field('webhook', validation_alias="type", serialization_alias="type")
    method: str
    url: str
    headers: dict[str, str] | None = None
    path_params: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    body: str | None = None

class ConversationHistoryTranscriptToolCallApiIntegrationWebhookDetailsInput(PermissiveModel):
    type_: Literal["api_integration_webhook"] | None = Field('api_integration_webhook', validation_alias="type", serialization_alias="type")
    integration_id: str | None = ''
    credential_id: str | None = ''
    integration_connection_id: str | None = ''
    webhook_details: ConversationHistoryTranscriptToolCallWebhookDetails

class ConversationHistoryTranscriptToolCallCommonModelInput(PermissiveModel):
    type_: Literal["system", "webhook", "client", "mcp", "workflow", "api_integration_webhook", "api_integration_mcp", "smb"] | None = Field(None, validation_alias="type", serialization_alias="type")
    request_id: str
    tool_name: str
    params_as_json: str
    tool_has_been_called: bool
    tool_details: ConversationHistoryTranscriptToolCallWebhookDetails | ConversationHistoryTranscriptToolCallClientDetails | ConversationHistoryTranscriptToolCallMcpDetails | ConversationHistoryTranscriptToolCallApiIntegrationWebhookDetailsInput | None = None

class ConversationInitiationSourceInfo(PermissiveModel):
    """Information about the source of conversation initiation"""
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="Source of the conversation initiation")
    version: str | None = Field(None, description="The SDK version number", max_length=50)

class CreateAgentRouteBodyConversationConfigAgentDynamicVariables(PermissiveModel):
    """Configuration for dynamic variables"""
    dynamic_variable_placeholders: dict[str, str | float | int | bool] | None = Field(None, description="A dictionary of dynamic variable placeholders and their values")

class CreateAgentRouteBodyConversationConfigAgentPromptCustomLlm(PermissiveModel):
    """Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'"""
    url: str = Field(..., description="The URL of the Chat Completions compatible endpoint")
    model_id: str | None = Field(None, description="The model ID to be used if URL serves multiple models")
    api_key: ConvAiSecretLocator | ConvAiEnvVarLocator | None = Field(None, description="The API key for authentication. Either a workspace secret reference {'secret_id': '...'} or an environment variable reference {'env_var_label': '...'}.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(None, description="Headers that should be included in the request")
    api_version: str | None = Field(None, description="The API version to use for the request")
    api_type: Literal["chat_completions", "responses"] | None = Field('chat_completions', description="The API type to use (chat_completions or responses)")

class CreateAgentRouteBodyConversationConfigAgentPromptRag(PermissiveModel):
    """Configuration for RAG"""
    enabled: bool | None = False
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = 'e5_mistral_7b_instruct'
    max_vector_distance: float | None = Field(0.6, description="Maximum vector distance of retrieved chunks.", gt=0.0, lt=1.0)
    max_documents_length: int | None = Field(50000, description="Maximum total length of document chunks retrieved from RAG.", gt=0, lt=10000000)
    max_retrieved_rag_chunks_count: int | None = Field(20, description="Maximum number of RAG document chunks to initially retrieve from the vector store. These are then further filtered by vector distance and total length.", le=20, gt=0)
    num_candidates: int | None = Field(None, description="Number of candidates evaluated in ANN vector search. Higher number means better results, but higher latency. Minimum recommended value is 100. If disabled, the default value is used.", le=10000, gt=0)
    query_rewrite_prompt_override: str | None = Field(None, description="Custom prompt for rewriting user queries before RAG retrieval. The conversation history will be automatically appended at the end. If not set, the default prompt will be used.", min_length=1, max_length=1000)

class CreateAgentRouteBodyConversationConfigAsr(PermissiveModel):
    """Configuration for conversational transcription"""
    quality: Literal["high"] | None = Field('high', description="The quality of the transcription")
    provider: Literal["elevenlabs", "scribe_realtime"] | None = Field('elevenlabs', description="The provider of the transcription service")
    user_input_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The format of the audio to be transcribed")
    keywords: list[str] | None = Field(None, description="Keywords to boost prediction probability for")

class CreateAgentRouteBodyConversationConfigConversation(PermissiveModel):
    """Configuration for conversational events"""
    text_only: bool | None = Field(False, description="If enabled audio will not be processed and only text will be used, use to avoid audio pricing.")
    max_duration_seconds: int | None = Field(600, description="The maximum duration of a conversation in seconds")
    client_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to the client")
    monitoring_enabled: bool | None = Field(False, description="Enable real-time monitoring of conversations via WebSocket")
    monitoring_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to monitoring connections.")

class CreateAgentRouteBodyConversationConfigTurnSoftTimeoutConfig(PermissiveModel):
    """Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses."""
    timeout_seconds: float | None = Field(-1.0, description="Time in seconds before showing the predefined message while waiting for LLM response. Set to -1 to disable.")
    message: str | None = Field('Hhmmmm...yeah.', description="Message to show when soft timeout is reached while waiting for LLM response", min_length=1, max_length=200)
    use_llm_generated_message: bool | None = Field(False, description="If enabled, the soft timeout message will be generated dynamically instead of using the static message.")

class CreateAgentRouteBodyConversationConfigTurn(PermissiveModel):
    """Configuration for turn detection"""
    turn_timeout: float | None = Field(7.0, description="Maximum wait time for the user's reply before re-engaging the user")
    initial_wait_time: float | None = Field(None, description="How long the agent will wait for the user to start the conversation if the first message is empty. If not set, uses the regular turn_timeout.")
    silence_end_call_timeout: float | None = Field(-1, description="Maximum wait time since the user last spoke before terminating the call")
    soft_timeout_config: CreateAgentRouteBodyConversationConfigTurnSoftTimeoutConfig | None = Field(None, description="Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses.")
    mode: Literal["silence", "turn"] | None = Field('turn', description="The mode of turn detection")
    turn_eagerness: Literal["patient", "normal", "eager"] | None = Field('normal', description="Controls how eager the agent is to respond. Low = less eager (waits longer), Standard = default eagerness, High = more eager (responds sooner)")
    spelling_patience: Literal["auto", "off"] | None = Field('auto', description="Controls if the agent should be more patient when user is spelling numbers and named entities. Auto = model based, Off = never wait extra")
    speculative_turn: bool | None = Field(False, description="When enabled, starts generating LLM responses during silence before full turn confidence is reached, reducing perceived latency. May increase LLM costs.")

class CreateAgentRouteBodyConversationConfigVad(PermissiveModel):
    """Configuration for voice activity detection"""
    background_voice_detection: bool | None = Field(False, description="Whether to use background voice filtering")

class CreateAgentRouteBodyPlatformSettingsAuth(PermissiveModel):
    """Settings for authentication"""
    enable_auth: bool | None = Field(False, description="If set to true, starting a conversation with an agent will require a signed token")
    allowlist: list[AllowlistItem] | None = Field(None, description="A list of hosts that are allowed to start conversations with the agent")
    require_origin_header: bool | None = Field(False, description="When enabled, connections with no origin header will be rejected. If the allowlist is empty, this option has no effect.")
    shareable_token: str | None = Field(None, description="A shareable token that can be used to start a conversation with the agent")

class CreateAgentRouteBodyPlatformSettingsCallLimits(PermissiveModel):
    """Call limits for the agent"""
    agent_concurrency_limit: int | None = Field(-1, description="The maximum number of concurrent conversations. -1 indicates that there is no maximum")
    daily_limit: int | None = Field(100000, description="The maximum number of conversations per day")
    bursting_enabled: bool | None = Field(True, description="Whether to enable bursting. If true, exceeding workspace concurrency limit will be allowed up to 3 times the limit. Calls will be charged at double rate when exceeding the limit.")

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigProfanity(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigReligionOrPolitics(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfig(PermissiveModel):
    sexual: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSexual | None = None
    violence: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigViolence | None = None
    harassment: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigHarassment | None = None
    self_harm: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSelfHarm | None = None
    profanity: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigProfanity | None = None
    religion_or_politics: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigReligionOrPolitics | None = None
    medical_and_legal_information: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsFocus(PermissiveModel):
    is_enabled: bool | None = False

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassmentThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHate(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHateThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmInstructions(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmIntent(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexualMinors(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolenceGraphic(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfig(PermissiveModel):
    sexual: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexual | None = None
    violence: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolence | None = None
    violence_graphic: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolenceGraphic | None = None
    harassment: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassment | None = None
    harassment_threatening: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassmentThreatening | None = None
    hate: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHate | None = None
    hate_threatening: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHateThreatening | None = None
    self_harm_instructions: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmInstructions | None = None
    self_harm: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarm | None = None
    self_harm_intent: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmIntent | None = None
    sexual_minors: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexualMinors | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsModeration(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfig | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsPromptInjection(PermissiveModel):
    is_enabled: bool | None = False

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgentPrompt(PermissiveModel):
    """Configures overrides for nested fields."""
    prompt: bool | None = Field(False, description="Whether to allow overriding the prompt field.")
    llm: bool | None = Field(False, description="Whether to allow overriding the llm field.")
    native_mcp_server_ids: bool | None = Field(False, description="Whether to allow overriding the native_mcp_server_ids field.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgent(PermissiveModel):
    """Configures overrides for nested fields."""
    first_message: bool | None = Field(False, description="Whether to allow overriding the first_message field.")
    language: bool | None = Field(False, description="Whether to allow overriding the language field.")
    prompt: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgentPrompt | None = Field(None, description="Configures overrides for nested fields.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideConversation(PermissiveModel):
    """Configures overrides for nested fields."""
    text_only: bool | None = Field(False, description="Whether to allow overriding the text_only field.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTts(PermissiveModel):
    """Configures overrides for nested fields."""
    voice_id: bool | None = Field(False, description="Whether to allow overriding the voice_id field.")
    stability: bool | None = Field(False, description="Whether to allow overriding the stability field.")
    speed: bool | None = Field(False, description="Whether to allow overriding the speed field.")
    similarity_boost: bool | None = Field(False, description="Whether to allow overriding the similarity_boost field.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig(PermissiveModel):
    """Configures overrides for nested fields."""
    message: bool | None = Field(False, description="Whether to allow overriding the message field.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurn(PermissiveModel):
    """Configures overrides for nested fields."""
    soft_timeout_config: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig | None = Field(None, description="Configures overrides for nested fields.")

class CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverride(PermissiveModel):
    """Overrides for the conversation configuration"""
    turn: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurn | None = Field(None, description="Configures overrides for nested fields.")
    tts: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTts | None = Field(None, description="Configures overrides for nested fields.")
    conversation: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideConversation | None = Field(None, description="Configures overrides for nested fields.")
    agent: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgent | None = Field(None, description="Configures overrides for nested fields.")

class CreateAgentRouteBodyPlatformSettingsOverrides(PermissiveModel):
    """Additional overrides for the agent during conversation initiation"""
    conversation_config_override: CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverride | None = Field(None, description="Overrides for the conversation configuration")
    custom_llm_extra_body: bool | None = Field(False, description="Whether to include custom LLM extra body")
    enable_conversation_initiation_client_data_from_webhook: bool | None = Field(False, description="Whether to enable conversation initiation client data from webhooks")

class CreateAgentRouteBodyPlatformSettingsPrivacyConversationHistoryRedaction(PermissiveModel):
    """Config for PII redaction in the conversation history"""
    enabled: bool | None = Field(False, description="Whether conversation history redaction is enabled")
    entities: list[Literal["name", "name.name_given", "name.name_family", "name.name_other", "email_address", "contact_number", "dob", "age", "religious_belief", "political_opinion", "sexual_orientation", "ethnicity_race", "marital_status", "occupation", "physical_attribute", "language", "username", "password", "url", "organization", "financial_id", "financial_id.payment_card", "financial_id.payment_card.payment_card_number", "financial_id.payment_card.payment_card_expiration_date", "financial_id.payment_card.payment_card_cvv", "financial_id.bank_account", "financial_id.bank_account.bank_account_number", "financial_id.bank_account.bank_routing_number", "financial_id.bank_account.swift_bic_code", "financial_id.financial_id_other", "location", "location.location_address", "location.location_city", "location.location_postal_code", "location.location_coordinate", "location.location_state", "location.location_country", "location.location_other", "date", "date_interval", "unique_id", "unique_id.government_issued_id", "unique_id.account_number", "unique_id.vehicle_id", "unique_id.healthcare_number", "unique_id.healthcare_number.medical_record_number", "unique_id.healthcare_number.health_plan_beneficiary_number", "unique_id.device_id", "unique_id.unique_id_other", "medical", "medical.medical_condition", "medical.medication", "medical.medical_procedure", "medical.medical_measurement", "medical.medical_other"]] | None = Field(None, description="The entities to redact from the conversation transcript, audio and analysis. Use top-level types like 'name', 'email_address', or dot notation for specific subtypes like 'name.full_name'.")

class CreateAgentRouteBodyPlatformSettingsPrivacy(PermissiveModel):
    """Privacy settings for the agent"""
    record_voice: bool | None = Field(True, description="Whether to record the conversation")
    retention_days: int | None = Field(-1, description="The number of days to retain the conversation. -1 indicates there is no retention limit")
    delete_transcript_and_pii: bool | None = Field(False, description="Whether to delete the transcript and PII")
    delete_audio: bool | None = Field(False, description="Whether to delete the audio")
    apply_to_existing_conversations: bool | None = Field(False, description="Whether to apply the privacy settings to existing conversations")
    zero_retention_mode: bool | None = Field(False, description="Whether to enable zero retention mode - no PII data is stored")
    conversation_history_redaction: CreateAgentRouteBodyPlatformSettingsPrivacyConversationHistoryRedaction | None = Field(None, description="Config for PII redaction in the conversation history")

class CreateAgentRouteBodyPlatformSettingsTesting(PermissiveModel):
    """Testing configuration for the agent"""
    attached_tests: list[AttachedTestModel] | None = Field(None, description="List of test IDs that should be run for this agent", min_length=0, max_length=1000)

class CreateAgentRouteBodyPlatformSettingsWidgetEndFeedback(PermissiveModel):
    """Configuration for feedback collected at the end of the conversation"""
    type_: Literal["rating"] | None = Field('rating', validation_alias="type", serialization_alias="type", description="The type of feedback to collect at the end of the conversation")

class CreateAgentRouteBodyPlatformSettingsWidgetStyles(PermissiveModel):
    """Styles for the widget"""
    base: str | None = Field(None, description="The base background color.")
    base_hover: str | None = Field(None, description="The color of the base background when hovered.")
    base_active: str | None = Field(None, description="The color of the base background when active (clicked).")
    base_border: str | None = Field(None, description="The color of the border against the base background.")
    base_subtle: str | None = Field(None, description="The color of subtle text against the base background.")
    base_primary: str | None = Field(None, description="The color of primary text against the base background.")
    base_error: str | None = Field(None, description="The color of error text against the base background.")
    accent: str | None = Field(None, description="The accent background color.")
    accent_hover: str | None = Field(None, description="The color of the accent background when hovered.")
    accent_active: str | None = Field(None, description="The color of the accent background when active (clicked).")
    accent_border: str | None = Field(None, description="The color of the border against the accent background.")
    accent_subtle: str | None = Field(None, description="The color of subtle text against the accent background.")
    accent_primary: str | None = Field(None, description="The color of primary text against the accent background.")
    overlay_padding: float | None = Field(None, description="The padding around the edges of the viewport.")
    button_radius: float | None = Field(None, description="The radius of the buttons.")
    input_radius: float | None = Field(None, description="The radius of the input fields.")
    bubble_radius: float | None = Field(None, description="The radius of the chat bubbles.")
    sheet_radius: float | None = Field(None, description="The default radius of sheets.")
    compact_sheet_radius: float | None = Field(None, description="The radius of the sheet in compact mode.")
    dropdown_sheet_radius: float | None = Field(None, description="The radius of the dropdown sheet.")

class CreateAgentRouteBodyPlatformSettingsWidgetTextContents(PermissiveModel):
    """Text contents of the widget"""
    main_label: str | None = Field(None, description="Call to action displayed inside the compact and full variants.")
    start_call: str | None = Field(None, description="Text and ARIA label for the start call button.")
    start_chat: str | None = Field(None, description="Text and ARIA label for the start chat button (text only)")
    new_call: str | None = Field(None, description="Text and ARIA label for the new call button. Displayed when the caller already finished at least one call in order ot start the next one.")
    end_call: str | None = Field(None, description="Text and ARIA label for the end call button.")
    mute_microphone: str | None = Field(None, description="ARIA label for the mute microphone button.")
    change_language: str | None = Field(None, description="ARIA label for the change language dropdown.")
    collapse: str | None = Field(None, description="ARIA label for the collapse button.")
    expand: str | None = Field(None, description="ARIA label for the expand button.")
    copied: str | None = Field(None, description="Text displayed when the user copies a value using the copy button.")
    accept_terms: str | None = Field(None, description="Text and ARIA label for the accept terms button.")
    dismiss_terms: str | None = Field(None, description="Text and ARIA label for the cancel terms button.")
    listening_status: str | None = Field(None, description="Status displayed when the agent is listening.")
    speaking_status: str | None = Field(None, description="Status displayed when the agent is speaking.")
    connecting_status: str | None = Field(None, description="Status displayed when the agent is connecting.")
    chatting_status: str | None = Field(None, description="Status displayed when the agent is chatting (text only)")
    input_label: str | None = Field(None, description="ARIA label for the text message input.")
    input_placeholder: str | None = Field(None, description="Placeholder text for the text message input.")
    input_placeholder_text_only: str | None = Field(None, description="Placeholder text for the text message input (text only)")
    input_placeholder_new_conversation: str | None = Field(None, description="Placeholder text for the text message input when starting a new conversation (text only)")
    user_ended_conversation: str | None = Field(None, description="Information message displayed when the user ends the conversation.")
    agent_ended_conversation: str | None = Field(None, description="Information message displayed when the agent ends the conversation.")
    conversation_id: str | None = Field(None, description="Text label used next to the conversation ID.")
    error_occurred: str | None = Field(None, description="Text label used when an error occurs.")
    copy_id: str | None = Field(None, description="Text and ARIA label used for the copy ID button.")
    initiate_feedback: str | None = Field(None, description="Text displayed to prompt the user for feedback.")
    request_follow_up_feedback: str | None = Field(None, description="Text displayed to request additional feedback details.")
    thanks_for_feedback: str | None = Field(None, description="Text displayed to thank the user for providing feedback.")
    thanks_for_feedback_details: str | None = Field(None, description="Additional text displayed explaining the value of user feedback.")
    follow_up_feedback_placeholder: str | None = Field(None, description="Placeholder text for the follow-up feedback input field.")
    submit: str | None = Field(None, description="Text and ARIA label for the submit button.")
    go_back: str | None = Field(None, description="Text and ARIA label for the go back button.")
    send_message: str | None = Field(None, description="Text and ARIA label for the send message button.")
    text_mode: str | None = Field(None, description="Text and ARIA label for the switch to text mode button.")
    voice_mode: str | None = Field(None, description="Text and ARIA label for the switch to voice mode button.")
    switched_to_text_mode: str | None = Field(None, description="Toast notification displayed when switching to text mode.")
    switched_to_voice_mode: str | None = Field(None, description="Toast notification displayed when switching to voice mode.")
    copy_: str | None = Field(None, validation_alias="copy", serialization_alias="copy", description="Text and ARIA label for the copy button.")
    download: str | None = Field(None, description="Text and ARIA label for the download button.")
    wrap: str | None = Field(None, description="Text and ARIA label for the wrap toggle button.")
    agent_working: str | None = Field(None, description="Status text displayed when the agent is processing a tool call.")
    agent_done: str | None = Field(None, description="Status text displayed when the agent finishes processing a tool call.")
    agent_error: str | None = Field(None, description="Status text displayed when the agent encounters an error during a tool call.")

class CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook(PermissiveModel):
    """The webhook to send conversation initiation client data to"""
    url: str = Field(..., description="The URL to send the webhook to")
    request_headers: dict[str, str | ConvAiSecretLocator] = Field(..., description="The headers to send with the webhook request")

class CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesWebhooks(PermissiveModel):
    post_call_webhook_id: str | None = None
    events: list[Literal["transcript", "audio", "call_initiation_failure"]] | None = Field(None, description="List of event types to send via webhook. Options: transcript, audio, call_initiation_failure.")
    send_audio: bool | None = Field(None, description="DEPRECATED: Use 'events' field instead. Whether to send audio data with post-call webhooks for ConvAI conversations")

class CreateAgentRouteBodyPlatformSettingsWorkspaceOverrides(PermissiveModel):
    """Workspace overrides for the agent"""
    conversation_initiation_client_data_webhook: CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook | None = Field(None, description="The webhook to send conversation initiation client data to")
    webhooks: CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesWebhooks | None = None

class CreateAssetParams(PermissiveModel):
    smb_tool_type: Literal["create_asset"] | None = 'create_asset'

class CreateClientAppointmentParams(PermissiveModel):
    smb_tool_type: Literal["create_client_appointment"] | None = 'create_client_appointment'

class CreateClientParams(PermissiveModel):
    """Create a new client in the system."""
    smb_tool_type: Literal["create_client"] | None = 'create_client'

class CreateProductParams(PermissiveModel):
    smb_tool_type: Literal["create_product"] | None = 'create_product'

class CreateRentalBookingParams(PermissiveModel):
    smb_tool_type: Literal["create_rental_booking"] | None = 'create_rental_booking'

class CreateServiceParams(PermissiveModel):
    """Create a new service in the system."""
    smb_tool_type: Literal["create_service"] | None = 'create_service'

class CreateStaffParams(PermissiveModel):
    """Create a new staff member in the system."""
    smb_tool_type: Literal["create_staff"] | None = 'create_staff'

class CriterionItemRequest(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", min_length=1)
    name: str = Field(..., min_length=1)
    conversation_goal_prompt: str = Field(..., min_length=1, max_length=2000)
    use_knowledge_base: bool | None = False

class CustomLlm(PermissiveModel):
    url: str = Field(..., description="The URL of the Chat Completions compatible endpoint")
    model_id: str | None = Field(None, description="The model ID to be used if URL serves multiple models")
    api_key: ConvAiSecretLocator | ConvAiEnvVarLocator | None = Field(None, description="The API key for authentication. Either a workspace secret reference {'secret_id': '...'} or an environment variable reference {'env_var_label': '...'}.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(None, description="Headers that should be included in the request")
    api_version: str | None = Field(None, description="The API version to use for the request")
    api_type: Literal["chat_completions", "responses"] | None = Field('chat_completions', description="The API type to use (chat_completions or responses)")

class CustomSipHeader(PermissiveModel):
    """Custom SIP header for phone transfers with a static (validated) value."""
    type_: Literal["static"] | None = Field('static', validation_alias="type", serialization_alias="type")
    key: str = Field(..., description="The SIP header name (e.g., 'X-Customer-ID')", min_length=1, max_length=64, pattern="^[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")
    value: str = Field(..., description="The header value", min_length=1, max_length=512, pattern="^[\\x09\\x20-\\x7E]+$")

class CustomSipHeaderWithDynamicVariable(PermissiveModel):
    """Custom SIP header for phone transfers with a dynamic variable reference.
The value is a variable name that will be resolved at runtime.
Value is not validated here since it will be substituted with actual value later."""
    type_: Literal["dynamic"] = Field(..., validation_alias="type", serialization_alias="type")
    key: str = Field(..., description="The SIP header name (e.g., 'X-Customer-ID')", min_length=1, max_length=64, pattern="^[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")
    value: str = Field(..., description="The dynamic variable name to resolve", min_length=1)

class DataExtractionFieldRequest(PermissiveModel):
    name: str = Field(..., min_length=1)
    type_: Literal["boolean", "string", "integer", "number"] = Field(..., validation_alias="type", serialization_alias="type")
    description: str = Field(..., min_length=1)

class DeleteAssetParams(PermissiveModel):
    smb_tool_type: Literal["delete_asset"] | None = 'delete_asset'

class DeleteCalendarEventParams(PermissiveModel):
    smb_tool_type: Literal["delete_calendar_event"] | None = 'delete_calendar_event'

class DeleteClientParams(PermissiveModel):
    """Delete an existing client from the system."""
    smb_tool_type: Literal["delete_client"] | None = 'delete_client'

class DeleteProductParams(PermissiveModel):
    smb_tool_type: Literal["delete_product"] | None = 'delete_product'

class DeleteServiceParams(PermissiveModel):
    """Delete an existing service from the system."""
    smb_tool_type: Literal["delete_service"] | None = 'delete_service'

class DeleteStaffParams(PermissiveModel):
    """Delete an existing staff member from the system."""
    smb_tool_type: Literal["delete_staff"] | None = 'delete_staff'

class DialogueInput(PermissiveModel):
    text: str = Field(..., description="The text to be converted into speech.")
    voice_id: str = Field(..., description="The ID of the voice to be used for the generation.")

class DocxExportOptions(PermissiveModel):
    include_speakers: bool | None = True
    include_timestamps: bool | None = True
    format_: Literal["docx"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = None
    max_segment_duration_s: float | None = None
    max_segment_chars: int | None = None

class DynamicVariableAssignment(PermissiveModel):
    """Configuration for extracting values from tool responses and assigning them to dynamic variables."""
    source: Literal["response"] | None = Field('response', description="The source to extract the value from. Currently only 'response' is supported.")
    dynamic_variable: str = Field(..., description="The name of the dynamic variable to assign the extracted value to")
    value_path: str = Field(..., description="Dot notation path to extract the value from the source (e.g., 'user.name' or 'data.0.id')")
    sanitize: bool | None = Field(False, description="If true, this assignment's value will be removed from the tool response before sending to the LLM and transcript, but still processed for variable assignment.")

class DynamicVariableSchemaOverride(PermissiveModel):
    source: Literal["dynamic_variable"] | None = 'dynamic_variable'
    dynamic_variable: str = Field(..., description="The name of the dynamic variable to use", min_length=1)

class DynamicVariableUpdateCommonModel(PermissiveModel):
    """Tracks a dynamic variable update that occurred during tool execution."""
    variable_name: str
    old_value: str | None = Field(...)
    new_value: str
    updated_at: float
    tool_name: str
    tool_request_id: str

class ConversationHistoryTranscriptApiIntegrationWebhookToolsResultCommonModelInput(PermissiveModel):
    request_id: str
    tool_name: str
    result_value: str
    is_error: bool
    tool_has_been_called: bool
    tool_latency_secs: float | None = 0
    error_type: str | None = ''
    raw_error_message: str | None = ''
    dynamic_variable_updates: list[DynamicVariableUpdateCommonModel] | None = None
    type_: Literal["api_integration_webhook"] = Field(..., validation_alias="type", serialization_alias="type")
    integration_id: str | None = ''
    credential_id: str | None = ''
    integration_connection_id: str | None = ''

class ConversationHistoryTranscriptOtherToolsResultCommonModel(PermissiveModel):
    request_id: str
    tool_name: str
    result_value: str
    is_error: bool
    tool_has_been_called: bool
    tool_latency_secs: float | None = 0
    error_type: str | None = ''
    raw_error_message: str | None = ''
    dynamic_variable_updates: list[DynamicVariableUpdateCommonModel] | None = None
    type_: Literal["client", "webhook", "mcp"] | None = Field(None, validation_alias="type", serialization_alias="type")

class DynamicVariablesConfig(PermissiveModel):
    dynamic_variable_placeholders: dict[str, str | float | int | bool] | None = Field(None, description="A dictionary of dynamic variable placeholders and their values")

class DynamicVariablesConfigWorkflowOverride(PermissiveModel):
    dynamic_variable_placeholders: dict[str, str | float | int | bool] | None = Field(None, description="A dictionary of dynamic variable placeholders and their values")

class EndCallToolConfig(PermissiveModel):
    system_tool_type: Literal["end_call"] | None = 'end_call'

class EndCallToolResultModel(PermissiveModel):
    result_type: Literal["end_call_success"] | None = 'end_call_success'
    status: Literal["success"] | None = 'success'
    reason: str | None = None
    message: str | None = None

class EndCallTriggerAction(PermissiveModel):
    type_: Literal["end_call"] | None = Field('end_call', validation_alias="type", serialization_alias="type")

class EnvironmentAuthConnectionLocator(PermissiveModel):
    """References an environment variable of type 'auth_connection' by label.
At runtime, resolves to the auth connection for the current environment,
falling back to the default environment."""
    env_var_label: str

class EnvironmentVariableAuthConnectionValueRequest(PermissiveModel):
    auth_connection_id: str

class EnvironmentVariableSecretValueRequest(PermissiveModel):
    secret_id: str

class ExactParameterEvaluationStrategy(PermissiveModel):
    type_: Literal["exact"] = Field(..., validation_alias="type", serialization_alias="type")
    expected_value: str = Field(..., description="The exact string value that the parameter must match.")

class GetClientAppointmentsParams(PermissiveModel):
    smb_tool_type: Literal["get_client_appointments"] | None = 'get_client_appointments'

class GetClientByPhoneParams(PermissiveModel):
    """Look up a client by their exact phone number."""
    smb_tool_type: Literal["get_client_by_phone"] | None = 'get_client_by_phone'

class GetOrCreateRagIndexRequestModel(PermissiveModel):
    document_id: str = Field(..., description="ID of the knowledgebase document for which to retrieve the index")
    create_if_missing: bool = Field(..., description="Whether to create the RAG index if it does not exist")
    model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] = Field(..., description="Embedding model to use for the RAG index")

class HtmlExportOptions(PermissiveModel):
    include_speakers: bool | None = True
    include_timestamps: bool | None = True
    format_: Literal["html"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = None
    max_segment_duration_s: float | None = None
    max_segment_chars: int | None = None

class ImageAvatar(PermissiveModel):
    type_: Literal["image"] | None = Field('image', validation_alias="type", serialization_alias="type", description="The type of the avatar")
    url: str | None = Field('', description="The URL of the avatar")

class KnowledgeBaseLocator(PermissiveModel):
    type_: Literal["file", "url", "text", "folder"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the knowledge base")
    name: str = Field(..., description="The name of the knowledge base")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the knowledge base")
    usage_mode: Literal["prompt", "auto"] | None = Field('auto', description="The usage mode of the knowledge base")

class LanguageDetectionToolConfig(PermissiveModel):
    system_tool_type: Literal["language_detection"] | None = 'language_detection'

class LanguageDetectionToolResultModel(PermissiveModel):
    result_type: Literal["language_detection_success"] | None = 'language_detection_success'
    status: Literal["success"] | None = 'success'
    reason: str | None = None
    language: str | None = None

class LanguagePresetTranslation(PermissiveModel):
    source_hash: str
    text: str

class ListAssetsParams(PermissiveModel):
    list_kwargs: dict[str, Any] | None = None
    smb_tool_type: Literal["list_assets"] | None = 'list_assets'

class ListCalendarEventsParams(PermissiveModel):
    smb_tool_type: Literal["list_calendar_events"] | None = 'list_calendar_events'

class ListClientsParams(PermissiveModel):
    """List clients ordered by most recently updated, with an optional limit."""
    smb_tool_type: Literal["list_clients"] | None = 'list_clients'

class ListProductsParams(PermissiveModel):
    list_kwargs: dict[str, Any] | None = None
    smb_tool_type: Literal["list_products"] | None = 'list_products'

class ListRentalServicesParams(PermissiveModel):
    list_kwargs: dict[str, Any] | None = None
    smb_tool_type: Literal["list_rental_services"] | None = 'list_rental_services'

class ListServicesParams(PermissiveModel):
    list_kwargs: dict[str, Any] | None = None
    smb_tool_type: Literal["list_services"] | None = 'list_services'

class ListStaffParams(PermissiveModel):
    list_kwargs: dict[str, Any] | None = None
    smb_tool_type: Literal["list_staff"] | None = 'list_staff'

class LiteralJsonSchemaProperty(PermissiveModel):
    """Schema property for literal JSON types. IMPORTANT: Only ONE of the following fields can be set: description (LLM provides value), dynamic_variable (value from variable), is_system_provided (system provides value), or constant_value (fixed value). These are mutually exclusive."""
    type_: Literal["boolean", "string", "integer", "number"] = Field(..., validation_alias="type", serialization_alias="type")
    description: str | None = Field('', description="The description of the property. When set, the LLM will provide the value based on this description. Mutually exclusive with dynamic_variable, is_system_provided, and constant_value.")
    enum: list[str] | None = Field(None, description="List of allowed string values for string type parameters")
    is_system_provided: bool | None = Field(False, description="If true, the value will be populated by the system at runtime. Used by API Integration Webhook tools for templating. Mutually exclusive with description, dynamic_variable, and constant_value.")
    dynamic_variable: str | None = Field('', description="The name of the dynamic variable to use for this property's value. Mutually exclusive with description, is_system_provided, and constant_value.")
    constant_value: str | int | float | bool | None = Field(None, description="A constant value to use for this property. Mutually exclusive with description, dynamic_variable, and is_system_provided.")

class LiteralOverride(PermissiveModel):
    description: str | None = None
    dynamic_variable: str | None = None
    constant_value: str | int | float | bool | None = None

class LlmLiteralJsonSchemaProperty(PermissiveModel):
    type_: Literal["boolean", "string", "integer", "number"] = Field(..., validation_alias="type", serialization_alias="type")
    description: str = Field(..., min_length=0)
    enum: list[str] | None = Field(None, description="List of allowed string values for string type parameters")

class AstllmNodeInputV0(PermissiveModel):
    type_: Literal["llm"] | None = Field('llm', validation_alias="type", serialization_alias="type")
    value_schema: LlmLiteralJsonSchemaProperty = Field(..., description="JSON schema describing the value that the LLM should extract.")

class AstllmNodeInput(PermissiveModel):
    astllm_node_input: AstllmNodeInputV0 | AstllmNodeInputV1

class LlmParameterEvaluationStrategy(PermissiveModel):
    type_: Literal["llm"] = Field(..., validation_alias="type", serialization_alias="type")
    description: str = Field(..., description="A description of the evaluation strategy to use for the test.")

class LlmSchemaOverride(PermissiveModel):
    source: Literal["llm"] | None = 'llm'
    prompt: str | None = Field(None, description="Prompt override for the LLM. If not provided, the original schema description is used.")

class LlmTokensCategoryUsage(PermissiveModel):
    tokens: int | None = 0
    price: float | None = 0.0

class LlmInputOutputTokensUsage(PermissiveModel):
    input_: LlmTokensCategoryUsage | None = Field(None, validation_alias="input", serialization_alias="input")
    input_cache_read: LlmTokensCategoryUsage | None = None
    input_cache_write: LlmTokensCategoryUsage | None = None
    output_total: LlmTokensCategoryUsage | None = None

class LlmUsageInput(PermissiveModel):
    model_usage: Annotated[dict[str, LlmInputOutputTokensUsage], AfterValidator(_check_property_names_c4546ddd)] | None = Field(None, json_schema_extra={'propertyNames': {'type': 'string', 'enum': ['gpt-4o-mini', 'gpt-4o', 'gpt-4', 'gpt-4-turbo', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-5', 'gpt-5.1', 'gpt-5.2', 'gpt-5.2-chat-latest', 'gpt-5-mini', 'gpt-5-nano', 'gpt-3.5-turbo', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-3-pro-preview', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite-preview', 'claude-sonnet-4-5', 'claude-sonnet-4-6', 'claude-sonnet-4', 'claude-haiku-4-5', 'claude-3-7-sonnet', 'claude-3-5-sonnet', 'claude-3-5-sonnet-v1', 'claude-3-haiku', 'grok-beta', 'custom-llm', 'qwen3-4b', 'qwen3-30b-a3b', 'gpt-oss-20b', 'gpt-oss-120b', 'glm-45-air-fp8', 'gemini-2.5-flash-preview-09-2025', 'gemini-2.5-flash-lite-preview-09-2025', 'gemini-2.5-flash-preview-05-20', 'gemini-2.5-flash-preview-04-17', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.0-flash-lite-001', 'gemini-2.0-flash-001', 'gemini-1.5-flash-002', 'gemini-1.5-flash-001', 'gemini-1.5-pro-002', 'gemini-1.5-pro-001', 'claude-sonnet-4@20250514', 'claude-sonnet-4-5@20250929', 'claude-haiku-4-5@20251001', 'claude-3-7-sonnet@20250219', 'claude-3-5-sonnet@20240620', 'claude-3-5-sonnet-v2@20241022', 'claude-3-haiku@20240307', 'gpt-5-2025-08-07', 'gpt-5.1-2025-11-13', 'gpt-5.2-2025-12-11', 'gpt-5-mini-2025-08-07', 'gpt-5-nano-2025-08-07', 'gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'gpt-4.1-nano-2025-04-14', 'gpt-4o-mini-2024-07-18', 'gpt-4o-2024-11-20', 'gpt-4o-2024-08-06', 'gpt-4o-2024-05-13', 'gpt-4-0613', 'gpt-4-0314', 'gpt-4-turbo-2024-04-09', 'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-1106', 'watt-tool-8b', 'watt-tool-70b'], 'title': 'LLM', 'default': 'gemini-2.5-flash'}})

class MatchAnythingParameterEvaluationStrategy(PermissiveModel):
    type_: Literal["anything"] = Field(..., validation_alias="type", serialization_alias="type")

class McpToolApprovalHash(PermissiveModel):
    """Model for storing tool approval hashes for per-tool approval."""
    tool_name: str = Field(..., description="The name of the MCP tool")
    tool_hash: str = Field(..., description="SHA256 hash of the tool's parameters and description")
    approval_policy: Literal["auto_approved", "requires_approval"] | None = Field('requires_approval', description="The approval policy for this tool")

class McpToolConfigOverride(PermissiveModel):
    tool_name: str = Field(..., description="The name of the MCP tool")
    force_pre_tool_speech: bool | None = Field(None, description="If set, overrides the server's force_pre_tool_speech setting for this tool")
    disable_interruptions: bool | None = Field(None, description="If set, overrides the server's disable_interruptions setting for this tool")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="If set, overrides the server's tool_call_sound setting for this tool")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(None, description="If set, overrides the server's tool_call_sound_behavior setting for this tool")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(None, description="If set, overrides the server's execution_mode setting for this tool")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Dynamic variable assignments for this MCP tool")
    input_overrides: dict[str, ConstantSchemaOverride | DynamicVariableSchemaOverride | LlmSchemaOverride] | None = Field(None, description="Mapping of json path to input override configuration")

class MetricRecord(PermissiveModel):
    elapsed_time: float

class ConversationTurnMetrics(PermissiveModel):
    metrics: dict[str, MetricRecord] | None = None
    convai_asr_provider: str | None = None
    convai_tts_model: str | None = None

class OrbAvatar(PermissiveModel):
    type_: Literal["orb"] | None = Field('orb', validation_alias="type", serialization_alias="type", description="The type of the avatar")
    color_1: str | None = Field('#2792dc', description="The first color of the avatar")
    color_2: str | None = Field('#9ce6e6', description="The second color of the avatar")

class PdfExportOptions(PermissiveModel):
    include_speakers: bool | None = True
    include_timestamps: bool | None = True
    format_: Literal["pdf"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = None
    max_segment_duration_s: float | None = None
    max_segment_chars: int | None = None

class PhoneNumberDynamicVariableTransferDestination(PermissiveModel):
    type_: Literal["phone_dynamic_variable"] | None = Field('phone_dynamic_variable', validation_alias="type", serialization_alias="type")
    phone_number: str

class PhoneNumberTransferDestination(PermissiveModel):
    type_: Literal["phone"] | None = Field('phone', validation_alias="type", serialization_alias="type")
    phone_number: str

class PlayDtmfResultErrorModel(PermissiveModel):
    result_type: Literal["play_dtmf_error"] | None = 'play_dtmf_error'
    status: Literal["error"] | None = 'error'
    error: str
    details: str | None = None

class PlayDtmfResultSuccessModel(PermissiveModel):
    result_type: Literal["play_dtmf_success"] | None = 'play_dtmf_success'
    status: Literal["success"] | None = 'success'
    dtmf_tones: str
    reason: str | None = None

class PlayDtmfToolConfig(PermissiveModel):
    """Allows the agent to play DTMF tones during a phone call.

This tool can be used to interact with automated phone systems, such as
navigating phone menus, entering extensions, or inputting numeric codes."""
    system_tool_type: Literal["play_keypad_touch_tone"] | None = 'play_keypad_touch_tone'
    use_out_of_band_dtmf: bool | None = Field(True, description="If true, send DTMF tones out-of-band using RFC 4733 (useful for SIP calls only). If false, send DTMF as in-band audio tones (works for all call types).")
    suppress_turn_after_dtmf: bool | None = Field(False, description="If true, the agent will not generate further speech after playing DTMF tones. This prevents the agent's speech from interfering with IVR systems.")

class PodcastBulletinModeData(PermissiveModel):
    host_voice_id: str = Field(..., description="The ID of the host voice.")

class PodcastBulletinMode(PermissiveModel):
    type_: Literal["bulletin"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of podcast to create.")
    bulletin: PodcastBulletinModeData = Field(..., description="The voice settings for the bulletin.")

class PodcastConversationModeData(PermissiveModel):
    host_voice_id: str = Field(..., description="The ID of the host voice.")
    guest_voice_id: str = Field(..., description="The ID of the guest voice.")

class PodcastConversationMode(PermissiveModel):
    type_: Literal["conversation"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of podcast to create.")
    conversation: PodcastConversationModeData = Field(..., description="The voice settings for the conversation.")

class PodcastTextSource(PermissiveModel):
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of source to create.")
    text: str = Field(..., description="The text to create the podcast from.")

class PodcastUrlSource(PermissiveModel):
    type_: Literal["url"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of source to create.")
    url: str = Field(..., description="The URL to create the podcast from.")

class PositionInput(PermissiveModel):
    x: float | None = 0.0
    y: float | None = 0.0

class PostDialDigitsDynamicVariable(PermissiveModel):
    type_: Literal["dynamic"] | None = Field('dynamic', validation_alias="type", serialization_alias="type")
    value: str = Field(..., description="The dynamic variable name to resolve", min_length=1)

class PostDialDigitsStatic(PermissiveModel):
    type_: Literal["static"] | None = Field('static', validation_alias="type", serialization_alias="type")
    value: str = Field(..., description="DTMF digits to send after call connects (e.g., 'ww1234' for extension)", min_length=1, pattern="^[0-9*#wW]*$")

class PromptAgentApiModelOverride(PermissiveModel):
    prompt: str | None = Field(None, description="The prompt for the agent")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(None, description="The LLM to query with the prompt and the chat history. If using data residency, the LLM must be supported in the data residency environment")
    native_mcp_server_ids: list[str] | None = Field(None, description="A list of Native MCP server ids to be used by the agent")

class AgentConfigOverrideInput(PermissiveModel):
    first_message: str | None = Field(None, description="If non-empty, the first message the agent will say. If empty, the agent waits for the user to start the discussion.")
    language: str | None = Field(None, description="Language of the agent - used for ASR and TTS")
    prompt: PromptAgentApiModelOverride | None = Field(None, description="The prompt for the agent")

class PromptEvaluationCriteria(PermissiveModel):
    """An evaluation using the transcript and a prompt for a yes/no achieved answer"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for the evaluation criteria")
    name: str
    type_: Literal["prompt"] | None = Field('prompt', validation_alias="type", serialization_alias="type", description="The type of evaluation criteria")
    conversation_goal_prompt: str = Field(..., description="The prompt that the agent should use to evaluate the conversation", max_length=2000)
    use_knowledge_base: bool | None = Field(False, description="When evaluating the prompt, should the agent's knowledge base be used.")

class CreateAgentRouteBodyPlatformSettingsEvaluation(PermissiveModel):
    """Settings for evaluation"""
    criteria: list[PromptEvaluationCriteria] | None = Field(None, description="Individual criteria that the agent should be evaluated against")

class PronunciationDictionaryAliasRuleRequestModel(PermissiveModel):
    string_to_replace: str = Field(..., description="The string to replace. Must be a non-empty string.")
    case_sensitive: bool | None = Field(True, description="Whether the rule should match case-sensitively.")
    word_boundaries: bool | None = Field(True, description="Whether the rule should only match at word boundaries.")
    type_: Literal["alias"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the rule.")
    alias: str = Field(..., description="The alias for the string to be replaced.")

class PronunciationDictionaryPhonemeRuleRequestModel(PermissiveModel):
    string_to_replace: str = Field(..., description="The string to replace. Must be a non-empty string.")
    case_sensitive: bool | None = Field(True, description="Whether the rule should match case-sensitively.")
    word_boundaries: bool | None = Field(True, description="Whether the rule should only match at word boundaries.")
    type_: Literal["phoneme"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the rule.")
    phoneme: str = Field(..., description="The phoneme rule.")
    alphabet: str = Field(..., description="The alphabet to use with the phoneme rule.")

class PronunciationDictionaryVersionLocatorDbModel(PermissiveModel):
    pronunciation_dictionary_id: str
    version_id: str | None = Field(...)

class PronunciationDictionaryVersionLocatorRequestModel(PermissiveModel):
    pronunciation_dictionary_id: str = Field(..., description="The ID of the pronunciation dictionary.")
    version_id: str | None = Field(None, description="The ID of the version of the pronunciation dictionary. If not provided, the latest version will be used.")

class PydanticPronunciationDictionaryVersionLocator(PermissiveModel):
    """A locator for other documents to be able to reference a specific dictionary and it's version.
This is a pydantic version of PronunciationDictionaryVersionLocatorDBModel.
Required to ensure compat with the rest of the agent data models."""
    pronunciation_dictionary_id: str = Field(..., description="The ID of the pronunciation dictionary")
    version_id: str | None = Field(..., description="The ID of the version of the pronunciation dictionary")

class QueryOverride(PermissiveModel):
    properties: dict[str, LiteralOverride] | None = None
    required: list[str] | None = None

class QueryParamsJsonSchema(StrictModel):
    properties: dict[str, LiteralJsonSchemaProperty] = Field(..., min_length=1)
    required: list[str] | None = None

class RagChunkMetadata(PermissiveModel):
    document_id: str
    chunk_id: str
    vector_distance: float

class RagConfigWorkflowOverride(PermissiveModel):
    enabled: bool | None = None
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = None
    max_vector_distance: float | None = Field(None, description="Maximum vector distance of retrieved chunks.")
    max_documents_length: int | None = Field(None, description="Maximum total length of document chunks retrieved from RAG.")
    max_retrieved_rag_chunks_count: int | None = Field(None, description="Maximum number of RAG document chunks to initially retrieve from the vector store. These are then further filtered by vector distance and total length.")
    num_candidates: int | None = Field(None, description="Number of candidates evaluated in ANN vector search. Higher number means better results, but higher latency. Minimum recommended value is 100. If disabled, the default value is used.")
    query_rewrite_prompt_override: str | None = Field(None, description="Custom prompt for rewriting user queries before RAG retrieval. The conversation history will be automatically appended at the end. If not set, the default prompt will be used.")

class RagRetrievalInfo(PermissiveModel):
    chunks: list[RagChunkMetadata]
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"]
    retrieval_query: str
    rag_latency_secs: float

class ReferencedToolCommonModel(PermissiveModel):
    """Reference to a tool for unit test evaluation."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the tool")
    type_: Literal["system", "webhook", "client", "workflow", "api_integration_webhook", "mcp"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the tool")

class RegexParameterEvaluationStrategy(PermissiveModel):
    type_: Literal["regex"] = Field(..., validation_alias="type", serialization_alias="type")
    pattern: str = Field(..., description="A regex pattern to match the agent's response against.")

class RegionConfigRequest(PermissiveModel):
    region_id: Literal["us1", "ie1", "au1"] = Field(..., description="Region ID")
    token: str = Field(..., description="Auth Token for this region")
    edge_location: Literal["ashburn", "dublin", "frankfurt", "sao-paulo", "singapore", "sydney", "tokyo", "umatilla", "roaming"] = Field(..., description="Edge location for this region")

class RequiredConstraint(PermissiveModel):
    """A set of fields that must all be present to satisfy this constraint."""
    required: list[str]

class RequiredConstraints(PermissiveModel):
    """Wrapper for anyOf/allOf composition constraints scoped to required fields."""
    any_of: list[RequiredConstraint] | None = None
    all_of: list[RequiredConstraint] | None = None

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables(PermissiveModel):
    """Configuration for dynamic variables"""
    dynamic_variable_placeholders: dict[str, str | float | int | bool] | None = Field(None, description="A dictionary of dynamic variable placeholders and their values")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm(PermissiveModel):
    """Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'"""
    url: str = Field(..., description="The URL of the Chat Completions compatible endpoint")
    model_id: str | None = Field(None, description="The model ID to be used if URL serves multiple models")
    api_key: ConvAiSecretLocator | ConvAiEnvVarLocator | None = Field(None, description="The API key for authentication. Either a workspace secret reference {'secret_id': '...'} or an environment variable reference {'env_var_label': '...'}.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(None, description="Headers that should be included in the request")
    api_version: str | None = Field(None, description="The API version to use for the request")
    api_type: Literal["chat_completions", "responses"] | None = Field('chat_completions', description="The API type to use (chat_completions or responses)")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag(PermissiveModel):
    """Configuration for RAG"""
    enabled: bool | None = False
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = 'e5_mistral_7b_instruct'
    max_vector_distance: float | None = Field(0.6, description="Maximum vector distance of retrieved chunks.", gt=0.0, lt=1.0)
    max_documents_length: int | None = Field(50000, description="Maximum total length of document chunks retrieved from RAG.", gt=0, lt=10000000)
    max_retrieved_rag_chunks_count: int | None = Field(20, description="Maximum number of RAG document chunks to initially retrieve from the vector store. These are then further filtered by vector distance and total length.", le=20, gt=0)
    num_candidates: int | None = Field(None, description="Number of candidates evaluated in ANN vector search. Higher number means better results, but higher latency. Minimum recommended value is 100. If disabled, the default value is used.", le=10000, gt=0)
    query_rewrite_prompt_override: str | None = Field(None, description="Custom prompt for rewriting user queries before RAG retrieval. The conversation history will be automatically appended at the end. If not set, the default prompt will be used.", min_length=1, max_length=1000)

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAsr(PermissiveModel):
    """Configuration for conversational transcription"""
    quality: Literal["high"] | None = Field('high', description="The quality of the transcription")
    provider: Literal["elevenlabs", "scribe_realtime"] | None = Field('elevenlabs', description="The provider of the transcription service")
    user_input_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The format of the audio to be transcribed")
    keywords: list[str] | None = Field(None, description="Keywords to boost prediction probability for")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigConversation(PermissiveModel):
    """Configuration for conversational events"""
    text_only: bool | None = Field(False, description="If enabled audio will not be processed and only text will be used, use to avoid audio pricing.")
    max_duration_seconds: int | None = Field(600, description="The maximum duration of a conversation in seconds")
    client_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to the client")
    monitoring_enabled: bool | None = Field(False, description="Enable real-time monitoring of conversations via WebSocket")
    monitoring_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to monitoring connections.")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig(PermissiveModel):
    """Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses."""
    timeout_seconds: float | None = Field(-1.0, description="Time in seconds before showing the predefined message while waiting for LLM response. Set to -1 to disable.")
    message: str | None = Field('Hhmmmm...yeah.', description="Message to show when soft timeout is reached while waiting for LLM response", min_length=1, max_length=200)
    use_llm_generated_message: bool | None = Field(False, description="If enabled, the soft timeout message will be generated dynamically instead of using the static message.")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurn(PermissiveModel):
    """Configuration for turn detection"""
    turn_timeout: float | None = Field(7.0, description="Maximum wait time for the user's reply before re-engaging the user")
    initial_wait_time: float | None = Field(None, description="How long the agent will wait for the user to start the conversation if the first message is empty. If not set, uses the regular turn_timeout.")
    silence_end_call_timeout: float | None = Field(-1, description="Maximum wait time since the user last spoke before terminating the call")
    soft_timeout_config: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig | None = Field(None, description="Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses.")
    mode: Literal["silence", "turn"] | None = Field('turn', description="The mode of turn detection")
    turn_eagerness: Literal["patient", "normal", "eager"] | None = Field('normal', description="Controls how eager the agent is to respond. Low = less eager (waits longer), Standard = default eagerness, High = more eager (responds sooner)")
    spelling_patience: Literal["auto", "off"] | None = Field('auto', description="Controls if the agent should be more patient when user is spelling numbers and named entities. Auto = model based, Off = never wait extra")
    speculative_turn: bool | None = Field(False, description="When enabled, starts generating LLM responses during silence before full turn confidence is reached, reducing perceived latency. May increase LLM costs.")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigVad(PermissiveModel):
    """Configuration for voice activity detection"""
    background_voice_detection: bool | None = Field(False, description="Whether to use background voice filtering")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsAuth(PermissiveModel):
    """Settings for authentication"""
    enable_auth: bool | None = Field(False, description="If set to true, starting a conversation with an agent will require a signed token")
    allowlist: list[AllowlistItem] | None = Field(None, description="A list of hosts that are allowed to start conversations with the agent")
    require_origin_header: bool | None = Field(False, description="When enabled, connections with no origin header will be rejected. If the allowlist is empty, this option has no effect.")
    shareable_token: str | None = Field(None, description="A shareable token that can be used to start a conversation with the agent")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsCallLimits(PermissiveModel):
    """Call limits for the agent"""
    agent_concurrency_limit: int | None = Field(-1, description="The maximum number of concurrent conversations. -1 indicates that there is no maximum")
    daily_limit: int | None = Field(100000, description="The maximum number of conversations per day")
    bursting_enabled: bool | None = Field(True, description="Whether to enable bursting. If true, exceeding workspace concurrency limit will be allowed up to 3 times the limit. Calls will be charged at double rate when exceeding the limit.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsEvaluation(PermissiveModel):
    """Settings for evaluation"""
    criteria: list[PromptEvaluationCriteria] | None = Field(None, description="Individual criteria that the agent should be evaluated against")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig(PermissiveModel):
    sexual: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual | None = None
    violence: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence | None = None
    harassment: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment | None = None
    self_harm: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm | None = None
    profanity: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity | None = None
    religion_or_politics: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics | None = None
    medical_and_legal_information: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus(PermissiveModel):
    is_enabled: bool | None = False

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig(PermissiveModel):
    sexual: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual | None = None
    violence: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence | None = None
    violence_graphic: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic | None = None
    harassment: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment | None = None
    harassment_threatening: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening | None = None
    hate: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate | None = None
    hate_threatening: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening | None = None
    self_harm_instructions: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions | None = None
    self_harm: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm | None = None
    self_harm_intent: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent | None = None
    sexual_minors: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection(PermissiveModel):
    is_enabled: bool | None = False

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt(PermissiveModel):
    """Configures overrides for nested fields."""
    prompt: bool | None = Field(False, description="Whether to allow overriding the prompt field.")
    llm: bool | None = Field(False, description="Whether to allow overriding the llm field.")
    native_mcp_server_ids: bool | None = Field(False, description="Whether to allow overriding the native_mcp_server_ids field.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent(PermissiveModel):
    """Configures overrides for nested fields."""
    first_message: bool | None = Field(False, description="Whether to allow overriding the first_message field.")
    language: bool | None = Field(False, description="Whether to allow overriding the language field.")
    prompt: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt | None = Field(None, description="Configures overrides for nested fields.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation(PermissiveModel):
    """Configures overrides for nested fields."""
    text_only: bool | None = Field(False, description="Whether to allow overriding the text_only field.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts(PermissiveModel):
    """Configures overrides for nested fields."""
    voice_id: bool | None = Field(False, description="Whether to allow overriding the voice_id field.")
    stability: bool | None = Field(False, description="Whether to allow overriding the stability field.")
    speed: bool | None = Field(False, description="Whether to allow overriding the speed field.")
    similarity_boost: bool | None = Field(False, description="Whether to allow overriding the similarity_boost field.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig(PermissiveModel):
    """Configures overrides for nested fields."""
    message: bool | None = Field(False, description="Whether to allow overriding the message field.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn(PermissiveModel):
    """Configures overrides for nested fields."""
    soft_timeout_config: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig | None = Field(None, description="Configures overrides for nested fields.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride(PermissiveModel):
    """Overrides for the conversation configuration"""
    turn: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn | None = Field(None, description="Configures overrides for nested fields.")
    tts: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts | None = Field(None, description="Configures overrides for nested fields.")
    conversation: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation | None = Field(None, description="Configures overrides for nested fields.")
    agent: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent | None = Field(None, description="Configures overrides for nested fields.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverrides(PermissiveModel):
    """Additional overrides for the agent during conversation initiation"""
    conversation_config_override: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride | None = Field(None, description="Overrides for the conversation configuration")
    custom_llm_extra_body: bool | None = Field(False, description="Whether to include custom LLM extra body")
    enable_conversation_initiation_client_data_from_webhook: bool | None = Field(False, description="Whether to enable conversation initiation client data from webhooks")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction(PermissiveModel):
    """Config for PII redaction in the conversation history"""
    enabled: bool | None = Field(False, description="Whether conversation history redaction is enabled")
    entities: list[Literal["name", "name.name_given", "name.name_family", "name.name_other", "email_address", "contact_number", "dob", "age", "religious_belief", "political_opinion", "sexual_orientation", "ethnicity_race", "marital_status", "occupation", "physical_attribute", "language", "username", "password", "url", "organization", "financial_id", "financial_id.payment_card", "financial_id.payment_card.payment_card_number", "financial_id.payment_card.payment_card_expiration_date", "financial_id.payment_card.payment_card_cvv", "financial_id.bank_account", "financial_id.bank_account.bank_account_number", "financial_id.bank_account.bank_routing_number", "financial_id.bank_account.swift_bic_code", "financial_id.financial_id_other", "location", "location.location_address", "location.location_city", "location.location_postal_code", "location.location_coordinate", "location.location_state", "location.location_country", "location.location_other", "date", "date_interval", "unique_id", "unique_id.government_issued_id", "unique_id.account_number", "unique_id.vehicle_id", "unique_id.healthcare_number", "unique_id.healthcare_number.medical_record_number", "unique_id.healthcare_number.health_plan_beneficiary_number", "unique_id.device_id", "unique_id.unique_id_other", "medical", "medical.medical_condition", "medical.medication", "medical.medical_procedure", "medical.medical_measurement", "medical.medical_other"]] | None = Field(None, description="The entities to redact from the conversation transcript, audio and analysis. Use top-level types like 'name', 'email_address', or dot notation for specific subtypes like 'name.full_name'.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacy(PermissiveModel):
    """Privacy settings for the agent"""
    record_voice: bool | None = Field(True, description="Whether to record the conversation")
    retention_days: int | None = Field(-1, description="The number of days to retain the conversation. -1 indicates there is no retention limit")
    delete_transcript_and_pii: bool | None = Field(False, description="Whether to delete the transcript and PII")
    delete_audio: bool | None = Field(False, description="Whether to delete the audio")
    apply_to_existing_conversations: bool | None = Field(False, description="Whether to apply the privacy settings to existing conversations")
    zero_retention_mode: bool | None = Field(False, description="Whether to enable zero retention mode - no PII data is stored")
    conversation_history_redaction: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction | None = Field(None, description="Config for PII redaction in the conversation history")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsTesting(PermissiveModel):
    """Testing configuration for the agent"""
    attached_tests: list[AttachedTestModel] | None = Field(None, description="List of test IDs that should be run for this agent", min_length=0, max_length=1000)

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback(PermissiveModel):
    """Configuration for feedback collected at the end of the conversation"""
    type_: Literal["rating"] | None = Field('rating', validation_alias="type", serialization_alias="type", description="The type of feedback to collect at the end of the conversation")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles(PermissiveModel):
    """Styles for the widget"""
    base: str | None = Field(None, description="The base background color.")
    base_hover: str | None = Field(None, description="The color of the base background when hovered.")
    base_active: str | None = Field(None, description="The color of the base background when active (clicked).")
    base_border: str | None = Field(None, description="The color of the border against the base background.")
    base_subtle: str | None = Field(None, description="The color of subtle text against the base background.")
    base_primary: str | None = Field(None, description="The color of primary text against the base background.")
    base_error: str | None = Field(None, description="The color of error text against the base background.")
    accent: str | None = Field(None, description="The accent background color.")
    accent_hover: str | None = Field(None, description="The color of the accent background when hovered.")
    accent_active: str | None = Field(None, description="The color of the accent background when active (clicked).")
    accent_border: str | None = Field(None, description="The color of the border against the accent background.")
    accent_subtle: str | None = Field(None, description="The color of subtle text against the accent background.")
    accent_primary: str | None = Field(None, description="The color of primary text against the accent background.")
    overlay_padding: float | None = Field(None, description="The padding around the edges of the viewport.")
    button_radius: float | None = Field(None, description="The radius of the buttons.")
    input_radius: float | None = Field(None, description="The radius of the input fields.")
    bubble_radius: float | None = Field(None, description="The radius of the chat bubbles.")
    sheet_radius: float | None = Field(None, description="The default radius of sheets.")
    compact_sheet_radius: float | None = Field(None, description="The radius of the sheet in compact mode.")
    dropdown_sheet_radius: float | None = Field(None, description="The radius of the dropdown sheet.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents(PermissiveModel):
    """Text contents of the widget"""
    main_label: str | None = Field(None, description="Call to action displayed inside the compact and full variants.")
    start_call: str | None = Field(None, description="Text and ARIA label for the start call button.")
    start_chat: str | None = Field(None, description="Text and ARIA label for the start chat button (text only)")
    new_call: str | None = Field(None, description="Text and ARIA label for the new call button. Displayed when the caller already finished at least one call in order ot start the next one.")
    end_call: str | None = Field(None, description="Text and ARIA label for the end call button.")
    mute_microphone: str | None = Field(None, description="ARIA label for the mute microphone button.")
    change_language: str | None = Field(None, description="ARIA label for the change language dropdown.")
    collapse: str | None = Field(None, description="ARIA label for the collapse button.")
    expand: str | None = Field(None, description="ARIA label for the expand button.")
    copied: str | None = Field(None, description="Text displayed when the user copies a value using the copy button.")
    accept_terms: str | None = Field(None, description="Text and ARIA label for the accept terms button.")
    dismiss_terms: str | None = Field(None, description="Text and ARIA label for the cancel terms button.")
    listening_status: str | None = Field(None, description="Status displayed when the agent is listening.")
    speaking_status: str | None = Field(None, description="Status displayed when the agent is speaking.")
    connecting_status: str | None = Field(None, description="Status displayed when the agent is connecting.")
    chatting_status: str | None = Field(None, description="Status displayed when the agent is chatting (text only)")
    input_label: str | None = Field(None, description="ARIA label for the text message input.")
    input_placeholder: str | None = Field(None, description="Placeholder text for the text message input.")
    input_placeholder_text_only: str | None = Field(None, description="Placeholder text for the text message input (text only)")
    input_placeholder_new_conversation: str | None = Field(None, description="Placeholder text for the text message input when starting a new conversation (text only)")
    user_ended_conversation: str | None = Field(None, description="Information message displayed when the user ends the conversation.")
    agent_ended_conversation: str | None = Field(None, description="Information message displayed when the agent ends the conversation.")
    conversation_id: str | None = Field(None, description="Text label used next to the conversation ID.")
    error_occurred: str | None = Field(None, description="Text label used when an error occurs.")
    copy_id: str | None = Field(None, description="Text and ARIA label used for the copy ID button.")
    initiate_feedback: str | None = Field(None, description="Text displayed to prompt the user for feedback.")
    request_follow_up_feedback: str | None = Field(None, description="Text displayed to request additional feedback details.")
    thanks_for_feedback: str | None = Field(None, description="Text displayed to thank the user for providing feedback.")
    thanks_for_feedback_details: str | None = Field(None, description="Additional text displayed explaining the value of user feedback.")
    follow_up_feedback_placeholder: str | None = Field(None, description="Placeholder text for the follow-up feedback input field.")
    submit: str | None = Field(None, description="Text and ARIA label for the submit button.")
    go_back: str | None = Field(None, description="Text and ARIA label for the go back button.")
    send_message: str | None = Field(None, description="Text and ARIA label for the send message button.")
    text_mode: str | None = Field(None, description="Text and ARIA label for the switch to text mode button.")
    voice_mode: str | None = Field(None, description="Text and ARIA label for the switch to voice mode button.")
    switched_to_text_mode: str | None = Field(None, description="Toast notification displayed when switching to text mode.")
    switched_to_voice_mode: str | None = Field(None, description="Toast notification displayed when switching to voice mode.")
    copy_: str | None = Field(None, validation_alias="copy", serialization_alias="copy", description="Text and ARIA label for the copy button.")
    download: str | None = Field(None, description="Text and ARIA label for the download button.")
    wrap: str | None = Field(None, description="Text and ARIA label for the wrap toggle button.")
    agent_working: str | None = Field(None, description="Status text displayed when the agent is processing a tool call.")
    agent_done: str | None = Field(None, description="Status text displayed when the agent finishes processing a tool call.")
    agent_error: str | None = Field(None, description="Status text displayed when the agent encounters an error during a tool call.")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook(PermissiveModel):
    """The webhook to send conversation initiation client data to"""
    url: str = Field(..., description="The URL to send the webhook to")
    request_headers: dict[str, str | ConvAiSecretLocator] = Field(..., description="The headers to send with the webhook request")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks(PermissiveModel):
    post_call_webhook_id: str | None = None
    events: list[Literal["transcript", "audio", "call_initiation_failure"]] | None = Field(None, description="List of event types to send via webhook. Options: transcript, audio, call_initiation_failure.")
    send_audio: bool | None = Field(None, description="DEPRECATED: Use 'events' field instead. Whether to send audio data with post-call webhooks for ConvAI conversations")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides(PermissiveModel):
    """Workspace overrides for the agent"""
    conversation_initiation_client_data_webhook: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook | None = Field(None, description="The webhook to send conversation initiation client data to")
    webhooks: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks | None = None

class RetryTriggerAction(PermissiveModel):
    type_: Literal["retry"] | None = Field('retry', validation_alias="type", serialization_alias="type")
    feedback: str | None = Field('Your response was blocked by a guardrail that blocks content that matches this condition/category: \'{{trigger_reason}}\' During your next turn you must tell the user "I\'m sorry but I can\'t answer that question, would you like to know something else?".', description="Custom feedback to inject into the agent when retrying after guardrail trigger.")

class CreateAgentRouteBodyPlatformSettingsGuardrailsContent(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfig | None = None
    trigger_action: EndCallTriggerAction | RetryTriggerAction | None = None

class CustomGuardrailConfig(PermissiveModel):
    """Single custom guardrail configuration"""
    is_enabled: bool | None = False
    name: str = Field(..., description="User-facing name for this guardrail", min_length=1, max_length=500)
    prompt: str = Field(..., description="Instruction describing what to block, e.g. 'don't talk about politics'", min_length=1, max_length=10000)
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    trigger_action: EndCallTriggerAction | RetryTriggerAction | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsCustomConfig(PermissiveModel):
    """Config container for custom guardrails list"""
    configs: list[CustomGuardrailConfig] | None = None

class CreateAgentRouteBodyPlatformSettingsGuardrailsCustom(PermissiveModel):
    """Container for custom guardrails, matching ModerationGuardrail pattern"""
    config: CreateAgentRouteBodyPlatformSettingsGuardrailsCustomConfig | None = Field(None, description="Config container for custom guardrails list")

class CreateAgentRouteBodyPlatformSettingsGuardrails(PermissiveModel):
    """Guardrails configuration for the agent"""
    version: Literal["1"] | None = '1'
    focus: CreateAgentRouteBodyPlatformSettingsGuardrailsFocus | None = None
    prompt_injection: CreateAgentRouteBodyPlatformSettingsGuardrailsPromptInjection | None = None
    content: CreateAgentRouteBodyPlatformSettingsGuardrailsContent | None = None
    moderation: CreateAgentRouteBodyPlatformSettingsGuardrailsModeration | None = None
    custom: CreateAgentRouteBodyPlatformSettingsGuardrailsCustom | None = Field(None, description="Container for custom guardrails, matching ModerationGuardrail pattern")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig | None = None
    trigger_action: EndCallTriggerAction | RetryTriggerAction | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig(PermissiveModel):
    """Config container for custom guardrails list"""
    configs: list[CustomGuardrailConfig] | None = None

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom(PermissiveModel):
    """Container for custom guardrails, matching ModerationGuardrail pattern"""
    config: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig | None = Field(None, description="Config container for custom guardrails list")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrails(PermissiveModel):
    """Guardrails configuration for the agent"""
    version: Literal["1"] | None = '1'
    focus: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus | None = None
    prompt_injection: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection | None = None
    content: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent | None = None
    moderation: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration | None = None
    custom: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom | None = Field(None, description="Container for custom guardrails, matching ModerationGuardrail pattern")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables(PermissiveModel):
    """Configuration for dynamic variables"""
    dynamic_variable_placeholders: dict[str, str | float | int | bool] | None = Field(None, description="A dictionary of dynamic variable placeholders and their values")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm(PermissiveModel):
    """Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'"""
    url: str = Field(..., description="The URL of the Chat Completions compatible endpoint")
    model_id: str | None = Field(None, description="The model ID to be used if URL serves multiple models")
    api_key: ConvAiSecretLocator | ConvAiEnvVarLocator | None = Field(None, description="The API key for authentication. Either a workspace secret reference {'secret_id': '...'} or an environment variable reference {'env_var_label': '...'}.")
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(None, description="Headers that should be included in the request")
    api_version: str | None = Field(None, description="The API version to use for the request")
    api_type: Literal["chat_completions", "responses"] | None = Field('chat_completions', description="The API type to use (chat_completions or responses)")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag(PermissiveModel):
    """Configuration for RAG"""
    enabled: bool | None = False
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = 'e5_mistral_7b_instruct'
    max_vector_distance: float | None = Field(0.6, description="Maximum vector distance of retrieved chunks.", gt=0.0, lt=1.0)
    max_documents_length: int | None = Field(50000, description="Maximum total length of document chunks retrieved from RAG.", gt=0, lt=10000000)
    max_retrieved_rag_chunks_count: int | None = Field(20, description="Maximum number of RAG document chunks to initially retrieve from the vector store. These are then further filtered by vector distance and total length.", le=20, gt=0)
    num_candidates: int | None = Field(None, description="Number of candidates evaluated in ANN vector search. Higher number means better results, but higher latency. Minimum recommended value is 100. If disabled, the default value is used.", le=10000, gt=0)
    query_rewrite_prompt_override: str | None = Field(None, description="Custom prompt for rewriting user queries before RAG retrieval. The conversation history will be automatically appended at the end. If not set, the default prompt will be used.", min_length=1, max_length=1000)

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAsr(PermissiveModel):
    """Configuration for conversational transcription"""
    quality: Literal["high"] | None = Field('high', description="The quality of the transcription")
    provider: Literal["elevenlabs", "scribe_realtime"] | None = Field('elevenlabs', description="The provider of the transcription service")
    user_input_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The format of the audio to be transcribed")
    keywords: list[str] | None = Field(None, description="Keywords to boost prediction probability for")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigConversation(PermissiveModel):
    """Configuration for conversational events"""
    text_only: bool | None = Field(False, description="If enabled audio will not be processed and only text will be used, use to avoid audio pricing.")
    max_duration_seconds: int | None = Field(600, description="The maximum duration of a conversation in seconds")
    client_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to the client")
    monitoring_enabled: bool | None = Field(False, description="Enable real-time monitoring of conversations via WebSocket")
    monitoring_events: list[Literal["conversation_initiation_metadata", "asr_initiation_metadata", "ping", "audio", "interruption", "user_transcript", "tentative_user_transcript", "agent_response", "agent_response_correction", "client_tool_call", "mcp_tool_call", "mcp_connection_status", "agent_tool_request", "agent_tool_response", "agent_response_metadata", "vad_score", "agent_chat_response_part", "client_error", "guardrail_triggered", "internal_turn_probability", "internal_tentative_agent_response"]] | None = Field(None, description="The events that will be sent to monitoring connections.")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig(PermissiveModel):
    """Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses."""
    timeout_seconds: float | None = Field(-1.0, description="Time in seconds before showing the predefined message while waiting for LLM response. Set to -1 to disable.")
    message: str | None = Field('Hhmmmm...yeah.', description="Message to show when soft timeout is reached while waiting for LLM response", min_length=1, max_length=200)
    use_llm_generated_message: bool | None = Field(False, description="If enabled, the soft timeout message will be generated dynamically instead of using the static message.")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurn(PermissiveModel):
    """Configuration for turn detection"""
    turn_timeout: float | None = Field(7.0, description="Maximum wait time for the user's reply before re-engaging the user")
    initial_wait_time: float | None = Field(None, description="How long the agent will wait for the user to start the conversation if the first message is empty. If not set, uses the regular turn_timeout.")
    silence_end_call_timeout: float | None = Field(-1, description="Maximum wait time since the user last spoke before terminating the call")
    soft_timeout_config: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig | None = Field(None, description="Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses.")
    mode: Literal["silence", "turn"] | None = Field('turn', description="The mode of turn detection")
    turn_eagerness: Literal["patient", "normal", "eager"] | None = Field('normal', description="Controls how eager the agent is to respond. Low = less eager (waits longer), Standard = default eagerness, High = more eager (responds sooner)")
    spelling_patience: Literal["auto", "off"] | None = Field('auto', description="Controls if the agent should be more patient when user is spelling numbers and named entities. Auto = model based, Off = never wait extra")
    speculative_turn: bool | None = Field(False, description="When enabled, starts generating LLM responses during silence before full turn confidence is reached, reducing perceived latency. May increase LLM costs.")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigVad(PermissiveModel):
    """Configuration for voice activity detection"""
    background_voice_detection: bool | None = Field(False, description="Whether to use background voice filtering")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsAuth(PermissiveModel):
    """Settings for authentication"""
    enable_auth: bool | None = Field(False, description="If set to true, starting a conversation with an agent will require a signed token")
    allowlist: list[AllowlistItem] | None = Field(None, description="A list of hosts that are allowed to start conversations with the agent")
    require_origin_header: bool | None = Field(False, description="When enabled, connections with no origin header will be rejected. If the allowlist is empty, this option has no effect.")
    shareable_token: str | None = Field(None, description="A shareable token that can be used to start a conversation with the agent")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsCallLimits(PermissiveModel):
    """Call limits for the agent"""
    agent_concurrency_limit: int | None = Field(-1, description="The maximum number of concurrent conversations. -1 indicates that there is no maximum")
    daily_limit: int | None = Field(100000, description="The maximum number of conversations per day")
    bursting_enabled: bool | None = Field(True, description="Whether to enable bursting. If true, exceeding workspace concurrency limit will be allowed up to 3 times the limit. Calls will be charged at double rate when exceeding the limit.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsEvaluation(PermissiveModel):
    """Settings for evaluation"""
    criteria: list[PromptEvaluationCriteria] | None = Field(None, description="Individual criteria that the agent should be evaluated against")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | Literal["low", "medium", "high"] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig(PermissiveModel):
    sexual: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual | None = None
    violence: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence | None = None
    harassment: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment | None = None
    self_harm: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm | None = None
    profanity: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity | None = None
    religion_or_politics: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics | None = None
    medical_and_legal_information: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig | None = None
    trigger_action: EndCallTriggerAction | RetryTriggerAction | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig(PermissiveModel):
    """Config container for custom guardrails list"""
    configs: list[CustomGuardrailConfig] | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom(PermissiveModel):
    """Container for custom guardrails, matching ModerationGuardrail pattern"""
    config: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig | None = Field(None, description="Config container for custom guardrails list")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus(PermissiveModel):
    is_enabled: bool | None = False

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic(PermissiveModel):
    is_enabled: bool | None = False
    threshold: float | None = Field(0.3, ge=0.0, le=1.0)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig(PermissiveModel):
    sexual: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual | None = None
    violence: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence | None = None
    violence_graphic: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic | None = None
    harassment: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment | None = None
    harassment_threatening: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening | None = None
    hate: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate | None = None
    hate_threatening: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening | None = None
    self_harm_instructions: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions | None = None
    self_harm: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm | None = None
    self_harm_intent: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent | None = None
    sexual_minors: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration(PermissiveModel):
    execution_mode: Literal["streaming", "blocking"] | None = 'streaming'
    config: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection(PermissiveModel):
    is_enabled: bool | None = False

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrails(PermissiveModel):
    """Guardrails configuration for the agent"""
    version: Literal["1"] | None = '1'
    focus: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus | None = None
    prompt_injection: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection | None = None
    content: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent | None = None
    moderation: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration | None = None
    custom: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom | None = Field(None, description="Container for custom guardrails, matching ModerationGuardrail pattern")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt(PermissiveModel):
    """Configures overrides for nested fields."""
    prompt: bool | None = Field(False, description="Whether to allow overriding the prompt field.")
    llm: bool | None = Field(False, description="Whether to allow overriding the llm field.")
    native_mcp_server_ids: bool | None = Field(False, description="Whether to allow overriding the native_mcp_server_ids field.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent(PermissiveModel):
    """Configures overrides for nested fields."""
    first_message: bool | None = Field(False, description="Whether to allow overriding the first_message field.")
    language: bool | None = Field(False, description="Whether to allow overriding the language field.")
    prompt: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt | None = Field(None, description="Configures overrides for nested fields.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation(PermissiveModel):
    """Configures overrides for nested fields."""
    text_only: bool | None = Field(False, description="Whether to allow overriding the text_only field.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts(PermissiveModel):
    """Configures overrides for nested fields."""
    voice_id: bool | None = Field(False, description="Whether to allow overriding the voice_id field.")
    stability: bool | None = Field(False, description="Whether to allow overriding the stability field.")
    speed: bool | None = Field(False, description="Whether to allow overriding the speed field.")
    similarity_boost: bool | None = Field(False, description="Whether to allow overriding the similarity_boost field.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig(PermissiveModel):
    """Configures overrides for nested fields."""
    message: bool | None = Field(False, description="Whether to allow overriding the message field.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn(PermissiveModel):
    """Configures overrides for nested fields."""
    soft_timeout_config: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig | None = Field(None, description="Configures overrides for nested fields.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride(PermissiveModel):
    """Overrides for the conversation configuration"""
    turn: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn | None = Field(None, description="Configures overrides for nested fields.")
    tts: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts | None = Field(None, description="Configures overrides for nested fields.")
    conversation: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation | None = Field(None, description="Configures overrides for nested fields.")
    agent: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent | None = Field(None, description="Configures overrides for nested fields.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverrides(PermissiveModel):
    """Additional overrides for the agent during conversation initiation"""
    conversation_config_override: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride | None = Field(None, description="Overrides for the conversation configuration")
    custom_llm_extra_body: bool | None = Field(False, description="Whether to include custom LLM extra body")
    enable_conversation_initiation_client_data_from_webhook: bool | None = Field(False, description="Whether to enable conversation initiation client data from webhooks")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction(PermissiveModel):
    """Config for PII redaction in the conversation history"""
    enabled: bool | None = Field(False, description="Whether conversation history redaction is enabled")
    entities: list[Literal["name", "name.name_given", "name.name_family", "name.name_other", "email_address", "contact_number", "dob", "age", "religious_belief", "political_opinion", "sexual_orientation", "ethnicity_race", "marital_status", "occupation", "physical_attribute", "language", "username", "password", "url", "organization", "financial_id", "financial_id.payment_card", "financial_id.payment_card.payment_card_number", "financial_id.payment_card.payment_card_expiration_date", "financial_id.payment_card.payment_card_cvv", "financial_id.bank_account", "financial_id.bank_account.bank_account_number", "financial_id.bank_account.bank_routing_number", "financial_id.bank_account.swift_bic_code", "financial_id.financial_id_other", "location", "location.location_address", "location.location_city", "location.location_postal_code", "location.location_coordinate", "location.location_state", "location.location_country", "location.location_other", "date", "date_interval", "unique_id", "unique_id.government_issued_id", "unique_id.account_number", "unique_id.vehicle_id", "unique_id.healthcare_number", "unique_id.healthcare_number.medical_record_number", "unique_id.healthcare_number.health_plan_beneficiary_number", "unique_id.device_id", "unique_id.unique_id_other", "medical", "medical.medical_condition", "medical.medication", "medical.medical_procedure", "medical.medical_measurement", "medical.medical_other"]] | None = Field(None, description="The entities to redact from the conversation transcript, audio and analysis. Use top-level types like 'name', 'email_address', or dot notation for specific subtypes like 'name.full_name'.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacy(PermissiveModel):
    """Privacy settings for the agent"""
    record_voice: bool | None = Field(True, description="Whether to record the conversation")
    retention_days: int | None = Field(-1, description="The number of days to retain the conversation. -1 indicates there is no retention limit")
    delete_transcript_and_pii: bool | None = Field(False, description="Whether to delete the transcript and PII")
    delete_audio: bool | None = Field(False, description="Whether to delete the audio")
    apply_to_existing_conversations: bool | None = Field(False, description="Whether to apply the privacy settings to existing conversations")
    zero_retention_mode: bool | None = Field(False, description="Whether to enable zero retention mode - no PII data is stored")
    conversation_history_redaction: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction | None = Field(None, description="Config for PII redaction in the conversation history")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsTesting(PermissiveModel):
    """Testing configuration for the agent"""
    attached_tests: list[AttachedTestModel] | None = Field(None, description="List of test IDs that should be run for this agent", min_length=0, max_length=1000)

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback(PermissiveModel):
    """Configuration for feedback collected at the end of the conversation"""
    type_: Literal["rating"] | None = Field('rating', validation_alias="type", serialization_alias="type", description="The type of feedback to collect at the end of the conversation")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles(PermissiveModel):
    """Styles for the widget"""
    base: str | None = Field(None, description="The base background color.")
    base_hover: str | None = Field(None, description="The color of the base background when hovered.")
    base_active: str | None = Field(None, description="The color of the base background when active (clicked).")
    base_border: str | None = Field(None, description="The color of the border against the base background.")
    base_subtle: str | None = Field(None, description="The color of subtle text against the base background.")
    base_primary: str | None = Field(None, description="The color of primary text against the base background.")
    base_error: str | None = Field(None, description="The color of error text against the base background.")
    accent: str | None = Field(None, description="The accent background color.")
    accent_hover: str | None = Field(None, description="The color of the accent background when hovered.")
    accent_active: str | None = Field(None, description="The color of the accent background when active (clicked).")
    accent_border: str | None = Field(None, description="The color of the border against the accent background.")
    accent_subtle: str | None = Field(None, description="The color of subtle text against the accent background.")
    accent_primary: str | None = Field(None, description="The color of primary text against the accent background.")
    overlay_padding: float | None = Field(None, description="The padding around the edges of the viewport.")
    button_radius: float | None = Field(None, description="The radius of the buttons.")
    input_radius: float | None = Field(None, description="The radius of the input fields.")
    bubble_radius: float | None = Field(None, description="The radius of the chat bubbles.")
    sheet_radius: float | None = Field(None, description="The default radius of sheets.")
    compact_sheet_radius: float | None = Field(None, description="The radius of the sheet in compact mode.")
    dropdown_sheet_radius: float | None = Field(None, description="The radius of the dropdown sheet.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents(PermissiveModel):
    """Text contents of the widget"""
    main_label: str | None = Field(None, description="Call to action displayed inside the compact and full variants.")
    start_call: str | None = Field(None, description="Text and ARIA label for the start call button.")
    start_chat: str | None = Field(None, description="Text and ARIA label for the start chat button (text only)")
    new_call: str | None = Field(None, description="Text and ARIA label for the new call button. Displayed when the caller already finished at least one call in order ot start the next one.")
    end_call: str | None = Field(None, description="Text and ARIA label for the end call button.")
    mute_microphone: str | None = Field(None, description="ARIA label for the mute microphone button.")
    change_language: str | None = Field(None, description="ARIA label for the change language dropdown.")
    collapse: str | None = Field(None, description="ARIA label for the collapse button.")
    expand: str | None = Field(None, description="ARIA label for the expand button.")
    copied: str | None = Field(None, description="Text displayed when the user copies a value using the copy button.")
    accept_terms: str | None = Field(None, description="Text and ARIA label for the accept terms button.")
    dismiss_terms: str | None = Field(None, description="Text and ARIA label for the cancel terms button.")
    listening_status: str | None = Field(None, description="Status displayed when the agent is listening.")
    speaking_status: str | None = Field(None, description="Status displayed when the agent is speaking.")
    connecting_status: str | None = Field(None, description="Status displayed when the agent is connecting.")
    chatting_status: str | None = Field(None, description="Status displayed when the agent is chatting (text only)")
    input_label: str | None = Field(None, description="ARIA label for the text message input.")
    input_placeholder: str | None = Field(None, description="Placeholder text for the text message input.")
    input_placeholder_text_only: str | None = Field(None, description="Placeholder text for the text message input (text only)")
    input_placeholder_new_conversation: str | None = Field(None, description="Placeholder text for the text message input when starting a new conversation (text only)")
    user_ended_conversation: str | None = Field(None, description="Information message displayed when the user ends the conversation.")
    agent_ended_conversation: str | None = Field(None, description="Information message displayed when the agent ends the conversation.")
    conversation_id: str | None = Field(None, description="Text label used next to the conversation ID.")
    error_occurred: str | None = Field(None, description="Text label used when an error occurs.")
    copy_id: str | None = Field(None, description="Text and ARIA label used for the copy ID button.")
    initiate_feedback: str | None = Field(None, description="Text displayed to prompt the user for feedback.")
    request_follow_up_feedback: str | None = Field(None, description="Text displayed to request additional feedback details.")
    thanks_for_feedback: str | None = Field(None, description="Text displayed to thank the user for providing feedback.")
    thanks_for_feedback_details: str | None = Field(None, description="Additional text displayed explaining the value of user feedback.")
    follow_up_feedback_placeholder: str | None = Field(None, description="Placeholder text for the follow-up feedback input field.")
    submit: str | None = Field(None, description="Text and ARIA label for the submit button.")
    go_back: str | None = Field(None, description="Text and ARIA label for the go back button.")
    send_message: str | None = Field(None, description="Text and ARIA label for the send message button.")
    text_mode: str | None = Field(None, description="Text and ARIA label for the switch to text mode button.")
    voice_mode: str | None = Field(None, description="Text and ARIA label for the switch to voice mode button.")
    switched_to_text_mode: str | None = Field(None, description="Toast notification displayed when switching to text mode.")
    switched_to_voice_mode: str | None = Field(None, description="Toast notification displayed when switching to voice mode.")
    copy_: str | None = Field(None, validation_alias="copy", serialization_alias="copy", description="Text and ARIA label for the copy button.")
    download: str | None = Field(None, description="Text and ARIA label for the download button.")
    wrap: str | None = Field(None, description="Text and ARIA label for the wrap toggle button.")
    agent_working: str | None = Field(None, description="Status text displayed when the agent is processing a tool call.")
    agent_done: str | None = Field(None, description="Status text displayed when the agent finishes processing a tool call.")
    agent_error: str | None = Field(None, description="Status text displayed when the agent encounters an error during a tool call.")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook(PermissiveModel):
    """The webhook to send conversation initiation client data to"""
    url: str = Field(..., description="The URL to send the webhook to")
    request_headers: dict[str, str | ConvAiSecretLocator] = Field(..., description="The headers to send with the webhook request")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks(PermissiveModel):
    post_call_webhook_id: str | None = None
    events: list[Literal["transcript", "audio", "call_initiation_failure"]] | None = Field(None, description="List of event types to send via webhook. Options: transcript, audio, call_initiation_failure.")
    send_audio: bool | None = Field(None, description="DEPRECATED: Use 'events' field instead. Whether to send audio data with post-call webhooks for ConvAI conversations")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides(PermissiveModel):
    """Workspace overrides for the agent"""
    conversation_initiation_client_data_webhook: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook | None = Field(None, description="The webhook to send conversation initiation client data to")
    webhooks: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks | None = None

class SearchClientsParams(PermissiveModel):
    """Search for clients by name, phone number, or email."""
    smb_tool_type: Literal["search_clients"] | None = 'search_clients'

class SegmentedJsonExportOptions(PermissiveModel):
    include_speakers: bool | None = True
    include_timestamps: bool | None = True
    format_: Literal["segmented_json"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = None
    max_segment_duration_s: float | None = None
    max_segment_chars: int | None = None

class SingleTestRunRequestModel(PermissiveModel):
    test_id: str = Field(..., description="ID of the test to run")
    workflow_node_id: str | None = Field(None, description="ID of the workflow node to run the test on. If not provided, the test will be run on the agent's default workflow node.")
    root_folder_id: str | None = Field(None, description="ID of the root folder to run the test on. If not provided, the test will be run on the agent's default folder.")
    root_folder_name: str | None = Field(None, description="Name of the root folder to run the test on. If not provided, the test will be run on the agent's default folder.")

class SipTrunkCredentialsRequestModel(PermissiveModel):
    username: str = Field(..., description="SIP trunk username")
    password: str | None = Field(None, description="SIP trunk password - if not specified, then remain unchanged")

class InboundSipTrunkConfigRequestModel(PermissiveModel):
    allowed_addresses: list[str] | None = Field(None, description="List of IP addresses that are allowed to use the trunk. Each item in the list can be an individual IP address or a Classless Inter-Domain Routing notation representing a CIDR block.")
    allowed_numbers: list[str] | None = Field(None, description="List of phone numbers that are allowed to use the trunk.")
    media_encryption: Literal["disabled", "allowed", "required"] | None = Field('allowed', description="Whether or not to encrypt media (data layer).")
    credentials: SipTrunkCredentialsRequestModel | None = Field(None, description="Optional digest authentication credentials (username/password).")
    remote_domains: list[str] | None = Field(None, description="Domains of remote SIP servers used to validate TLS certificates.")

class OutboundSipTrunkConfigRequestModel(PermissiveModel):
    address: str = Field(..., description="Hostname or IP the SIP INVITE is sent to.")
    transport: Literal["auto", "udp", "tcp", "tls"] | None = Field('auto', description="Protocol to use for SIP transport (signalling layer).")
    media_encryption: Literal["disabled", "allowed", "required"] | None = Field('allowed', description="Whether or not to encrypt media (data layer).")
    headers: dict[str, str] | None = Field(None, description="SIP X-* headers for INVITE request. These headers are sent as-is and may help identify this call.")
    credentials: SipTrunkCredentialsRequestModel | None = Field(None, description="Optional digest authentication credentials (username/password). If not provided, ACL authentication is assumed.")

class SipUriDynamicVariableTransferDestination(PermissiveModel):
    type_: Literal["sip_uri_dynamic_variable"] | None = Field('sip_uri_dynamic_variable', validation_alias="type", serialization_alias="type")
    sip_uri: str

class SipUriTransferDestination(PermissiveModel):
    type_: Literal["sip_uri"] | None = Field('sip_uri', validation_alias="type", serialization_alias="type")
    sip_uri: str

class PhoneNumberTransfer(PermissiveModel):
    custom_sip_headers: list[CustomSipHeader | CustomSipHeaderWithDynamicVariable] | None = Field(None, description="Custom SIP headers to include when transferring the call. Each header can be either a static value or a dynamic variable reference.", max_length=20)
    transfer_destination: PhoneNumberTransferDestination | SipUriTransferDestination | PhoneNumberDynamicVariableTransferDestination | SipUriDynamicVariableTransferDestination | None = None
    phone_number: str | None = None
    condition: str
    transfer_type: Literal["blind", "conference", "sip_refer"] | None = 'conference'
    post_dial_digits: PostDialDigitsStatic | PostDialDigitsDynamicVariable | None = Field(None, description="DTMF digits to send after call connects (e.g., 'ww1234' for extension). Can be either a static value or a dynamic variable reference. Use 'w' for 0.5s pause. Only supported for Twilio transfers.")

class SkipTurnToolConfig(PermissiveModel):
    """Allows the agent to explicitly skip its turn.

This tool should be invoked by the LLM when the user indicates they would like
to think or take a short pause before continuing the conversation—e.g. when
they say: "Give me a second", "Let me think", or "One moment please".  After
calling this tool, the assistant should not speak until the user speaks
again, or another normal turn-taking condition is met.  The tool itself has
no parameters and performs no side-effects other than informing the backend
that the current turn generation is complete."""
    system_tool_type: Literal["skip_turn"] | None = 'skip_turn'

class SkipTurnToolResponseModel(PermissiveModel):
    result_type: Literal["skip_turn_success"] | None = 'skip_turn_success'
    status: Literal["success"] | None = 'success'
    reason: str | None = None

class SoftTimeoutConfigOverride(PermissiveModel):
    message: str | None = Field(None, description="Message to show when soft timeout is reached while waiting for LLM response")

class SoftTimeoutConfigWorkflowOverride(PermissiveModel):
    timeout_seconds: float | None = Field(None, description="Time in seconds before showing the predefined message while waiting for LLM response. Set to -1 to disable.")
    message: str | None = Field(None, description="Message to show when soft timeout is reached while waiting for LLM response")
    use_llm_generated_message: bool | None = Field(None, description="If enabled, the soft timeout message will be generated dynamically instead of using the static message.")

class SrtExportOptions(PermissiveModel):
    max_characters_per_line: int | None = 42
    include_speakers: bool | None = False
    include_timestamps: bool | None = True
    format_: Literal["srt"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = 0.8
    max_segment_duration_s: float | None = 4
    max_segment_chars: int | None = 84

class SuggestedAudioTag(PermissiveModel):
    tag: str = Field(..., description="Audio tag to use (for best performance, 1-2 words, e.g., 'happy', 'excited')", min_length=1, max_length=30)
    description: str | None = Field(None, description="Optional description of when to use this tag", max_length=200)

class SupportedVoice(PermissiveModel):
    label: str = Field(..., min_length=1)
    voice_id: str = Field(..., min_length=1)
    description: str | None = None
    language: str | None = None
    model_family: Literal["turbo", "flash", "multilingual", "v3_conversational"] | None = None
    optimize_streaming_latency: Literal[0, 1, 2, 3, 4] | None = None
    stability: float | None = Field(None, ge=0.0, le=1.0)
    speed: float | None = Field(None, ge=0.7, le=1.2)
    similarity_boost: float | None = Field(None, ge=0.0, le=1.0)

class CreateAgentRouteBodyConversationConfigTts(PermissiveModel):
    """Configuration for conversational text to speech"""
    model_id: Literal["eleven_turbo_v2", "eleven_turbo_v2_5", "eleven_flash_v2", "eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3_conversational"] | None = Field('eleven_flash_v2', description="The model to use for TTS")
    voice_id: str | None = Field('cjVigY5qzO86Huf0OWal', description="The voice ID to use for TTS", min_length=0)
    supported_voices: list[SupportedVoice] | None = Field(None, description="Additional supported voices for the agent")
    expressive_mode: bool | None = Field(True, description="When enabled, applies expressive audio tags prompt. Automatically disabled for non-v3 models.")
    suggested_audio_tags: list[SuggestedAudioTag] | None = Field(None, description="Suggested audio tags to boost expressive speech (for eleven_v3 and eleven_v3_conversational models). The agent can still use other tags not listed here.", max_length=20)
    agent_output_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The audio format to use for TTS")
    optimize_streaming_latency: Literal[0, 1, 2, 3, 4] | None = Field(3, description="The optimization for streaming latency")
    stability: float | None = Field(0.5, description="The stability of generated speech", ge=0.0, le=1.0)
    speed: float | None = Field(1.0, description="The speed of generated speech", ge=0.7, le=1.2)
    similarity_boost: float | None = Field(0.8, description="The similarity boost for generated speech", ge=0.0, le=1.0)
    text_normalisation_type: Literal["system_prompt", "elevenlabs"] | None = Field('system_prompt', description="Method for converting numbers to words before converting text to speech. If set to SYSTEM_PROMPT, the system prompt will be updated to include normalization instructions. If set to ELEVENLABS, the text will be normalized after generation, incurring slight additional latency.")
    pronunciation_dictionary_locators: list[PydanticPronunciationDictionaryVersionLocator] | None = Field(None, description="The pronunciation dictionary locators")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTts(PermissiveModel):
    """Configuration for conversational text to speech"""
    model_id: Literal["eleven_turbo_v2", "eleven_turbo_v2_5", "eleven_flash_v2", "eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3_conversational"] | None = Field('eleven_flash_v2', description="The model to use for TTS")
    voice_id: str | None = Field('cjVigY5qzO86Huf0OWal', description="The voice ID to use for TTS", min_length=0)
    supported_voices: list[SupportedVoice] | None = Field(None, description="Additional supported voices for the agent")
    expressive_mode: bool | None = Field(True, description="When enabled, applies expressive audio tags prompt. Automatically disabled for non-v3 models.")
    suggested_audio_tags: list[SuggestedAudioTag] | None = Field(None, description="Suggested audio tags to boost expressive speech (for eleven_v3 and eleven_v3_conversational models). The agent can still use other tags not listed here.", max_length=20)
    agent_output_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The audio format to use for TTS")
    optimize_streaming_latency: Literal[0, 1, 2, 3, 4] | None = Field(3, description="The optimization for streaming latency")
    stability: float | None = Field(0.5, description="The stability of generated speech", ge=0.0, le=1.0)
    speed: float | None = Field(1.0, description="The speed of generated speech", ge=0.7, le=1.2)
    similarity_boost: float | None = Field(0.8, description="The similarity boost for generated speech", ge=0.0, le=1.0)
    text_normalisation_type: Literal["system_prompt", "elevenlabs"] | None = Field('system_prompt', description="Method for converting numbers to words before converting text to speech. If set to SYSTEM_PROMPT, the system prompt will be updated to include normalization instructions. If set to ELEVENLABS, the text will be normalized after generation, incurring slight additional latency.")
    pronunciation_dictionary_locators: list[PydanticPronunciationDictionaryVersionLocator] | None = Field(None, description="The pronunciation dictionary locators")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTts(PermissiveModel):
    """Configuration for conversational text to speech"""
    model_id: Literal["eleven_turbo_v2", "eleven_turbo_v2_5", "eleven_flash_v2", "eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3_conversational"] | None = Field('eleven_flash_v2', description="The model to use for TTS")
    voice_id: str | None = Field('cjVigY5qzO86Huf0OWal', description="The voice ID to use for TTS", min_length=0)
    supported_voices: list[SupportedVoice] | None = Field(None, description="Additional supported voices for the agent")
    expressive_mode: bool | None = Field(True, description="When enabled, applies expressive audio tags prompt. Automatically disabled for non-v3 models.")
    suggested_audio_tags: list[SuggestedAudioTag] | None = Field(None, description="Suggested audio tags to boost expressive speech (for eleven_v3 and eleven_v3_conversational models). The agent can still use other tags not listed here.", max_length=20)
    agent_output_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field('pcm_16000', description="The audio format to use for TTS")
    optimize_streaming_latency: Literal[0, 1, 2, 3, 4] | None = Field(3, description="The optimization for streaming latency")
    stability: float | None = Field(0.5, description="The stability of generated speech", ge=0.0, le=1.0)
    speed: float | None = Field(1.0, description="The speed of generated speech", ge=0.7, le=1.2)
    similarity_boost: float | None = Field(0.8, description="The similarity boost for generated speech", ge=0.0, le=1.0)
    text_normalisation_type: Literal["system_prompt", "elevenlabs"] | None = Field('system_prompt', description="Method for converting numbers to words before converting text to speech. If set to SYSTEM_PROMPT, the system prompt will be updated to include normalization instructions. If set to ELEVENLABS, the text will be normalized after generation, incurring slight additional latency.")
    pronunciation_dictionary_locators: list[PydanticPronunciationDictionaryVersionLocator] | None = Field(None, description="The pronunciation dictionary locators")

class TestToolResultModel(PermissiveModel):
    result_type: Literal["testing_tool_result"] | None = 'testing_tool_result'
    status: Literal["success"] | None = 'success'
    reason: str | None = 'Skipping tool call in test mode'

class TimeRange(PermissiveModel):
    start_ms: int
    end_ms: int

class SectionSource(PermissiveModel):
    song_id: str = Field(..., description="The ID of the song to source the section from. You can find the song ID in the response headers when you generate a song.", min_length=1, max_length=100)
    range_: TimeRange = Field(..., validation_alias="range", serialization_alias="range", description="The range to extract from the source song.")
    negative_ranges: list[TimeRange] | None = Field(None, description="The ranges to exclude from the 'range'.", max_length=10)

class SongSection(PermissiveModel):
    section_name: str = Field(..., description="The name of the section. Must be between 1 and 100 characters.", min_length=1, max_length=100)
    positive_local_styles: list[str] = Field(..., description="The styles and musical directions that should be present in this section. Use English language for best result.", max_length=50)
    negative_local_styles: list[str] = Field(..., description="The styles and musical directions that should not be present in this section. Use English language for best result.", max_length=50)
    duration_ms: int = Field(..., description="The duration of the section in milliseconds. Must be between 3000ms and 120000ms.", ge=3000, le=120000)
    lines: list[str] = Field(..., description="The lyrics of the section. Max 200 characters per line.", max_length=30)
    source_from: SectionSource | None = Field(None, description="Optional source to extract the section from. Used for inpainting. Only available to enterprise clients with access to the inpainting feature.")

class ToolMockConfig(PermissiveModel):
    default_return_value: str | None = 'Tool Called.'
    default_is_error: bool | None = False

class TransferBranchInfoDefaultingToMain(PermissiveModel):
    branch_reason: Literal["defaulting_to_main"]
    branch_id: str

class TransferBranchInfoTrafficSplit(PermissiveModel):
    branch_reason: Literal["traffic_split"]
    branch_id: str
    traffic_percentage: float

class TransferToAgentToolConfig(PermissiveModel):
    system_tool_type: Literal["transfer_to_agent"] | None = 'transfer_to_agent'
    transfers: list[AgentTransfer]

class TransferToAgentToolResultErrorModel(PermissiveModel):
    result_type: Literal["transfer_to_agent_error"] | None = 'transfer_to_agent_error'
    status: Literal["error"] | None = 'error'
    from_agent: str
    error: str

class TransferToAgentToolResultSuccessModel(PermissiveModel):
    result_type: Literal["transfer_to_agent_success"] | None = 'transfer_to_agent_success'
    status: Literal["success"] | None = 'success'
    from_agent: str
    to_agent: str
    condition: str
    delay_ms: int | None = 0
    transfer_message: str | None = None
    enable_transferred_agent_first_message: bool | None = False
    branch_info: Annotated[TransferBranchInfoTrafficSplit | TransferBranchInfoDefaultingToMain, Field(discriminator="branch_reason")] | None = None

class TransferToNumberResultErrorModel(PermissiveModel):
    result_type: Literal["transfer_to_number_error"] | None = 'transfer_to_number_error'
    status: Literal["error"] | None = 'error'
    error: str
    details: str | None = None

class TransferToNumberResultSipSuccessModel(PermissiveModel):
    result_type: Literal["transfer_to_number_sip_success"] | None = 'transfer_to_number_sip_success'
    status: Literal["success"] | None = 'success'
    transfer_number: str
    reason: str | None = None
    note: str | None = None

class TransferToNumberResultTwilioSuccessModel(PermissiveModel):
    result_type: Literal["transfer_to_number_twilio_success"] | None = 'transfer_to_number_twilio_success'
    status: Literal["success"] | None = 'success'
    transfer_number: str
    reason: str | None = None
    client_message: str | None = None
    agent_message: str
    conference_name: str
    post_dial_digits: str | None = None
    note: str | None = None

class TransferToNumberToolConfigInput(PermissiveModel):
    system_tool_type: Literal["transfer_to_number"] | None = 'transfer_to_number'
    transfers: list[PhoneNumberTransfer]
    enable_client_message: bool | None = Field(True, description="Whether to play a message to the client while they wait for transfer. Defaults to true for backward compatibility.")

class TtsConversationalConfigOverride(PermissiveModel):
    voice_id: str | None = Field(None, description="The voice ID to use for TTS")
    stability: float | None = Field(None, description="The stability of generated speech")
    speed: float | None = Field(None, description="The speed of generated speech")
    similarity_boost: float | None = Field(None, description="The similarity boost for generated speech")

class TtsConversationalConfigWorkflowOverrideInput(PermissiveModel):
    model_id: Literal["eleven_turbo_v2", "eleven_turbo_v2_5", "eleven_flash_v2", "eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3_conversational"] | None = Field(None, description="The model to use for TTS")
    voice_id: str | None = Field(None, description="The voice ID to use for TTS")
    supported_voices: list[SupportedVoice] | None = Field(None, description="Additional supported voices for the agent")
    expressive_mode: bool | None = Field(None, description="When enabled, applies expressive audio tags prompt. Automatically disabled for non-v3 models.")
    suggested_audio_tags: list[SuggestedAudioTag] | None = Field(None, description="Suggested audio tags to boost expressive speech (for eleven_v3 and eleven_v3_conversational models). The agent can still use other tags not listed here.")
    agent_output_audio_format: Literal["pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_44100", "pcm_48000", "ulaw_8000"] | None = Field(None, description="The audio format to use for TTS")
    optimize_streaming_latency: Literal[0, 1, 2, 3, 4] | None = Field(None, description="The optimization for streaming latency")
    stability: float | None = Field(None, description="The stability of generated speech")
    speed: float | None = Field(None, description="The speed of generated speech")
    similarity_boost: float | None = Field(None, description="The similarity boost for generated speech")
    text_normalisation_type: Literal["system_prompt", "elevenlabs"] | None = Field(None, description="Method for converting numbers to words before converting text to speech. If set to SYSTEM_PROMPT, the system prompt will be updated to include normalization instructions. If set to ELEVENLABS, the text will be normalized after generation, incurring slight additional latency.")
    pronunciation_dictionary_locators: list[PydanticPronunciationDictionaryVersionLocator] | None = Field(None, description="The pronunciation dictionary locators")

class TurnConfigOverride(PermissiveModel):
    soft_timeout_config: SoftTimeoutConfigOverride | None = Field(None, description="Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses.")

class ConversationConfigClientOverrideInput(PermissiveModel):
    turn: TurnConfigOverride | None = Field(None, description="Configuration for turn detection")
    tts: TtsConversationalConfigOverride | None = Field(None, description="Configuration for conversational text to speech")
    conversation: ConversationConfigOverride | None = Field(None, description="Configuration for conversational events")
    agent: AgentConfigOverrideInput | None = Field(None, description="Agent specific configuration")

class ConversationInitiationClientDataRequestInput(PermissiveModel):
    conversation_config_override: ConversationConfigClientOverrideInput | None = None
    custom_llm_extra_body: dict[str, Any] | None = None
    user_id: str | None = Field(None, description="ID of the end user participating in this conversation (for agent owner's user identification)")
    source_info: ConversationInitiationSourceInfo | None = None
    dynamic_variables: dict[str, str | float | int | bool] | None = None

class LanguagePresetInput(PermissiveModel):
    overrides: ConversationConfigClientOverrideInput = Field(..., description="The overrides for the language preset")
    first_message_translation: LanguagePresetTranslation | None = Field(None, description="The translation of the first message")
    soft_timeout_translation: LanguagePresetTranslation | None = Field(None, description="The translation of the soft timeout message")

class OutboundCallRecipient(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    phone_number: str | None = None
    whatsapp_user_id: str | None = None
    conversation_initiation_client_data: ConversationInitiationClientDataRequestInput | None = None

class TurnConfigWorkflowOverride(PermissiveModel):
    turn_timeout: float | None = Field(None, description="Maximum wait time for the user's reply before re-engaging the user")
    initial_wait_time: float | None = Field(None, description="How long the agent will wait for the user to start the conversation if the first message is empty. If not set, uses the regular turn_timeout.")
    silence_end_call_timeout: float | None = Field(None, description="Maximum wait time since the user last spoke before terminating the call")
    soft_timeout_config: SoftTimeoutConfigWorkflowOverride | None = Field(None, description="Configuration for soft timeout functionality. Provides immediate feedback during longer LLM responses.")
    mode: Literal["silence", "turn"] | None = Field(None, description="The mode of turn detection")
    turn_eagerness: Literal["patient", "normal", "eager"] | None = Field(None, description="Controls how eager the agent is to respond. Low = less eager (waits longer), Standard = default eagerness, High = more eager (responds sooner)")
    spelling_patience: Literal["auto", "off"] | None = Field(None, description="Controls if the agent should be more patient when user is spelling numbers and named entities. Auto = model based, Off = never wait extra")
    speculative_turn: bool | None = Field(None, description="When enabled, starts generating LLM responses during silence before full turn confidence is reached, reducing perceived latency. May increase LLM costs.")

class TxtExportOptions(PermissiveModel):
    max_characters_per_line: int | None = 100
    include_speakers: bool | None = True
    include_timestamps: bool | None = True
    format_: Literal["txt"] = Field(..., validation_alias="format", serialization_alias="format")
    segment_on_silence_longer_than_s: float | None = None
    max_segment_duration_s: float | None = None
    max_segment_chars: int | None = None

class ExportOptions(RootModel[Annotated[
    SegmentedJsonExportOptions
    | DocxExportOptions
    | PdfExportOptions
    | TxtExportOptions
    | HtmlExportOptions
    | SrtExportOptions,
    Field(discriminator="format_")
]]):
    pass

class UnitTestToolCallParameter(PermissiveModel):
    eval_: Annotated[LlmParameterEvaluationStrategy | RegexParameterEvaluationStrategy | ExactParameterEvaluationStrategy | MatchAnythingParameterEvaluationStrategy, Field(discriminator="type_")] = Field(..., validation_alias="eval", serialization_alias="eval")
    path: str

class UnitTestWorkflowNodeTransitionEvaluationNodeId(PermissiveModel):
    type_: Literal["node_id"] | None = Field('node_id', validation_alias="type", serialization_alias="type")
    agent_id: str = Field(..., description="The ID of the agent whose workflow contains the target node.")
    target_node_id: str = Field(..., description="The ID of the workflow node that the agent should transition to.")

class UnitTestToolCallEvaluationModelInput(PermissiveModel):
    parameters: list[UnitTestToolCallParameter] | None = Field(None, description="Parameters to evaluate for the agent's tool call. If empty, the tool call parameters are not evaluated.")
    referenced_tool: ReferencedToolCommonModel | None = Field(None, description="The tool to evaluate a call against.")
    verify_absence: bool | None = Field(False, description="Whether to verify that the tool was NOT called.")
    workflow_node_transition: UnitTestWorkflowNodeTransitionEvaluationNodeId | None = Field(None, description="Configuration for testing workflow node transitions. When set, the test will verify the agent transitions to the specified workflow node.")

class UpdateAssetParams(PermissiveModel):
    smb_tool_type: Literal["update_asset"] | None = 'update_asset'

class UpdateCalendarEventParams(PermissiveModel):
    smb_tool_type: Literal["update_calendar_event"] | None = 'update_calendar_event'

class UpdateClientParams(PermissiveModel):
    """Update an existing client's information."""
    smb_tool_type: Literal["update_client"] | None = 'update_client'

class UpdateProductParams(PermissiveModel):
    smb_tool_type: Literal["update_product"] | None = 'update_product'

class UpdateServiceParams(PermissiveModel):
    """Update an existing service's information."""
    smb_tool_type: Literal["update_service"] | None = 'update_service'

class UpdateStaffParams(PermissiveModel):
    """Update an existing staff member's information."""
    smb_tool_type: Literal["update_staff"] | None = 'update_staff'

class SmbToolConfig(PermissiveModel):
    """SMB tool configuration that wraps SMB tool parameters."""
    type_: Literal["smb"] | None = Field('smb', validation_alias="type", serialization_alias="type", description="Tool type identifier")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    enabled: bool | None = Field(True, description="Whether this tool is enabled for the agent")
    params: SearchClientsParams | ListClientsParams | GetClientByPhoneParams | CreateClientParams | UpdateClientParams | DeleteClientParams | ListStaffParams | CreateStaffParams | UpdateStaffParams | DeleteStaffParams | ListAssetsParams | CreateAssetParams | UpdateAssetParams | DeleteAssetParams | ListServicesParams | CreateServiceParams | UpdateServiceParams | DeleteServiceParams | ListProductsParams | CreateProductParams | UpdateProductParams | DeleteProductParams | CheckServiceAvailabilityParams | CreateClientAppointmentParams | GetClientAppointmentsParams | ListCalendarEventsParams | UpdateCalendarEventParams | DeleteCalendarEventParams | ListRentalServicesParams | CheckRentalAvailabilityParams | CreateRentalBookingParams

class UrlAvatar(PermissiveModel):
    type_: Literal["url"] | None = Field('url', validation_alias="type", serialization_alias="type", description="The type of the avatar")
    custom_url: str | None = Field('', description="The custom URL of the avatar")

class UserFeedback(PermissiveModel):
    score: Literal["like", "dislike"]
    time_in_call_secs: int

class VadConfigWorkflowOverride(PermissiveModel):
    background_voice_detection: bool | None = Field(None, description="Whether to use background voice filtering")

class VoiceMailDetectionResultSuccessModel(PermissiveModel):
    result_type: Literal["voicemail_detection_success"] | None = 'voicemail_detection_success'
    status: Literal["success"] | None = 'success'
    voicemail_message: str | None = None
    reason: str | None = None

class ConversationHistoryTranscriptSystemToolResultCommonModelInput(PermissiveModel):
    request_id: str
    tool_name: str
    result_value: str
    is_error: bool
    tool_has_been_called: bool
    tool_latency_secs: float | None = 0
    error_type: str | None = ''
    raw_error_message: str | None = ''
    dynamic_variable_updates: list[DynamicVariableUpdateCommonModel] | None = None
    type_: Literal["system"] = Field(..., validation_alias="type", serialization_alias="type")
    result: EndCallToolResultModel | LanguageDetectionToolResultModel | TransferToAgentToolResultSuccessModel | TransferToAgentToolResultErrorModel | TransferToNumberResultTwilioSuccessModel | TransferToNumberResultSipSuccessModel | TransferToNumberResultErrorModel | SkipTurnToolResponseModel | PlayDtmfResultSuccessModel | PlayDtmfResultErrorModel | VoiceMailDetectionResultSuccessModel | TestToolResultModel | None = None

class VoicemailDetectionToolConfig(PermissiveModel):
    """Allows the agent to detect when a voicemail system is encountered.

This tool should be invoked by the LLM when it detects that the call has been
answered by a voicemail system rather than a human. If a voicemail message
is configured, it will be played; otherwise the call will end immediately."""
    system_tool_type: Literal["voicemail_detection"] | None = 'voicemail_detection'
    voicemail_message: str | None = Field(None, description="Optional message to leave on voicemail when detected. If not provided, the call will end immediately when voicemail is detected. Supports dynamic variables (e.g., {{system__time}}, {{system__call_duration_secs}}, {{custom_variable}}).")

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsEndCall(PermissiveModel):
    """The end call tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsLanguageDetection(PermissiveModel):
    """The language detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone(PermissiveModel):
    """The play DTMF tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsSkipTurn(PermissiveModel):
    """The skip turn tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToAgent(PermissiveModel):
    """The transfer to agent tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToNumber(PermissiveModel):
    """The transfer to number tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsVoicemailDetection(PermissiveModel):
    """The voicemail detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class CreateAgentRouteBodyConversationConfigAgentPromptBuiltInTools(PermissiveModel):
    """Built-in system tools to be used by the agent"""
    end_call: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsEndCall | None = Field(None, description="The end call tool")
    language_detection: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsLanguageDetection | None = Field(None, description="The language detection tool")
    transfer_to_agent: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToAgent | None = Field(None, description="The transfer to agent tool")
    transfer_to_number: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToNumber | None = Field(None, description="The transfer to number tool")
    skip_turn: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsSkipTurn | None = Field(None, description="The skip turn tool")
    play_keypad_touch_tone: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone | None = Field(None, description="The play DTMF tool")
    voicemail_detection: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsVoicemailDetection | None = Field(None, description="The voicemail detection tool")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall(PermissiveModel):
    """The end call tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection(PermissiveModel):
    """The language detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone(PermissiveModel):
    """The play DTMF tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn(PermissiveModel):
    """The skip turn tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent(PermissiveModel):
    """The transfer to agent tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber(PermissiveModel):
    """The transfer to number tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection(PermissiveModel):
    """The voicemail detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools(PermissiveModel):
    """Built-in system tools to be used by the agent"""
    end_call: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall | None = Field(None, description="The end call tool")
    language_detection: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection | None = Field(None, description="The language detection tool")
    transfer_to_agent: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent | None = Field(None, description="The transfer to agent tool")
    transfer_to_number: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber | None = Field(None, description="The transfer to number tool")
    skip_turn: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn | None = Field(None, description="The skip turn tool")
    play_keypad_touch_tone: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone | None = Field(None, description="The play DTMF tool")
    voicemail_detection: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection | None = Field(None, description="The voicemail detection tool")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall(PermissiveModel):
    """The end call tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection(PermissiveModel):
    """The language detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone(PermissiveModel):
    """The play DTMF tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn(PermissiveModel):
    """The skip turn tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent(PermissiveModel):
    """The transfer to agent tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber(PermissiveModel):
    """The transfer to number tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection(PermissiveModel):
    """The voicemail detection tool"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools(PermissiveModel):
    """Built-in system tools to be used by the agent"""
    end_call: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall | None = Field(None, description="The end call tool")
    language_detection: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection | None = Field(None, description="The language detection tool")
    transfer_to_agent: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent | None = Field(None, description="The transfer to agent tool")
    transfer_to_number: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber | None = Field(None, description="The transfer to number tool")
    skip_turn: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn | None = Field(None, description="The skip turn tool")
    play_keypad_touch_tone: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone | None = Field(None, description="The play DTMF tool")
    voicemail_detection: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection | None = Field(None, description="The voicemail detection tool")

class SystemToolConfigInput(PermissiveModel):
    """A system tool is a tool that is used to call a system method in the server"""
    type_: Literal["system"] | None = Field('system', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str | None = Field('', description="Description of when the tool should be used and what it does. Leave empty to use the default description that's optimized for the specific tool type.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    params: EndCallToolConfig | LanguageDetectionToolConfig | TransferToAgentToolConfig | TransferToNumberToolConfigInput | SkipTurnToolConfig | PlayDtmfToolConfig | VoicemailDetectionToolConfig

class BuiltInToolsWorkflowOverrideInput(PermissiveModel):
    end_call: SystemToolConfigInput | None = Field(None, description="The end call tool")
    language_detection: SystemToolConfigInput | None = Field(None, description="The language detection tool")
    transfer_to_agent: SystemToolConfigInput | None = Field(None, description="The transfer to agent tool")
    transfer_to_number: SystemToolConfigInput | None = Field(None, description="The transfer to number tool")
    skip_turn: SystemToolConfigInput | None = Field(None, description="The skip turn tool")
    play_keypad_touch_tone: SystemToolConfigInput | None = Field(None, description="The play DTMF tool")
    voicemail_detection: SystemToolConfigInput | None = Field(None, description="The voicemail detection tool")

class WhatsAppTemplateDocumentParamDetails(PermissiveModel):
    link: str
    filename: str | None = None

class WhatsAppTemplateDocumentParam(PermissiveModel):
    type_: Literal["document"] | None = Field('document', validation_alias="type", serialization_alias="type")
    document: WhatsAppTemplateDocumentParamDetails

class WhatsAppTemplateImageParamDetails(PermissiveModel):
    link: str

class WhatsAppTemplateImageParam(PermissiveModel):
    type_: Literal["image"] | None = Field('image', validation_alias="type", serialization_alias="type")
    image: WhatsAppTemplateImageParamDetails

class WhatsAppTemplateLocationParamDetails(PermissiveModel):
    latitude: str
    longitude: str
    name: str
    address: str

class WhatsAppTemplateLocationParam(PermissiveModel):
    type_: Literal["location"] | None = Field('location', validation_alias="type", serialization_alias="type")
    location: WhatsAppTemplateLocationParamDetails

class WhatsAppTemplateTextParam(PermissiveModel):
    parameter_name: str | None = None
    type_: Literal["text"] | None = Field('text', validation_alias="type", serialization_alias="type")
    text: str

class WhatsAppTemplateBodyComponentParams(PermissiveModel):
    type_: Literal["body"] | None = Field('body', validation_alias="type", serialization_alias="type")
    parameters: list[WhatsAppTemplateTextParam]

class WhatsAppTemplateButtonComponentParams(PermissiveModel):
    type_: Literal["button"] | None = Field('button', validation_alias="type", serialization_alias="type")
    parameters: list[WhatsAppTemplateTextParam]
    index: int
    sub_type: str

class WhatsAppTemplateHeaderComponentParams(PermissiveModel):
    type_: Literal["header"] | None = Field('header', validation_alias="type", serialization_alias="type")
    parameters: list[WhatsAppTemplateTextParam | WhatsAppTemplateImageParam | WhatsAppTemplateDocumentParam | WhatsAppTemplateLocationParam]

class WidgetTermsTranslation(PermissiveModel):
    source_hash: str
    text: str

class WidgetTextContents(PermissiveModel):
    main_label: str | None = Field(None, description="Call to action displayed inside the compact and full variants.")
    start_call: str | None = Field(None, description="Text and ARIA label for the start call button.")
    start_chat: str | None = Field(None, description="Text and ARIA label for the start chat button (text only)")
    new_call: str | None = Field(None, description="Text and ARIA label for the new call button. Displayed when the caller already finished at least one call in order ot start the next one.")
    end_call: str | None = Field(None, description="Text and ARIA label for the end call button.")
    mute_microphone: str | None = Field(None, description="ARIA label for the mute microphone button.")
    change_language: str | None = Field(None, description="ARIA label for the change language dropdown.")
    collapse: str | None = Field(None, description="ARIA label for the collapse button.")
    expand: str | None = Field(None, description="ARIA label for the expand button.")
    copied: str | None = Field(None, description="Text displayed when the user copies a value using the copy button.")
    accept_terms: str | None = Field(None, description="Text and ARIA label for the accept terms button.")
    dismiss_terms: str | None = Field(None, description="Text and ARIA label for the cancel terms button.")
    listening_status: str | None = Field(None, description="Status displayed when the agent is listening.")
    speaking_status: str | None = Field(None, description="Status displayed when the agent is speaking.")
    connecting_status: str | None = Field(None, description="Status displayed when the agent is connecting.")
    chatting_status: str | None = Field(None, description="Status displayed when the agent is chatting (text only)")
    input_label: str | None = Field(None, description="ARIA label for the text message input.")
    input_placeholder: str | None = Field(None, description="Placeholder text for the text message input.")
    input_placeholder_text_only: str | None = Field(None, description="Placeholder text for the text message input (text only)")
    input_placeholder_new_conversation: str | None = Field(None, description="Placeholder text for the text message input when starting a new conversation (text only)")
    user_ended_conversation: str | None = Field(None, description="Information message displayed when the user ends the conversation.")
    agent_ended_conversation: str | None = Field(None, description="Information message displayed when the agent ends the conversation.")
    conversation_id: str | None = Field(None, description="Text label used next to the conversation ID.")
    error_occurred: str | None = Field(None, description="Text label used when an error occurs.")
    copy_id: str | None = Field(None, description="Text and ARIA label used for the copy ID button.")
    initiate_feedback: str | None = Field(None, description="Text displayed to prompt the user for feedback.")
    request_follow_up_feedback: str | None = Field(None, description="Text displayed to request additional feedback details.")
    thanks_for_feedback: str | None = Field(None, description="Text displayed to thank the user for providing feedback.")
    thanks_for_feedback_details: str | None = Field(None, description="Additional text displayed explaining the value of user feedback.")
    follow_up_feedback_placeholder: str | None = Field(None, description="Placeholder text for the follow-up feedback input field.")
    submit: str | None = Field(None, description="Text and ARIA label for the submit button.")
    go_back: str | None = Field(None, description="Text and ARIA label for the go back button.")
    send_message: str | None = Field(None, description="Text and ARIA label for the send message button.")
    text_mode: str | None = Field(None, description="Text and ARIA label for the switch to text mode button.")
    voice_mode: str | None = Field(None, description="Text and ARIA label for the switch to voice mode button.")
    switched_to_text_mode: str | None = Field(None, description="Toast notification displayed when switching to text mode.")
    switched_to_voice_mode: str | None = Field(None, description="Toast notification displayed when switching to voice mode.")
    copy_: str | None = Field(None, validation_alias="copy", serialization_alias="copy", description="Text and ARIA label for the copy button.")
    download: str | None = Field(None, description="Text and ARIA label for the download button.")
    wrap: str | None = Field(None, description="Text and ARIA label for the wrap toggle button.")
    agent_working: str | None = Field(None, description="Status text displayed when the agent is processing a tool call.")
    agent_done: str | None = Field(None, description="Status text displayed when the agent finishes processing a tool call.")
    agent_error: str | None = Field(None, description="Status text displayed when the agent encounters an error during a tool call.")

class WidgetLanguagePreset(PermissiveModel):
    text_contents: WidgetTextContents | None = Field(None, description="The text contents for the selected language")
    terms_text: str | None = Field(None, description="The text to display for terms and conditions in this language")
    terms_html: str | None = Field(None, description="The HTML to display for terms and conditions in this language")
    terms_key: str | None = Field(None, description="The key to display for terms and conditions in this language")
    terms_translation: WidgetTermsTranslation | None = Field(None, description="The translation cache for the terms")

class CreateAgentRouteBodyPlatformSettingsWidget(PermissiveModel):
    """Configuration for the widget"""
    variant: Literal["tiny", "compact", "full", "expandable"] | None = Field('full', description="The variant of the widget")
    placement: Literal["top-left", "top", "top-right", "bottom-left", "bottom", "bottom-right"] | None = Field('bottom-right', description="The placement of the widget on the screen")
    expandable: Literal["never", "mobile", "desktop", "always"] | None = Field('never', description="Whether the widget is expandable")
    avatar: OrbAvatar | UrlAvatar | ImageAvatar | None = Field(None, description="The avatar of the widget")
    feedback_mode: Literal["none", "during", "end"] | None = Field('none', description="The feedback mode of the widget")
    end_feedback: CreateAgentRouteBodyPlatformSettingsWidgetEndFeedback | None = Field(None, description="Configuration for feedback collected at the end of the conversation")
    bg_color: str | None = Field('#ffffff', description="The background color of the widget")
    text_color: str | None = Field('#000000', description="The text color of the widget")
    btn_color: str | None = Field('#000000', description="The button color of the widget")
    btn_text_color: str | None = Field('#ffffff', description="The button text color of the widget")
    border_color: str | None = Field('#e1e1e1', description="The border color of the widget")
    focus_color: str | None = Field('#000000', description="The focus color of the widget")
    border_radius: int | None = Field(None, description="The border radius of the widget")
    btn_radius: int | None = Field(None, description="The button radius of the widget")
    action_text: str | None = Field(None, description="The action text of the widget")
    start_call_text: str | None = Field(None, description="The start call text of the widget")
    end_call_text: str | None = Field(None, description="The end call text of the widget")
    expand_text: str | None = Field(None, description="The expand text of the widget")
    listening_text: str | None = Field(None, description="The text to display when the agent is listening")
    speaking_text: str | None = Field(None, description="The text to display when the agent is speaking")
    shareable_page_text: str | None = Field(None, description="The text to display when sharing")
    shareable_page_show_terms: bool | None = Field(True, description="Whether to show terms and conditions on the shareable page")
    terms_text: str | None = Field(None, description="The text to display for terms and conditions")
    terms_html: str | None = Field(None, description="The HTML to display for terms and conditions")
    terms_key: str | None = Field(None, description="The key to display for terms and conditions")
    show_avatar_when_collapsed: bool | None = Field(False, description="Whether to show the avatar when the widget is collapsed")
    disable_banner: bool | None = Field(False, description="Whether to disable the banner")
    override_link: str | None = Field(None, description="The override link for the widget")
    markdown_link_allowed_hosts: list[AllowlistItem] | None = Field(None, description="List of allowed hostnames for clickable markdown links. Use { hostname: '*' } to allow any domain. Empty means no links are allowed.")
    markdown_link_include_www: bool | None = Field(True, description="Whether to automatically include www. variants of allowed hosts")
    markdown_link_allow_http: bool | None = Field(True, description="Whether to allow http:// in addition to https:// for allowed hosts")
    mic_muting_enabled: bool | None = Field(False, description="Whether to enable mic muting")
    transcript_enabled: bool | None = Field(False, description="Whether the widget should show the conversation transcript as it goes on")
    text_input_enabled: bool | None = Field(True, description="Whether the user should be able to send text messages")
    conversation_mode_toggle_enabled: bool | None = Field(False, description="Whether to enable the conversation mode toggle in the widget")
    default_expanded: bool | None = Field(False, description="Whether the widget should be expanded by default")
    always_expanded: bool | None = Field(False, description="Whether the widget should always be expanded")
    dismissible: bool | None = Field(False, description="Whether the widget can be dismissed by the user")
    show_agent_status: bool | None = Field(False, description="Whether to show agent working/done/error status during tool use")
    show_conversation_id: bool | None = Field(True, description="Whether to show the conversation ID after disconnection.")
    strip_audio_tags: bool | None = Field(True, description="Whether to strip audio markup from messages.")
    syntax_highlight_theme: Literal["light", "dark"] | None = Field(None, description="Theme for code block syntax highlighting. Defaults to auto-detection by the widget when not set.")
    text_contents: CreateAgentRouteBodyPlatformSettingsWidgetTextContents | None = Field(None, description="Text contents of the widget")
    styles: CreateAgentRouteBodyPlatformSettingsWidgetStyles | None = Field(None, description="Styles for the widget")
    language_selector: bool | None = Field(False, description="Whether to show the language selector")
    supports_text_only: bool | None = Field(True, description="Whether the widget can switch to text only mode")
    custom_avatar_path: str | None = Field(None, description="The custom avatar path")
    language_presets: dict[str, WidgetLanguagePreset] | None = Field(None, description="Language presets for the widget")

class CreateAgentRouteBodyPlatformSettings(PermissiveModel):
    """Platform settings including widget config, auth, privacy, guardrails, and evaluation"""
    evaluation: CreateAgentRouteBodyPlatformSettingsEvaluation | None = Field(None, description="Settings for evaluation")
    widget: CreateAgentRouteBodyPlatformSettingsWidget | None = Field(None, description="Configuration for the widget")
    data_collection: dict[str, LiteralJsonSchemaProperty] | None = Field(None, description="Data collection settings")
    overrides: CreateAgentRouteBodyPlatformSettingsOverrides | None = Field(None, description="Additional overrides for the agent during conversation initiation")
    workspace_overrides: CreateAgentRouteBodyPlatformSettingsWorkspaceOverrides | None = Field(None, description="Workspace overrides for the agent")
    testing: CreateAgentRouteBodyPlatformSettingsTesting | None = Field(None, description="Testing configuration for the agent")
    archived: bool | None = Field(False, description="Whether the agent is archived")
    guardrails: CreateAgentRouteBodyPlatformSettingsGuardrails | None = Field(None, description="Guardrails configuration for the agent")
    summary_language: str | None = Field(None, description="Language for all conversation analysis outputs (summaries, titles, evaluation rationales, data collection rationales). If not set, the language will be inferred from the conversation. Must be one of the supported conversation languages.")
    auth: CreateAgentRouteBodyPlatformSettingsAuth | None = Field(None, description="Settings for authentication")
    call_limits: CreateAgentRouteBodyPlatformSettingsCallLimits | None = Field(None, description="Call limits for the agent")
    privacy: CreateAgentRouteBodyPlatformSettingsPrivacy | None = Field(None, description="Privacy settings for the agent")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidget(PermissiveModel):
    """Configuration for the widget"""
    variant: Literal["tiny", "compact", "full", "expandable"] | None = Field('full', description="The variant of the widget")
    placement: Literal["top-left", "top", "top-right", "bottom-left", "bottom", "bottom-right"] | None = Field('bottom-right', description="The placement of the widget on the screen")
    expandable: Literal["never", "mobile", "desktop", "always"] | None = Field('never', description="Whether the widget is expandable")
    avatar: OrbAvatar | UrlAvatar | ImageAvatar | None = Field(None, description="The avatar of the widget")
    feedback_mode: Literal["none", "during", "end"] | None = Field('none', description="The feedback mode of the widget")
    end_feedback: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback | None = Field(None, description="Configuration for feedback collected at the end of the conversation")
    bg_color: str | None = Field('#ffffff', description="The background color of the widget")
    text_color: str | None = Field('#000000', description="The text color of the widget")
    btn_color: str | None = Field('#000000', description="The button color of the widget")
    btn_text_color: str | None = Field('#ffffff', description="The button text color of the widget")
    border_color: str | None = Field('#e1e1e1', description="The border color of the widget")
    focus_color: str | None = Field('#000000', description="The focus color of the widget")
    border_radius: int | None = Field(None, description="The border radius of the widget")
    btn_radius: int | None = Field(None, description="The button radius of the widget")
    action_text: str | None = Field(None, description="The action text of the widget")
    start_call_text: str | None = Field(None, description="The start call text of the widget")
    end_call_text: str | None = Field(None, description="The end call text of the widget")
    expand_text: str | None = Field(None, description="The expand text of the widget")
    listening_text: str | None = Field(None, description="The text to display when the agent is listening")
    speaking_text: str | None = Field(None, description="The text to display when the agent is speaking")
    shareable_page_text: str | None = Field(None, description="The text to display when sharing")
    shareable_page_show_terms: bool | None = Field(True, description="Whether to show terms and conditions on the shareable page")
    terms_text: str | None = Field(None, description="The text to display for terms and conditions")
    terms_html: str | None = Field(None, description="The HTML to display for terms and conditions")
    terms_key: str | None = Field(None, description="The key to display for terms and conditions")
    show_avatar_when_collapsed: bool | None = Field(False, description="Whether to show the avatar when the widget is collapsed")
    disable_banner: bool | None = Field(False, description="Whether to disable the banner")
    override_link: str | None = Field(None, description="The override link for the widget")
    markdown_link_allowed_hosts: list[AllowlistItem] | None = Field(None, description="List of allowed hostnames for clickable markdown links. Use { hostname: '*' } to allow any domain. Empty means no links are allowed.")
    markdown_link_include_www: bool | None = Field(True, description="Whether to automatically include www. variants of allowed hosts")
    markdown_link_allow_http: bool | None = Field(True, description="Whether to allow http:// in addition to https:// for allowed hosts")
    mic_muting_enabled: bool | None = Field(False, description="Whether to enable mic muting")
    transcript_enabled: bool | None = Field(False, description="Whether the widget should show the conversation transcript as it goes on")
    text_input_enabled: bool | None = Field(True, description="Whether the user should be able to send text messages")
    conversation_mode_toggle_enabled: bool | None = Field(False, description="Whether to enable the conversation mode toggle in the widget")
    default_expanded: bool | None = Field(False, description="Whether the widget should be expanded by default")
    always_expanded: bool | None = Field(False, description="Whether the widget should always be expanded")
    dismissible: bool | None = Field(False, description="Whether the widget can be dismissed by the user")
    show_agent_status: bool | None = Field(False, description="Whether to show agent working/done/error status during tool use")
    show_conversation_id: bool | None = Field(True, description="Whether to show the conversation ID after disconnection.")
    strip_audio_tags: bool | None = Field(True, description="Whether to strip audio markup from messages.")
    syntax_highlight_theme: Literal["light", "dark"] | None = Field(None, description="Theme for code block syntax highlighting. Defaults to auto-detection by the widget when not set.")
    text_contents: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents | None = Field(None, description="Text contents of the widget")
    styles: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles | None = Field(None, description="Styles for the widget")
    language_selector: bool | None = Field(False, description="Whether to show the language selector")
    supports_text_only: bool | None = Field(True, description="Whether the widget can switch to text only mode")
    custom_avatar_path: str | None = Field(None, description="The custom avatar path")
    language_presets: dict[str, WidgetLanguagePreset] | None = Field(None, description="Language presets for the widget")

class ResubmitTestsRouteBodyAgentConfigOverridePlatformSettings(PermissiveModel):
    evaluation: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsEvaluation | None = Field(None, description="Settings for evaluation")
    widget: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidget | None = Field(None, description="Configuration for the widget")
    data_collection: dict[str, LiteralJsonSchemaProperty] | None = Field(None, description="Data collection settings")
    overrides: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverrides | None = Field(None, description="Additional overrides for the agent during conversation initiation")
    workspace_overrides: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides | None = Field(None, description="Workspace overrides for the agent")
    testing: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsTesting | None = Field(None, description="Testing configuration for the agent")
    archived: bool | None = Field(False, description="Whether the agent is archived")
    guardrails: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrails | None = Field(None, description="Guardrails configuration for the agent")
    summary_language: str | None = Field(None, description="Language for all conversation analysis outputs (summaries, titles, evaluation rationales, data collection rationales). If not set, the language will be inferred from the conversation. Must be one of the supported conversation languages.")
    auth: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsAuth | None = Field(None, description="Settings for authentication")
    call_limits: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsCallLimits | None = Field(None, description="Call limits for the agent")
    privacy: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacy | None = Field(None, description="Privacy settings for the agent")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidget(PermissiveModel):
    """Configuration for the widget"""
    variant: Literal["tiny", "compact", "full", "expandable"] | None = Field('full', description="The variant of the widget")
    placement: Literal["top-left", "top", "top-right", "bottom-left", "bottom", "bottom-right"] | None = Field('bottom-right', description="The placement of the widget on the screen")
    expandable: Literal["never", "mobile", "desktop", "always"] | None = Field('never', description="Whether the widget is expandable")
    avatar: OrbAvatar | UrlAvatar | ImageAvatar | None = Field(None, description="The avatar of the widget")
    feedback_mode: Literal["none", "during", "end"] | None = Field('none', description="The feedback mode of the widget")
    end_feedback: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback | None = Field(None, description="Configuration for feedback collected at the end of the conversation")
    bg_color: str | None = Field('#ffffff', description="The background color of the widget")
    text_color: str | None = Field('#000000', description="The text color of the widget")
    btn_color: str | None = Field('#000000', description="The button color of the widget")
    btn_text_color: str | None = Field('#ffffff', description="The button text color of the widget")
    border_color: str | None = Field('#e1e1e1', description="The border color of the widget")
    focus_color: str | None = Field('#000000', description="The focus color of the widget")
    border_radius: int | None = Field(None, description="The border radius of the widget")
    btn_radius: int | None = Field(None, description="The button radius of the widget")
    action_text: str | None = Field(None, description="The action text of the widget")
    start_call_text: str | None = Field(None, description="The start call text of the widget")
    end_call_text: str | None = Field(None, description="The end call text of the widget")
    expand_text: str | None = Field(None, description="The expand text of the widget")
    listening_text: str | None = Field(None, description="The text to display when the agent is listening")
    speaking_text: str | None = Field(None, description="The text to display when the agent is speaking")
    shareable_page_text: str | None = Field(None, description="The text to display when sharing")
    shareable_page_show_terms: bool | None = Field(True, description="Whether to show terms and conditions on the shareable page")
    terms_text: str | None = Field(None, description="The text to display for terms and conditions")
    terms_html: str | None = Field(None, description="The HTML to display for terms and conditions")
    terms_key: str | None = Field(None, description="The key to display for terms and conditions")
    show_avatar_when_collapsed: bool | None = Field(False, description="Whether to show the avatar when the widget is collapsed")
    disable_banner: bool | None = Field(False, description="Whether to disable the banner")
    override_link: str | None = Field(None, description="The override link for the widget")
    markdown_link_allowed_hosts: list[AllowlistItem] | None = Field(None, description="List of allowed hostnames for clickable markdown links. Use { hostname: '*' } to allow any domain. Empty means no links are allowed.")
    markdown_link_include_www: bool | None = Field(True, description="Whether to automatically include www. variants of allowed hosts")
    markdown_link_allow_http: bool | None = Field(True, description="Whether to allow http:// in addition to https:// for allowed hosts")
    mic_muting_enabled: bool | None = Field(False, description="Whether to enable mic muting")
    transcript_enabled: bool | None = Field(False, description="Whether the widget should show the conversation transcript as it goes on")
    text_input_enabled: bool | None = Field(True, description="Whether the user should be able to send text messages")
    conversation_mode_toggle_enabled: bool | None = Field(False, description="Whether to enable the conversation mode toggle in the widget")
    default_expanded: bool | None = Field(False, description="Whether the widget should be expanded by default")
    always_expanded: bool | None = Field(False, description="Whether the widget should always be expanded")
    dismissible: bool | None = Field(False, description="Whether the widget can be dismissed by the user")
    show_agent_status: bool | None = Field(False, description="Whether to show agent working/done/error status during tool use")
    show_conversation_id: bool | None = Field(True, description="Whether to show the conversation ID after disconnection.")
    strip_audio_tags: bool | None = Field(True, description="Whether to strip audio markup from messages.")
    syntax_highlight_theme: Literal["light", "dark"] | None = Field(None, description="Theme for code block syntax highlighting. Defaults to auto-detection by the widget when not set.")
    text_contents: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents | None = Field(None, description="Text contents of the widget")
    styles: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles | None = Field(None, description="Styles for the widget")
    language_selector: bool | None = Field(False, description="Whether to show the language selector")
    supports_text_only: bool | None = Field(True, description="Whether the widget can switch to text only mode")
    custom_avatar_path: str | None = Field(None, description="The custom avatar path")
    language_presets: dict[str, WidgetLanguagePreset] | None = Field(None, description="Language presets for the widget")

class RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettings(PermissiveModel):
    evaluation: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsEvaluation | None = Field(None, description="Settings for evaluation")
    widget: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidget | None = Field(None, description="Configuration for the widget")
    data_collection: dict[str, LiteralJsonSchemaProperty] | None = Field(None, description="Data collection settings")
    overrides: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverrides | None = Field(None, description="Additional overrides for the agent during conversation initiation")
    workspace_overrides: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides | None = Field(None, description="Workspace overrides for the agent")
    testing: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsTesting | None = Field(None, description="Testing configuration for the agent")
    archived: bool | None = Field(False, description="Whether the agent is archived")
    guardrails: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrails | None = Field(None, description="Guardrails configuration for the agent")
    summary_language: str | None = Field(None, description="Language for all conversation analysis outputs (summaries, titles, evaluation rationales, data collection rationales). If not set, the language will be inferred from the conversation. Must be one of the supported conversation languages.")
    auth: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsAuth | None = Field(None, description="Settings for authentication")
    call_limits: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsCallLimits | None = Field(None, description="Call limits for the agent")
    privacy: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacy | None = Field(None, description="Privacy settings for the agent")

class WorkflowEndNodeModelInput(PermissiveModel):
    type_: Literal["end"] | None = Field('end', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")

class WorkflowLlmConditionModelInput(PermissiveModel):
    label: str | None = Field(None, description="Optional human-readable label for the condition used throughout the UI.")
    type_: Literal["llm"] | None = Field('llm', validation_alias="type", serialization_alias="type")
    condition: str = Field(..., description="Condition to evaluate")

class WorkflowPhoneNumberNodeModelInput(PermissiveModel):
    custom_sip_headers: list[CustomSipHeader | CustomSipHeaderWithDynamicVariable] | None = Field(None, description="Custom SIP headers to include when transferring the call. Each header can be either a static value or a dynamic variable reference.", max_length=20)
    type_: Literal["phone_number"] | None = Field('phone_number', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")
    transfer_destination: PhoneNumberTransferDestination | SipUriTransferDestination | PhoneNumberDynamicVariableTransferDestination | SipUriDynamicVariableTransferDestination
    transfer_type: Literal["blind", "conference", "sip_refer"] | None = 'conference'
    post_dial_digits: PostDialDigitsStatic | PostDialDigitsDynamicVariable | None = Field(None, description="DTMF digits to send after call connects (e.g., 'ww1234' for extension). Can be either a static value or a dynamic variable reference. Use 'w' for 0.5s pause.")

class WorkflowResultConditionModelInput(PermissiveModel):
    label: str | None = Field(None, description="Optional human-readable label for the condition used throughout the UI.")
    type_: Literal["result"] | None = Field('result', validation_alias="type", serialization_alias="type")
    successful: bool = Field(..., description="Whether all tools in the previously executed tool node were executed successfully.")

class WorkflowStandaloneAgentNodeModelInput(PermissiveModel):
    type_: Literal["standalone_agent"] | None = Field('standalone_agent', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")
    agent_id: str = Field(..., description="The ID of the agent to transfer the conversation to.")
    delay_ms: int | None = Field(0, description="Artificial delay in milliseconds applied before transferring the conversation.")
    transfer_message: str | None = Field(None, description="Optional message sent to the user before the transfer is initiated.")
    enable_transferred_agent_first_message: bool | None = Field(False, description="Whether to enable the transferred agent to send its configured first message after the transfer.")

class WorkflowStartNodeModelInput(PermissiveModel):
    type_: Literal["start"] | None = Field('start', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")

class WorkflowToolEdgeStepModel(PermissiveModel):
    step_latency_secs: float
    type_: Literal["edge"] | None = Field('edge', validation_alias="type", serialization_alias="type")
    edge_id: str
    target_node_id: str

class WorkflowToolLocator(PermissiveModel):
    tool_id: str

class WorkflowToolMaxIterationsExceededStepModel(PermissiveModel):
    step_latency_secs: float
    type_: Literal["max_iterations_exceeded"] | None = Field('max_iterations_exceeded', validation_alias="type", serialization_alias="type")
    max_iterations: int

class WorkflowToolNodeModelInput(PermissiveModel):
    type_: Literal["tool"] | None = Field('tool', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")
    tools: list[WorkflowToolLocator] | None = Field(None, description="List of tools to execute in parallel. The entire node is considered successful if all tools are executed successfully.")

class WorkflowUnconditionalModelInput(PermissiveModel):
    label: str | None = Field(None, description="Optional human-readable label for the condition used throughout the UI.")
    type_: Literal["unconditional"] | None = Field('unconditional', validation_alias="type", serialization_alias="type")

class AgentConfigApiModelWorkflowOverrideInput(PermissiveModel):
    first_message: str | None = Field(None, description="If non-empty, the first message the agent will say. If empty, the agent waits for the user to start the discussion.")
    language: str | None = Field(None, description="Language of the agent - used for ASR and TTS")
    hinglish_mode: bool | None = Field(None, description="When enabled and language is Hindi, the agent will respond in Hinglish")
    dynamic_variables: DynamicVariablesConfigWorkflowOverride | None = Field(None, description="Configuration for dynamic variables")
    disable_first_message_interruptions: bool | None = Field(None, description="If true, the user will not be able to interrupt the agent while the first message is being delivered.")
    prompt: PromptAgentApiModelWorkflowOverrideInput | None = Field(None, description="The prompt for the agent")

class ApiIntegrationWebhookOverridesInput(PermissiveModel):
    """A whitelist of fields that can be overridden by users when
configuring an API Integration Webhook Tool."""
    schema_overrides: dict[str, ConstantSchemaOverride | DynamicVariableSchemaOverride | LlmSchemaOverride] | None = None
    path_params_schema: dict[str, LiteralOverride] | None = None
    query_params_schema: QueryOverride | None = None
    request_body_schema: ObjectOverrideInput | None = None
    request_headers: dict[str, str | ConvAiDynamicVariable] | None = None
    response_filter_mode: Literal["all", "allow"] | None = None
    response_filters: list[str] | None = None

class ApiIntegrationWebhookToolConfigInput(PermissiveModel):
    type_: Literal["api_integration_webhook"] | None = Field('api_integration_webhook', validation_alias="type", serialization_alias="type")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str = Field(..., description="Description of when the tool should be used and what it does.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete. Must be between 5 and 120 seconds (inclusive).", ge=5, le=120)
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    dynamic_variables: DynamicVariablesConfig | None = Field(None, description="Configuration for dynamic variables")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field('immediate', description="Determines when and how the tool executes: 'immediate' executes the tool right away when requested by the LLM, 'post_tool_speech' waits for the agent to finish speaking before executing, 'async' runs the tool in the background without blocking - best for long-running operations.")
    tool_version: str | None = Field('1.0.0', description="The version of the API integration tool")
    api_integration_id: str
    api_integration_connection_id: str
    api_schema_overrides: ApiIntegrationWebhookOverridesInput | None = Field(None, description="User overrides applied on top of the base api_schema")

class ArrayJsonSchemaPropertyInput(StrictModel):
    type_: Literal["array"] | None = Field('array', validation_alias="type", serialization_alias="type")
    description: str | None = ''
    items: LiteralJsonSchemaProperty | ObjectJsonSchemaPropertyInput | ArrayJsonSchemaPropertyInput

class AstAndOperatorNodeInput(PermissiveModel):
    type_: Literal["and_operator"] | None = Field('and_operator', validation_alias="type", serialization_alias="type")
    children: list[AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput] = Field(..., description="Child nodes of the logical operator.", min_length=2)

class AstConditionalOperatorNodeInput(PermissiveModel):
    type_: Literal["conditional_operator"] | None = Field('conditional_operator', validation_alias="type", serialization_alias="type")
    condition: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Condition deciding which expression should be selected.")
    true_expression: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., validation_alias="trueExpression", serialization_alias="trueExpression", description="Expression selected if the condition is true.")
    false_expression: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., validation_alias="falseExpression", serialization_alias="falseExpression", description="Expression selected if the condition is false.")

class AstEqualsOperatorNodeInput(PermissiveModel):
    type_: Literal["eq_operator"] | None = Field('eq_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstGreaterThanOperatorNodeInput(PermissiveModel):
    type_: Literal["gt_operator"] | None = Field('gt_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstGreaterThanOrEqualsOperatorNodeInput(PermissiveModel):
    type_: Literal["gte_operator"] | None = Field('gte_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstLessThanOperatorNodeInput(PermissiveModel):
    type_: Literal["lt_operator"] | None = Field('lt_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstLessThanOrEqualsOperatorNodeInput(PermissiveModel):
    type_: Literal["lte_operator"] | None = Field('lte_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstNotEqualsOperatorNodeInput(PermissiveModel):
    type_: Literal["neq_operator"] | None = Field('neq_operator', validation_alias="type", serialization_alias="type")
    left: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Left operand of the binary operator.")
    right: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Right operand of the binary operator.")

class AstOrOperatorNodeInput(PermissiveModel):
    type_: Literal["or_operator"] | None = Field('or_operator', validation_alias="type", serialization_alias="type")
    children: list[AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput] = Field(..., description="Child nodes of the logical operator.", min_length=2)

class ClientToolConfigInput(PermissiveModel):
    """A client tool is one that sends an event to the user's client to trigger something client side"""
    type_: Literal["client"] | None = Field('client', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str = Field(..., description="Description of when the tool should be used and what it does.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete. Must be between 1 and 120 seconds (inclusive).", ge=1, le=120)
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    parameters: ObjectJsonSchemaPropertyInput | None = Field(None, description="Schema for any parameters to pass to the client")
    expects_response: bool | None = Field(False, description="If true, calling this tool should block the conversation until the client responds with some response which is passed to the llm. If false then we will continue the conversation without waiting for the client to respond, this is useful to show content to a user but not block the conversation")
    dynamic_variables: DynamicVariablesConfig | None = Field(None, description="Configuration for dynamic variables")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field('immediate', description="Determines when and how the tool executes: 'immediate' executes the tool right away when requested by the LLM, 'post_tool_speech' waits for the agent to finish speaking before executing, 'async' runs the tool in the background without blocking - best for long-running operations.")

class ConversationHistoryTranscriptCommonModelInput(PermissiveModel):
    role: Literal["user", "agent"]
    agent_metadata: AgentMetadata | None = None
    message: str | None = None
    multivoice_message: ConversationHistoryMultivoiceMessageModel | None = None
    tool_calls: list[ConversationHistoryTranscriptToolCallCommonModelInput] | None = None
    tool_results: list[ConversationHistoryTranscriptOtherToolsResultCommonModel | ConversationHistoryTranscriptSystemToolResultCommonModelInput | ConversationHistoryTranscriptApiIntegrationWebhookToolsResultCommonModelInput | ConversationHistoryTranscriptWorkflowToolsResultCommonModelInput] | None = None
    feedback: UserFeedback | None = None
    llm_override: str | None = None
    time_in_call_secs: int
    conversation_turn_metrics: ConversationTurnMetrics | None = None
    rag_retrieval_info: RagRetrievalInfo | None = None
    llm_usage: LlmUsageInput | None = None
    interrupted: bool | None = False
    original_message: str | None = None
    source_medium: Literal["audio", "text", "image", "file"] | None = None

class ConversationHistoryTranscriptWorkflowToolsResultCommonModelInput(PermissiveModel):
    request_id: str
    tool_name: str
    result_value: str
    is_error: bool
    tool_has_been_called: bool
    tool_latency_secs: float | None = 0
    error_type: str | None = ''
    raw_error_message: str | None = ''
    dynamic_variable_updates: list[DynamicVariableUpdateCommonModel] | None = None
    type_: Literal["workflow"] = Field(..., validation_alias="type", serialization_alias="type")
    result: WorkflowToolResponseModelInput | None = None

class ConversationalConfigApiModelWorkflowOverrideInput(PermissiveModel):
    asr: AsrConversationalConfigWorkflowOverride | None = Field(None, description="Configuration for conversational transcription")
    turn: TurnConfigWorkflowOverride | None = Field(None, description="Configuration for turn detection")
    tts: TtsConversationalConfigWorkflowOverrideInput | None = Field(None, description="Configuration for conversational text to speech")
    conversation: ConversationConfigWorkflowOverride | None = Field(None, description="Configuration for conversational events")
    language_presets: dict[str, LanguagePresetInput] | None = Field(None, description="Language presets for conversations")
    vad: VadConfigWorkflowOverride | None = Field(None, description="Configuration for voice activity detection")
    agent: AgentConfigApiModelWorkflowOverrideInput | None = Field(None, description="Agent specific configuration")

class CreateAgentRouteBodyConversationConfig(PermissiveModel):
    """Conversation configuration including ASR, TTS, turn handling, and agent prompt settings"""
    asr: CreateAgentRouteBodyConversationConfigAsr | None = Field(None, description="Configuration for conversational transcription")
    turn: CreateAgentRouteBodyConversationConfigTurn | None = Field(None, description="Configuration for turn detection")
    tts: CreateAgentRouteBodyConversationConfigTts | None = Field(None, description="Configuration for conversational text to speech")
    conversation: CreateAgentRouteBodyConversationConfigConversation | None = Field(None, description="Configuration for conversational events")
    language_presets: dict[str, LanguagePresetInput] | None = Field(None, description="Language presets for conversations")
    vad: CreateAgentRouteBodyConversationConfigVad | None = Field(None, description="Configuration for voice activity detection")
    agent: CreateAgentRouteBodyConversationConfigAgent | None = Field(None, description="Agent specific configuration")

class CreateAgentRouteBodyConversationConfigAgent(PermissiveModel):
    """Agent specific configuration"""
    first_message: str | None = Field('', description="If non-empty, the first message the agent will say. If empty, the agent waits for the user to start the discussion.")
    language: str | None = Field('en', description="Language of the agent - used for ASR and TTS")
    hinglish_mode: bool | None = Field(False, description="When enabled and language is Hindi, the agent will respond in Hinglish")
    dynamic_variables: CreateAgentRouteBodyConversationConfigAgentDynamicVariables | None = Field(None, description="Configuration for dynamic variables")
    disable_first_message_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while the first message is being delivered.")
    prompt: CreateAgentRouteBodyConversationConfigAgentPrompt | None = Field(None, description="The prompt for the agent")

class CreateAgentRouteBodyConversationConfigAgentPrompt(PermissiveModel):
    """The prompt for the agent"""
    prompt: str | None = Field('', description="The prompt for the agent")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field('gemini-2.5-flash', description="The LLM to query with the prompt and the chat history. If using data residency, the LLM must be supported in the data residency environment")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Reasoning effort of the model. Only available for some models.")
    thinking_budget: int | None = Field(None, description="Max number of tokens used for thinking. Use 0 to turn off if supported by the model.")
    temperature: float | None = Field(0.0, description="The temperature for the LLM")
    max_tokens: int | None = Field(-1, description="If greater than 0, maximum number of tokens the LLM can predict")
    tool_ids: list[str] | None = Field(None, description="A list of IDs of tools used by the agent")
    built_in_tools: CreateAgentRouteBodyConversationConfigAgentPromptBuiltInTools | None = Field(None, description="Built-in system tools to be used by the agent")
    mcp_server_ids: list[str] | None = Field(None, description="A list of MCP server ids to be used by the agent", max_length=10)
    native_mcp_server_ids: list[str] | None = Field(None, description="A list of Native MCP server ids to be used by the agent", max_length=10)
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(None, description="A list of knowledge bases to be used by the agent")
    custom_llm: CreateAgentRouteBodyConversationConfigAgentPromptCustomLlm | None = Field(None, description="Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'")
    ignore_default_personality: bool | None = Field(False, description="Whether to remove the default personality lines from the system prompt")
    rag: CreateAgentRouteBodyConversationConfigAgentPromptRag | None = Field(None, description="Configuration for RAG")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Timezone for displaying current time in system prompt. If set, the current time will be included in the system prompt using this timezone. Must be a valid timezone name (e.g., 'America/New_York', 'Europe/London', 'UTC').")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(None, description="Configuration for backup LLM cascading. Can be disabled, use system defaults, or specify custom order.")
    cascade_timeout_seconds: float | None = Field(8.0, description="Time in seconds before cascading to backup LLM. Must be between 2 and 15 seconds.", ge=2.0, le=15.0)
    tools: list[WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput | ApiIntegrationWebhookToolConfigInput | SmbToolConfig] | None = Field(None, description="A list of tools that the agent can use over the course of the conversation, use tool_ids instead")

class CreateAgentRouteBodyWorkflow(PermissiveModel):
    """Workflow definition with nodes and edges"""
    edges: dict[str, WorkflowEdgeModelInput] | None = None
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(None, min_length=1)
    prevent_subagent_loops: bool | None = Field(False, description="Whether to prevent loops in the workflow execution.")

class McpToolConfigInput(PermissiveModel):
    """An MCP tool configuration that can be used to call MCP servers"""
    type_: Literal["mcp"] | None = Field('mcp', validation_alias="type", serialization_alias="type")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str = Field(..., description="Description of when the tool should be used and what it does.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete.")
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    integration_type: Literal["mcp_server", "mcp_integration"] = Field(..., description="The type of MCP tool")
    parameters: ObjectJsonSchemaPropertyInput | None = Field(None, description="Schema for any parameters the LLM needs to provide to the MCP tool.")
    approval_policy: Literal["auto_approve_all", "require_approval_all", "require_approval_per_tool"] | None = Field('require_approval_all', description="The approval policy for the MCP tool")
    mcp_tool_name: str = Field(..., description="The name of the MCP tool to call")
    mcp_tool_description: str = Field(..., description="The description of the MCP tool to call")
    mcp_server_id: str = Field(..., description="The id of the MCP server to call")
    mcp_server_name: str = Field(..., description="The name of the MCP server to call")
    mcp_input_schema: dict[str, Any] | None = Field(None, description="Original inputSchema dict for consistent hashing")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field('immediate', description="Determines when and how the tool executes: 'immediate' executes the tool right away when requested by the LLM, 'post_tool_speech' waits for the agent to finish speaking before executing, 'async' runs the tool in the background without blocking - best for long-running operations.")
    input_overrides: dict[str, ConstantSchemaOverride | DynamicVariableSchemaOverride | LlmSchemaOverride] | None = Field(None, description="Input parameter overrides for this tool")

class ObjectJsonSchemaPropertyInput(StrictModel):
    type_: Literal["object"] | None = Field('object', validation_alias="type", serialization_alias="type")
    required: list[str] | None = None
    description: str | None = ''
    properties: dict[str, LiteralJsonSchemaProperty | ObjectJsonSchemaPropertyInput | ArrayJsonSchemaPropertyInput] | None = None
    required_constraints: RequiredConstraints | None = None

class ObjectOverrideInput(PermissiveModel):
    description: str | None = None
    properties: dict[str, LiteralOverride | ObjectOverrideInput] | None = None
    required: list[str] | None = None

class PromptAgentApiModelWorkflowOverrideInput(PermissiveModel):
    prompt: str | None = Field(None, description="The prompt for the agent")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(None, description="The LLM to query with the prompt and the chat history. If using data residency, the LLM must be supported in the data residency environment")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Reasoning effort of the model. Only available for some models.")
    thinking_budget: int | None = Field(None, description="Max number of tokens used for thinking. Use 0 to turn off if supported by the model.")
    temperature: float | None = Field(None, description="The temperature for the LLM")
    max_tokens: int | None = Field(None, description="If greater than 0, maximum number of tokens the LLM can predict")
    tool_ids: list[str] | None = Field(None, description="A list of IDs of tools used by the agent")
    built_in_tools: BuiltInToolsWorkflowOverrideInput | None = Field(None, description="Built-in system tools to be used by the agent")
    mcp_server_ids: list[str] | None = Field(None, description="A list of MCP server ids to be used by the agent")
    native_mcp_server_ids: list[str] | None = Field(None, description="A list of Native MCP server ids to be used by the agent")
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(None, description="A list of knowledge bases to be used by the agent")
    custom_llm: CustomLlm | None = Field(None, description="Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'")
    ignore_default_personality: bool | None = Field(None, description="Whether to remove the default personality lines from the system prompt")
    rag: RagConfigWorkflowOverride | None = Field(None, description="Configuration for RAG")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Timezone for displaying current time in system prompt. If set, the current time will be included in the system prompt using this timezone. Must be a valid timezone name (e.g., 'America/New_York', 'Europe/London', 'UTC').")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(None, description="Configuration for backup LLM cascading. Can be disabled, use system defaults, or specify custom order.")
    cascade_timeout_seconds: float | None = Field(None, description="Time in seconds before cascading to backup LLM. Must be between 2 and 15 seconds.")
    tools: list[WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput | ApiIntegrationWebhookToolConfigInput | SmbToolConfig] | None = Field(None, description="A list of tools that the agent can use over the course of the conversation, use tool_ids instead")

class ResubmitTestsRouteBodyAgentConfigOverride(PermissiveModel):
    """Agent configuration overrides for test resubmission"""
    conversation_config: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfig
    platform_settings: ResubmitTestsRouteBodyAgentConfigOverridePlatformSettings
    workflow: ResubmitTestsRouteBodyAgentConfigOverrideWorkflow | None = None

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfig(PermissiveModel):
    asr: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAsr | None = Field(None, description="Configuration for conversational transcription")
    turn: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurn | None = Field(None, description="Configuration for turn detection")
    tts: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTts | None = Field(None, description="Configuration for conversational text to speech")
    conversation: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigConversation | None = Field(None, description="Configuration for conversational events")
    language_presets: dict[str, LanguagePresetInput] | None = Field(None, description="Language presets for conversations")
    vad: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigVad | None = Field(None, description="Configuration for voice activity detection")
    agent: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgent | None = Field(None, description="Agent specific configuration")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgent(PermissiveModel):
    """Agent specific configuration"""
    first_message: str | None = Field('', description="If non-empty, the first message the agent will say. If empty, the agent waits for the user to start the discussion.")
    language: str | None = Field('en', description="Language of the agent - used for ASR and TTS")
    hinglish_mode: bool | None = Field(False, description="When enabled and language is Hindi, the agent will respond in Hinglish")
    dynamic_variables: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables | None = Field(None, description="Configuration for dynamic variables")
    disable_first_message_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while the first message is being delivered.")
    prompt: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPrompt | None = Field(None, description="The prompt for the agent")

class ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPrompt(PermissiveModel):
    """The prompt for the agent"""
    prompt: str | None = Field('', description="The prompt for the agent")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field('gemini-2.5-flash', description="The LLM to query with the prompt and the chat history. If using data residency, the LLM must be supported in the data residency environment")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Reasoning effort of the model. Only available for some models.")
    thinking_budget: int | None = Field(None, description="Max number of tokens used for thinking. Use 0 to turn off if supported by the model.")
    temperature: float | None = Field(0.0, description="The temperature for the LLM")
    max_tokens: int | None = Field(-1, description="If greater than 0, maximum number of tokens the LLM can predict")
    tool_ids: list[str] | None = Field(None, description="A list of IDs of tools used by the agent")
    built_in_tools: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools | None = Field(None, description="Built-in system tools to be used by the agent")
    mcp_server_ids: list[str] | None = Field(None, description="A list of MCP server ids to be used by the agent", max_length=10)
    native_mcp_server_ids: list[str] | None = Field(None, description="A list of Native MCP server ids to be used by the agent", max_length=10)
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(None, description="A list of knowledge bases to be used by the agent")
    custom_llm: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm | None = Field(None, description="Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'")
    ignore_default_personality: bool | None = Field(False, description="Whether to remove the default personality lines from the system prompt")
    rag: ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag | None = Field(None, description="Configuration for RAG")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Timezone for displaying current time in system prompt. If set, the current time will be included in the system prompt using this timezone. Must be a valid timezone name (e.g., 'America/New_York', 'Europe/London', 'UTC').")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(None, description="Configuration for backup LLM cascading. Can be disabled, use system defaults, or specify custom order.")
    cascade_timeout_seconds: float | None = Field(8.0, description="Time in seconds before cascading to backup LLM. Must be between 2 and 15 seconds.", ge=2.0, le=15.0)
    tools: list[WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput | ApiIntegrationWebhookToolConfigInput | SmbToolConfig] | None = Field(None, description="A list of tools that the agent can use over the course of the conversation, use tool_ids instead")

class ResubmitTestsRouteBodyAgentConfigOverrideWorkflow(PermissiveModel):
    edges: dict[str, WorkflowEdgeModelInput] | None = None
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(None, min_length=1)
    prevent_subagent_loops: bool | None = Field(False, description="Whether to prevent loops in the workflow execution.")

class RunAgentTestSuiteRouteBodyAgentConfigOverride(PermissiveModel):
    """Agent configuration overrides for test execution"""
    conversation_config: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfig
    platform_settings: RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettings
    workflow: RunAgentTestSuiteRouteBodyAgentConfigOverrideWorkflow | None = None

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfig(PermissiveModel):
    asr: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAsr | None = Field(None, description="Configuration for conversational transcription")
    turn: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurn | None = Field(None, description="Configuration for turn detection")
    tts: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTts | None = Field(None, description="Configuration for conversational text to speech")
    conversation: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigConversation | None = Field(None, description="Configuration for conversational events")
    language_presets: dict[str, LanguagePresetInput] | None = Field(None, description="Language presets for conversations")
    vad: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigVad | None = Field(None, description="Configuration for voice activity detection")
    agent: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgent | None = Field(None, description="Agent specific configuration")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgent(PermissiveModel):
    """Agent specific configuration"""
    first_message: str | None = Field('', description="If non-empty, the first message the agent will say. If empty, the agent waits for the user to start the discussion.")
    language: str | None = Field('en', description="Language of the agent - used for ASR and TTS")
    hinglish_mode: bool | None = Field(False, description="When enabled and language is Hindi, the agent will respond in Hinglish")
    dynamic_variables: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables | None = Field(None, description="Configuration for dynamic variables")
    disable_first_message_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while the first message is being delivered.")
    prompt: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPrompt | None = Field(None, description="The prompt for the agent")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPrompt(PermissiveModel):
    """The prompt for the agent"""
    prompt: str | None = Field('', description="The prompt for the agent")
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field('gemini-2.5-flash', description="The LLM to query with the prompt and the chat history. If using data residency, the LLM must be supported in the data residency environment")
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Reasoning effort of the model. Only available for some models.")
    thinking_budget: int | None = Field(None, description="Max number of tokens used for thinking. Use 0 to turn off if supported by the model.")
    temperature: float | None = Field(0.0, description="The temperature for the LLM")
    max_tokens: int | None = Field(-1, description="If greater than 0, maximum number of tokens the LLM can predict")
    tool_ids: list[str] | None = Field(None, description="A list of IDs of tools used by the agent")
    built_in_tools: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools | None = Field(None, description="Built-in system tools to be used by the agent")
    mcp_server_ids: list[str] | None = Field(None, description="A list of MCP server ids to be used by the agent", max_length=10)
    native_mcp_server_ids: list[str] | None = Field(None, description="A list of Native MCP server ids to be used by the agent", max_length=10)
    knowledge_base: list[KnowledgeBaseLocator] | None = Field(None, description="A list of knowledge bases to be used by the agent")
    custom_llm: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm | None = Field(None, description="Definition for a custom LLM if LLM field is set to 'CUSTOM_LLM'")
    ignore_default_personality: bool | None = Field(False, description="Whether to remove the default personality lines from the system prompt")
    rag: RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag | None = Field(None, description="Configuration for RAG")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Timezone for displaying current time in system prompt. If set, the current time will be included in the system prompt using this timezone. Must be a valid timezone name (e.g., 'America/New_York', 'Europe/London', 'UTC').")
    backup_llm_config: BackupLlmDefault | BackupLlmDisabled | BackupLlmOverride | None = Field(None, description="Configuration for backup LLM cascading. Can be disabled, use system defaults, or specify custom order.")
    cascade_timeout_seconds: float | None = Field(8.0, description="Time in seconds before cascading to backup LLM. Must be between 2 and 15 seconds.", ge=2.0, le=15.0)
    tools: list[WebhookToolConfigInput | ClientToolConfigInput | SystemToolConfigInput | McpToolConfigInput | ApiIntegrationWebhookToolConfigInput | SmbToolConfig] | None = Field(None, description="A list of tools that the agent can use over the course of the conversation, use tool_ids instead")

class RunAgentTestSuiteRouteBodyAgentConfigOverrideWorkflow(PermissiveModel):
    edges: dict[str, WorkflowEdgeModelInput] | None = None
    nodes: dict[str, WorkflowStartNodeModelInput | WorkflowEndNodeModelInput | WorkflowPhoneNumberNodeModelInput | WorkflowOverrideAgentNodeModelInput | WorkflowStandaloneAgentNodeModelInput | WorkflowToolNodeModelInput] | None = Field(None, min_length=1)
    prevent_subagent_loops: bool | None = Field(False, description="Whether to prevent loops in the workflow execution.")

class TestFromConversationMetadataInput(PermissiveModel):
    conversation_id: str
    agent_id: str
    branch_id: str | None = None
    workflow_node_id: str | None = None
    original_agent_reply: list[ConversationHistoryTranscriptCommonModelInput] | None = None

class WebhookToolApiSchemaConfigInput(PermissiveModel):
    request_headers: dict[str, str | ConvAiSecretLocator | ConvAiDynamicVariable | ConvAiEnvVarLocator] | None = Field(None, description="Headers that should be included in the request")
    url: str = Field(..., description="The URL that the webhook will be sent to. May include path parameters, e.g. https://example.com/agents/{agent_id}")
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | None = Field('GET', description="The HTTP method to use for the webhook")
    path_params_schema: dict[str, LiteralJsonSchemaProperty] | None = Field(None, description="Schema for path parameters, if any. The keys should match the placeholders in the URL.")
    query_params_schema: QueryParamsJsonSchema | None = Field(None, description="Schema for any query params, if any. These will be added to end of the URL as query params. Note: properties in a query param must all be literal types")
    request_body_schema: ObjectJsonSchemaPropertyInput | None = Field(None, description="Schema for the body parameters, if any. Used for POST/PATCH/PUT requests. The schema should be an object which will be sent as the json body")
    content_type: Literal["application/json", "application/x-www-form-urlencoded"] | None = Field('application/json', description="Content type for the request body. Only applies to POST/PUT/PATCH requests.")
    auth_connection: AuthConnectionLocator | EnvironmentAuthConnectionLocator | None = Field(None, description="Optional auth connection to use for authentication with this webhook")

class WebhookToolConfigInput(PermissiveModel):
    """A webhook tool is a tool that calls an external webhook from our server"""
    type_: Literal["webhook"] | None = Field('webhook', validation_alias="type", serialization_alias="type", description="The type of tool")
    name: str = Field(..., min_length=0, pattern="^[a-zA-Z0-9_-]{1,64}$")
    description: str = Field(..., description="Description of when the tool should be used and what it does.", min_length=0)
    response_timeout_secs: int | None = Field(20, description="The maximum time in seconds to wait for the tool call to complete. Must be between 5 and 120 seconds (inclusive).", ge=5, le=120)
    disable_interruptions: bool | None = Field(False, description="If true, the user will not be able to interrupt the agent while this tool is running.")
    force_pre_tool_speech: bool | None = Field(False, description="If true, the agent will speak before the tool call.")
    assignments: list[DynamicVariableAssignment] | None = Field(None, description="Configuration for extracting values from tool responses and assigning them to dynamic variables")
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined tool call sound type to play during tool execution. If not specified, no tool call sound will be played.")
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field('auto', description="Determines when the tool call sound should play. 'auto' only plays when there's pre-tool speech, 'always' plays for every tool call.")
    tool_error_handling_mode: Literal["auto", "summarized", "passthrough", "hide"] | None = Field('auto', description="Controls how tool errors are processed before being shared with the agent. 'auto' determines handling based on tool type (summarized for native integrations, hide for others), 'summarized' sends an LLM-generated summary, 'passthrough' sends the raw error, 'hide' does not share the error with the agent.")
    dynamic_variables: DynamicVariablesConfig | None = Field(None, description="Configuration for dynamic variables")
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field('immediate', description="Determines when and how the tool executes: 'immediate' executes the tool right away when requested by the LLM, 'post_tool_speech' waits for the agent to finish speaking before executing, 'async' runs the tool in the background without blocking - best for long-running operations.")
    api_schema: WebhookToolApiSchemaConfigInput = Field(..., description="The schema for the outgoing webhoook, including parameters and URL specification")

class WorkflowEdgeModelInput(PermissiveModel):
    source: str = Field(..., description="ID of the source node.")
    target: str = Field(..., description="ID of the target node.")
    forward_condition: WorkflowUnconditionalModelInput | WorkflowLlmConditionModelInput | WorkflowResultConditionModelInput | WorkflowExpressionConditionModelInput | None = Field(None, description="Condition that must be met for the edge to be traversed in the forward direction (source to target).")
    backward_condition: WorkflowUnconditionalModelInput | WorkflowLlmConditionModelInput | WorkflowResultConditionModelInput | WorkflowExpressionConditionModelInput | None = Field(None, description="Condition that must be met for the edge to be traversed in the backward direction (target to source).")

class WorkflowExpressionConditionModelInput(PermissiveModel):
    label: str | None = Field(None, description="Optional human-readable label for the condition used throughout the UI.")
    type_: Literal["expression"] | None = Field('expression', validation_alias="type", serialization_alias="type")
    expression: AstStringNodeInput | AstNumberNodeInput | AstBooleanNodeInput | AstllmNodeInput | AstDynamicVariableNodeInput | AstOrOperatorNodeInput | AstAndOperatorNodeInput | AstEqualsOperatorNodeInput | AstNotEqualsOperatorNodeInput | AstGreaterThanOperatorNodeInput | AstLessThanOperatorNodeInput | AstGreaterThanOrEqualsOperatorNodeInput | AstLessThanOrEqualsOperatorNodeInput | AstConditionalOperatorNodeInput = Field(..., description="Expression to evaluate.")

class WorkflowOverrideAgentNodeModelInput(PermissiveModel):
    conversation_config: ConversationalConfigApiModelWorkflowOverrideInput | None = Field(None, description="Configuration overrides applied while the subagent is conducting the conversation.")
    additional_prompt: str | None = Field(None, description="Specific goal for this subagent. It will be added to the system prompt and can be used to further refine the agent's behavior in this specific context.")
    additional_knowledge_base: list[KnowledgeBaseLocator] | None = Field(None, description="Additional knowledge base documents that the subagent has access to. These will be used in addition to the main agent's documents.")
    additional_tool_ids: list[str] | None = Field(None, description="IDs of additional tools that the subagent has access to. These will be used in addition to the main agent's tools.")
    type_: Literal["override_agent"] | None = Field('override_agent', validation_alias="type", serialization_alias="type")
    position: PositionInput | None = Field(None, description="Position of the node in the workflow.")
    edge_order: list[str] | None = Field(None, description="The ids of outgoing edges in the order they should be evaluated.")
    label: str = Field(..., description="Human-readable label for the node used throughout the UI.")

class WorkflowToolNestedToolsStepModelInput(PermissiveModel):
    step_latency_secs: float
    type_: Literal["nested_tools"] | None = Field('nested_tools', validation_alias="type", serialization_alias="type")
    node_id: str
    requests: list[ConversationHistoryTranscriptToolCallCommonModelInput]
    results: list[ConversationHistoryTranscriptOtherToolsResultCommonModel | ConversationHistoryTranscriptSystemToolResultCommonModelInput | ConversationHistoryTranscriptApiIntegrationWebhookToolsResultCommonModelInput | ConversationHistoryTranscriptWorkflowToolsResultCommonModelInput]
    is_successful: bool

class WorkflowToolResponseModelInput(PermissiveModel):
    """A common model for workflow tool responses."""
    steps: list[WorkflowToolEdgeStepModel | WorkflowToolNestedToolsStepModelInput | WorkflowToolMaxIterationsExceededStepModel] | None = None


# Rebuild models to resolve forward references (required for circular refs)
AgentConfigApiModelWorkflowOverrideInput.model_rebuild()
AgentConfigOverrideInput.model_rebuild()
AgentDeploymentPercentageStrategy.model_rebuild()
AgentDeploymentRequestItem.model_rebuild()
AgentFailureResponseExample.model_rebuild()
AgentMetadata.model_rebuild()
AgentSuccessfulResponseExample.model_rebuild()
AgentTransfer.model_rebuild()
AllowlistItem.model_rebuild()
ApiIntegrationWebhookOverridesInput.model_rebuild()
ApiIntegrationWebhookToolConfigInput.model_rebuild()
ArrayJsonSchemaPropertyInput.model_rebuild()
AsrConversationalConfigWorkflowOverride.model_rebuild()
AstAndOperatorNodeInput.model_rebuild()
AstBooleanNodeInput.model_rebuild()
AstConditionalOperatorNodeInput.model_rebuild()
AstDynamicVariableNodeInput.model_rebuild()
AstEqualsOperatorNodeInput.model_rebuild()
AstGreaterThanOperatorNodeInput.model_rebuild()
AstGreaterThanOrEqualsOperatorNodeInput.model_rebuild()
AstLessThanOperatorNodeInput.model_rebuild()
AstLessThanOrEqualsOperatorNodeInput.model_rebuild()
AstllmNodeInput.model_rebuild()
AstllmNodeInputV0.model_rebuild()
AstllmNodeInputV1.model_rebuild()
AstNotEqualsOperatorNodeInput.model_rebuild()
AstNumberNodeInput.model_rebuild()
AstOrOperatorNodeInput.model_rebuild()
AstStringNodeInput.model_rebuild()
AttachedTestModel.model_rebuild()
AuthConnectionLocator.model_rebuild()
BackupLlmDefault.model_rebuild()
BackupLlmDisabled.model_rebuild()
BackupLlmOverride.model_rebuild()
BuiltInToolsWorkflowOverrideInput.model_rebuild()
ChapterContentBlockInputModel.model_rebuild()
ChapterContentParagraphTtsNodeInputModel.model_rebuild()
CheckRentalAvailabilityParams.model_rebuild()
CheckServiceAvailabilityParams.model_rebuild()
ClientToolConfigInput.model_rebuild()
ConstantSchemaOverride.model_rebuild()
ConvAiDynamicVariable.model_rebuild()
ConvAiEnvVarLocator.model_rebuild()
ConvAiSecretLocator.model_rebuild()
ConvAiUserSecretDbModel.model_rebuild()
ConversationalConfigApiModelWorkflowOverrideInput.model_rebuild()
ConversationConfigClientOverrideInput.model_rebuild()
ConversationConfigOverride.model_rebuild()
ConversationConfigWorkflowOverride.model_rebuild()
ConversationHistoryMultivoiceMessageModel.model_rebuild()
ConversationHistoryMultivoiceMessagePartModel.model_rebuild()
ConversationHistoryTranscriptApiIntegrationWebhookToolsResultCommonModelInput.model_rebuild()
ConversationHistoryTranscriptCommonModelInput.model_rebuild()
ConversationHistoryTranscriptOtherToolsResultCommonModel.model_rebuild()
ConversationHistoryTranscriptSystemToolResultCommonModelInput.model_rebuild()
ConversationHistoryTranscriptToolCallApiIntegrationWebhookDetailsInput.model_rebuild()
ConversationHistoryTranscriptToolCallClientDetails.model_rebuild()
ConversationHistoryTranscriptToolCallCommonModelInput.model_rebuild()
ConversationHistoryTranscriptToolCallMcpDetails.model_rebuild()
ConversationHistoryTranscriptToolCallWebhookDetails.model_rebuild()
ConversationHistoryTranscriptWorkflowToolsResultCommonModelInput.model_rebuild()
ConversationInitiationClientDataRequestInput.model_rebuild()
ConversationInitiationSourceInfo.model_rebuild()
ConversationTurnMetrics.model_rebuild()
CreateAgentRouteBodyConversationConfig.model_rebuild()
CreateAgentRouteBodyConversationConfigAgent.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentDynamicVariables.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPrompt.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInTools.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsEndCall.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsLanguageDetection.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsSkipTurn.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToAgent.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsTransferToNumber.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptBuiltInToolsVoicemailDetection.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptCustomLlm.model_rebuild()
CreateAgentRouteBodyConversationConfigAgentPromptRag.model_rebuild()
CreateAgentRouteBodyConversationConfigAsr.model_rebuild()
CreateAgentRouteBodyConversationConfigConversation.model_rebuild()
CreateAgentRouteBodyConversationConfigTts.model_rebuild()
CreateAgentRouteBodyConversationConfigTurn.model_rebuild()
CreateAgentRouteBodyConversationConfigTurnSoftTimeoutConfig.model_rebuild()
CreateAgentRouteBodyConversationConfigVad.model_rebuild()
CreateAgentRouteBodyPlatformSettings.model_rebuild()
CreateAgentRouteBodyPlatformSettingsAuth.model_rebuild()
CreateAgentRouteBodyPlatformSettingsCallLimits.model_rebuild()
CreateAgentRouteBodyPlatformSettingsEvaluation.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrails.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContent.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfig.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigHarassment.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigProfanity.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigReligionOrPolitics.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSelfHarm.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigSexual.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsContentConfigViolence.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsCustom.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsCustomConfig.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsFocus.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModeration.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfig.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassment.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHarassmentThreatening.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHate.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigHateThreatening.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarm.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmInstructions.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSelfHarmIntent.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexual.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigSexualMinors.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolence.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsModerationConfigViolenceGraphic.model_rebuild()
CreateAgentRouteBodyPlatformSettingsGuardrailsPromptInjection.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverrides.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverride.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgent.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideAgentPrompt.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideConversation.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTts.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurn.model_rebuild()
CreateAgentRouteBodyPlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig.model_rebuild()
CreateAgentRouteBodyPlatformSettingsPrivacy.model_rebuild()
CreateAgentRouteBodyPlatformSettingsPrivacyConversationHistoryRedaction.model_rebuild()
CreateAgentRouteBodyPlatformSettingsTesting.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWidget.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWidgetEndFeedback.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWidgetStyles.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWidgetTextContents.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWorkspaceOverrides.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook.model_rebuild()
CreateAgentRouteBodyPlatformSettingsWorkspaceOverridesWebhooks.model_rebuild()
CreateAgentRouteBodyWorkflow.model_rebuild()
CreateAssetParams.model_rebuild()
CreateClientAppointmentParams.model_rebuild()
CreateClientParams.model_rebuild()
CreateProductParams.model_rebuild()
CreateRentalBookingParams.model_rebuild()
CreateServiceParams.model_rebuild()
CreateStaffParams.model_rebuild()
CriterionItemRequest.model_rebuild()
CustomGuardrailConfig.model_rebuild()
CustomLlm.model_rebuild()
CustomSipHeader.model_rebuild()
CustomSipHeaderWithDynamicVariable.model_rebuild()
DataExtractionFieldRequest.model_rebuild()
DeleteAssetParams.model_rebuild()
DeleteCalendarEventParams.model_rebuild()
DeleteClientParams.model_rebuild()
DeleteProductParams.model_rebuild()
DeleteServiceParams.model_rebuild()
DeleteStaffParams.model_rebuild()
DialogueInput.model_rebuild()
DocxExportOptions.model_rebuild()
DynamicVariableAssignment.model_rebuild()
DynamicVariableSchemaOverride.model_rebuild()
DynamicVariablesConfig.model_rebuild()
DynamicVariablesConfigWorkflowOverride.model_rebuild()
DynamicVariableUpdateCommonModel.model_rebuild()
EndCallToolConfig.model_rebuild()
EndCallToolResultModel.model_rebuild()
EndCallTriggerAction.model_rebuild()
EnvironmentAuthConnectionLocator.model_rebuild()
EnvironmentVariableAuthConnectionValueRequest.model_rebuild()
EnvironmentVariableSecretValueRequest.model_rebuild()
ExactParameterEvaluationStrategy.model_rebuild()
ExportOptions.model_rebuild()
GetClientAppointmentsParams.model_rebuild()
GetClientByPhoneParams.model_rebuild()
GetOrCreateRagIndexRequestModel.model_rebuild()
HtmlExportOptions.model_rebuild()
ImageAvatar.model_rebuild()
InboundSipTrunkConfigRequestModel.model_rebuild()
KnowledgeBaseLocator.model_rebuild()
LanguageDetectionToolConfig.model_rebuild()
LanguageDetectionToolResultModel.model_rebuild()
LanguagePresetInput.model_rebuild()
LanguagePresetTranslation.model_rebuild()
ListAssetsParams.model_rebuild()
ListCalendarEventsParams.model_rebuild()
ListClientsParams.model_rebuild()
ListProductsParams.model_rebuild()
ListRentalServicesParams.model_rebuild()
ListServicesParams.model_rebuild()
ListStaffParams.model_rebuild()
LiteralJsonSchemaProperty.model_rebuild()
LiteralOverride.model_rebuild()
LlmInputOutputTokensUsage.model_rebuild()
LlmLiteralJsonSchemaProperty.model_rebuild()
LlmParameterEvaluationStrategy.model_rebuild()
LlmSchemaOverride.model_rebuild()
LlmTokensCategoryUsage.model_rebuild()
LlmUsageInput.model_rebuild()
MatchAnythingParameterEvaluationStrategy.model_rebuild()
McpToolApprovalHash.model_rebuild()
McpToolConfigInput.model_rebuild()
McpToolConfigOverride.model_rebuild()
MetricRecord.model_rebuild()
ObjectJsonSchemaPropertyInput.model_rebuild()
ObjectOverrideInput.model_rebuild()
OrbAvatar.model_rebuild()
OutboundCallRecipient.model_rebuild()
OutboundSipTrunkConfigRequestModel.model_rebuild()
PdfExportOptions.model_rebuild()
PhoneNumberDynamicVariableTransferDestination.model_rebuild()
PhoneNumberTransfer.model_rebuild()
PhoneNumberTransferDestination.model_rebuild()
PlayDtmfResultErrorModel.model_rebuild()
PlayDtmfResultSuccessModel.model_rebuild()
PlayDtmfToolConfig.model_rebuild()
PodcastBulletinMode.model_rebuild()
PodcastBulletinModeData.model_rebuild()
PodcastConversationMode.model_rebuild()
PodcastConversationModeData.model_rebuild()
PodcastTextSource.model_rebuild()
PodcastUrlSource.model_rebuild()
PositionInput.model_rebuild()
PostDialDigitsDynamicVariable.model_rebuild()
PostDialDigitsStatic.model_rebuild()
PromptAgentApiModelOverride.model_rebuild()
PromptAgentApiModelWorkflowOverrideInput.model_rebuild()
PromptEvaluationCriteria.model_rebuild()
PronunciationDictionaryAliasRuleRequestModel.model_rebuild()
PronunciationDictionaryPhonemeRuleRequestModel.model_rebuild()
PronunciationDictionaryVersionLocatorDbModel.model_rebuild()
PronunciationDictionaryVersionLocatorRequestModel.model_rebuild()
PydanticPronunciationDictionaryVersionLocator.model_rebuild()
QueryOverride.model_rebuild()
QueryParamsJsonSchema.model_rebuild()
RagChunkMetadata.model_rebuild()
RagConfigWorkflowOverride.model_rebuild()
RagRetrievalInfo.model_rebuild()
ReferencedToolCommonModel.model_rebuild()
RegexParameterEvaluationStrategy.model_rebuild()
RegionConfigRequest.model_rebuild()
RequiredConstraint.model_rebuild()
RequiredConstraints.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverride.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgent.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPrompt.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigAsr.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigConversation.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTts.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurn.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideConversationConfigVad.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettings.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsAuth.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsCallLimits.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsEvaluation.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrails.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverrides.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacy.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsTesting.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidget.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks.model_rebuild()
ResubmitTestsRouteBodyAgentConfigOverrideWorkflow.model_rebuild()
RetryTriggerAction.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverride.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgent.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentDynamicVariables.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPrompt.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInTools.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsEndCall.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsLanguageDetection.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsPlayKeypadTouchTone.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsSkipTurn.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToAgent.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsTransferToNumber.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptBuiltInToolsVoicemailDetection.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptCustomLlm.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAgentPromptRag.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigAsr.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigConversation.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTts.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurn.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigTurnSoftTimeoutConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideConversationConfigVad.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettings.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsAuth.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsCallLimits.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsEvaluation.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrails.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContent.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigHarassment.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigMedicalAndLegalInformation.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigProfanity.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigReligionOrPolitics.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSelfHarm.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigSexual.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsContentConfigViolence.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustom.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsCustomConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsFocus.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModeration.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassment.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHarassmentThreatening.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHate.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigHateThreatening.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarm.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmInstructions.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSelfHarmIntent.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexual.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigSexualMinors.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolence.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsModerationConfigViolenceGraphic.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsGuardrailsPromptInjection.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverrides.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverride.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgent.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideAgentPrompt.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideConversation.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTts.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurn.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsOverridesConversationConfigOverrideTurnSoftTimeoutConfig.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacy.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsPrivacyConversationHistoryRedaction.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsTesting.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidget.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetEndFeedback.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetStyles.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWidgetTextContents.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverrides.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesConversationInitiationClientDataWebhook.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverridePlatformSettingsWorkspaceOverridesWebhooks.model_rebuild()
RunAgentTestSuiteRouteBodyAgentConfigOverrideWorkflow.model_rebuild()
SearchClientsParams.model_rebuild()
SectionSource.model_rebuild()
SegmentedJsonExportOptions.model_rebuild()
SingleTestRunRequestModel.model_rebuild()
SipTrunkCredentialsRequestModel.model_rebuild()
SipUriDynamicVariableTransferDestination.model_rebuild()
SipUriTransferDestination.model_rebuild()
SkipTurnToolConfig.model_rebuild()
SkipTurnToolResponseModel.model_rebuild()
SmbToolConfig.model_rebuild()
SoftTimeoutConfigOverride.model_rebuild()
SoftTimeoutConfigWorkflowOverride.model_rebuild()
SongSection.model_rebuild()
SrtExportOptions.model_rebuild()
SuggestedAudioTag.model_rebuild()
SupportedVoice.model_rebuild()
SystemToolConfigInput.model_rebuild()
TestFromConversationMetadataInput.model_rebuild()
TestToolResultModel.model_rebuild()
TimeRange.model_rebuild()
ToolMockConfig.model_rebuild()
TransferBranchInfoDefaultingToMain.model_rebuild()
TransferBranchInfoTrafficSplit.model_rebuild()
TransferToAgentToolConfig.model_rebuild()
TransferToAgentToolResultErrorModel.model_rebuild()
TransferToAgentToolResultSuccessModel.model_rebuild()
TransferToNumberResultErrorModel.model_rebuild()
TransferToNumberResultSipSuccessModel.model_rebuild()
TransferToNumberResultTwilioSuccessModel.model_rebuild()
TransferToNumberToolConfigInput.model_rebuild()
TtsConversationalConfigOverride.model_rebuild()
TtsConversationalConfigWorkflowOverrideInput.model_rebuild()
TurnConfigOverride.model_rebuild()
TurnConfigWorkflowOverride.model_rebuild()
TxtExportOptions.model_rebuild()
UnitTestToolCallEvaluationModelInput.model_rebuild()
UnitTestToolCallParameter.model_rebuild()
UnitTestWorkflowNodeTransitionEvaluationNodeId.model_rebuild()
UpdateAssetParams.model_rebuild()
UpdateCalendarEventParams.model_rebuild()
UpdateClientParams.model_rebuild()
UpdateProductParams.model_rebuild()
UpdateServiceParams.model_rebuild()
UpdateStaffParams.model_rebuild()
UrlAvatar.model_rebuild()
UserFeedback.model_rebuild()
VadConfigWorkflowOverride.model_rebuild()
VoiceMailDetectionResultSuccessModel.model_rebuild()
VoicemailDetectionToolConfig.model_rebuild()
WebhookToolApiSchemaConfigInput.model_rebuild()
WebhookToolConfigInput.model_rebuild()
WhatsAppTemplateBodyComponentParams.model_rebuild()
WhatsAppTemplateButtonComponentParams.model_rebuild()
WhatsAppTemplateDocumentParam.model_rebuild()
WhatsAppTemplateDocumentParamDetails.model_rebuild()
WhatsAppTemplateHeaderComponentParams.model_rebuild()
WhatsAppTemplateImageParam.model_rebuild()
WhatsAppTemplateImageParamDetails.model_rebuild()
WhatsAppTemplateLocationParam.model_rebuild()
WhatsAppTemplateLocationParamDetails.model_rebuild()
WhatsAppTemplateTextParam.model_rebuild()
WidgetLanguagePreset.model_rebuild()
WidgetTermsTranslation.model_rebuild()
WidgetTextContents.model_rebuild()
WorkflowEdgeModelInput.model_rebuild()
WorkflowEndNodeModelInput.model_rebuild()
WorkflowExpressionConditionModelInput.model_rebuild()
WorkflowLlmConditionModelInput.model_rebuild()
WorkflowOverrideAgentNodeModelInput.model_rebuild()
WorkflowPhoneNumberNodeModelInput.model_rebuild()
WorkflowResultConditionModelInput.model_rebuild()
WorkflowStandaloneAgentNodeModelInput.model_rebuild()
WorkflowStartNodeModelInput.model_rebuild()
WorkflowToolEdgeStepModel.model_rebuild()
WorkflowToolLocator.model_rebuild()
WorkflowToolMaxIterationsExceededStepModel.model_rebuild()
WorkflowToolNestedToolsStepModelInput.model_rebuild()
WorkflowToolNodeModelInput.model_rebuild()
WorkflowToolResponseModelInput.model_rebuild()
WorkflowUnconditionalModelInput.model_rebuild()
