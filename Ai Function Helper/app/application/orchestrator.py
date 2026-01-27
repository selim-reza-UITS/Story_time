from app.models.schemas import (
    ChatRequest, ChatResponse, 
    LearnRequest, LearnResponse, 
    GrammarRequest, GrammarResponse
)
from app.infrastructure.llm_client import LLMClient
from app.infrastructure.tts_client import TTSClient
from app.domain.prompt_builder import PromptBuilder
from app.domain.conversation import ConversationManager
from app.domain.grammar.grammar_service import GrammarService
from app.guardrails.guardrails import Guardrails
from app.infrastructure.config_service import JsonConfigService
import base64

class Orchestrator:
    def __init__(self):
        # Initialize all services
        self.llm_client = LLMClient()
        self.tts_client = TTSClient()
        self.prompt_builder = PromptBuilder()
        self.conversation_manager = ConversationManager()
        # Inject LLM client into GrammarService
        self.grammar_service = GrammarService(self.llm_client)
        self.guardrails = Guardrails()
        self.config_service = JsonConfigService()

    def handle_chat_request(self, request: ChatRequest) -> ChatResponse:
        # 1. Fetch Config & Construct System Prompt
        config = self.config_service.get_config()
        system_prompt = self.prompt_builder.build_system_prompt(config.behavior_settings, request.context)
        formatted_history = self.prompt_builder.format_conversation_history(request.conversation_history)
        
        # Combine into complete user message context
        full_user_message = f"{formatted_history}\nUser: {request.message}"
        
        # 2. Call LLM
        raw_response = self.llm_client.generate_chat_response(system_prompt, full_user_message)
        
        # 3. Apply Guardrails
        safe_response = self.guardrails.validate_response(raw_response)

        # 4. Optional: Generate Speech for the chat response (Voice Assistant feature)
        # Assuming we want the chat to speak back.
        #audio_bytes = self.tts_client.text_to_speech(safe_response)
        
        # Encode audio to base64
        # audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None

        return ChatResponse(
            chat_response=safe_response,
            # speech_output=audio_b64
        )

    def handle_learn_request(self, request: LearnRequest) -> LearnResponse:
        """
        Handles Pronunciation + Word Description request.
        """
        word = request.word

        # 1. Generate Description via LLM
        # We can reuse generate_description or create a more specific prompt
        description = self.llm_client.generate_description(word)
        
        # 2. Generate Pronunciation Audio via TTS
        # The user specifically asked for pronunciation to be done by TTS
        audio_bytes = self.tts_client.text_to_speech(word)

        # Encode audio to base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None

        return LearnResponse(
            description=description,
            pronunciation_audio=audio_b64
        )

    def handle_grammar_request(self, request: GrammarRequest) -> GrammarResponse:
        """
        Handles Grammar Correction request.
        """
        text = request.text
        
        # 1. Correct Grammar
        corrected_text = self.grammar_service.correct_grammar(text)
        
        return GrammarResponse(
            corrected_text=corrected_text
        )
